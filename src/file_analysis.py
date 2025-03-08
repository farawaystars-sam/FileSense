import os
import json
import pytesseract
from PIL import Image
from multiprocessing import Pool
import pdfplumber
from docx import Document
import ollama
import time

# Configure Ollama
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MODEL_NAME = 'qwen:7b'  # Using Qwen model for better categorization

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
    
    prompt = f"""Analyze and categorize these files based on content and type:
    Files: {json.dumps(file_summaries)}
    Suggested Categories: {categories_str}
    
    Return JSON with structure:
    {{
        "categories": {{
            "category_name": {{
                "files": ["file_path1"],
                "confidence": 0.95,
                "tags": ["tag1"]
            }}
        }},
        "analytics": {{
            "total_files": <number>,
            "categorized_files": <number>,
            "uncategorized_files": <number>,
            "average_confidence": <number>
        }}
    }}"""
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
            file_info['type'] = 'unknown'

    except Exception as e:
        file_info['error'] = str(e)

    # Summarize content if too large
    if file_info['content']:
        file_info['content'] = summarize_content(file_info['content'])

    return file_path, json.dumps(file_info)

# Function to analyze files for suggested categories
def analyze_files_for_categories(file_summaries):
    """
    Pre-analyze files to suggest appropriate categories based on content and metadata.
    
    Args:
        file_summaries (dict): Dictionary containing file information and content.
        
    Returns:
        list: List of suggested categories with hierarchical structure.
    """
    # Define hierarchical category patterns
    category_patterns = {
        'Documents': {
            'Academic': {
                'patterns': ['research', 'paper', 'thesis', 'study', 'academic'],
                'tags': ['education', 'research', 'academic']
            },
            'Technical': {
                'patterns': ['documentation', 'manual', 'guide', 'api', 'specification'],
                'tags': ['technical', 'reference', 'guide']
            },
            'Business': {
                'patterns': ['proposal', 'contract', 'agreement', 'invoice', 'report'],
                'tags': ['business', 'legal', 'financial']
            }
        },
        'Code': {
            'Source Code': {
                'patterns': ['code', 'script', 'program', 'implementation', 'class', 'function'],
                'tags': ['development', 'programming', 'source']
            },
            'Configuration': {
                'patterns': ['config', 'settings', 'env', 'setup', 'init'],
                'tags': ['configuration', 'setup', 'environment']
            },
            'Data': {
                'patterns': ['json', 'csv', 'xml', 'database', 'sql'],
                'tags': ['data', 'database', 'storage']
            }
        },
        'Media': {
            'Images': {
                'patterns': ['photo', 'image', 'picture', 'screenshot', 'diagram'],
                'tags': ['visual', 'image', 'photo']
            },
            'Presentations': {
                'patterns': ['presentation', 'slides', 'deck', 'demo'],
                'tags': ['presentation', 'slides', 'deck']
            },
            'Videos': {
                'patterns': ['video', 'recording', 'screencast', 'tutorial'],
                'tags': ['video', 'media', 'recording']
            }
        },
        'Project': {
            'Documentation': {
                'patterns': ['readme', 'docs', 'wiki', 'guide', 'tutorial'],
                'tags': ['documentation', 'guide', 'reference']
            },
            'Planning': {
                'patterns': ['plan', 'roadmap', 'timeline', 'milestone', 'schedule'],
                'tags': ['planning', 'project', 'timeline']
            },
            'Meetings': {
                'patterns': ['meeting', 'minutes', 'agenda', 'discussion', 'notes'],
                'tags': ['meeting', 'collaboration', 'discussion']
            }
        },
        'Personal': {
            'Notes': {
                'patterns': ['note', 'journal', 'diary', 'todo', 'reminder'],
                'tags': ['notes', 'personal', 'reminder']
            },
            'Finance': {
                'patterns': ['budget', 'expense', 'receipt', 'invoice', 'payment'],
                'tags': ['finance', 'money', 'expense']
            },
            'Schedule': {
                'patterns': ['calendar', 'schedule', 'appointment', 'event', 'planner'],
                'tags': ['schedule', 'calendar', 'planning']
            }
        }
    }
    
    # Initialize category matches with confidence scores
    category_matches = {}
    
    # Analyze each file
    for file_path, info in file_summaries.items():
        file_type = info.get('type', '').lower()
        filename = os.path.basename(file_path).lower()
        content = str(info.get('content', '')).lower()
        
        # Check each category and subcategory
        for main_cat, subcats in category_patterns.items():
            for subcat, details in subcats.items():
                confidence = 0
                matches = 0
                
                # Check patterns in filename and content
                for pattern in details['patterns']:
                    if pattern in filename:
                        confidence += 0.4
                        matches += 1
                    if pattern in content:
                        confidence += 0.6
                        matches += 1
                
                # Adjust confidence based on file type
                if file_type:
                    if file_type in main_cat.lower():
                        confidence += 0.2
                    if any(tag in file_type for tag in details['tags']):
                        confidence += 0.1
                
                # Normalize confidence score
                if matches > 0:
                    confidence = min(confidence, 1.0)
                    if subcat not in category_matches:
                        category_matches[subcat] = {
                            'confidence': confidence,
                            'count': 1,
                            'parent': main_cat,
                            'tags': details['tags']
                        }
                    else:
                        # Update existing category stats
                        prev = category_matches[subcat]
                        prev['confidence'] = (prev['confidence'] * prev['count'] + confidence) / (prev['count'] + 1)
                        prev['count'] += 1
    
    # Convert matches to suggested categories
    suggested = []
    for subcat, details in category_matches.items():
        if details['confidence'] >= 0.3:  # Minimum confidence threshold
            suggested.append(f"{details['parent']}/{subcat} (confidence: {details['confidence']:.2f})")
    
    return suggested if suggested else [
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
    Run the Ollama model to analyze and categorize files.
    
    Args:
        prompt (str): The prompt containing file information to analyze.
        
    Returns:
        dict: A dictionary containing categorized files and analytics.
    """
    try:
        # Call Ollama with the prompt
        response = ollama.chat(model=MODEL_NAME, messages=[{
            'role': 'user',
            'content': prompt
        }])

        # Parse the response
        try:
            # Extract the JSON part from the response
            response_text = response['message']['content']
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx + 1]
                result = json.loads(json_str)
                
                # Validate and structure the result
                if 'categories' in result:
                    # Convert to the expected format
                    proposed_struct = {}
                    total_confidence = 0
                    total_files = 0
                    
                    # Process each category
                    for category, info in result['categories'].items():
                        if 'files' in info:
                            # Add files to the proposed structure
                            proposed_struct[category] = info['files']
                            
                            # Update confidence metrics
                            confidence = info.get('confidence', 0.0)
                            total_confidence += confidence * len(info['files'])
                            total_files += len(info['files'])
                    
                    # Calculate analytics
                    analytics = {
                        'total_files': total_files,
                        'categorized_files': total_files,
                        'uncategorized_files': 0,
                        'average_confidence': round(total_confidence / total_files if total_files > 0 else 0, 2),
                        'categories_count': len(proposed_struct),
                        'largest_category': max(
                            ((cat, len(files)) for cat, files in proposed_struct.items()),
                            key=lambda x: x[1],
                            default=('none', 0)
                        )[0]
                    }
                    
                    # Add success flag
                    return {
                        'success': True,
                        'proposed_struct': proposed_struct,
                        'analytics': analytics,
                        'message': 'Files successfully categorized'
                    }
                else:
                    raise ValueError('Invalid response format: missing categories')
            else:
                raise ValueError('Could not find JSON in response')
        except json.JSONDecodeError as e:
            raise ValueError(f'Failed to parse JSON response: {str(e)}')
    except Exception as e:
        return {
            'success': False,
            'proposed_struct': {'uncategorized': []},
            'analytics': {
                'total_files': 0,
                'categorized_files': 0,
                'uncategorized_files': 0,
                'average_confidence': 0,
                'error': str(e)
            },
            'message': f'Error analyzing files: {str(e)}'
        }
    try:
        # First check if Ollama is running
        status = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if status.returncode != 0:
            print("Starting Ollama service...")
            subprocess.Popen(["ollama", "serve"])
            # Wait for service to start
            import time
            time.sleep(5)
        
        # Run Ollama with the Qwen2 model
        print("Running Ollama model...")
        result = subprocess.run(
            ["ollama", "run", "qwen2:7b", "--format json", prompt],
            capture_output=True,
            text=True,
            env={**os.environ, 'OLLAMA_HOST': 'localhost:11434'}
        )

        # Check if the command was successful
        if result.returncode != 0:
            print(f"Ollama error: {result.stderr}")
            return {
                'proposed_struct': {},
                'errors': f'Failed to run Ollama: {result.stderr}',
                'spare': 'Error occurred during model execution'
            }

        # Process the model's output
        output = result.stdout.strip()
        print(f"Model output: {output[:200]}...")
        
        try:
            # Try to extract JSON from the response
            # Look for JSON-like structure in the output
            import re
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                response = json.loads(json_str)
                
                # Validate the response structure
                if isinstance(response, dict) and 'proposed_struct' in response:
                    return response
            
            # If we couldn't parse JSON or it's not in the expected format,
            # try to parse the model's natural language response
            categories = {}
            current_category = None
            
            # Split output into lines and process each line
            for line in output.split('\n'):
                line = line.strip()
                
                # Look for category headers
                if line.endswith(':') or 'category:' in line.lower():
                    current_category = line.replace(':', '').strip()
                    categories[current_category] = []
                # Look for file paths under current category
                elif current_category and line and not line.startswith(('*', '-', '#')):
                    # Clean up the file path
                    file_path = line.strip('"').strip("'").strip()
                    if file_path:
                        categories[current_category].append(
                            [file_path, f"{current_category}/{os.path.basename(file_path)}"]
                        )
            
            return {
                'proposed_struct': categories,
                'errors': 'no errors occurred happy happy',
                'spare': 'Categories extracted from model response'
            }
            
        except Exception as e:
            print(f"Error parsing model output: {e}")
            # Fall back to basic content-based categorization
            return {
                'proposed_struct': {
                    'documents': [],
                    'images': [],
                    'code': [],
                    'other': []
                },
                'errors': f'Failed to parse model output: {str(e)}',
                'spare': 'Using fallback categorization'
            }
            
    except Exception as e:
        print(f"Unexpected error in run_ollama_model: {e}")
        return {
            'proposed_struct': {},
            'errors': f'Unexpected error: {str(e)}',
            'spare': 'Error occurred during model execution'
        }

# Function to get the primary category based on file type
def get_file_type_category(file_info):
    """
    Get the primary category based on file type with improved detection.
    
    Args:
        file_info (dict): Dictionary containing file information
        
    Returns:
        str: Primary category
    """
    # Enhanced file type mappings with more specific categories
    type_mappings = {
        'text': {
            'extensions': ['.txt', '.md', '.rst'],
            'category': 'documents'
        },
        'source': {
            'extensions': ['.py', '.js', '.java', '.cpp', '.h', '.cs', '.rb', '.php'],
            'category': 'code'
        },
        'image': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'category': 'images'
        },
        'document': {
            'extensions': ['.pdf', '.doc', '.docx', '.odt', '.rtf'],
            'category': 'documents'
        },
        'spreadsheet': {
            'extensions': ['.csv', '.xls', '.xlsx', '.ods'],
            'category': 'data'
        },
        'presentation': {
            'extensions': ['.ppt', '.pptx', '.odp', '.key'],
            'category': 'presentations'
        },
        'video': {
            'extensions': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
            'category': 'videos'
        },
        'audio': {
            'extensions': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
            'category': 'audio'
        },
        'archive': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'category': 'archives'
        },
        'config': {
            'extensions': ['.json', '.yaml', '.yml', '.ini', '.conf', '.env'],
            'category': 'configuration'
        }
    }
    
    # Get file extension
    ext = os.path.splitext(file_info['name'])[1].lower()
    
    # Find matching type based on extension
    for file_type, info in type_mappings.items():
        if ext in info['extensions']:
            return info['category']
    
    # Default category based on content type
    mime_type = file_info.get('type', '').lower()
    if 'text' in mime_type:
        return 'documents'
    elif 'image' in mime_type:
        return 'images'
    elif 'video' in mime_type:
        return 'videos'
    elif 'audio' in mime_type:
        return 'audio'
    
    return 'others'

# Function to determine subcategory based on content analysis using a more sophisticated approach
def analyze_content_for_subcategory(filename, content, primary_category):
    """
    Determine subcategory based on content analysis.
    
    Args:
        filename (str): Name of the file
        content (str): Content of the file
        primary_category (str): Primary category based on file type
        
    Returns:
        str: Determined subcategory
    """
    # Convert to lowercase for case-insensitive matching
    content = content.lower()
    filename = filename.lower()
    
    # Define category patterns with weights and required matches
    category_patterns = {
        'development': {
            'patterns': ['class', 'function', 'import', 'def ', 'var ', 'const ', 'module', 'package'],
            'extensions': ['.py', '.js', '.java', '.cpp', '.h', '.cs'],
            'weight': 1.5,
            'min_matches': 2
        },
        'documentation': {
            'patterns': ['readme', 'guide', 'documentation', 'manual', 'tutorial', 'howto', 'docs'],
            'extensions': ['.md', '.txt', '.pdf', '.doc', '.docx'],
            'weight': 1.2,
            'min_matches': 1
        },
        'configuration': {
            'patterns': ['config', 'settings', 'env', 'setup', 'init', 'properties'],
            'extensions': ['.json', '.yaml', '.yml', '.ini', '.conf', '.env'],
            'weight': 1.3,
            'min_matches': 1
        },
        'data': {
            'patterns': ['data', 'dataset', 'training', 'test', 'validation', 'sample'],
            'extensions': ['.csv', '.json', '.xml', '.sql', '.db'],
            'weight': 1.4,
            'min_matches': 1
        },
        'media': {
            'patterns': ['image', 'photo', 'video', 'audio', 'recording', 'thumbnail'],
            'extensions': ['.jpg', '.png', '.gif', '.mp4', '.mp3', '.wav'],
            'weight': 1.1,
            'min_matches': 1
        },
        'research': {
            'patterns': ['research', 'paper', 'study', 'analysis', 'experiment', 'methodology'],
            'extensions': ['.pdf', '.doc', '.docx', '.tex'],
            'weight': 1.2,
            'min_matches': 2
        }
    }
    
    # Calculate scores for each category
    scores = {}
    for category, rules in category_patterns.items():
        score = 0
        matches = 0
        
        # Check filename and extension
        for ext in rules['extensions']:
            if filename.endswith(ext):
                score += rules['weight'] * 2
                matches += 1
                break
        
        # Check content patterns
        for pattern in rules['patterns']:
            if pattern in content:
                score += rules['weight']
                matches += 1
        
        # Only consider categories that meet minimum match criteria
        if matches >= rules['min_matches']:
            scores[category] = score
    
    # Get the best matching category
    if scores:
        best_category = max(scores.items(), key=lambda x: x[1])[0]
        return f"{best_category}_{primary_category}"
    
    return primary_category

# Function to analyze file contents and organize them into folders with improved categorization
def file_content_analysis(dir_path, dry_run=False, force=False):
    """
    Analyze file contents in the specified directory and organize them into folders based on their content.

    Args:
        dir_path (str): Path of the directory containing the input files
        dry_run (bool): If True, only simulate the organization
        force (bool): If True, overwrite existing files
        
    Returns:
        dict: Proposed structure and performance data
    """
    try:
        start_time = time.time()
        
        # Get all files recursively
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

        # Process files in parallel
        with Pool(processes=4) as pool:
            results = pool.map(process_file, files)

        # Create file summaries
        file_summaries = {}
        for file_path, content in results:
            try:
                content_info = json.loads(content)
                if content_info:
                    file_summaries[file_path] = content_info
            except json.JSONDecodeError:
                continue

        if not file_summaries:
            return {
                'proposed_struct': {},
                'errors': 'No valid files could be processed',
                'spare': 'None of the files could be analyzed',
                'performance_data': {
                    'time_taken(s)': time.time() - start_time,
                    'total_files': len(files),
                    'dry_run': dry_run
                }
            }

        # Categorize files with confidence scores
        categorized_files = {}
        dirs_created = set()
        files_moved = 0
        
        for file_path, file_info in file_summaries.items():
            # Get primary and subcategories
            primary_category = get_file_type_category(file_info)
            subcategory = analyze_content_for_subcategory(
                file_info['name'],
                file_info.get('content', ''),
                primary_category
            )
            
            # Calculate confidence score based on content matches
            confidence_score = 0.0
            if 'content' in file_info and file_info['content']:
                # Add confidence based on content analysis
                content_patterns = {
                    'development': ['class', 'function', 'import'],
                    'documentation': ['readme', 'guide', 'manual'],
                    'data': ['dataset', 'training', 'test'],
                    'media': ['image', 'video', 'audio']
                }
                
                matches = 0
                total_patterns = 0
                for patterns in content_patterns.values():
                    total_patterns += len(patterns)
                    for pattern in patterns:
                        if pattern in file_info['content'].lower():
                            matches += 1
                
                confidence_score = min(0.8, matches / total_patterns + 0.2)
            else:
                # Base confidence on file extension matching
                confidence_score = 0.6
            
            # Create category structure
            category = subcategory
            if confidence_score < 0.4:
                category = 'others'
            
            # Create category in structure
            if category not in categorized_files:
                categorized_files[category] = {
                    'files': [],
                    'confidence': confidence_score,
                    'tags': []
                }
            
            # Add file to category
            new_path = f"{category}/{file_info['name']}"
            categorized_files[category]['files'].append(new_path)
            
            # Update confidence score as average
            current_conf = categorized_files[category]['confidence']
            current_files = len(categorized_files[category]['files'])
            categorized_files[category]['confidence'] = (current_conf * (current_files - 1) + confidence_score) / current_files
            
            # Create directory and move file if not dry run
            if not dry_run:
                category_path = os.path.join(dir_path, category)
                if not os.path.exists(category_path):
                    try:
                        os.makedirs(category_path, exist_ok=True)
                        dirs_created.add(category)
                    except OSError as e:
                        print(f"Error creating directory {category_path}: {e}")
                
                target_path = os.path.join(dir_path, new_path)
                try:
                    if not os.path.exists(target_path) or force:
                        if os.path.exists(target_path):
                            os.remove(target_path)
                        os.rename(file_path, target_path)
                        files_moved += 1
                except OSError as e:
                    print(f"Error moving file {file_path}: {e}")

        # Prepare performance data
        perf_data = {
            'time_taken(s)': time.time() - start_time,
            'total_files': len(files),
            'dry_run': dry_run,
            'directories_created': len(dirs_created),
            'files_moved': files_moved
        }

        return {
            'proposed_struct': categorized_files,
            'errors': None,
            'spare': "Files categorized by type and content with confidence scores",
            'performance_data': perf_data
        }

    except Exception as e:
        return {
            'proposed_struct': {'uncategorized': [f for f in files]},
            'errors': str(e),
            'performance_data': {
                'total_files': len(files) if 'files' in locals() else 0,
                'error': str(e)
            }
        }


def display_category_tree(categories, indent=0):
    """Display the category tree structure with file counts and confidence scores.
    
    Args:
        categories (dict): Dictionary containing category information
        indent (int): Current indentation level
    """
    for category, info in categories.items():
        prefix = '  ' * indent + ('└─ ' if indent > 0 else '')
        file_count = len(info.get('files', []))
        confidence = info.get('confidence', 0.0)
        tags = ', '.join(info.get('tags', []))
        
        # Print category with stats
        print(f"{prefix}{category} ({file_count} files, {confidence:.2f} confidence)")
        if tags:
            print(f"{' ' * (len(prefix) + 2)}Tags: {tags}")
            
        # Print files if any
        if file_count > 0:
            for file_path in info['files']:
                print(f"{' ' * (len(prefix) + 2)}├─ {os.path.basename(file_path)}")
        
        # Recursively display subcategories
        if 'subcategories' in info:
            display_category_tree(info['subcategories'], indent + 1)

def display_organization_summary(result):
    """Display a comprehensive summary of file organization.
    
    Args:
        result (dict): Result dictionary from file_content_analysis
    """
    print("\n=== File Organization Summary ===")
    print("\nPerformance Metrics:")
    perf = result.get('performance_data', {})
    print(f"├─ Analysis Time: {perf.get('time_taken(s)', 0):.2f} seconds")
    print(f"├─ Total Files: {perf.get('total_files', 0)}")
    print(f"├─ Files Processed: {perf.get('files_moved', 0)}")
    print(f"└─ Directories Created: {perf.get('directories_created', 0)}")
    
    print("\nFile Type Distribution:")
    print(f"├─ Images: {perf.get('#image_files', 0)} files ({perf.get('image_size(B)', 0):,} bytes)")
    print(f"├─ Documents: {perf.get('#document_files', 0)} files ({perf.get('document_size(B)', 0):,} bytes)")
    print(f"└─ Unclassified: {perf.get('#unclassified_files', 0)} files ({perf.get('unclassified_size(B)', 0):,} bytes)")
    
    if 'proposed_struct' in result:
        print("\nCategory Structure:")
        display_category_tree(result['proposed_struct'])

if __name__ == "__main__":
    dir_path = input("enter path")
    
    # Run analysis with dry_run=True first
    print("\nAnalyzing files...")
    result = file_content_analysis(dir_path, dry_run=True)
    
    if result and 'proposed_struct' in result:
        # Display comprehensive organization summary
        display_organization_summary(result)
        
        # Ask for confirmation before actual organization
        user_input = input("\nWould you like to proceed with the file organization? (yes/no): ")
        if user_input.lower() == 'yes':
            print("\nProceeding with file organization...")
            final_result = file_content_analysis(dir_path, dry_run=False, force=False)
            
            # Display final organization results
            if final_result:
                print("\n=== Final Organization Results ===")
                display_organization_summary(final_result)
                print("\nFile organization completed successfully!")
            else:
                print("\nError: File organization failed.")
            print("\nOrganization Complete!")
        else:
            print("\nFile organization cancelled.")
    else:
        print("Failed to analyze files.")
