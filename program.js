/* Generic program definition (no personal data). Shared by app.js and fit.py.
 * Everything after the assignment below must stay strict JSON (fit.py parses it). */
window.FIT_PROGRAM = {
  "exercises": [
    {
      "id": "pull",
      "slot": "Pair 1A: Pull",
      "category": "pair1",
      "targetRange": "3 x 5-8",
      "ladders": [
        "L1: Scapular Pulls / Dead Hangs",
        "L2: Arch Hangs",
        "L3: Pull-Up Negatives (5-10s eccentric)",
        "L4: Chin-Ups / Pull-Ups",
        "L5: L-Sit Pull-Ups",
        "L6: Archer / Typewriter Pull-Ups"
      ],
      "cues": [
        "Start from a full dead hang with arms straight.",
        "Depress scapulae (pull shoulders down away from ears) before bending elbows.",
        "Drive elbows down and back toward your ribs until chin clears the bar.",
        "Lower under strict control (1-2s eccentric) all the way to dead hang."
      ],
      "faults": "Kipping knees, crane-necking chin over bar with rounded shoulders, cutting bottom 20% of dead hang.",
      "defaultNote": "",
      "minRep": 5,
      "maxRep": 8
    },
    {
      "id": "squat",
      "slot": "Pair 1B: Squat",
      "category": "pair1",
      "targetRange": "3 x 5-8 (/leg)",
      "ladders": [
        "L1: Assisted Squat",
        "L2: Full Depth Bodyweight Squat",
        "L3: Single-Leg Sofa Step-Up (No Back-Leg Push)",
        "L4: Bulgarian Split Squat (Rear Foot on Sofa)",
        "L5: Beginner Shrimp Squat (Knee + Toes touch)",
        "L6: Intermediate/Advanced Shrimp or Pistol Squat"
      ],
      "cues": [
        "For Single-Leg Sofa Step-Up: place top foot flat on sofa, lean torso slightly forward over working knee.",
        "Keep rear foot dorsiflexed (toes pulled up) so you cannot bounce off the back calf.",
        "Take a 3-second lowering phase down to the floor on each rep.",
        "Once 8,8,8 feels easy, switch to Bulgarian Split Squats or Beginner Shrimp Squats."
      ],
      "faults": "Pushing off the floor with the back foot; knee caving inward (valgus); dropping down uncontrolled.",
      "defaultNote": "",
      "minRep": 5,
      "maxRep": 8
    },
    {
      "id": "dip",
      "slot": "Pair 2A: Dip",
      "category": "pair2",
      "targetRange": "3 x 5-8",
      "ladders": [
        "L1: Parallel Bar Support Hold (60s)",
        "L2: Negative Dips (5-8s eccentric)",
        "L3: Parallel Bar Dips",
        "L4: L-Sit Dips / Pause Dips (2s bottom)",
        "L5: Ring Dips / Korean Dips"
      ],
      "cues": [
        "Start in locked-out support with depressed shoulders (long neck).",
        "Lean torso slightly forward (~15-20 deg) and tuck elbows back (~45 deg maximum flare).",
        "Descend until upper arms are at least parallel to the floor (shoulder crease below elbow).",
        "Press up to full lockout and re-depress shoulders at the top."
      ],
      "faults": "Shrugging shoulders into ears; flaring elbows out 90 deg; stopping above parallel.",
      "defaultNote": "",
      "minRep": 5,
      "maxRep": 8
    },
    {
      "id": "hinge",
      "slot": "Pair 2B: Hinge",
      "category": "pair2",
      "targetRange": "3 x 8-12",
      "ladders": [
        "L1: Romanian Deadlift (Bodyweight / Single-Leg Balance)",
        "L2: Glute Bridge Hold / Marching Bridge",
        "L3: Floor Slide Hamstring Curl (Both Legs)",
        "L4: Eccentric Single-Leg Floor Slide (2-up, 1-down)",
        "L5: Single-Leg Floor Slide Hamstring Curl",
        "L6: Nordic Hamstring Curl (Anchored under sofa)"
      ],
      "cues": [
        "Lie supine with heels on sliders/towel/socks on smooth floor.",
        "Tuck pelvis slightly (posterior pelvic tilt) and squeeze glutes before sliding.",
        "Keep a straight line from knees through hips to shoulders throughout the slide.",
        "If 3x9-12 bilateral feels manageable, slide out on 1 leg (4s eccentric) and pull back with 2 legs."
      ],
      "faults": "Letting hips sag toward the floor while sliding; overarching lower back instead of using hamstrings.",
      "defaultNote": "",
      "minRep": 8,
      "maxRep": 12
    },
    {
      "id": "row",
      "slot": "Pair 3A: Row",
      "category": "pair3",
      "targetRange": "3 x 8-12",
      "ladders": [
        "L1: Incline Rows (45 deg body angle)",
        "L2: Horizontal Inverted Rows (Feet on floor)",
        "L3: Feet-Elevated Inverted Rows (Feet on sofa)",
        "L4: Wide-Grip / Tuck Front Lever Rows",
        "L5: Archer Rows / One-Arm Row Progression"
      ],
      "cues": [
        "Maintain a rigid plank from ankles to shoulders (squeeze glutes and abs).",
        "Pull bar/rings to lower chest or upper abs while retracting shoulder blades together.",
        "Pause 1 second at the top of every rep to eliminate momentum.",
        "Keep wrists neutral (do not curl wrists at the top)."
      ],
      "faults": "Hips sagging or piking up to shorten the lever; head jutting forward to meet the bar.",
      "defaultNote": "",
      "minRep": 8,
      "maxRep": 12
    },
    {
      "id": "push",
      "slot": "Pair 3B: Push-Up",
      "category": "pair3",
      "targetRange": "3 x 5-8",
      "ladders": [
        "L1: Incline Push-Up (Hands on sofa)",
        "L2: Full Standard Push-Up (Hollow body)",
        "L3: Diamond Push-Up",
        "L4: Decline Diamond / Feet-Elevated Push-Up",
        "L5: Pseudo Planche Push-Up (PPPU - lean forward)",
        "L6: Archer Push-Up"
      ],
      "cues": [
        "Form a diamond or narrow triangle with index fingers and thumbs under your sternum.",
        "Tuck pelvis (posterior pelvic tilt) and squeeze quads + glutes.",
        "Keep elbows tracking back at ~30-45 deg along your ribcage (never flare sideways).",
        "Touch chest to hands, then press to full lockout with scapular protraction at the top."
      ],
      "faults": "Elbows flaring out into a T-shape; lower back sagging; stopping short of chest-to-hand contact.",
      "defaultNote": "",
      "minRep": 5,
      "maxRep": 8
    },
    {
      "id": "core_antiext",
      "slot": "Core 1: Anti-Extension",
      "category": "core",
      "targetRange": "2 x 30-60s / 8-12",
      "ladders": [
        "L1: Forearm Plank (Hollow Body / PPT) 30-60s",
        "L2: Long-Lever Plank (Elbows ahead of eyes)",
        "L3: Plank Towel/Socks Floor Slide Out",
        "L4: Standing Ab Walkouts"
      ],
      "cues": [
        "Tuck tailbone under hard (posterior pelvic tilt) so lower back is flat, not arched.",
        "Protract shoulder blades (push floor away) and pull elbows metaphorically toward toes.",
        "Once 2x30s feels easy, walk elbows 5-10cm forward into a Long-Lever Plank."
      ],
      "faults": "Passive resting on lumbar spine; looking up instead of neutral neck.",
      "defaultNote": "",
      "minRep": null,
      "maxRep": null
    },
    {
      "id": "core_antirot",
      "slot": "Core 2: Anti-Rotation",
      "category": "core",
      "targetRange": "2 x 15-45s/side",
      "ladders": [
        "L1: Side Plank (Feet stacked) 15-45s/side",
        "L2: Side Plank with Top Leg Abduction",
        "L3: Copenhagen Plank (Top foot/knee on sofa)"
      ],
      "cues": [
        "Place elbow directly beneath shoulder; stack hips and shoulders vertically.",
        "Drive bottom hip high off the floor and squeeze glutes so body forms a straight line.",
        "Copenhagen Plank (top leg on sofa) is a top-tier progression for runners (adductor + oblique armor)."
      ],
      "faults": "Top shoulder rolling forward; hips flexing backward into a V-shape.",
      "defaultNote": "",
      "minRep": null,
      "maxRep": null
    },
    {
      "id": "core_ext",
      "slot": "Core 3: Extension",
      "category": "core",
      "targetRange": "2 x 8-12",
      "ladders": [
        "L1: Prone Arch Hold (Superman with straight arms/legs)",
        "L2: Prone Arch Raises (Dynamic 2s hold at top)",
        "L3: Sofa Reverse Hyperextensions (Hips on edge of sofa)"
      ],
      "cues": [
        "For Sofa Reverse Hyper: lie prone on sofa with hip crease right at the edge, gripping sofa frame.",
        "Raise straight legs using glutes and spinal erectors until body is horizontal.",
        "Pause 1 second at the top; do not swing wildly above horizontal."
      ],
      "faults": "Bending knees excessively; using momentum to hyperextend lumbar spine.",
      "defaultNote": "",
      "minRep": null,
      "maxRep": null
    },
    {
      "id": "skill_hs",
      "slot": "Sunday Skill: Handstand & Crow",
      "category": "skill",
      "targetRange": "10-15 min quality",
      "ladders": [
        "L1: Wrist Prep + Pike Hold (Feet on sofa)",
        "L2: Crow Pose (Frog Stand) on floor (5 x 15-30s)",
        "L3: Chest-to-Wall Handstand Hold (5 x 20-45s)",
        "L4: Wall Heel Pulls / Toe Pulls -> Freestanding Balance"
      ],
      "cues": [
        "Grip the floor actively with fingertips (cambered hand) to control forward tilt.",
        "In Chest-to-Wall Handstand: push tall through shoulders (elevate scapulae) and tuck ribs in.",
        "Always come down with 2-3 reps in the tank; never train balance skills to failure."
      ],
      "faults": "Banana back (rib flare + anterior pelvic tilt); passive shoulders.",
      "defaultNote": "",
      "minRep": null,
      "maxRep": null
    },
    {
      "id": "skill_lsit",
      "slot": "Sunday Skill: L-Sit & Skin the Cat",
      "category": "skill",
      "targetRange": "60s total / 3x3-5",
      "ladders": [
        "L1: Foot-Supported L-Sit on Floor/Books (60s)",
        "L2: One-Leg Assisted L-Sit (30s/side)",
        "L3: Tuck L-Sit (60s total in 10-20s sets)",
        "L4: Full L-Sit + Skin the Cat (German Hang)"
      ],
      "cues": [
        "Depress shoulders hard to create clearance between hips and floor.",
        "Practice Seated Pike Leg Lifts (3x10) to eliminate hip flexor cramping.",
        "For Skin the Cat: keep grip secure, tuck knees through arms into controlled German Hang stretch."
      ],
      "faults": "Hunching shoulders forward without depressing scapulae.",
      "defaultNote": "",
      "minRep": null,
      "maxRep": null
    }
  ],
  "defaultSchedule": [
    {
      "day": "MON",
      "type": "RR Full Body #1",
      "rx": "Pairs 1-3 (3x5-8 / 3x8-12) + Core Triplet (2 sets)",
      "dur": "55m | 90s rest"
    },
    {
      "day": "TUE",
      "type": "Run #1: Easy + Strides",
      "rx": "7-8 km conversational Zone 2 + 4x20s fast strides at end",
      "dur": "45-50m | HR <148"
    },
    {
      "day": "WED",
      "type": "RR Full Body #2",
      "rx": "Pairs 1-3 (+1 rep target) + Core Triplet (2 sets)",
      "dur": "55m | 90s rest"
    },
    {
      "day": "THU",
      "type": "Run #2: Tempo / Threshold",
      "rx": "8-9 km total (2km WU -> 4-5km Tempo -> 2km CD)",
      "dur": "50-55m | HR 155-165"
    },
    {
      "day": "FRI",
      "type": "RR Full Body #3",
      "rx": "Pairs 1-3 (+1 rep target) + Core Triplet (2 sets)",
      "dur": "55m | 90s rest"
    },
    {
      "day": "SAT",
      "type": "Run #3: Long Aerobic Run",
      "rx": "10-12 km steady aerobic endurance pace",
      "dur": "65m | HR 148-155"
    },
    {
      "day": "SUN",
      "type": "Skill & Mobility Day",
      "rx": "Handstand (10m) + Crow (5m) + L-Sit (60s) + Skin the Cat + Mobility",
      "dur": "40m | Low CNS"
    }
  ],
  "defaultProgramNotes": "# RULES & PHASE 2 NOTES\n- Equipment: 100% Bodyweight Only (Pull-up bar, Dip setup, Row setup, Sofa/Floor). Zero barbells or bands.\n- Double Progression: Add +1 rep per session across sets (e.g., 4,4,4 -> 5,4,4 -> 5,5,4 -> ... -> 8,8,8), then advance to the next level in the ladder.\n- Core Triplet Volume: Kept at 2 sets (Plank 2x30s / Side Plank 2x15s / Arch-RevHyper 2x8) to manage systemic fatigue alongside high daily step counts + 3x running.\n- Phase 2 Note (Future Option): If lower-body fatigue accumulates during the cut, Wednesday RR can transition into an Upper-Body + Skill Maintenance day while Mon & Fri remain full 3-pair RR."
};
