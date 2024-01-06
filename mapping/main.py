from generate_types import generate_graphql_types_from_owl
from mapping.generate_queries import generate_graph_queries

if "__main__" == __name__:
    print("Welcome")
    generated_types_file_path = generate_graphql_types_from_owl()
    generate_graph_queries(generated_types_file_path=generated_types_file_path)
    print("Done")
