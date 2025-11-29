import streamlit as st

def selgita():
    st.subheader("Mis probleemi ELSA lahendab?")
    st.write(
        "Kes meist ei sooviks paremat ülevaadet enda rahaasjadest? "
        "ELSA on lihtne programm, kuhu saad sisestada oma igapäevased kulud ja sissetulekud. "
        "Programm hoiab kirjeid CSV-failis, lisab neile ajatembli ja kuvab sinu rahakasutust "
        "visuaalselt nii kategooriate kui perioodide kaupa."
    )
    st.write(
        "Vali vasakult menüüst, kas soovid andmeid sisse lugeda, uusi kirjeid lisada "
        "või kulutusi analüüsida."
    )
