import pandas as pd
from abifunktsioonid import puhasta_andmed
import matplotlib.pyplot as plt
import streamlit as st

def analyysi():
    """
    Genereerib statistika ja graafikud sisestatud andmete põhjal.
    Kasutab rohelist värvi tulude ja punast kulude jaoks.
    """
    st.header("📊 Analüüs ja graafikud")

    if "sisestused_df" not in st.session_state or st.session_state["sisestused_df"].empty:
        st.info("Andmed puuduvad. Palun lae fail või sisesta andmed.")
        return

    # Andmete puhastamine
    df_raw = st.session_state["sisestused_df"].copy()
    df, eemaldatud = puhasta_andmed(df_raw)

    if eemaldatud > 0:
        st.warning(f"Hoiatus: {eemaldatud} vigast rida eemaldati analüüsist.")

    if df.empty:
        st.warning("Analüüsiks pole piisavalt andmeid.")
        return

    # --- FILTRID ---
    st.markdown("### 1. Filtrid")
    col1, col2 = st.columns(2)

    with col1:
        tyyp_filter = st.selectbox("Tüüp", ["Kõik", "Ainult kulud", "Ainult sissetulekud"])
    
    with col2:
        d1 = df["Kuupäev"].min().date()
        d2 = df["Kuupäev"].max().date()
        date_range = st.date_input("Vahemik", (d1, d2))

    # Rakendame filtrid
    if tyyp_filter == "Ainult kulud":
        df = df[df["Tulu/kulu"] == "Kulu"]
    elif tyyp_filter == "Ainult sissetulekud":
        df = df[df["Tulu/kulu"] == "Tulu"]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        df = df[(df["Kuupäev"].dt.date >= date_range[0]) & (df["Kuupäev"].dt.date <= date_range[1])]

    if df.empty:
        st.warning("Valitud filtritega andmeid ei leitud.")
        return

    # --- ÜLEVAADE KATEGOORIATE KAUPA ---
    st.markdown("### 2. Kogupilt kategooriate kaupa")

    by_cat = df.groupby("Kategooria")["Summa"].sum().sort_values(ascending=False)
    
    st.write(f"**Kokku valitud perioodil:** {by_cat.sum():.2f} €")
    st.dataframe(by_cat)

    # --- GRAAFIK (Vertikaalne tulpdiagramm) ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Määrame värvid: Tulu=Roheline, Kulu=Punane, Muu=Hall
    color_map = []
    for cat in by_cat.index:
        sample = df[df["Kategooria"] == cat]
        if not sample.empty:
            tüüp = sample["Tulu/kulu"].iloc[0]
            color_map.append("green" if tüüp == "Tulu" else "red")
        else:
            color_map.append("gray")

    bars = ax.bar(by_cat.index.astype(str), by_cat.values, color=color_map)

    # Kirjutame numbrid tulpade kohale
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.0f}", 
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5), textcoords="offset points",
            ha="center", va="bottom", fontsize=10
        )

    ax.set_ylabel("Summa (€)")
    ax.set_title("Summa kategooriate kaupa")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)

    # --- DETAILNE AJALINE VAADE ---
    st.markdown("### 3. Ajaline vaade")
    
    valitav_cat = st.selectbox("Vali kategooria detailideks", by_cat.index)
    periood = st.selectbox("Periood", ["Päev", "Nädal", "Kuu", "Aasta"])
    
    df_cat = df[df["Kategooria"] == valitav_cat]
    
    if not df_cat.empty:
        # Grupeerime vastavalt valitud perioodile
        periood_map = {
            "Päev": df_cat["Kuupäev"].dt.date, 
            "Nädal": df_cat["Kuupäev"].dt.to_period("W"),
            "Kuu": df_cat["Kuupäev"].dt.to_period("M"),
            "Aasta": df_cat["Kuupäev"].dt.to_period("Y")
        }
        
        jaotus = df_cat.groupby(periood_map[periood])["Summa"].sum()
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        
        # Leiame kategooria värvi põhigraafikult
        cat_idx = list(by_cat.index).index(valitav_cat)
        cat_color = color_map[cat_idx]
        
        bars2 = ax2.bar(jaotus.index.astype(str), jaotus.values, color=cat_color)
        
        # Numbrid peale
        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(f"{height:.0f}", 
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 5), textcoords="offset points",
                         ha="center", va="bottom", fontsize=9)

        ax2.set_title(f"{valitav_cat} ({periood})")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Valitud kategoorias andmed puuduvad.")
