import pandas as pd
from abifunktsioonid import puhasta_andmed
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date # Impordi kuupäeva tüüp


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
        # Vältimaks viga kuupäeva min/max leidmisel, kui andmestikus pole ühtegi kehtivat kuupäeva.
        d1_val = date.today()
        d2_val = date.today()

        if "Kuupäev" in df.columns and not df["Kuupäev"].empty:
            try:
                # Proovime leida min/max kehtivat kuupäeva
                min_date = df["Kuupäev"].min()
                max_date = df["Kuupäev"].max()
                
                # Kontrollime, et min ja max ei oleks NaT (Not a Time)
                if pd.notna(min_date) and pd.notna(max_date):
                    d1_val = min_date.date()
                    d2_val = max_date.date()
            except Exception:
                # Kui ebaõnnestub (nt. rikutud andmete tõttu), kasutame vaikimisi tänast kuupäeva
                st.warning("Kuupäevaveerus tekkis viga. Kasutatakse tänast kuupäeva.")
        
        date_range = st.date_input("Vahemik", (d1_val, d2_val))

    # Rakendame filtrid
    if tyyp_filter == "Ainult kulud":
        df = df[df["Tulu/kulu"] == "Kulu"]
    elif tyyp_filter == "Ainult sissetulekud":
        df = df[df["Tulu/kulu"] == "Tulu"]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        # Esmalt tagame, et Kuupäev on date tüüpi enne võrdlemist
        start_date = date_range[0]
        end_date = date_range[1]
        
        # Filtreerime kuupäevade vahemiku järgi (peame võrdlema date objektidega)
        df = df[(df["Kuupäev"].dt.date >= start_date) & (df["Kuupäev"].dt.date <= end_date)]


    if df.empty:
        st.warning("Valitud filtritega andmeid ei leitud.")
        return

    # --- ÜLEVAADE KATEGOORIATE KAUPA ---
    st.markdown("### 2. Kogupilt kategooriate kaupa")

    # Grupeerime kategooriad ja summeerime
    by_cat = df.groupby(["Kategooria", "Tulu/kulu"])["Summa"].sum().unstack(fill_value=0)
    
    # Loome värvikaardi: Tulu (roheline) ja Kulu (punane)
    final_df = pd.DataFrame({
        'Summa': by_cat.sum(axis=1),
        'Tüüp': by_cat.idxmax(axis=1) # Määrab, kas tegu oli valdavalt Tulu või Kuluga
    }).sort_values(by='Summa', ascending=False)
    
    st.write(f"**Kokku valitud perioodil:** {final_df['Summa'].sum():.2f} €")
    st.dataframe(final_df)

    # --- GRAAFIK (Vertikaalne tulpdiagramm) ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Määrame värvid final_df põhjal
    color_map = final_df['Tüüp'].apply(lambda x: "green" if x == "Tulu" else "red").tolist()

    bars = ax.bar(final_df.index.astype(str), final_df['Summa'].values, color=color_map)

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
    
    valitav_cat_options = final_df.index.tolist()
    if not valitav_cat_options:
        st.info("Kategooria valimiseks pole andmeid.")
        return

    valitav_cat = st.selectbox("Vali kategooria detailideks", valitav_cat_options)
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
        
        # Leiame kategooria värvi final_df-st
        cat_type = final_df.loc[valitav_cat, 'Tüüp']
        cat_color = "green" if cat_type == "Tulu" else "red"
        
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
