# andmebaas.py
import json
import os

DEFAULT_DB = {
    "categories": [
        "Söök ja jook",
        "Meelelahutus",
        "Kommunaalid",
        "Laenud",
        "Transport",
        "Kodu",
        "Investeeringud",
        "Muu",
        "Laps"
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
        "IKEA": "Kodu",
        "Swedbank": "Laenud",
        "LHV": "Laenud", 
        "SEB": "Laenud", 
        "III sammas": "Investeeringud",
        "Lapse riided": "Laps",
        "Riided": "Muu",
        "Mikroinvesteerimine": "Investeeringud"
    }
}

def load_db():
    return DEFAULT_DB
