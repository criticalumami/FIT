import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

xml_path = "/Users/mzrxa/.gemini/antigravity/scratch/FIT/health_export/apple_health_export/Export.xml"

# Let's aggregate daily since 2026-08-25
# Notice that both Watch (SSW0) and Phone (SS02) record steps/distance/basal/active energy.
# Let's separate by sourceName so we don't double count!
daily_by_src = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
activity_by_day = {}
vo2_by_day = {}
rhr_by_day = {}
whr_by_day = {}
weight_by_day = {}
sleep_by_day = defaultdict(float)

for event, elem in ET.iterparse(xml_path, events=("end",)):
    if elem.tag == "Record":
        rtype = elem.attrib.get("type", "")
        sdate = elem.attrib.get("startDate", "")
        edate = elem.attrib.get("endDate", "")
        src = elem.attrib.get("sourceName", "")
        val = elem.attrib.get("value", "")
        if sdate >= "2026-08-25":
            day = sdate[:10]
            if rtype in (
                "HKQuantityTypeIdentifierBasalEnergyBurned",
                "HKQuantityTypeIdentifierActiveEnergyBurned",
                "HKQuantityTypeIdentifierStepCount",
                "HKQuantityTypeIdentifierDistanceWalkingRunning",
                "HKQuantityTypeIdentifierFlightsClimbed",
                "HKQuantityTypeIdentifierAppleExerciseTime",
            ):
                try:
                    daily_by_src[day][rtype][src] += float(val)
                except ValueError:
                    pass
            elif rtype == "HKQuantityTypeIdentifierVO2Max" and src == "SSW0":
                vo2_by_day[day] = float(val)
            elif rtype == "HKQuantityTypeIdentifierRestingHeartRate":
                rhr_by_day[day] = float(val)
            elif rtype == "HKQuantityTypeIdentifierWalkingHeartRateAverage":
                whr_by_day[day] = float(val)
            elif rtype == "HKQuantityTypeIdentifierBodyMass":
                weight_by_day[day] = float(val)
            elif rtype == "HKCategoryTypeIdentifierSleepAnalysis":
                if "Asleep" in val:
                    try:
                        t1 = datetime.strptime(sdate[:19], "%Y-%m-%d %H:%M:%S")
                        t2 = datetime.strptime(edate[:19], "%Y-%m-%d %H:%M:%S")
                        dur_hr = (t2 - t1).total_seconds() / 3600.0
                        # Attribute sleep to the end date day
                        sleep_by_day[edate[:10]] += dur_hr
                    except Exception:
                        pass
        elem.clear()
    elif elem.tag == "ActivitySummary":
        dc = elem.attrib.get("dateComponents", "")
        if dc >= "2026-08-25":
            activity_by_day[dc] = dict(elem.attrib)
        elem.clear()

days = sorted(set(list(daily_by_src.keys()) + list(activity_by_day.keys())))
print(f"{'Date':10} | {'Wt':5} | {'ActKcal':7} | {'Basal(W/P)':14} | {'TDEE':6} | {'ExMin':5} | {'Steps(W/P)':14} | {'DistKm(W/P)':12} | {'RHR':4} | {'WHR':5} | {'VO2':5} | {'SlpHr':5}")
print("-" * 125)
for d in days:
    wt = f"{weight_by_day[d]:.1f}" if d in weight_by_day else ""
    act_sum = activity_by_day.get(d, {})
    act_kcal = float(act_sum.get("activeEnergyBurned", 0)) if act_sum else daily_by_src[d]["HKQuantityTypeIdentifierActiveEnergyBurned"].get("SSW0", 0)
    ex_min = float(act_sum.get("appleExerciseTime", 0)) if act_sum else daily_by_src[d]["HKQuantityTypeIdentifierAppleExerciseTime"].get("SSW0", 0)
    
    basal_w = daily_by_src[d]["HKQuantityTypeIdentifierBasalEnergyBurned"].get("SSW0", 0)
    basal_p = daily_by_src[d]["HKQuantityTypeIdentifierBasalEnergyBurned"].get("SS02", 0)
    basal_best = basal_w if basal_w > 500 else (basal_w + basal_p)
    tdee = act_kcal + basal_best

    steps_w = daily_by_src[d]["HKQuantityTypeIdentifierStepCount"].get("SSW0", 0)
    steps_p = daily_by_src[d]["HKQuantityTypeIdentifierStepCount"].get("SS02", 0)

    dist_w = daily_by_src[d]["HKQuantityTypeIdentifierDistanceWalkingRunning"].get("SSW0", 0)
    dist_p = daily_by_src[d]["HKQuantityTypeIdentifierDistanceWalkingRunning"].get("SS02", 0)

    rhr = f"{rhr_by_day[d]:.0f}" if d in rhr_by_day else ""
    whr = f"{whr_by_day[d]:.0f}" if d in whr_by_day else ""
    vo2 = f"{vo2_by_day[d]:.1f}" if d in vo2_by_day else ""
    slp = f"{sleep_by_day[d]:.1f}" if d in sleep_by_day else ""

    print(f"{d:10} | {wt:5} | {act_kcal:7.0f} | {basal_w:6.0f}/{basal_p:<6.0f} | {tdee:6.0f} | {ex_min:5.0f} | {steps_w:6.0f}/{steps_p:<6.0f} | {dist_w:5.1f}/{dist_p:<5.1f} | {rhr:4} | {whr:5} | {vo2:5} | {slp:5}")
