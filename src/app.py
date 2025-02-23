from flask import Flask, jsonify
from FileSense import filesense

app = Flask(__name__)

def my_func():
    input_path = "/home/samadiga/Exp/FilseSense v.1.0.0/Data"
    retured_structure = filesense(input_path)
    assert retured_structure, "The returned structure is empty:in my func"
    return retured_structure
    
@app.route("/process", methods=["GET"])
def process():
    response = my_func()
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

