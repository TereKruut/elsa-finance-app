from abifunktsioonid import *
from konstandid import *
from datetime import datetime
from kategoriseerimine import kategoriseeri
from andmebaas import load_db
import streamlit as st
import pandas as pd

# --- PÕHIFUNKTSIOON ---

def sisesta():
    st.header("✏️ Lisa uus kulu või sissetulek")

    prepare_session_df()
    df_sisestused = st.session_state["sisestused_df"]

    # 1. SISSETULEKUD
    st.markdown("### 1. Lisa uus sissetulek")
    with st.form("lisa_sissetulek_form"):
        kuupäev_sisse = st.date_input("Kuupäev", format="YYYY-MM-DD", key="kuupäev_sisse")
        summa_str_sisse = st.text_input("Summa (näiteks 13.02)", key="summa_sisse")
        kategooria_sisse = st.selectbox("Sissetuleku allikas", TULU_KATEGOORIAD, key="kategooria_sissetulek")
        submitted_sisse = st.form_submit_button("Lisa sissetulek")

    if submitted_sisse:
        try:
            summa_clean = summa_str_sisse.replace(",", ".")
            summa_val = float(summa_clean)
            timestamp = datetime.now().isoformat(timespec="seconds")

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev_sisse.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tulu/kulu": "Tulu",
                "Kategooria": kategooria_sisse,
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )
            st.success("Sissetulek lisatud.")
        except ValueError:
            st.error("Vigane summa. Palun sisesta number (nt 13.02).")

    # ------------------------------------------------------------------
    # 2. VÄLJAMINEKUD
    # ------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Lisa uus väljaminek")

    # Laeme põhiandmebaasi
    db = load_db()
    
    # --- AJUTISED MUUDATUSED SESSIOONIS ---
    # Kui kasutaja on lisanud uue kategooria, hoiame seda ajutiselt meeles, 
    # et ta saaks seda kohe kasutada, isegi kui GitHubi pole veel uuendatud.
    if "temp_merchants" not in st.session_state:
        st.session_state["temp_merchants"] = {}
    if "temp_categories" not in st.session_state:
        st.session_state["temp_categories"] = []

    # Ühendame andmebaasi ja ajutised asjad
    koik_kategooriad = sorted(list(set(db["categories"] + st.session_state["temp_categories"])))
    koik_kaupmehed = sorted(list(set(list(db["merchants"].keys()) + list(st.session_state["temp_merchants"].keys()))))

    # Listid dropdownide jaoks
    kateg_list = [""] + koik_kategooriad
    kaupmehed_list = [""] + koik_kaupmehed

    # --- SOOVIAVALDUSED (Expanderid) ---
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("➕ Kaupmees puudub?"):
            st.caption("Lisa kaupmees ajutiselt ja saada arendajale palve see andmebaasi lisada.")
            uus_kaup = st.text_input("Uus kaupmees", key="req_kaup")
            uus_kaup_kat = st.selectbox("Seosta kategooriaga", kateg_list, key="req_kaup_kat")
            
            if st.button("Kasuta ja teavita arendajat", key="btn_req_kaup"):
                if uus_kaup and uus_kaup_kat:
                    # 1. Lisa ajutiselt sessiooni
                    st.session_state["temp_merchants"][uus_kaup] = uus_kaup_kat
                    # 2. Saada info arendajale
                    success, msg = saada_soov_githubi("Kaupmees", uus_kaup, uus_kaup_kat)
                    if success:
                        st.success(f"Kaupmees '{uus_kaup}' lisatud valikusse! ({msg})")
                        st.rerun()
                    else:
                        st.warning(f"Kaupmees lisatud valikusse, aga teavitamine ebaõnnestus: {msg}")
                        st.rerun()
                else:
                    st.warning("Täida väljad!")

    with col2:
        with st.expander("➕ Kategooria puudub?"):
            st.caption("Lisa kategooria ajutiselt ja saada arendajale palve see andmebaasi lisada.")
            uus_kat = st.text_input("Uus kategooria", key="req_kat")
            
            if st.button("Kasuta ja teavita arendajat", key="btn_req_kat"):
                if uus_kat and uus_kat not in koik_kategooriad:
                    # 1. Lisa ajutiselt sessiooni
                    st.session_state["temp_categories"].append(uus_kat)
                    # 2. Saada info arendajale
                    success, msg = saada_soov_githubi("Kategooria", uus_kat)
                    if success:
                        st.success(f"Kategooria '{uus_kat}' lisatud valikusse! ({msg})")
                        st.rerun()
                    else:
                        st.warning(f"Kategooria lisatud valikusse, aga teavitamine ebaõnnestus: {msg}")
                        st.rerun()
                elif uus_kat in koik_kategooriad:
                    st.warning("See kategooria on juba olemas.")
                else:
                    st.warning("Sisesta nimi.")

    # --- VORM ---
    
    with st.form("lisa_väljaminek_form"):
        kuupäev_välja = st.date_input("Kuupäev", format="YYYY-MM-DD", key="kuupäev_välja")
        summa_str_välja = st.text_input("Summa (näiteks 13.02)", key="summa_välja")

        kaupmees = st.selectbox("Kaupmees (võib jätta tühjaks)", kaupmehed_list, key="kaupmees_väljaminek")
        kategooria_välja = st.selectbox("Kulu kategooria (võib jätta tühjaks)", kateg_list, key="kategooria_kulu")
        
        kirjeldus_välja = st.text_area("Lühikirjeldus (valikuline)", height=80)

        submitted_välja = st.form_submit_button("Lisa väljaminek")

    if submitted_välja:
        try:
            summa_clean = summa_str_välja.replace(",", ".")
            summa_val = float(summa_clean)
            timestamp = datetime.now().isoformat(timespec="seconds")

            # Kategooria loogika:
            # 1. Kasutaja valitud kategooria
            # 2. Ajutine seos sessioonis
            # 3. Püsiv seos andmebaasis
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
            st.success("Kirje lisatud.")
        except ValueError:
            st.error("Vigane summa. Palun sisesta number (nt 13.02).")

    # 3. TABEL
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
