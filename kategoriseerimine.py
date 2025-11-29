from konstandid import KULU_KATEGOORIAD, KAUPMEHED

# Kaardistus: kaupmees -> kulukategooria
KAUPMEES_TO_KATEGOORIA = {
    "Rimi": "Söök ja jook",
    "Selver": "Söök ja jook",
    "Maxima": "Söök ja jook",
    "COOP": "Söök ja jook",
    "Apollo": "Meelelahutus",
    "Elektrum": "Kommunaalid",
    "Tartu Veevärk": "Kommunaalid",
    "LHV": "Laenud",
    # vajadusel lisa siia veel
}


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

    auto = KAUPMEES_TO_KATEGOORIA.get(kaup, "")
    return auto or olemasolev
