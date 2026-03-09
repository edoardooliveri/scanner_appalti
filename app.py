import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

# --- CONFIGURAZIONE ---
SHEET_ID = "1HqSEWHR20Nyj5wMU_XcP7F4TxvKGLw2c-Tfhd4QeJOw"

def leggi_cloud(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        res = requests.get(url)
        if res.status_code != 200:
            return pd.DataFrame()
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

def scansiona_preciso(url_albo, elenco_parole):
    risultati = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # Calcoliamo la base del sito per i link relativi
        parti_url = url_albo.split('/')
        base_site = f"{parti_url[0]}//{parti_url[2]}" 
        
        res = requests.get(url_albo, headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                testo = " ".join(link.get_text().split())
                
                if len(testo) < 5: continue
                
                if any(str(p).lower() in testo.lower() for p in elenco_parole):
                    # Ricostruzione link universale
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = f"{base_site}{href}"
                    else:
                        path_base = url_albo.rsplit('/', 1)[0]
                        full_url = f"{path_base}/{href}"
                    
                    risultati.append({"Oggetto": testo, "Link": full_url})
    except:
        pass
    return risultati

# --- INTERFACCIA ---
st.set_page_config(page_title="Scanner Appalti Cloud", layout="wide")
st.title("🔎 Scanner Appalti Universale")

# Caricamento dati
df_albi = leggi_cloud("0")
df_p = leggi_cloud("176166623")
df_storico = leggi_cloud("729073786")

menu = st.sidebar.radio("Navigazione", ["🔍 Scansione", "📥 Dashboard", "⚙️ Configurazione"])

if menu == "🔍 Scansione":
    st.subheader("Avvia Ricerca sui siti configurati")
    
    if st.button("🚀 ANALIZZA TUTTI I SITI"):
        # Controlliamo che ci siano parole e siti
        if 'parola' in df_p.columns and not df_albi.empty:
            lista_parole = df_p['parola'].dropna().tolist()
            bar = st.progress(0)
            
            for i, row in df_albi.iterrows():
                nome_ente = row.get('ente', f"Sito {i+1}")
                url_sito = row.get('url', '')
                
                st.write(f"Cerco su: **{nome_ente}**...")
                
                if url_sito:
                    trovati = scansiona_preciso(url_sito, lista_parole)
                    if trovati:
                        for t in trovati:
                            # FORMATO CLICCABILE: [Testo](Link)
                            st.success(f"✅ **Trovato:** [{t['Oggetto']}]({t['Link']})")
                    else:
                        st.info(f"Nessun match su {nome_ente}")
                
                bar.progress((i + 1) / len(df_albi))
            st.success("Scansione ultimata!")
        else:
            st.error("Errore: controlla che il Foglio Google abbia le colonne 'Ente', 'URL' e 'Parola'.")

elif menu == "📥 Dashboard":
    st.subheader("Storico Bandi Salvati")
    st.dataframe(df_storico)

elif menu == "⚙️ Configurazione":
    st.subheader("Gestione Database")
    st.write(f"Modifica i dati qui: [Foglio Google](https://docs.google.com/spreadsheets/d/{SHEET_ID})")