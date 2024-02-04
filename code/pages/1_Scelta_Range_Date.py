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
import lib.common as common

try:
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Scelta Range Date")
	st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)
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
		load_dotenv()
		ldv_folders = []
		for root, dirs, files in os.walk(os.path.join('ldv')):
			for name in dirs:
				ldv_folders.append(os.path.join(name))
		st.image(os.path.join('images','Slide1.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase **il sistema recupera da una serie di e-mail i contenuti più importanti** sulla base del range di date scelto dall’operatore, per restringere il campo di ricerca. 
Le e-mail sono provenienti dall’estero e sono rese disponibili tramite una mailbox Mercitalia.
Contengono gli allegati Lettera di Vettura e Distinta Carri, sotto forma di PDF o Excel.
**Tutti gli allegati sono convertiti in immagini**. L'utente selezionerà la mail con cui viene inizializzato il processo di estrazione cognitiva dei dati.

### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa
- **Azure Blob Storage**: Servizio di storage per file/blob ad alta scalabilità 
""")	
		col_1, col_2 = st.columns([1,1])
		with col_1:
			data_inizio = st.date_input('Seleziona la data di inizio del range', datetime.date(2023, 11, 1))
		with col_2:
			data_fine = st.date_input('Seleziona la data di fine del range', datetime.date(2023, 11, 30))

		import pandas as pd
		import streamlit as st
		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
		
		ldv_folders = []
		colonne = ['Data email', 'Oggetto', 'Da']
		df = pd.DataFrame(columns=colonne)
		i = 0
		for root, dirs, files in os.walk(os.path.join('ldv')):
			for name in dirs:
				file_msg = os.path.join('ldv', name, 'msg_data.txt')
				with open(file_msg, 'r') as file:
					content = file.read()
					from_pattern = r"from: (.+)"
					from_match = re.search(from_pattern, content)
					from_value = from_match.group(1) if from_match else None
					subject_pattern = r"subject: (.+)"
					subject_match = re.search(subject_pattern, content)
					subject_value = subject_match.group(1) if subject_match else None
					data_convertita = datetime.datetime.strptime(name, '%Y%m%d %H%M%S')
					if data_inizio <= data_convertita.date() <= data_fine:
						df.loc[i] = [name, subject_value, from_value]
				i += 1

		# select the columns you want the users to see
		gb = GridOptionsBuilder.from_dataframe(df)
		# configure selection
		gb.configure_selection(selection_mode="single", use_checkbox=True)
		gb.configure_side_bar()
		gridOptions = gb.build()

		data = AgGrid(df,
					gridOptions=gridOptions,
					enable_enterprise_modules=True,
					allow_unsafe_jscode=True,
					update_mode=GridUpdateMode.SELECTION_CHANGED,
					columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

		selected_rows = data["selected_rows"]

		# if len(selected_rows) != 0:
		# 	st.session_state["selected_email"] = selected_rows[0]['Data email']
		# 	st.write('Email selezionata: '.format(st.session_state["selected_email"]))
		# 	st.write('**Data**: {}'.format(selected_rows[0]['Data email']))
		# 	st.write('**Soggetto**: {}'.format(selected_rows[0]['Oggetto']))
		# 	st.write('**Da**: {}'.format(selected_rows[0]['Da']))

		if st.button("Conferma i valori"):
			common.clean_session()
			st.session_state["ldv"] = selected_rows[0]['Data email']
			print('mail selected ' + st.session_state["ldv"])
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())