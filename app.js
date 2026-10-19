/*
 * FIT // suckless grayscale training & recomposition system
 * Vanilla JS, zero dependencies, localStorage + GitHub REST sync
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'fit_suckless_state_v2';
  const GH_TOKEN_KEY = 'fit_suckless_gh_token';

  // Complete 100% Bodyweight-Only Exercise Ladders & Form Guides
  const EXERCISE_DB = [
    {
      id: 'pull',
      slot: 'Pair 1A: Pull',
      category: 'pair1',
      targetRange: '3 x 5-8',
      ladders: [
        'L1: Scapular Pulls / Dead Hangs',
        'L2: Arch Hangs',
        'L3: Pull-Up Negatives (5-10s eccentric)',
        'L4: Chin-Ups / Pull-Ups',
        'L5: L-Sit Pull-Ups',
        'L6: Archer / Typewriter Pull-Ups'
      ],
      cues: [
        'Start from a full dead hang with arms straight.',
        'Depress scapulae (pull shoulders down away from ears) before bending elbows.',
        'Drive elbows down and back toward your ribs until chin clears the bar.',
        'Lower under strict control (1-2s eccentric) all the way to dead hang.'
      ],
      faults: 'Kipping knees, crane-necking chin over bar with rounded shoulders, cutting bottom 20% of dead hang.',
      defaultNote: 'Current: 4,4,4 strict pull-ups. Add +1 rep to Set 1 -> 5,4,4 next session.'
    },
    {
      id: 'squat',
      slot: 'Pair 1B: Squat',
      category: 'pair1',
      targetRange: '3 x 5-8 (/leg)',
      ladders: [
        'L1: Assisted Squat',
        'L2: Full Depth Bodyweight Squat',
        'L3: Single-Leg Sofa Step-Up (No Back-Leg Push)',
        'L4: Bulgarian Split Squat (Rear Foot on Sofa)',
        'L5: Beginner Shrimp Squat (Knee + Toes touch)',
        'L6: Intermediate/Advanced Shrimp or Pistol Squat'
      ],
      cues: [
        'For Single-Leg Sofa Step-Up: place top foot flat on sofa, lean torso slightly forward over working knee.',
        'Keep rear foot dorsiflexed (toes pulled up) so you cannot bounce off the back calf.',
        'Take a 3-second lowering phase down to the floor on each rep.',
        'Once 8,8,8 feels easy, switch to Bulgarian Split Squats or Beginner Shrimp Squats.'
      ],
      faults: 'Pushing off the floor with the back foot; knee caving inward (valgus); dropping down uncontrolled.',
      defaultNote: 'Day 1 hit 8,8,8 (/leg) on Single-Leg Sofa Step-Ups. Ready for strict 3s eccentric or Bulgarian Split Squat.'
    },
    {
      id: 'dip',
      slot: 'Pair 2A: Dip',
      category: 'pair2',
      targetRange: '3 x 5-8',
      ladders: [
        'L1: Parallel Bar Support Hold (60s)',
        'L2: Negative Dips (5-8s eccentric)',
        'L3: Parallel Bar Dips',
        'L4: L-Sit Dips / Pause Dips (2s bottom)',
        'L5: Ring Dips / Korean Dips'
      ],
      cues: [
        'Start in locked-out support with depressed shoulders (long neck).',
        'Lean torso slightly forward (~15-20 deg) and tuck elbows back (~45 deg maximum flare).',
        'Descend until upper arms are at least parallel to the floor (shoulder crease below elbow).',
        'Press up to full lockout and re-depress shoulders at the top.'
      ],
      faults: 'Shrugging shoulders into ears; flaring elbows out 90 deg; stopping above parallel.',
      defaultNote: 'Day 1 hit 5,5,5. Target 6,5,5 next session.'
    },
    {
      id: 'hinge',
      slot: 'Pair 2B: Hinge',
      category: 'pair2',
      targetRange: '3 x 8-12',
      ladders: [
        'L1: Romanian Deadlift (Bodyweight / Single-Leg Balance)',
        'L2: Glute Bridge Hold / Marching Bridge',
        'L3: Floor Slide Hamstring Curl (Both Legs)',
        'L4: Eccentric Single-Leg Floor Slide (2-up, 1-down)',
        'L5: Single-Leg Floor Slide Hamstring Curl',
        'L6: Nordic Hamstring Curl (Anchored under sofa)'
      ],
      cues: [
        'Lie supine with heels on sliders/towel/socks on smooth floor.',
        'Tuck pelvis slightly (posterior pelvic tilt) and squeeze glutes before sliding.',
        'Keep a straight line from knees through hips to shoulders throughout the slide.',
        'If 3x9-12 bilateral feels manageable, slide out on 1 leg (4s eccentric) and pull back with 2 legs.'
      ],
      faults: 'Letting hips sag toward the floor while sliding; overarching lower back instead of using hamstrings.',
      defaultNote: 'Day 1 hit 9,9,9 on Floor Slide Progression. Target 10,10,10 or 2-up/1-down eccentric next.'
    },
    {
      id: 'row',
      slot: 'Pair 3A: Row',
      category: 'pair3',
      targetRange: '3 x 8-12',
      ladders: [
        'L1: Incline Rows (45 deg body angle)',
        'L2: Horizontal Inverted Rows (Feet on floor)',
        'L3: Feet-Elevated Inverted Rows (Feet on sofa)',
        'L4: Wide-Grip / Tuck Front Lever Rows',
        'L5: Archer Rows / One-Arm Row Progression'
      ],
      cues: [
        'Maintain a rigid plank from ankles to shoulders (squeeze glutes and abs).',
        'Pull bar/rings to lower chest or upper abs while retracting shoulder blades together.',
        'Pause 1 second at the top of every rep to eliminate momentum.',
        'Keep wrists neutral (do not curl wrists at the top).'
      ],
      faults: 'Hips sagging or piking up to shorten the lever; head jutting forward to meet the bar.',
      defaultNote: 'Day 1 hit 7,7,7. Target 8,7,7 -> 8,8,8.'
    },
    {
      id: 'push',
      slot: 'Pair 3B: Push-Up',
      category: 'pair3',
      targetRange: '3 x 5-8',
      ladders: [
        'L1: Incline Push-Up (Hands on sofa)',
        'L2: Full Standard Push-Up (Hollow body)',
        'L3: Diamond Push-Up',
        'L4: Decline Diamond / Feet-Elevated Push-Up',
        'L5: Pseudo Planche Push-Up (PPPU - lean forward)',
        'L6: Archer Push-Up'
      ],
      cues: [
        'Form a diamond or narrow triangle with index fingers and thumbs under your sternum.',
        'Tuck pelvis (posterior pelvic tilt) and squeeze quads + glutes.',
        'Keep elbows tracking back at ~30-45 deg along your ribcage (never flare sideways).',
        'Touch chest to hands, then press to full lockout with scapular protraction at the top.'
      ],
      faults: 'Elbows flaring out into a T-shape; lower back sagging; stopping short of chest-to-hand contact.',
      defaultNote: 'Day 1 hit 4,4,4 on Diamond Push-Ups. Target 5,4,4 next session.'
    },
    {
      id: 'core_antiext',
      slot: 'Core 1: Anti-Extension',
      category: 'core',
      targetRange: '2 x 30-60s / 8-12',
      ladders: [
        'L1: Forearm Plank (Hollow Body / PPT) 30-60s',
        'L2: Long-Lever Plank (Elbows ahead of eyes)',
        'L3: Plank Towel/Socks Floor Slide Out',
        'L4: Standing Ab Walkouts'
      ],
      cues: [
        'Tuck tailbone under hard (posterior pelvic tilt) so lower back is flat, not arched.',
        'Protract shoulder blades (push floor away) and pull elbows metaphorically toward toes.',
        'Once 2x30s feels easy, walk elbows 5-10cm forward into a Long-Lever Plank.'
      ],
      faults: 'Passive resting on lumbar spine; looking up instead of neutral neck.',
      defaultNote: 'Current: 2x30s strict hollow plank (2 sets total to save energy during cut).'
    },
    {
      id: 'core_antirot',
      slot: 'Core 2: Anti-Rotation',
      category: 'core',
      targetRange: '2 x 15-45s/side',
      ladders: [
        'L1: Side Plank (Feet stacked) 15-45s/side',
        'L2: Side Plank with Top Leg Abduction',
        'L3: Copenhagen Plank (Top foot/knee on sofa)'
      ],
      cues: [
        'Place elbow directly beneath shoulder; stack hips and shoulders vertically.',
        'Drive bottom hip high off the floor and squeeze glutes so body forms a straight line.',
        'Copenhagen Plank (top leg on sofa) is a top-tier progression for runners (adductor + oblique armor).'
      ],
      faults: 'Top shoulder rolling forward; hips flexing backward into a V-shape.',
      defaultNote: 'Current: 2x15s/side. Build toward 2x30s/side.'
    },
    {
      id: 'core_ext',
      slot: 'Core 3: Extension',
      category: 'core',
      targetRange: '2 x 8-12',
      ladders: [
        'L1: Prone Arch Hold (Superman with straight arms/legs)',
        'L2: Prone Arch Raises (Dynamic 2s hold at top)',
        'L3: Sofa Reverse Hyperextensions (Hips on edge of sofa)'
      ],
      cues: [
        'For Sofa Reverse Hyper: lie prone on sofa with hip crease right at the edge, gripping sofa frame.',
        'Raise straight legs using glutes and spinal erectors until body is horizontal.',
        'Pause 1 second at the top; do not swing wildly above horizontal.'
      ],
      faults: 'Bending knees excessively; using momentum to hyperextend lumbar spine.',
      defaultNote: 'Current: 2x8 Arch / Reverse Hyper.'
    },
    {
      id: 'skill_hs',
      slot: 'Sunday Skill: Handstand & Crow',
      category: 'skill',
      targetRange: '10-15 min quality',
      ladders: [
        'L1: Wrist Prep + Pike Hold (Feet on sofa)',
        'L2: Crow Pose (Frog Stand) on floor (5 x 15-30s)',
        'L3: Chest-to-Wall Handstand Hold (5 x 20-45s)',
        'L4: Wall Heel Pulls / Toe Pulls -> Freestanding Balance'
      ],
      cues: [
        'Grip the floor actively with fingertips (cambered hand) to control forward tilt.',
        'In Chest-to-Wall Handstand: push tall through shoulders (elevate scapulae) and tuck ribs in.',
        'Always come down with 2-3 reps in the tank; never train balance skills to failure.'
      ],
      faults: 'Banana back (rib flare + anterior pelvic tilt); passive shoulders.',
      defaultNote: 'Sunday Skill & Mobility Day focus.'
    },
    {
      id: 'skill_lsit',
      slot: 'Sunday Skill: L-Sit & Skin the Cat',
      category: 'skill',
      targetRange: '60s total / 3x3-5',
      ladders: [
        'L1: Foot-Supported L-Sit on Floor/Books (60s)',
        'L2: One-Leg Assisted L-Sit (30s/side)',
        'L3: Tuck L-Sit (60s total in 10-20s sets)',
        'L4: Full L-Sit + Skin the Cat (German Hang)'
      ],
      cues: [
        'Depress shoulders hard to create clearance between hips and floor.',
        'Practice Seated Pike Leg Lifts (3x10) to eliminate hip flexor cramping.',
        'For Skin the Cat: keep grip secure, tuck knees through arms into controlled German Hang stretch.'
      ],
      faults: 'Hunching shoulders forward without depressing scapulae.',
      defaultNote: 'Accumulate 60s total L-sit time on Sundays.'
    }
  ];

  // Default initial state matching user's exact logs and Apple Health data
  const DEFAULT_STATE = {
    meta: {
      startWeight: 88.0,
      startDate: '2026-09-03',
      targetWeight: 73.5,
      tdee: 3390,
      targetKcal: 2400,
      avgSteps: 25307
    },
    activeProgressions: {
      pull: 'L4: Chin-Ups / Pull-Ups',
      squat: 'L3: Single-Leg Sofa Step-Up (No Back-Leg Push)',
      dip: 'L3: Parallel Bar Dips',
      hinge: 'L3: Floor Slide Hamstring Curl (Both Legs)',
      row: 'L2: Horizontal Inverted Rows (Feet on floor)',
      push: 'L3: Diamond Push-Up',
      core_antiext: 'L1: Forearm Plank (Hollow Body / PPT) 30-60s',
      core_antirot: 'L1: Side Plank (Feet stacked) 15-45s/side',
      core_ext: 'L3: Sofa Reverse Hyperextensions (Hips on edge of sofa)',
      skill_hs: 'L2: Crow Pose (Frog Stand) on floor (5 x 15-30s)',
      skill_lsit: 'L1: Foot-Supported L-Sit on Floor/Books (60s)'
    },
    customNotes: {},
    rrSessions: [
      {
        id: 'rr-2026-10-19',
        date: '2026-10-19',
        bw: 80.0,
        pull_prog: 'L4: Chin-Ups / Pull-Ups',
        pull_sets: '4,4,4',
        squat_prog: 'L3: Single-Leg Sofa Step-Up (No Back-Leg Push)',
        squat_sets: '8,8,8 (/leg)',
        dip_prog: 'L3: Parallel Bar Dips',
        dip_sets: '5,5,5',
        hinge_prog: 'L3: Floor Slide Hamstring Curl (Both Legs)',
        hinge_sets: '9,9,9',
        row_prog: 'L2: Horizontal Inverted Rows (Feet on floor)',
        row_sets: '7,7,7',
        push_prog: 'L3: Diamond Push-Up',
        push_sets: '4,4,4',
        antiext: 'Plank 2x30s',
        antirot: 'Side Plank 2x15s/side',
        ext: 'Arch/RevHyper 2x8',
        notes: 'RR Day 1 baseline. Core Triplet trimmed to 2 sets.'
      }
    ],
    weightLog: [
      { id: 'w1', date: '2026-09-03', kg: 88.0, kcal: null },
      { id: 'w2', date: '2026-09-17', kg: 85.0, kcal: null },
      { id: 'w3', date: '2026-09-24', kg: 81.0, kcal: null },
      { id: 'w4', date: '2026-10-16', kg: 80.0, kcal: 2400 }
    ],
    runLog: [
      { id: 'r1', date: '2026-10-01', type: 'Easy Run (Z2 + Strides)', km: 5.54, min: 34.8, hr: 158, notes: 'Apple Health' },
      { id: 'r2', date: '2026-10-04', type: 'Tempo / Threshold Run', km: 7.45, min: 45.7, hr: 162, notes: 'Apple Health' },
      { id: 'r3', date: '2026-10-07', type: 'Long Aerobic Run', km: 10.67, min: 64.9, hr: 158, notes: 'Apple Health' },
      { id: 'r4', date: '2026-10-09', type: 'Easy Run (Z2 + Strides)', km: 5.05, min: 31.3, hr: 152, notes: 'Apple Health' },
      { id: 'r5', date: '2026-10-10', type: 'Long Aerobic Run', km: 10.17, min: 65.5, hr: 154, notes: 'Apple Health' },
      { id: 'r6', date: '2026-10-12', type: 'Easy Run (Z2 + Strides)', km: 6.13, min: 38.4, hr: 153, notes: 'Apple Health' },
      { id: 'r7', date: '2026-10-14', type: 'Tempo / Threshold Run', km: 8.39, min: 52.8, hr: 160, notes: 'Apple Health' },
      { id: 'r8', date: '2026-10-16', type: 'Easy Run (Z2 + Strides)', km: 6.80, min: 43.3, hr: 156, notes: 'Apple Health' },
      { id: 'r9', date: '2026-10-19', type: 'Recovery Jog', km: 2.66, min: 17.5, hr: 147, notes: 'Warm-up run before RR #1' }
    ],
    schedule: [
      { day: 'MON', type: 'RR Full Body #1', rx: 'Pairs 1-3 (3x5-8 / 3x8-12) + Core Triplet (2 sets)', dur: '55m | 90s rest' },
      { day: 'TUE', type: 'Run #1: Easy + Strides', rx: '7-8 km conversational Zone 2 + 4x20s fast strides at end', dur: '45-50m | HR <150' },
      { day: 'WED', type: 'RR Full Body #2', rx: 'Pairs 1-3 (+1 rep target) + Core Triplet (2 sets)', dur: '55m | 90s rest' },
      { day: 'THU', type: 'Run #2: Tempo / Threshold', rx: '8-9 km total (2km WU -> 4-5km Tempo -> 2km CD)', dur: '50-55m | HR 155-165' },
      { day: 'FRI', type: 'RR Full Body #3', rx: 'Pairs 1-3 (+1 rep target) + Core Triplet (2 sets)', dur: '55m | 90s rest' },
      { day: 'SAT', type: 'Run #3: Long Aerobic Run', rx: '10-12 km steady aerobic endurance pace', dur: '65m | HR 148-155' },
      { day: 'SUN', type: 'Skill & Mobility Day', rx: 'Handstand (10m) + Crow (5m) + L-Sit (60s) + Skin the Cat + Mobility', dur: '40m | Low CNS' }
    ],
    programNotes: [
      '# RULES & PHASE 2 NOTES',
      '- Equipment: 100% Bodyweight Only (Pull-up bar, Dip setup, Row setup, Sofa/Floor). Zero barbells or bands.',
      '- Double Progression: Add +1 rep per session across sets (e.g., 4,4,4 -> 5,4,4 -> 5,5,4 -> ... -> 8,8,8), then advance to the next level in the ladder.',
      '- Core Triplet Volume: Kept at 2 sets (Plank 2x30s / Side Plank 2x15s / Arch-RevHyper 2x8) to manage systemic fatigue alongside 25k steps/day + 3x running.',
      '- Phase 2 Note (Future Option): If lower-body fatigue accumulates during the cut to 73.5 kg, Wednesday RR can transition into an Upper-Body + Skill Maintenance day while Mon & Fri remain full 3-pair RR.'
    ].join('\n')
  };

  let state = loadState();

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return Object.assign({}, DEFAULT_STATE, parsed);
      }
    } catch (e) {
      console.error('Failed to read localStorage:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_STATE));
  }

  function saveState(msg) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      if (msg) showToast(msg);
      renderAll();
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

  // Helper: compute next target sets from a comma-separated string like "4,4,4" or "8,8,8 (/leg)"
  function computeNextSets(setStr, maxRep = 8) {
    if (!setStr) return '5,5,5';
    const match = setStr.match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(.*)/);
    if (!match) return setStr + ' (+1)';
    let s1 = parseInt(match[1], 10);
    let s2 = parseInt(match[2], 10);
    let s3 = parseInt(match[3], 10);
    const suffix = match[4] || '';

    if (s1 >= maxRep && s2 >= maxRep && s3 >= maxRep) {
      return `${s1},${s2},${s3}${suffix} [LEVEL UP ->]`;
    }
    if (s1 <= s2 && s1 <= s3) {
      s1 += 1;
    } else if (s2 <= s3) {
      s2 += 1;
    } else {
      s3 += 1;
    }
    return `${s1},${s2},${s3}${suffix}`;
  }

  function sumReps(setStr) {
    if (!setStr) return 0;
    const nums = setStr.match(/\d+/g);
    if (!nums) return 0;
    return nums.slice(0, 3).reduce((a, b) => a + parseInt(b, 10), 0);
  }

  function getLatestWeight() {
    if (!state.weightLog || state.weightLog.length === 0) return 80.0;
    const sorted = [...state.weightLog].sort((a, b) => a.date.localeCompare(b.date));
    return sorted[sorted.length - 1].kg;
  }

  function getLatestRR() {
    if (!state.rrSessions || state.rrSessions.length === 0) return null;
    const sorted = [...state.rrSessions].sort((a, b) => a.date.localeCompare(b.date));
    return sorted[sorted.length - 1];
  }

  // ==========================================
  // RENDER VIEW 1: STATUS & DASHBOARD
  // ==========================================
  function renderStatus() {
    const curWeight = getLatestWeight();
    document.getElementById('bar-bw').textContent = curWeight.toFixed(1) + 'kg';

    const startW = state.meta.startWeight || 88.0;
    const targetW = state.meta.targetWeight || 73.5;
    const totalToLose = startW - targetW;
    const lostSoFar = startW - curWeight;
    const remaining = Math.max(0, curWeight - targetW);
    const pct = Math.min(100, Math.max(0, (lostSoFar / totalToLose) * 100));

    // KPI boxes
    const lastRR = getLatestRR();
    const totalRunsKm = state.runLog.reduce((acc, r) => acc + Number(r.km || 0), 0);
    const kpiHtml = `
      <div class="stat-box">
        <div class="stat-label">Current Weight</div>
        <div class="stat-val">${curWeight.toFixed(1)} kg</div>
        <div class="stat-sub">-${lostSoFar.toFixed(1)} kg since Sep 3 (${remaining.toFixed(1)} kg to goal)</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Daily Energy Target</div>
        <div class="stat-val">2,400 kcal</div>
        <div class="stat-sub">TDEE ~${state.meta.tdee} kcal | Protein 160-185g</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">RR Sessions Logged</div>
        <div class="stat-val">${state.rrSessions.length}</div>
        <div class="stat-sub">Last: ${lastRR ? lastRR.date : 'None'} (Pull ${lastRR ? lastRR.pull_sets : '-'})</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Logged Running Vol</div>
        <div class="stat-val">${totalRunsKm.toFixed(1)} km</div>
        <div class="stat-sub">${state.runLog.length} runs | Avg 25.3k steps/day</div>
      </div>
    `;
    document.getElementById('dashboard-kpis').innerHTML = kpiHtml;

    // ASCII Progress Bar
    const barWidth = 28;
    const filled = Math.round((pct / 100) * barWidth);
    const barStr = '#'.repeat(filled) + '.'.repeat(Math.max(0, barWidth - filled));
    const ascii = [
      `START  : ${startW.toFixed(1)} kg (2026-09-03)`,
      `CURRENT: ${curWeight.toFixed(1)} kg ([${barStr}] ${pct.toFixed(1)}%)`,
      `TARGET : ${targetW.toFixed(1)} kg (Est. ~6-8 weeks at -0.8 kg/wk)`,
      `DEFICIT: ~900 kcal/day (Intake 2,400 vs Burn ~3,390 kcal)`
    ].join('\n');
    document.getElementById('ascii-progress').textContent = ascii;

    // Next Workout Target Table
    const nextTbody = document.querySelector('#next-target-table tbody');
    if (lastRR) {
      const rows = [
        ['1A: Pull', state.activeProgressions.pull, lastRR.pull_sets, computeNextSets(lastRR.pull_sets, 8)],
        ['1B: Squat', state.activeProgressions.squat, lastRR.squat_sets, computeNextSets(lastRR.squat_sets, 8)],
        ['2A: Dip', state.activeProgressions.dip, lastRR.dip_sets, computeNextSets(lastRR.dip_sets, 8)],
        ['2B: Hinge', state.activeProgressions.hinge, lastRR.hinge_sets, computeNextSets(lastRR.hinge_sets, 12)],
        ['3A: Row', state.activeProgressions.row, lastRR.row_sets, computeNextSets(lastRR.row_sets, 12)],
        ['3B: Push', state.activeProgressions.push, lastRR.push_sets, computeNextSets(lastRR.push_sets, 8)],
        ['Core (2x)', 'Plank / Side / Arch', `${lastRR.antiext} | ${lastRR.antirot} | ${lastRR.ext}`, 'Plank 2x35s | Side 2x20s | Arch 2x9']
      ];
      nextTbody.innerHTML = rows.map(r => `
        <tr>
          <td><strong>${r[0]}</strong></td>
          <td class="muted">${r[1]}</td>
          <td>${r[2]}</td>
          <td><span class="badge badge-invert">${r[3]}</span></td>
        </tr>
      `).join('');
    }

    // Active Progressions Quick Switcher
    const progTbody = document.querySelector('#active-progressions-table tbody');
    progTbody.innerHTML = EXERCISE_DB.slice(0, 9).map(ex => {
      const currentVal = state.activeProgressions[ex.id] || ex.ladders[0];
      const optionsHtml = ex.ladders.map(l => `<option value="${l}" ${l === currentVal ? 'selected' : ''}>${l}</option>`).join('');
      return `
        <tr>
          <td><strong>${ex.slot}</strong></td>
          <td>
            <select data-prog-switch="${ex.id}" aria-label="${ex.slot} Progression">
              ${optionsHtml}
            </select>
          </td>
          <td>${ex.targetRange}</td>
          <td class="muted">Hit max reps x3 -> next level</td>
        </tr>
      `;
    }).join('');

    // Mini Schedule Table
    const miniSchedTbody = document.querySelector('#mini-schedule-table tbody');
    miniSchedTbody.innerHTML = state.schedule.map(s => `
      <tr>
        <td><strong>${s.day}</strong></td>
        <td>${s.type}</td>
        <td class="muted">${s.rx}</td>
      </tr>
    `).join('');
  }

  // ==========================================
  // RENDER VIEW 2: LOG & EDIT WORKOUTS
  // ==========================================
  function populateLoggerSelects() {
    const map = [
      ['rr-pull-prog', 'pull'],
      ['rr-squat-prog', 'squat'],
      ['rr-dip-prog', 'dip'],
      ['rr-hinge-prog', 'hinge'],
      ['rr-row-prog', 'row'],
      ['rr-push-prog', 'push']
    ];
    map.forEach(([selectId, exId]) => {
      const sel = document.getElementById(selectId);
      const ex = EXERCISE_DB.find(e => e.id === exId);
      if (!sel || !ex) return;
      const active = state.activeProgressions[exId] || ex.ladders[0];
      sel.innerHTML = ex.ladders.map(l => `<option value="${l}" ${l === active ? 'selected' : ''}>${l}</option>`).join('');
    });
  }

  function renderRRHistory() {
    const tbody = document.querySelector('#rr-history-table tbody');
    const sorted = [...state.rrSessions].sort((a, b) => b.date.localeCompare(a.date));
    document.getElementById('rr-count-meta').textContent = `${sorted.length} session(s) logged`;

    tbody.innerHTML = sorted.map(s => {
      const totalVol = sumReps(s.pull_sets) + sumReps(s.squat_sets) + sumReps(s.dip_sets) +
                       sumReps(s.hinge_sets) + sumReps(s.row_sets) + sumReps(s.push_sets);
      return `
        <tr>
          <td><strong>${s.date}</strong></td>
          <td>${s.bw ? Number(s.bw).toFixed(1) + 'kg' : '-'}</td>
          <td>
            <div><strong>P:</strong> ${s.pull_sets} <span class="muted">(${shortProg(s.pull_prog)})</span></div>
            <div><strong>S:</strong> ${s.squat_sets} <span class="muted">(${shortProg(s.squat_prog)})</span></div>
          </td>
          <td>
            <div><strong>D:</strong> ${s.dip_sets} <span class="muted">(${shortProg(s.dip_prog)})</span></div>
            <div><strong>H:</strong> ${s.hinge_sets} <span class="muted">(${shortProg(s.hinge_prog)})</span></div>
          </td>
          <td>
            <div><strong>R:</strong> ${s.row_sets} <span class="muted">(${shortProg(s.row_prog)})</span></div>
            <div><strong>PU:</strong> ${s.push_sets} <span class="muted">(${shortProg(s.push_prog)})</span></div>
          </td>
          <td>
            <div>${s.antiext}</div>
            <div>${s.antirot}</div>
            <div>${s.ext}</div>
          </td>
          <td><strong>${totalVol}</strong> reps</td>
          <td class="muted">${s.notes || ''}</td>
          <td>
            <div class="btn-row">
              <button type="button" class="btn-inline" data-edit-rr="${s.id}">edit</button>
              <button type="button" class="btn-inline" data-del-rr="${s.id}">del</button>
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

  // Shorthand Parser: e.g. "pullu 4 4 4 singlelegraisedsquat 8 8 8 floorslideprogression 9 9 9 dips 5 5 5 inverted rows 7 7 7 diamond p 4 4 4 plank 30sx2"
  function parseShorthandToForm(raw) {
    if (!raw || !raw.trim()) return false;
    const s = raw.toLowerCase();

    function extractTriple(regex) {
      const m = s.match(regex);
      if (m) return `${m[1]},${m[2]},${m[3]}`;
      return null;
    }

    const pull = extractTriple(/pull\w*\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);
    const squat = extractTriple(/(?:squat\w*|step\w*|bss|shrimp\w*)\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);
    const hinge = extractTriple(/(?:floor\w*|slide\w*|hinge\w*|nordic\w*|curl\w*)\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);
    const dip = extractTriple(/dip\w*\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);
    const row = extractTriple(/(?:inverted\s+rows?|rows?)\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);
    const push = extractTriple(/(?:diamond\s*p\w*|push\w*|pppu)\s+(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)/);

    if (pull) document.getElementById('rr-pull-sets').value = pull;
    if (squat) document.getElementById('rr-squat-sets').value = squat + ' (/leg)';
    if (hinge) document.getElementById('rr-hinge-sets').value = hinge;
    if (dip) document.getElementById('rr-dip-sets').value = dip;
    if (row) document.getElementById('rr-row-sets').value = row;
    if (push) document.getElementById('rr-push-sets').value = push;

    const plankM = s.match(/plank\s+([0-9sx]+)/);
    if (plankM) document.getElementById('rr-antiext').value = 'Plank ' + plankM[1];

    const sideM = s.match(/side\s*planks?\s+([0-9sx]+)/);
    if (sideM) document.getElementById('rr-antirot').value = 'Side Plank ' + sideM[1];

    const archM = s.match(/(?:arch|reverse\s*hyper|revhyper)[a-z\s]*([0-9sx]+)/);
    if (archM) document.getElementById('rr-ext').value = 'Arch/RevHyper ' + archM[1];

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
    document.getElementById('rr-bw').value = getLatestWeight().toFixed(1);
    if (last) {
      document.getElementById('rr-pull-sets').value = computeNextSets(last.pull_sets, 8).replace(/\s*\[.*\]/, '');
      document.getElementById('rr-squat-sets').value = computeNextSets(last.squat_sets, 8).replace(/\s*\[.*\]/, '');
      document.getElementById('rr-dip-sets').value = computeNextSets(last.dip_sets, 8).replace(/\s*\[.*\]/, '');
      document.getElementById('rr-hinge-sets').value = computeNextSets(last.hinge_sets, 12).replace(/\s*\[.*\]/, '');
      document.getElementById('rr-row-sets').value = computeNextSets(last.row_sets, 12).replace(/\s*\[.*\]/, '');
      document.getElementById('rr-push-sets').value = computeNextSets(last.push_sets, 8).replace(/\s*\[.*\]/, '');
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
        <td><strong>${item.day}</strong></td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="type" value="${escapeAttr(item.type)}" aria-label="${item.day} session type">
        </td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="rx" value="${escapeAttr(item.rx)}" aria-label="${item.day} prescription">
        </td>
        <td>
          <input type="text" data-sched-idx="${idx}" data-sched-field="dur" value="${escapeAttr(item.dur)}" aria-label="${item.day} duration">
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
      const customNote = state.customNotes[ex.id] !== undefined ? state.customNotes[ex.id] : ex.defaultNote;

      const ladderHtml = ex.ladders.map(step => {
        const isCur = step === currentProg;
        return `
          <li class="ladder-item ${isCur ? 'current' : ''}">
            <span>${step}</span>
            ${isCur
              ? '<span class="badge">ACTIVE</span>'
              : `<button type="button" class="btn-inline" data-set-ladder="${ex.id}" data-step="${escapeAttr(step)}">Set Active</button>`
            }
          </li>
        `;
      }).join('');

      const cuesHtml = ex.cues.map(c => `<li>- ${c}</li>`).join('');

      return `
        <div class="tile col-6">
          <div class="tile-header">
            <span>${ex.slot}</span>
            <span class="meta">Target: ${ex.targetRange}</span>
          </div>
          <div class="tile-body">
            <h4>Bodyweight Progression Ladder</h4>
            <ul class="ladder-list">${ladderHtml}</ul>

            <h4 style="margin-top:10px;">Strict Form Cues (Tempo 10X0)</h4>
            <ul style="list-style:none; margin-bottom:8px; font-size:12px;">${cuesHtml}</ul>

            <p style="font-size:11px;" class="muted"><strong>Avoid Faults:</strong> ${ex.faults}</p>

            <div class="field" style="margin-top:8px;">
              <label for="note-${ex.id}">Personal Setup / Form Note:</label>
              <div class="btn-row">
                <input type="text" id="note-${ex.id}" data-ex-note="${ex.id}" value="${escapeAttr(customNote)}" style="flex:1;">
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
  function renderMetrics() {
    // Weight Table & SVG Chart
    const sortedW = [...state.weightLog].sort((a, b) => a.date.localeCompare(b.date));
    const wTbody = document.querySelector('#weight-table tbody');
    wTbody.innerHTML = [...sortedW].reverse().map((w, i, arr) => {
      const prev = arr[i + 1];
      const delta = prev ? (w.kg - prev.kg) : 0;
      const deltaStr = prev ? (delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)) : '-';
      return `
        <tr>
          <td><strong>${w.date}</strong></td>
          <td>${Number(w.kg).toFixed(1)} kg</td>
          <td class="muted">${deltaStr} kg</td>
          <td>${w.kcal ? w.kcal + ' kcal' : '-'}</td>
          <td><button type="button" class="btn-inline" data-del-wt="${w.id}">del</button></td>
        </tr>
      `;
    }).join('');

    renderWeightSvg(sortedW);

    // Run Table
    const sortedR = [...state.runLog].sort((a, b) => b.date.localeCompare(a.date));
    const totalKm = sortedR.reduce((a, r) => a + Number(r.km || 0), 0);
    document.getElementById('run-summary-meta').textContent = `${sortedR.length} runs | ${totalKm.toFixed(1)} km total`;

    const rTbody = document.querySelector('#run-table tbody');
    rTbody.innerHTML = sortedR.map(r => {
      const paceDec = r.km > 0 ? (r.min / r.km) : 0;
      const pMin = Math.floor(paceDec);
      const pSec = Math.round((paceDec - pMin) * 60).toString().padStart(2, '0');
      return `
        <tr>
          <td><strong>${r.date}</strong></td>
          <td>${r.type}</td>
          <td>${Number(r.km).toFixed(2)} km</td>
          <td>${Number(r.min).toFixed(1)} m</td>
          <td>${pMin}:${pSec}/km</td>
          <td>${r.hr ? r.hr + ' bpm' : '-'}</td>
          <td><button type="button" class="btn-inline" data-del-run="${r.id}">del</button></td>
        </tr>
      `;
    }).join('');
  }

  function renderWeightSvg(sortedW) {
    const wrap = document.getElementById('weight-svg-wrap');
    if (!sortedW.length) {
      wrap.innerHTML = '<div class="muted">No weight entries yet.</div>';
      return;
    }
    const W = 500, H = 155, padL = 38, padR = 18, padT = 14, padB = 24;
    const minKg = 72;
    const maxKg = 90;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const yFor = kg => padT + plotH - ((kg - minKg) / (maxKg - minKg)) * plotH;
    const xFor = idx => sortedW.length === 1 ? padL + plotW / 2 : padL + (idx / (sortedW.length - 1)) * plotW;

    const targetY = yFor(state.meta.targetWeight || 73.5);
    const pts = sortedW.map((d, i) => `${xFor(i).toFixed(1)},${yFor(d.kg).toFixed(1)}`).join(' ');

    const circles = sortedW.map((d, i) => {
      const cx = xFor(i).toFixed(1);
      const cy = yFor(d.kg).toFixed(1);
      return `
        <circle cx="${cx}" cy="${cy}" r="3.5" fill="currentColor" />
        <text x="${cx}" y="${cy - 7}" text-anchor="middle" font-size="10" fill="currentColor">${d.kg.toFixed(1)}</text>
        <text x="${cx}" y="${H - 6}" text-anchor="middle" font-size="9" fill="#888">${d.date.slice(5)}</text>
      `;
    }).join('');

    wrap.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" width="100%" height="155" role="img" aria-label="Weight progress chart">
        <line x1="${padL}" y1="${yFor(88)}" x2="${W - padR}" y2="${yFor(88)}" stroke="#333" stroke-dasharray="2,2"/>
        <text x="4" y="${yFor(88) + 3}" font-size="9" fill="#888">88kg</text>
        <line x1="${padL}" y1="${yFor(80)}" x2="${W - padR}" y2="${yFor(80)}" stroke="#333" stroke-dasharray="2,2"/>
        <text x="4" y="${yFor(80) + 3}" font-size="9" fill="#888">80kg</text>
        <line x1="${padL}" y1="${targetY}" x2="${W - padR}" y2="${targetY}" stroke="#888" stroke-dasharray="4,3"/>
        <text x="4" y="${targetY + 3}" font-size="9" fill="currentColor">73.5</text>
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
      `- **Current Weight:** ${getLatestWeight().toFixed(1)} kg (Start: 88.0 kg -> Goal: 73.5 kg)`,
      `- **Daily Energy Target:** ~2,400 kcal (TDEE ~3,390 kcal | 160-185g Protein)`,
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
    const savedToken = localStorage.getItem(GH_TOKEN_KEY);
    const tokenInput = document.getElementById('gh-token');
    if (savedToken && tokenInput && !tokenInput.value) {
      tokenInput.value = savedToken;
    }
  }

  function escapeAttr(str) {
    return String(str || '').replace(/"/g, '&quot;');
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
      const root = document.documentElement;
      const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
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
    state.schedule = JSON.parse(JSON.stringify(DEFAULT_STATE.schedule));
    saveState('DEFAULT SCHEDULE RESTORED');
  });

  // Weight Form
  document.getElementById('weight-form').addEventListener('submit', e => {
    e.preventDefault();
    const date = document.getElementById('wt-date').value;
    const kg = parseFloat(document.getElementById('wt-val').value);
    const kcal = parseInt(document.getElementById('wt-kcal').value, 10);
    if (!date || isNaN(kg)) return;
    state.weightLog.push({
      id: 'w-' + Date.now(),
      date,
      kg,
      kcal: !isNaN(kcal) ? kcal : null
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
      state = Object.assign({}, DEFAULT_STATE, parsed);
      saveState('STATE IMPORTED');
    } catch (err) {
      showToast('INVALID JSON');
    }
  });

  document.getElementById('btn-factory-reset').addEventListener('click', () => {
    state = JSON.parse(JSON.stringify(DEFAULT_STATE));
    saveState('RESET TO BASELINE');
  });

  // GitHub Direct API Sync
  async function githubUpsertFile(repo, branch, token, path, contentStr, message) {
    const url = `https://api.github.com/repos/${repo}/contents/${path}`;
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'Content-Type': 'application/json'
    };
    let sha = null;
    const getRes = await fetch(`${url}?ref=${encodeURIComponent(branch)}`, { headers });
    if (getRes.ok) {
      const getJson = await getRes.json();
      sha = getJson.sha;
    }
    const body = {
      message,
      content: btoa(unescape(encodeURIComponent(contentStr))),
      branch
    };
    if (sha) body.sha = sha;
    const putRes = await fetch(url, { method: 'PUT', headers, body: JSON.stringify(body) });
    if (!putRes.ok) {
      const errText = await putRes.text();
      throw new Error(`GitHub API ${putRes.status}: ${errText}`);
    }
  }

  document.getElementById('gh-sync-form').addEventListener('submit', async e => {
    e.preventDefault();
    const repo = document.getElementById('gh-repo').value.trim();
    const branch = document.getElementById('gh-branch').value.trim();
    const token = document.getElementById('gh-token').value.trim();
    const statusEl = document.getElementById('gh-sync-status');
    if (!token) {
      statusEl.textContent = 'Error: Enter a GitHub Personal Access Token first.';
      return;
    }
    localStorage.setItem(GH_TOKEN_KEY, token);
    statusEl.textContent = 'Pushing data.json and WORKOUT_LOG.md to GitHub...';
    try {
      await githubUpsertFile(repo, branch, token, 'data.json', JSON.stringify(state, null, 2), 'Sync FIT state from web UI');
      await githubUpsertFile(repo, branch, token, 'WORKOUT_LOG.md', generateMarkdownExport(), 'Sync WORKOUT_LOG.md from web UI');
      statusEl.textContent = `Synced to ${repo}@${branch} at ${new Date().toLocaleTimeString()}`;
      showToast('SYNCED TO GITHUB');
    } catch (err) {
      statusEl.textContent = err.message;
    }
  });

  document.getElementById('btn-gh-pull').addEventListener('click', async () => {
    const repo = document.getElementById('gh-repo').value.trim();
    const branch = document.getElementById('gh-branch').value.trim();
    const statusEl = document.getElementById('gh-sync-status');
    statusEl.textContent = 'Fetching latest data.json...';
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${repo}/${branch}/data.json?t=${Date.now()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const remoteState = await res.json();
      state = Object.assign({}, DEFAULT_STATE, remoteState);
      saveState('PULLED FROM GITHUB');
      statusEl.textContent = `Pulled latest data.json from ${repo}@${branch}.`;
    } catch (err) {
      statusEl.textContent = 'Pull failed: ' + err.message;
    }
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
  prefillNextTargetIntoForm();
  renderAll();
})();
