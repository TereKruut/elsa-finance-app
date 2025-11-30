from abifunktsioonid import *
from konstandid import *
from datetime import datetime
from kategoriseerimine import kategoriseeri
from andmebaas import load_db, save_db


def sisesta():
    st.header("✏️ Lisa uus kulu või sissetulek")

    prepare_session_df()
    df_sisestused = st.session_state["sisestused_df"]

    # 1. Võimalus alustada olemasolevast failist
    st.markdown("### 1. Alusta olemasolevast failist (valikuline)")

    uploaded_base = st.file_uploader(
        "Lae olemasolev CSV, et jätkata sinna lisamist",
        type=["csv"],
        key="write_base",
    )

    if uploaded_base is not None and df_sisestused.empty:
        try:
            df_base = pd.read_csv(uploaded_base, encoding="utf-8")

            # Tagame, et kõigil veergudel on koht
            for col in ALL_COLUMNS:
                if col not in df_base.columns:
                    df_base[col] = "" if col != "Summa" else 0.0

            df_base = df_base[ALL_COLUMNS]
            st.session_state["sisestused_df"] = df_base
            df_sisestused = df_base

            st.success("Olemasolev fail laetud.")
        except Exception as e:
            st.error(f"Faili lugemisel tekkis viga: {e}")

    # 2. Uue sissetuleku sisestamine
    st.markdown("### 2. Lisa uus sissetulek")

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

    # 3. Uue väljamineku sisestamine
    st.markdown("### 2. Lisa uus väljaminek")

    # ----------------------------------------------
    # FIXED: proper indentation inside form
    # ----------------------------------------------

    with st.form("lisa_väljaminek_form"):
        # inputs inside the form
        kuupäev_välja = st.date_input("Kuupäev", format="YYYY-MM-DD", key="kuupäev_välja")
        summa_str_välja = st.text_input("Summa (näiteks 13.02)", key="summa_välja")

        # load dynamic DB
        db = load_db()
        kategooriad = db["categories"]
        kaupmehed_map = db["merchants"]
        kaupmehed_list = sorted([""] + list(kaupmehed_map.keys()))
        kateg_list = sorted([""] + kategooriad)

        # allow adding new merchant
        kaupmees = st.selectbox("Kaupmees (võib jätta tühjaks)", kaupmehed_list, key="kaupmees_väljaminek")

        if st.checkbox("Lisa uus kaupmees", key="lisa_uus_kaupmees_checkbox"):
            uus_kaup = st.text_input("Sisesta uus kaupmees", key="uus_kaupmees_input")
            if uus_kaup:
                uus_kateg = st.selectbox("Seosta kaupmees kategooriaga", [""] + kateg_list, key="uus_kaup_kateg")
                if st.button("Salvesta uus kaupmees", key="salvesta_uus_kaupmees"):
                    if uus_kaup in kaupmehed_map:
                        st.warning("Kaupmees juba olemas")
                    else:
                        if uus_kateg == "":
                            st.warning("Vali kategooria või lisa uus kategooria esimesena")
                        else:
                            kaupmehed_map[uus_kaup] = uus_kateg
                            save_db(db)
                            st.success(f"Kaupmees '{uus_kaup}' lisatud kategooriasse '{uus_kateg}'")
                            st.experimental_rerun()

        kategooria_välja = st.selectbox("Kulu kategooria (võib jätta tühjaks)", kateg_list, key="kategooria_kulu")

        if st.checkbox("Lisa uus kategooria", key="lisa_uus_kateg_checkbox"):
            uus_k = st.text_input("Sisesta uus kategooria", key="uus_kateg_input")
            if st.button("Salvesta uus kategooria", key="salvesta_uus_kateg"):
                if uus_k and uus_k not in kategooriad:
                    kategooriad.append(uus_k)
                    save_db(db)
                    st.success(f"Kategooria '{uus_k}' lisatud")
                    st.experimental_rerun()
                else:
                    st.warning("Kategooria on tühi või juba olemas")

        kirjeldus_välja = st.text_area("Lühikirjeldus (valikuline)", height=80)

        submitted_välja = st.form_submit_button("Lisa väljaminek")

    # ----------------------------------------------
    # End of form – validation happens outside the form
    # ----------------------------------------------

    if submitted_välja:
        kaupmees_täidetud = bool(kaupmees.strip())
        kategooria_täidetud = bool(kategooria_välja.strip())

        if not kaupmees_täidetud and not kategooria_täidetud:
            st.error("Palun vali vähemalt kaupmees või kategooria.")
        else:
            try:
                summa_clean = summa_str_välja.replace(",", ".")
                summa_val = float(summa_clean)
                timestamp = datetime.now().isoformat(timespec="seconds")

                kategooria_lõplik = kategoriseeri(kaupmees, kategooria_välja)

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

    # 4. Näita hetkeandmeid + CSV
    if not st.session_state["sisestused_df"].empty:
        st.markdown("### 3. Praegune CSV sisu")
        st.dataframe(st.session_state["sisestused_df"])

        st.markdown("### 4. Laadi CSV alla (loo / uuenda fail)")
        csv_bytes = st.session_state["sisestused_df"].to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Laadi alla CSV-fail",
            data=csv_bytes,
            file_name="elsa_kirjed.csv",
            mime="text/csv",
        )
    else:
        st.info("Kirjeid pole veel lisatud.")
