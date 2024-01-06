from generate_types import generate_graphql_types_from_owl

if "__main__" == __name__:
    print("Welcome")
    generated_types_file_path = generate_graphql_types_from_owl()
    print("Done")
