import ast
import os
from typing import TextIO, Tuple
from common import camel_to_snake_case, BASIC_TYPES

GENERATED_QUERIES_FILE_PATH = "generated_graphql_queries.py"
GENERATED_MUTATIONS_FILE_PATH = "generated_graphql_mutations.py"
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


def generate_file_header(file_type: str, generated_types_file_path: str):
    if file_type == "queries":
        file_path = GENERATED_QUERIES_FILE_PATH
    else:
        file_path = GENERATED_MUTATIONS_FILE_PATH

    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'a') as file:
        file.write("from typing import Optional, List\n\nimport strawberry\n\n")
        resolve_imports(output_file=file, types_file=generated_types_file_path)
        if file_type == "queries":
            file.write("@strawberry.type\nclass GriseraQuery:\n\n")
        else:
            file.write("@strawberry.type\nclass GriseraMutation:\n\n")


def get_property_content(class_property: ast.AnnAssign) -> Tuple[str, str]:
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
    return argument_name, property_type


def generate_graph_queries(generated_types_file_path: str):
    print(f"Generating GraphQL queries...")
    generate_file_header(file_type="queries", generated_types_file_path=generated_types_file_path)
    with open(generated_types_file_path, 'r') as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "AdditionalParameters" not in node.name and "Input" not in node.name:
            with open(GENERATED_QUERIES_FILE_PATH, 'a') as file:
                query_params = "self, dataset_context: DatasetInput, "
                for class_property in node.body:
                    if isinstance(class_property, ast.AnnAssign):
                        if class_property.target.id != "additionalParameters":
                            argument_name, property_type = get_property_content(class_property)
                            query_params = query_params + f"{argument_name}: Optional[{property_type}] = None, "

                query_params += "additional_parameters: Optional[List[AdditionalParameterInput]] = None"

                file.write(
                    f"{indent_builder(size=1)}@strawberry.field\n"
                    f"{indent_builder(size=1)}def get_{camel_to_snake_case(node.name)}({query_params}) -> {node.name}:\n"
                    f"{indent_builder(size=2)}pass\n\n")
    print(f"GraphQL queries generated and saved in {GENERATED_QUERIES_FILE_PATH}")


def generate_graph_mutations(generated_types_file_path: str):
    print(f"Generating GraphQL mutations...")
    generate_file_header(file_type="mutations", generated_types_file_path=generated_types_file_path)
    with open(generated_types_file_path, 'r') as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "AdditionalParameters" not in node.name and "Input" not in node.name:
            with open(GENERATED_MUTATIONS_FILE_PATH, 'a') as file:
                if node.name == "Dataset":
                    delete_parameters = "self, "
                    create_params = "self, "
                    update_parameters = "self, "
                else:
                    create_params = "self, dataset_context: DatasetInput, "
                    update_parameters = "self, dataset_context: DatasetInput, "
                    delete_parameters = "self, dataset_context: DatasetInput, "
                for class_property in node.body:
                    if isinstance(class_property, ast.AnnAssign):
                        if class_property.target.id != "additionalParameters":
                            argument_name, property_type = get_property_content(class_property)
                            if class_property.target.id != "id":
                                create_params = create_params + f"{argument_name}: {property_type}, "
                                update_parameters = update_parameters + f"{argument_name}: Optional[{property_type}] = None, "
                            else:
                                update_parameters = update_parameters + f"{argument_name}: {property_type}, "

                delete_parameters = f"{delete_parameters} name: str" if node.name == "Dataset" else f"{delete_parameters} _id: str"
                create_params += "additional_parameters: Optional[List[AdditionalParameterInput]] = None"
                update_parameters += "additional_parameters: Optional[List[AdditionalParameterInput]] = None"

                file.write(
                    f"{indent_builder(size=1)}@strawberry.mutation\n"
                    f"{indent_builder(size=1)}def create_{camel_to_snake_case(node.name)}({create_params}) -> str:\n"
                    f"{indent_builder(size=2)}pass\n\n"
                )

                file.write(
                    f"{indent_builder(size=1)}@strawberry.mutation\n"
                    f"{indent_builder(size=1)}def delete_{camel_to_snake_case(node.name)}({delete_parameters}) -> str:\n"
                    f"{indent_builder(size=2)}pass\n\n"
                )

                file.write(
                    f"{indent_builder(size=1)}@strawberry.mutation\n"
                    f"{indent_builder(size=1)}def update_{camel_to_snake_case(node.name)}({update_parameters}) -> str:\n"
                    f"{indent_builder(size=2)}pass\n\n"
                )
    print(f"GraphQL mutations generated and saved in {GENERATED_MUTATIONS_FILE_PATH}")
