from typing import Dict, List
import requests
from owlready2 import *

BASIC_TYPES = ["str", "int", "float", "bool"]
GENERATED_TYPES_FILE_PATH = "generated_data_types.py"


def get_owl_files_from_github(branch: str, owl_root_file_name: str = "owlAC.owl") -> List[str]:
    owl_files = []
    url = f"https://api.github.com/repos/GRISERA/road/git/trees/{branch}?recursive=1"
    response = requests.get(url)
    response_json = response.json()
    if "tree" not in response_json:
        raise Exception(f"Error fetching OWL files from GitHub: {response_json}")

    for gh_file in response_json["tree"]:
        if gh_file["path"].endswith(".owl"):
            owl_files.append(f"https://raw.githubusercontent.com/GRISERA/road/{branch}/{gh_file['path']}")

    owl_files.insert(0, owl_files.pop(
        owl_files.index(f"https://raw.githubusercontent.com/GRISERA/road/{branch}/{owl_root_file_name}")))
    return owl_files


def map_class_from_owl(road_class) -> Dict:
    class_properties = {}
    class_properties["name"] = road_class.name
    class_properties["description"] = str(road_class.comment[0])
    class_properties["fields"] = get_fields(road_class)
    return class_properties


def get_fields(road_class) -> Dict:
    fields_properties = {}
    for child in road_class.is_a:
        if child.__class__.__name__ == "ThingClass" and child.name != "Thing":
            fields_properties[f"{child.name}"] = child.name
        if child.__class__.__name__ == "Restriction":
            if child.property.__class__.__name__ == "Inverse":
                pass  # what to do with inverse? Hopefully nothing
            elif "owlAC" in str(child.value):
                fields_properties[f"{child.property.__name__}"] = child.value.name
            elif "owlAC" not in str(child.value):
                field_type = re.search(r"<class '([^']+)'", str(child.value))
                fields_properties[f"{child.property.__name__}"] = field_type.group(1)
    return fields_properties


def create_class_from_specification(class_specification: Dict) -> str:
    if class_specification["fields"] is not None:
        unique_properties_str = "".join(
            [f"\n    {prop}: {prop_type}" for prop, prop_type in class_specification['fields'].items()])
    else:
        unique_properties_str = ""
    class_definition = f"""
@strawberry.type
class {class_specification["name"]}:
    \"""
    {class_specification["description"]}
    \"""
    id: strawberry.ID
    name: str
    additionalParameters: Optional[List[AdditionalParameters]]{unique_properties_str}
"""
    return class_definition


def check_if_subclass_exists(ordered_types: List[Dict], value: str) -> bool:
    for ordered_type in ordered_types:
        if value in ordered_type["name"] or value in BASIC_TYPES:
            return True
    return False


def check_if_class_already_exists(road_class: str) -> bool:
    with open(GENERATED_TYPES_FILE_PATH, 'r') as file:
        for line in file.readlines():
            if f"class {road_class}:" in line:
                return True
    return False


def order_graphql_types(graphql_types: List[Dict]) -> List[Dict]:
    graphql_types = sorted(graphql_types, key=lambda x: len(x['fields']))
    if len(graphql_types) == 1:
        return graphql_types

    ordered_types = []
    for _type in graphql_types:
        if len(_type['fields']) == 0:
            ordered_types.append(_type)

    while len(ordered_types) != len(graphql_types):
        for new_type in graphql_types:
            if len(new_type['fields']) > 0:
                good_to_go = False
                for value in new_type['fields'].values():
                    if check_if_subclass_exists(ordered_types=ordered_types, value=value):
                        good_to_go = True
                    elif check_if_class_already_exists(road_class=value):
                        good_to_go = True
                    else:
                        good_to_go = False
                        break
                if good_to_go and new_type not in ordered_types:
                    ordered_types.append(new_type)
    return ordered_types


def process_owl_file(owl_file_path: str) -> List[Dict]:
    onto = get_ontology(owl_file_path).load()
    road_classes = list(onto.classes())
    graphql_types = []
    for road_class in road_classes:
        if check_if_class_already_exists(road_class.name):
            continue
        translated_owl_class = map_class_from_owl(road_class)
        graphql_types.append(translated_owl_class)

    graphql_types = order_graphql_types(graphql_types)
    return graphql_types


def save_types_into_file(graphql_types: List[Dict]):
    with open(GENERATED_TYPES_FILE_PATH, 'a') as graphql_types_file:
        for graphql_type in graphql_types:
            graphql_types_file.write(create_class_from_specification(class_specification=graphql_type) + '\n')


def generate_graphql_types_from_owl() -> str:
    additional_parameters_spec = f"""
    @strawberry.type
    class AdditionalParameters:
        \"""
        A set of additional parameters that can be assigned to any ROAD class.
        \"""
        key: str
        value: str
        """
    if os.path.exists(GENERATED_TYPES_FILE_PATH):
        os.remove(GENERATED_TYPES_FILE_PATH)
    with open(GENERATED_TYPES_FILE_PATH, 'a') as file:
        file.write("from typing import List, Optional\n\nimport strawberry\n\n")
        file.write(additional_parameters_spec + '\n')
    print("Initializing complete")

    owl_files = get_owl_files_from_github(branch="main")
    print(f"OWL files fetched: {owl_files}")
    for owl_file in owl_files:
        print(f"Processing OWL file: {owl_file}")
        graphql_types_from_owl = process_owl_file(owl_file_path=owl_file)
        save_types_into_file(graphql_types=graphql_types_from_owl)
        print(f"OWL file {owl_file} translated and saved")
    return GENERATED_TYPES_FILE_PATH
