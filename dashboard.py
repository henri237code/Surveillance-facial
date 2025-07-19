import streamlit as st
import sqlite3
import pandas as pd

# Identifiant
USERNAME = "admin"
PASSWORD = "ia2"

st.title("Connexion")

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if username == USERNAME and password == PASSWORD:
    st.success("Connecté avec succès ")

    # Connexion et création automatique de la base et table
    conn = sqlite3.connect('detections.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            date_heure TEXT
        )
    ''')
    conn.commit()

    #  Lecture des données
    df = pd.read_sql_query("SELECT * FROM detection", conn)

    st.title(" Dashboard Surveillance IA2")

    if df.empty:
        st.info("Aucune détection enregistrée pour le moment.")
    else:
        noms = ["Tous"] + sorted(df['nom'].unique().tolist())
        selected_nom = st.selectbox("Filtrer par nom", noms)

        if selected_nom != "Tous":
            df = df[df["nom"] == selected_nom]

        st.subheader(" Historique des détections")
        st.dataframe(df)

        #  Graphique
        st.subheader(" Statistiques")
        stats = df['nom'].value_counts().rename_axis('Nom').reset_index(name='Nombre')
        st.bar_chart(stats.set_index('Nom'))

else:
    st.warning("Veuillez entrer les identifiants corrects")
