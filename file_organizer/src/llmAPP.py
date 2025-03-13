from flask import Flask, request, jsonify
from flask_cors import CORS  # Allow cross-origin requests (from Electron app)
import os
import shutil
import json
import re
from multiprocessing import Pool
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
import mimetypes

# Set up the Ollama LLM with the Qwen model
llm = ChatOllama(model="qwen2:7b")

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-domain requests

# Global variables for storing grouped files and performance data
GROUPED_FILES = {}
PERF_DATA = {}
TEMP_DIR = "tmp"

def create_prompt(file_summaries):
    """
    Create a prompt message for the LLM based on the file summaries.
    """
    template = """You are an AI file organization assistant. Your task is to analyze files and organize them into semantic folders based on their content.

    ## Objective
    Create a human-like folder structure that organizes files based on their actual content, purpose, and relationships. The organization should feel natural and intuitive, as if a human had carefully organized their files.
    
    ## Input Data
    {file_list}

    ## Task Description
    1. Analyze each file's content, metadata, and context
    2. Identify the main topics, purposes, and relationships between files
    3. Create meaningful, descriptive folder names that reflect content
    4. Group related files together based on their semantic meaning

    ## Critical Rules
    1. NEVER create categories based on file types (e.g., no "PDFs", "Images", etc.)
    2. NEVER put the same file in multiple categories
    3. Focus on what the file is about, not what format it's in
    4. Use natural, descriptive folder names (e.g., "Project Documentation", "Meeting Notes")
    5. Group files by their purpose or subject matter
    6. A screenshot of a document should go with related documents
    7. An image of a project should go with project files
    8. Text files describing a topic should go with other files about that topic

    ## Required Output Format
    You must return ONLY a JSON object with EXACTLY this structure:
    {{
        "proposed_struct": {{
            "Project Planning": [
                ["/full/path/to/doc.pdf", "Project Planning/requirements_doc"],
                ["/full/path/to/screenshot.png", "Project Planning/timeline_chart"]
            ],
            "Technical Documentation": [
                ["/full/path/to/notes.txt", "Technical Documentation/api_notes"]
            ]
        }},
        "errors": "no errors occurred happy happy",
        "spare": "Brief comment about the organization"
    }}

    CRITICAL FORMAT RULES:
    1. The output must be valid JSON
    2. Do not include any text before or after the JSON
    3. Use the exact field names shown above
    4. Each file must appear in exactly one category
    5. Each file entry must be a list with exactly 2 strings
    6. Use full file paths exactly as provided
    7. Folder names should be clear and descriptive
    8. No file type based categories allowed
    """
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(template)
    ])
    
    return prompt, {"file_list": json.dumps(file_summaries, indent=2)}

def process_file(file_path):
    """
    Process a single file: extract content and metadata for content analysis.
    """
    try:
        # Get file metadata
        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        file_size = os.path.getsize(file_path)
        file_info = f"[Filename: {filename}]\n[Type: {mime_type}]\n[Size: {file_size} bytes]\n"
        
        # Try to extract text content for better analysis
        try:
            if mime_type and mime_type.startswith('text/'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return file_path, f"{file_info}Content: {content[:1000] if len(content) > 1000 else content}"
            
            # For binary files, just return metadata
            return file_path, file_info
            
        except Exception as e:
            # If we can't read the file, still return the metadata
            return file_path, file_info
            
    except Exception as e:
        return file_path, f"[Error processing file: {str(e)}]"

def get_folder_structure(file_summaries):
    """Use LangChain with Ollama to generate a content-based folder structure."""
    try:
        # Create the prompt and input
        prompt, input_dict = create_prompt(file_summaries)
        
        # Create the chain
        chain = prompt | llm
        
        # Get result from the model
        result = chain.invoke(input_dict)
        
        # Parse the JSON response
        response_data = json.loads(result.content)
        
        # Extract the proposed structure
        proposed_struct = response_data.get('proposed_struct', {})
        errors = response_data.get('errors', 'no errors occurred happy happy')
        spare = response_data.get('spare', '')
        
        # Convert the structure to the desired format
        output_structure = {}
        for category, files in proposed_struct.items():
            output_structure[category] = {
                "files": [path for path, _ in files]
            }
        
        return {
            "proposed_structure": output_structure,
            "errors": errors,
            "spare": spare
        }
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"error": "Failed to parse model response"}
        
    except Exception as e:
        print(f"\nError in get_folder_structure: {str(e)}")
        return {"error": f"Failed to process model response: {str(e)}"}

