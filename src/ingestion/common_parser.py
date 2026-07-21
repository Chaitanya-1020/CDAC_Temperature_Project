import json


def read_json_objects(file_path):
    """
    Reads concatenated JSON objects from a file.

    Example file format:

    { ... }
    { ... }
    { ... }

    Returns one JSON object at a time.
    """

    with open(file_path, "r", encoding="utf-8") as file:

        buffer = ""
        brace_count = 0

        for line in file:

            buffer += line

            brace_count += line.count("{")
            brace_count -= line.count("}")

            if brace_count == 0 and buffer.strip():

                yield json.loads(buffer)

                buffer = ""