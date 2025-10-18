import json

def save_query(path, entry):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
