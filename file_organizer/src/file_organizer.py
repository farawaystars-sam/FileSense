import os
import json
import re
from multiprocessing import Pool
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
import mimetypes

# Set up the Ollama LLM with the Qwen model
llm = ChatOllama(model="qwen2:7b")

def create_prompt(file_summaries):
    """
    Create a prompt message for the LLM based on the file summaries.
    """
    template = """You are an AI file organization assistant. Your task is to analyze files and organize them into semantic folders based on their content, purpose, and context.

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

def extract_keywords_from_filename(filename):
    """
    Extract meaningful keywords from the filename for better categorization.
    """
    # Remove file extensions and split into words
    name = os.path.splitext(filename)[0]
    words = re.findall(r'\w+', name)
    
    # Filter out common stopwords
    stopwords = {"file", "doc", "document", "image", "pdf", "txt", "png", "jpg"}
    keywords = [word.lower() for word in words if word.lower() not in stopwords]
    
    return keywords

def process_file(file_path):
    """
    Process a single file: extract content, metadata, and context for better analysis.
    """
    try:
        # Get file metadata
        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        file_size = os.path.getsize(file_path)
        
        # Extract keywords from filename
        keywords = extract_keywords_from_filename(filename)
        
        # Prepare file info
        file_info = {
            "filename": filename,
            "type": mime_type,
            "size": f"{file_size} bytes",
            "keywords": keywords
        }
        
        # Try to extract text content for better analysis
        try:
            if mime_type and mime_type.startswith('text/'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_info["content"] = content[:1000] if len(content) > 1000 else content
            else:
                file_info["content"] = "Binary file (no text content)"
            
        except Exception as e:
            file_info["content"] = f"Error reading content: {str(e)}"
        
        return file_path, file_info
        
    except Exception as e:
        return file_path, {"error": f"Error processing file: {str(e)}"}

def parse_folder_structure(text):
    """Parse folder structure from text output."""
    try:
        # Extract JSON from the response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print("No JSON structure found in response")
            return None
        
        # Parse the JSON
        response = json.loads(match.group(0))
        
        # Validate required fields
        if 'proposed_struct' not in response:
            print("No 'proposed_struct' found in response")
            return None
            
        if 'errors' not in response:
            print("No 'errors' field found in response")
            return None
            
        if 'spare' not in response:
            print("No 'spare' field found in response")
            return None
            
        # Validate the structure format
        proposed_struct = response['proposed_struct']
        if not isinstance(proposed_struct, dict):
            print("'proposed_struct' must be a dictionary")
            return None
            
        # Track files to ensure no duplicates
        seen_files = set()
        
        # Validate each category's files
        for category, files in proposed_struct.items():
            if not isinstance(files, list):
                print(f"Files for category {category} must be a list")
                return None
                
            # Check for file type based categories
            if any(type_name in category.lower() for type_name in ['pdf', 'doc', 'image', 'text', 'file']):
                print(f"Category {category} appears to be based on file type")
                return None
                
            for file_item in files:
                if not isinstance(file_item, list) and not isinstance(file_item, tuple):
                    print(f"Each file item must be a list or tuple: {file_item}")
                    return None
                if len(file_item) != 2:
                    print(f"Each file item must have exactly 2 elements: {file_item}")
                    return None
                    
                # Check for duplicate files
                if file_item[0] in seen_files:
                    print(f"File {file_item[0]} appears in multiple categories")
                    return None
                seen_files.add(file_item[0])
                
        return response
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error parsing structure: {e}")
        return None

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

if __name__ == "__main__":
    dir_path = "/Users/vidya/Downloads/10MB"  # Your test directory
    result = file_content_analysis(dir_path)
    if result:
        print(json.dumps(result, indent=4))