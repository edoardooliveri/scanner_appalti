import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import StringIO

# --- CONFIGURAZIONE GOOGLE SHEETS ---
# 1. Crea un foglio Google con tre fogli (schede): "Albi", "Parole", "Storico"
# 2. Condividilo come "Editor" con "Chiunque abbia il link"
# 3. Incolla il link qui sotto
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/1HqSEWHR20Nyj5wMU_XcP7F4TxvKGLw2c-Tfhd4QeJOw/edit?usp=sharing"

def leggi_cloud(gid):
    try:
        base_url = URL_FOGLIO.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        res = requests.get(csv_url)
        return pd.read_csv(StringIO(res.text))
    except:
        return pd.DataFrame()

# Funzione per salvare (ti servirà per l'archiviazione e aggiunta siti)
def salva_cloud():
    st.info("💡 Per salvare modifiche permanenti (aggiunta siti/parole), usa direttamente il Foglio Google. I tasti 'Aggiungi' qui sotto funzioneranno solo per la sessione corrente finché non collegheremo le API di scrittura.")

# --- INTERFACCIA ---
st.set_page_config(page_title="Scanner Appalti Cloud", layout="wide")

# Carichiamo i dati dai GID (0 è il primo foglio, gli altri li trovi nell'URL del browser)
# Sostituisci i numeri qui sotto con quelli del tuo foglio Google
df_albi = leggi_cloud("0") # GID Foglio Albi
df_p = leggi_cloud("176166623") # GID Foglio Parole
df_storico = leggi_cloud("729073786") # GID Foglio Storico

# --- MOTORE DI RICERCA (IL TUO ORIGINALE) ---
def scansiona_preciso(url_albo, parole):
    risultati = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url_albo, headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                testo = " ".join(link.get_text().split())
                href = link['href']
                if len(testo) < 10: continue
                for p in parole:
                    if str(p).lower() in testo.lower():
                        if not href.startswith('http'):
                            base = "/".join(url_albo.split("/")[:3])
                            full_url = base + (href if href.startswith('/') else '/' + href)
                        else: full_url = href
                        risultati.append({"Oggetto": testo, "Link": full_url})
    except: pass
    return risultati

menu = st.sidebar.radio("Navigazione", ["🔍 Scansione", "📥 Dashboard (7gg)", "⚙️ Configurazione"])

if menu == "🔍 Scansione":
    st.title("Avvia Ricerca Automatica")
    if st.button("🚀 ANALIZZA TUTTI I SITI"):
        bar = st.progress(0)
        nuovi_ritrovamenti = []
        for i, row in df_albi.iterrows():
            st.write(f"Controllo: **{row['Ente']}**...")
            trovati = scansiona_preciso(row['URL'], df_p['Parola'].tolist())
            for t in trovati:
                # Verifica se già presente nello storico cloud
                if t['Link'] not in df_storico['Link_Diretto'].values:
                    st.success(f"Nuovo trovato: {t['Oggetto']}")
                    # Qui dovresti aggiungere la logica di scrittura su Sheets (opzionale se leggi solo)
            bar.progress((i + 1) / len(df_albi))
        st.success("Scansione completata!")

elif menu == "📥 Dashboard (7gg)":
    st.title("Risultati Cloud")
    # Mostra i dati dello storico caricati da Google Sheets
    st.table(df_storico)

elif menu == "⚙️ Configurazione":
    st.title("Database Cloud")
    st.write("Per gestire i siti e le parole, usa il link di Google Sheets:")
    st.markdown(f"[🔗 APRI FOGLIO GOOGLE]({URL_FOGLIO})")
    st.write("I dati appariranno qui automaticamente al prossimo aggiornamento.")