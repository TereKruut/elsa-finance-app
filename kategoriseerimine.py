# kategoriseerimine.py
from andmebaas import load_db, save_db


def kategoriseeri(kaupmees: str, olemasolev_kategooria: str) -> str:
    """
    Tagastab lõpliku kategooria väljamineku reale.
    - Kui kasutaja on Kategooria ise valinud (mitte tühi) -> jääb samaks.
    - Kui kategooria on tühi ja kaupmehele on vaste olemas -> kasutatakse automaatset kategooriat.
    - Kui kumbagi pole, tagastab tühja stringi.
    """
    olemasolev = (olemasolev_kategooria or "").strip()
    if olemasolev:
        return olemasolev

    kaup = (kaupmees or "").strip()
    if not kaup:
        return olemasolev  # ei tea midagi, jätame tühjaks

    db = load_db()
    auto = db["merchants"].get(kaup, "")
    return auto or olemasolev
