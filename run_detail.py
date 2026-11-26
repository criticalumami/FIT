"""Second-by-second detail for runs in an Apple Health export.

parse_health() collects every sample that matters during a run (heart rate, distance, speed, power,
cadence, stride length, vertical oscillation, ground contact time) plus each workout's events,
metadata and GPS route. build_run_detail() turns one workout into:

- series:   a 5-second time series (HR, distance, pace, power, cadence, elevation, GPS, form metrics)
- splits:   per-km splits (time, pace, HR, power, cadence, elevation)
- segments: warm-up / reps / recoveries / cool-down (or a steady block), found from the run itself
- zones:    minutes in each HR zone
- extras:   elevation gain, cadence, stride, temperature and the like from the workout metadata

Everything is plain JSON so the private data repo can keep it next to data.json.
"""
import bisect
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HK = "HKQuantityTypeIdentifier"
RUN_SAMPLE_TYPES = {HK + t for t in (
    "HeartRate", "DistanceWalkingRunning", "RunningSpeed", "RunningPower", "RunningStrideLength",
    "RunningVerticalOscillation", "RunningGroundContactTime", "StepCount", "ActiveEnergyBurned")}

# HR zones from the user's threshold (~170): easy, steady, tempo, VO2, max.
ZONES = [("easy", 0, 145), ("steady", 145, 160), ("tempo", 160, 168), ("vo2", 168, 179), ("max", 179, 999)]
STEP = 5  # seconds between points in the stored series


def epoch(s):
    """'2026-11-19 07:12:03 +0200' (Export.xml) or '2026-11-19T05:12:03Z' (GPX) -> epoch seconds."""
    s = s.strip()
    try:
        if "T" in s:
            s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s).timestamp()
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z").timestamp()
    except ValueError:
        return None


def to_si(rtype, value, unit):
    """Normalise sample units: km, m/s, W, m, cm, ms, count, kcal, bpm."""
    u = (unit or "").lower()
    t = rtype.replace(HK, "")
    if t == "DistanceWalkingRunning":
        return value * 1.609344 if u.startswith("mi") else value / 1000 if u == "m" else value
    if t == "RunningSpeed":
        if u in ("km/hr", "km/h"):
            return value / 3.6
        if u in ("mi/hr", "mi/h"):
            return value * 0.44704
        return value  # m/s
    if t == "RunningStrideLength":
        return value * 0.3048 if u == "ft" else value
    if t == "RunningVerticalOscillation":
        return value * 2.54 if u == "in" else value
    if t == "ActiveEnergyBurned":
        return value / 4.184 if u == "kj" else value
    return value


def collect_sample(store, a):
    """Called by parse_health for every Record: keep the ones a run detail needs."""
    rtype = a.get("type", "")
    if rtype not in RUN_SAMPLE_TYPES:
        return
    t1, t2 = epoch(a.get("startDate", "")), epoch(a.get("endDate", ""))
    try:
        v = to_si(rtype, float(a.get("value", "")), a.get("unit"))
    except ValueError:
        return
    if t1 is None:
        return
    store.setdefault(rtype.replace(HK, ""), []).append((t1, t2 if t2 is not None else t1, v, a.get("sourceName", "")))


def workout_extras(el):
    """Events, metadata and route file of one <Workout> element."""
    events, meta, route = [], {}, None
    for c in el.iter():
        if c.tag == "WorkoutEvent":
            events.append({"type": c.attrib.get("type", "").replace("HKWorkoutEventType", ""),
                           "t": epoch(c.attrib.get("date", "")), "dur": c.attrib.get("duration")})
        elif c.tag == "MetadataEntry":
            meta[c.attrib.get("key", "")] = c.attrib.get("value", "")
        elif c.tag == "FileReference" and c.attrib.get("path", "").endswith(".gpx"):
            route = c.attrib["path"]
    return events, meta, route


def parse_gpx(fh):
    """[(epoch, lat, lon, ele)] from a workout-route GPX."""
    pts = []
    for _, el in ET.iterparse(fh, events=("end",)):
        if el.tag.endswith("trkpt"):
            t = ele = None
            for c in el:
                if c.tag.endswith("time"):
                    t = epoch(c.text or "")
                elif c.tag.endswith("ele"):
                    try:
                        ele = float(c.text)
                    except (TypeError, ValueError):
                        pass
            try:
                lat, lon = float(el.attrib["lat"]), float(el.attrib["lon"])
            except (KeyError, ValueError):
                lat = lon = None
            if t is not None and lat is not None:
                pts.append((t, lat, lon, ele))
            el.clear()
    pts.sort()
    return pts


