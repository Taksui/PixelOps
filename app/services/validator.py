def validate_input(query: str):
    return bool(query.strip())

def validate_output(response: dict):
    return "temperature" in response