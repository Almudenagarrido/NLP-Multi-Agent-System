import json

class MemoryAgent:

    def __init__(self, path):
        self.path = path

    def save_entry(self, entry, key):
        with open(self.path, "r") as f:
            data = json.load(f)
        if key in data:
            data[key].append(entry)
        else:
            data[key] = [entry]
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def load_entries(self, key):
        with open(self.path, "r") as f:
            data = json.load(f)
        if key in data:
            return data[key]
        return []