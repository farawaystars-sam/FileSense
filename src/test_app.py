# import flask

from FileSense import filesense


input_path = "/home/samadiga/Exp/FilseSense v.1.0.0/Data"
output_path = "."  # Default to current directory

returned_structure = filesense(input_path)

# returned_structure = filesense(input_path, output_path)

assert returned_structure, "The returned structure is empty"
