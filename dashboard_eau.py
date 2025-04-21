import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pyairtable import Table
from datetime import datetime

# ---- Paramètres Airtable ----
AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]
DASHBOARD_PASSWORD = st.secrets["PASSWORD"]

# ---- Connexion à Airtable ----
@st.cache_resource
def connect_airtable():
    return Table(AIRTABLE_TOKEN, BASE_ID, TABLE_NAME)

# ---- Fonction de mot de passe ----
def check_password():
    def password_entered():
        if st.session_state["password"] == DASHBOARD_PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Mot de passe :", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Mot de passe :", type="password", on_change=password_entered, key="password")
        st.error("❌ Mot de passe incorrect")
        return False
    else:
        return True

# ---- Main app ----
if check_password():
    st.title("💧 Suivi de la consommation d'eau - Airtable")

    table = connect_airtable()

    # Charger les données
    records = table.all()
    df = pd.DataFrame([{
        "date": r['fields']['date'],
        "volume": r['fields']['volume']
    } for r in records if 'date' in r['fields'] and 'volume' in r['fields']])

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # --- FORMULAIRE pour ajouter une nouvelle mesure ---
    st.subheader("Ajouter une nouvelle mesure 📋")
    with st.form(key="ajout_form"):
        nouvelle_date = st.date_input("Date du relevé")
        nouveau_volume = st.number_input("Volume (en m³)", min_value=0.0, step=0.001)
        submit_button = st.form_submit_button(label="Ajouter")

    if submit_button:
        table.create({
            "date": nouvelle_date.strftime('%Y-%m-%d'),
            "volume": float(nouveau_volume)
        })
        st.success(f"✅ Relevé ajouté : {nouvelle_date} - {nouveau_volume} m³")
        st.experimental_rerun()  # Recharger l'app pour afficher immédiatement la mise à jour

    # Afficher les données
    st.subheader("Données de consommation :")
    st.dataframe(df)

    # Graphique
    st.subheader("Évolution de la consommation d'eau 📈")
    fig, ax = plt.subplots()
    ax.plot(df['date'], df['volume'], marker='o')
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume (m³)")
    ax.set_title("Consommation d'eau dans le temps")
    ax.grid(True)
    st.pyplot(fig)

    # Statistiques rapides
    st.subheader("Statistiques rapides 📊")
    consommation_totale = df['volume'].iloc[-1] - df['volume'].iloc[0]
    st.metric("Consommation totale mesurée", value=f
