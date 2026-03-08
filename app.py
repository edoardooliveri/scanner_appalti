import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO

# --- CONFIGURAZIONE ---
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/1HqSEWHR20Nyj5wMU_XcP7F4TxvKGLw2c-Tfhd4QeJOw/edit?usp=sharing"

def leggi_cloud(gid, colonne_default):
    try:
        base_url = URL_FOGLIO.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        res = requests.get(csv_url)
        df = pd.read_csv(StringIO(res.text))
        if df.empty:
            return pd.DataFrame(columns=colonne_default)
        return df
    except:
        return pd.DataFrame(columns=colonne_default)

st.set_page_config(page_title="Scanner Appalti Cloud", layout="wide")

# Caricamento con "Paracadute" (se il foglio è vuoto, crea le colonne giuste)
df_albi = leggi_cloud("0", ["Ente", "URL"])
df_p = leggi_cloud("176166623", ["Parola"])
df_storico = leggi_cloud("729073786", ["Data_Rilevazione", "Ente", "Oggetto", "Link_Diretto", "Archiviato"])

# --- MOTORE DI RICERCA ---
def scansiona_preciso(url_albo, parole):
    risultati = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url_albo, headers=headers, timeout=15)
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

menu = st.sidebar.radio("Navigazione", ["🔍 Scansione", "📥 Dashboard", "⚙️ Configurazione"])

if menu == "🔍 Scansione":
    st.title("Avvia Ricerca")
    if st.button("🚀 ANALIZZA TUTTI I SITI"):
        if df_albi.empty or df_p.empty:
            st.error("Aggiungi dati nel Foglio Google!")
        else:
            bar = st.progress(0)
            for i, row in df_albi.iterrows():
                # Il controllo 'Ente' ora è protetto
                nome_ente = row.get('Ente', 'Sconosciuto')
                st.write(f"Controllo: **{nome_ente}**...")
                
                trovati = scansiona_preciso(row.get('URL', ''), df_p['Parola'].tolist())
                for t in trovati:
                    if t['Link'] not in df_storico['Link_Diretto'].values:
                        st.success(f"Trovato: {t['Oggetto']}")
                bar.progress((i + 1) / len(df_albi))
            st.success("Scansione completata!")

elif menu == "📥 Dashboard":
    st.title("Risultati")
    st.write("Dati caricati dal cloud:")
    st.dataframe(df_storico)

elif menu == "⚙️ Configurazione":
    st.title("Database Cloud")
    st.markdown(f"[🔗 APRI FOGLIO GOOGLE]({URL_FOGLIO})")