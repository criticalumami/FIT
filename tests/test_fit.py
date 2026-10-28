"""Run: python3 -m unittest discover tests"""
import json
import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fit  # noqa: E402

EXAMPLE = os.path.join(os.path.dirname(fit.__file__), "data.example.json")


class FitTests(unittest.TestCase):
    def setUp(self):
        self.program = fit.load_program()
        with open(EXAMPLE) as f:
            self.data = json.load(f)

    def test_program_js_is_strict_json_with_rep_ranges(self):
        ids = [e["id"] for e in self.program["exercises"]]
        self.assertIn("pull", ids)
        for e in self.program["exercises"]:
            if e["category"].startswith("pair"):
                self.assertLess(e["minRep"], e["maxRep"])
        self.assertEqual(len(self.program["defaultSchedule"]), 7)

    def test_pace_matches_lib_js(self):
        self.assertEqual(fit.pace(8.02, 66.1), "8:15")
        self.assertEqual(fit.pace(1, 6.999), "7:00")
        self.assertEqual(fit.pace(0, 5), "-")

    def test_workout_log_contains_sessions_runs_and_weights(self):
        md = fit.workout_log_md(self.data)
        self.assertIn("| 2026-01-05 | 90.0 | 5,5,4 |", md)
        self.assertIn("Easy Run (Zone 2 - No Strides)", md)
        self.assertIn("| 2026-01-12 | 89.3 kg |", md)
        self.assertIn("Goal: 80.0 kg", md)

    def test_markdown_cells_escape_pipes(self):
        self.data["rrSessions"][0]["notes"] = "a | b"
        self.assertIn("a \\| b", fit.workout_log_md(self.data))

    def test_csv_round_trips(self):
        import csv, io
        rows = list(csv.DictReader(io.StringIO(fit.rr_csv(self.data))))
        self.assertEqual(rows[0]["pull_sets"], "5,5,4")
        self.assertEqual(rows[0]["bw_kg"], "90.0")

    def test_calendar_uses_schedule_and_stable_uids(self):
        self.data["schedule"] = self.program["defaultSchedule"]
        events = list(fit.calendar_events(self.data, self.program, date(2026, 1, 7), 2))
        self.assertEqual(len(events), 14)
        self.assertEqual(events[0][0], date(2026, 1, 5))  # aligned to Monday
        self.assertIn("Current steps:", events[0][2])      # RR day lists active steps
        ics = fit.build_ics(events)
        self.assertIn("UID:fit-2026-01-05@fit.local", ics)
        self.assertTrue(all(len(l.encode()) <= 75 for l in ics.split("\r\n")))
        unfolded = ics.replace("\r\n ", "")
        self.assertIn("Current steps:\\n- Pair 1A", unfolded)

    def test_ics_escape(self):
        self.assertEqual(fit.ics_escape("a,b;c\nd\\"), "a\\,b\\;c\\nd\\\\")

    def test_replace_block_is_idempotent(self):
        text = "a\n<!-- BEGIN GENERATED:x -->\n<!-- END GENERATED:x -->\nb"
        once = fit.replace_block(text, "x", "BODY")
        self.assertEqual(fit.replace_block(once, "x", "BODY"), once)
        with self.assertRaises(ValueError):
            fit.replace_block("no markers", "x", "BODY")

    def test_log_commands_write_data_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            with open(path, "w") as f:
                json.dump(self.data, f)
            real = os.path.join(os.path.dirname(fit.__file__), "data.json")
            before = os.path.getmtime(real) if os.path.exists(real) else None
            old = fit.DATA_PATH
            fit.DATA_PATH = path
            try:
                fit.main(["log-weight", "2026-01-19", "88.9", "--offline"])
                fit.main(["log-rr", "pull=6,5,4", "squat=5,5,5 (/leg)", "--date", "2026-01-19", "--offline"])
                fit.main(["log-rr", "pull=6,5,5", "--date", "2026-01-19", "--offline"])  # same day replaces
            finally:
                fit.DATA_PATH = old
            if before is not None:
                self.assertEqual(os.path.getmtime(real), before, "test touched the real data.json")
            with open(path) as f:
                saved = json.load(f)
            self.assertEqual(saved["weightLog"][-1]["kg"], 88.9)
            same_day = [s for s in saved["rrSessions"] if s["date"] == "2026-01-19"]
            self.assertEqual(len(same_day), 1)
            self.assertEqual(same_day[0]["pull_sets"], "6,5,5")
            self.assertEqual(same_day[0]["bw"], 88.9)
            self.assertTrue(same_day[0]["pull_prog"].startswith("L3"))
            self.assertTrue(same_day[0]["updatedAt"].endswith("Z"))

    def test_merge_cases_match_lib_js(self):
        cases_path = os.path.join(os.path.dirname(__file__), "merge_cases.json")
        with open(cases_path) as f:
            cases = json.load(f)
        for c in cases:
            with self.subTest(c["name"]):
                out = fit.merge_states(c["local"], c["remote"])
                for key, ids in c["expect"].items():
                    self.assertEqual([e["id"] for e in out[key]], ids)
                for path, val in (c.get("expectValues") or {}).items():
                    parts = path.split(".")
                    got = out[parts[0]][parts[1]] if len(parts) == 2 else \
                        next(e for e in out[parts[0]] if e["id"] == parts[1])[parts[2]]
                    self.assertEqual(got, val)
                if "expectDeleted" in c:
                    self.assertEqual(sorted(out.get("deleted", {})), c["expectDeleted"])

    def test_log_rr_step_changes_and_leg_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            with open(path, "w") as f:
                json.dump(self.data, f)
            old = fit.DATA_PATH
            fit.DATA_PATH = path
            try:
                fit.main(["log-rr", "pull=5,5,4", "squat=5,5,5", "squat_step=L4", "push=8,8,7", "push_step=full standard",
                          "ext=Arch hold 25s", "ext_step=L1", "--date", "2026-01-26", "--offline"])
            finally:
                fit.DATA_PATH = old
            with open(path) as f:
                saved = json.load(f)
            s = next(x for x in saved["rrSessions"] if x["date"] == "2026-01-26")
            self.assertTrue(s["squat_prog"].startswith("L4: Bulgarian"))
            self.assertEqual(s["squat_sets"], "5,5,5 (/leg)")
            self.assertTrue(s["push_prog"].startswith("L2: Full Standard"))
            self.assertTrue(s["pull_prog"].startswith("L3"))  # unchanged step kept
            self.assertEqual(saved["activeProgressions"]["squat"], s["squat_prog"])
            self.assertEqual(saved["activeProgressions"]["push"], s["push_prog"])
            self.assertTrue(saved["activeProgressions"]["core_ext"].startswith("L1: Prone Arch Hold"))
            self.assertGreater(saved["settingsUpdatedAt"], self.data.get("settingsUpdatedAt") or "")

    def test_now_iso_matches_js_format(self):
        import re
        self.assertRegex(fit.now_iso(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")


if __name__ == "__main__":
    unittest.main()
