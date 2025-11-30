# andmebaas.py
import json
import os

DB_FILE = "kaupmehed_andmebaas.json"

DEFAULT_DB = {
    "categories": [
        "Söök ja jook",
        "Meelelahutus",
        "Kommunaalid",
        "Laenud",
        "Transport",
        "Kodu",
        "Investeeringud",
        "Muu"
    ],
    "merchants": {
        "Rimi": "Söök ja jook",
        "Selver": "Söök ja jook",
        "Maxima": "Söök ja jook",
        "COOP": "Söök ja jook",
        "Bolt": "Söök ja jook",
        "Wolt": "Söök ja jook",
        "Apollo": "Meelelahutus",
        "Spotify": "Meelelahutus",
        "Netflix": "Meelelahutus",
        "Elektrum": "Kommunaalid",
        "Tartu Veevärk": "Kommunaalid",
        "Alexela": "Transport",
        "Circle K": "Transport",
        "IKEA": "Kodu"
    }
}


def load_db():
    """Load DB from JSON, create default if missing."""
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB.copy()
    with open(DB_FILE, encoding="utf-8") as f:
        data = json.load(f)
    # ensure keys exist
    if "categories" not in data:
        data["categories"] = DEFAULT_DB["categories"]
    if "merchants" not in data:
        data["merchants"] = DEFAULT_DB["merchants"]
    return data


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
