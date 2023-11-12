from typing import Dict, List

from owlready2 import *

onto = get_ontology("https://road.affectivese.org/documentation/owlAC.owl").load()

BASIC_TYPES = ["str", "int", "float", "bool"]


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
                print("skipping inversion...")
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


def order_graphql_types(graphql_types: List[Dict]) -> List[Dict]:
    graphql_types = sorted(graphql_types, key=lambda x: len(x['fields']))
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
                    else:
                        good_to_go = False
                        break
                if good_to_go and new_type not in ordered_types:
                    ordered_types.append(new_type)
    return ordered_types


if "__main__" == __name__:
    types_output_filename = "generated_data_types.py"
    road_classes = list(onto.classes())
    graphql_types = []
    for road_class in road_classes:
        translated_owl_class = map_class_from_owl(road_class)
        graphql_types.append(translated_owl_class)

    graphql_types = order_graphql_types(graphql_types)

    additional_parameters_spec = f"""
@strawberry.type
class AdditionalParameters:
    \"""
    A set of additional parameters that can be assigned to any ROAD class.
    \"""
    key: str
    value: str
"""

    if os.path.exists(types_output_filename):
        os.remove(types_output_filename)
    with open(types_output_filename, 'a') as file:
        file.write("from typing import List, Optional\n\nimport strawberry\n\n")
        file.write(additional_parameters_spec + '\n')
        for _type in graphql_types:
            file.write(create_class_from_specification(class_specification=_type) + '\n')