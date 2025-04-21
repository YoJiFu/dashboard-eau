import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pyairtable import Table
from datetime import datetime
import time

# ---- Configuration page ----
st.set_page_config(
    page_title="Suivi de l'eau 💧",
    page_icon="💧",
    layout="wide"
)

# ---- Rafraîchissement automatique ----
AUTO_REFRESH_INTERVAL = 300  # 5 minutes

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

elapsed = time.time() - st.session_state["last_refresh"]
remaining = int(AUTO_REFRESH_INTERVAL - elapsed)

# ---- Mot de passe ----
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
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

# ---- Main App ----
if check_password():
    # Petite bannière info
    with st.container():
        st.info("🔄 Rafraîchissement automatique toutes les 5 minutes activé", icon="⏳")

    # Compteur de rafraîchissement
    if remaining > 0:
        st.caption(f"⏳ Prochaine actualisation dans **{remaining}** secondes")
    else:
        st.session_state["last_refresh"] = time.time()
        st.experimental_rerun()

    st.title("💧 Suivi de la consommation d'eau")

    # Connexion à Airtable et chargement sous spinner
    with st.spinner("Chargement des données... 💧"):
        AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
        BASE_ID = st.secrets["BASE_ID"]
        TABLE_NAME = st.secrets["TABLE_NAME"]

        table = Table(AIRTABLE_TOKEN, BASE_ID, TABLE_NAME)

        records = table.all()
        df = pd.DataFrame([{
            "date": r['fields']['date'],
            "volume": r['fields']['volume']
        } for r in records if 'date' in r['fields'] and 'volume' in r['fields']])

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

    if df.empty:
        st.info("Aucune donnée trouvée. Ajoutez votre première mesure 👇")
    else:
        # --- Section Graphique ---
        st.subheader("📈 Évolution de la consommation")
        fig, ax = plt.subplots()
        ax.plot(df['date'], df['volume'], marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Volume (m³)")
        ax.set_title("Consommation d'eau dans le temps")
        ax.grid(True)
        st.pyplot(fig)

        # --- Statistiques jolies ---
        st.subheader("📊 Statistiques globales")
        consommation_totale = df['volume'].iloc[-1] - df['volume'].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Consommation totale", f"{consommation_totale:.3f} m³")
        with col2:
            st.metric("Consommation maximale", f"{df['volume'].max():.3f} m³")
        with col3:
            st.metric("Consommation minimale", f"{df['volume'].min():.3f} m³")
        with col4:
            st.metric("Consommation moyenne", f"{df['volume'].mean():.3f} m³")

        st.divider()

    # --- Formulaire pour ajouter une mesure ---
    st.subheader("➕ Ajouter une nouvelle mesure")
    with st.form(key="ajout_form"):
        nouvelle_date = st.date_input("Date du relevé")
        nouveau_volume = st.number_input("Volume relevé (en m³)", min_value=0.0, step=0.001)
        submit_button = st.form_submit_button(label="Ajouter")

    if submit_button:
        table.create({
            "date": nouvelle_date.strftime('%Y-%m-%d'),
            "volume": float(nouveau_volume)
        })
        st.success(f"✅ Relevé ajouté : {nouvelle_date} - {nouveau_volume} m³")
        st.experimental_rerun()

    # --- Tableau brut et bouton Export CSV ---
    if not df.empty:
        st.subheader("📋 Données brutes")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données au format CSV",
            data=csv,
            file_name='consommation_eau.csv',
            mime='text/csv'
        )
