import matplotlib.pyplot as plt
from konstandid import *
from abifunktsioonid import *
from selgitamine import *
from lugemine import *

# --- Üldine seadistus ---
st.set_page_config(page_title="Kulutuste analüüs ELSA", layout="wide")

# --- UI: pealkiri ja menüü ---

st.title("💸 ELSA – Kulude ja sissetulekute jälgimine")

st.sidebar.header("Menüü")
mode = st.sidebar.radio(
    "Mida soovid teha?",
    ["Selgitus", "Failist lugemine", "Kulu / sissetuleku sisestamine", "Analüüs ja graafikud"],
)

# --- Selgitus / probleemikirjeldus ---
if mode == "Selgitus":
    selgita()

# --- CSV lugemine (Failist lugeda) ---
elif mode == "Failist lugemine":
    loe()

# --- CSV loomine / kirjutamine (Faili kirjutada) ---

elif mode == "Kulu / sissetuleku sisestamine":
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

    # 2. Uue kirje sisestamine
    st.markdown("### 2. Lisa uus kirje")

    # Kirje tüüp peab olema VORMIST VÄLJAS
    tyyp = st.radio("Kirje tüüp", ["Kulu", "Sissetulek"], key="kirje_tyyp")

    with st.form("lisa_kirje_form"):
        kuupäev = st.date_input("Kuupäev", format="YYYY-MM-DD")
        summa_str = st.text_input("Summa (näiteks 13.02)")

        # NÜÜD valime kategooria vastavalt tyyp väärtusele
        if tyyp == "Sissetulek":
            kategooria = st.selectbox(
                "Sissetuleku kategooria",
                TULU_KATEGOORIAD,
                key="kategooria_sissetulek",
            )
        else:
            kategooria = st.selectbox(
                "Kulu kategooria",
                KULU_KATEGOORIAD,
                key="kategooria_kulu",
            )

        kaupmees = st.text_input("Kaupmees / allikas (valikuline)")
        kirjeldus = st.text_area("Lühikirjeldus (valikuline)", height=80)

        submitted = st.form_submit_button("Lisa kirje")

    if submitted:
        try:
            summa_clean = summa_str.replace(",", ".")
            summa_val = float(summa_clean)

            from datetime import datetime
            timestamp = datetime.now().isoformat(timespec="seconds")

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tüüp": tyyp,
                "Kategooria": kategooria,
                "Kaupmees": kaupmees,
                "Kirjeldus": kirjeldus,
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )
            st.success("Kirje lisatud.")
        except ValueError:
            st.error("Vigane summa. Palun sisesta number (nt 13.02).")


    # 3. Näita hetkeandmeid + 4. võimalus CSV luua/uuendada
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

# --- Analüüs / graafikud (Analüüsida kulutusi) ---

