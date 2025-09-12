import pandas as pd
import random
import streamlit as st
from datetime import datetime
from utils import extract_class_level
from persistence import persist_weekly_log, load_weekly_log, save_state_to_sheet
from constants import SPREADSHEET_ID

def generate_arrangement(absent_dict, absence_reason_dict, selected_periods, day, day_mode, PersistentStateWorksheet, timetable_df):
    today = datetime.today().strftime("%A, %d %B %Y")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    arrangements = []
    suggested_arrangements = []
    arrangement_count = {}
    arrangement_tracker = {}
    day_df = timetable_df[timetable_df["Day"].str.lower() == day.lower()]

    for absent_teacher, absence_type in absent_dict.items():
        if absence_type == "1st half":
            teacher_schedule = day_df[(day_df["Teacher"] == absent_teacher) & (day_df["Period"].isin(range(5, 9)))]
        elif absence_type == "2nd half":
            teacher_schedule = day_df[(day_df["Teacher"] == absent_teacher) & (day_df["Period"].isin(range(1, 5)))]
        else:
            teacher_schedule = day_df[(day_df["Teacher"] == absent_teacher)]

        teacher_schedule = teacher_schedule[teacher_schedule["Period"].isin(selected_periods)]

        for _, row in teacher_schedule.iterrows():
            target_class = row["Class"]
            if pd.isna(target_class) or str(target_class).strip() in ["", "CCA", "LIB", "LIBRARY", "P.E.", "SPORTS"]:
                continue

            period = row["Period"]
            level = extract_class_level(target_class)
            if level is None:
                continue
            
            target_domain = "Primary" if level <= 5 else "Secondary" if level <= 10 else "Senior Secondary"

            free_teachers = day_df[
                (day_df["Period"] == period) &
                (~day_df["Teacher"].isin(absent_dict.keys())) &
                (day_df["TPOD"] < 7) &
                (day_df["Class"].isna() | day_df["Class"].isin(["", "CCA", "LIB", "LIBRARY", "P.E.", "SPORTS"]))
            ].copy()

            substitute = None
            suggested_teachers = []
            domain_priority = {
                "Senior Secondary": ["PGT", "Principal", "Misc"],
                "Secondary": ["TGT", "Misc", "PGT", "Principal"],
                "Primary": ["PRT", "Misc", "Principal"]
            }
            
            candidates = pd.DataFrame()
            for domain in domain_priority[target_domain]:
                candidates = free_teachers[free_teachers["Domain"] == domain]
                if not candidates.empty:
                    break

            if candidates.empty:
                relaxed_free = day_df[
                    (day_df["Period"] == period) &
                    (~day_df["Teacher"].isin(absent_dict.keys())) &
                    (day_df["Class"].isna() | day_df["Class"].isin(["", "CCA", "LIB", "LIBRARY", "P.E.", "SPORTS"]))
                ]
                for domain in domain_priority[target_domain]:
                    candidates = relaxed_free[relaxed_free["Domain"] == domain]
                    if not candidates.empty:
                        break

            if not candidates.empty:
                teacher_list = list(candidates["Teacher"].unique())
                random.shuffle(teacher_list)
                teacher_list.sort(key=lambda t: arrangement_count.get(t, 0))

                suggested_teachers = teacher_list.copy()

                for t in teacher_list:
                    if arrangement_tracker.get((t, period), False):
                        continue
                    substitute = t
                    arrangement_tracker[(t, period)] = True
                    arrangement_count[substitute] = arrangement_count.get(substitute, 0) + 1
                    break

            arrangements.append({
                "Absent Teacher": absent_teacher,
                "Period": period,
                "Class": target_class,
                "Substitute Teacher": substitute
            })

            suggested_arrangements.append({
                "Absent Teacher": absent_teacher,
                "Period": period,
                "Class": target_class,
                "Suggested Teachers": ", ".join(suggested_teachers[:5]) if suggested_teachers else ""
            })

    df = pd.DataFrame(arrangements)
    df["Sub_with_Class"] = df.apply(
        lambda x: f"{str(x['Substitute Teacher'])} ({str(x['Class'])})"
        if pd.notna(x["Substitute Teacher"]) and str(x["Substitute Teacher"]).strip()
        else "",
        axis=1
    )
    pivot_df = df.pivot(index="Absent Teacher", columns="Period", values="Sub_with_Class").fillna("")
    for p in selected_periods:
        if p not in pivot_df.columns:
            pivot_df[p] = ""
    pivot_df = pivot_df[[p for p in selected_periods]]
    pivot_df.columns = [f"Period {p}" for p in pivot_df.columns]
    output_df_reset = pivot_df.reset_index()
    output_df_reset.insert(1, "Reason", output_df_reset["Absent Teacher"].map(absence_reason_dict))

    suggestions_df = pd.DataFrame(suggested_arrangements)

    weekly_log_df = load_weekly_log(SPREADSHEET_ID)
    if not weekly_log_df.empty:
        all_logs = [{
            "date": row["Date"],
            "day": row["Day"],
            "arrangement": row.drop(["Date", "Day"]).to_frame().T
        } for _, row in weekly_log_df.iterrows()]
    else:
        all_logs = []

    if "final_edited_arrangement" in st.session_state:
        arrangement_df = st.session_state.final_edited_arrangement
        source = "manual"
    else:
        arrangement_df = output_df_reset
        source = "auto"
    
    # === Check if entry exists for today ===
    updated = False
    for i, entry in enumerate(all_logs):
        if entry["date"] == today:
            # Overwrite existing
            all_logs[i] = {
                "date": today,
                "day": day,
                "arrangement": arrangement_df,
                "source": source,
                "timestamp": timestamp
            }
            updated = True
            break

    if not updated:
        all_logs.append({
            "date": today,
            "day": day,
            "arrangement": arrangement_df,
            "source": source,
            "timestamp": timestamp
        })

    # === Deduplicate by (day, date) to avoid stale entries ===
    seen = set()
    dedup_logs = []
    for log in all_logs:
        key = (log["day"], log["date"])
        if key not in seen:
            dedup_logs.append(log)
            seen.add(key)

    st.session_state["generated_arrangement"] = output_df_reset
    st.session_state["suggestions_df"] = suggestions_df
    save_state_to_sheet(
        date_str=today,
        day_mode=day_mode,
        absent_teachers=list(absent_dict.keys()),
        reasons_dict=absence_reason_dict,
        timetable_df=output_df_reset,
        worksheet=PersistentStateWorksheet,
        custom_periods = st.session_state.get("__meta__custom_periods", []),
        suggestions_df=suggestions_df
    )
    return output_df_reset, suggestions_df