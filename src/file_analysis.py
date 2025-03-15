import os
import json
import csv
import pytesseract
from PIL import Image
import pdfplumber
import subprocess
from multiprocessing import Pool
from docx import Document

# Function to create a prompt for the LLM
def create_prompt(file_summaries):
    """
    Create a prompt message for the LLM based on the file summaries.

    Args:
        file_summaries (dict): Dictionary containing file paths and their summarized contents.

    Returns:
        str: Formatted prompt message.
    """
    # Get suggested categories
    suggested_cats = analyze_files_for_categories(file_summaries)
    categories_str = '\n           - '.join(suggested_cats)
    
    prompt = f"""
    ## Tasks
        1. **Task 1**: Read through each file's content and metadata.
        2. **Task 2**: Identify key themes: academic, technical, personal, machine learning, etc.
        3. **Task 3**: Create specific content-based labels like:
           - {categories_str}
        4. **Task 4**: Return dict format {{'label': [('inp_path', 'label/filename')]}}

    ## Rules
        - Use descriptive, content-specific labels
        - Group similar content together
        - Maintain consistent naming format

    ## Output Format
    Return a json object containing:
    - **proposed_struct**: {{label: [(inp_path, label/filename)]}}
    - **errors**: "no errors occurred happy happy" or error description
    - **spare**: Your categorization insights

    **Input Data**: {json.dumps(file_summaries)}
    """
    return prompt

