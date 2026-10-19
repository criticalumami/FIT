#!/usr/bin/env python3
"""
Convert all FIT events in the 'AJA' Google Calendar to All-Day events (8 weeks starting Mon Oct 19, 2026),
and update fit_schedule.ics with all-day VALUE=DATE events and 100% bodyweight-only descriptions.
"""
import subprocess
from datetime import datetime, timedelta, timezone
import uuid

start_monday = datetime(2026, 10, 19)
weeks = 8

RR_DESC = (
    "r/bodyweightfitness Recommended Routine (Full Body — No Bands/Barbells)\n\n"
    "1. Warm-Up (5-8m): Towel/broomstick shoulder dislocates, Squat sky reaches, Wrist prep, Deadbugs (30s), Arch hangs (10), Dip support hold (30-60s)\n"
    "2. Pair A (3x5-8, 90s rest): Pull-Ups (or L-Sit Pull-Ups) + Squat Progression (Bulgarian Split Squats -> Shrimp/Pistol Squats)\n"
    "3. Pair B (3x5-8, 90s rest): Parallel Bar Dips + Bodyweight Hinge (Single-Leg RDL -> Towel Sliding Leg Curls -> Nordic Negatives)\n"
    "4. Pair C (3x5-8, 90s rest): Horizontal Rows (or Wide/Elevated Rows) + Push-Up Progression (Full -> Diamond -> Pseudo Planche Push-Ups)\n"
    "5. Core Triplet (3x8-12, 60s rest): Hanging Knee/Leg Raises + Copenhagen/Side Plank (30s/side) + Reverse Hypers/Arch Body Holds"
)

SCHEDULE_TEMPLATE = [
    (0, "FIT: Full Recommended Routine (RR)", RR_DESC),
    (
        1,
        "FIT: Run 1 — Easy Aerobic (5–6 km)",
        "5–6 km Easy Aerobic Run (~35–40 min)\nTarget HR: < 148 bpm (Zone 2 conversational pace)\nOptional finisher: 4x 20s smooth strides with 40s walk/jog recovery.",
    ),
    (2, "FIT: Full Recommended Routine (RR)", RR_DESC),
    (
        3,
        "FIT: Run 2 — Tempo / Quality (7–8 km)",
        "7–8 km Quality / Tempo Run (~50–60 min)\n- First 2 km: Easy warm-up (< 145 bpm)\n- Middle 3–4 km: Brisk Tempo (155–165 bpm, ~6:45–7:10 /km)\n- Final 2 km: Easy cool-down (< 148 bpm)",
    ),
    (
        4,
        "FIT: Full Recommended Routine (RR)",
        RR_DESC + "\n\nNote: Leave 1–2 reps in reserve on Squats/SL-RDLs today to keep legs fresh for Saturday's 10 km long run.",
    ),
    (
        5,
        "FIT: Run 3 — Long Endurance Run (10 km+)",
        "10 km+ Steady Endurance Run (~75 min)\n- First 2 km: Extra easy warm-up (< 145 bpm)\n- Remainder: Steady aerobic groove (148–155 bpm)",
    ),
    (
        6,
        "FIT: Skill & Mobility Day (Active Recovery)",
        "Sunday Skill & Mobility Routine (~30–35 min, no muscular failure):\n1. GMB Wrist Prep + Towel Shoulder Dislocates (5m)\n2. Handstand Practice: Chest-to-wall holds / heel pulls (10m timer)\n3. Crow / Crane Pose balance holds (5m timer)\n4. L-Sit (3x 15-20s) + Seated Pike Compression Leg Lifts (3x 10s)\n5. Skin the Cat / German Hang on Pull-up Bar (3x 3-5 slow reps)\n6. Runner's Mobility: Couch Stretch + Calf/Achilles Stretch (5m)",
    ),
]

ics_lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//FIT//Health & Weight Loss Tracker//EN",
    "CALSCALE:GREGORIAN",
]

applescript_lines = [
    'tell application "Calendar"',
    '  if not (exists calendar "FIT") then',
    '    make new calendar with properties {name:"FIT", color:{65535, 0, 0}}',
    '  else',
    '    set color of calendar "FIT" to {65535, 0, 0}',
    '  end if',
    '  tell calendar "FIT"',
    '    set baseDate to current date',
    '    set year of baseDate to 2026',
    '    set month of baseDate to October',
    '    set day of baseDate to 19',
    '    set hours of baseDate to 0',
    '    set minutes of baseDate to 0',
    '    set seconds of baseDate to 0',
    '    try',
    '      delete (every event whose summary begins with "FIT:")',
    '    end try',
]

now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

for w in range(weeks):
    for day_offset, title, desc in SCHEDULE_TEMPLATE:
        total_days = w * 7 + day_offset
        ev_date = start_monday + timedelta(days=total_days)
        next_date = ev_date + timedelta(days=1)

        ics_desc = desc.replace("\n", "\\n")
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@fit.local",
            f"DTSTAMP:{now_utc}",
            f"DTSTART;VALUE=DATE:{ev_date.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{next_date.strftime('%Y%m%d')}",
            f"SUMMARY:{title}",
            f"DESCRIPTION:{ics_desc}",
            "END:VEVENT",
        ])

        as_desc = desc.replace('"', '\\"').replace("\n", "\\n")
        applescript_lines.extend([
            f'    set sDate to baseDate + ({total_days} * days)',
            f'    make new event at end with properties {{summary:"{title}", start date:sDate, end date:sDate, allday event:true, description:"{as_desc}"}}',
        ])

ics_lines.append("END:VCALENDAR")
applescript_lines.extend([
    '  end tell',
    'end tell',
])

with open("/Users/mzrxa/.gemini/antigravity/scratch/FIT/fit_schedule.ics", "w") as f:
    f.write("\r\n".join(ics_lines) + "\r\n")

as_script = "\n".join(applescript_lines)
res = subprocess.run(["osascript", "-e", as_script], capture_output=True, text=True)
print("Return code:", res.returncode)
if res.stdout:
    print("Stdout:", res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)
