import pandas as pd
from datetime import datetime
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from gsheet import save_df_to_gsheet, load_df_from_gsheet, get_or_create_worksheet

# -----------------------------
# Weekly Log Persistence
# -----------------------------
def persist_weekly_log(df, spreadsheet_id):
    """Save weekly arrangement to WeeklyLog and mirror into monthly log."""
    ws = get_or_create_worksheet(sheet_id=spreadsheet_id, worksheet_name="WeeklyLog")
    save_df_to_gsheet(df, ws)
    append_to_monthly_log(df, spreadsheet_id)

def load_weekly_log(spreadsheet_id):
    ws = get_or_create_worksheet(sheet_id=spreadsheet_id, worksheet_name="WeeklyLog")
    return load_df_from_gsheet(ws)

# -----------------------------
# Monthly Log Persistence
# -----------------------------
def append_to_monthly_log(timetable_df, spreadsheet_id):
    """Append or update the current arrangement in {MonthName}Log."""
    today = datetime.today()
    month_name = today.strftime("%B")
    month_sheet_name = f"{month_name}Log"

    ws = get_or_create_worksheet(sheet_id=spreadsheet_id, worksheet_name=month_sheet_name)
    month_df = load_df_from_gsheet(ws)

    # Remove today's entry if exists (overwrite scenario)
    today_str = today.strftime("%A, %d %B %Y")
    if not month_df.empty and 'Date' in month_df.columns:
        month_df = month_df[month_df['Date'] != today_str]

    # Add Date and Day columns
    new_df = timetable_df.copy()
    new_df['Date'] = today_str
    new_df['Day'] = today.strftime("%A")

    # Append and save
    month_df = pd.concat([month_df, new_df], ignore_index=True)
    save_df_to_gsheet(month_df, ws)


# -----------------------------
# Session State Persistence
# -----------------------------
def save_state_to_sheet(date_str, day_mode, absent_teachers, reasons_dict, timetable_df, worksheet, custom_periods=None, suggestions_df=None):
    """Save current session (daily arrangement + suggestions_df) to PersistentState sheet."""
    state_df = timetable_df.copy()
    state_df['__meta__date'] = date_str
    state_df['__meta__day_mode'] = day_mode
    state_df['__meta__absent_teachers'] = ','.join(absent_teachers)
    state_df['__meta__reasons'] = '|'.join([f"{k}:{v}" for k, v in reasons_dict.items()])
    state_df['__meta__custom_periods'] = ','.join(custom_periods) if custom_periods else ""

    # Clear old sheet
    worksheet.clear()
    set_with_dataframe(worksheet, state_df)

    # Save suggestions_df as JSON in S1
    if suggestions_df is not None:
        if suggestions_df.empty:
            # Ensure empty DataFrame has the expected columns
            suggestions_df = pd.DataFrame(columns=["Absent Teacher", "Period", "Class", "Suggested Teachers"])
        worksheet.update("S1", [[suggestions_df.to_json(orient="split")]])

def load_state_from_sheet(worksheet):
    """Load previous session data (including suggestions_df) from PersistentState sheet."""
    df = get_as_dataframe(worksheet).dropna(how="all")
    if df.empty:
        return None, None, [], {}, [], pd.DataFrame(), pd.DataFrame(columns=["Absent Teacher", "Period", "Class", "Suggested Teachers"])

    # Restore metadata
    date_str = df['__meta__date'].iloc[0] if '__meta__date' in df.columns else None
    day_mode = df['__meta__day_mode'].iloc[0] if '__meta__day_mode' in df.columns else None
    absent_teachers = df['__meta__absent_teachers'].iloc[0].split(',') if '__meta__absent_teachers' in df.columns and pd.notna(df['__meta__absent_teachers'].iloc[0]) else []
    
    reasons_dict = {}
    if '__meta__reasons' in df.columns and pd.notna(df['__meta__reasons'].iloc[0]):
        reasons_raw = str(df['__meta__reasons'].iloc[0]).split('|')
        reasons_dict = {r.split(':')[0]: r.split(':')[1] for r in reasons_raw if ':' in r}

    custom_periods = []
    if '__meta__custom_periods' in df.columns and pd.notna(df['__meta__custom_periods'].iloc[0]):
        try:
            custom_periods = [p.strip() for p in df['__meta__custom_periods'].iloc[0].split(',') if p.strip()]
        except Exception:
            custom_periods = []

    # Drop metadata columns
    df = df.drop(columns=['__meta__date', '__meta__day_mode', '__meta__absent_teachers',
                          '__meta__reasons', '__meta__custom_periods'], errors='ignore')

    # Load suggestions_df back from S1
    cell_val = worksheet.acell("S1").value
    if cell_val:
        suggestions_df = pd.read_json(cell_val, orient="split")
    else:
        suggestions_df = pd.DataFrame(columns=["Absent Teacher", "Period", "Class", "Suggested Teachers"])
    
    # Ensure required columns exist
    for col in ["Absent Teacher", "Period", "Class", "Suggested Teachers"]:
        if col not in suggestions_df.columns:
            suggestions_df[col] = pd.NA

    return date_str, day_mode, absent_teachers, reasons_dict, custom_periods, df, suggestions_df