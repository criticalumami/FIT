"""Run: python3 -m unittest discover tests"""
import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fit  # noqa: E402

NOW = "2026-10-23T08:00:00.000Z"


def blank():
    return {"meta": {}, "rrSessions": [], "weightLog": [], "runLog": [], "dailyLog": []}


class NormalizeTests(unittest.TestCase):
    def test_shortcut_text_values_with_units(self):
        day = fit.normalize_health_day({
            "date": "2026-10-23", "weightKg": "78,9 kg", "restingHr": "61 count/min", "steps": "12 345",
            "sleepH": "7.2", "activeKcal": "", "runs": "8.02 km|52.5 min|600\n\n5|31",
        })
        self.assertEqual(day["weightKg"], 78.9)
        self.assertEqual(day["restingHr"], 61)
        self.assertEqual(day["sleepH"], 7.2)
        self.assertNotIn("activeKcal", day)
        self.assertEqual(day["runs"], [{"km": 8.02, "min": 52.5, "kcal": 600}, {"km": 5.0, "min": 31.0}])

    def test_metres_and_seconds_are_converted(self):
        day = fit.normalize_health_day({"date": "2026-10-23", "runs": [{"km": 8020, "sec": 3150}]})
        self.assertEqual(day["runs"], [{"km": 8.02, "min": 52.5}])

    def test_bad_date_rejected(self):
        with self.assertRaises(ValueError):
            fit.normalize_health_day({"date": "today"})


class ApplyTests(unittest.TestCase):
    def test_import_is_idempotent_and_updates_in_place(self):
        data = blank()
        day = fit.normalize_health_day({"date": "2026-10-23", "weightKg": 78.9, "restingHr": 61, "steps": 9000,
                                         "runs": [{"km": 8.02, "min": 52.5, "hr": 144}]})
        self.assertEqual(len(fit.apply_health_day(data, day, NOW)), 3)
        self.assertEqual(fit.apply_health_day(data, day, NOW), [])  # same data again: no change
        later = fit.normalize_health_day({"date": "2026-10-23", "restingHr": 61, "steps": 21000})
        self.assertEqual(fit.apply_health_day(data, later, NOW), ["~ dailyLog 2026-10-23 ['steps']"])
        self.assertEqual(data["dailyLog"][0]["steps"], 21000)
        self.assertEqual(data["runLog"][0]["type"], "Easy Run (Zone 2)")
        self.assertEqual(data["runLog"][0]["updatedAt"], NOW)

    def test_hand_logged_entries_win(self):
        data = blank()
        data["weightLog"].append({"id": "w-1", "date": "2026-10-23", "kg": 79.2})
        data["runLog"].append({"id": "r-1", "date": "2026-10-23", "km": 8.0, "min": 53})
        day = fit.normalize_health_day({"date": "2026-10-23", "weightKg": 78.9, "runs": [{"km": 8.02, "min": 52.5}]})
        self.assertEqual(fit.apply_health_day(data, day, NOW), [])
        self.assertEqual([w["kg"] for w in data["weightLog"]], [79.2])
        self.assertEqual(len(data["runLog"]), 1)

    def test_shortcut_run_then_full_export_fills_in_heart_rate(self):
        data = blank()
        fit.apply_health_day(data, fit.normalize_health_day({"date": "2026-10-25", "runs": "10.1|70"}), NOW)
        full = fit.normalize_health_day({"date": "2026-10-25", "runs": [{"km": 10.04, "min": 70.2, "hr": 147, "maxHr": 160}]})
        fit.apply_health_day(data, full, NOW)
        self.assertEqual(len(data["runLog"]), 1)
        self.assertEqual(data["runLog"][0]["hr"], 147)
        self.assertEqual(data["runLog"][0]["type"], "Long Aerobic Run")

    def test_deleted_entries_are_not_resurrected(self):
        data = blank()
        data["deleted"] = {"w-hk-2026-10-23": "2026-10-23T09:00:00.000Z"}
        fit.apply_health_day(data, fit.normalize_health_day({"date": "2026-10-23", "weightKg": 78.9}), NOW)
        self.assertEqual(data["weightLog"], [])


