from typing import Dict, List, Tuple

import requests
from owlready2 import *

from common import camel_to_snake_case, BASIC_TYPES

GENERATED_TYPES_FILE_PATH = "generated_graphql_types.py"
OWL_ONTOLOGY_FILES = ["Main.owl", "Properties.owl", "Stimulus.owl", "Models.Measures.Emotion.PAD.owl",
                      "Models.Measures.Emotion.Ekman.owl", "Models.Measures.Emotion.Neutral.owl",
                      "Models.Measures.SignalDependent.EDA.owl", "Models.Appearance.Somatotype.owl",
                      "Models.Appearance.Occlusion.owl", "Models.Personality.BigFive.owl"]


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


def get_owl_files_from_local_directory(owl_root_file_name: str = "owlAC.owl") -> List[str]:
    owl_files = []
    local_path = "C:\\Users\\LocalAdmin\\road"
    for file in os.listdir("C:\\Users\\LocalAdmin\\road"):
        f = os.path.join(local_path, file)
        if os.path.isfile(f) and file.endswith(".owl"):
            owl_files.append(f)

    owl_files.insert(0, owl_files.pop(
        owl_files.index(f"C:\\Users\\LocalAdmin\\road\\{owl_root_file_name}")))
    return owl_files


def get_owl_files_from_road_website() -> List[str]:
    owl_files = []
    for file in OWL_ONTOLOGY_FILES:
        owl_files.append(f"https://road.affectivese.org/documentation/{file}")
    return owl_files


def map_class_from_owl(road_class) -> Dict:
    class_properties = {}
    class_properties["name"] = road_class.name
    class_properties["description"] = str(road_class.comment.first())
    class_properties["fields"] = get_fields_from_owl(road_class)
    class_properties["interfaces"] = get_interfaces_from_owl(road_class)
    class_properties["labels"] = [str(label) for label in road_class.label]
    return class_properties


def get_interfaces_from_owl(road_class) -> List:
    interfaces = ["Thing"]
    for child in road_class.is_a:
        if child.__class__.__name__ == "ThingClass" and child.name != "Thing":
            interfaces.append(child.name)
    return interfaces


def get_fields_from_owl(road_class) -> Dict:
    fields_properties = {}
    for child in road_class.is_a:
        if child.__class__.__name__ == "Restriction":
            if child.property.__class__.__name__ == "Inverse":
                pass  # what to do with inverse? Hopefully nothing
            elif "owlAC" in str(child.value):
                fields_properties[f"{child.property.__name__}"] = child.value.name
            elif "owlAC" not in str(child.value):
                if hasattr(child.value, "name") and child.property.__name__ != "isPartOf":
                    fields_properties[f"{child.property.__name__}"] = child.value.name
                else:
                    field_type = re.search(r"<class '([^']+)'", str(child.value))
                    if field_type and child.property.__name__ != "name":
                        fields_properties[f"{child.property.__name__}"] = field_type.group(1)
    return fields_properties


def get_class_properties_from_specification(class_specification: Dict) -> Tuple[str, str]:
    if "fields" in class_specification:
        unique_properties_str = ""
        for prop_name, prop_type in class_specification['fields'].items():
            converted_prop = camel_to_snake_case(prop_name)
            formatted_str = f"\n    {converted_prop}: {prop_type}"
            unique_properties_str += formatted_str

        unique_input_properties_str = ""
        for prop_name, prop_type in class_specification['fields'].items():
            converted_prop = camel_to_snake_case(prop_name)
            if prop_type in BASIC_TYPES:
                formatted_str = f"\n    {converted_prop}: Optional[{prop_type}] = None"
            else:
                formatted_str = f"\n    {converted_prop}: Optional[{prop_type}Input] = None"
            unique_input_properties_str += formatted_str
        return unique_properties_str, unique_input_properties_str
    return "", ""


def get_class_signature_details_from_specification(class_specification: Dict) -> str:
    if "AbstractClass" in class_specification["labels"]:
        strawberry_header = "@strawberry.interface"
        class_interfaces = ""
    else:
        strawberry_header = "@strawberry.type"
        class_interfaces = "("
        for interface in class_specification["interfaces"]:
            class_interfaces += f"{interface}, "
        class_interfaces = class_interfaces[:-2] + ")"

    if "HighQuantity" in class_specification["labels"]:
        print(f"TODO Implement pagination for class: {class_specification['name']}")
    return strawberry_header, class_interfaces


