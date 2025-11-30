# kategoriseerimine.py

from konstandid import KULU_KATEGOORIAD, KAUPMEHED

def kategoriseeri(kaupmees: str, olemasolev_kategooria: str, mappings: dict) -> str:
    """
    Tagastab lõpliku kategooria väljamineku reale.
    """
    olemasolev = (olemasolev_kategooria or "").strip()
    if olemasolev:
        return olemasolev

    kaup = (kaupmees or "").strip()
    if not kaup:
        return ""

    return mappings.get(kaup, "")
