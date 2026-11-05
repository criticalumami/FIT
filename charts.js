/*
 * FIT // charts tab (7:charts). Plain inline SVG, zero dependencies, monochrome.
 * app.js calls FITCharts.render(state) whenever state changes; charts redraw at
 * their real pixel width (ResizeObserver), so text stays legible on phones.
 */
(function () {
  'use strict';

  const L = window.FITLib;
  const PROGRAM = window.FIT_PROGRAM;
  const esc = L.escapeHtml;
  const NS = 'http://www.w3.org/2000/svg';

  let state = null;
  const hoverData = {}; // chart id -> { pts: [{x, y, tip}], top, bottom }

  // ---------- small utils ----------
  const fmtPace = m => {
    let mm = Math.floor(m), ss = Math.round((m - mm) * 60);
    if (ss === 60) { mm += 1; ss = 0; }
    return `${mm}:${String(ss).padStart(2, '0')}`;
  };
  const md = iso => iso.slice(5);
  const todayIso = () => new Date().toISOString().slice(0, 10);

  function niceTicks(min, max, count = 4) {
    if (min === max) { min -= 1; max += 1; }
    const raw = (max - min) / count;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(f => f * mag).find(s => s >= raw) || raw;
    const lo = Math.floor(min / step) * step, hi = Math.ceil(max / step) * step;
    const ticks = [];
    for (let v = lo; v <= hi + step / 1e6; v += step) ticks.push(+v.toFixed(6));
    return ticks;
  }

  function runKind(type) {
    const t = String(type || '');
    if (/long/i.test(t)) return 'long';
    if (/tempo|threshold|4\s*x\s*4|interval/i.test(t)) return 'tempo';
    return 'easy';
  }
  const RUN_KINDS = [
    { id: 'easy', label: 'easy', marker: 'circle', dash: '' },
    { id: 'long', label: 'long', marker: 'diamond', dash: '6,3' },
    { id: 'tempo', label: 'tempo / 4x4', marker: 'square', dash: '1.5,3' }
  ];

  function marker(shape, x, y, r = 4.5) {
    const ring = 'stroke="var(--bg-alt)" stroke-width="2" paint-order="stroke"';
    if (shape === 'square') return `<rect x="${x - r + 0.5}" y="${y - r + 0.5}" width="${2 * r - 1}" height="${2 * r - 1}" fill="currentColor" ${ring}/>`;
    if (shape === 'diamond') return `<path d="M${x} ${y - r - 1}L${x + r + 1} ${y}L${x} ${y + r + 1}L${x - r - 1} ${y}Z" fill="currentColor" ${ring}/>`;
    if (shape === 'hollow') return `<circle cx="${x}" cy="${y}" r="${r - 1}" fill="var(--bg-alt)" stroke="currentColor" stroke-width="1.5"/>`;
    if (shape === 'dot') return `<circle cx="${x}" cy="${y}" r="2.5" fill="var(--fg-dim)"/>`;
    return `<circle cx="${x}" cy="${y}" r="${r}" fill="currentColor" ${ring}/>`;
  }

  function legend(items) {
    return `<div class="chart-legend">${items.map(i => `
      <span><svg width="${i.line ? 26 : 12}" height="12" aria-hidden="true">
        ${i.line ? `<line x1="1" y1="6" x2="25" y2="6" stroke="${i.color || 'currentColor'}" stroke-width="2" stroke-dasharray="${i.dash || ''}"/>` : ''}
        ${i.marker ? marker(i.marker, i.line ? 13 : 6, 6, 4) : ''}
      </svg>${esc(i.label)}</span>`).join('')}</div>`;
  }

  /*
   * Time-axis chart. opts:
   *  id, width, height, x0, x1 (ISO dates), yMin, yMax, invert, yFmt,
   *  refs: [{ y, label, strong }], vlines: [{ date, label }], band: { y0, y1, label },
   *  series: [{ pts: [{ date, y, tip, marker }], line, dash, width, color, markers }]
   */
  function timeChart(o) {
    const W = Math.max(260, Math.round(o.width)), H = o.height || 190;
    const padL = 44, padR = 14, padT = 12, padB = 24;
    const pw = W - padL - padR, ph = H - padT - padB;
    const d0 = L.isoToDay(o.x0), d1 = Math.max(d0 + 1, L.isoToDay(o.x1));
    const xOf = iso => padL + ((L.isoToDay(iso) - d0) / (d1 - d0)) * pw;
    const ticks = niceTicks(o.yMin, o.yMax, H < 160 ? 3 : 4);
    const lo = ticks[0], hi = ticks[ticks.length - 1];
    const yOf = v => o.invert ? padT + ((v - lo) / (hi - lo)) * ph : padT + ph - ((v - lo) / (hi - lo)) * ph;
    const yFmt = o.yFmt || (v => String(v));

    // x ticks: pick a day step that leaves >= 64px per label
    const steps = [1, 2, 3, 7, 14, 28, 56, 91, 182];
    const step = steps.find(s => (s / (d1 - d0)) * pw >= 64) || 365;
    const xt = [];
    for (let d = Math.ceil(d0 / step) * step; d <= d1; d += step) xt.push(d);

    let svg = '';
    if (o.band) {
      const a = yOf(Math.max(lo, Math.min(hi, o.band.y0))), b = yOf(Math.max(lo, Math.min(hi, o.band.y1)));
      svg += `<rect x="${padL}" y="${Math.min(a, b)}" width="${pw}" height="${Math.abs(a - b)}" fill="var(--bg-hover)"/>`;
      if (o.band.label) svg += `<text x="${padL + 4}" y="${Math.max(a, b) - 4}" class="ch-ax">${esc(o.band.label)}</text>`;
    }
    ticks.forEach(t => {
      const y = yOf(t);
      svg += `<line x1="${padL}" x2="${W - padR}" y1="${y}" y2="${y}" stroke="var(--border)" stroke-width="1"/>`;
      svg += `<text x="${padL - 6}" y="${y + 3.5}" text-anchor="end" class="ch-ax">${esc(yFmt(t))}</text>`;
    });
    xt.forEach(d => {
      const x = padL + ((d - d0) / (d1 - d0)) * pw;
      svg += `<line x1="${x}" x2="${x}" y1="${padT + ph}" y2="${padT + ph + 4}" stroke="var(--border-strong)"/>`;
      svg += `<text x="${x}" y="${H - 6}" text-anchor="middle" class="ch-ax">${md(L.dayToIso(d))}</text>`;
    });
    svg += `<line x1="${padL}" x2="${W - padR}" y1="${padT + ph}" y2="${padT + ph}" stroke="var(--border-strong)"/>`;

    (o.vlines || []).forEach(v => {
      const x = xOf(v.date);
      svg += `<line x1="${x}" x2="${x}" y1="${padT}" y2="${padT + ph}" stroke="var(--fg-dim)" stroke-dasharray="2,3"/>`;
      if (v.label) svg += `<text x="${x + 3}" y="${padT + 9}" class="ch-ax ch-strong">${esc(v.label)}</text>`;
    });
    (o.refs || []).forEach(r => {
      if (r.y < lo || r.y > hi) return;
      const y = yOf(r.y);
      svg += `<line x1="${padL}" x2="${W - padR}" y1="${y}" y2="${y}" stroke="${r.strong ? 'currentColor' : 'var(--fg-dim)'}" stroke-width="${r.strong ? 1.5 : 1}" stroke-dasharray="5,4"/>`;
      svg += `<text x="${padL + 4}" y="${y - 4}" class="ch-ax${r.strong ? ' ch-strong' : ''}">${esc(r.label)}</text>`;
    });

    const hov = [];
    o.series.forEach(s => {
      const pts = s.pts.filter(p => p.y != null && !isNaN(p.y));
      if (s.line !== false && pts.length > 1) {
        svg += `<polyline fill="none" stroke="${s.color || 'currentColor'}" stroke-width="${s.width || 2}" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="${s.dash || ''}" points="${pts.map(p => `${xOf(p.date).toFixed(1)},${yOf(p.y).toFixed(1)}`).join(' ')}"/>`;
      }
      pts.forEach(p => {
        const x = xOf(p.date), y = yOf(p.y);
        if (s.markers !== false) svg += marker(p.marker || s.marker || 'circle', +x.toFixed(1), +y.toFixed(1));
        if (p.label) svg += `<text x="${x}" y="${y - 9}" text-anchor="middle" class="ch-val">${esc(p.label)}</text>`;
        if (p.tip) hov.push({ x, y, tip: p.tip });
      });
    });

    hoverData[o.id] = { pts: hov, top: padT, bottom: padT + ph };
    return `<svg class="chart-svg" data-chart="${o.id}" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.aria || '')}">${svg}
      <line class="ch-cross" x1="0" x2="0" y1="${padT}" y2="${padT + ph}" stroke="var(--fg-muted)" stroke-width="1" visibility="hidden"/></svg>`;
  }

  // ---------- individual charts ----------
  function weightChart(width) {
    const w = (state.weightLog || []).filter(x => x && x.date && !isNaN(Number(x.kg)))
      .map(x => ({ date: x.date, kg: Number(x.kg) })).sort((a, b) => a.date.localeCompare(b.date));
    if (!w.length) return { meta: '', html: '<p class="muted">No weigh-ins yet.</p>' };
    const target = state.meta.targetWeight != null ? Number(state.meta.targetWeight) : null;
    const trend = L.weightTrend(state.weightLog, 28, state.meta.maxLossPctPerWeek || 1.0);
    const eta = L.goalEta(trend, target);
    const last = w[w.length - 1];

    // Projection: to the goal if the trend heads there, else 4 weeks out on the current slope.
    let proj = null;
    if (trend && trend.ratePerWeek != null) {
      proj = eta && target != null
        ? { date: eta, y: target }
        : { date: L.dayToIso(L.isoToDay(trend.latestDate) + 28), y: trend.avg7 + trend.ratePerWeek * 4 };
    }
    const x1 = proj ? proj.date : last.date;
    const ys = w.map(x => x.kg).concat(target != null ? [target] : [], proj ? [proj.y] : []);
    const series = [{
      pts: w.map(x => ({ date: x.date, y: x.kg, tip: `${x.date}<br><b>${x.kg.toFixed(1)} kg</b>` })),
      width: 2
    }];
    if (proj) {
      series.push({
        pts: [
          { date: trend.latestDate, y: trend.avg7 },
          { date: proj.date, y: proj.y, marker: 'hollow', tip: `${eta ? 'Goal ETA' : '4-week projection'} ${proj.date}<br><b>${proj.y.toFixed(1)} kg</b> at ${trend.ratePerWeek.toFixed(2)} kg/wk` }
        ],
        dash: '4,4', width: 1.5, color: 'var(--fg-muted)', markers: true
      });
      series[1].pts[0].marker = 'dot';
    }
    const html = timeChart({
      id: 'weight', width, height: 210, x0: w[0].date, x1,
      yMin: Math.min(...ys) - 0.5, yMax: Math.max(...ys) + 0.5,
      yFmt: v => `${v}`, aria: 'Bodyweight over time with goal line and projection',
      refs: target != null ? [{ y: target, label: `goal ${target.toFixed(1)} kg`, strong: true }] : [],
      series
    }) + legend([
      { label: 'weigh-in (kg)', line: true, marker: 'circle' },
      ...(proj ? [{ label: eta ? 'trend to goal' : 'trend, 4 wk', line: true, dash: '4,4', color: 'var(--fg-muted)', marker: 'hollow' }] : []),
      ...(target != null ? [{ label: 'goal', line: true, dash: '5,4' }] : [])
    ]);
    const togo = target != null ? `${(last.kg - target).toFixed(1)} kg to go` : '';
    const meta = [`${last.kg.toFixed(1)} kg`, togo, eta ? `ETA ${eta}` : (trend && trend.ratePerWeek != null ? `${trend.ratePerWeek.toFixed(2)} kg/wk` : '')]
      .filter(Boolean).join(' | ');
    return { meta, html };
  }

  function weeklyVolumeChart(width) {
    const weeks = L.weeklyKm(state.runLog);
    if (!weeks.length) return { meta: '', html: '<p class="muted">No runs yet.</p>' };
    const W = Math.max(260, Math.round(width)), H = 190;
    const padL = 44, padR = 14, padT = 16, padB = 24;
    const pw = W - padL - padR, ph = H - padT - padB;
    const ticks = niceTicks(0, Math.max(...weeks.map(x => x.km)) * 1.08, 4);
    const hi = ticks[ticks.length - 1];
    const yOf = v => padT + ph - (v / hi) * ph;
    const band = pw / weeks.length;
    const bw = Math.max(6, Math.min(48, band - 6));
    const today = L.isoToDay(todayIso());
    const labelEvery = Math.ceil(52 / band);
    let svg = '';
    ticks.forEach(t => {
      svg += `<line x1="${padL}" x2="${W - padR}" y1="${yOf(t)}" y2="${yOf(t)}" stroke="var(--border)"/>`;
      svg += `<text x="${padL - 6}" y="${yOf(t) + 3.5}" text-anchor="end" class="ch-ax">${t}</text>`;
    });
    const hov = [];
    weeks.forEach((wk, i) => {
      const cx = padL + band * i + band / 2;
      const y = yOf(wk.km), h = padT + ph - y;
      const live = today - L.isoToDay(wk.weekStart) < 7;
      if (h > 0) {
        const r = Math.min(4, bw / 2, h);
        // rounded top, square base
        svg += `<path d="M${cx - bw / 2} ${padT + ph}V${y + r}Q${cx - bw / 2} ${y} ${cx - bw / 2 + r} ${y}H${cx + bw / 2 - r}Q${cx + bw / 2} ${y} ${cx + bw / 2} ${y + r}V${padT + ph}Z"
          fill="${live ? 'var(--bg-hover)' : 'currentColor'}" stroke="${live ? 'currentColor' : 'none'}" stroke-dasharray="${live ? '3,2' : ''}"/>`;
      }
      const isLast = i === weeks.length - 1;
      if (wk.jump || isLast) {
        svg += `<text x="${cx}" y="${y - 5}" text-anchor="middle" class="ch-val">${wk.km.toFixed(1)}${wk.jump && !live ? ' !' : ''}</text>`;
      }
      if (i % labelEvery === 0) svg += `<text x="${cx}" y="${H - 6}" text-anchor="middle" class="ch-ax">${md(wk.weekStart)}</text>`;
      const change = wk.change == null ? '' : `<br>${wk.change > 0 ? '+' : ''}${Math.round(wk.change * 100)}% vs prev${wk.jump && !live ? ' (over +10%)' : ''}`;
      hov.push({ x: cx, y, tip: `Week of ${wk.weekStart}${live ? ' (in progress)' : ''}<br><b>${wk.km.toFixed(1)} km</b>${change}` });
    });
    svg += `<line x1="${padL}" x2="${W - padR}" y1="${padT + ph}" y2="${padT + ph}" stroke="var(--border-strong)"/>`;
    hoverData.weekly = { pts: hov, top: padT, bottom: padT + ph, bars: true };
    const html = `<svg class="chart-svg" data-chart="weekly" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Weekly running kilometres">${svg}
      <line class="ch-cross" x1="0" x2="0" y1="${padT}" y2="${padT + ph}" stroke="var(--fg-muted)" visibility="hidden"/></svg>`
      + `<p class="hint">Weeks run Mon-Sun. "!" marks a week more than 10% over the one before; the outlined bar is the current week.</p>`;
    const done = weeks.filter(wk => today - L.isoToDay(wk.weekStart) >= 7).slice(-4);
    const avg4 = done.length ? done.reduce((a, x) => a + x.km, 0) / done.length : null;
    return { meta: avg4 != null ? `4-wk avg ${avg4.toFixed(1)} km/wk` : '', html };
  }

  function runSeriesByKind(runs, valueFn, tipFn) {
    return RUN_KINDS.map(k => ({
      pts: runs.filter(r => runKind(r.type) === k.id && valueFn(r) != null)
        .map(r => ({ date: r.date, y: valueFn(r), tip: tipFn(r) })),
      marker: k.marker, dash: k.dash, width: 1.5
    })).filter(s => s.pts.length);
  }
  const runLegend = runs => legend(RUN_KINDS.filter(k => runs.some(r => runKind(r.type) === k.id))
    .map(k => ({ label: k.label, line: true, dash: k.dash, marker: k.marker })));
  const runTip = r => `${r.date} | ${esc(r.type)}<br><b>${r.km.toFixed(2)} km</b> in ${r.min.toFixed(1)} min<br>${fmtPace(r.paceMin)}/km${r.hr ? ` | ${r.hr} bpm` : ''}`;

  function paceChart(width) {
    const runs = L.runSeries(state.runLog);
    if (!runs.length) return { meta: '', html: '<p class="muted">No runs yet.</p>' };
    const paces = runs.map(r => r.paceMin);
    const html = timeChart({
      id: 'pace', width, height: 200, x0: runs[0].date, x1: runs[runs.length - 1].date,
      yMin: Math.min(...paces) - 0.1, yMax: Math.max(...paces) + 0.1, invert: true,
      yFmt: fmtPace, aria: 'Pace per run in minutes per kilometre, faster is higher',
      series: runSeriesByKind(runs, r => r.paceMin, runTip)
    }) + runLegend(runs) + '<p class="hint">min/km, faster is higher.</p>';
    const easy = runs.filter(r => runKind(r.type) === 'easy');
    const e = easy[easy.length - 1];
    return { meta: e ? `last easy ${fmtPace(e.paceMin)}/km` : '', html };
  }

  function hrChart(width) {
    const runs = L.runSeries(state.runLog).filter(r => r.hr);
    if (!runs.length) return { meta: '', html: '<p class="muted">No runs with heart rate yet.</p>' };
    const hrs = runs.map(r => Number(r.hr));
    const caps = L.RUN_HR_RULES.map(r => r.cap);
    const html = timeChart({
      id: 'hr', width, height: 200, x0: runs[0].date, x1: runs[runs.length - 1].date,
      yMin: Math.min(...hrs, ...caps) - 3, yMax: Math.max(...hrs, ...caps) + 3,
      aria: 'Average heart rate per run with easy and long run caps',
      refs: L.RUN_HR_RULES.map((r, i) => ({ y: r.cap, label: `${r.label} cap ${r.cap}`, strong: i === 0 })),
      series: runSeriesByKind(runs, r => Number(r.hr), runTip)
    }) + runLegend(runs);
    const over = runs.filter(r => L.runHrFlag(r)).length;
    return { meta: `${over} of ${runs.length} over cap`, html };
  }

  function vo2Chart(width) {
    const byDate = new Map();
    (state.runLog || []).forEach(r => { if (r && r.date && r.vo2) byDate.set(r.date, { v: Number(r.vo2), src: 'run' }); });
    (state.dailyLog || []).forEach(d => { if (d && d.date && d.vo2) byDate.set(d.date, { v: Number(d.vo2), src: 'Health' }); });
    const pts = [...byDate.entries()].sort((a, b) => a[0].localeCompare(b[0]))
      .map(([date, x]) => ({ date, y: x.v, tip: `${date}<br><b>${x.v.toFixed(1)}</b> mL/kg/min (${x.src})` }));
    if (!pts.length) return { meta: '', html: '<p class="muted">No VO2max readings yet.</p>' };
    const ys = pts.map(p => p.y);
    const html = timeChart({
      id: 'vo2', width, height: 170, x0: pts[0].date, x1: pts[pts.length - 1].date,
      yMin: Math.min(...ys) - 0.5, yMax: Math.max(...ys) + 0.5, aria: 'VO2max estimate over time',
      series: [{ pts, width: 2, marker: pts.length > 30 ? 'dot' : 'circle' }]
    });
    return { meta: `latest ${ys[ys.length - 1].toFixed(1)}`, html };
  }

  function rhrChart(width) {
    const m = L.rollingMean(state.dailyLog, 'restingHr', 7);
    if (!m.length) return { meta: '', html: '<p class="muted">No resting HR from Apple Health yet.</p>' };
    const ys = m.map(p => p.value);
    const html = timeChart({
      id: 'rhr', width, height: 170, x0: m[0].date, x1: m[m.length - 1].date,
      yMin: Math.min(...ys) - 1, yMax: Math.max(...ys) + 1, aria: 'Resting heart rate, daily and 7-day average',
      series: [
        { pts: m.map(p => ({ date: p.date, y: p.value, marker: 'dot' })), line: false },
        { pts: m.map(p => ({ date: p.date, y: Math.round(p.mean * 10) / 10, tip: `${p.date}<br>${p.value} bpm<br><b>7-day avg ${p.mean.toFixed(1)}</b>` })), width: 2, markers: false }
      ]
    }) + legend([{ label: 'daily', marker: 'dot' }, { label: '7-day avg', line: true }]);
    return { meta: `7-day avg ${m[m.length - 1].mean.toFixed(1)} bpm`, html };
  }

  // ---------- RR small multiples ----------
  const RR_STRENGTH = ['pull', 'squat', 'dip', 'hinge', 'row', 'push'];
  const RR_CORE = [
    { field: 'antiext', id: 'core_antiext' },
    { field: 'antirot', id: 'core_antirot' },
    { field: 'ext', id: 'core_ext' }
  ];
  const exById = id => (PROGRAM.exercises || []).find(e => e.id === id) || {};

  function rrMultiples(width) {
    const sessions = (state.rrSessions || []).filter(s => s && s.date);
    if (!sessions.length) return '<p class="muted">No RR sessions logged yet.</p>';
    const dates = sessions.map(s => s.date).sort();
    const x0 = dates[0], x1 = dates[dates.length - 1];
    const cols = width >= 900 ? 3 : width >= 560 ? 2 : 1;
    const cw = (width - (cols - 1) * 12) / cols;

    const cells = RR_STRENGTH.map(slot => {
      const ex = exById(slot);
      const s = L.rrSlotSeries(sessions, slot);
      if (!s.length) return '';
      const min = ex.minRep || 5, max = ex.maxRep || 8;
      const last = s[s.length - 1];
      const ys = s.map(p => p.total).concat([3 * min, 3 * max]);
      const chart = timeChart({
        id: 'rr-' + slot, width: cw, height: 150, x0, x1,
        yMin: Math.min(...ys) - 1, yMax: Math.max(...ys) + 1,
        band: { y0: 3 * min, y1: 3 * max, label: `${min}-${max} x3` },
        vlines: s.filter(p => p.levelChange).map(p => ({ date: p.date, label: p.level ? `L${p.level}` : 'new step' })),
        aria: `${slot} total reps per session`,
        series: [{ pts: s.map(p => ({ date: p.date, y: p.total, tip: `${p.date}<br><b>${esc(p.sets)}</b> = ${p.total} reps<br>${esc(p.prog)}` })), width: 2 }]
      });
      return `<div class="rr-cell">
        <div class="rr-cell-head"><strong>${esc(slot)}</strong><span class="muted">${esc(last.sets)} | ${last.total} reps</span></div>
        <div class="rr-cell-prog muted">${esc(last.prog || ex.slot || '')}</div>${chart}</div>`;
    });

    RR_CORE.forEach(c => {
      const s = L.rrHoldSeries(sessions, c.field);
      if (s.length < 2) return;
      const last = s[s.length - 1];
      const ys = s.map(p => p.seconds);
      cells.push(`<div class="rr-cell">
        <div class="rr-cell-head"><strong>${esc(c.id.replace('core_', 'core '))}</strong><span class="muted">${last.seconds}s total</span></div>
        <div class="rr-cell-prog muted">${esc(exById(c.id).slot || '')}, total hold time</div>
        ${timeChart({
          id: 'rr-' + c.id, width: cw, height: 150, x0, x1,
          yMin: Math.max(0, Math.min(...ys) - 10), yMax: Math.max(...ys) + 10, yFmt: v => `${v}s`,
          aria: `${c.id} total hold seconds per session`,
          series: [{ pts: s.map(p => ({ date: p.date, y: p.seconds, tip: `${p.date}<br><b>${esc(p.text)}</b> = ${p.seconds}s` })), width: 2 }]
        })}</div>`);
    });
    return `<div class="rr-grid" style="grid-template-columns:repeat(${cols}, minmax(0, 1fr))">${cells.join('')}</div>
      <p class="hint">Total reps across the 3 sets. The shaded band is the target range; reaching its top on every set means level up. Dashed verticals mark a step change.</p>`;
  }

  // ---------- render ----------
  const TILES = [
    { id: 'weight', fn: weightChart },
    { id: 'weekly', fn: weeklyVolumeChart },
    { id: 'pace', fn: paceChart },
    { id: 'hr', fn: hrChart },
    { id: 'vo2', fn: vo2Chart },
    { id: 'rhr', fn: rhrChart }
  ];

  function draw() {
    const root = document.getElementById('view-charts');
    if (!root || !state || !root.offsetParent) return; // hidden tab: redraw when shown
    TILES.forEach(t => {
      const body = document.getElementById('ch-' + t.id);
      if (!body) return;
      const r = t.fn(body.clientWidth);
      body.innerHTML = r.html;
      const meta = document.getElementById('ch-' + t.id + '-meta');
      if (meta) meta.textContent = r.meta;
    });
    const rr = document.getElementById('ch-rr');
    if (rr) rr.innerHTML = rrMultiples(rr.clientWidth);
  }

  // ---------- hover tooltip (mouse + touch) ----------
  let tipEl = null;
  function onMove(e) {
    const svg = e.target.closest && e.target.closest('svg.chart-svg');
    if (!svg) return hide();
    const data = hoverData[svg.dataset.chart];
    if (!data || !data.pts.length) return hide();
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    let best = null;
    data.pts.forEach(p => { if (!best || Math.abs(p.x - x) < Math.abs(best.x - x)) best = p; });
    if (!best || Math.abs(best.x - x) > 40) return hide();
    document.querySelectorAll('.ch-cross').forEach(c => c.setAttribute('visibility', 'hidden'));
    const cross = svg.querySelector('.ch-cross');
    if (cross && !data.bars) { cross.setAttribute('x1', best.x); cross.setAttribute('x2', best.x); cross.setAttribute('visibility', 'visible'); }
    if (!tipEl) { tipEl = document.createElement('div'); tipEl.className = 'chart-tip'; document.body.appendChild(tipEl); }
    tipEl.innerHTML = best.tip;
    tipEl.hidden = false;
    const tw = tipEl.offsetWidth, th = tipEl.offsetHeight;
    let left = rect.left + best.x + 12;
    if (left + tw > window.innerWidth - 8) left = rect.left + best.x - tw - 12;
    let top = rect.top + best.y - th - 10;
    if (top < 8) top = rect.top + best.y + 14;
    tipEl.style.left = Math.max(8, left) + 'px';
    tipEl.style.top = top + 'px';
  }
  function hide() {
    if (tipEl) tipEl.hidden = true;
    document.querySelectorAll('.ch-cross').forEach(c => c.setAttribute('visibility', 'hidden'));
  }

  function init() {
    const root = document.getElementById('view-charts');
    if (!root) return;
    root.addEventListener('pointermove', onMove);
    root.addEventListener('pointerdown', onMove);
    root.addEventListener('pointerleave', hide);
    window.addEventListener('scroll', hide, { passive: true });
    let lastW = 0, raf = 0;
    const ro = new ResizeObserver(entries => {
      const w = Math.round(entries[0].contentRect.width);
      if (w === lastW) return;
      lastW = w; // 0 while the tab is hidden, so showing it again always redraws
      if (!w) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    });
    ro.observe(root);
  }

  window.FITCharts = {
    render(s) {
      state = s;
      draw();
    }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