def _haversine(a, b):
    r = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _in_window(samples, t0, t1, source=None):
    out = [s for s in samples if s[1] >= t0 and s[0] <= t1 and (source is None or s[3] == source)]
    out.sort()
    return out


def _main_source(samples, t0, t1, fallback):
    """The source with the most samples inside the run (the watch), so phone + watch never mix."""
    counts = {}
    for s in _in_window(samples, t0, t1):
        counts[s[3]] = counts.get(s[3], 0) + 1
    if not counts:
        return None
    best = max(counts, key=counts.get)
    # Prefer the workout's own source, unless another device (e.g. AirPods or a strap
    # recording HR) has far more samples: then the workout source holds only stragglers.
    if fallback in counts and counts[fallback] * 4 >= counts[best]:
        return fallback
    return best


def _interp(points, n, t0, max_gap=20):
    """Point samples [(t, v)] -> per-second list (None where there is no sample within max_gap)."""
    out = [None] * n
    if not points:
        return out
    ts = [p[0] for p in points]
    for i in range(n):
        t = t0 + i
        j = bisect.bisect_left(ts, t)
        if j < len(ts) and ts[j] == t:
            out[i] = points[j][1]
            continue
        a = points[j - 1] if j > 0 else None
        b = points[j] if j < len(ts) else None
        if a and b and b[0] - a[0] <= max_gap * 2:
            f = (t - a[0]) / (b[0] - a[0])
            out[i] = a[1] + f * (b[1] - a[1])
        elif a and t - a[0] <= max_gap:
            out[i] = a[1]
        elif b and b[0] - t <= max_gap:
            out[i] = b[1]
    return out


def _spread(samples, n, t0):
    """Interval samples [(t1, t2, v)] (distance, steps) -> per-second increments."""
    inc = [0.0] * n
    for s1, s2, v, _ in samples:
        a, b = max(int(math.floor(s1 - t0)), 0), min(int(math.ceil(s2 - t0)), n)
        if b <= a:
            if 0 <= a < n:
                inc[a] += v
            continue
        per = v / (b - a)
        for i in range(a, b):
            inc[i] += per
    return inc


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _smooth(xs, w):
    out, n = [], len(xs)
    pre = [0.0]
    cnt = [0]
    for x in xs:
        pre.append(pre[-1] + (x if x is not None else 0))
        cnt.append(cnt[-1] + (1 if x is not None else 0))
    for i in range(n):
        a, b = max(0, i - w // 2), min(n, i + w // 2 + 1)
        c = cnt[b] - cnt[a]
        out.append((pre[b] - pre[a]) / c if c else None)
    return out


def _pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, max(0, int(q * (len(xs) - 1))))]


def _r(v, nd=0):
    if v is None:
        return None
    return round(v, nd) if nd else int(round(v))


def _pace(sec, km):
    return _r(sec / km) if km and km > 0.01 else None


def _stats(sec, a, b):
    """Metrics for seconds [a, b) of the per-second arrays."""
    km = sec["km"][b - 1] - (sec["km"][a - 1] if a > 0 else 0.0) if b > a else 0
    hr = [x for x in sec["hr"][a:b] if x is not None]
    moving = sum(1 for m in sec["moving"][a:b] if m)
    steps = sum(sec["steps"][a:b])
    out = {"start": a, "dur": b - a, "km": round(km, 3), "pace": _pace(moving or (b - a), km),
           "hr": _r(_mean(hr)), "maxHr": _r(max(hr)) if hr else None,
           "endHr": _r(sec["hr"][b - 1]) if sec["hr"][b - 1] is not None else None,
           "power": _r(_mean(sec["power"][a:b])),
           "cadence": _r(steps / ((b - a) / 60.0)) if steps and b > a else None,
           "stride": _r(_mean(sec["stride"][a:b]), 2), "vo": _r(_mean(sec["vo"][a:b]), 1),
           "gct": _r(_mean(sec["gct"][a:b]))}
    ele = [x for x in sec["ele"][a:b] if x is not None]
    if len(ele) > 1:
        up = down = 0.0
        ref = ele[0]
        for e in ele[1:]:  # 1 m hysteresis so GPS noise doesn't count as climbing
            if e - ref >= 1:
                up += e - ref
                ref = e
            elif ref - e >= 1:
                down += ref - e
                ref = e
        out["up"], out["down"] = _r(up), _r(down)
    return {k: v for k, v in out.items() if v is not None}


