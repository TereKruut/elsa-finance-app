from konstandid import ALL_COLUMNS
import pandas as pd
import streamlit as st

# --- Abifunktsioonid ---

def prepare_session_df():
    """Loob tühja DataFrame'i õige veerustruktuuriga, kui seda veel ei ole."""
    if "sisestused_df" not in st.session_state:
        st.session_state["sisestused_df"] = pd.DataFrame(columns=ALL_COLUMNS)


def puhasta_andmed(df: pd.DataFrame):
    """
    - Tagab, et kõik vajalikud veerud on olemas
    - Teeb tüübid korda
    - Eemaldab vead / tühjad read
    """
    # Lisa puuduolevad veerud
    for col in ALL_COLUMNS:
        if col not in df.columns:
            if col == "Summa":
                df[col] = 0.0
            else:
                df[col] = ""

    # Timestamp ja kuupäev
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    if "Kuupäev" in df.columns:
        df["Kuupäev"] = pd.to_datetime(df["Kuupäev"], errors="coerce")
    else:
        df["Kuupäev"] = df["Timestamp"].dt.date
        df["Kuupäev"] = pd.to_datetime(df["Kuupäev"], errors="coerce")

    # Summa numbriks
    df["Summa"] = pd.to_numeric(df["Summa"], errors="coerce")

    # Eemaldame selgelt vigased read
    df.dropna(subset=["Kuupäev", "Summa"], inplace=True)

    df["Kategooria"].fillna("Määramata", inplace=True)

    if "Tulu/kulu" not in df.columns or df["Tulu/kulu"].eq("").all():
        df["Tulu/kulu"] = "Määramata"

    algne = len(df)
    df = df[df["Summa"] != 0]
    eemaldatud = algne - len(df)

    return df, eemaldatud