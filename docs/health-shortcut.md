# Apple Health → FIT

## Easiest: the ready-made "FIT Upload" shortcut (recommended)

**Install once (1 minute):**

1. On your iPhone, open [FIT Upload.shortcut](https://github.com/criticalumami/FIT/raw/main/shortcuts/FIT%20Upload.shortcut), or open the same file on your Mac (it syncs to the iPhone through iCloud).
2. Tap **Kurzbefehl hinzufügen** (Add Shortcut). When asked, paste your **FIT-data token** (`github_pat_…`, the same one the web app uses). Adding can take a few seconds.

**Each time you want to update (4 taps, e.g. after your Saturday long run):**

1. **Health** app → your profile picture (top right) → **Alle Health-Daten exportieren** (Export All Health Data) → **Exportieren**.
2. In the share sheet, pick **FIT Upload**.

That's it. The shortcut uploads the export to the private `FIT-data` repo, and a GitHub Action imports the last 60 days: runs with heart rate and power, weigh-ins, sleep, resting heart rate and steps. The notification shows GitHub's answer: **"Upload: uploaded (… Bytes)"** means it worked; anything else is the error (e.g. "Bad credentials" = token wrong or revoked). If you start the shortcut without a file, it asks you to pick the export. The web app shows the new data after its next sync (open it or switch back to it). Nothing is duplicated, and entries you logged by hand always win.

If **FIT Upload** doesn't appear in the share sheet: scroll the app row to the end → **Mehr** (More) → enable it, or tap **Aktionen bearbeiten** at the bottom of the share sheet and add it to Favorites.

---

## Advanced: build a fully automatic daily shortcut yourself

*Written for an iPhone set to **German**. Each step gives the German label first and the English one in brackets. If a label differs slightly on your iOS version, type a keyword such as "Health", "Datum" or "URL" into the action search.*

Once a day (and after each watch workout, if you like) the Shortcut uploads a small snapshot to `inbox/` in the private `FIT-data` repo. A GitHub Action there merges it into `data.json` within about a minute; the web app and `fit.py` pick it up on their next sync. Your Mac doesn't need to be on.

It reuses the **FIT-data token** you already made for the web app (Contents read & write on `FIT-data` only). German number formats such as `78,9 kg` or `29.376 Schritte` are understood.

## Build the Shortcut

Open **Kurzbefehle** (Shortcuts) → **+**. Name it **FIT Health Sync**.

To rename a result: tap the blue result variable of an action → **Umbenennen** (Rename).

1. **Health-Messwerte suchen** (Find Health Samples)
   - Typ: **Gewicht** (Weight)
   - Filter: **Startdatum** · **ist heute** (Start Date is today)
   - **Sortieren nach**: Startdatum · **Reihenfolge**: Neueste zuerst (Latest First)
   - **Begrenzen** (Limit) on, **1**
   - Rename the result to `Weight`
2. **Health-Messwerte suchen**: Typ **Ruheherzfrequenz** (Resting Heart Rate), Startdatum ist heute, Neueste zuerst, Begrenzen **1** → rename `RHR`
3. **Health-Messwerte suchen**: Typ **Schritte** (Steps), Startdatum ist heute, **Gruppieren nach: Tag** (Group By: Day) → rename `Steps`
4. **Health-Messwerte suchen**: Typ **Aktive Energie** (Active Energy), Startdatum ist heute, Gruppieren nach: Tag → rename `ActiveKcal`
5. **Datum** (Date): **Aktuelles Datum** (Current Date), then **Datum formatieren** (Format Date):
   - Datumsformat: **Eigenes** (Custom), format `yyyy-MM-dd` (type it exactly, including capital MM)
   - Rename the result to `Today`
6. **Wörterbuch** (Dictionary). Add each entry with **Text** as the type:

   | Schlüssel (Key) | Wert (Value) |
   | :-- | :-- |
   | `date` | `Today` |
   | `weightKg` | `Weight` |
   | `restingHr` | `RHR` |
   | `steps` | `Steps` |
   | `activeKcal` | `ActiveKcal` |

   Type the keys exactly as shown (in English). They're the field names FIT reads.
7. **Text aus Eingabe abrufen** (Get Text from Input). Input: Wörterbuch.
8. **Base64-Codierung** (Base64 Encode). Modus **Codieren** (Encode), **Zeilenumbrüche: Keine** (Line Breaks: None).
9. **Datum** → **Aktuelles Datum** → **Datum formatieren**: Eigenes, `yyyy-MM-dd-HHmmss` → rename `Stamp`
10. **Inhalte von URL abrufen** (Get Contents of URL):
    - URL: `https://api.github.com/repos/criticalumami/FIT-data/contents/inbox/Stamp.json`. Replace the word Stamp with the `Stamp` variable: tap at that spot and pick it.
    - Tap **Mehr anzeigen** (Show More):
    - **Methode** (Method): **PUT**
    - **Header** (Headers):
      - `Authorization` → `Bearer ` (with the space) followed by your FIT-data token
      - `Accept` → `application/vnd.github+json`
    - **Hauptteil der Anfrage** (Request Body): **JSON**
      - `message` (Text) → `Health from iPhone`
      - `content` (Text) → the **Base64-codiert** (Base64 Encoded) variable from step 8

Tap ▶ to run it once. Allow the Health access (**Erlauben** / **Alle aktivieren**) and the network request. Within a minute, the web app's dashboard shows an **Apple Health** box (open it, or switch back to it, to sync).

Missing values are fine: if you didn't weigh in, `weightKg` is just empty and is skipped.

## Make it automatic

**Kurzbefehle** → **Automation** → **+** (Neue Automation / New Automation):

- **Tageszeit** (Time of Day) → 21:30 → **Täglich** (Daily) → **Sofort ausführen** (Run Immediately) → choose **FIT Health Sync**.
- Optional: **Apple Watch-Training** (Apple Watch Workout) → **Endet** (Ends) → **Sofort ausführen** → **FIT Health Sync**.

## Runs

Watch runs come in through the full-export import with complete heart-rate and power data. In the Health app: profile picture → **Alle Health-Daten exportieren** (Export All Health Data), send the zip to the Mac, then:

```bash
python3 fit.py import-health ~/Downloads/Export.zip
```

To have the Shortcut send runs too, add a `runs` key (Text) to the Wörterbuch, one run per line as `km|minutes|kcal` (e.g. `8,02|52,5|600`). Runs merge with later exports, without duplicates.

## Payload reference

Values may be numbers or text with units, in German or English formatting ("78,9 kg", "29.376 Schritte", "61 count/min"); the importer extracts the number.

```json
{"date": "2026-10-23", "weightKg": "78,9 kg", "restingHr": "61", "steps": "29.376", "activeKcal": "1.576",
 "sleepH": "7,1", "vo2": "39,8", "runs": "8,02|52,5|600"}
```

Files the Action can't read are moved to `inbox/failed/` in the data repo instead of being lost.
