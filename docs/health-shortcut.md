# iPhone Shortcut: send Apple Health to FIT automatically

Once a day (and after each watch workout, if you like) the Shortcut uploads a small JSON snapshot to `inbox/` in the private `FIT-data` repo. A GitHub Action there merges it into `data.json` within about a minute; the web app and `fit.py` pick it up on their next sync. Your Mac doesn't need to be on.

It reuses the **FIT-data token** you already made for the web app (Contents read & write on `FIT-data` only).

## Build the Shortcut (Shortcuts app → +)

Name it **FIT Health Sync**. Add these actions in order:

1. **Find Health Samples**: Type **Weight**, Start Date **is today**, Sort by **Start Date**, Order **Latest First**, Limit **1**. Tap the result variable → rename to `Weight`.
2. **Find Health Samples**: Type **Resting Heart Rate**, Start Date **is today**, Latest First, Limit **1** → rename `RHR`.
3. **Find Health Samples**: Type **Steps**, Start Date **is today**, **Group By: Day** → rename `Steps`.
4. **Find Health Samples**: Type **Active Energy**, Start Date **is today**, **Group By: Day** → rename `ActiveKcal`.
5. **Date** (Current Date) → **Format Date**: Custom, `yyyy-MM-dd` → rename `Today`.
6. **Dictionary** with these Text keys:
   | Key | Value |
   | :-- | :-- |
   | `date` | `Today` |
   | `weightKg` | `Weight` |
   | `restingHr` | `RHR` |
   | `steps` | `Steps` |
   | `activeKcal` | `ActiveKcal` |
7. **Get Text from Input** (input: Dictionary).
8. **Base64 Encode** (input: Text), Line Breaks: **None**.
9. **Date** (Current Date) → **Format Date**: Custom, `yyyy-MM-dd-HHmmss` → rename `Stamp`.
10. **Get Contents of URL**:
    - URL: `https://api.github.com/repos/criticalumami/FIT-data/contents/inbox/Stamp.json` (insert the `Stamp` variable where it says Stamp)
    - Method: **PUT**
    - Headers: `Authorization` = `Bearer ` followed by your FIT-data token; `Accept` = `application/vnd.github+json`
    - Request Body: **JSON**, fields `message` (Text) = `Health from iPhone`, `content` (Text) = **Base64 Encoded**

Run it once by hand and allow the Health and network permissions. Within a minute, the web app's dashboard shows an **Apple Health** box (open it or switch back to it to sync).

Missing values are fine: if you didn't weigh in, `weightKg` is just empty and is skipped.

## Make it automatic (Shortcuts → Automation → +)

- **Time of Day** → 21:30, Daily → **Run Immediately** → FIT Health Sync.
- Optional: **Apple Watch Workout** → When workout **ends** → **Run Immediately** → FIT Health Sync.

## Runs

Watch runs come in through the full-export import with complete heart-rate and power data. Run this on the Mac after exporting from the Health app:

```bash
python3 fit.py import-health ~/Downloads/Export.zip
```

To have the Shortcut send runs too, add a `runs` key with Text value, one run per line as `km|minutes|kcal` (e.g. `8.02|52.5|600`). The importer merges them with later exports, without duplicates.

## Payload reference

Values may be numbers or text with units ("78.9 kg", "61 count/min"); the importer extracts the number.

```json
{"date": "2026-10-23", "weightKg": "78.9 kg", "restingHr": 61, "steps": 24000, "activeKcal": 1200,
 "sleepH": 7.1, "vo2": 39.8, "runs": "8.02|52.5|600"}
```

Files the Action can't read are moved to `inbox/failed/` in the data repo instead of being lost.