def find_segments(sec, n):
    """Warm-up / reps / recoveries / cool-down from the run's own intensity (power, else speed)."""
    sig = sec["power"] if sum(1 for x in sec["power"] if x) > 0.6 * n else sec["speed"]
    sm = _smooth(sig, 21)
    moving_vals = [v for v, m in zip(sm, sec["moving"]) if m and v]
    lo, hi = _pct(moving_vals, 0.25), _pct(moving_vals, 0.9)
    if not lo or not hi or hi < lo * 1.12:  # too even to have hard parts: one steady block
        return [dict(_stats(sec, 0, n), kind="steady")], []
    thr = lo + 0.5 * (hi - lo)
    hard = [bool(v and v > thr) for v in sm]
    blocks, i = [], 0
    while i < n:
        if hard[i]:
            j = i
            while j < n and hard[j]:
                j += 1
            blocks.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for b in blocks:  # join hard blocks split by a short dip (a hill crest, a traffic light)
        if merged and b[0] - merged[-1][1] <= 20:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    strides = [b for b in merged if 8 <= b[1] - b[0] < 45]
    reps = [b for b in merged if b[1] - b[0] >= 60]
    if not reps:
        segs = [dict(_stats(sec, 0, n), kind="steady")]
        return segs, [dict(_stats(sec, a, b), kind="stride") for a, b in strides]
    segs = []
    if reps[0][0] > 30:
        segs.append(dict(_stats(sec, 0, reps[0][0]), kind="warmup"))
    for k, (a, b) in enumerate(reps):
        rep = dict(_stats(sec, a, b), kind="rep" if len(reps) > 1 else "tempo", n=k + 1)
        if b + 60 < n and sec["hr"][b] is not None and sec["hr"][b + 60] is not None:
            rep["hrDrop60"] = _r(sec["hr"][b] - sec["hr"][b + 60])
        segs.append(rep)
        nxt = reps[k + 1][0] if k + 1 < len(reps) else None
        if nxt is not None:
            segs.append(dict(_stats(sec, b, nxt), kind="recovery", n=k + 1))
    if n - reps[-1][1] > 30:
        segs.append(dict(_stats(sec, reps[-1][1], n), kind="cooldown"))
    warm_end = reps[0][0]
    return segs, [dict(_stats(sec, a, b), kind="stride") for a, b in strides if b <= warm_end]


