# FIT — Bodyweight Training & Running Tracker

A zero-dependency web app (Recommended Routine + running + weight trend) plus a small CLI (`fit.py`) for generating logs, a calendar, and Apple Health summaries.

**This repo and its GitHub Pages site are public.** Personal data never goes in git: `data.json`, `generated/`, `archive/`, `health_export/` and `Export.zip` are git-ignored, and the deploy step publishes an explicit allow-list of app files only.

## Where things live

| File | What it is | Tracked? |
| :--- | :--- | :--- |
| `data.json` | **Single source of truth** for your logs, weights, runs, schedule, targets (`meta`) | No (personal) |
| `data.example.json` | Same shape with fake values, for reference/tests | Yes |
| `program.js` | Exercise ladders, cues, rep ranges, default schedule (generic) | Yes |
| `lib.js` | Pure logic: progression, weight trend, HR checks, weekly volume | Yes |
| `app.js`, `index.html`, `style.css` | Web app | Yes |
| `fit.py` | CLI: generate logs/calendar, log entries, parse Apple Health | Yes |
| `PROGRAM.md` | Program write-up; its schedule & ladder sections are generated | Yes |
| `generated/` | `WORKOUT_LOG.md`, `rr_log.csv`, `fit_schedule.ics`, health summaries, form guide | No |

## Daily use

**Web app** (phone or desktop): log RR sessions, runs and weigh-ins. Data is stored in that browser's `localStorage`, so use **6:sync → Download fit_state.json** regularly as a backup.

**Getting web data into `data.json`:** download `fit_state.json` from the app and save it over `data.json`. Or use the GitHub sync with a **private** data repo (the app refuses to push to a public one): create e.g. `you/FIT-data` (private), and a fine-grained token limited to that repo with *Contents: read & write* and an expiry date.

**Run the app locally with your data** (first load seeds from `data.json` when the browser has no saved state):

```bash
python3 -m http.server 8000
```

**Regenerate logs, CSV, calendar and the generated parts of `PROGRAM.md`:**

```bash
python3 fit.py generate
```

Options: `--copy-to "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/FIT"` copies the log into Obsidian; `--apple-calendar` replaces upcoming `FIT:` events in macOS Calendar; `--start YYYY-MM-DD --weeks 8` sets the calendar range.

**Log from the terminal:**

```bash
python3 fit.py log-weight 2026-10-21 78.6
```

```bash
python3 fit.py log-run 2026-10-22 "Tempo / Threshold Run" 8.5 58.0 --hr 160
```

```bash
python3 fit.py log-rr pull=5,4,4 squat="5,5,5 (/leg)" dip=6,5,5 hinge=9,9,9 row=8,7,7 push=5,4,4 --notes "felt good"
```

**Apple Health:** export from the Health app, unzip into `health_export/`, then:

```bash
python3 fit.py health health_export/apple_health_export/Export.xml --since 2026-08-25
```

## What the app checks for you

- **Progression:** add a rep to the weakest set each session; at the top of the range on all 3 sets it suggests the next step, and below the bottom of the range it suggests an easier one.
- **Weight:** 7-day average plus a trend-based weekly rate. It flags loss faster than `meta.maxLossPctPerWeek` (default 1% body weight/week).
- **Runs:** flags easy runs over 148 bpm and long runs over 155 bpm, and weeks where distance jumps more than 10%.

## Tests

```bash
node --test tests/*.test.js
```

```bash
python3 -m unittest discover tests
```

CI runs both on every push and pull request; Pages deploys from `main` only after they pass.
