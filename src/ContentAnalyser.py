import os   # For system API calls
from pathlib import Path  # Object-oriented file system paths
from DocAnalyser import classify_document
from ImageAnalyser import classify_image

# Supported file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".docx"}

def analyse_content(input_path):
    """Classify files, group by label, and reorganize.
    
    Parameters:
    -input_path: path to the dir where the content is to be reorgnaized. str/os.path

    Returns:
    -grouped_files: a dict with relative paths where key is the folder name and 
        values are the files under that key.
        for example, if file is "AI innvoation.pdf" to be sorted to 'technology',
        key is 'technology', and value is 'technology/AI innovation.pdf'

    """
    grouped_files = {}

    for root, _, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)
            extension = Path(file).suffix.lower()

            try:
                if extension in IMAGE_EXTENSIONS:
                    label = classify_image(file_path)
                elif extension in DOCUMENT_EXTENSIONS:
                    label = classify_document(file_path)
                else:
                    continue  # Skip unsupported file types
                
                # Group files by label
                grouped_files.setdefault(label, []).append(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    return grouped_files
