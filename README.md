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

**Syncing between devices (automatic):** your data lives in the private repo `criticalumami/FIT-data` (sync refuses public repos). Changes from different devices are **merged**, not overwritten, and deletions carry over.

- **Web app, once per device:** tab 6 → paste a fine-grained token (only `FIT-data`, *Contents: read & write*) → tick **Remember on this device**. After that it syncs when the app opens, when you return to it, and a few seconds after every change. The `sync:` indicator in the top bar shows the status; *Forget Token* removes it.
- **Mac:** `log-weight`, `log-run` and `log-rr` sync automatically before and after (add `--offline` to skip). To sync manually (uses your `gh` login):

```bash
python3 fit.py sync
```

`python3 fit.py pull` replaces `data.json` with the repo copy, for recovery only.

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

**Apple Health from the iPhone:** install the ready-made [FIT Upload](shortcuts/FIT%20Upload.shortcut) shortcut, then Health → profile → *Export All Health Data* → share to **FIT Upload**; an Action in the data repo imports it. Guide (also a fully automatic daily option you build yourself): [docs/health-shortcut.md](docs/health-shortcut.md). Rebuild the shortcut with `tools/make_shortcut.py`.

**Apple Health, from a full export** (adds runs with HR/power, weigh-ins and daily metrics; safe to re-run):

```bash
python3 fit.py import-health ~/Downloads/Export.zip
```

For the summary text files, unzip the export into `health_export/`, then:

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
