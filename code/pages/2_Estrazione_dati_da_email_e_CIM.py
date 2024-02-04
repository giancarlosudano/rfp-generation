import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import base64
import datetime
import glob
import json
import openai
import os
import requests
import sys
import re

def get_override(folder, variable_name):
	variabili = {}
	with open(os.path.join('ldv', folder, 'override.txt'), 'r') as file:
		for riga in file:
			# Rimozione degli spazi bianchi e dei caratteri di nuova linea
			riga = riga.strip()
			# Controllo se la riga non è vuota
			if riga:
				# Divisione della riga in base al segno '='
				chiave, valore = riga.split('=')
				# Aggiunta della coppia chiave-valore al dizionario
				variabili[chiave] = valore
	return variabili[variable_name]

def read_field_from_cim(my_bar):
	if st.session_state['box-01'] == "":
		from azure.core.credentials import AzureKeyCredential
		from azure.ai.formrecognizer import DocumentAnalysisClient
		endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
		key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
		model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
		model_id = "ldv6-neural"
		document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

		with open(os.path.join('ldv', st.session_state['ldv'], "cim.jpg"),'rb') as f:
			poller = document_analysis_client.begin_analyze_document(model_id, document=f)
		result = poller.result()

		for idx, document in enumerate(result.documents):
			for name, field in document.fields.items():
				st.session_state[name] = field.value

		llm = AzureChatOpenAI(
			azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
			api_key=os.getenv("AZURE_OPENAI_KEY"),
			api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
			max_tokens=1000, 
			temperature=0,
			deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
			model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
			streaming=False
		)

		my_bar.progress(int((1) / 30 * 100), text="Elaborazione Mittente")
		st.session_state["box-01-clean"] = prompt_for_box("1", "Estrai dal testo solo la ragione sociale del mittente della CIM", st.session_state["box-01"], llm)

		my_bar.progress(int((2) / 30 * 100), text="Elaborazione Mittente Codice 1")
		st.session_state["box-02-clean"] = prompt_for_box("2", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-02"], llm)

		my_bar.progress(int((3) / 30 * 100), text="Elaborazione Mittente Codice 2")
		st.session_state["box-03-clean"] = prompt_for_box("3", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-03"], llm)

		my_bar.progress(int((4) / 30 * 100), text="Elaborazione Destinatario")
		st.session_state["box-04-clean"] = prompt_for_box("4", "Estrai dal testo solo la denominazione o ragione sociale", st.session_state["box-04"], llm)

		my_bar.progress(int((5) / 30 * 100), text="Elaborazione Destinatario Codice 1")
		st.session_state["box-05-clean"] = prompt_for_box("5", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-05"], llm)

		my_bar.progress(int((6) / 30 * 100), text="Elaborazione Destinatario Codice 1")
		st.session_state["box-06-clean"] = prompt_for_box("6", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-06"], llm)

		my_bar.progress(int((7) / 30 * 100), text="Elaborazione Luogo di consegna")
		st.session_state["box-10-clean"] = prompt_for_box("10", "Estrai solo le informazioni di un luogo di consegna della CIM", st.session_state["box-10"], llm)

		my_bar.progress(int((8) / 30 * 100), text="Elaborazione Luogo di consegna codice")
		st.session_state["box-11-clean"] = prompt_for_box("11", "Estrai dal testo un codice alfanumerico che rappresenta il codice di una stazione di destinazione della CIM", st.session_state["box-11"], llm)

		my_bar.progress(int((9) / 30 * 100), text="Elaborazione Destinazione")
		st.session_state["box-12-clean"] = prompt_for_box("12", "Estrai dal testo un codice alfanumerico. Se il codice inizia con 2 cancella il 2. Se inizia con 12 cancella il 12.", st.session_state["box-12"], llm)

		my_bar.progress(int((10) / 30 * 100), text="Elaborazione Destinazione Codice")
		st.session_state["box-13-clean"] = prompt_for_box("13", "Estrai dal testo le informazioni più importanti", st.session_state["box-13"], llm)

		my_bar.progress(int((11) / 30 * 100), text="Elaborazione box 14")
		st.session_state["box-14-clean"] = prompt_for_box("14", "Estrai dal testo un codice numerico che rappresenta un codice della CIM", st.session_state["box-14"], llm)

		my_bar.progress(int((12) / 30 * 100), text="Elaborazione box 16")
		st.session_state["box-16-clean"] = prompt_for_box("16", "Estrai le informazioni di un luogo di presa in carico della CIM", st.session_state["box-16"], llm)

		my_bar.progress(int((13) / 30 * 100), text="Elaborazione box 16 orario")
		st.session_state["box-16-orario-clean"] = prompt_for_box("16", "Interpreta la stringa come una data di presa in carico della CIM, eventualmente anche data e orario", st.session_state["box-16-orario"], llm)

		my_bar.progress(int((14) / 30 * 100), text="Elaborazione 17")
		st.session_state["box-17-clean"] = prompt_for_box("17", "Interpreta la stringa come una data di presa in carico della CIM, eventualmente anche data e orario", st.session_state["box-17"], llm)		

		my_bar.progress(int((15) / 30 * 100), text="Elaborazione 18")
		st.session_state["box-18-clean"] = prompt_for_box("18", "Estrai le informazioni dal testo", st.session_state["box-18"], llm)

		my_bar.progress(int((16) / 30 * 100), text="Elaborazione 19")
		st.session_state["box-19-1-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1"], llm)

		my_bar.progress(int((17) / 30 * 100), text="Elaborazione 19")
		st.session_state["box-19-2-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1"], llm)

		st.session_state["box-23"] = get_override(st.session_state['ldv'], "box-23")
		st.session_state["box-23-clean"] = get_override(st.session_state['ldv'], "box-23")

		my_bar.progress(int((18) / 30 * 100), text="Elaborazione 24")
		st.session_state["box-24-clean"] = prompt_for_box("24", "Estrai una sequenza di uno o più codici numerici. Se incontri il testo NHM non considerarlo.", st.session_state["box-24"], llm)

		my_bar.progress(int((19) / 30 * 100), text="Elaborazione 25")
		st.session_state["box-25-clean"] = prompt_for_box("25", "Interpreta le informazioni dal testo, che sono dei pesi di vagoni. Estrai se lo trovi il totale della massa.", st.session_state["box-25"], llm)

		my_bar.progress(int((21) / 30 * 100), text="Elaborazione 29")
		st.session_state["box-29-clean"] = prompt_for_box("29", "Interpreta le informazioni di luogo e data della CIM", st.session_state["box-29"], llm)

		my_bar.progress(int((22) / 30 * 100), text="Elaborazione 49")
		st.session_state["box-49-clean"] = prompt_for_box("49", "Estrai dal testo un codice numerico composto eventualmente da più parti. ", st.session_state["box-49"], llm)

		my_bar.progress(int((23) / 30 * 100), text="Elaborazione 57")
		st.session_state["box-57-clean"] = prompt_for_box("57", "Nel testo ci sono informazioni di trasporti, con indirizzi e percorsi. Estrai tutte le informazioni che riesci a leggere in modo ordinato. ", st.session_state["box-57"], llm)

		my_bar.progress(int((24) / 30 * 100), text="Elaborazione 62 1")
		st.session_state["box-62-paese-clean"] = prompt_for_etichetta("62", "Estrai dal testo un codice numerico di due cifre", st.session_state["box-62-paese"], llm)

		my_bar.progress(int((25) / 30 * 100), text="Elaborazione 62 2")
		st.session_state["box-62-stazione-clean"] = prompt_for_etichetta("62", "Estrai dal testo un codice numerico o alfanumerico", st.session_state["box-62-stazione"], llm)

		my_bar.progress(int((26) / 30 * 100), text="Elaborazione 62 3")
		st.session_state["box-62-impresa-clean"] = prompt_for_etichetta("62", "Estrai dal testo un codice numerico o alfanumerico", st.session_state["box-62-impresa"], llm)

		my_bar.progress(int((27) / 30 * 100), text="Elaborazione 62 4")
		st.session_state["box-62-spedizione-clean"] = prompt_for_etichetta("62", "Estrai dal testo un codice numerico o alfanumerico", st.session_state["box-62-spedizione"], llm)

		my_bar.progress(int((28) / 30 * 100), text="Elaborazione 62 luogo (da 29)")
		st.session_state["box-62-luogo-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni del luogo.", st.session_state["box-29"], llm)

		my_bar.progress(int((29) / 30 * 100), text="Elaborazione 62 luogo (da 29)")
		st.session_state["box-62-data-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni della data. Il risultato deve essere in questo formato: YYYYMMDD. Ignora eventualmente l'orario", st.session_state["box-29"], llm)

	return

def prompt_for_box(numero_casella: str, descrizione_estrazione: str, box: str, llm: AzureChatOpenAI):
	prompt_base = """il testo delimitato da ### deriva da una scansione OCR di un modulo di trasporto ferroviario CIM internazionale. 
Il testo deriva da una casella che ha come numero iniziale {numero_casella} e che può contenere la descrizione della casella stessa.
###
{box}
###

{descrizione_estrazione}
- Non aggiungere altro alla risposta
- Se il testo inizia con il numero della casella non includerlo nella risposta
- Se non trovi nessun codice o nessuna informazione, scrivi "Non trovato"

Esempio 
- se la casella è la 29 e il testo è "29 800400500" la risposta sarà "80400500"
- se la casella è la 19 e il testo è "19 Ragione Sociale xxx yyy" la risposta sarà "Ragione Sociale xxx yyy"

Risposta:
"""

	output_parser = StrOutputParser()
	system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da una testo analizzato con OCR da documenti CIM utilizzati nel trasporto ferroviario internazionale di merci."
	prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])
	chain = prompt | llm | output_parser
	response = chain.invoke({"input": prompt_base.format(numero_casella=numero_casella, descrizione_estrazione=descrizione_estrazione, box=box)})
	
	return response


