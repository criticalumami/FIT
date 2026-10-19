#!/usr/bin/env python3
"""
FIT Quick Logger for Recommended Routine (RR), Runs, and Weight.
Syncs automatically to:
  1. WORKOUT_LOG.md & rr_log.csv in the FIT GitHub repo
  2. FIT/FIT - Workout Log.md in the iCloud Obsidian Vault
"""
import csv
import os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DIR, "rr_log.csv")
MD_PATH = os.path.join(DIR, "WORKOUT_LOG.md")
OBSIDIAN_LOG_PATH = "/Users/mzrxa/Library/Mobile Documents/iCloud~md~obsidian/Documents/FIT/FIT - Workout Log.md"

HEADERS = [
    "date",
    "day",
    "pullup_var",
    "pullup_reps",
    "squat_var",
    "squat_reps",
    "dip_var",
    "dip_reps",
    "hinge_var",
    "hinge_reps",
    "row_var",
    "row_reps",
    "pushup_var",
    "pushup_reps",
    "core1_reps",
    "core2_reps",
    "core3_reps",
    "notes",
]

def ensure_files():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
    if not os.path.exists(MD_PATH):
        with open(MD_PATH, "w") as f:
            f.write("# Recommended Routine (RR) & Training Log\n\n")
            f.write("> **Target Range:** `3 sets x 5–8 reps` per exercise. When you hit **`8,8,8`** with clean form, level up to the next variation at `5,5,5`!\n\n")
            f.write("| Date | Day | Pull-Ups | Squats | Dips | Hinges | Rows | Push-Ups | Core (C1 / C2 / C3) | Notes |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")

def append_entry(entry: dict):
    ensure_files()
    now = datetime.now()
    date_str = entry.get("date", now.strftime("%Y-%m-%d"))
    day_str = entry.get("day", now.strftime("%a"))

    row = [
        date_str,
        day_str,
        entry.get("pullup_var", "Pull-Up"),
        entry.get("pullup_reps", "-"),
        entry.get("squat_var", "Sofa Step-Up (Single-Leg)"),
        entry.get("squat_reps", "-"),
        entry.get("dip_var", "Parallel Dip"),
        entry.get("dip_reps", "-"),
        entry.get("hinge_var", "Floor Slide Curl"),
        entry.get("hinge_reps", "-"),
        entry.get("row_var", "Inverted Row"),
        entry.get("row_reps", "-"),
        entry.get("pushup_var", "Diamond Push-Up"),
        entry.get("pushup_reps", "-"),
        entry.get("core1_reps", "-"),
        entry.get("core2_reps", "-"),
        entry.get("core3_reps", "-"),
        entry.get("notes", ""),
    ]

    with open(CSV_PATH, "a", newline="") as f:
        csv.writer(f).writerow(row)

    c_str = f"{row[14]} / {row[15]} / {row[16]}"
    md_line = (
        f"| **{date_str}** | {day_str} "
        f"| {row[2]}: `{row[3]}` "
        f"| {row[4]}: `{row[5]}` "
        f"| {row[6]}: `{row[7]}` "
        f"| {row[8]}: `{row[9]}` "
        f"| {row[10]}: `{row[11]}` "
        f"| {row[12]}: `{row[13]}` "
        f"| `{c_str}` "
        f"| {row[17]} |\n"
    )
    with open(MD_PATH, "a") as f:
        f.write(md_line)

    # Also update Obsidian log if present
    if os.path.exists(OBSIDIAN_LOG_PATH):
        with open(OBSIDIAN_LOG_PATH, "r") as f:
            obs_content = f.read()
        marker = "\n---\n\n## Detailed Session Logs"
        if marker in obs_content:
            obs_content = obs_content.replace(marker, md_line + marker, 1)
        else:
            obs_content += "\n" + md_line
        short_date = date_str.replace("-", "")[2:]
        detail_block = (
            f"\n### \\_{short_date} (RR — {day_str.upper()})\n"
            f"- **Pair A:** `{row[2]}`: `{row[3]}` | `{row[4]}`: `{row[5]}`\n"
            f"- **Pair B:** `{row[6]}`: `{row[7]}` | `{row[8]}`: `{row[9]}`\n"
            f"- **Pair C:** `{row[10]}`: `{row[11]}` | `{row[12]}`: `{row[13]}`\n"
            f"- **Core Triplet:** `{c_str}`\n"
        )
        if row[17]:
            detail_block += f"- **Notes:** {row[17]}\n"
        obs_content += detail_block
        with open(OBSIDIAN_LOG_PATH, "w") as f:
            f.write(obs_content)

    print(f"Logged RR workout for {date_str} ({day_str}) -> WORKOUT_LOG.md, rr_log.csv & Obsidian FIT vault")

if __name__ == "__main__":
    ensure_files()
    with open(MD_PATH) as f:
        print(f.read())
