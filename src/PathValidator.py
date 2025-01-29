import os

def validate_path(input_path):
    """Validate if the path exists and is a directory."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Path '{input_path}' does not exist.")
    if not os.path.isdir(input_path):
        raise NotADirectoryError(f"Path '{input_path}' is not a directory.")
    return input_path