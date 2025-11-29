import streamlit as st
import pandas as pd

def loe():
    st.header("📂 Loe CSV-faili sisu")

    uploaded_file = st.file_uploader("Vali CSV-fail", type=["csv"], key="read_file")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
            st.success(f"Fail loetud: {uploaded_file.name}")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Faili lugemisel tekkis viga: {e}")
    else:
        st.info("Palun vali CSV-fail, mida soovid vaadata.")