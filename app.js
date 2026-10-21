/*
 * FIT // suckless grayscale training & recomposition system
 * Vanilla JS, zero dependencies, localStorage + optional private-repo GitHub sync.
 *
 * No personal data lives in this file: it is published. Your data lives in
 * localStorage and in the local, git-ignored data.json (see README).
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'fit_suckless_state_v3';
  const GH_TOKEN_KEY = 'fit_suckless_gh_token';
  const GH_REPO_KEY = 'fit_suckless_gh_repo';
  // Opt-in "remember on this device" token for automatic sync (fine-grained, one private repo).
  const GH_REMEMBER_KEY = 'fit_sync_token_v2';

  const L = window.FITLib;
  const esc = L.escapeHtml;
  const PROGRAM = window.FIT_PROGRAM;
  const EXERCISE_DB = PROGRAM.exercises;
  const exById = id => EXERCISE_DB.find(e => e.id === id) || {};

  // Generic empty state. Real values come from localStorage or data.json.
  const DEFAULT_STATE = {
    meta: {
      startWeight: null,
      startDate: null,
      targetWeight: null,
      tdee: null,
      targetKcal: null,
      avgSteps: null,
      rhr: null,
      maxLossPctPerWeek: 1.0
    },
    activeProgressions: {},
    customNotes: {},
    rrSessions: [],
    weightLog: [],
    runLog: [],
    schedule: PROGRAM.defaultSchedule,
    programNotes: PROGRAM.defaultProgramNotes,
    deleted: {},
    settingsUpdatedAt: null
  };

  function clone(x) {
    return JSON.parse(JSON.stringify(x));
  }

  function withDefaults(parsed) {
    const base = clone(DEFAULT_STATE);
    const merged = Object.assign(base, parsed);
    merged.meta = Object.assign(clone(DEFAULT_STATE.meta), parsed && parsed.meta);
    return merged;
  }

  let state = loadState();

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return withDefaults(JSON.parse(raw));
    } catch (e) {
      console.error('Failed to read localStorage:', e);
    }
    return clone(DEFAULT_STATE);
  }

  // First run with empty storage: when served locally (python3 -m http.server),
  // seed from the git-ignored data.json. On GitHub Pages this 404s harmlessly.
  async function seedFromLocalDataJson() {
    let hasStored = false;
    try { hasStored = !!localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (hasStored || !/^https?:$/.test(location.protocol)) return;
    try {
      const res = await fetch('data.json', { cache: 'no-store' });
      if (!res.ok) return;
      state = withDefaults(await res.json());
      saveState('LOADED LOCAL data.json', { replaced: true });
    } catch (e) {}
  }

  // Change tracking for sync: stamp edited entries, tombstone deleted ones,
  // and note when settings changed, by diffing against the last saved snapshot.
  const SETTINGS_KEYS = ['meta', 'activeProgressions', 'customNotes', 'schedule', 'programNotes'];

  function entryKey(e) {
    const c = Object.assign({}, e);
    delete c.updatedAt;
    return JSON.stringify(c);
  }

  function takeSnapshot(s) {
    const entries = new Map();
    L.LOG_KEYS.forEach(k => (s[k] || []).forEach(e => entries.set(e.id, entryKey(e))));
    return { settings: JSON.stringify(SETTINGS_KEYS.map(k => s[k])), entries };
  }

  let snapshot = takeSnapshot(state);

  function stampChanges() {
    const now = new Date().toISOString();
    const seen = new Set();
    L.LOG_KEYS.forEach(k => (state[k] || []).forEach(e => {
      seen.add(e.id);
      if (snapshot.entries.get(e.id) !== entryKey(e)) e.updatedAt = now;
    }));
    snapshot.entries.forEach((_, id) => {
      if (!seen.has(id)) {
        state.deleted = state.deleted || {};
        state.deleted[id] = now;
      }
    });
    if (JSON.stringify(SETTINGS_KEYS.map(k => state[k])) !== snapshot.settings) state.settingsUpdatedAt = now;
  }

  // opts.replaced: state was swapped wholesale (import/pull/reset) -> don't treat as user edits.
  // opts.noSync: don't schedule an automatic sync.
  function saveState(msg, opts = {}) {
    try {
      if (!opts.replaced) stampChanges();
      snapshot = takeSnapshot(state);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      if (msg) showToast(msg);
      renderAll();
      if (!opts.noSync) scheduleSync();
    } catch (e) {
      console.error('Failed to save state:', e);
    }
  }

  function showToast(text) {
    const el = document.getElementById('toast-status');
    if (!el) return;
    el.textContent = text;
    el.classList.add('visible');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => el.classList.remove('visible'), 3200);
  }

  const RR_SLOTS = [
    ['1A: Pull', 'pull'],
    ['1B: Squat', 'squat'],
    ['2A: Dip', 'dip'],
    ['2B: Hinge', 'hinge'],
    ['3A: Row', 'row'],
    ['3B: Push', 'push']
  ];

  function nextFor(exId, setStr) {
    const ex = exById(exId);
    return L.computeNextSets(setStr, ex.minRep || 5, ex.maxRep || 8);
  }

  // Ladder step one below / above the given step, or null.
  function adjacentStep(exId, step, dir) {
    const ladders = exById(exId).ladders || [];
    const i = ladders.indexOf(step);
    if (i === -1) return null;
    return ladders[i + dir] || null;
  }

  function nextBadge(exId, step, next) {
    if (next.action === 'level_up') {
      const up = adjacentStep(exId, step, +1);
      return `${esc(next.sets)} <span class="muted">[LEVEL UP -> ${esc(up ? shortProg(up) : 'next step')}]</span>`;
    }
    if (next.action === 'regress') {
      const down = adjacentStep(exId, step, -1);
      return `${esc(next.sets)} <span class="muted">[below ${exById(exId).minRep}: consider ${esc(down ? shortProg(down) : 'an easier step')}]</span>`;
    }
    return esc(next.sets);
  }

  function getLatestWeight() {
    const t = L.weightTrend(state.weightLog);
    return t ? t.latest : null;
  }

  function fmtKg(kg) {
    return kg == null || isNaN(kg) ? '-' : Number(kg).toFixed(1) + ' kg';
  }

  function getLatestRR() {
    if (!state.rrSessions || state.rrSessions.length === 0) return null;
    const sorted = [...state.rrSessions].sort((a, b) => a.date.localeCompare(b.date));
    return sorted[sorted.length - 1];
  }

  function trendLine(t) {
    if (!t || t.ratePerWeek == null) return 'Rate: need 2+ weigh-ins';
    const maxPct = state.meta.maxLossPctPerWeek || 1.0;
    const pct = t.ratePctBw.toFixed(2);
    const warn = t.tooFast ? ` | ! FASTER THAN ${maxPct}%/wk TARGET` : '';
    return `Rate since ${t.windowStart}: ${t.ratePerWeek > 0 ? '+' : ''}${t.ratePerWeek.toFixed(2)} kg/wk (${pct}% BW/wk)${warn}`;
  }

  // ==========================================
  // RENDER VIEW 1: STATUS & DASHBOARD
  // ==========================================
  function renderStatus() {
    const m = state.meta;
    const trend = L.weightTrend(state.weightLog, 28, m.maxLossPctPerWeek || 1.0);
    const curWeight = trend ? trend.latest : null;
    const sortedWeights = [...state.weightLog].sort((a, b) => a.date.localeCompare(b.date));
    const startW = m.startWeight != null ? Number(m.startWeight) : (sortedWeights[0] ? Number(sortedWeights[0].kg) : null);
    const startDate = m.startDate || (sortedWeights[0] ? sortedWeights[0].date : null);
    const targetW = m.targetWeight != null ? Number(m.targetWeight) : null;

    document.getElementById('bar-bw').textContent = curWeight != null ? curWeight.toFixed(1) + 'kg' : '-';
    document.getElementById('bar-target').textContent = targetW != null ? `-> ${targetW.toFixed(1)}kg` : '';
    document.getElementById('trajectory-title').textContent =
      `Recomposition Trajectory (${fmtKg(startW)} -> ${fmtKg(targetW)})`;

    const haveGoal = startW != null && targetW != null && curWeight != null && startW !== targetW;
    const lostSoFar = haveGoal ? startW - curWeight : 0;
    const remaining = haveGoal ? Math.max(0, curWeight - targetW) : 0;
    const pct = haveGoal ? Math.min(100, Math.max(0, (lostSoFar / (startW - targetW)) * 100)) : 0;

    const lastRR = getLatestRR();
    const sortedRuns = [...state.runLog].sort((a, b) => a.date.localeCompare(b.date));
    const lastRun = sortedRuns.length ? sortedRuns[sortedRuns.length - 1] : null;
    const lastVo2Run = L.latestBy(state.runLog, 'vo2');
    const totalRunsKm = state.runLog.reduce((acc, r) => acc + Number(r.km || 0), 0);
    const weeks = L.weeklyKm(state.runLog);
    const thisWeek = weeks.length ? weeks[weeks.length - 1] : null;
    const rhrStr = m.rhr ? ` | RHR ${esc(m.rhr)} bpm` : '';

    const kpiHtml = `
      <div class="stat-box">
        <div class="stat-label">Weight (7-day avg)</div>
        <div class="stat-val">${trend ? trend.avg7.toFixed(1) + ' kg' : '-'}</div>
        <div class="stat-sub">${trend ? `latest ${trend.latest.toFixed(1)} on ${esc(trend.latestDate)} | ${trend.entries7} weigh-in(s) this week` : 'No weigh-ins'}${haveGoal ? `<br>-${lostSoFar.toFixed(1)} kg since ${esc(startDate)} (${remaining.toFixed(1)} kg to goal)` : ''}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Rate of Loss</div>
        <div class="stat-val">${trend && trend.ratePctBw != null ? trend.ratePctBw.toFixed(2) + '%/wk' : '-'}</div>
        <div class="stat-sub">${trend && trend.ratePerWeek != null ? `${trend.ratePerWeek.toFixed(2)} kg/wk | target <= ${m.maxLossPctPerWeek || 1.0}% BW/wk` : 'Need 2+ weigh-ins'}${trend && trend.tooFast ? '<br><strong>! Faster than target: consider eating a little more</strong>' : ''}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Latest Run (${lastRun ? esc(lastRun.date.slice(5)) : '-'})</div>
        <div class="stat-val">${lastRun ? Number(lastRun.km).toFixed(2) + ' km' : '-'}</div>
        <div class="stat-sub">${lastRun ? `${esc(lastRun.hr || '-')} bpm avg (${esc(lastRun.maxHr || '-')} max)${lastVo2Run ? ` | VO2 ${esc(lastVo2Run.vo2)}` : ''}` : 'No runs'}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Running Volume (This Week)</div>
        <div class="stat-val">${thisWeek ? thisWeek.km.toFixed(1) + ' km/wk' : '-'}</div>
        <div class="stat-sub">${totalRunsKm.toFixed(1)} km total over ${state.runLog.length} runs${rhrStr}${thisWeek && thisWeek.jump ? `<br><strong>! +${Math.round(thisWeek.change * 100)}% vs last week (&gt;10%)</strong>` : ''}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">RR Sessions Logged</div>
        <div class="stat-val">${state.rrSessions.length}</div>
        <div class="stat-sub">Last: ${lastRR ? esc(lastRR.date) : 'None'} (Pull ${lastRR ? esc(lastRR.pull_sets) : '-'})</div>
      </div>
    `;
    const isEmpty = !state.weightLog.length && !state.runLog.length && !state.rrSessions.length;
    const emptyHtml = isEmpty ? `
      <div class="stat-box" style="grid-column:1 / -1;">
        <div class="stat-label">No data in this browser</div>
        <div class="stat-sub">Your history isn't published with the site. Load your <code>data.json</code> once per browser:
          <button type="button" class="btn-inline" data-goto-tab="sync">6:sync -&gt; Load file</button></div>
      </div>` : '';
    document.getElementById('dashboard-kpis').innerHTML = emptyHtml + kpiHtml;

    // ASCII Progress Bar
    const barWidth = 28;
    const filled = Math.round((pct / 100) * barWidth);
    const barStr = '#'.repeat(filled) + '.'.repeat(Math.max(0, barWidth - filled));
    const lastZ2 = [...sortedRuns].reverse().find(r => r.hr && !L.runHrFlag(r) && /easy|zone\s*2|z2/i.test(r.type || ''));
    let eta = '';
    if (haveGoal && trend && trend.ratePerWeek < 0 && remaining > 0) {
      eta = ` (ETA ~${Math.ceil(remaining / -trend.ratePerWeek)} wk at current trend)`;
    }
    const ascii = [
      `START  : ${fmtKg(startW)}${startDate ? ` (${startDate})` : ''}`,
      `CURRENT: ${fmtKg(curWeight)} ([${barStr}] ${pct.toFixed(1)}%)`,
      `TARGET : ${fmtKg(targetW)}${eta}`,
      `CARDIO : ${lastVo2Run ? `VO2 Max ${lastVo2Run.vo2}` : 'VO2 Max -'}${m.rhr ? ` | RHR ${m.rhr} bpm` : ''}${lastZ2 ? ` | Latest Z2: ${Number(lastZ2.km).toFixed(2)} km @ ${lastZ2.hr} bpm` : ''}`
    ].join('\n');
    document.getElementById('ascii-progress').textContent = ascii;
    document.getElementById('weight-rate-summary').textContent = trendLine(trend);

    // Next Workout Target Table
    const nextTbody = document.querySelector('#next-target-table tbody');
    if (lastRR) {
      const rows = RR_SLOTS.map(([label, id]) => {
        const step = state.activeProgressions[id] || lastRR[id + '_prog'];
        const sets = lastRR[id + '_sets'];
        return [label, step, sets, nextBadge(id, step, nextFor(id, sets))];
      });
      nextTbody.innerHTML = rows.map(r => `
        <tr>
          <td><strong>${esc(r[0])}</strong></td>
          <td class="muted">${esc(r[1])}</td>
          <td>${esc(r[2])}</td>
          <td><span class="badge badge-invert">${r[3]}</span></td>
        </tr>
      `).join('') + `
        <tr>
          <td><strong>Core (2x)</strong></td>
          <td class="muted">Plank / Side / Arch</td>
          <td>${esc(lastRR.antiext)} | ${esc(lastRR.antirot)} | ${esc(lastRR.ext)}</td>
          <td><span class="badge badge-invert">+5s holds / +1 rep</span></td>
        </tr>
      `;
    } else {
      nextTbody.innerHTML = '<tr><td colspan="4" class="muted">No sessions logged yet.</td></tr>';
    }

    // Active Progressions Quick Switcher
    const progTbody = document.querySelector('#active-progressions-table tbody');
    progTbody.innerHTML = EXERCISE_DB.slice(0, 9).map(ex => {
      const currentVal = state.activeProgressions[ex.id] || ex.ladders[0];
      const optionsHtml = ex.ladders.map(l => `<option value="${esc(l)}" ${l === currentVal ? 'selected' : ''}>${esc(l)}</option>`).join('');
      return `
        <tr>
          <td><strong>${esc(ex.slot)}</strong></td>
          <td>
            <select data-prog-switch="${esc(ex.id)}" aria-label="${esc(ex.slot)} Progression">
              ${optionsHtml}
            </select>
          </td>
          <td>${esc(ex.targetRange)}</td>
          <td class="muted">${ex.maxRep ? `Hit ${ex.maxRep}x3 -> next level; below ${ex.minRep} -> easier step` : 'Extend hold time'}</td>
        </tr>
      `;
    }).join('');

    // Mini Schedule Table
    const miniSchedTbody = document.querySelector('#mini-schedule-table tbody');
    miniSchedTbody.innerHTML = state.schedule.map(s => `
      <tr>
        <td><strong>${esc(s.day)}</strong></td>
        <td>${esc(s.type)}</td>
        <td class="muted">${esc(s.rx)}</td>
      </tr>
    `).join('');
  }

  // ==========================================
  // RENDER VIEW 2: LOG & EDIT WORKOUTS
  // ==========================================
  function populateLoggerSelects() {
    RR_SLOTS.forEach(([, exId]) => {
      const sel = document.getElementById(`rr-${exId}-prog`);
      const ex = exById(exId);
      if (!sel || !ex.ladders) return;
      const active = state.activeProgressions[exId] || ex.ladders[0];
      sel.innerHTML = ex.ladders.map(l => `<option value="${esc(l)}" ${l === active ? 'selected' : ''}>${esc(l)}</option>`).join('');
    });
  }

  function renderRRHistory() {
    const tbody = document.querySelector('#rr-history-table tbody');
    const sorted = [...state.rrSessions].sort((a, b) => b.date.localeCompare(a.date));
    document.getElementById('rr-count-meta').textContent = `${sorted.length} session(s) logged`;

    const cell = (label, s, id) =>
      `<div><strong>${label}:</strong> ${esc(s[id + '_sets'])} <span class="muted">(${esc(shortProg(s[id + '_prog']))})</span></div>`;

    tbody.innerHTML = sorted.map(s => {
      const totalVol = RR_SLOTS.reduce((acc, [, id]) => acc + L.sumReps(s[id + '_sets']), 0);
      return `
        <tr>
          <td><strong>${esc(s.date)}</strong></td>
          <td>${s.bw ? Number(s.bw).toFixed(1) + 'kg' : '-'}</td>
          <td>${cell('P', s, 'pull')}${cell('S', s, 'squat')}</td>
          <td>${cell('D', s, 'dip')}${cell('H', s, 'hinge')}</td>
          <td>${cell('R', s, 'row')}${cell('PU', s, 'push')}</td>
          <td>
            <div>${esc(s.antiext)}</div>
            <div>${esc(s.antirot)}</div>
            <div>${esc(s.ext)}</div>
          </td>
          <td><strong>${totalVol}</strong> reps</td>
          <td class="muted">${esc(s.notes)}</td>
          <td>
            <div class="btn-row">
              <button type="button" class="btn-inline" data-edit-rr="${esc(s.id)}">edit</button>
              <button type="button" class="btn-inline" data-del-rr="${esc(s.id)}">del</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  function shortProg(str) {
    if (!str) return '';
    return str.replace(/^L\d:\s*/, '').split('(')[0].trim();
  }

  function parseShorthandToForm(raw) {
    const parsed = L.parseShorthand(raw);
    if (!parsed) return false;
    Object.entries(parsed).forEach(([field, val]) => {
      if (!val) return;
      const el = document.getElementById('rr-' + field.replace('_sets', '-sets'));
      if (el) el.value = val;
    });
    if (!document.getElementById('rr-date').value) {
      document.getElementById('rr-date').value = new Date().toISOString().slice(0, 10);
    }
    return true;
  }

  function prefillNextTargetIntoForm() {
    populateLoggerSelects();
    const last = getLatestRR();
    document.getElementById('rr-edit-id').value = '';
    document.getElementById('rr-form-title').textContent = 'Log New RR Session (Prefilled Next Target)';
    document.getElementById('rr-date').value = new Date().toISOString().slice(0, 10);
    const w = getLatestWeight();
    document.getElementById('rr-bw').value = w != null ? w.toFixed(1) : '';
    if (last) {
      RR_SLOTS.forEach(([, id]) => {
        const next = nextFor(id, last[id + '_sets']);
        document.getElementById(`rr-${id}-sets`).value = next.sets;
        // Level-up targets (minRep x3) belong to the next ladder step.
        const sel = document.getElementById(`rr-${id}-prog`);
        const up = next.action === 'level_up' && adjacentStep(id, sel.value, +1);
        if (up) sel.value = up;
      });
      document.getElementById('rr-antiext').value = last.antiext || 'Plank 2x30s';
      document.getElementById('rr-antirot').value = last.antirot || 'Side Plank 2x15s/side';
      document.getElementById('rr-ext').value = last.ext || 'Arch/RevHyper 2x8';
    }
  }

  // ==========================================
  // RENDER VIEW 3: PROGRAM & SCHEDULE
  // ==========================================
  function renderProgram() {
    const tbody = document.querySelector('#editable-schedule-table tbody');
    tbody.innerHTML = state.schedule.map((item, idx) => `
      <tr>
        <td><strong>${esc(item.day)}</strong></td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="type" value="${esc(item.type)}" aria-label="${esc(item.day)} session type">
        </td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="rx" value="${esc(item.rx)}" aria-label="${esc(item.day)} prescription">
        </td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="dur" value="${esc(item.dur)}" aria-label="${esc(item.day)} duration">
        </td>
      </tr>
    `).join('');

    const notesArea = document.getElementById('program-notes-area');
    if (notesArea && document.activeElement !== notesArea) {
      notesArea.value = state.programNotes || '';
    }
  }

  // ==========================================
  // RENDER VIEW 4: FORM & PROGRESSION LADDERS
  // ==========================================
  let currentFormFilter = 'all';

  function renderFormGuides() {
    const container = document.getElementById('form-guides-container');
    const list = currentFormFilter === 'all'
      ? EXERCISE_DB
      : EXERCISE_DB.filter(e => e.category === currentFormFilter);

    container.innerHTML = list.map(ex => {
      const currentProg = state.activeProgressions[ex.id] || ex.ladders[0];
      const customNote = state.customNotes[ex.id] !== undefined ? state.customNotes[ex.id] : (ex.defaultNote || '');

      const ladderHtml = ex.ladders.map(step => {
        const isCur = step === currentProg;
        return `
          <li class="ladder-item ${isCur ? 'current' : ''}">
            <span>${esc(step)}</span>
            ${isCur
              ? '<span class="badge">ACTIVE</span>'
              : `<button type="button" class="btn-inline" data-set-ladder="${esc(ex.id)}" data-step="${esc(step)}">Set Active</button>`
            }
          </li>
        `;
      }).join('');

      const cuesHtml = ex.cues.map(c => `<li>- ${esc(c)}</li>`).join('');

      return `
        <div class="tile col-6">
          <div class="tile-header">
            <span>${esc(ex.slot)}</span>
            <span class="meta">Target: ${esc(ex.targetRange)}</span>
          </div>
          <div class="tile-body">
            <h4>Bodyweight Progression Ladder</h4>
            <ul class="ladder-list">${ladderHtml}</ul>

            <h4 style="margin-top:10px;">Strict Form Cues (Tempo 10X0)</h4>
            <ul style="list-style:none; margin-bottom:8px; font-size:12px;">${cuesHtml}</ul>

            <p style="font-size:11px;" class="muted"><strong>Avoid Faults:</strong> ${esc(ex.faults)}</p>

            <div class="field" style="margin-top:8px;">
              <label for="note-${ex.id}">Personal Setup / Form Note:</label>
              <div class="btn-row">
                <input type="text" id="note-${ex.id}" data-ex-note="${ex.id}" value="${esc(customNote)}" style="flex:1;">
                <button type="button" class="btn-inline" data-save-ex-note="${ex.id}">Save</button>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  // ==========================================
  // RENDER VIEW 5: RUNS, WEIGHT & METRICS
  // ==========================================
  const EASY_HR_CAP = L.RUN_HR_RULES[0].cap;

  function renderMetrics() {
    // Weight Table & SVG Chart
    const sortedW = [...state.weightLog].sort((a, b) => a.date.localeCompare(b.date));
    const trend = L.weightTrend(state.weightLog, 28, state.meta.maxLossPctPerWeek || 1.0);
    document.getElementById('weight-goal-meta').textContent =
      state.meta.targetWeight != null ? `Goal: ${Number(state.meta.targetWeight).toFixed(1)} kg` : '';
    document.getElementById('weight-trend-meta').textContent = trendLine(trend);

    const wTbody = document.querySelector('#weight-table tbody');
    wTbody.innerHTML = [...sortedW].reverse().map((w, i, arr) => {
      const prev = arr[i + 1];
      const delta = prev ? (w.kg - prev.kg) : 0;
      const deltaStr = prev ? (delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)) : '-';
      // 7-day rolling mean ending on this entry
      const d = L.isoToDay(w.date);
      const win = sortedW.filter(x => { const xd = L.isoToDay(x.date); return xd <= d && xd > d - 7; });
      const avg = win.reduce((a, x) => a + Number(x.kg), 0) / win.length;
      return `
        <tr>
          <td><strong>${esc(w.date)}</strong></td>
          <td>${Number(w.kg).toFixed(1)} kg</td>
          <td>${avg.toFixed(1)} kg <span class="muted">(n=${win.length})</span></td>
          <td class="muted">${deltaStr} kg</td>
          <td><button type="button" class="btn-inline" data-del-wt="${esc(w.id)}">del</button></td>
        </tr>
      `;
    }).join('');

    renderWeightSvg(sortedW);

    // Run Table & SVG Chart
    const sortedRAsc = [...state.runLog].sort((a, b) => a.date.localeCompare(b.date));
    renderRunSvg(sortedRAsc);

    const sortedR = [...sortedRAsc].reverse();
    const totalKm = sortedR.reduce((a, r) => a + Number(r.km || 0), 0);
    const withHr = sortedR.filter(r => r.hr);
    const avgHr = withHr.length ? Math.round(withHr.reduce((a, r) => a + Number(r.hr), 0) / withHr.length) : 0;
    const flagged = sortedR.filter(r => L.runHrFlag(r)).length;
    document.getElementById('run-summary-meta').textContent =
      `${sortedR.length} runs | ${totalKm.toFixed(2)} km total | Avg HR ${avgHr} bpm | ${flagged} over HR cap`;

    const rTbody = document.querySelector('#run-table tbody');
    rTbody.innerHTML = sortedR.map(r => {
      const flag = L.runHrFlag(r);
      const hrDisplay = r.hr ? `${esc(r.hr)}${r.maxHr ? ' / ' + esc(r.maxHr) : ''} bpm` : '-';
      const flagHtml = flag ? `<br><strong title="Planned ${flag.label} run: cap ${flag.cap} bpm">! +${flag.over} over ${flag.cap}</strong>` : '';
      return `
        <tr>
          <td><strong>${esc(r.date)}</strong></td>
          <td>${esc(r.type)}</td>
          <td><strong>${Number(r.km).toFixed(2)} km</strong></td>
          <td>${Number(r.min).toFixed(1)} m</td>
          <td>${L.pace(Number(r.km), Number(r.min))}/km</td>
          <td>${hrDisplay}${flagHtml}</td>
          <td class="muted">${r.power ? esc(r.power) + 'W' : '-'}</td>
          <td>${r.vo2 ? Number(r.vo2).toFixed(1) : '-'}</td>
          <td class="muted">${esc(r.notes)}</td>
          <td><button type="button" class="btn-inline" data-del-run="${esc(r.id)}">del</button></td>
        </tr>
      `;
    }).join('');

    // Weekly volume (Mon-Sun) with >10% jump flag
    const weeks = L.weeklyKm(state.runLog);
    const today = L.isoToDay(new Date().toISOString().slice(0, 10));
    document.querySelector('#weekly-km-table tbody').innerHTML = [...weeks].reverse().map(w => {
      const inProgress = today - L.isoToDay(w.weekStart) < 7;
      const change = w.change == null ? '-' : `${w.change > 0 ? '+' : ''}${Math.round(w.change * 100)}%`;
      return `
      <tr>
        <td><strong>${esc(w.weekStart)}</strong>${inProgress ? ' <span class="muted">(in progress)</span>' : ''}</td>
        <td>${w.km.toFixed(1)} km</td>
        <td class="${w.jump ? '' : 'muted'}">${inProgress && !w.jump ? '-' : change}${w.jump ? ' <strong>! &gt;10%</strong>' : ''}</td>
      </tr>
    `;
    }).join('');
  }

  function renderRunSvg(sortedR) {
    const wrap = document.getElementById('run-svg-wrap');
    if (!wrap) return;
    if (!sortedR.length) {
      wrap.innerHTML = '<div class="muted">No runs logged yet.</div>';
      return;
    }
    const W = 620, H = 160, padL = 38, padR = 36, padT = 18, padB = 26;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;
    const minHr = 135, maxHr = 175;
    const maxKm = Math.max(12, ...sortedR.map(r => Number(r.km || 0)));

    const xFor = idx => sortedR.length === 1 ? padL + plotW / 2 : padL + (idx / (sortedR.length - 1)) * plotW;
    const yForHr = hr => padT + plotH - ((Math.min(maxHr, Math.max(minHr, hr || 150)) - minHr) / (maxHr - minHr)) * plotH;
    const hForKm = km => (Math.min(maxKm, km || 0) / maxKm) * plotH;

    const z2Y = yForHr(EASY_HR_CAP);
    const hrPts = sortedR.filter(r => r.hr).map(r => `${xFor(sortedR.indexOf(r)).toFixed(1)},${yForHr(r.hr).toFixed(1)}`).join(' ');

    const barsAndDots = sortedR.map((r, i) => {
      const cx = xFor(i);
      const bh = hForKm(r.km);
      const by = padT + plotH - bh;
      const hy = yForHr(r.hr);
      const isZ2 = r.hr && r.hr <= EASY_HR_CAP;
      return `
        <rect x="${(cx - 10).toFixed(1)}" y="${by.toFixed(1)}" width="20" height="${bh.toFixed(1)}" fill="var(--bg-hover)" stroke="var(--border-strong)" stroke-width="1" />
        <text x="${cx.toFixed(1)}" y="${(by + 11).toFixed(1)}" text-anchor="middle" font-size="8.5" fill="var(--fg-muted)">${Number(r.km).toFixed(1)}k</text>
        ${r.hr ? `<circle cx="${cx.toFixed(1)}" cy="${hy.toFixed(1)}" r="${isZ2 ? 4.5 : 3.5}" fill="currentColor" />
        <text x="${cx.toFixed(1)}" y="${(hy - 7).toFixed(1)}" text-anchor="middle" font-size="9.5" font-weight="${isZ2 ? '700' : '400'}" fill="currentColor">${esc(r.hr)}</text>` : ''}
        <text x="${cx.toFixed(1)}" y="${H - 7}" text-anchor="middle" font-size="9" fill="var(--fg-muted)">${esc(r.date.slice(5))}</text>
      `;
    }).join('');

    wrap.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" width="100%" height="160" role="img" aria-label="Running distance and heart rate trend chart">
        <line x1="${padL}" y1="${yForHr(165)}" x2="${W - padR}" y2="${yForHr(165)}" stroke="var(--border)" stroke-dasharray="2,2"/>
        <text x="4" y="${yForHr(165) + 3}" font-size="8.5" fill="var(--fg-muted)">165 bpm</text>
        <line x1="${padL}" y1="${z2Y.toFixed(1)}" x2="${W - padR}" y2="${z2Y.toFixed(1)}" stroke="var(--border-strong)" stroke-dasharray="4,3"/>
        <text x="4" y="${(z2Y + 3).toFixed(1)}" font-size="8.5" fill="currentColor">${EASY_HR_CAP} Z2</text>
        <text x="${W - padR + 4}" y="${padT + 8}" font-size="8.5" fill="var(--fg-muted)">Bars: km</text>
        <text x="${W - padR + 4}" y="${padT + 20}" font-size="8.5" fill="currentColor">Line: HR</text>
        ${barsAndDots}
        <polyline fill="none" stroke="currentColor" stroke-width="1.8" points="${hrPts}" />
      </svg>
    `;
  }

  function renderWeightSvg(sortedW) {
    const wrap = document.getElementById('weight-svg-wrap');
    if (!sortedW.length) {
      wrap.innerHTML = '<div class="muted">No weight entries yet.</div>';
      return;
    }
    const W = 500, H = 155, padL = 38, padR = 18, padT = 14, padB = 24;
    const target = state.meta.targetWeight != null ? Number(state.meta.targetWeight) : null;
    const kgs = sortedW.map(w => Number(w.kg)).concat(target != null ? [target] : []);
    const minKg = Math.floor(Math.min(...kgs) - 1);
    const maxKg = Math.ceil(Math.max(...kgs) + 1);
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const yFor = kg => padT + plotH - ((kg - minKg) / (maxKg - minKg)) * plotH;
    // Time-proportional x axis so sparse weigh-ins aren't evenly spaced.
    const d0 = L.isoToDay(sortedW[0].date);
    const span = Math.max(1, L.isoToDay(sortedW[sortedW.length - 1].date) - d0);
    const xFor = w => sortedW.length === 1 ? padL + plotW / 2 : padL + ((L.isoToDay(w.date) - d0) / span) * plotW;

    const pts = sortedW.map(d => `${xFor(d).toFixed(1)},${yFor(d.kg).toFixed(1)}`).join(' ');
    const circles = sortedW.map(d => {
      const cx = xFor(d).toFixed(1);
      const cy = yFor(d.kg).toFixed(1);
      return `
        <circle cx="${cx}" cy="${cy}" r="3.5" fill="currentColor" />
        <text x="${cx}" y="${cy - 7}" text-anchor="middle" font-size="10" fill="currentColor">${Number(d.kg).toFixed(1)}</text>
        <text x="${cx}" y="${H - 6}" text-anchor="middle" font-size="9" fill="var(--fg-muted)">${esc(d.date.slice(5))}</text>
      `;
    }).join('');

    const gridKg = [maxKg - 1, Math.round((minKg + maxKg) / 2)];
    const grid = gridKg.map(kg => `
        <line x1="${padL}" y1="${yFor(kg)}" x2="${W - padR}" y2="${yFor(kg)}" stroke="var(--border)" stroke-dasharray="2,2"/>
        <text x="4" y="${yFor(kg) + 3}" font-size="9" fill="var(--fg-muted)">${kg}kg</text>`).join('');
    const targetLine = target == null ? '' : `
        <line x1="${padL}" y1="${yFor(target)}" x2="${W - padR}" y2="${yFor(target)}" stroke="var(--border-strong)" stroke-dasharray="4,3"/>
        <text x="4" y="${yFor(target) + 3}" font-size="9" fill="currentColor">${target.toFixed(1)}</text>`;

    wrap.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" width="100%" height="155" role="img" aria-label="Weight progress chart">
        ${grid}
        ${targetLine}
        <polyline fill="none" stroke="currentColor" stroke-width="2" points="${pts}" />
        ${circles}
      </svg>
    `;
  }

  // ==========================================
  // RENDER VIEW 6: EXPORT & SYNC PREVIEW
  // ==========================================
  function generateMarkdownExport() {
    const lines = [
      '# FIT // WORKOUT & RECOMPOSITION LOG',
      '',
      `- **Current Weight:** ${fmtKg(getLatestWeight())} (Start: ${fmtKg(state.meta.startWeight)} -> Goal: ${fmtKg(state.meta.targetWeight)})`,
      `- **Cardio Vitals:** VO2 Max ${(L.latestBy(state.runLog, 'vo2') || {}).vo2 || '-'} mL/(kg·min) | Resting HR ${state.meta.rhr || '-'} bpm`,
      '',
      '## Recommended Routine Sessions',
      '',
      '| Date | BW | Pull | Squat | Dip | Hinge | Row | Push | Core Triplet (2x) | Notes |',
      '| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |'
    ];
    const sorted = [...state.rrSessions].sort((a, b) => b.date.localeCompare(a.date));
    sorted.forEach(s => {
      lines.push(`| ${s.date} | ${s.bw || '-'} | ${s.pull_sets} | ${s.squat_sets} | ${s.dip_sets} | ${s.hinge_sets} | ${s.row_sets} | ${s.push_sets} | ${s.antiext}, ${s.antirot}, ${s.ext} | ${s.notes || ''} |`);
    });

    lines.push('', '## Apple Watch Running Log', '');
    lines.push('| Date | Type | Distance | Duration | Pace | Avg / Max HR | Power | VO2 Max | Notes |');
    lines.push('| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |');
    const sortedR = [...state.runLog].sort((a, b) => b.date.localeCompare(a.date));
    sortedR.forEach(r => {
      lines.push(`| ${r.date} | ${r.type} | ${Number(r.km).toFixed(2)} km | ${Number(r.min).toFixed(1)} m | ${L.pace(Number(r.km), Number(r.min))}/km | ${r.hr || '-'}${r.maxHr ? '/' + r.maxHr : ''} bpm | ${r.power ? r.power + 'W' : '-'} | ${r.vo2 || '-'} | ${r.notes || ''} |`);
    });

    return lines.join('\n');
  }

  function generateCsvExport() {
    const header = 'date,bw_kg,pull_prog,pull_sets,squat_prog,squat_sets,dip_prog,dip_sets,hinge_prog,hinge_sets,row_prog,row_sets,push_prog,push_sets,antiext,antirot,ext,notes';
    const rows = state.rrSessions.map(s => [
      s.date, s.bw || '', s.pull_prog, s.pull_sets, s.squat_prog, s.squat_sets,
      s.dip_prog, s.dip_sets, s.hinge_prog, s.hinge_sets, s.row_prog, s.row_sets,
      s.push_prog, s.push_sets, s.antiext, s.antirot, s.ext, s.notes || ''
    ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','));
    return [header, ...rows].join('\n');
  }

  function renderSync() {
    const preview = document.getElementById('export-preview');
    if (preview) {
      preview.value = generateMarkdownExport();
    }
    let savedRepo = null, remembered = false;
    try {
      savedRepo = localStorage.getItem(GH_REPO_KEY);
      remembered = !!localStorage.getItem(GH_REMEMBER_KEY);
    } catch (e) {}
    const repoInput = document.getElementById('gh-repo');
    if (savedRepo && repoInput) repoInput.value = savedRepo;
    const rememberBox = document.getElementById('gh-remember');
    if (rememberBox && remembered) rememberBox.checked = true;
  }

  function renderAll() {
    renderStatus();
    populateLoggerSelects();
    renderRRHistory();
    renderProgram();
    renderFormGuides();
    renderMetrics();
    renderSync();
  }

  // ==========================================
  // TIMER (Web Audio API monochrome beep)
  // ==========================================
  let timerSec = 90;
  let timerTarget = 90;
  let timerInterval = null;

  function playBeep(freq = 880, dur = 0.12) {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = new Ctx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.value = freq;
      gain.gain.value = 0.08;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + dur);
    } catch (e) {}
  }

  function updateTimerDisplay() {
    const m = Math.floor(timerSec / 60).toString().padStart(2, '0');
    const s = (timerSec % 60).toString().padStart(2, '0');
    document.getElementById('bar-timer-display').textContent = `${m}:${s}`;
  }

  function toggleTimer() {
    const btn = document.getElementById('bar-timer-toggle');
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
      btn.textContent = 'start';
      btn.classList.remove('active');
    } else {
      if (timerSec <= 0) timerSec = timerTarget;
      btn.textContent = 'pause';
      btn.classList.add('active');
      timerInterval = setInterval(() => {
        timerSec -= 1;
        updateTimerDisplay();
        if (timerSec > 0 && timerSec <= 3) playBeep(660, 0.08);
        if (timerSec <= 0) {
          clearInterval(timerInterval);
          timerInterval = null;
          btn.textContent = 'start';
          btn.classList.remove('active');
          playBeep(1046, 0.35);
          showToast('REST COMPLETE');
        }
      }, 1000);
    }
  }

  // ==========================================
  // COLOR SCHEME (Follow System + Override)
  // ==========================================
  const COLOR_SCHEME_KEY = 'color-scheme';
  const darkMql = window.matchMedia('(prefers-color-scheme: dark)');

  function getSystemScheme() {
    return darkMql.matches ? 'dark' : 'light';
  }

  function applyColorSchemeMeta() {
    const meta = document.querySelector('meta[name="color-scheme"]');
    let stored = null;
    try {
      stored = localStorage.getItem(COLOR_SCHEME_KEY);
    } catch (e) {}
    const validOverride = (stored === 'light' || stored === 'dark') ? stored : null;
    if (meta) {
      meta.content = validOverride || 'light dark';
    }
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = validOverride ? `inv:${validOverride}` : 'inv:auto';
      btn.title = validOverride
        ? `Theme pinned to ${validOverride} (click to revert to system auto, shortcut: t)`
        : `Following system (${getSystemScheme()}) — click to override (shortcut: t)`;
    }
  }

  function toggleColorScheme() {
    let stored = null;
    try {
      stored = localStorage.getItem(COLOR_SCHEME_KEY);
    } catch (e) {}
    const sys = getSystemScheme();
    const rendered = (stored === 'light' || stored === 'dark') ? stored : sys;
    const target = rendered === 'dark' ? 'light' : 'dark';

    try {
      if (target !== sys) {
        localStorage.setItem(COLOR_SCHEME_KEY, target);
        showToast(`THEME OVERRIDE: ${target.toUpperCase()}`);
      } else {
        localStorage.removeItem(COLOR_SCHEME_KEY);
        showToast('THEME: FOLLOW SYSTEM (AUTO)');
      }
    } catch (e) {}

    const meta = document.querySelector('meta[name="color-scheme"]');
    if (meta) {
      meta.content = target !== sys ? target : 'light dark';
    }
    applyColorSchemeMeta();
  }

  window.addEventListener('storage', e => {
    if (e.key === COLOR_SCHEME_KEY) {
      applyColorSchemeMeta();
    }
  });
  darkMql.addEventListener('change', () => {
    applyColorSchemeMeta();
  });

  // ==========================================
  // EVENT LISTENERS & NAVIGATION
  // ==========================================
  function switchTab(tabName) {
    document.querySelectorAll('.dwm-tag').forEach(btn => {
      btn.setAttribute('aria-selected', btn.dataset.tab === tabName ? 'true' : 'false');
    });
    document.querySelectorAll('.view-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === 'view-' + tabName);
    });
  }

  document.addEventListener('click', e => {
    const tabBtn = e.target.closest('.dwm-tag');
    if (tabBtn) {
      switchTab(tabBtn.dataset.tab);
      return;
    }

    const gotoBtn = e.target.closest('[data-goto-tab]');
    if (gotoBtn) {
      switchTab(gotoBtn.dataset.gotoTab);
      return;
    }

    const timerSet = e.target.closest('[data-timer-set]');
    if (timerSet) {
      timerTarget = parseInt(timerSet.dataset.timerSet, 10);
      timerSec = timerTarget;
      updateTimerDisplay();
      if (!timerInterval) toggleTimer();
      return;
    }

    if (e.target.id === 'bar-timer-toggle') {
      toggleTimer();
      return;
    }

    if (e.target.id === 'theme-toggle') {
      toggleColorScheme();
      return;
    }

    if (e.target.id === 'btn-prefill-next' || e.target.id === 'btn-fill-from-last') {
      prefillNextTargetIntoForm();
      switchTab('log');
      showToast('LOADED NEXT OVERLOAD TARGET');
      return;
    }

    if (e.target.id === 'btn-reset-rr-form') {
      document.getElementById('rr-session-form').reset();
      document.getElementById('rr-edit-id').value = '';
      document.getElementById('rr-form-title').textContent = 'Log / Edit Recommended Routine Session';
      document.getElementById('rr-date').value = new Date().toISOString().slice(0, 10);
      populateLoggerSelects();
      return;
    }

    // Edit or delete RR session
    const editId = e.target.getAttribute('data-edit-rr');
    if (editId) {
      const sess = state.rrSessions.find(x => x.id === editId);
      if (sess) {
        populateLoggerSelects();
        document.getElementById('rr-edit-id').value = sess.id;
        document.getElementById('rr-form-title').textContent = `Editing Session: ${sess.date}`;
        document.getElementById('rr-date').value = sess.date;
        document.getElementById('rr-bw').value = sess.bw || '';
        document.getElementById('rr-notes').value = sess.notes || '';
        document.getElementById('rr-pull-prog').value = sess.pull_prog;
        document.getElementById('rr-pull-sets').value = sess.pull_sets;
        document.getElementById('rr-squat-prog').value = sess.squat_prog;
        document.getElementById('rr-squat-sets').value = sess.squat_sets;
        document.getElementById('rr-dip-prog').value = sess.dip_prog;
        document.getElementById('rr-dip-sets').value = sess.dip_sets;
        document.getElementById('rr-hinge-prog').value = sess.hinge_prog;
        document.getElementById('rr-hinge-sets').value = sess.hinge_sets;
        document.getElementById('rr-row-prog').value = sess.row_prog;
        document.getElementById('rr-row-sets').value = sess.row_sets;
        document.getElementById('rr-push-prog').value = sess.push_prog;
        document.getElementById('rr-push-sets').value = sess.push_sets;
        document.getElementById('rr-antiext').value = sess.antiext;
        document.getElementById('rr-antirot').value = sess.antirot;
        document.getElementById('rr-ext').value = sess.ext;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        showToast('LOADED FOR EDITING');
      }
      return;
    }

    const delId = e.target.getAttribute('data-del-rr');
    if (delId) {
      state.rrSessions = state.rrSessions.filter(x => x.id !== delId);
      saveState('SESSION DELETED');
      return;
    }

    // Set ladder step active from Form tab
    const ladderEx = e.target.getAttribute('data-set-ladder');
    if (ladderEx) {
      state.activeProgressions[ladderEx] = e.target.getAttribute('data-step');
      saveState('PROGRESSION UPDATED');
      return;
    }

    // Save custom exercise note
    const noteEx = e.target.getAttribute('data-save-ex-note');
    if (noteEx) {
      const inp = document.getElementById('note-' + noteEx);
      if (inp) {
        state.customNotes[noteEx] = inp.value;
        saveState('FORM NOTE SAVED');
      }
      return;
    }

    // Filter form guides
    const filterBtn = e.target.closest('[data-form-filter]');
    if (filterBtn) {
      currentFormFilter = filterBtn.dataset.formFilter;
      document.querySelectorAll('[data-form-filter]').forEach(b => b.classList.toggle('active', b === filterBtn));
      renderFormGuides();
      return;
    }

    // Delete weight or run
    const delWt = e.target.getAttribute('data-del-wt');
    if (delWt) {
      state.weightLog = state.weightLog.filter(w => w.id !== delWt);
      saveState('WEIGHT ENTRY DELETED');
      return;
    }

    const delRun = e.target.getAttribute('data-del-run');
    if (delRun) {
      state.runLog = state.runLog.filter(r => r.id !== delRun);
      saveState('RUN DELETED');
      return;
    }
  });

  // Progression dropdown switch on Dashboard
  document.addEventListener('change', e => {
    const progSwitch = e.target.getAttribute('data-prog-switch');
    if (progSwitch) {
      state.activeProgressions[progSwitch] = e.target.value;
      saveState('PROGRESSION UPDATED');
      return;
    }

    const schedIdx = e.target.getAttribute('data-sched-idx');
    if (schedIdx !== null) {
      const idx = parseInt(schedIdx, 10);
      const field = e.target.getAttribute('data-sched-field');
      if (state.schedule[idx] && field) {
        state.schedule[idx][field] = e.target.value;
        saveState('SCHEDULE UPDATED');
      }
    }
  });

  // Shorthand Form
  document.getElementById('shorthand-form').addEventListener('submit', e => {
    e.preventDefault();
    const raw = document.getElementById('shorthand-input').value;
    if (parseShorthandToForm(raw)) {
      showToast('PARSED INTO FORM');
    }
  });

  document.getElementById('btn-parse-and-save').addEventListener('click', () => {
    const raw = document.getElementById('shorthand-input').value;
    if (parseShorthandToForm(raw)) {
      document.getElementById('rr-session-form').requestSubmit();
    }
  });

  // Save RR Session Form
  document.getElementById('rr-session-form').addEventListener('submit', e => {
    e.preventDefault();
    const editId = document.getElementById('rr-edit-id').value;
    const dateVal = document.getElementById('rr-date').value || new Date().toISOString().slice(0, 10);
    const bwVal = parseFloat(document.getElementById('rr-bw').value);

    const entry = {
      id: editId || ('rr-' + Date.now()),
      date: dateVal,
      bw: !isNaN(bwVal) ? bwVal : getLatestWeight(),
      pull_prog: document.getElementById('rr-pull-prog').value,
      pull_sets: document.getElementById('rr-pull-sets').value.trim(),
      squat_prog: document.getElementById('rr-squat-prog').value,
      squat_sets: document.getElementById('rr-squat-sets').value.trim(),
      dip_prog: document.getElementById('rr-dip-prog').value,
      dip_sets: document.getElementById('rr-dip-sets').value.trim(),
      hinge_prog: document.getElementById('rr-hinge-prog').value,
      hinge_sets: document.getElementById('rr-hinge-sets').value.trim(),
      row_prog: document.getElementById('rr-row-prog').value,
      row_sets: document.getElementById('rr-row-sets').value.trim(),
      push_prog: document.getElementById('rr-push-prog').value,
      push_sets: document.getElementById('rr-push-sets').value.trim(),
      antiext: document.getElementById('rr-antiext').value.trim(),
      antirot: document.getElementById('rr-antirot').value.trim(),
      ext: document.getElementById('rr-ext').value.trim(),
      notes: document.getElementById('rr-notes').value.trim()
    };

    if (editId) {
      const idx = state.rrSessions.findIndex(x => x.id === editId);
      if (idx !== -1) state.rrSessions[idx] = entry;
    } else {
      state.rrSessions.push(entry);
    }

    // Also update active progressions to match logged session
    state.activeProgressions.pull = entry.pull_prog;
    state.activeProgressions.squat = entry.squat_prog;
    state.activeProgressions.dip = entry.dip_prog;
    state.activeProgressions.hinge = entry.hinge_prog;
    state.activeProgressions.row = entry.row_prog;
    state.activeProgressions.push = entry.push_prog;

    document.getElementById('rr-edit-id').value = '';
    document.getElementById('rr-form-title').textContent = 'Log / Edit Recommended Routine Session';
    saveState('RR SESSION SAVED');
  });

  // Program Notes & Reset Schedule
  document.getElementById('program-notes-form').addEventListener('submit', e => {
    e.preventDefault();
    state.programNotes = document.getElementById('program-notes-area').value;
    saveState('PROGRAM NOTES SAVED');
  });

  document.getElementById('btn-save-program-notes').addEventListener('click', () => {
    state.programNotes = document.getElementById('program-notes-area').value;
    saveState('PROGRAM NOTES SAVED');
  });

  document.getElementById('btn-reset-schedule').addEventListener('click', () => {
    state.schedule = clone(DEFAULT_STATE.schedule);
    saveState('DEFAULT SCHEDULE RESTORED');
  });

  // Weight Form
  document.getElementById('weight-form').addEventListener('submit', e => {
    e.preventDefault();
    const date = document.getElementById('wt-date').value;
    const kg = parseFloat(document.getElementById('wt-val').value);
    if (!date || isNaN(kg)) return;
    state.weightLog.push({
      id: 'w-' + Date.now(),
      date,
      kg,
      kcal: null
    });
    document.getElementById('wt-val').value = '';
    saveState('WEIGHT LOGGED');
  });

  // Run Form
  document.getElementById('run-form').addEventListener('submit', e => {
    e.preventDefault();
    const date = document.getElementById('run-date').value;
    const type = document.getElementById('run-type').value;
    const km = parseFloat(document.getElementById('run-km').value);
    const min = parseFloat(document.getElementById('run-min').value);
    const hr = parseInt(document.getElementById('run-hr').value, 10);
    const notes = document.getElementById('run-notes').value.trim();
    if (!date || isNaN(km) || isNaN(min)) return;
    state.runLog.push({
      id: 'r-' + Date.now(),
      date,
      type,
      km,
      min,
      hr: !isNaN(hr) ? hr : null,
      notes
    });
    document.getElementById('run-km').value = '';
    document.getElementById('run-min').value = '';
    saveState('RUN LOGGED');
  });

  // Export Downloads
  function downloadFile(filename, content, mime = 'text/plain') {
    const blob = new Blob([content], { type: mime });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  document.getElementById('btn-export-md').addEventListener('click', () => {
    downloadFile('WORKOUT_LOG.md', generateMarkdownExport(), 'text/markdown');
  });
  document.getElementById('btn-export-csv').addEventListener('click', () => {
    downloadFile('rr_log.csv', generateCsvExport(), 'text/csv');
  });
  document.getElementById('btn-export-json').addEventListener('click', () => {
    downloadFile('fit_state.json', JSON.stringify(state, null, 2), 'application/json');
  });
  document.getElementById('btn-copy-md').addEventListener('click', () => {
    navigator.clipboard.writeText(generateMarkdownExport()).then(() => showToast('MARKDOWN COPIED'));
  });

  // Import JSON & Factory Reset
  document.getElementById('import-json-form').addEventListener('submit', e => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(document.getElementById('import-json-input').value);
      state = withDefaults(parsed);
      saveState('STATE IMPORTED', { replaced: true });
    } catch (err) {
      showToast('INVALID JSON');
    }
  });

  document.getElementById('import-json-file').addEventListener('change', async e => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    try {
      state = withDefaults(JSON.parse(await file.text()));
      saveState(`IMPORTED ${file.name}`, { replaced: true });
      switchTab('status');
    } catch (err) {
      showToast('INVALID JSON FILE');
    }
    e.target.value = '';
  });

  document.getElementById('btn-factory-reset').addEventListener('click', () => {
    if (!confirm('Erase ALL logged data in this browser? (Synced data on GitHub is not deleted.) Export JSON first if unsure.')) return;
    forgetToken();
    state = clone(DEFAULT_STATE);
    saveState('ALL DATA CLEARED', { replaced: true, noSync: true });
  });

  // ==========================================
  // GITHUB SYNC (private repos only: this data is personal)
  // Merges both ways (lib.js mergeStates), so devices never overwrite each other.
  // ==========================================
  function ghHeaders(token, accept = 'application/vnd.github+json') {
    return {
      'Authorization': `Bearer ${token}`,
      'Accept': accept,
      'X-GitHub-Api-Version': '2022-11-28'
    };
  }

  function ghError(res, text) {
    const err = new Error(`GitHub API ${res.status}${text ? ': ' + text.slice(0, 160) : ''}`);
    err.status = res.status;
    return err;
  }

  const verifiedPrivate = new Set();
  async function assertPrivateRepo(repo, token) {
    if (verifiedPrivate.has(repo)) return;
    const res = await fetch(`https://api.github.com/repos/${repo}`, { headers: ghHeaders(token), cache: 'no-store' });
    if (res.status === 401) throw new Error('Token rejected (expired or revoked?). Paste a new one in 6:sync.');
    if (!res.ok) throw new Error(`Cannot read repo ${repo} (HTTP ${res.status}). Check the name and token.`);
    const info = await res.json();
    if (!info.private) {
      throw new Error(`Refusing to sync: ${repo} is PUBLIC. Use a private repo for your data (e.g. ${repo.split('/')[0]}/FIT-data).`);
    }
    verifiedPrivate.add(repo);
  }

  function b64encodeUtf8(str) {
    return btoa(unescape(encodeURIComponent(str)));
  }

  function b64decodeUtf8(b64) {
    const bin = atob(b64.replace(/\n/g, ''));
    return new TextDecoder().decode(Uint8Array.from(bin, c => c.charCodeAt(0)));
  }

  async function getFile(cfg, path) {
    const res = await fetch(
      `https://api.github.com/repos/${cfg.repo}/contents/${path}?ref=${encodeURIComponent(cfg.branch)}`,
      { headers: ghHeaders(cfg.token), cache: 'no-store' }
    );
    if (res.status === 404) return { text: null, sha: null };
    if (!res.ok) throw ghError(res, await res.text());
    const json = await res.json();
    return { text: b64decodeUtf8(json.content || ''), sha: json.sha };
  }

  async function putFile(cfg, path, text, sha, message) {
    const body = { message, content: b64encodeUtf8(text), branch: cfg.branch };
    if (sha) body.sha = sha;
    const res = await fetch(`https://api.github.com/repos/${cfg.repo}/contents/${path}`, {
      method: 'PUT',
      headers: Object.assign(ghHeaders(cfg.token), { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body)
    });
    if (!res.ok) throw ghError(res, await res.text());
  }

  function getToken() {
    const typed = document.getElementById('gh-token').value.trim();
    if (typed) return typed;
    try {
      return sessionStorage.getItem(GH_TOKEN_KEY) || localStorage.getItem(GH_REMEMBER_KEY) || '';
    } catch (e) {
      return '';
    }
  }

  function getSyncConfig() {
    const token = getToken();
    if (!token) return null;
    const repo = document.getElementById('gh-repo').value.trim();
    const branch = document.getElementById('gh-branch').value.trim() || 'main';
    return repo ? { repo, branch, token } : null;
  }

  function storeToken() {
    const token = document.getElementById('gh-token').value.trim();
    const repo = document.getElementById('gh-repo').value.trim();
    const remember = document.getElementById('gh-remember').checked;
    try {
      if (repo) localStorage.setItem(GH_REPO_KEY, repo);
      if (token) sessionStorage.setItem(GH_TOKEN_KEY, token);
      if (remember && token) localStorage.setItem(GH_REMEMBER_KEY, token);
      if (!remember) localStorage.removeItem(GH_REMEMBER_KEY);
    } catch (e) {}
  }

  function forgetToken() {
    try {
      localStorage.removeItem(GH_REMEMBER_KEY);
      sessionStorage.removeItem(GH_TOKEN_KEY);
    } catch (e) {}
    document.getElementById('gh-token').value = '';
    document.getElementById('gh-remember').checked = false;
    setSyncStatus('off');
  }

  function setSyncStatus(kind, detail = '') {
    const bar = document.getElementById('bar-sync');
    const statusEl = document.getElementById('gh-sync-status');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const label = {
      off: 'sync:off',
      busy: 'sync:...',
      ok: `sync:ok ${time}`,
      error: 'sync:ERR'
    }[kind];
    if (bar) {
      bar.textContent = label;
      bar.title = detail || label;
    }
    if (statusEl && (detail || kind !== 'busy')) {
      statusEl.textContent = detail || (kind === 'ok' ? `In sync at ${time}.` : kind === 'off' ? 'Automatic sync is off on this device.' : '');
    }
  }

  let syncTimer = null;
  let syncing = false;
  let syncQueued = false;

  function scheduleSync(delayMs = 4000) {
    if (!getSyncConfig()) return;
    clearTimeout(syncTimer);
    syncTimer = setTimeout(() => syncNow(), delayMs);
  }

  async function syncNow({ loud = false } = {}) {
    const cfg = getSyncConfig();
    if (!cfg) {
      setSyncStatus('off');
      if (loud) setSyncStatus('error', 'Paste your token first.');
      return;
    }
    if (syncing) {
      syncQueued = true;
      return;
    }
    syncing = true;
    setSyncStatus('busy');
    try {
      await assertPrivateRepo(cfg.repo, cfg.token);
      for (let attempt = 0; ; attempt++) {
        const remoteFile = await getFile(cfg, 'data.json');
        const remote = remoteFile.text ? JSON.parse(remoteFile.text) : null;
        const merged = withDefaults(L.mergeStates(state, remote));

        if (L.stableStringify(merged) !== L.stableStringify(state)) {
          state = merged;
          saveState(null, { replaced: true, noSync: true });
        }
        if (remote && L.stableStringify(merged) === L.stableStringify(remote)) break;

        try {
          await putFile(cfg, 'data.json', JSON.stringify(merged, null, 2) + '\n', remoteFile.sha, 'Sync from web app');
        } catch (err) {
          // Another device pushed between our read and write: re-read and merge again.
          if ((err.status === 409 || err.status === 422) && attempt < 2) continue;
          throw err;
        }
        try {
          const log = await getFile(cfg, 'WORKOUT_LOG.md');
          await putFile(cfg, 'WORKOUT_LOG.md', generateMarkdownExport() + '\n', log.sha, 'Sync WORKOUT_LOG.md from web app');
        } catch (e) {
          console.warn('WORKOUT_LOG.md not updated:', e);
        }
        break;
      }
      setSyncStatus('ok');
      if (loud) showToast('SYNCED');
    } catch (err) {
      setSyncStatus('error', err.message);
      showToast('SYNC FAILED: see 6:sync');
    } finally {
      syncing = false;
      if (syncQueued) {
        syncQueued = false;
        scheduleSync(500);
      }
    }
  }

  document.getElementById('gh-sync-form').addEventListener('submit', e => {
    e.preventDefault();
    storeToken();
    syncNow({ loud: true });
  });

  document.getElementById('gh-remember').addEventListener('change', () => {
    storeToken();
    if (document.getElementById('gh-remember').checked) syncNow({ loud: true });
  });

  document.getElementById('btn-gh-forget').addEventListener('click', () => {
    forgetToken();
    showToast('TOKEN REMOVED FROM THIS DEVICE');
  });

  document.getElementById('btn-gh-pull').addEventListener('click', async () => {
    if (!confirm('Replace ALL data in this browser with the GitHub copy? Unsynced local changes will be lost.')) return;
    storeToken();
    const cfg = getSyncConfig();
    if (!cfg) return setSyncStatus('error', 'Paste your token first.');
    try {
      await assertPrivateRepo(cfg.repo, cfg.token);
      const remote = await getFile(cfg, 'data.json');
      if (!remote.text) throw new Error('No data.json in the repo yet.');
      state = withDefaults(JSON.parse(remote.text));
      saveState('REPLACED WITH GITHUB COPY', { replaced: true, noSync: true });
      setSyncStatus('ok');
    } catch (err) {
      setSyncStatus('error', 'Replace failed: ' + err.message);
    }
  });

  // A tab left open across a deploy must not keep running old code (old builds
  // could overwrite synced data). Compare our build id with the live one and reload.
  const APP_VERSION = (document.querySelector('meta[name="app-version"]') || {}).content || 'dev';
  async function reloadIfStale() {
    if (APP_VERSION === 'dev' || !/^https?:$/.test(location.protocol)) return false;
    try {
      const res = await fetch(location.pathname + '?v=' + Date.now(), { cache: 'no-store' });
      const live = (await res.text()).match(/name="app-version" content="([^"]+)"/);
      if (live && live[1] !== APP_VERSION) {
        location.reload();
        return true;
      }
    } catch (e) {}
    return false;
  }

  // Pick up changes from other devices when returning to the tab/app.
  document.addEventListener('visibilitychange', async () => {
    if (document.visibilityState !== 'visible') return;
    if (await reloadIfStale()) return;
    scheduleSync(0);
  });

  // Keyboard shortcuts (1-6 tabs, t theme, space timer) when not in input/textarea
  document.addEventListener('keydown', e => {
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.metaKey || e.ctrlKey || e.altKey) return;
    const tabMap = { '1': 'status', '2': 'log', '3': 'program', '4': 'form', '5': 'metrics', '6': 'sync' };
    if (tabMap[e.key]) {
      e.preventDefault();
      switchTab(tabMap[e.key]);
    } else if (e.key === 't' || e.key === 'T') {
      e.preventDefault();
      document.getElementById('theme-toggle').click();
    } else if (e.key === ' ') {
      e.preventDefault();
      toggleTimer();
    }
  });

  // Initialize default dates and render
  const todayIso = new Date().toISOString().slice(0, 10);
  document.getElementById('rr-date').value = todayIso;
  document.getElementById('wt-date').value = todayIso;
  document.getElementById('run-date').value = todayIso;
  // Tokens used to persist in localStorage; keep them for this tab only now.
  try { localStorage.removeItem(GH_TOKEN_KEY); } catch (e) {}
  applyColorSchemeMeta();
  prefillNextTargetIntoForm();
  renderAll();
  seedFromLocalDataJson();
  if (getSyncConfig()) syncNow();
  else setSyncStatus('off');
})();
