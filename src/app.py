from FileSense import filesense
# if __name__ == "__main__":
#     input_path = "/home/samadiga/Exp/FilseSense v.1.0.0/Data"
#     retured_structure = filesense(input_path)
#     assert retured_structure, "The returned structure is empty:in my func"
#     print(retured_structure)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Allow cross-origin requests (from Electron app)
import os

TEMP_DIR = "tmp"
GROUPED_FILES = {}

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-domain requests

def get_dir_structure(dir_path):
    dir_structure = {}
    
    for root, _, files in os.walk(dir_path):
        relative_root = os.path.relpath(root, dir_path)
        if relative_root == ".":
            dir_structure[relative_root] = [f for f in files]
        else:
            dir_structure[relative_root] = [os.path.join(relative_root, f) for f in files]
    
    return dir_structure

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


@app.route("/process", methods=["POST"])
def process_input():
    try:
        data = request.json
        user_input = data.get("user_input", "")

        print(f"🖥️ Received input: {user_input}")
        # calling filesense function
        retured_structure = filesense(user_input)
        global GROUPED_FILES 
        GROUPED_FILES = retured_structure
        print(f"Grouped files :{GROUPED_FILES}")
        data_for_b = {}
        for label, file_tup in retured_structure.items():
            for ini_p, new_p in file_tup:
                print( f" in app.py {ini_p} -> {new_p}, {label}")
                if label not in data_for_b:
                    data_for_b[label] = []
                data_for_b[label].append(new_p)        

        print(f"Returned structure: {data_for_b}")      

        return jsonify(data_for_b)
    except Exception as e:
        print(f"❌ Error in processing: {e}")
        return jsonify({"error": "Server error"}), 500
    
@app.route("/accept-changes", methods=['POST'])    
def accept_changes():
    try:
        data = request.json
        dir_s = data.get("structure", "")
        if not dir_s:
            raise Exception("Invalid request from json")
        # cqll implement 
        print(f"Grouped in accept chnages: {GROUPED_FILES}")
        implement_changes(GROUPED_FILES)
        return jsonify({"message": "Changes implemented successfully"})
    except Exception as e:
        print(f"Error in making changes {e}")
        return jsonify({"error": f"Server error{e}"}), 500
    
def implement_changes(dir_struct, output_path=os.path.join(".", TEMP_DIR)):
    print(f"call to implement changes { GROUPED_FILES}")
    for key, value in dir_struct.items():
        for initial_path, prop_file in value:
            print(f" {key}: {initial_path} -> {prop_file}")

    return True

if __name__ == "__main__":
    app.run(debug=True)