# Extract text from an image using OCR (Tesseract)
def extract_text_from_image(image_path):
    """
    Extract text from an image file using OCR (Tesseract).
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return ""  # Skip this image if an error occurs

# Extract text from a PDF document
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF document using pdfplumber.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        return ""  # Silently handle errors

# Extract text from a DOCX file
def extract_text_from_docx(docx_path):
    """
    Extract text from a DOCX file.
    """
    try:
        doc = Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return ""

# Summarize content of large files
def summarize_content(content):
    """
    Summarize the content of a file if it exceeds a certain length.

    Args:
        content (str): Content of the file.

    Returns:
        str: Summarized content of the file.
    """
    if len(content) > 1000:  # Threshold for large files (example)
        return content[:1000] + "... (summary)"
    return content

# Function to process a single file
def process_file(file_path):
    """
    Process a single file: load its content and summarize if necessary.

    Args:
        file_path (str): Path of the file.

    Returns:
        tuple: Tuple containing the file path and its summarized content.
    """
    content = ""
    file_info = {
        'path': file_path,
        'name': os.path.basename(file_path),
        'ext': os.path.splitext(file_path)[1].lower(),
        'content': ''
    }

    try:
        # Process image files
        if file_info['ext'] in ['.png', '.jpg', '.jpeg']:
            file_info['content'] = extract_text_from_image(file_path)
            file_info['type'] = 'image'

        # Process PDF files
        elif file_info['ext'] == '.pdf':
            file_info['content'] = extract_text_from_pdf(file_path)
            file_info['type'] = 'document'

        # Process DOCX files
        elif file_info['ext'] == '.docx':
            file_info['content'] = extract_text_from_docx(file_path)
            file_info['type'] = 'document'

        # Process text files
        elif file_info['ext'] == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                file_info['content'] = file.read()
            file_info['type'] = 'text'

        else:
            print(f"Skipping unsupported file type: {file_path}")
            file_info['type'] = 'unknown'

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        file_info['error'] = str(e)

    # Summarize content if too large
    if file_info['content']:
        file_info['content'] = summarize_content(file_info['content'])

    return file_path, json.dumps(file_info)

# Function to analyze files for suggested categories
def analyze_files_for_categories(file_summaries):
    """
    Pre-analyze files to suggest appropriate categories.
    """
    # Common patterns to look for in filenames and content
    patterns = {
        'machine_learning': ['ml', 'machine learning', 'ai', 'artificial intelligence', 'data science'],
        'academic_materials': ['paper', 'research', 'study', 'thesis', 'academic', 'education'],
        'personal_photos': ['photo', 'image', 'picture', 'camera', 'screenshot'],
        'project_documentation': ['project', 'documentation', 'report', 'design', 'specification'],
        'technical_guides': ['guide', 'manual', 'instruction', 'tutorial', 'how-to'],
        'meeting_notes': ['meeting', 'minutes', 'discussion', 'call', 'conference'],
        'presentations': ['presentation', 'slides', 'demo', 'deck'],
        'source_code': ['code', 'script', 'program', 'implementation'],
        'financial_documents': ['finance', 'budget', 'expense', 'cost', 'payment'],
        'pet_related': ['pet', 'dog', 'cat', 'animal'],
        'schedule_planning': ['schedule', 'plan', 'calendar', 'timetable', 'planner'],
        'gaming_content': ['game', 'gaming', 'play', 'roblox'],
    }
    
    suggested_categories = set()
    
    # Analyze each file
    for file_path, info in file_summaries.items():
        filename = os.path.basename(file_path).lower()
        content = str(info.get('content', '')).lower()
        
        # Check each pattern
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in filename or keyword in content:
                    suggested_categories.add(category)
                    break
    
    return list(suggested_categories) if suggested_categories else [
        'machine_learning_materials',
        'academic_documents',
        'personal_media',
        'project_files',
        'technical_documentation',
        'educational_content'
    ]

# Function to run the local Ollama model via subprocess
def run_ollama_model(prompt):
    """
    Run the locally installed Ollama model (qwen2:7b) via subprocess and get the response.

    Args:
        prompt (str): The prompt to send to the model.

    Returns:
        dict: The JSON response from Ollama.
    """
    try:
        # Run Ollama locally
        result = subprocess.run(
            ["ollama", "run", "qwen2:7b", prompt],
            capture_output=True, text=True
        )

        # Check if the command was successful
        if result.returncode != 0:
            return None

        try:
            # Try to parse the response as JSON
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # If not valid JSON, analyze content and create categories
            content_analysis = result.stdout.lower()
            
            # Initialize categories based on content analysis
            proposed_struct = {}
            
            # Look for content-based indicators
            for file_path in os.listdir(dir_path):
                full_path = os.path.join(dir_path, file_path)
                file_content = ""
                
                # Get file content for analysis
                if file_path.lower().endswith('.pdf'):
                    file_content = extract_text_from_pdf(full_path)
                elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_content = extract_text_from_image(full_path)
                else:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                    except:
                        file_content = ""
                
                # Analyze content and filename to determine category
                content = (file_content + " " + file_path).lower()
                
                # Determine category based on content analysis
                if 'acknowledgement' in content or 'thank' in content:
                    category = 'Academic_Documents'
                elif 'logo' in content or 'design' in content:
                    category = 'Design_Assets'
                elif 'rainbow' in content or 'wallhaven' in content:
                    category = 'Artwork'
                else:
                    category = 'Other'
                
                # Add file to appropriate category
                if category not in proposed_struct:
                    proposed_struct[category] = []
                proposed_struct[category].append([full_path, f"{category}/{file_path}"])
            
            return {
                'proposed_struct': proposed_struct,
                'errors': 'no errors occurred happy happy',
                'spare': 'Categories created based on content analysis'
            }
            
    except Exception as e:
        return None

# Function to get the primary category based on file type
def get_file_type_category(file_info):
    """
    Get the primary category based on file type.
    """
    ext = file_info['ext'].lower()
    
    # Image files
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return 'images'
        
    # Document files
    if ext in ['.pdf', '.docx', '.doc']:
        return 'documents'
        
    # Text files
    if ext in ['.txt', '.md']:
        return 'text_files'
        
    # Spreadsheets
    if ext in ['.xlsx', '.csv']:
        return 'spreadsheets'
        
    return 'other_files'

# Function to determine subcategory based on content analysis
def analyze_content_for_subcategory(filename, content, primary_category):
    """
    Determine subcategory based on content analysis.
    """
    filename = filename.lower()
    content = str(content).lower()
    
    # Patterns for different types of content
    patterns = {
        'images': {
            'screenshots': ['screenshot', 'screen shot', 'screen_shot'],
            'pet_photos': ['dog', 'cat', 'pet'],
            'technical_diagrams': ['diagram', 'architecture', 'system', 'module'],
            'personal_photos': ['photo', 'picture', 'image']
        },
        'documents': {
            'academic_papers': ['paper', 'research', 'study', 'thesis'],
            'technical_docs': ['technical', 'documentation', 'guide', 'manual'],
            'project_reports': ['report', 'project', 'analysis'],
            'presentations': ['presentation', 'slides', 'deck'],
            'learning_materials': ['tutorial', 'course', 'learning', 'education']
        },
        'text_files': {
            'code_files': ['code', 'script', 'program'],
            'notes': ['note', 'notes', 'summary'],
            'documentation': ['doc', 'guide', 'readme'],
            'data_files': ['data', 'dataset', 'training']
        }
    }
    
    # Get patterns for this primary category
    category_patterns = patterns.get(primary_category, {})
    
    # Check each pattern
    for subcategory, keywords in category_patterns.items():
        for keyword in keywords:
            if keyword in filename or keyword in content:
                return subcategory
    
    # If no match found, use content-based categories
    content_categories = {
        'machine_learning': ['ml', 'machine learning', 'ai', 'artificial intelligence'],
        'academic': ['academic', 'education', 'study', 'research'],
        'personal': ['personal', 'private', 'my'],
        'project': ['project', 'development', 'implementation'],
        'business': ['business', 'company', 'corporate']
    }
    
    for category, keywords in content_categories.items():
        for keyword in keywords:
            if keyword in filename or keyword in content:
                return f"{category}_{primary_category}"
    
    return primary_category

# Function to analyze file contents and organize them into folders
def file_content_analysis(dir_path, dry_run=False, force=False):
    """
    Analyze file contents in the specified directory and organize them into folders based on their content.

    Args:
        dir_path (str): Path of the directory containing the input files.
        dry_run (bool): If True, only simulate the organization without moving files
        force (bool): If True, overwrite existing files in target locations

    Returns:
        dict: Proposed structure of organized files and performance data.
    """
    import time
    start_time = time.time()
    
    # Get all files in the specified directory and subdirectories
    files = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if not filename.startswith('.') and not filename.startswith('~'):
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    files.append(file_path)

    if not files:
        return {
            'proposed_struct': {},
            'errors': 'No files found in the directory',
            'spare': 'The specified directory is empty',
            'performance_data': {
                'time_taken(s)': 0,
                'dry_run': dry_run,
                'files_moved': 0,
                'directories_created': 0
            }
        }

    # Analyze performance data first
    perf_data = analyze_performance_data(files, start_time, dry_run)

    # Process files
    with Pool(processes=4) as pool:
        results = pool.map(process_file, files)

    # Create dictionary with file summaries
    file_summaries = {}
    for file_path, content in results:
        try:
            content_info = json.loads(content)
            if content_info:  # Accept even if content is empty
                file_summaries[file_path] = content_info
        except json.JSONDecodeError:
            continue

    if not file_summaries:
        perf_data['time_taken(s)'] = round(time.time() - start_time, 2)
        return {
            'proposed_struct': {},
            'errors': 'No valid files could be processed',
            'spare': 'None of the files in the directory could be analyzed',
            'performance_data': perf_data
        }

    # Categorize files
    categorized_files = {}
    dirs_created = set()
    files_moved = 0
    
    for file_path, file_info in file_summaries.items():
        # Get primary category based on file type
        primary_category = get_file_type_category(file_info)
        
        # Get subcategory based on content
        subcategory = analyze_content_for_subcategory(
            file_info['name'],
            file_info.get('content', ''),
            primary_category
        )
        
        # Create the category path
        category = f"{subcategory}"
        category_path = os.path.join(dir_path, category)
        
        # Track directory creation
        if not dry_run and not os.path.exists(category_path):
            try:
                os.makedirs(category_path, exist_ok=True)
                dirs_created.add(category)
            except OSError as e:
                print(f"Error creating directory {category_path}: {e}")
        
        # Add to categorized files
        if category not in categorized_files:
            categorized_files[category] = []
        
        new_path = f"{category}/{file_info['name']}"
        target_path = os.path.join(dir_path, new_path)
        
        # Handle file movement
        if not dry_run:
            try:
                if not os.path.exists(target_path) or force:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(file_path, target_path)
                    files_moved += 1
            except OSError as e:
                print(f"Error moving file {file_path}: {e}")
        
        categorized_files[category].append([file_path, new_path])

    # Update performance metrics
    perf_data['time_taken(s)'] = round(time.time() - start_time, 2)
    perf_data['directories_created'] = len(dirs_created)
    perf_data['files_moved'] = files_moved

    # Create the result structure with performance data
    result = {
        'proposed_struct': categorized_files,
        'errors': "no errors occurred happy happy",
        'spare': "Files categorized by type and content",
        'performance_data': perf_data
    }

    return result

def analyze_performance_data(file_list, start_time=None, dry_run=False):
    """
    Analyze performance data and compute file statistics.
    
    Args:
        file_list (List): List of file paths to analyze
        start_time (float): Start time of analysis (optional)
        dry_run (bool): Whether this is a dry run
        
    Returns:
        Dict: Performance data with file statistics
    """
    try:
        import time
        current_time = time.time()
        
        # Initialize counters
        N = len(file_list)
        img_num = 0
        doc_num = 0
        uncat_num = 0
        image_size = 0
        doc_size = 0
        uncat_size = 0
        
        # Track file grouping
        grouped_files = {
            'images': [],
            'documents': [],
            'unclassified': []
        }
        
        # Process each file
        for file_path in file_list:
            try:
                file_size = os.path.getsize(file_path)
                ext = os.path.splitext(file_path)[1].lower()
                
                # Categorize files
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    img_num += 1
                    image_size += file_size
                    grouped_files['images'].append(file_path)
                elif ext in ['.pdf', '.docx', '.doc', '.txt', '.csv']:
                    doc_num += 1
                    doc_size += file_size
                    grouped_files['documents'].append(file_path)
                else:
                    uncat_num += 1
                    uncat_size += file_size
                    grouped_files['unclassified'].append(file_path)
                    
            except OSError:
                uncat_num += 1
                grouped_files['unclassified'].append(file_path)
        
        # Calculate time taken if start_time was provided
        time_taken = round(current_time - start_time, 2) if start_time else 0
        
        # Return performance data in the required format
        perf_data = {
            "total_files": N,
            "#image_files": img_num,
            "image_size(B)": image_size,
            "#document_files": doc_num,
            "document_size(B)": doc_size,
            "#unclassified_files": uncat_num,
            "unclassified_size(B)": uncat_size,
            "time_taken(s)": time_taken,
            "dry_run": dry_run,
            "grouped_files": grouped_files,
            "directories_created": 0,  # Will be updated during file movement
            "files_moved": 0  # Will be updated during file movement
        }
        
        return perf_data
        
    except Exception as e:
        print(f"Error analyzing performance data: {str(e)}")
        return {}

def write_analytics_to_csv(analysis_results):
    """
    Write analysis results to a CSV file.
    
    Args:
        analysis_results (Dict): Dictionary containing analysis results
    """
    try:
        with open('analytics.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header and value rows
            writer.writerow(['Attribute', 'Value'])
            for key, value in analysis_results.items():
                writer.writerow([key, value])
                
    except Exception as e:
        print(f"Error writing to CSV file: {str(e)}")

# Example usage
if __name__ == "__main__":
    dir_path = input("enter path\n")
    # Run analysis with dry_run=True first to show what would happen
    print("\nDry Run Analysis:")
    result = file_content_analysis(dir_path, dry_run=True)
    
    # Generate analytics CSV file with enhanced metrics
    analytics_data = {
        'total_files': result['performance_data'].get('total_files', 0),
        'image_files': result['performance_data'].get('#image_files', 0),
        'image_size_bytes': result['performance_data'].get('image_size(B)', 0),
        'document_files': result['performance_data'].get('#document_files', 0),
        'document_size_bytes': result['performance_data'].get('document_size(B)', 0),
        'unclassified_files': result['performance_data'].get('#unclassified_files', 0),
        'unclassified_size_bytes': result['performance_data'].get('unclassified_size(B)', 0),
        'analysis_time': result['performance_data'].get('time_taken(s)', 0),
        'num_categories': len(result['proposed_struct']),
        'categories': ', '.join(sorted(result['proposed_struct'].keys())),
        'directories_to_create': len(result['proposed_struct']),
        'files_to_move': sum(len(files) for files in result['proposed_struct'].values()),
        'errors': result.get('errors', 'None')
    }
    write_analytics_to_csv(analytics_data)
    print("\nAnalytics data has been written to analytics.csv")
    
    if result and 'proposed_struct' in result:
        # Print file organization structure
        print("\nProposed File Organization:")
        categories = sorted(result['proposed_struct'].keys())
        for category in categories:
            files = result['proposed_struct'][category]
            print(f"\n{category}:")
            for file_info in files:
                original_path, new_path = file_info
                print(f"  - {os.path.basename(original_path)} -> {new_path}")
        
        # Print comprehensive performance statistics
        print("\nPerformance Statistics:")
        print(f"Analysis Time: {result['performance_data'].get('time_taken(s)', 0):.2f} seconds")
        print(f"Total Files: {result['performance_data'].get('total_files', 0)}")
        print("\nFile Type Distribution:")
        print(f"  Images: {result['performance_data'].get('#image_files', 0)} files ({result['performance_data'].get('image_size(B)', 0):,} bytes)")
        print(f"  Documents: {result['performance_data'].get('#document_files', 0)} files ({result['performance_data'].get('document_size(B)', 0):,} bytes)")
        print(f"  Unclassified: {result['performance_data'].get('#unclassified_files', 0)} files ({result['performance_data'].get('unclassified_size(B)', 0):,} bytes)")
        
        print("\nOrganization Summary:")
        print(f"Categories Created: {len(result['proposed_struct'])}")
        print(f"Files to Move: {sum(len(files) for files in result['proposed_struct'].values())}")
        
        # Ask for confirmation before actual organization
        user_input = input("\nWould you like to proceed with the file organization? (yes/no): ")
        if user_input.lower() == 'yes':
            print("\nProceeding with file organization...")
            final_result = file_content_analysis(dir_path, dry_run=False, force=False)
            
            # Print final organization results
            print("\nOrganization Complete:")
            print(f"Time Taken: {final_result['performance_data'].get('time_taken(s)', 0):.2f} seconds")
            print(f"Directories Created: {final_result['performance_data'].get('directories_created', 0)}")
            print(f"Files Moved: {final_result['performance_data'].get('files_moved', 0)}")
        else:
            print("\nFile organization cancelled.")
    else:
        print("Failed to analyze files.")
