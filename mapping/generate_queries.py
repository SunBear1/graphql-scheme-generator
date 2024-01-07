import ast
import os
from typing import TextIO
from common import camel_to_snake_case, BASIC_TYPES

GENERATED_QUERIES_FILE_PATH = "generated_graphql_queries.py"
ACRONYMS = ["PAD"]


def indent_builder(size: int) -> str:
    return "    " * size


def resolve_imports(output_file: TextIO, types_file: str):
    with open(types_file, 'r') as file:
        code = file.read()
    classes = ""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name != "AdditionalParameters":
            classes = classes + f"{node.name}, "
    output_file.write(f"from {types_file[:-3]} import {classes[:-2]}\n\n\n")


def generate_graph_queries(generated_types_file_path: str) -> str:
    print(f"Generating GraphQL queries...")
    if os.path.exists(GENERATED_QUERIES_FILE_PATH):
        os.remove(GENERATED_QUERIES_FILE_PATH)
    with open(GENERATED_QUERIES_FILE_PATH, 'a') as file:
        file.write("import strawberry\n\n")
        resolve_imports(output_file=file, types_file=generated_types_file_path)
        file.write("@strawberry.type\nclass GriseraQuery:\n\n")
    with open(generated_types_file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name != "AdditionalParameters" and "Input" not in node.name:
            with open(GENERATED_QUERIES_FILE_PATH, 'a') as file:
                for class_property in node.body:
                    if isinstance(class_property, ast.AnnAssign) and class_property.target.id != "additionalParameters":
                        property_name = class_property.target.id
                        if property_name == "id":
                            argument_name = "_id"
                            property_type = "str"
                        else:
                            if class_property.annotation.id not in BASIC_TYPES:
                                property_type = f"{class_property.annotation.id}Input"
                            else:
                                property_type = class_property.annotation.id
                            argument_name = camel_to_snake_case(property_name)
                        file.write(f"{indent_builder(size=1)}@strawberry.field\n")
                        file.write(
                            f"{indent_builder(size=1)}def {camel_to_snake_case(node.name)}_by_{camel_to_snake_case(property_name)}"
                            f"(self, {argument_name}: {property_type}) -> {node.name}:\n")
                        file.write(f"{indent_builder(size=2)}pass\n\n")
    print(f"GraphQL queries generated and saved in {GENERATED_QUERIES_FILE_PATH}")
    return GENERATED_QUERIES_FILE_PATH
