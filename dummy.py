# import sys

# print("hello")
# print(sys.version)

from flask import Flask, jsonify

app = Flask(__name__)

file_tree = {
    "folder1": "folder1/file1.txt",
    "folder1/subfolder1": "folder1/subfolder1/file2.txt",
    "folder2": "folder2/file3.txt",
    "folder2/subfolder2": "folder2/subfolder2/file4.txt",
    "folder3": "folder3/file5.txt",
}

@app.route('/get_tree_data')
def get_tree_data():
    return jsonify(file_tree)

if __name__ == '__main__':
    app.run(debug=True)