def build_run_detail(workout, samples, gpx=None):
    """workout: dict with startDate/endDate/sourceName/events/metadata. Returns the detail dict."""
    t0, t1 = epoch(workout.get("startDate", "")), epoch(workout.get("endDate", ""))
    if t0 is None or t1 is None or t1 <= t0:
        return None
    n = int(t1 - t0) + 1
    src = workout.get("sourceName")

    def pts(kind):
        s = samples.get(kind, [])
        ms = _main_source(s, t0, t1, src)
        return [(x[0], x[2]) for x in _in_window(s, t0, t1, ms)]

    def ivs(kind):
        s = samples.get(kind, [])
        ms = _main_source(s, t0, t1, src)
        return _in_window(s, t0, t1, ms)

    sec = {"hr": _interp(pts("HeartRate"), n, t0), "power": _interp(pts("RunningPower"), n, t0),
           "speed": _interp(pts("RunningSpeed"), n, t0), "stride": _interp(pts("RunningStrideLength"), n, t0),
           "vo": _interp(pts("RunningVerticalOscillation"), n, t0),
           "gct": _interp(pts("RunningGroundContactTime"), n, t0),
           "steps": _spread(ivs("StepCount"), n, t0)}
    dist = _spread(ivs("DistanceWalkingRunning"), n, t0)
    gpx = [p for p in (gpx or []) if t0 - 5 <= p[0] <= t1 + 5]
    sec["lat"] = _interp([(p[0], p[1]) for p in gpx], n, t0, 15)
    sec["lon"] = _interp([(p[0], p[2]) for p in gpx], n, t0, 15)
    sec["ele"] = _interp([(p[0], p[3]) for p in gpx if p[3] is not None], n, t0, 15)
    if sum(dist) < 0.05 and len(gpx) > 1:  # no distance samples: measure the route instead
        dist = [0.0] * n
        for a, b in zip(gpx, gpx[1:]):
            i = min(max(int(b[0] - t0), 0), n - 1)
            dist[i] += _haversine(a[1:3], b[1:3]) / 1000
    km, c = [], 0.0
    for d in dist:
        c += d
        km.append(c)
    sec["km"] = km
    if not any(sec["speed"]):
        sec["speed"] = [d * 1000 for d in _smooth(dist, 11)]
    # Paused time (Pause/Resume, MotionPaused/MotionResumed events).
    moving = [True] * n
    paused_at = None
    for e in sorted((e for e in workout.get("events", []) if e.get("t")), key=lambda e: e["t"]):
        if e["type"] in ("Pause", "MotionPaused"):
            paused_at = e["t"]
        elif e["type"] in ("Resume", "MotionResumed") and paused_at is not None:
            for i in range(max(0, int(paused_at - t0)), min(n, int(e["t"] - t0))):
                moving[i] = False
            paused_at = None
    sec["moving"] = moving

    # Per-km splits.
    splits, a, mark = [], 0, 1.0
    for i in range(n):
        if km[i] >= mark:
            splits.append(dict(_stats(sec, a, i + 1), km_mark=int(mark)))
            a, mark = i + 1, mark + 1
    if n - a > 20 and km[-1] - (km[a - 1] if a else 0) > 0.05:
        splits.append(dict(_stats(sec, a, n), km_mark=round(km[-1], 2)))

    segments, strides = find_segments(sec, n)
    zones = {name: 0.0 for name, _, _ in ZONES}
    for h in sec["hr"]:
        if h is None:
            continue
        for name, lo, hi in ZONES:
            if lo <= h < hi:
                zones[name] += 1 / 60
                break
    meta = workout.get("metadata", {})

    def meta_num(key):
        v = meta.get(key, "")
        try:
            num = float(v.split()[0])
        except (ValueError, IndexError):
            return None
        unit = v.split()[1] if len(v.split()) > 1 else ""
        return num / 100 if unit == "cm" else (num - 32) * 5 / 9 if unit == "degF" else num / 100 if unit == "%" else num

    summary = _stats(sec, 0, n)
    extras = {"elevGain": _r(meta_num("HKElevationAscended")) if meta.get("HKElevationAscended") else summary.get("up"),
              "tempC": _r(meta_num("HKWeatherTemperature"), 1), "humidity": _r((meta_num("HKWeatherHumidity") or 0) * 100) or None,
              "indoor": meta.get("HKIndoorWorkout") == "1" or None, "avgMETs": _r(meta_num("HKAverageMETs"), 1),
              "cadence": summary.get("cadence"), "stride": summary.get("stride"), "vo": summary.get("vo"),
              "gct": summary.get("gct"), "gps": bool(gpx) or None,
              "pausedMin": _r(sum(1 for m in moving if not m) / 60, 1) or None}
    extras = {k: v for k, v in extras.items() if v is not None}
    series = {k: [] for k in ("t", "hr", "km", "pace", "power", "cad", "ele", "lat", "lon", "stride", "vo", "gct")}
    spd = _smooth(sec["speed"], 31)
    for i in range(0, n, STEP):
        b = min(n, i + STEP)
        series["t"].append(i)
        series["hr"].append(_r(_mean(sec["hr"][i:b])))
        series["km"].append(round(km[i], 3))
        series["pace"].append(_r(1000 / spd[i]) if spd[i] and spd[i] > 0.5 else None)
        series["power"].append(_r(_mean(sec["power"][i:b])))
        series["cad"].append(_r(sum(sec["steps"][i:b]) * 60 / (b - i)) if any(sec["steps"][i:b]) else None)
        series["ele"].append(_r(sec["ele"][i], 1))
        series["lat"].append(_r(sec["lat"][i], 6))
        series["lon"].append(_r(sec["lon"][i], 6))
        series["stride"].append(_r(sec["stride"][i], 2))
        series["vo"].append(_r(sec["vo"][i], 1))
        series["gct"].append(_r(sec["gct"][i]))
    series = {k: v for k, v in series.items() if any(x is not None for x in v)}
    return {"start": workout.get("startDate"), "end": workout.get("endDate"), "source": src,
            "summary": summary, "extras": extras, "zones": {k: round(v, 1) for k, v in zones.items()},
            "splits": splits, "segments": segments, "strides": strides,
            "events": [e for e in workout.get("events", []) if e.get("t")], "metadata": meta, "series": series}


def compact(detail):
    """The small part of a detail that goes on the runLog entry itself."""
    keep = ("kind", "n", "dur", "km", "pace", "hr", "maxHr", "endHr", "power", "cadence", "hrDrop60", "up", "km_mark")
    slim = lambda xs: [{k: s[k] for k in keep if k in s} for s in xs]  # noqa: E731
    return {"splits": slim(detail["splits"]), "segments": slim(detail["segments"]),
            "strides": len(detail["strides"]) or None, "zones": detail["zones"], "extras": detail["extras"]}
