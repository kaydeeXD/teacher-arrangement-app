import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # creds = ServiceAccountCredentials.from_json_keyfile_name("../credentials.json", scope)
    creds = Credentials.from_service_account_info(
        dict(st.secrets["credentials"]),
        scopes=scope
    )
    client = gspread.authorize(creds)
    return client

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

def load_df_from_gsheet(worksheet):
    data = worksheet.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)