from konstandid import *

# Kaardistus: kaupmees -> kategooria
KAUPMEES_TO_KATEGOORIA = {
    "Rimi": "Söök ja jook",
    "Selver": "Söök ja jook",
    "Maxima": "Söök ja jook",
    "COOP": "Söök ja jook",
    "Apollo": "Meelelahutus",
    "Elektrum": "Kommunaalid",
    "Tartu Veevärk": "Kommunaalid",
    "LHV": "Laenud",
    # vajadusel lisa siia uusi
}


def kategoriseeri(kaupmees: str, kategooria: str) -> str:
    """
    Tagastab korrektse kategooria väljaminekule.
    - Kui kasutaja valis kategooria käsitsi → seda EI muudeta.
    - Kui kategooria on tühi ja kaupmehele on teada kategooria → määratakse automaatselt.
    - Kui kategooriat ei õnnestu määrata → tagastab tühi string.
    """

    # kui kasutaja on kategooria ise valinud → ära muuda
    if kategooria.strip():
        return kategooria

    # kui kaupmees puudub → ei saa midagi määrata
    if not kaupmees.strip():
        return ""

    # kui kaupmehel on vaste sõnastikus → tagasta see
    return KAUPMEES_TO_KATEGOORIA.get(kaupmees, "")