def file_content_analysis(dir_path):
    """
    Analyze file contents in the specified directory and organize them into folders based on their content.
    """
    # Check if the directory exists
    if not os.path.exists(dir_path):
        print(f"Error: Directory '{dir_path}' does not exist.")
        return None

    # Get all files recursively in the specified directory and its subdirectories
    files = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    # Check if there are any files in the directory
    if not files:
        print(f"Error: No files found in directory '{dir_path}'.")
        return None

    # Parallel processing of files
    with Pool(processes=4) as pool:
        results = pool.map(process_file, files)

    # Create dictionary with file summaries
    file_summaries = {file_path: content for file_path, content in results}

    # Get folder structure using Langchain and Ollama
    folder_structure = get_folder_structure(file_summaries)

    return folder_structure

@app.route("/browse", methods=["POST"])
def send_initial_struct():
    try: 
        data = request.json
        input_path = data.get("input_path", "")
        print(f"📂 Browsing: {input_path}")

        # Get initial directory structure
        dir_structure = {}
        for root, _, files in os.walk(input_path):
            relative_root = os.path.relpath(root, input_path)
            if relative_root == ".":
                dir_structure[relative_root] = [f for f in files]
            else:
                dir_structure[relative_root] = [os.path.join(relative_root, f) for f in files]
        
        return jsonify(dir_structure)
    except Exception as e:
        print(f"Error while browsing initial struct: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/process", methods=["POST"])
def process_input():
    try:
        data = request.json
        user_input = data.get("user_input", "")

        print(f"🖥️ Received input: {user_input}")
        
        # Call file_content_analysis to get the folder structure
        global PERF_DATA
        retured_structure = file_content_analysis(user_input)
        global GROUPED_FILES 
        GROUPED_FILES = retured_structure.get("proposed_structure", {})
        
        print(f"Grouped files: {GROUPED_FILES}")
        return jsonify(GROUPED_FILES)
    except Exception as e:
        print(f"❌ Error in processing: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route("/accept-changes", methods=['POST'])    
def accept_changes():
    try:
        # Implicit positive rating: 1
        PERF_DATA["rating"] = 1
        data = request.json
        dir_s = data.get("structure", "")
        if not dir_s:
            raise Exception("Invalid request from json")
        
        # Call implement_changes
        success = implement_changes(GROUPED_FILES)
        return jsonify({"status": f"Changes implemented successfully {success}"})
    except Exception as e:
        print(f"Error in making changes {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

def implement_changes(dir_struct, output_path=os.path.join(".", TEMP_DIR)):
    try:    
        print(f"Call to implement changes: {GROUPED_FILES}")
        for key, value in dir_struct.items():
            label_dir = os.path.join(output_path, key)
            os.makedirs(label_dir, exist_ok=True)
            for file_path in value["files"]:
                shutil.copy(file_path, label_dir)
                print(f"Moved {file_path} to {label_dir}")
        return True
    except Exception as e:
        print(f"Error in implementing changes: {e}")
        return False

@app.route("/reject-changes", methods=['POST'])    
def reject_changes():
    try:
        # Implicit negative rating: 0
        PERF_DATA["rating"] = 0
        data = request.json
        mes = data.get("message", "")
        if not mes:
            raise Exception("Invalid request from json")
        
        # Call undo_changes
        success = undo_changes()
        return jsonify({"status": f"Changes rejected successfully {success}"})
    except Exception as e:
        print(f"Error in making changes {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

def undo_changes(output_path=os.path.join(".", TEMP_DIR)):
    try:    
        shutil.rmtree(output_path)
        return True
    except Exception as e:
        print(f"Error in rejecting changes: {e}")
        return False

if __name__ == "__main__":
    app.run(debug=True)