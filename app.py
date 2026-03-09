def scansiona_preciso(url_albo, elenco_parole):
    risultati = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Identifichiamo la base del sito (es: https://albo.esempio.it)
    # serve per i link che iniziano con "/"
    parti_url = url_albo.split('/')
    base_site = f"{parti_url[0]}//{parti_url[2]}" 

    try:
        res = requests.get(url_albo, headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Cerchiamo tutti i link nella pagina
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                testo = " ".join(link.get_text().split()) # Pulisce spazi e invii a capo
                
                if len(testo) < 5: continue # Ignora link senza testo
                
                # Controllo parole chiave
                if any(str(p).lower() in testo.lower() for p in elenco_parole):
                    # --- RICOSTRUZIONE LINK UNIVERSALE ---
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = f"{base_site}{href}"
                    else:
                        # Se il link è relativo (es: dettaglio.php), lo incolla all'URL base
                        path_base = url_albo.rsplit('/', 1)[0]
                        full_url = f"{path_base}/{href}"
                    
                    risultati.append({"Oggetto": testo, "Link": full_url})
    except Exception as e:
        print(f"Errore su {url_albo}: {e}")
    return risultati

# --- PARTE DELLA VISUALIZZAZIONE NELL'INTERFACCIA ---
# Sostituisci il pezzo dentro "if st.button('🚀 ANALIZZA TUTTI I SITI'):"
if st.button("🚀 ANALIZZA TUTTI I SITI"):
    # ... (caricamento parole come già fatto) ...
    bar = st.progress(0)
    for i, row in df_albi.iterrows():
        ente_attuale = row.get('ente', f"Sito {i+1}")
        st.write(f"🔍 Controllo: **{ente_attuale}**...")
        
        trovati = scansiona_preciso(row.get('url', ''), lista_parole)
        
        if trovati:
            for t in trovati:
                # CREA IL LINK CLICCABILE (Markdown)
                # La sintassi [Testo](URL) rende il testo blu e cliccabile
                st.success(f"✅ **Trovato:** [{t['Oggetto']}]({t['Link']})")
        else:
            st.info(f"Nessun match trovato su {ente_attuale}")
            
        bar.progress((i + 1) / len(df_albi))
    st.success("Scansione completata!")