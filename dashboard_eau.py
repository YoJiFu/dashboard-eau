import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titre de la page
st.title("💧 Suivi de la consommation d'eau")

# Charger les données
@st.cache_data
def load_data():
    return pd.read_csv("eau.csv", parse_dates=["date"])

df = load_data()

# Afficher un aperçu
st.subheader("Données de consommation :")
st.dataframe(df)

# Afficher le graphique
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
st.metric("Consommation maximale", f"{df['volume'].max():.3f} m³")
st.metric("Consommation minimale", f"{df['volume'].min():.3f} m³")
st.metric("Consommation moyenne", f"{df['volume'].mean():.3f} m³")