def prompt_for_etichetta(numero_casella: str, descrizione_estrazione: str, box: str, llm: AzureChatOpenAI):
	prompt_base = """il testo delimitato da ### deriva da una scansione OCR di un modulo di trasporto ferroviario CIM internazionale. 

###
{box}
###

{descrizione_estrazione}
- pulisci il testo da eventuali caratteri non alfanumerici come , . - o spazi
- Non aggiungere altro alla risposta
- Se non trovi nessun codice o nessuna informazione, scrivi "Non trovato"

Risposta:
"""

	output_parser = StrOutputParser()
	system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da una testo analizzato con OCR da documenti CIM utilizzati nel trasporto ferroviario internazionale di merci."
	prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])
	chain = prompt | llm | output_parser
	response = chain.invoke({"input": prompt_base.format(numero_casella=numero_casella, descrizione_estrazione=descrizione_estrazione, box=box)})
	
	return response

try:
	st.set_page_config(page_title="Mercitalia - Automazione LdV / RdS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Estrazione dati da email e allegati")
	st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)
	load_dotenv()

	import streamlit_authenticator as stauth	
	import yaml
	from yaml.loader import SafeLoader

	with open('config.yaml') as file:
		config = yaml.load(file, Loader=SafeLoader)

	authenticator = stauth.Authenticate(
		config['credentials'],
		config['cookie']['name'],
		config['cookie']['key'],
		config['cookie']['expiry_days'],
		config['preauthorized']
	)

	if st.session_state["authentication_status"]:		
		st.image(os.path.join('images','Slide2.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema recupera informazioni relative a:
- contenuto specifico della e-mail (compreso mittente ed oggetto)
- allegati PDF o Excel (che vengono convertiti in immagini)

Successivamente viene utilizzato un **modello di training AI, opportunamente allenato su documenti CIM** (standard internazionale), **per estrarre le informazioni più importanti dalla lettera di vettura**. 
Viene utilizzato anche **GPT4-Vision** assieme al servizio complementare **Azure AI Vision per estrarre informazioni dai documenti di dettaglio dei vagoni**, in quanto rappresentano tabelle "dense", con formati estremamente variabili. 
I dati estratti dalle CIM vengono passati al **servizio GPT4 per una pulizia ulteriore del testo**.

### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa
- **Azure Blob Storage**: Servizio di storage per file/blob ad alta scalabilità
- **Azure OpenAI**: Servizio di Large Language Model con modelli GPT4-Turbo e GPT-4-Vision
- **Azure Document Intelligence**: Servizio di AI per l'analisi di documenti, utilizzato un Custom Extraction Model per la CIM
""")
		# Recupero Allegati e presentazione
		file_cim = os.path.join('ldv', st.session_state['ldv'], 'cim.jpg')
		st.write("cim file: {}".format(file_cim))	
		st.image(file_cim, use_column_width=True)
  
		# Recupero Dati Email
		file_msg = os.path.join('ldv', st.session_state['ldv'], 'msg_data.txt')
		with open(file_msg, 'r') as file:
			content = file.read()
			from_pattern = r"from: (.+)"
			from_match = re.search(from_pattern, content)
			from_value = from_match.group(1) if from_match else None
			subject_pattern = r"subject: (.+)"
			subject_match = re.search(subject_pattern, content)
			subject_value = subject_match.group(1) if subject_match else None
			body_match = re.search(r'body:([\s\S]+)', content)
			body_value = body_match.group(1).strip()

		expander_email = st.expander("Email", expanded=True)
		expander_email.text_input("Da:", value=from_value, key="from_email")
		expander_email.text_input("Oggetto:", value=subject_value, key="email_subject")
		expander_email.text_area("Corpo", height=150, value=body_value, key="email_body")
		expander_email.info("Possibili estrazioni")
		expander_email.text_area("Estrazioni", height=100, value="", key="email_extraction")
		# -------

		progress_text = "Lettura dati da allegati e chiamate a GPT4..."
		my_bar = st.progress(0, text=progress_text)
		read_field_from_cim(my_bar)
  
		st.info("Dati estratti dalla CIM")
  
		with st.form("my_form"):

			colbox1_1, colbox1_2 = st.columns([1,1])	
			with colbox1_1:
				st.text_area("(1) Mittente", value=st.session_state["box-01"], disabled=True, height=150, key="box1_1")
			with colbox1_2:
				st.text_area("(1) Mittente (Clean)", value=st.session_state["box-01-clean"], height=150, key="box1_2")
			
			colbox2_1, colbox2_2 = st.columns([1,1])
			with colbox2_1:
				st.text_area("(2) Mittente Codice 1", value=st.session_state["box-02"], disabled=True, height=100, key="box2_1")
			with colbox2_2:
				st.text_area("(2) Mittente Codice 1 (Clean)", value=st.session_state["box-02-clean"], height=100, key="box2_2")

			colbox2_1, colbox2_2 = st.columns([1,1])
			with colbox2_1:
				st.text_area("(3) Mittente Codice 2", value=st.session_state["box-03"], disabled=True, height=100, key="box3_1")
			with colbox2_2:
				st.text_area("(3) Mittente Codice 2 (Clean)", value=st.session_state["box-03-clean"], height=100, key="box3_2")

			colbox1_1, colbox1_2 = st.columns([1,1])	
			with colbox1_1:
				st.text_area("(4) Destinatario", value=st.session_state["box-04"], disabled=True, height=150, key="box4_1")
			with colbox1_2:
				st.text_area("(4) Destinatario (Clean)", value=st.session_state["box-04-clean"], height=150, key="box4_2")
			
			colbox2_1, colbox2_2 = st.columns([1,1])
			with colbox2_1:
				st.text_area("(5) Destinatario Codice 1", value=st.session_state["box-05"], disabled=True, height=100, key="box5_1")
			with colbox2_2:
				st.text_area("(5) Destinatario Codice 1 (Clean)", value=st.session_state["box-05-clean"], height=100, key="box5_2")

			colbox2_1, colbox2_2 = st.columns([1,1])
			with colbox2_1:
				st.text_area("(6) Destinatario Codice 2", value=st.session_state["box-06"], disabled=True, height=100, key="box6_1")
			with colbox2_2:
				st.text_area("(6) Destinatario Codice 2 (Clean)", value=st.session_state["box-06-clean"], height=100, key="box6_2")

			colbox10_1, colbox10_2= st.columns([1,1])
			with colbox10_1:
				st.text_area("(10) Luogo di Consegna", value=st.session_state["box-10"], disabled=True, height=100, key="box10_1")
			with colbox10_2:
				st.text_area("(10) Luogo di Consegna (Clean)", value=st.session_state["box-10-clean"], height=100, key="box10_2")

			colbox11_1, colbox11_2 = st.columns([1,1])
			with colbox11_1:
				st.text_area("(11) Codice Luogo Consegna 1", value=st.session_state["box-11"], disabled=True, height=100, key="box11_1")
			with colbox11_2:
				st.text_area("(11) Codice Luogo Consegna 1 (Clean)", value=st.session_state["box-11-clean"], height=100, key="box11_2")
	
			colbox12_1, colbox12_2 = st.columns([1,1])
			with colbox11_1:
				st.text_area("(12) Codice Luogo Consegna 2", value=st.session_state["box-12"], disabled=True, height=100, key="box12_1")
			with colbox11_2:
				st.text_area("(12) Codice Luogo Consegna 2 (Clean)", value=st.session_state["box-12-clean"], height=100, key="box12_2")

			colbox13_1, colbox13_2 = st.columns([1,1])
			with colbox13_1:
				st.text_area("(13) Condizioni commerciali", value=st.session_state["box-13"], disabled=True, height=100, key="box13_1")
			with colbox13_2:
				st.text_area("(13) Condizioni commerciali (Clean)", value=st.session_state["box-13-clean"], height=100, key="box13_2", )

			colbox14_1, colbox14_2= st.columns([1,1])
			with colbox14_1:
				st.text_area("(14) Codice Contratto", value=st.session_state["box-14"], disabled=True, height=100, key="box14_1")
			with colbox14_2:
				st.text_area("(14) Codice Contratto (Clean)", value=st.session_state["box-14-clean"], height=100, key="box14_2")

			colbox16_1, colbox16_2= st.columns([1,1])
			with colbox16_1:
				st.text_area("(16) Origine", value=st.session_state["box-16"], disabled=True, height=100, key="box16_1")
			with colbox16_2:
				st.text_area("(16) Origine (Clean)", value=st.session_state["box-16-clean"], height=100, key="box16_2")
	
			colbox16_1_orario, colbox16_2_orario= st.columns([1,1])
			with colbox16_1_orario:
				st.text_area("(16) Origine Data", value=st.session_state["box-14"], disabled=True, height=100, key="box16_orario_1")
			with colbox16_2_orario:
				st.text_area("(16) Origine Data (Clean)", value=st.session_state["box-14-clean"], height=100, key="box16_orario_2")

			colbox17_1, colbox17_2= st.columns([1,1])
			with colbox17_1:
				st.text_area("(17) Origine Codice", value=st.session_state["box-17"], disabled=True, height=100, key="box17_1")
			with colbox17_2:
				st.text_area("(17) Origine Codice (Clean)", value=st.session_state["box-17-clean"], height=100, key="box17_2")

			colbox18_1, colbox18_2 = st.columns([1,1])
			with colbox18_1:
				st.text_area("(18) Matricola carro distinta", value=st.session_state["box-18"], disabled=True, height=100, key="box18_1")
			with colbox18_2:
				st.text_area("(18) Matricola carro distinta (Clean)", value=st.session_state["box-18-clean"], height=100, key="box18_2")

			colbox19_1_1, colbox19_1_2 = st.columns([1,1])
			with colbox19_1_1:
				st.text_area("(19) Matricola carro percorso", value=st.session_state["box-19-1"], disabled=True, height=100, key="box19_1_1")
			with colbox19_1_2:
				st.text_area("(19) Matricola carro percorso (Clean)", value=st.session_state["box-19-1-clean"], height=100, key="box19_1_2")
	
			colbox19_2_1, colbox19_2_2 = st.columns([1,1])
			with colbox19_2_1:
				st.text_area("(19) Matricola carro da", value=st.session_state["box-19-2"], disabled=True, height=100, key="box19_2_1")
			with colbox19_2_2:
				st.text_area("(19) Matricola carro da (Clean)", value=st.session_state["box-19-2-clean"], height=100, key="box19_2_2")

			colbox23_1, colbox23_2 = st.columns([1,1])
			with colbox23_1:
				st.text_area("(23) Casella RID", value=st.session_state["box-23"], disabled=True, height=100, key="box23_1")
			with colbox23_2:
				st.text_area("(23) Casella RID (Clean)", value=st.session_state["box-23-clean"], height=100, key="box23_2")	

			colbox24_1, colbox24_2 = st.columns([1,1])
			with colbox24_1:
				st.text_area("(24) Codice NHM", value=st.session_state["box-24"], disabled=True, height=100, key="box24_1")
			with colbox24_2:
				st.text_area("(24) Codice NHM (Clean)", value=st.session_state["box-24-clean"], height=100, key="box24_2")

			colbox25_1, colbox25_2 = st.columns([1,1])
			with colbox25_1:
				st.text_area("(25) Massa", value=st.session_state["box-25"], disabled=True, height=100, key="box25_1")
			with colbox25_2:
				st.text_area("(25) Massa (Clean)", value=st.session_state["box-25-clean"], height=100, key="box25_2")

			colbox49_1, colbox49_2 = st.columns([1,1])
			with colbox49_1:
				st.text_area("(49) Codice Affrancazione", value=st.session_state["box-49"], disabled=True, height=100, key="box49_1")
			with colbox49_2:
				st.text_area("(49) Codice Affrancazione (Clean)", value=st.session_state["box-49-clean"], height=100, key="box49_2")

			colbox57_1, colbox57_2 = st.columns([1,1])
			with colbox57_1:
				st.text_area("(57) Altro trasporti", value=st.session_state["box-57"], disabled=True, height=100, key="box57_1")
			with colbox57_2:
				st.text_area("(57) Altro trasporti (Clean)", value=st.session_state["box-57-clean"], height=100, key="box57_2")

			st.info("(62) Identificazione Spedizione")

			col_identificazione1, col_identificazione2 = st.columns([1,1])
			with col_identificazione1:
				st.text_input("Codice Paese", key="ident_paese_1", value=st.session_state["box-62-paese"], disabled=True)
				st.text_input("Codice Stazione", key="ident_stazione_1", value=st.session_state["box-62-stazione"], disabled=True)
				st.text_input("Codice Impresa", key="ident_impresa_1", value=st.session_state["box-62-impresa"], disabled=True)
				st.text_input("Codice Spedizione", key="ident_spedizione_1", value=st.session_state["box-62-spedizione"], disabled=True)
				st.text_input("Luogo", key="box-29", value=st.session_state["box-29"], disabled=True)
			
			with col_identificazione2:
				st.text_input("Codice Paese", key="ident_paese_2", value=st.session_state["box-62-paese-clean"], disabled=False)
				st.text_input("Codice Stazione", key="ident_stazione_2", value=st.session_state["box-62-stazione-clean"], disabled=False)
				st.text_input("Codice Impresa", key="ident_impresa_2", value=st.session_state["box-62-impresa-clean"], disabled=False)
				st.text_input("Codice Spedizione", key="ident_spedizione_2", value=st.session_state["box-62-spedizione-clean"], disabled=False)
				st.text_input("Luogo", key="ident_luogo_2", value=st.session_state["box-62-luogo-clean"], disabled=False)
				st.text_input("Data", key="ident_data_2", value=st.session_state["box-62-data-clean"], disabled=False)
			# -------

			submitted = st.form_submit_button("Conferma valori")
  
			if submitted:
				st.session_state["box-01-clean"] = st.session_state.box1_2
				st.session_state["box-02-clean"] = st.session_state.box2_2
				st.session_state["box-03-clean"] = st.session_state.box3_2	
				st.session_state["box-04-clean"] = st.session_state.box4_2
				st.session_state["box-05-clean"] = st.session_state.box5_2
				st.session_state["box-06-clean"] = st.session_state.box6_2
				st.session_state["box-10-clean"] = st.session_state.box10_2
				st.session_state["box-11-clean"] = st.session_state.box11_2
				st.session_state["box-12-clean"] = st.session_state.box12_2
				st.session_state["box-13-clean"] = st.session_state.box13_2
				st.session_state["box-14-clean"] = st.session_state.box14_2
				st.session_state["box-16-clean"] = st.session_state.box16_2
				st.session_state["box-16-orario-clean"] = st.session_state.box16_orario_2
				st.session_state["box-17-clean"] = st.session_state.box17_2
				st.session_state["box-18-clean"] = st.session_state.box18_2
				st.session_state["box-19-1-clean"] = st.session_state.box19_1_2
				st.session_state["box-19-2-clean"] = st.session_state.box19_2_2
				st.session_state["box-24-clean"] = st.session_state.box24_2
				st.session_state["box-25-clean"] = st.session_state.box25_2
				st.session_state["box-49-clean"] = st.session_state.box49_2
				st.session_state["box-57-clean"] = st.session_state.box57_2
				st.session_state["box-62-paese-clean"] = st.session_state.ident_paese_2
				st.session_state["box-62-stazione-clean"] = st.session_state.ident_stazione_2
				st.session_state["box-62-impresa-clean"] = st.session_state.ident_impresa_2
				st.session_state["box-62-spedizione-clean"] = st.session_state.ident_spedizione_2
				st.session_state["box-62-luogo-clean"] = st.session_state.ident_luogo_2
				st.session_state["box-62-data-clean"] = st.session_state.ident_data_2
				# non c'è bisogno del codice 29, è stato scomposto in 62 luodo e 62 data

				st.session_state["box-01-orfeus"] = st.session_state.box1_2
				st.session_state["box-02-orfeus"] = st.session_state.box2_2
				st.session_state["box-03-orfeus"] = st.session_state.box3_2	
				st.session_state["box-04-orfeus"] = st.session_state.box4_2
				st.session_state["box-05-orfeus"] = st.session_state.box5_2
				st.session_state["box-06-orfeus"] = st.session_state.box6_2
				st.session_state["box-10-orfeus"] = st.session_state.box10_2
				st.session_state["box-11-orfeus"] = st.session_state.box11_2
				st.session_state["box-12-orfeus"] = st.session_state.box12_2
				st.session_state["box-13-orfeus"] = st.session_state.box13_2
				st.session_state["box-14-orfeus"] = st.session_state.box14_2
				st.session_state["box-16-orfeus"] = st.session_state.box16_2
				st.session_state["box-16-orario-orfeus"] = st.session_state.box16_orario_2
				st.session_state["box-17-orfeus"] = st.session_state.box17_2
				st.session_state["box-18-orfeus"] = st.session_state.box18_2
				st.session_state["box-19-1-orfeus"] = st.session_state.box19_1_2
				st.session_state["box-19-2-orfeus"] = st.session_state.box19_2_2
				st.session_state["box-24-orfeus"] = st.session_state.box24_2
				st.session_state["box-25-orfeus"] = st.session_state.box25_2
				st.session_state["box-49-orfeus"] = st.session_state.box49_2
				st.session_state["box-57-orfeus"] = st.session_state.box57_2
				# non c'è bisogno di dati di etichetta

				st.toast("Valori confermati. E' possibile procedere con la fase successiva")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())