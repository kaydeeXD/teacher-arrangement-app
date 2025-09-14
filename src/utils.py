from constants import MISC_KEYWORDS
from datetime import datetime, timedelta

def get_teacher_domain(name):
    """Classify teacher by domain based on name keywords."""
    name_upper = name.upper()
    if any(k in name_upper for k in MISC_KEYWORDS):
        return "Misc"
    elif "PRINCIPAL" in name_upper:
        return "Principal"
    elif "PGT" in name_upper:
        return "PGT"
    elif "TGT" in name_upper:
        return "TGT"
    elif "PRT" in name_upper:
        return "PRT"
    return "Unknown"

def extract_class_level(class_str):
    """Extract numeric level from class name."""
    roman_map = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
        "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
        "XI": 11, "XII": 12
    }
    if not class_str or not isinstance(class_str, str):
        return None
    first_part = class_str.upper().strip().split()[0]
    return roman_map.get(first_part, None)

def is_same_week(date_str):
    """Check if a given date string is in the current week."""
    try:
        log_date = datetime.strptime(date_str, "%A, %d %B %Y").date()
        today = datetime.today().date()
        return log_date.isocalendar()[1] == today.isocalendar()[1] and log_date.year == today.year
    except Exception:
        return False
    
def get_current_week_dates():
    """Return list of dates (Mon-Sat) for current week."""
    today = datetime.today()
    start = today - timedelta(days=today.weekday())  # Monday
    return [(start + timedelta(days=i)).strftime("%A, %d %B %Y") for i in range(6)]  # Mon-Sat

def get_last_week_dates():
    """Return list of dates (Mon-Sat) for last week."""
    today = datetime.today().date()
    start = today - timedelta(days=today.weekday() + 7)
    return [(start + timedelta(days=i)) for i in range(6)]  # Mon-Sat