from sisestamine import *
from analyysimine import *
from lugemine import *
from selgitamine import *
from abifunktsioonid import prepare_session_df
from konstandid import ALL_COLUMNS
import streamlit as st
import pandas as pd

# --- Üldine seadistus ---
st.set_page_config(page_title="Kulutuste analüüs ELSA", layout="wide")

# Valmistame ette session_state, kui see on tühi
prepare_session_df()

# --- UI: pealkiri ---
st.title("💸 ELSA – Kulude ja sissetulekute jälgimine")

# --- KÜLGRIBA: Andmete laadimine ---
st.sidebar.header("📂 Andmete laadimine")
uploaded_file = st.sidebar.file_uploader(
    "Lae CSV fail (valikuline)", 
    type=["csv"], 
    key="global_upload",
    help="Siit laetud faili kasutatakse kõigis vaadetes."
)

# Kontrollime, kas fail on laetud ja kas see on uus fail (et mitte üle kirjutada manuaalseid sisestusi iga 'rerun'-iga)
if uploaded_file is not None:
    # Kasutame sessiooni olekut, et meeles pidada viimati laetud faili nime
    if "last_loaded_file" not in st.session_state or st.session_state["last_loaded_file"] != uploaded_file.name:
        try:
            df_new = pd.read_csv(uploaded_file, encoding="utf-8")
            
            # Lihtne kontroll ja veergude lisamine
            for col in ALL_COLUMNS:
                if col not in df_new.columns:
                    df_new[col] = "" if col != "Summa" else 0.0
            
            # Salvestame andmed session_state'i
            st.session_state["sisestused_df"] = df_new[ALL_COLUMNS]
            st.session_state["last_loaded_file"] = uploaded_file.name
            
            st.sidebar.success(f"Fail '{uploaded_file.name}' laetud!")
            # Võib-olla soovid lehte värskendada, et andmed kohe ilmuksid
            st.rerun()
            
        except Exception as e:
            st.sidebar.error(f"Viga faili lugemisel: {e}")

# --- KÜLGRIBA: Menüü ---
st.sidebar.markdown("---")
st.sidebar.header("Menüü")
mode = st.sidebar.radio(
    "Mida soovid teha?",
    ["Selgitus", "Failist lugemine", "Kulu / sissetuleku sisestamine", "Analüüs ja graafikud"],
)

# --- VAATED ---
if mode == "Selgitus":
    selgita()

elif mode == "Failist lugemine":
    # Nüüd lihtsalt kuvab andmeid, ei küsi faili
    loe()

elif mode == "Kulu / sissetuleku sisestamine":
    sisesta()

elif mode == "Analüüs ja graafikud":
    # Kasutab mälus olevaid andmeid
    analyysi()
