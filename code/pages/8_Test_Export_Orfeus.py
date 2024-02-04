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
import pandas as pd

def read_field_from_cim():
	
	import time
	folder_path = os.path.join('orpheus')
	file_list = os.listdir(folder_path)
	
	i = 0
	df = pd.DataFrame(columns=['File', 'UICountryCode', 'StationCode', 'SendingCarrier', 'ConsignmentNumber', 'AcceptanceDate'])
 
	for index, file_name in enumerate(file_list):
		# Costruisci il percorso completo del file
		file_path = os.path.join(folder_path, file_name)
		# Verifica che sia un file e non una cartella
		if os.path.isfile(file_path):

			# Chiama la funzione per il file
			tree = ET.parse(file_path)
			root = tree.getroot()
			uic_country_codes = []
			station_codes = []
			carrier_codes = []
			consignment_numbers = []
			acceptance_dates = []
			
			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				uic_country_code_node = ecn.find(".//AcceptancePoint/Point/Country/UICCountryCode")
				if uic_country_code_node is not None:
					uic_country_codes.append(uic_country_code_node.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				station_code = ecn.find(".//AcceptancePoint/Station/Code")
				if station_code is not None:
					station_codes.append(station_code.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECNs"):
				carrier_code = ecn.find(".//ECNHeader/SendingCarrier")
				if carrier_codes is not None:
					carrier_codes.append(carrier_code.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				consignment_number = ecn.find(".//AcceptancePoint/ConsignmentNumber")
				if consignment_numbers is not None:
					consignment_numbers.append(consignment_number.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				acceptance_date = ecn.find(".//AcceptancePoint/AcceptanceDate")
				if acceptance_date is not None:
					acceptance_dates.append(acceptance_date.text)
			
			data_ora_originale = acceptance_dates[0]
			# Analizzare la stringa nel formato originale
			# '%Y-%m-%dT%H:%M:%S%z' è il formato di analisi
			# '%Y' sta per anno, '%m' per mese, '%d' per giorno, '%H' per ore, '%M' per minuti, '%S' per secondi, '%z' per il fuso orario
			try:
				data_ora_obj = datetime.datetime.strptime(data_ora_originale, '%Y-%m-%dT%H:%M:%S%z')
				# Formattare l'oggetto datetime nel nuovo formato
				# '%Y%m%d-%H%M%S' è il formato di output
				data_ora_formattata = data_ora_obj.strftime('%Y%m%d')
			except ValueError as e:
				print(f"Errore nella conversione della data: {e} nel file {file_name}")

			# Example dataframes
			df.loc[i] = [file_name, uic_country_codes[0], station_codes[0], carrier_codes[0], consignment_numbers[0], data_ora_formattata]
			i += 1
	
	st.dataframe(df)
	with pd.ExcelWriter(path='orfeus-xmls.xlsx', engine='xlsxwriter') as writer:
		df.to_excel(writer, sheet_name="orfeus xmls")
		writer.save()
	return df

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
		read_field_from_cim()

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())