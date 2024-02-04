import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import StreamlitCallbackHandler
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

try:
	st.set_page_config(page_title="Mercitalia - Automazione LdV / RdS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Export finale dei dati verso sistemi Mercitalia")
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
		st.image(os.path.join('images','Slide7.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase viene utilizzato **GPT4 per produrre il codice applicativo (in modalità agente autonomo)** per convertire i dati della **Distinta carri** nel formato del **file Excel usato dai sistemi attuali**.
A questo scopo **viene utilizzato GPT4 per sviluppare un algoritmo di ricerca**, che imposta le condizioni più adatte e stringenti, necessarie per la ricerca.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa.
- **Azure OpenAI**: Servizio di LLM in modalità GPT4-Turbo per l'automazione del processo di agente autonomo nella creazione del file excel finale
""")

		import xml.etree.ElementTree as ET
		import pandas as pd
		nomefile = os.path.join('orpheus','ECTD.20231106_232258_875.xml')
		# Caricare e analizzare il file XML
		tree = ET.parse(nomefile)
		root = tree.getroot()

		st.code("""
Creare un DataFrame vuoto con le colonne specificate
columns = ['Marcatura Carro', 'Tara', 'Codice NHM UTI', 'Codice UTI', 'Marc. UTI', 
		'Peso netto UTI', 'Peso lordo UTI', 'Tara UTI', 'Lunghezza UTI', 'NHM merce contenuta', 
		'Anno RID', 'Codice ONU', 'Etichetta pericolo 1']
df = pd.DataFrame(columns=columns)

# Iterare attraverso ogni Wagon e raccogliere i dati
for wagon in root.findall('.//Wagon'):
	wagon_number = wagon.get('WagonNumber')
	wagon_mass = wagon.find('.//WagonMass').text if wagon.find('.//WagonMass') is not None else None

	for uti in wagon.findall('.//UTI'):
		nhm_code = uti.find('.//NHMCode').text if uti.find('.//NHMCode') is not None else None
		uti_number = uti.find('.//UTIDetails/Number').text if uti.find('.//UTIDetails/Number') is not None else None
		uti_prefix = uti.find('.//UTIDetails/Prefix').text.strip() if uti.find('.//UTIDetails/Prefix') is not None else None
		gross_mass = uti.find('.//GrossMass').text if uti.find('.//GrossMass') is not None else None
		tare_weight = uti.find('.//UTIDetails/TareWeight').text if uti.find('.//UTIDetails/TareWeight') is not None else None
		length = uti.find('.//UTIDetails/Dimensions/Length').get('value') if uti.find('.//UTIDetails/Dimensions/Length') is not None else None
		
		# RID-specific data
		rid_year = uti.find('.//RID/Law').text if uti.find('.//RID/Law') is not None else None
		un_number = uti.find('.//RID/UNNumber').text if uti.find('.//RID/UNNumber') is not None else None
		danger_label = uti.find('.//RID/DangerLabel').text if uti.find('.//RID/DangerLabel') is not None else None

		# Aggiungere i dati al DataFrame
		df = df.append({
			'Marcatura Carro': wagon_number, 
			'Tara': wagon_mass, 
			'Codice NHM UTI': nhm_code, 
			'Codice UTI': uti_number, 
			'Marc. UTI': uti_prefix, 
			'Peso netto UTI': None,  # Non presente nell'XML fornito
			'Peso lordo UTI': gross_mass, 
			'Tara UTI': tare_weight, 
			'Lunghezza UTI': length, 
			'NHM merce contenuta': None,  # Non presente nell'XML fornito
			'Anno RID': rid_year, 
			'Codice ONU': un_number, 
			'Etichetta pericolo 1': danger_label
		}, ignore_index=True)
""", line_numbers=True, language='python')

		# Creare un DataFrame vuoto con le colonne specificate
		columns = ['Marcatura Carro', 'Tara', 'Codice NHM UTI', 'Codice UTI', 'Marc. UTI', 
				'Peso netto UTI', 'Peso lordo UTI', 'Tara UTI', 'Lunghezza UTI', 'NHM merce contenuta', 
				'Anno RID', 'Codice ONU', 'Etichetta pericolo 1']
		df = pd.DataFrame(columns=columns)

		# Iterare attraverso ogni Wagon e raccogliere i dati
		for wagon in root.findall('.//Wagon'):
			wagon_number = wagon.get('WagonNumber')
			wagon_mass = wagon.find('.//WagonMass').text if wagon.find('.//WagonMass') is not None else None

			for uti in wagon.findall('.//UTI'):
				nhm_code = uti.find('.//NHMCode').text if uti.find('.//NHMCode') is not None else None
				uti_number = uti.find('.//UTIDetails/Number').text if uti.find('.//UTIDetails/Number') is not None else None
				uti_prefix = uti.find('.//UTIDetails/Prefix').text.strip() if uti.find('.//UTIDetails/Prefix') is not None else None
				gross_mass = uti.find('.//GrossMass').text if uti.find('.//GrossMass') is not None else None
				tare_weight = uti.find('.//UTIDetails/TareWeight').text if uti.find('.//UTIDetails/TareWeight') is not None else None
				length = uti.find('.//UTIDetails/Dimensions/Length').get('value') if uti.find('.//UTIDetails/Dimensions/Length') is not None else None
				
				# RID-specific data
				rid_year = uti.find('.//RID/Law').text if uti.find('.//RID/Law') is not None else None
				un_number = uti.find('.//RID/UNNumber').text if uti.find('.//RID/UNNumber') is not None else None
				danger_label = uti.find('.//RID/DangerLabel').text if uti.find('.//RID/DangerLabel') is not None else None

				# Aggiungere i dati al DataFrame
				df = df.append({
					'Marcatura Carro': wagon_number, 
					'Tara': wagon_mass, 
					'Codice NHM UTI': nhm_code, 
					'Codice UTI': uti_number, 
					'Marc. UTI': uti_prefix, 
					'Peso netto UTI': None,  # Non presente nell'XML fornito
					'Peso lordo UTI': gross_mass, 
					'Tara UTI': tare_weight, 
					'Lunghezza UTI': length, 
					'NHM merce contenuta': None,  # Non presente nell'XML fornito
					'Anno RID': rid_year, 
					'Codice ONU': un_number, 
					'Etichetta pericolo 1': danger_label
				}, ignore_index=True)

		# Salvare il DataFrame in un file Excel
		df.to_excel('wagon_data.xlsx', index=False)

		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode		
		gb = GridOptionsBuilder.from_dataframe(df)
		gb.configure_side_bar()
		gridOptions = gb.build()

		data = AgGrid(df,
					gridOptions=gridOptions,
					enable_enterprise_modules=True,
					allow_unsafe_jscode=True,
					update_mode=GridUpdateMode.SELECTION_CHANGED,
					columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

		with open('wagon_data.xlsx', "rb") as template_file:
			template_byte = template_file.read()

		st.download_button(label="Scarica il file Excel con la distinta carri",
						data=template_byte,
						file_name="template.xlsx",
						mime='application/octet-stream')

		st.download_button(label="Scarica il file XML (CIM + distinta carri)",
						data=template_byte,
						file_name="template.xlsx",
						mime='application/octet-stream')

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())






