import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

# --- CONFIGURAZIONE ---
# Usa l'ID pulito del foglio
SHEET_ID = "1HqSEWHR20Nyj5wMU_XcP7F4TxvKGLw2c-Tfhd4QeJOw"

def leggi_cloud(gid):
    try:
        # Costruiamo il link di esportazione in modo pulito
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        res = requests.get(url)
        if res.status_code != 200:
            return pd.DataFrame()
        
        df = pd.read_csv(StringIO(res.text))
        # Pulizia estrema: togliamo spazi dai nomi delle colonne e mettiamoli Minuscoli
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Scanner Appalti Cloud", layout="wide")

# Caricamento dati (Usiamo i tuoi GID corretti)
df_albi = leggi_cloud("0")              # Foglio Albi
df_p = leggi_cloud("176166623")         # Foglio Parole
df_storico = leggi_cloud("729073786")    # Foglio Storico

# --- INTERFACCIA ---
st.title("🔎 Scanner Appalti")

# Visualizziamo i dati caricati per capire cosa vede l'app
with st.expander("Verifica Dati Cloud (Debug)"):
    st.write("Colonne Albi trovate:", df_albi.columns.tolist())
    st.write("Colonne Parole trovate:", df_p.columns.tolist())

# Logica di scansione corretta per colonne minuscole
if st.button("🚀 AVVIA SCANSIONE"):
    # Cerchiamo le colonne indipendentemente da come le hai scritte (Ente, ente, ENTE)
    if 'ente' in df_albi.columns and 'url' in df_albi.columns and 'parola' in df_p.columns:
        bar = st.progress(0)
        for i, row in df_albi.iterrows():
            st.write(f"Controllo: **{row['ente']}**...")
            # Qui andrebbe la tua funzione scansiona_preciso...
            bar.progress((i + 1) / len(df_albi))
        st.success("Scansione completata!")
    else:
        st.error("ERRORE: Le colonne nel Foglio Google devono chiamarsi Ente, URL e Parola.")
        st.info(f"L'app vede queste colonne: Albi={df_albi.columns.tolist()}, Parole={df_p.columns.tolist()}")