import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

@st.cache_resource
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

@st.cache_resource
def get_or_create_worksheet(sheet_id, worksheet_name, rows=1000, cols=20):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id)
    try:
        worksheet = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows=str(rows), cols=str(cols))
    return worksheet

def save_df_to_gsheet(df, worksheet):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

@st.cache_data(ttl=60)
def load_df_from_gsheet(_worksheet):
    data = _worksheet.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)