class InboxAndExportTests(unittest.TestCase):
    def test_ingest_inbox_merges_and_quarantines_bad_files(self):
        with tempfile.TemporaryDirectory() as d:
            data_path, inbox = os.path.join(d, "data.json"), os.path.join(d, "inbox")
            os.makedirs(inbox)
            with open(data_path, "w") as f:
                json.dump(blank(), f)
            with open(os.path.join(inbox, "2026-10-23-0700.json"), "w") as f:
                json.dump({"date": "2026-10-23", "weightKg": "78.9 kg", "restingHr": 60}, f)
            with open(os.path.join(inbox, "broken.json"), "w") as f:
                f.write("{not json")
            old = fit.DATA_PATH
            try:
                fit.main(["ingest-inbox", "--data", data_path, "--inbox", inbox, "--log", os.path.join(d, "LOG.md")])
            finally:
                fit.DATA_PATH = old
            with open(data_path) as f:
                saved = json.load(f)
            self.assertEqual(saved["weightLog"][0]["kg"], 78.9)
            self.assertEqual(saved["dailyLog"][0]["restingHr"], 60)
            self.assertEqual(sorted(os.listdir(inbox)), ["failed"])
            self.assertEqual(os.listdir(os.path.join(inbox, "failed")), ["broken.json"])
            self.assertTrue(os.path.exists(os.path.join(d, "LOG.md")))

    XML = """<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
 <Record type="HKQuantityTypeIdentifierBodyMass" sourceName="Scale" unit="kg" startDate="2026-10-22 07:00:00 +0300" endDate="2026-10-22 07:00:00 +0300" value="78.8"/>
 <Record type="HKQuantityTypeIdentifierRestingHeartRate" sourceName="SSW0" unit="count/min" startDate="2026-10-22 08:00:00 +0300" endDate="2026-10-22 08:00:00 +0300" value="73"/>
 <Record type="HKQuantityTypeIdentifierStepCount" sourceName="SSW0" unit="count" startDate="2026-10-22 09:00:00 +0300" endDate="2026-10-22 10:00:00 +0300" value="29376"/>
 <Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="SSW0" startDate="2026-10-21 23:00:00 +0300" endDate="2026-10-22 06:00:00 +0300" value="HKCategoryValueSleepAnalysisAsleepCore"/>
 <Workout workoutActivityType="HKWorkoutActivityTypeRunning" duration="35.6" durationUnit="min" sourceName="SSW0" startDate="2026-10-22 10:53:00 +0300" endDate="2026-10-22 11:29:00 +0300">
  <WorkoutStatistics type="HKQuantityTypeIdentifierDistanceWalkingRunning" sum="5.00838" unit="km"/>
  <WorkoutStatistics type="HKQuantityTypeIdentifierHeartRate" average="158.7" maximum="185" unit="count/min"/>
  <WorkoutStatistics type="HKQuantityTypeIdentifierRunningPower" average="193.3" unit="W"/>
 </Workout>
</HealthData>
"""

    def test_full_export_from_zip_and_xml(self):
        with tempfile.TemporaryDirectory() as d:
            xml = os.path.join(d, "Export.xml")
            with open(xml, "w") as f:
                f.write(self.XML)
            zpath = os.path.join(d, "Export.zip")
            with zipfile.ZipFile(zpath, "w") as z:
                z.write(xml, "apple_health_export/Export.xml")
            for path in (xml, zpath):
                with self.subTest(path=os.path.basename(path)):
                    days = fit.health_days_from_export(path, "2026-10-20")
                    day = next(x for x in days if x["date"] == "2026-10-22")
                    self.assertEqual(day["weightKg"], 78.8)
                    self.assertEqual(day["restingHr"], 73)
                    self.assertEqual(day["steps"], 29376)
                    self.assertEqual(day["sleepH"], 7.0)
                    self.assertEqual(day["runs"], [{"km": 5.01, "min": 35.6, "hr": 159, "maxHr": 185, "power": 193}])
                    data = blank()
                    fit.apply_health_day(data, day, NOW)
                    self.assertEqual(data["runLog"][0]["type"], "Tempo / Threshold Run")


if __name__ == "__main__":
    unittest.main()
