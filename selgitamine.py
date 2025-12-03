import streamlit as st

def selgita():
    """
    Kuvab kasutajale rakenduse tutvustuse ja kasutusjuhendi.
    """
    st.header("💡 ELSA – Kulude jälgimise selgitus")
    st.write(
        "Kes meist ei sooviks paremat ülevaadet enda rahaasjadest? "
        "ELSA on lihtne programm, kuhu saad sisestada oma igapäevased kulud ja sissetulekud. "
        "Programm hoiab kirjeid CSV-failis, lisab neile ajatempli ja kuvab sinu rahakasutust "
        "visuaalselt nii kategooriate kui perioodide kaupa."
    )
    st.write(
        "**Juhised:**\n"
        "1. Lae soovi korral vasakult menüüst üles olemasolev CSV fail.\n"
        "2. Vali **'Sisestamine'**, et lisada uusi tehinguid.\n"
        "3. Kui kaupmeest või kategooriat pole nimekirjas, saad selle ajutiselt lisada ja saata arendajale palve see püsivalt andmebaasi lisada (GitHub Issue).\n"
        "4. Vali **'Analüüs'**, et näha kuhu raha kaob."
    )
