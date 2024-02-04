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


def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)
    return result


def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (
            word.span.offset + word.span.length
        ) <= (span.offset + span.length):
            return True
    return False

def read_from_wagonlist():
	import pandas as pd
 
	from azure.core.credentials import AzureKeyCredential
	from azure.ai.formrecognizer import DocumentAnalysisClient

	endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
	key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

	document_analysis_client = DocumentAnalysisClient(
		endpoint=endpoint, credential=AzureKeyCredential(key)
	)

	with open(os.path.join('ldv', st.session_state['ldv'], "distinta-00.pdf"), 'rb') as f:
		poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=f)
	result = poller.result()
 
	dataframes = []  # This list will store all DataFrames
 
	for table_idx, table in enumerate(result.tables):  
		print(  
			"Table # {} has {} rows and {} columns".format(  
			table_idx, table.row_count, table.column_count  
			)  
		)  
			
		for cell in table.cells:  
			print(  
				"...Cell[{}][{}] has content '{}' with span {}".format(  
				cell.row_index,
				cell.column_index,  
				cell.content.encode("utf-8"),
				cell.column_span
				)
			)

		df = pd.DataFrame(index=range(table.row_count), columns=range(table.column_count))
		for cell in table.cells:
			row = cell.row_index
			col = cell.column_index
			span = cell.column_span
			content = cell.content

			# Controllare se la cella ha uno span e replicare il contenuto
			for i in range(span):
				df.at[row, col + i] = content
		df.columns = df.columns.map(str)
		dataframes.append(df)
	# for table_idx, table in enumerate(result.tables):

	# 	# # Initialize a list to store each row of the table
	# 	table_content = [[] for _ in range(table.row_count)]

	# 	for cell in table.cells:
	# 		# Append cell content to the correct row in table_content
	# 		table_content[cell.row_index].append(cell.content)

		# Convert table_content to a DataFrame and add to the dataframes list
		# df = pd.DataFrame(table_content)

	for df in dataframes:
		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode		
		gb = GridOptionsBuilder.from_dataframe(df)
		gb.configure_side_bar()
		gridOptions = gb.build()

		AgGrid(df,
			gridOptions=gridOptions,
			enable_enterprise_modules=True,
			allow_unsafe_jscode=True,
			update_mode=GridUpdateMode.NO_UPDATE,
			columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

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
  
		read_from_wagonlist()

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())