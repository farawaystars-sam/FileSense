import argparse  # For parsing command-line arguments
import os  # For interacting with the operating system (file handling, paths)
import shutil  # For file operations like copying and moving files
from PathValidator import validate_path     # For validating path
from ContentAnalyser import analyse_content # A high level function for analysing content

# version
__version__ = "0.1.0"

def main():
    parser = argparse.ArgumentParser(description="CLI for AI-powered file reorganization.")
    parser.add_argument('-i', '--input-path', type=str, required=True, help='Specify the input directory path.')
    parser.add_argument('-o', '--output-path', type=str, required=True, help='Specify the output directory path.')
    parser.add_argument('-d', '--dry-run', action='store_true', default=True, help='Ask user to accept/reject changes (default).')
    parser.add_argument('-f', '--force', action='store_true', help='Apply changes without confirmation.')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()
    try:
        input_folder = validate_path(args.input_path)
        output_folder = args.output_path
        os.makedirs(output_folder, exist_ok=True)

        dry_run = not args.force
        grouped_files = analyse_content(input_folder)

        # Reorganize files into labeled folders
        for label, files in grouped_files.items():
            label_dir = os.path.join(output_folder, label)
            os.makedirs(label_dir, exist_ok=True)
        
            for file_path in files:
                if dry_run:
                    user_input = input(f"Move {file_path} to {label_dir}? (y/n): ")
                    if user_input.lower() != 'y' or user_input.lower() != 'Y':
                        print(f"[-]  Skipping file .{file_path[label:]}....")
                        continue  # Skip this file if the user doesn't accept the change
                        
                shutil.copy(file_path, label_dir)
                print(f"Moved {file_path} to {label_dir}")

        print("Reorganization completed!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()