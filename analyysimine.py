import pandas as pd
from konstandid import *
from abifunktsioonid import *
from selgitamine import *
from lugemine import *
import matplotlib.pyplot as plt


def analyysi():
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
                    # 1. Filtrid: Tulu/kulu + kuupäevavahemik
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
                        df = df[df["Tulu/kulu"] == "Kulu"]
                    elif tyyp_filter == "Ainult sissetulekud":
                        df = df[df["Tulu/kulu"] == "Tulu"]

                    # Kuupäevavahemik
                    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                        start_date, end_date = date_range
                        mask = (df["Kuupäev"].dt.date >= start_date) & (df["Kuupäev"].dt.date <= end_date)
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

                        # Protsentuaalne jaotus (horisontaalne tulpdiagramm)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.barh(by_cat.index, by_cat.values)
                        ax.set_xlabel("Summa")
                        ax.set_title("Kulu osakaal kategooriate kaupa (%)")
                        plt.tight_layout()
                        st.pyplot(fig)


                        
                        # Arvuline jaotus (tulpdiagramm) – sissetulekud rohelised, kulud punased, väärtused peal
                        fig2, ax2 = plt.subplots(figsize=(10, 5))

                        color_map = []
                        for cat in by_cat.index:
                            
                            cat_type = df[df["Kategooria"] == cat]["Tulu/kulu"].iloc[0]
                        
                            if cat_type == "Tulu":
                                color_map.append("green")
                            else:
                                color_map.append("red")
                        
                        bars = ax2.bar(by_cat.index.astype(str), by_cat.values, color=color_map)
                        
                        # Add numbers above bars
                        for bar in bars:
                            height = bar.get_height()
                            ax2.annotate(
                                f"{height:.0f}",
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 5),
                                textcoords="offset points",
                                ha="center",
                                va="bottom",
                                fontsize=9,
                            )
                        
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
