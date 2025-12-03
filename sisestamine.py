from abifunktsioonid import prepare_session_df
from datetime import datetime
from andmebaas import load_db, TULU_KATEGOORIAD
import streamlit as st
import pandas as pd


def sisesta():
    st.header("✏️ Lisa uus kulu või sissetulek")

    prepare_session_df()

    # ------------------------------------------------------------------
    # 1. SISSETULEKUD
    # ------------------------------------------------------------------
    st.markdown("### 1. Lisa uus sissetulek")

    with st.form("lisa_sissetulek_form"):
        kuupäev_sisse = st.date_input("Kuupäev")
        summa_str_sisse = st.text_input("Summa (näiteks 13.02)")
        kategooria_sisse = st.selectbox("Sissetuleku allikas", TULU_KATEGOORIAD)
        submitted_sisse = st.form_submit_button("Lisa sissetulek")

    if submitted_sisse:
        try:
            summa_val = float(summa_str_sisse.replace(",", "."))
            timestamp = datetime.now().isoformat(timespec="seconds")

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev_sisse.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tulu/kulu": "Tulu",
                "Kategooria": kategooria_sisse,
                "Kaupmees": "",
                "Kirjeldus": "",
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )

            st.success("✅ Sissetulek lisatud.")

        except ValueError:
            st.error("❌ Vigane summa. Palun sisesta number (nt 13.02).")

    # ------------------------------------------------------------------
    # 2. VÄLJAMINEKUD
    # ------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Lisa uus väljaminek")

    db = load_db()

    # Ajutised sessioonimuudatused
    if "temp_merchants" not in st.session_state:
        st.session_state["temp_merchants"] = {}
    if "temp_categories" not in st.session_state:
        st.session_state["temp_categories"] = []

    koik_kategooriad = sorted(list(set(db["categories"] + st.session_state["temp_categories"])))
    koik_kaupmehed = sorted(
        list(set(list(db["merchants"].keys()) + list(st.session_state["temp_merchants"].keys())))
    )

    kateg_list = [""] + koik_kategooriad
    kaupmehed_list = [""] + koik_kaupmehed

    with st.form("lisa_valjaminek_form"):
        kuupäev_välja = st.date_input("Kuupäev")
        summa_str_välja = st.text_input("Summa (näiteks 13.02)")
        kaupmees = st.selectbox("Kaupmees (valikuline)", kaupmehed_list)
        kategooria_välja = st.selectbox("Kulu kategooria (valikuline)", kateg_list)
        kirjeldus_välja = st.text_area("Lühikirjeldus (valikuline)", height=80)

        submitted_välja = st.form_submit_button("Lisa väljaminek")

    if submitted_välja:
        try:
            summa_val = float(summa_str_välja.replace(",", "."))
            timestamp = datetime.now().isoformat(timespec="seconds")

            kategooria_lõplik = kategooria_välja

            if kaupmees and not kategooria_lõplik:
                if kaupmees in st.session_state["temp_merchants"]:
                    kategooria_lõplik = st.session_state["temp_merchants"][kaupmees]
                elif kaupmees in db["merchants"]:
                    kategooria_lõplik = db["merchants"][kaupmees]
                else:
                    kategooria_lõplik = "Määramata"

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev_välja.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tulu/kulu": "Kulu",
                "Kategooria": kategooria_lõplik,
                "Kaupmees": kaupmees,
                "Kirjeldus": kirjeldus_välja,
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )

            st.success("✅ Väljaminek lisatud.")

        except ValueError:
            st.error("❌ Vigane summa.")

    # ------------------------------------------------------------------
    # 3. TABEL + CSV
    # ------------------------------------------------------------------
    if not st.session_state["sisestused_df"].empty:
        st.markdown("---")
        st.markdown("### 3. Praegune CSV sisu")

        st.dataframe(st.session_state["sisestused_df"])

        csv_bytes = st.session_state["sisestused_df"].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Laadi alla CSV-fail",
            data=csv_bytes,
            file_name="elsa_kirjed.csv",
            mime="text/csv",
        )
    else:
        st.info("Kirjeid pole veel lisatud.")
