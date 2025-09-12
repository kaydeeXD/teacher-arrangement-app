import os
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    creds_json = os.getenv("GCP_CREDENTIALS")
    if creds_json is None:
        raise ValueError("❌ GCP_CREDENTIALS not found. Did you set the GitHub secret?")
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

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