import io
import os
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fit  # noqa: E402

TZ = timezone(timedelta(hours=2))
T0 = datetime(2026, 11, 19, 7, 0, 0, tzinfo=TZ)


def fmt(t):
    return t.strftime("%Y-%m-%d %H:%M:%S %z")


def plan():
    """(seconds, pace s/km, power W, hr start, hr end) blocks of a 5x4 interval session."""
    blocks = [(720, 420, 180, 120, 145)]
    for _ in range(3):  # strides at the end of the warm-up
        blocks += [(20, 270, 300, 145, 150), (60, 450, 170, 150, 145)]
    for k in range(5):
        blocks.append((240, 320, 260, 150, 175))
        if k < 4:
            blocks.append((180, 450, 170, 175, 145))
    blocks.append((480, 435, 175, 150, 140))
    return blocks


def build_export():
    recs, gpx = [], []
    t, lat = 0, 33.89
    hr_pts, power_pts, dist = [], [], []
    for dur, pace, power, h1, h2 in plan():
        for i in range(dur):
            sec = t + i
            hr_pts.append((sec, h1 + (h2 - h1) * min(1.0, i / max(1, min(dur, 90)))))
            power_pts.append((sec, power))
            dist.append(1.0 / pace)  # km per second
        t += dur
    total = t
    for sec in range(0, total, 5):
        recs.append(("HeartRate", "count/min", sec, sec, round(hr_pts[sec][1]), "Watch"))
        recs.append(("RunningPower", "W", sec, sec, power_pts[sec][1], "Watch"))
    for sec in range(0, total - 10, 10):
        km = sum(dist[sec:sec + 10])
        recs.append(("DistanceWalkingRunning", "km", sec, sec + 10, round(km, 5), "Watch"))
        recs.append(("StepCount", "count", sec, sec + 10, 28, "Watch"))
    for sec in range(0, total - 60, 60):  # the phone also counts distance: must not be added
        recs.append(("DistanceWalkingRunning", "km", sec, sec + 60, round(sum(dist[sec:sec + 60]), 5), "iPhone"))
    cum = 0.0
    for sec in range(0, total, 3):
        cum += sum(dist[sec:sec + 3])
        gpx.append((T0 + timedelta(seconds=sec), lat + cum / 111.0, 35.5, 20 + 10 * (cum % 2)))
    rows = [f'<Record type="HKQuantityTypeIdentifier{tp}" sourceName="{src}" unit="{u}" value="{v}" '
            f'startDate="{fmt(T0 + timedelta(seconds=a))}" endDate="{fmt(T0 + timedelta(seconds=b))}"/>'
            for tp, u, a, b, v, src in recs]
    end = T0 + timedelta(seconds=total)
    km_total = sum(dist[:total - 10])
    xml = f'''<?xml version="1.0"?><HealthData>{"".join(rows)}
<Workout workoutActivityType="HKWorkoutActivityTypeRunning" duration="{total / 60:.2f}" durationUnit="min" sourceName="Watch"
 startDate="{fmt(T0)}" endDate="{fmt(end)}">
 <MetadataEntry key="HKIndoorWorkout" value="0"/><MetadataEntry key="HKElevationAscended" value="4200 cm"/>
 <MetadataEntry key="HKWeatherTemperature" value="68 degF"/>
 <WorkoutStatistics type="HKQuantityTypeIdentifierDistanceWalkingRunning" sum="{km_total:.3f}" unit="km"/>
 <WorkoutStatistics type="HKQuantityTypeIdentifierHeartRate" average="157" maximum="178" unit="count/min"/>
 <WorkoutRoute sourceName="Watch"><FileReference path="/workout-routes/route_2026-11-19_7.00am.gpx"/></WorkoutRoute>
</Workout></HealthData>'''
    pts = "".join(f'<trkpt lat="{la:.6f}" lon="{lo}"><ele>{e:.1f}</ele><time>{tt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</time></trkpt>'
                  for tt, la, lo, e in gpx)
    route = f'<?xml version="1.0"?><gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>{pts}</trkseg></trk></gpx>'
    return xml, route, km_total


class RunDetailTests(unittest.TestCase):
    def test_interval_session_is_broken_down(self):
        xml, route, km_total = build_export()
        with tempfile.TemporaryDirectory() as d:
            zpath = os.path.join(d, "export.zip")
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("apple_health_export/export.xml", xml)
                z.writestr("apple_health_export/workout-routes/route_2026-11-19_7.00am.gpx", route)
            days = fit.health_days_from_export(zpath, "2026-11-19")
        run = days[0]["runs"][0]
        det = run["detail"]
        kinds = [s["kind"] for s in det["segments"]]
        self.assertEqual(kinds.count("rep"), 5, kinds)
        self.assertEqual(kinds.count("recovery"), 4)
        self.assertEqual(kinds[0], "warmup")
        self.assertEqual(kinds[-1], "cooldown")
        reps = [s for s in det["segments"] if s["kind"] == "rep"]
        for r in reps:
            self.assertAlmostEqual(r["dur"], 240, delta=25)
            self.assertAlmostEqual(r["pace"], 320, delta=15)
            self.assertIn("hrDrop60", r)
        self.assertEqual(len(det["strides"]), 3)
        # Distance comes from the watch only (the phone's samples are not added on top).
        self.assertAlmostEqual(det["summary"]["km"], km_total, delta=0.05)
        self.assertEqual(len([s for s in det["splits"] if isinstance(s["km_mark"], int)]), int(km_total))
        self.assertEqual(det["extras"]["elevGain"], 42)
        self.assertAlmostEqual(det["extras"]["tempC"], 20.0, delta=0.1)
        self.assertTrue(det["extras"]["gps"])
        self.assertIn("lat", det["series"])
        self.assertGreater(det["zones"]["vo2"], 5)

    def test_detail_is_saved_next_to_data(self):
        xml, route, _ = build_export()
        with tempfile.TemporaryDirectory() as d:
            zpath = os.path.join(d, "export.zip")
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("apple_health_export/export.xml", xml)
                z.writestr("apple_health_export/workout-routes/route_2026-11-19_7.00am.gpx", route)
            data_path = os.path.join(d, "data.json")
            with open(data_path, "w") as f:
                f.write('{"runLog": [], "rrSessions": [], "weightLog": [], "dailyLog": []}')
            fit.main(["import-health", zpath, "--since", "2026-11-19", "--offline", "--data", data_path])
            import json
            with open(data_path) as f:
                data = json.load(f)
            run = data["runLog"][0]
            self.assertEqual(run["detail"], f"runs/{run['id']}.json")
            self.assertEqual(len([s for s in run["segments"] if s["kind"] == "rep"]), 5)
            self.assertTrue(os.path.exists(os.path.join(d, run["detail"])))


if __name__ == "__main__":
    unittest.main()
