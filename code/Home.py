import sys
import streamlit as st
import os
import logging
from dotenv import load_dotenv
import streamlit_authenticator as stauth
import xml.etree.ElementTree as ET

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
st.set_page_config(page_title="Automazione Lettere di Vettura <=> RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

st.title("Automazione Processo Acquisizione Lettere di Vettura")
st.subheader("Trasporti internazionali in Import")
st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)

print('--------------------------------')
print(' NEW SESSION ')
print('--------------------------------')
print(os.getenv("AZURE_OPENAI_BASE")) 
print(os.getenv("AZURE_OPENAI_KEY"))

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

name, authentication_status, username = authenticator.login(location='main')

if username == 'smith@mercitalia.com':
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "John Smith"

# # # begin test
# # from azure.core.credentials import AzureKeyCredential
# # from azure.ai.formrecognizer import DocumentAnalysisClient

# # endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
# # key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# # document_analysis_client = DocumentAnalysisClient(
# #     endpoint=endpoint, credential=AzureKeyCredential(key)
# # )

# with open(os.path.join('ldv', '20231107 131436', "distinta-00.pdf"),'rb') as f:
#     poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=f)
# result = poller.result()



#end test


if username == '':
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "John Smith"

if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*, you are an **admin**.')
    
    import lib.common as common
    common.clean_session()
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')