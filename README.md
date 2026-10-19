# FIT — Health & Weight Loss Tracker

## Current Baseline (Oct 16, 2026)
- **Age / Sex / Height:** 37M, 171–172 cm
- **Current Weight:** `80.0 kg` (down `-8.0 kg` from `88.0 kg` on Sep 3, 2026)
- **Healthy BMI (< 25) Target:** `73.0–74.0 kg`
- **Average Daily Burn (TDEE, Oct 4–15):** `~3,390 kcal/day` (`2,053 kcal` basal + `1,338 kcal` active)
- **Average Daily Steps:** `25,307 steps/day` (~19.9 km/day)
- **Cardio Fitness:** RHR `59 bpm`, Walking HR `76.5 bpm`, VO2 Max `39.0–39.2 mL/(kg·min)`
- **Target Nutrition for Fat Loss (~0.8–1.0 kg/week):** `2,300–2,500 kcal/day`, `150–160g protein/day`

## Directory Contents
- `health_export/` — Extracted Apple Health & Fitness export (`Export.xml`, workout routes, ECGs)
- `parse_health.py` — Full XML parser for point metrics, workouts, and activity summaries
- `daily_breakdown.py` — Daily aggregator for TDEE, steps, distance, heart rate, VO2 max, and sleep
- `health_summary.txt` — Generated summary output
