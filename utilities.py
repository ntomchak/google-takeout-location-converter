import os, json
from datetime import datetime

def timestamp_to_datetime(timestamp):
    timestamp = timestamp.replace("Z", "+00:00")
    return datetime.fromisoformat(timestamp)
    
def json_from_path(path):
    if os.path.isfile(path):
        with open(path, 'r', encoding="utf8") as file:
            return json.load(file)