elif mode == "Analüüs ja graafikud":
    st.header("📊 Analüüs ja graafikud")

    uploaded_analysis = st.file_uploader(
        "Vali CSV-fail analüüsiks", type=["csv"], key="analysis_file"
    )

    if uploaded_analysis is not None:
        try:
            df_raw = pd.read_csv(uploaded_analysis, encoding="utf-8")
        except Exception as e:
            st.error(f"Faili lugemisel tekkis viga: {e}")
        else:
            if df_raw.empty:
                st.warning("Fail on tühi.")
            else:
                df, eemaldatud = puhasta_andmed(df_raw)

                if eemaldatud > 0:
                    st.warning(
                        f"Hoiatus: {eemaldatud} rida eemaldati vigaste andmete tõttu."
                    )

                if df.empty:
                    st.error("Pärast puhastust ei jäänud ühtegi kehtivat rida.")
                else:
                    # 1. Filtrid: tüüp + kuupäevavahemik
                    st.markdown("### 1. Filtrid")

                    col1, col2 = st.columns(2)

                    with col1:
                        tyyp_filter = st.selectbox(
                            "Millist tüüpi kirjeid vaadata?",
                            ["Kõik", "Ainult kulud", "Ainult sissetulekud"],
                        )

                    with col2:
                        min_date = df["Kuupäev"].min().date()
                        max_date = df["Kuupäev"].max().date()
                        date_range = st.date_input(
                            "Vali kuupäevavahemik",
                            (min_date, max_date),
                            format="YYYY-MM-DD",
                        )

                    # Tüübifilter
                    if tyyp_filter == "Ainult kulud":
                        df = df[df["Tüüp"] == "Kulu"]
                    elif tyyp_filter == "Ainult sissetulekud":
                        df = df[df["Tüüp"] == "Sissetulek"]

                    # Kuupäevavahemik
                    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                        start_date, end_date = date_range
                        mask = (
                            df["Kuupäev"].dt.date >= start_date
                        ) & (df["Kuupäev"].dt.date <= end_date)
                        df = df[mask]

                    if df.empty:
                        st.warning("Filtrite järel andmeid ei jäänud.")
                    else:
                        # 2. Kogupilt kategooriate kaupa (protsent + arv)
                        st.markdown("### 2. Kogupilt kategooriate kaupa")

                        by_cat = (
                            df.groupby("Kategooria")["Summa"]
                            .sum()
                            .sort_values(ascending=False)
                        )
                        total = by_cat.sum()

                        summary = pd.DataFrame(
                            {
                                "Summa": by_cat,
                                "Osakaal %": (by_cat / total * 100).round(1),
                            }
                        )

                        st.write("Kokku:", float(total))
                        st.dataframe(summary)

                        # Protsentuaalne jaotus (pie)
                        fig1, ax1 = plt.subplots(figsize=(6, 6))
                        ax1.pie(by_cat, labels=by_cat.index, autopct="%1.1f%%", startangle=90)
                        ax1.axis("equal")
                        st.pyplot(fig1)

                        # Arvuline jaotus (tulpdiagramm)
                        fig2, ax2 = plt.subplots(figsize=(8, 4))
                        ax2.bar(by_cat.index.astype(str), by_cat.values)
                        ax2.set_ylabel("Summa")
                        ax2.set_title("Summa kategooriate kaupa")
                        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
                        st.pyplot(fig2)

                        # 3. Detailne vaade ühe kategooria ajas (päev/nädal/kuu/kvartal/aasta)
                        st.markdown("### 3. Ajavahemiku analüüs ühe kategooria kaupa")

                        valitav_kategooria = st.selectbox(
                            "Vali kategooria detailsema vaate jaoks",
                            options=by_cat.index,
                        )

                        ajavahemiku_valik = st.selectbox(
                            "Vali ajavahemik:",
                            options=["Päev", "Nädal", "Kuu", "Kvartal", "Aasta"],
                        )

                        df_kat = df[df["Kategooria"] == valitav_kategooria]

                        if not df_kat.empty:
                            if ajavahemiku_valik == "Päev":
                                jaotus = df_kat.groupby(
                                    df_kat["Kuupäev"].dt.date
                                )["Summa"].sum()
                            elif ajavahemiku_valik == "Nädal":
                                jaotus = df_kat.groupby(
                                    df_kat["Kuupäev"].dt.to_period("W")
                                )["Summa"].sum()
                            elif ajavahemiku_valik == "Kuu":
                                jaotus = df_kat.groupby(
                                    df_kat["Kuupäev"].dt.to_period("M")
                                )["Summa"].sum()
                            elif ajavahemiku_valik == "Kvartal":
                                jaotus = df_kat.groupby(
                                    df_kat["Kuupäev"].dt.to_period("Q")
                                )["Summa"].sum()
                            elif ajavahemiku_valik == "Aasta":
                                jaotus = df_kat.groupby(
                                    df_kat["Kuupäev"].dt.to_period("Y")
                                )["Summa"].sum()
                            else:
                                jaotus = None

                            if jaotus is not None and not jaotus.empty:
                                labels = jaotus.index.astype(str)

                                fig3, ax3 = plt.subplots(figsize=(10, 4))
                                ax3.bar(labels, jaotus.values)
                                ax3.set_title(
                                    f"{valitav_kategooria} – {ajavahemiku_valik} lõikes"
                                )
                                ax3.set_xlabel(ajavahemiku_valik)
                                ax3.set_ylabel("Summa")
                                plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")
                                st.pyplot(fig3)
                            else:
                                st.info(
                                    "Selles kategoorias pole valitud perioodi lõikes andmeid."
                                )
                        else:
                            st.info("Valitud kategoorias pole andmeid.")
    else:
        st.info("Palun vali CSV-fail analüüsiks.")
