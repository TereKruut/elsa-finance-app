from konstandid import KULU_KATEGOORIAD, KAUPMEHED
import pandas as pd

KAUPMEES_TO_KATEGOORIA = {
    "Rimi": "Söök ja jook",
    "Selver": "Söök ja jook",
    "Maxima": "Söök ja jook",
    "COOP": "Söök ja jook",
    "Apollo": "Meelelahutus",
    "Elektrum": "Kommunaalid",
    "Tartu Veevärk": "Kommunaalid",
    "LHV": "Laenud",
    # lisa siia veel reegleid, kui tahad
}


def rakenda_kategoriseerimine(df: pd.DataFrame) -> pd.DataFrame:
    """
    Täidab/muudab veeru 'Kategooria' kulukirjete puhul.
    - Kui kasutaja on ise kategooria valinud, seda EI muudeta.
    - Kui kategooria on tühi ja kaupmehele on vaste olemas, kategooria pannakse automaatselt.
    """

    def leia_kategooria(rida):
        # ainult kulud – sissetulekute kategooriaid ei puutu
        if rida.get("Tüüp") != "Kulu":
            return rida.get("Kategooria", "")

        olemasolev = str(rida.get("Kategooria") or "").strip()
        if olemasolev:
            return olemasolev

        kaupmees = str(rida.get("Kaupmees") or "").strip()
        if not kaupmees:
            return olemasolev  # jääb tühjaks

        auto_kat = KAUPMEES_TO_KATEGOORIA.get(kaupmees, "")
        return auto_kat or olemasolev

    if "Kategooria" in df.columns:
        df["Kategooria"] = df.apply(leia_kategooria, axis=1)

    return df