def create_class_from_specification(class_specification: Dict) -> str:
    unique_properties_str, unique_input_properties_str = get_class_properties_from_specification(class_specification)
    strawberry_header, class_interfaces = get_class_signature_details_from_specification(class_specification)

    class_definition = f"""
{strawberry_header}
class {class_specification["name"]}{class_interfaces}:
    \"""
    {class_specification["description"]}
    \"""
    id: strawberry.ID
    name: str
    additionalParameters: Optional[List[AdditionalParameters]]{unique_properties_str}
    
    
@strawberry.input
class {class_specification["name"]}Input:
    id: Optional[strawberry.ID] = None
    name: Optional[str] = None{unique_input_properties_str}
"""
    return class_definition


def check_if_subclass_exists(ordered_types: List[Dict], value: str) -> bool:
    for ordered_type in ordered_types:
        if value == ordered_type["name"] or value in BASIC_TYPES:
            return True
    return False


def check_if_class_already_exists(road_class: str) -> bool:
    with open(GENERATED_TYPES_FILE_PATH, 'r') as file:
        for line in file.readlines():
            if f"class {road_class}" in line:
                return True
    return False


def order_graphql_types(graphql_types: List[Dict]) -> List[Dict]:
    graphql_types = sorted(graphql_types, key=lambda x: len(x['fields']))
    if len(graphql_types) == 1:
        return graphql_types

    ordered_types = []

    while len(ordered_types) != len(graphql_types):
        for new_type in graphql_types:
            dependencies = new_type["interfaces"].copy()
            if len(new_type['fields']) > 0:
                dependencies += list(new_type['fields'].values())
            if len(dependencies) > 0:
                good_to_go = False
                for value in dependencies:
                    if check_if_subclass_exists(ordered_types=ordered_types, value=value):
                        good_to_go = True
                    elif check_if_class_already_exists(road_class=value):
                        good_to_go = True
                    else:
                        good_to_go = False
                        break
            else:
                good_to_go = True
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


def generate_graphql_types_from_owl(source: str) -> str:
    additional_parameters_spec = f"""
@strawberry.type
class AdditionalParameters:
    \"""
    A set of additional parameters that can be assigned to any ROAD class.
    \"""
    key: str
    value: str\n
    
@strawberry.input
class AdditionalParameterInput:
    key: str = None
    value: str = None\n

@strawberry.interface
class Thing:
    id: strawberry.ID
    name: str
    additionalParameters: Optional[List[AdditionalParameters]]

@strawberry.type
class Dataset(Thing):
    id: strawberry.ID
    name: str\n

@strawberry.input
class DatasetInput:
    name: str = None\n"""
    if os.path.exists(GENERATED_TYPES_FILE_PATH):
        os.remove(GENERATED_TYPES_FILE_PATH)
    with open(GENERATED_TYPES_FILE_PATH, 'a') as file:
        file.write("from typing import List, Optional\n\nimport strawberry\n\n")
        file.write(additional_parameters_spec + '\n')
    print("Initializing complete")

    if source == "github":
        owl_files = get_owl_files_from_github(branch="main")
    elif source == "local":
        owl_files = get_owl_files_from_local_directory()
    elif source == "road.affectivese.org":
        owl_files = get_owl_files_from_road_website()
    else:
        raise Exception("Invalid source. Please choose 'github' or 'road.affectivese.org'")

    print(f"OWL files fetched: {owl_files}")
    for owl_file in owl_files:
        print(f"Processing OWL file: {owl_file}")
        graphql_types_from_owl = process_owl_file(owl_file_path=owl_file)
        save_types_into_file(graphql_types=graphql_types_from_owl)
        print(f"OWL file {owl_file} translated and saved")
    print(f"GraphQL types generated and saved in {GENERATED_TYPES_FILE_PATH}")
    return GENERATED_TYPES_FILE_PATH
