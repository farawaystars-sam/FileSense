from src.FileSense import filesense

if __name__ == "__main__":
    input_path = "/home/samadiga/Exp/FilseSense v.1.0.0/Data"
    retured_structure = filesense(input_path)
    assert retured_structure, "The returned structure is empty:in my func"
    print(retured_structure)