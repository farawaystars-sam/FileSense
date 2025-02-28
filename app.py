# from src.FileSense import filesense

# if __name__ == "__main__":
#     input_path = "/home/samadiga/Exp/FilseSense v.1.0.0/Data"
#     retured_structure = filesense(input_path)
#     assert retured_structure, "The returned structure is empty:in my func"
#     print(retured_structure)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Allow cross-origin requests (from Electron app)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-domain requests

@app.route("/process", methods=["POST"])
def process_input():
    try:
        data = request.json
        user_input = data.get("user_input", "")

        print(f"🖥️ Received input: {user_input}")
        d = {'user_input': user_input, "response": 1234 }        

        return jsonify(d)
    except Exception as e:
        print(f"❌ Error in processing: {e}")
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
