import pandas as pd
from utils import get_teacher_domain

def parse_timetable(file):
    """Read and parse timetable Excel file into a structured DataFrame."""
    df = pd.read_excel(file, sheet_name="TEACHER  WISE", header=None)
    parsed_rows = []
    current_teacher = None

    for _, row in df.iterrows():
        first_cell = str(row[0]).strip() if pd.notna(row[0]) else ""
        # Detect teacher name rows
        if (
            first_cell
            and first_cell.upper() not in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
            and not first_cell.isdigit()
            and "TOTAL" not in first_cell.upper()
            and "TPOD" not in first_cell.upper()
        ):
            current_teacher = first_cell
            continue

        # Detect timetable rows for days
        if first_cell.upper() in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"] and current_teacher:
            day = first_cell.capitalize()
            tpod_val = row[9] if pd.notna(row[9]) else None
            for period_num in range(1, 9):
                class_val = row[period_num] if pd.notna(row[period_num]) else None
                parsed_rows.append({
                    "Teacher": current_teacher,
                    "Day": day,
                    "Period": period_num,
                    "Class": str(class_val).strip() if class_val else None,
                    "TPOD": int(tpod_val) if pd.notna(tpod_val) else None
                })

    df = pd.DataFrame(parsed_rows)
    df["Domain"] = df["Teacher"].apply(get_teacher_domain)
    return df