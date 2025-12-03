from sisestamine import sisesta
from analyysimine import analyysi
from lugemine import loe
from selgitamine import selgita
from abifunktsioonid import prepare_session_df
from andmebaas import ALL_COLUMNS
import streamlit as st
import pandas as pd

# --- Üldine seadistus (Pealkiri ja paigutus) ---
st.set_page_config(page_title="Kulutuste analüüs ELSA", layout="wide")

# Valmistame ette session_state (andmete hoidla)
prepare_session_df()

st.title("💸 ELSA – Kulude ja sissetulekute jälgimine")

# --- KÜLGRIBA: Andmete laadimine ---
st.sidebar.header("📂 Lae CSV")
uploaded = st.sidebar.file_uploader("Vali fail (valikuline)", type=["csv"], key="global")

# Faili lugemise loogika
if uploaded:
    # Kontrollime, kas see fail on juba laetud
    if "last_loaded" not in st.session_state or st.session_state["last_loaded"] != uploaded.name:
        try:
            df = pd.read_csv(uploaded)
            # Tagame, et kõik vajalikud veerud oleksid olemas
            for c in ALL_COLUMNS:
                if c not in df.columns: 
                    df[c] = 0.0 if c=="Summa" else ""
            
            # Salvestame andmed sessiooni mällu
            st.session_state["sisestused_df"] = df[ALL_COLUMNS]
            st.session_state["last_loaded"] = uploaded.name
            st.sidebar.success("Fail laetud!")
            st.rerun() # Värskendame lehte
        except Exception as e:
            st.sidebar.error(f"Viga faili lugemisel: {e}")

# --- KÜLGRIBA: Navigatsioonimenüü ---
st.sidebar.markdown("---")
valik = st.sidebar.radio("Menüü", ["Selgitus", "Failist lugemine", "Sisestamine", "Analüüs"])

# --- VAATED ---
if valik == "Selgitus": 
    selgita()
elif valik == "Failist lugemine": 
    loe()
elif valik == "Sisestamine": 
    sisesta()
elif valik == "Analüüs": 
    analyysi()
