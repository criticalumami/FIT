// Run: node --test tests/
const test = require('node:test');
const assert = require('node:assert/strict');
const L = require('../lib.js');

test('computeNextSets adds a rep to the weakest (earliest) set', () => {
  assert.deepEqual(L.computeNextSets('5,5,5', 5, 8), { sets: '6,5,5', action: 'progress' });
  assert.deepEqual(L.computeNextSets('6,5,5', 5, 8), { sets: '6,6,5', action: 'progress' });
  assert.deepEqual(L.computeNextSets('6,6,5', 5, 8), { sets: '6,6,6', action: 'progress' });
});

test('computeNextSets keeps suffixes like (/leg)', () => {
  assert.equal(L.computeNextSets('7,7,7 (/leg)', 5, 8).sets, '8,7,7 (/leg)');
});

test('computeNextSets levels up at max reps and restarts at min', () => {
  assert.deepEqual(L.computeNextSets('8,8,8 (/leg)', 5, 8), { sets: '5,5,5 (/leg)', action: 'level_up' });
  assert.equal(L.computeNextSets('9,9,9', 5, 8).action, 'level_up');
  assert.equal(L.computeNextSets('9,9,9', 8, 12).action, 'progress');
});

test('computeNextSets flags sets below the minimum', () => {
  assert.deepEqual(L.computeNextSets('4,4,4', 5, 8), { sets: '5,4,4', action: 'regress' });
});

test('computeNextSets handles empty and unparseable input', () => {
  assert.deepEqual(L.computeNextSets('', 5, 8), { sets: '5,5,5', action: 'start' });
  assert.equal(L.computeNextSets('2x30s', 5, 8).action, 'unknown');
});

test('sumReps sums the first three numbers', () => {
  assert.equal(L.sumReps('8,8,8 (/leg)'), 24);
  assert.equal(L.sumReps(''), 0);
});

test('parseShorthand reads every exercise and does not confuse plank with side plank', () => {
  const p = L.parseShorthand('pullu 4 4 4 step 8 8 8 floorslide 9 9 9 dips 5 5 5 inverted rows 7 7 7 diamond p 4 4 4 side plank 15sx2 plank 30sx2 arch 2x8');
  assert.equal(p.pull_sets, '4,4,4');
  assert.equal(p.squat_sets, '8,8,8 (/leg)');
  assert.equal(p.hinge_sets, '9,9,9');
  assert.equal(p.dip_sets, '5,5,5');
  assert.equal(p.row_sets, '7,7,7');
  assert.equal(p.push_sets, '4,4,4');
  assert.equal(p.antiext, 'Plank 30sx2');
  assert.equal(p.antirot, 'Side Plank 15sx2');
  assert.equal(p.ext, 'Arch/RevHyper 2x8');
  assert.equal(L.parseShorthand('   '), null);
});

test('escapeHtml neutralises markup', () => {
  assert.equal(L.escapeHtml('<img src=x onerror="a">&\''), '&lt;img src=x onerror=&quot;a&quot;&gt;&amp;&#39;');
  assert.equal(L.escapeHtml(null), '');
});

test('weightTrend: 7-day average and weekly rate', () => {
  const log = [
    { date: '2026-10-01', kg: 82 },
    { date: '2026-10-08', kg: 81 },
    { date: '2026-10-15', kg: 80 },
    { date: '2026-10-20', kg: 79.6 },
    { date: '2026-10-21', kg: 79.4 }
  ];
  const t = L.weightTrend(log);
  assert.equal(t.latest, 79.4);
  assert.equal(t.entries7, 3); // 15th, 20th, 21st
  assert.ok(Math.abs(t.avg7 - (80 + 79.6 + 79.4) / 3) < 1e-9);
  assert.ok(t.ratePerWeek < -0.8 && t.ratePerWeek > -1.2, `rate ${t.ratePerWeek}`);
  assert.ok(t.ratePctBw > 1.0 && t.tooFast);
});

test('weightTrend: slow loss is not flagged; empty and single entries are safe', () => {
  const t = L.weightTrend([{ date: '2026-10-01', kg: 80 }, { date: '2026-10-15', kg: 79.4 }]);
  assert.ok(Math.abs(t.ratePerWeek + 0.3) < 1e-9);
  assert.equal(t.tooFast, false);
  assert.equal(L.weightTrend([]), null);
  assert.equal(L.weightTrend([{ date: '2026-10-01', kg: 80 }]).ratePerWeek, null);
});

test('runHrFlag uses the cap for the session type', () => {
  assert.deepEqual(L.runHrFlag({ type: 'Easy Aerobic Run', hr: 154 }), { label: 'easy', cap: 148, over: 6 });
  assert.equal(L.runHrFlag({ type: 'Easy Run (Zone 2)', hr: 142 }), null);
  assert.equal(L.runHrFlag({ type: 'Long Aerobic Run (10K)', hr: 152 }), null);
  assert.equal(L.runHrFlag({ type: 'Long Aerobic Run (10K)', hr: 156 }).over, 1);
  assert.equal(L.runHrFlag({ type: 'Tempo / Threshold Run', hr: 169 }), null);
  assert.equal(L.runHrFlag({ type: 'Easy', hr: null }), null);
});

test('weeklyKm groups Monday-Sunday, fills gaps and flags >10% jumps', () => {
  const weeks = L.weeklyKm([
    { date: '2026-10-05', km: 10 }, // Mon
    { date: '2026-10-11', km: 10 }, // Sun same week
    { date: '2026-10-14', km: 21 }, // next week: +5%
    { date: '2026-10-28', km: 30 } // two weeks later, gap week in between
  ]);
  assert.deepEqual(weeks.map(w => [w.weekStart, w.km]), [
    ['2026-10-05', 20], ['2026-10-12', 21], ['2026-10-19', 0], ['2026-10-26', 30]
  ]);
  assert.equal(weeks[1].jump, false);
  assert.equal(weeks[2].jump, false);
  assert.equal(weeks[3].change, null); // previous week was 0
});

test('pace never prints :60', () => {
  assert.equal(L.pace(8.02, 66.1), '8:15');
  assert.equal(L.pace(1, 6.999), '7:00');
  assert.equal(L.pace(0, 10), '-');
});
