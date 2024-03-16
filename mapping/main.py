from generate_types import generate_graphql_types_from_owl
from generate_methods import generate_graph_queries, generate_graph_mutations

if "__main__" == __name__:
    print("Welcome")
    generated_types_file_path = generate_graphql_types_from_owl(source="local")
    generate_graph_queries(generated_types_file_path=generated_types_file_path)
    generate_graph_mutations(generated_types_file_path=generated_types_file_path)
    print("Done")
