/*
 * FIT // pure logic (no DOM). Loaded by index.html as window.FITLib and by
 * Node tests via require('./lib.js').
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.FITLib = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const DAY_MS = 86400000;

  function escapeHtml(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function isoToDay(iso) {
    return Math.floor(Date.parse(iso + 'T00:00:00Z') / DAY_MS);
  }

  function dayToIso(day) {
    return new Date(day * DAY_MS).toISOString().slice(0, 10);
  }

  // "4,4,4" or "8,8,8 (/leg)" -> { reps: [4,4,4], suffix: ' (/leg)' }
  function parseSets(setStr) {
    const m = String(setStr || '').match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(.*)/);
    if (!m) return null;
    return { reps: [+m[1], +m[2], +m[3]], suffix: m[4] || '' };
  }

  /*
   * Double progression: add one rep to the weakest set until every set hits
   * maxRep, then level up. Any set below minRep means the step is too hard.
   * Returns { sets, action } with action in 'start' | 'progress' | 'level_up' | 'regress' | 'unknown'.
   */
  function computeNextSets(setStr, minRep = 5, maxRep = 8) {
    if (!setStr) return { sets: `${minRep},${minRep},${minRep}`, action: 'start' };
    const p = parseSets(setStr);
    if (!p) return { sets: setStr, action: 'unknown' };
    const reps = p.reps.slice();

    if (reps.every(r => r >= maxRep)) {
      return { sets: `${minRep},${minRep},${minRep}${p.suffix}`, action: 'level_up' };
    }
    let i = 0;
    if (!(reps[0] <= reps[1] && reps[0] <= reps[2])) i = reps[1] <= reps[2] ? 1 : 2;
    reps[i] += 1;
    const action = p.reps.some(r => r < minRep) ? 'regress' : 'progress';
    return { sets: reps.join(',') + p.suffix, action };
  }

  function sumReps(setStr) {
    const nums = String(setStr || '').match(/\d+/g);
    if (!nums) return 0;
    return nums.slice(0, 3).reduce((a, b) => a + parseInt(b, 10), 0);
  }

  // Shorthand: "pullu 4 4 4 step 8 8 8 floorslide 9 9 9 dips 5 5 5 rows 7 7 7 diamond p 4 4 4 plank 30sx2"
  function parseShorthand(raw) {
    if (!raw || !raw.trim()) return null;
    const s = raw.toLowerCase();
    const triple = re => {
      const m = s.match(re);
      return m ? `${m[1]},${m[2]},${m[3]}` : null;
    };
    const T = String.raw`\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)`;
    const out = {
      pull_sets: triple(new RegExp(String.raw`pull\w*` + T)),
      squat_sets: triple(new RegExp(String.raw`(?:squat\w*|step\w*|bss|shrimp\w*)` + T)),
      hinge_sets: triple(new RegExp(String.raw`(?:floor\w*|slide\w*|hinge\w*|nordic\w*|curl\w*)` + T)),
      dip_sets: triple(new RegExp(String.raw`dip\w*` + T)),
      row_sets: triple(new RegExp(String.raw`(?:inverted\s+rows?|rows?)` + T)),
      push_sets: triple(new RegExp(String.raw`(?:diamond\s*p\w*|push\w*|pppu)` + T)),
      antiext: null,
      antirot: null,
      ext: null
    };
    if (out.squat_sets) out.squat_sets += ' (/leg)';
    // Match side plank first and blank it out so the plain-plank regex can't grab it.
    const sideM = s.match(/side\s*planks?\s+([0-9sx]+)/);
    if (sideM) out.antirot = 'Side Plank ' + sideM[1];
    const plankM = s.replace(/side\s*planks?\s+[0-9sx]+/, '').match(/plank\s+([0-9sx]+)/);
    if (plankM) out.antiext = 'Plank ' + plankM[1];
    const archM = s.match(/(?:arch|reverse\s*hyper|revhyper)[a-z\s]*([0-9sx]+)/);
    if (archM) out.ext = 'Arch/RevHyper ' + archM[1];
    return out;
  }

  /*
   * Weight trend from sparse weigh-ins.
   * avg7: mean of entries in the 7 days up to the latest entry.
   * ratePerWeek: least-squares slope (kg/week) over the last `windowDays`
   *   (falls back to all entries if fewer than 2 in the window).
   * ratePctBw: weekly loss as % of current trend weight (positive = losing).
   */
  function weightTrend(weightLog, windowDays = 28, maxPctPerWeek = 1.0) {
    const pts = (weightLog || [])
      .filter(w => w && w.date && !isNaN(Number(w.kg)))
      .map(w => ({ d: isoToDay(w.date), kg: Number(w.kg) }))
      .sort((a, b) => a.d - b.d);
    if (!pts.length) return null;
    const last = pts[pts.length - 1];
    const recent7 = pts.filter(p => p.d > last.d - 7);
    const avg7 = recent7.reduce((a, p) => a + p.kg, 0) / recent7.length;

    let win = pts.filter(p => p.d > last.d - windowDays);
    if (win.length < 2) win = pts;
    let ratePerWeek = null;
    if (win.length >= 2 && win[win.length - 1].d !== win[0].d) {
      const n = win.length;
      const mx = win.reduce((a, p) => a + p.d, 0) / n;
      const my = win.reduce((a, p) => a + p.kg, 0) / n;
      const num = win.reduce((a, p) => a + (p.d - mx) * (p.kg - my), 0);
      const den = win.reduce((a, p) => a + (p.d - mx) ** 2, 0);
      ratePerWeek = (num / den) * 7;
    }
    const ratePctBw = ratePerWeek == null ? null : (-ratePerWeek / avg7) * 100;
    return {
      latest: last.kg,
      latestDate: dayToIso(last.d),
      avg7,
      entries7: recent7.length,
      ratePerWeek,
      ratePctBw,
      windowStart: dayToIso(win[0].d),
      tooFast: ratePctBw != null && ratePctBw > maxPctPerWeek
    };
  }

  // Heart-rate caps by session type (first match wins).
  const RUN_HR_RULES = [
    { re: /easy|zone\s*2|\bz2\b|recovery|shakeout/i, cap: 148, label: 'easy' },
    { re: /long/i, cap: 155, label: 'long' }
  ];

  // Returns null if OK/unknown, else { label, cap, over }.
  function runHrFlag(run, rules = RUN_HR_RULES) {
    if (!run || !run.hr) return null;
    const rule = rules.find(r => r.re.test(run.type || ''));
    if (!rule || run.hr <= rule.cap) return null;
    return { label: rule.label, cap: rule.cap, over: run.hr - rule.cap };
  }

  // Monday-based weeks. Flags weeks that grow > maxIncrease over the previous week.
  function weeklyKm(runLog, maxIncrease = 0.10) {
    const byWeek = new Map();
    (runLog || []).forEach(r => {
      if (!r || !r.date) return;
      const d = isoToDay(r.date);
      const dow = (new Date(d * DAY_MS).getUTCDay() + 6) % 7; // Mon=0
      const wk = d - dow;
      byWeek.set(wk, (byWeek.get(wk) || 0) + Number(r.km || 0));
    });
    if (!byWeek.size) return [];
    const weeks = [...byWeek.keys()].sort((a, b) => a - b);
    const out = [];
    for (let wk = weeks[0]; wk <= weeks[weeks.length - 1]; wk += 7) {
      const km = byWeek.get(wk) || 0;
      const prev = out.length ? out[out.length - 1].km : null;
      const change = prev ? (km - prev) / prev : null;
      out.push({ weekStart: dayToIso(wk), km, change, jump: change != null && change > maxIncrease });
    }
    return out;
  }

  function latestBy(list, field) {
    const withVal = (list || []).filter(x => x && x[field] != null && x[field] !== '');
    if (!withVal.length) return null;
    return withVal.slice().sort((a, b) => a.date.localeCompare(b.date))[withVal.length - 1];
  }

  function pace(km, min) {
    if (!(km > 0) || !(min > 0)) return '-';
    const dec = min / km;
    let m = Math.floor(dec);
    let s = Math.round((dec - m) * 60);
    if (s === 60) { m += 1; s = 0; }
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  /*
   * Sync merge (mirrored by merge_states() in fit.py; keep them identical).
   * - Log arrays are unioned by id. Same id on both sides: the later updatedAt
   *   wins; ties/missing go to `local`.
   * - `deleted` holds tombstones { id: isoTime } so deletions propagate
   *   instead of being resurrected by the other side.
   * - Everything else (meta, progressions, notes, schedule...) comes from the
   *   side with the later settingsUpdatedAt; ties go to `local`, unless local
   *   has no entries at all and remote does (an empty browser never wins).
   */
  const LOG_KEYS = ['rrSessions', 'weightLog', 'runLog'];

  // JSON with sorted keys, for "did anything actually change?" comparisons.
  function stableStringify(v) {
    if (Array.isArray(v)) return '[' + v.map(stableStringify).join(',') + ']';
    if (v && typeof v === 'object') {
      return '{' + Object.keys(v).sort().filter(k => v[k] !== undefined)
        .map(k => JSON.stringify(k) + ':' + stableStringify(v[k])).join(',') + '}';
    }
    return JSON.stringify(v === undefined ? null : v);
  }

  function mergeStates(local, remote) {
    if (!remote) return JSON.parse(JSON.stringify(local));
    if (!local) return JSON.parse(JSON.stringify(remote));
    const newer = (a, b) => String(b || '') > String(a || '');
    const count = s => LOG_KEYS.reduce((n, k) => n + (s[k] || []).length, 0);
    const lt = String(local.settingsUpdatedAt || ''), rt = String(remote.settingsUpdatedAt || '');
    // Later settings win; on a tie, a side with no log entries (fresh/empty browser) never wins.
    const base = rt > lt || (rt === lt && count(local) === 0 && count(remote) > 0) ? remote : local;
    const out = JSON.parse(JSON.stringify(base));

    const deleted = Object.assign({}, remote.deleted || {}, local.deleted || {});
    Object.keys(remote.deleted || {}).forEach(id => {
      if (newer(deleted[id], remote.deleted[id])) deleted[id] = remote.deleted[id];
    });
    out.deleted = deleted;

    LOG_KEYS.forEach(key => {
      const byId = new Map();
      (local[key] || []).forEach(e => byId.set(e.id, e));
      (remote[key] || []).forEach(e => {
        const cur = byId.get(e.id);
        if (!cur || newer(cur.updatedAt, e.updatedAt)) byId.set(e.id, e);
      });
      out[key] = [...byId.values()]
        .filter(e => !(e.id in deleted) || newer(deleted[e.id], e.updatedAt))
        .map(e => JSON.parse(JSON.stringify(e)))
        .sort((a, b) => String(a.date).localeCompare(String(b.date)) || String(a.id).localeCompare(String(b.id)));
    });
    return out;
  }

  return {
    mergeStates,
    stableStringify,
    LOG_KEYS,
    escapeHtml,
    parseSets,
    computeNextSets,
    sumReps,
    parseShorthand,
    weightTrend,
    runHrFlag,
    RUN_HR_RULES,
    weeklyKm,
    latestBy,
    pace,
    isoToDay,
    dayToIso
  };
});
