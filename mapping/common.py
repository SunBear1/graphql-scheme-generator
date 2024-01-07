BASIC_TYPES = ["str", "int", "float", "bool"]


def camel_to_snake_case(name: str):
    snake_case = name[0]
    for idx in range(1, len(name) - 1):
        is_upper = name[idx].isupper()
        followed_by_lower = not name[idx + 1].isupper()
        preceded_by_lower = not name[idx - 1].isupper()
        if (is_upper and followed_by_lower) or (is_upper and preceded_by_lower):
            snake_case += '_'
        snake_case += name[idx]
    snake_case += name[len(name) - 1]  # append last letter
    return snake_case.lower()
