from flask import Flask, request, jsonify
from flask_cors import CORS
from file_analysis import file_content_analysis
import os
import logging
import shutil
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


TEMP_DIR = "tmp"
GROUPED_FILES = {}
PERF_DATA = {}

def get_dir_structure(dir_path):
    dir_structure = {}

    for root, _, files in os.walk(dir_path):
        relative_root = os.path.relpath(root, dir_path)
        if relative_root == ".":
            dir_structure[relative_root] = [f for f in files]
        else:
            dir_structure[relative_root] = [os.path.join(relative_root, f) for f in files]
    
    return dir_structure


def write_data_to_csv(file_name, data:dict):
    # Writing to a csv 
    print(f"DATA: {data}")
    df = pd.DataFrame(data.values(), index=data.keys()).T
    csv_file = file_name or "analytics.csv"
    # Check if the file exists
    file_exists = os.path.isfile(csv_file)
    # Write or append data based on file existence
    df.to_csv(csv_file, 
                mode='a' if file_exists else 'w', 
                index=False, header=not file_exists)   

@app.route("/browse", methods=["POST"])
def send_initial_struct():
    try: 
        data = request.json
        input_path = data.get("input_path", "")
        print(f"📂 Browsing: {input_path}")

        #call get_dir_struct
        dir_structure = get_dir_structure(input_path)
        print(f"inistual dir struct: {dir_structure}")
        return jsonify(dir_structure)
    except Exception as e:
        print(f" while browsing initial struct: {e} occured")


@app.route('/process', methods=['POST'])
def analyze():
    try:
        data = request.json
        dir_path = data.get("user_input", "")
        
        logger.info(f"Received request to analyze directory: {dir_path}")
        print(f"in the process method: {dir_path}")
        if not dir_path or not os.path.isdir(dir_path):
            logger.error(f"Invalid directory path: {dir_path}")
            return jsonify({
                'proposed_struct': {},
                'errors': f'Invalid directory path: {dir_path}',
                'spare': 'Please provide a valid directory path'
            }), 400
            
        logger.info("Starting file content analysis...")
        result = file_content_analysis(dir_path)
        
        if not result:
            logger.error("No valid files found in directory")
            return jsonify({
                'proposed_struct': {}
                # 'errors': 'No valid files found in directory',
                # 'spare': 'The specified directory is empty or contains no supported files'
            }), 400
        
        logger.info("Analysis completed successfully")
        return jsonify(result)
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing request: {error_msg}")
        return jsonify({
            'proposed_struct': {},
            'errors': f'Server error: {error_msg}',
            'spare': 'An unexpected error occurred while processing your request'
        }), 500

@app.route("/accept-changes", methods=['POST'])    
def accept_changes():
    try:
        #implicit positive rating: 1
        PERF_DATA["rating"] = 1
        data = request.json
        dir_s = data.get("structure", "")
        if not dir_s:
            raise Exception("Invalid request from json")
        # cqll implement 
        print(f"Grouped in accept chnages: {GROUPED_FILES}")
        success = implement_changes(GROUPED_FILES)
        # write analytics data to csv
        write_data_to_csv('my_file.csv', PERF_DATA)
        return jsonify({"status": f"Changes implemented successfully {success}"})
    except Exception as e:
        print(f"Error in making changes {e}")
        return jsonify({"error": f"Server error{e}"}), 500
    
def implement_changes(dir_struct, output_path=os.path.join(".", TEMP_DIR)):
    try:    
        print(f"call to implement changes { GROUPED_FILES}")
        for key, value in dir_struct.items():
            label_dir = os.path.join(output_path, key)
            if __debug__:
                print("label_dir: ", label_dir)
            os.makedirs(label_dir, exist_ok=True)
            for initial_path, prop_file in value:
                if __debug__:
                    print(f" {key}: {initial_path} -> {prop_file}")
                shutil.copy(initial_path, label_dir)
                print(f"Moved {initial_path} to {label_dir}")
        return True
    except Exception as e:
        print(f"Error in implementing changes: {e}")
        return False

@app.route("/reject-changes", methods=['POST'])    
def reject_changes():
    try:
        #implicit positive rating: 0
        PERF_DATA["rating"] = 0
        data = request.json
        mes = data.get("message", "")
        if not mes:
            raise Exception("Invalid request from json")
        # call undo 
        success = undo_changes()
         # write analytics data to csv
        write_data_to_csv('my_file.csv', PERF_DATA)
        return jsonify({"status": f"Changes rejected successfully {success}"})
    except Exception as e:
        print(f"Error in making changes {e}")
        return jsonify({"error": f"Server error{e}"}), 500
    
def undo_changes(output_path=os.path.join(".", TEMP_DIR)):
    try:    
        os.removedirs(output_path)
        return True
    except Exception as e:
        print(f"Error in rejecting changes: {e}")
        return False

if __name__ == '__main__':
    app.run()
    # try:
    #     # Try port 5000 first, then 5001 if 5000 is busy
    #     try:
    #         app.run(port=5000)
    #     except OSError:
    #         logger.info("Port 5000 is busy, trying port 5001...")
    #         app.run(port=5001)
    # except Exception as e:
    #     logger.error(f"Failed to start server: {e}")
