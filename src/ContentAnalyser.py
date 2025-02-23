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
    return group_files_by_label(input_path)
    # grouped_files = {}
    # # get all the files in the input path
    # def get_all_files(base_dir):
    #     file_list = []
        
    #     for root, _, files in os.walk(base_dir):
    #         for file in files:
    #             absolute_path = os.path.join(root, file)
    #             file_list.append(absolute_path)
    #     print(file_list)
    #     return file_list
    
    # files_list = get_all_files(input_path)
    
    # try:
    #     # Classify files and group by label under the input path
    #     for file_path in files_list:
    #         extension = Path(file_path).suffix.lower()

    #         if extension in IMAGE_EXTENSIONS:
    #             label = classify_image(file_path)
    #         elif extension in DOCUMENT_EXTENSIONS:
    #             label = classify_document(file_path)
    #         else:
    #             continue  # Skip unsupported file types
            
    #         # extract file name
    #         # file_name = os.basename(file_path)

    #         # Group files by label by appending the file to input path under labeled folder
             
    #         assert label is not None, "The label is None: check the classifier"

    #         if label not in grouped_files:
    #             grouped_files[label] = []
            
    #         grouped_files[label].append(os.path.join(label, os.path.basename(file_path)))
        
    #         return grouped_files
    # except Exception as e:
    #     print(f"Error processing {file_path}: {e}")
    

    # # for root, _, files in os.walk(input_path):
    # #     for file in files:
    # #         file_path = os.path.join(root, file)
    # #         extension = Path(file).suffix.lower()

    # #         try:
    # #             if extension in IMAGE_EXTENSIONS:
    # #                 label = classify_image(file_path)
    # #             elif extension in DOCUMENT_EXTENSIONS:
    # #                 label = classify_document(file_path)
    # #             else:
    # #                 continue  # Skip unsupported file types
                
    # #             # Group files by label
    # #             grouped_files.setdefault(label, []).append(file_path)
    # #         except Exception as e:
    # #             print(f"Error processing {file_path}: {e}")
    # # return grouped_files


def get_all_files(base_dir):
    file_list = []
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            absolute_path = os.path.join(root, file)
            file_list.append(absolute_path)
    
    return file_list

def img_func(file_path):
    return classify_image(file_path)

def doc_func(file_path):
    return classify_document(file_path)

def group_files_by_label(base_dir):
    files = get_all_files(base_dir)
    grouped_files = {}
    
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            label = img_func(file)
        elif ext in DOCUMENT_EXTENSIONS:
            label = doc_func(file)
        else:
            continue

        assert label is not None, "The dir label is None: check the classifier"
        
        if label not in grouped_files:
            grouped_files[label] = []
        
        grouped_files[label].append(os.path.join(label, os.path.basename(file)))
        
        assert grouped_files, "The grouped_files is empty: check the above code"
    return grouped_files