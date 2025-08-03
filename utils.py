import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".anki_deck_builder")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")


def save_last_folder(folder_path, key="last_folder"):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = load_all_folders()
    data[key] = folder_path
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_last_folder(key="last_folder"):
    data = load_all_folders()
    return data.get(key)


def load_all_folders():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}
