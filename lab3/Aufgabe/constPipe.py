HOST = "127.0.0.1"

SPLIT_ENDPOINT = f"tcp://{HOST}:50011"

MAPPER_ENDPOINTS = [
    f"tcp://{HOST}:50012",
    f"tcp://{HOST}:50013",
    f"tcp://{HOST}:50014"
]

REDUCER_ENDPOINTS = [
    f"tcp://{HOST}:50015",
    f"tcp://{HOST}:50016",
]