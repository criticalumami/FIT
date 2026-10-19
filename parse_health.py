import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from datetime import datetime
import json

xml_path = "/Users/mzrxa/.gemini/antigravity/scratch/FIT/health_export/apple_health_export/Export.xml"

me_info = {}
record_counts = Counter()
record_units = {}
record_latest = {}

# Daily aggregators for recent data (e.g. 2025-2026)
daily_sums = defaultdict(lambda: defaultdict(float))
# Point measurements (weight, body fat, BMI, VO2Max, resting HR, height, waist, etc.)
point_records = defaultdict(list)
workouts = []
activity_summaries = []

SUM_TYPES = {
    "HKQuantityTypeIdentifierStepCount",
    "HKQuantityTypeIdentifierDistanceWalkingRunning",
    "HKQuantityTypeIdentifierActiveEnergyBurned",
    "HKQuantityTypeIdentifierBasalEnergyBurned",
    "HKQuantityTypeIdentifierFlightsClimbed",
    "HKQuantityTypeIdentifierAppleExerciseTime",
    "HKQuantityTypeIdentifierAppleStandTime",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed",
    "HKQuantityTypeIdentifierDietaryProtein",
    "HKQuantityTypeIdentifierDietaryCarbohydrates",
    "HKQuantityTypeIdentifierDietaryFatTotal",
    "HKQuantityTypeIdentifierDietaryWater",
}

POINT_TYPES = {
    "HKQuantityTypeIdentifierBodyMass",
    "HKQuantityTypeIdentifierBodyMassIndex",
    "HKQuantityTypeIdentifierBodyFatPercentage",
    "HKQuantityTypeIdentifierLeanBodyMass",
    "HKQuantityTypeIdentifierHeight",
    "HKQuantityTypeIdentifierWaistCircumference",
    "HKQuantityTypeIdentifierRestingHeartRate",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage",
    "HKQuantityTypeIdentifierVO2Max",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
}

for event, elem in ET.iterparse(xml_path, events=("end",)):
    tag = elem.tag
    if tag == "Me":
        me_info = dict(elem.attrib)
    elif tag == "Record":
        rtype = elem.attrib.get("type", "")
        record_counts[rtype] += 1
        unit = elem.attrib.get("unit", "")
        if unit:
            record_units[rtype] = unit
        start_date = elem.attrib.get("startDate", "")
        val_str = elem.attrib.get("value", "")
        source = elem.attrib.get("sourceName", "")

        if start_date > record_latest.get(rtype, ("", ""))[0]:
            record_latest[rtype] = (start_date, val_str, unit, source)

        if rtype in SUM_TYPES and start_date >= "2026-01-01":
            day = start_date[:10]
            try:
                daily_sums[day][(rtype, source)] += float(val_str)
            except ValueError:
                pass
        elif rtype in POINT_TYPES:
            try:
                point_records[rtype].append((start_date, float(val_str), unit, source))
            except ValueError:
                pass
        elem.clear()
    elif tag == "Workout":
        w = dict(elem.attrib)
        # Check WorkoutStatistics children if any
        stats = {}
        for child in elem:
            if child.tag == "WorkoutStatistics":
                st_type = child.attrib.get("type", "")
                stats[st_type] = {
                    "sum": child.attrib.get("sum"),
                    "average": child.attrib.get("average"),
                    "maximum": child.attrib.get("maximum"),
                    "unit": child.attrib.get("unit"),
                }
        w["stats"] = stats
        workouts.append(w)
        elem.clear()
    elif tag == "ActivitySummary":
        activity_summaries.append(dict(elem.attrib))
        elem.clear()

print("=== ME INFO ===")
print(json.dumps(me_info, indent=2))

print("\n=== RECORD COUNTS & LATEST ===")
for rtype, count in record_counts.most_common():
    latest = record_latest.get(rtype, ("", "", "", ""))
    print(f"{rtype}: {count} records | latest: {latest[0]} = {latest[1]} {latest[2]} ({latest[3]})")

print("\n=== POINT RECORDS SUMMARY ===")
for rtype, recs in point_records.items():
    recs.sort(key=lambda x: x[0])
    print(f"\n--- {rtype} (total {len(recs)}) ---")
    for r in recs[-15:]:
        print(f"  {r[0]}: {r[1]} {r[2]} [{r[3]}]")

print(f"\n=== WORKOUTS (total {len(workouts)}) ===")
workouts.sort(key=lambda x: x.get("startDate", ""))
for w in workouts[-20:]:
    print(f"  {w.get('startDate')} | {w.get('workoutActivityType')} | dur={w.get('duration')} {w.get('durationUnit')} | stats={w.get('stats')} | src={w.get('sourceName')}")

print(f"\n=== ACTIVITY SUMMARIES (total {len(activity_summaries)}) ===")
activity_summaries.sort(key=lambda x: x.get("dateComponents", ""))
for a in activity_summaries[-15:]:
    print(f"  {a.get('dateComponents')}: active={a.get('activeEnergyBurned')}/{a.get('activeEnergyBurnedGoal')} kcal, exercise={a.get('appleExerciseTime')}/{a.get('appleExerciseTimeGoal')} min, stand={a.get('appleStandHours')}/{a.get('appleStandHoursGoal')} hr")
