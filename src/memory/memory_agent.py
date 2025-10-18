import json

class MemoryAgent:

    def __init__(self, path):
        self.path = path

    def save_entry(entry):
        with open("history.json", "r") as f:
            data = json.load(f)
        key = entry['Symbol']
        if key in data:
            data[key].append(entry)
        else:
            data[key] = [entry]
        with open("history.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_entires(key):
        with open("history.json", "r") as f:
            data = json.load(f)
        return json[key]