import json
from datetime import datetime

LOG_FILE = "data/logs.json"

def log_request(endpoint, response):
    log_entry = {
        "timestamp": str(datetime.now()),
        "endpoint": endpoint,
        "response": response
    }

    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)