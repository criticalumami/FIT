#!/usr/bin/env python3
"""
Generate the dedicated Sunday Skill & Mobility Day Visual Form Guide PDF
(Skill_Day_Form_Guide.pdf & generated/Skill_Day_Form_Guide.pdf).
Uses clean Darebee / Overcoming Gravity style anatomical ink line-art illustrations
for every exercise card.
"""
import base64
import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(DIR, "generated")
ART_DIR = os.path.join(DIR, "assets", "art")
HTML_PATH = os.path.join(OUT_DIR, "skill_day_form_guide.html")
PDF_PATH_GEN = os.path.join(OUT_DIR, "Skill_Day_Form_Guide.pdf")
PDF_PATH_ROOT = os.path.join(DIR, "Skill_Day_Form_Guide.pdf")


def img_card(filename, label_top, cue_bottom):
    """Embed a high-resolution Darebee-style anatomical ink illustration card."""
    p = os.path.join(ART_DIR, filename)
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"""
    <div class="art-box">
      <div class="art-top">{label_top}</div>
      <div class="art-img-wrap">
        <img src="data:image/jpeg;base64,{b64}" alt="{label_top}">
      </div>
      <div class="art-cue">{cue_bottom}</div>
    </div>
    """


CARDS = {
    "wrist_prep": img_card("warmup_wrist.jpg", "1A. GMB QUADRUPED WRIST PREP", "ELBOWS 100% LOCKED — ROCK OVER SPREAD FINGERS"),
    "yuri": img_card("warmup_dislocate.jpg", "1B. STICK / TOWEL DISLOCATES", "SHRUG UP OVERHEAD — KEEP RIBS TUCKED DOWN"),
    "handstand_wall": img_card("skill_handstand.jpg", "2A. CHEST-TO-WALL HANDSTAND", "FACE WALL — PUSH FLOOR AWAY — LOCK PPT"),
    "heel_pulls": img_card("skill_heel_pull.jpg", "2B. WALL HEEL PULLS (FINGER BRAKES)", "PRESS FINGERTIPS TO FLOAT TOES 2 CM OFF WALL"),
    "crow": img_card("skill_crow.jpg", "3A. CROW POSE (BENT ELBOW SHELF)", "KNEES ON TRICEPS — GAZE 30 CM AHEAD"),
    "crane": img_card("skill_crane.jpg", "3B. CRANE POSE (LOCKED ARMS)", "STRAIGHT ARMS — KNEES HIGH IN ARMPITS"),
    "lsit": img_card("skill_lsit.jpg", "4A. FLOOR L-SIT PROGRESSION", "PALMS BESIDE HIPS — DEPRESS SHOULDERS HARD"),
    "pike_lift": img_card("skill_pike.jpg", "4B. SEATED PIKE COMPRESSION LIFTS", "HANDS PAST KNEES — LIFT LOCKED LEGS"),
    "skin_tuck": img_card("skill_skinthecat.jpg", "5A. SKIN THE CAT TUCK PASS", "OVERHAND GRIP — TUCK KNEES THROUGH ARMS"),
    "german_hang": img_card("skill_germanhang.jpg", "5B. CONTROLLED GERMAN HANG", "ELBOWS LOCKED — MILD 5/10 PEC/BICEP STRETCH"),
    "couch_stretch": img_card("rehab_couch.jpg", "6A. KNEELING COUCH STRETCH", "TUCK TAILBONE (PPT) & SQUEEZE REAR GLUTE"),
    "ankle_rehab": img_card("rehab_ankle.jpg", "6B. SOLEUS DRIVE + ISO CALF HOLD", "60s SOLEUS STRETCH + 3×30s ANKLE TENDON HOLD"),
}


HTML_DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sunday Skill &amp; Mobility Day — Darebee-Style Visual Form Guide</title>
<style>
  @page {{
    size: A4;
    margin: 6.5mm 8.5mm 6.5mm 8.5mm;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    font-size: 7.8pt;
    line-height: 1.25;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .page {{
    page-break-after: always;
    break-after: page;
  }}
  .page:last-child {{
    page-break-after: auto;
    break-after: auto;
  }}
  .hero {{
    background: #111111;
    color: #ffffff;
    padding: 7px 12px;
    border-bottom: 3px solid #dc2626;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .hero h1 {{
    font-size: 12.8pt;
    font-weight: 900;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .hero p {{
    font-size: 7.4pt;
    color: #d4d4d8;
  }}
  .hero-badge {{
    background: #27272a;
    border: 1px solid #52525b;
    border-left: 3px solid #dc2626;
    padding: 4px 9px;
    text-align: right;
    font-size: 6.9pt;
    line-height: 1.3;
    white-space: nowrap;
  }}
  .hero-badge strong {{
    color: #f87171;
    font-size: 7.5pt;
  }}
  .rules-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    margin-bottom: 5px;
  }}
  .rule-card {{
    background: #fafafa;
    border: 1px solid #d4d4d8;
    border-top: 2.5px solid #111111;
    padding: 4px 6px;
  }}
  .rule-card h4 {{
    font-size: 7.1pt;
    color: #111111;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .rule-card p {{
    font-size: 6.65pt;
    color: #3f3f46;
  }}
  .section-bar {{
    background: #111111;
    color: #ffffff;
    padding: 3.5px 9px;
    border-left: 4px solid #dc2626;
    font-size: 8.3pt;
    font-weight: 800;
    margin: 4px 0 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    letter-spacing: 0.3px;
  }}
  .section-bar .sub {{
    font-size: 6.8pt;
    font-weight: 500;
    color: #fca5a5;
  }}
  .move-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
    margin-bottom: 4px;
  }}
  .move-card {{
    border: 1.2px solid #d4d4d8;
    padding: 4.5px 6px;
    background: #ffffff;
    display: flex;
    gap: 7px;
    align-items: stretch;
    page-break-inside: avoid;
  }}
  .move-card.highlight {{
    border: 1.4px solid #111111;
  }}
  .art-box {{
    width: 158px;
    flex-shrink: 0;
    border: 1px solid #a1a1aa;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}
  .art-top {{
    background: #f4f4f5;
    border-bottom: 1px solid #e4e4e7;
    color: #18181b;
    font-size: 5.5pt;
    font-weight: 800;
    text-align: center;
    padding: 2px 3px;
    letter-spacing: 0.2px;
  }}
  .art-img-wrap {{
    height: 102px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    padding: 3px;
  }}
  .art-img-wrap img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
  }}
  .art-cue {{
    background: #111111;
    color: #ffffff;
    font-size: 5.1pt;
    font-weight: 700;
    text-align: center;
    padding: 2px 3px;
    letter-spacing: 0.15px;
  }}
  .move-body {{
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .move-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2px;
    gap: 4px;
  }}
  .move-title-row h3 {{
    font-size: 7.7pt;
    font-weight: 800;
    color: #111111;
  }}
  .pill {{
    background: #111111;
    color: #ffffff;
    font-size: 6.0pt;
    font-weight: 700;
    padding: 1px 4.5px;
    white-space: nowrap;
  }}
  .pill.red {{ background: #dc2626; }}
  .pill.green {{ background: #15803d; }}
  .pill.blue {{ background: #1d4ed8; }}
  .move-body ul {{
    padding-left: 10px;
    font-size: 6.7pt;
    color: #27272a;
  }}
  .move-body li {{
    margin-bottom: 1.2px;
  }}
  .ladder-strip {{
    margin-top: 2px;
    padding: 2px 4px;
    background: #f4f4f5;
    border-left: 2.5px solid #111111;
    font-size: 6.2pt;
    color: #27272a;
  }}
  .good {{ color: #15803d; font-weight: 700; }}
  .bad {{ color: #b91c1c; font-weight: 700; }}
  .note-bar {{
    background: #fafafa;
    border: 1px solid #d4d4d8;
    border-left: 3.5px solid #dc2626;
    padding: 5px 8px;
    font-size: 6.9pt;
    color: #18181b;
    margin-top: 4px;
  }}
  .timeline-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.7pt;
    margin-bottom: 4px;
  }}
  .timeline-table th, .timeline-table td {{
    border: 1px solid #d4d4d8;
    padding: 2.2px 5px;
    text-align: left;
  }}
  .timeline-table th {{
    background: #18181b;
    color: #ffffff;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 6.3pt;
  }}
</style>
</head>
<body>

<!-- ==================== PAGE 1: OVERVIEW, WRIST PREP, HANDSTAND & CROW/CRANE ==================== -->
<div class="page">
  <div class="hero">
    <div>
      <h1>Sunday Skill &amp; Mobility Day — Visual Form Guide</h1>
      <p>Darebee &amp; GMB-Inspired Anatomical Line-Art Manual: Balance, Straight-Arm Strength, Compression &amp; Tendon Rehab</p>
    </div>
    <div class="hero-badge">
      <strong>Duration: 30–35 Minutes</strong><br>
      Intensity: <strong>Low CNS (2–3 RIR)</strong><br>
      Equipment: <strong>Floor, Wall, Bar</strong>
    </div>
  </div>

  <div class="rules-grid">
    <div class="rule-card">
      <h4>1. Purpose of Skill Day</h4>
      <p>Mon/Wed/Fri RR builds mechanical tension and Tue/Thu/Sat builds aerobic capacity. Sunday wires <strong>vestibular balance, straight-arm tendon resilience, and active joint mobility</strong> without taxing recovery.</p>
    </div>
    <div class="rule-card">
      <h4>2. Stop Before Shaking (2–3 RIR)</h4>
      <p>Balance is neurological. End every Handstand, Crow, or L-Sit hold <strong>2–3 seconds before form degrades</strong>. Clean holds wire balance; shaky holds wire bad motor patterns.</p>
    </div>
    <div class="rule-card">
      <h4>3. Timer-Based Blocks</h4>
      <p>Set a countdown timer (<strong>10 min Handstand</strong>, <strong>5 min Crow</strong>) and accumulate crisp <strong>15–30s holds</strong> with <strong>45–60s rest</strong> between attempts.</p>
    </div>
  </div>

  <table class="timeline-table">
    <thead>
      <tr>
        <th style="width:72px;">Block</th>
        <th style="width:62px;">Time</th>
        <th style="width:175px;">Exercise / Drill</th>
        <th>Your Current Active Level (from FIT Tracker)</th>
        <th style="width:125px;">Prescription</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Prep</strong></td>
        <td>0:00–0:05</td>
        <td>GMB Wrist Prep + Stick Dislocates</td>
        <td>Quadruped wrist rocks/pulses + 10 slow overhead pass-throughs</td>
        <td>10 reps each | Smooth</td>
      </tr>
      <tr>
        <td><strong>2. Inversion</strong></td>
        <td>0:05–0:15</td>
        <td>Chest-to-Wall Handstand &amp; Heel Pulls</td>
        <td><strong>L2/L3:</strong> Chest-to-Wall Hold + Finger-Brake Heel Pulls</td>
        <td>5–6 &times; 15–30s | 60s rest</td>
      </tr>
      <tr>
        <td><strong>3. Arm Bal</strong></td>
        <td>0:15–0:20</td>
        <td>Crow Pose &rarr; Straight-Arm Crane</td>
        <td><strong>L2:</strong> Crow Pose on floor (5 &times; 15–30s) &rarr; Crane</td>
        <td>4–5 &times; 15–30s | 45s rest</td>
      </tr>
      <tr>
        <td><strong>4. Core L</strong></td>
        <td>0:20–0:25</td>
        <td>Floor L-Sit + Seated Pike Leg Lifts</td>
        <td><strong>L1/L2:</strong> Foot-Supported / 1-Leg L-Sit + Pike Lifts</td>
        <td>60s total + 3 &times; 10s lifts</td>
      </tr>
      <tr>
        <td><strong>5. Bar Hang</strong></td>
        <td>0:25–0:29</td>
        <td>Skin the Cat &rarr; German Hang</td>
        <td>Tuck inversion through arms &rarr; controlled German Hang</td>
        <td>2–3 &times; 3–5 slow reps</td>
      </tr>
      <tr>
        <td><strong>6. Rehab</strong></td>
        <td>0:29–0:35</td>
        <td>Couch Stretch + Soleus / Ankle Iso</td>
        <td>Hip flexor unlock + <strong>Achilles/Ankle Tendonitis Rehab</strong></td>
        <td>60s/side + 3 &times; 30s iso</td>
      </tr>
    </tbody>
  </table>

  <div class="section-bar">
    <span>BLOCK 1: WRIST &amp; SHOULDER ARTICULAR PREP (5 MINUTES)</span>
    <span class="sub">Mandatory Before Handstands, Crow Pose &amp; Floor L-Sits</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["wrist_prep"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1A. GMB Quadruped Wrist Prep</h3>
            <span class="pill red">10 Reps &times; 4 Directions</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> On hands and knees, spread fingers wide and <strong>lock elbows 100% straight</strong> (bent elbows steal the stretch from the wrists).</li>
            <li><strong>4 Angles:</strong> (1) Forward shoulder rocks over fingertips; (2) First-knuckle palm heel lifts; (3) Fingers pointing backward toward knees; (4) Back-of-hand stretch.</li>
            <li><span class="good">&#10003; Goal:</span> Prepare wrist flexors and joint capsule for 90&deg;+ extension under load.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["yuri"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1B. Towel / Stick Shoulder Dislocates</h3>
            <span class="pill">10 Slow Reps</span>
          </div>
          <ul>
            <li><strong>100% Band-Free Option:</strong> Hold a broomstick, dowel, or bath towel pulled taut with a wide overhand grip.</li>
            <li><strong>Execution:</strong> Keep elbows locked straight, <strong>shrug shoulders up</strong> as arms pass overhead, and keep lower ribs tucked down (PPT) so your lower back never arches.</li>
            <li><span class="good">&#10003; Goal:</span> Opens chest and anterior shoulder capsule before Handstands and German Hangs.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>BLOCK 2: HANDSTAND &amp; OVERHEAD BALANCE PROGRESSION (10-MINUTE TIMER)</span>
    <span class="sub">Accumulate 5–6 Crisp Holds of 15–30s — Rest 60s Between Holds</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["handstand_wall"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>2A. Chest-to-Wall Handstand Hold</h3>
            <span class="pill red">5–6 &times; 15–30s</span>
          </div>
          <ul>
            <li><strong>Always Face the Wall:</strong> Walking feet up <strong>chest-to-wall</strong> enforces a straight hollow line (kicking up back-to-wall teaches a banana arch).</li>
            <li><strong>3 Key Cues:</strong> (1) Push floor away hard (<strong>elevate shoulders into ears</strong>); (2) Tuck tailbone (PPT) &amp; squeeze glutes; (3) Only tops of toes touch the wall.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: 45&deg; Wall Plank (60s) &rarr; L2: Chest-to-Wall (30s) &rarr; L3: Heel Pulls &rarr; L4: Freestanding</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["heel_pulls"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>2B. Wall Heel Pulls ("Finger Brakes")</h3>
            <span class="pill green">Freestanding Drill</span>
          </div>
          <ul>
            <li><strong>How Handstand Balance Works:</strong> Your fingertips act as your front brakes to stop over-balancing.</li>
            <li><strong>Execution:</strong> From Chest-to-Wall Handstand (hands 8 cm from wall), <strong>claw your fingertips hard into the floor</strong> with straight arms until your toes <strong>float 1–2 cm off the wall for 2–5 seconds</strong>.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Safety:</strong> Come down with 3–5s in reserve so you can walk down cleanly.</div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>BLOCK 3: CROW POSE &rarr; CRANE POSE PROGRESSION (5-MINUTE TIMER)</span>
    <span class="sub">Builds Wrist Endurance, Anterior Deltoid Strength &amp; Forward-Lean Control</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["crow"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>3A. Crow Pose / Frog Stand (Bent Arms)</h3>
            <span class="pill red">ACTIVE: L2 (5&times;15–30s)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Squat down, place palms shoulder-width apart with cambered fingers gripping the floor.</li>
            <li><strong>Execution:</strong> Rest knees on backs of triceps, bend elbows slightly to form a shelf, and lean shoulders forward while <strong>gazing 30 cm ahead on the floor</strong> until feet float up.</li>
            <li><span class="bad">&#10007; Fault:</span> Looking straight down or tucking chin causes you to somersault forward!</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["crane"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>3B. Crane Pose (Straight-Arm Bakasana)</h3>
            <span class="pill blue">Level 3–4 Upgrade</span>
          </div>
          <ul>
            <li><strong>What Changes in Crane:</strong> Tuck knees high into your armpits, <strong>lock elbows 100% straight</strong>, push upper back toward the ceiling (max scapular protraction), and drive hips high.</li>
            <li><strong>Transfer:</strong> Builds elite straight-arm scapular protraction for Planche leans and handstand presses.</li>
            <li><strong>Target:</strong> Once <strong>3 &times; 30s Crow</strong> is solid, practice <strong>5–10s straight-arm Crane holds</strong>.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 2: COMPRESSION, SKIN THE CAT & RUNNER'S TENDON REHAB ==================== -->
<div class="page">
  <div class="section-bar">
    <span>BLOCK 4: L-SIT &amp; ACTIVE PIKE COMPRESSION (5 MINUTES)</span>
    <span class="sub">Scapular Depression + Core / Hip-Flexor Compression Strength</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["lsit"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>4A. Floor L-Sit Progression Ladder</h3>
            <span class="pill red">60s Total Hold</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Sit tall with legs extended. Place palms flat on the floor (or on two books) beside your mid-thighs/hips.</li>
            <li><strong>Key Cue:</strong> Lock elbows straight and <strong>push shoulders DOWN hard away from ears</strong> (scapular depression) to float hips and legs off the floor.</li>
            <li><strong>Accumulate 60s total</strong> across sets (e.g., 4 &times; 15s or 3 &times; 20s).</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: Foot-Supported (60s) &rarr; L2: 1-Leg Assisted &rarr; L3: Tuck L-Sit &rarr; L4: Full L-Sit</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["pike_lift"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>4B. Seated Pike Compression Leg Lifts</h3>
            <span class="pill green">3 &times; 10s or 10 Reps</span>
          </div>
          <ul>
            <li><strong>Why It's Essential:</strong> Full L-Sits fail when your hip flexors (iliopsoas + rectus femoris) can't hold straight legs at a 90&deg; pike.</li>
            <li><strong>Execution:</strong> Sit in a pike, fold torso slightly forward, and place fingertips on the floor <strong>beside your knees/shins</strong>.</li>
            <li>Without leaning backward, lock knees, point toes, and lift both heels 5–10 cm off the floor for <strong>10 seconds</strong> (quad cramping is normal at first!).</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>BLOCK 5: SKIN THE CAT &amp; GERMAN HANG ON PULL-UP BAR (3–4 MINUTES)</span>
    <span class="sub">Bulletproofs Biceps Tendons, Pecs &amp; Anterior Shoulders in Full Extension</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["skin_tuck"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>5A. Skin the Cat Tuck Inversion</h3>
            <span class="pill red">2–3 &times; 3–5 Slow Reps</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Hang from pull-up bar with an <strong>overhand (pronated) grip</strong> and locked straight arms.</li>
            <li><strong>Execution:</strong> Depress scapulae, tuck knees tightly to chest, and press straight arms down to rotate backward through your arms.</li>
            <li><span class="good">&#10003; Strength Bonus:</span> Pulling out of the inverted tuck builds the exact straight-arm lat power needed for Front Levers.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["german_hang"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>5B. Controlled German Hang Stretch</h3>
            <span class="pill blue">3–5s Bottom Hold</span>
          </div>
          <ul>
            <li><strong>Descent:</strong> Once feet pass through your arms, slowly lower hips into shoulder extension while keeping <strong>elbows 100% locked</strong>.</li>
            <li><strong>Intensity Cap:</strong> Stop at a <strong>mild 5/10 stretch</strong> across your chest and biceps tendons (keep a chair/sofa under your feet for light support if needed).</li>
            <li>Tuck knees and pull hips back over to dead hang.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>BLOCK 6: RUNNER'S MOBILITY &amp; ANKLE TENDON REHAB (5–7 MINUTES)</span>
    <span class="sub">Unlocks Hip Extension &amp; Directly Rehabs Ankle / Achilles Tendons (Flagged Oct 22)</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["couch_stretch"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>6A. Kneeling Couch Stretch</h3>
            <span class="pill red">60s / Side</span>
          </div>
          <ul>
            <li><strong>Why Runners Need It:</strong> 25k steps/day + running + Step-Ups shorten the psoas and rectus femoris, pulling on the pelvis and lower back.</li>
            <li><strong>Setup:</strong> Place rear knee on a cushion at the base of a wall/sofa (shin vertical up the wall) and front foot in a 90&deg; lunge.</li>
            <li><strong>Key Cue:</strong> <strong>Tuck tailbone under (PPT) and squeeze the rear glute 100%</strong> BEFORE bringing torso upright. Hold 60s/side.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["ankle_rehab"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>6B. Soleus Wall Drive + Iso Tendon Hold</h3>
            <span class="pill green">Ankle Tendon Care</span>
          </div>
          <ul>
            <li><strong>1. Bent-Knee Soleus Stretch (60s/side):</strong> Foot 8–10 cm from wall; drive bent knee toward wall with heel flat on floor to release deep soleus tension.</li>
            <li><strong>2. Isometric Calf/Ankle Hold (3 &times; 30s/side):</strong> Irritated ankle tendons (flagged Oct 22) dislike fast bouncing, but <strong>30-second mid-range isometric heel-raise holds</strong> provide immediate tendon analgesia and stimulate collagen stiffening.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="note-bar">
    <strong>Sunday Session Checklist (~32 mins total):</strong>
    (1) <strong>Wrist &amp; Stick Prep</strong> 5m &rarr;
    (2) <strong>Chest-to-Wall Handstand &amp; Heel Pulls</strong> 10m timer &rarr;
    (3) <strong>Crow / Crane Pose</strong> 5m timer &rarr;
    (4) <strong>L-Sit (60s total) + Pike Lifts (3&times;10s)</strong> 5m &rarr;
    (5) <strong>Skin the Cat / German Hang</strong> 2–3&times;3–5 reps &rarr;
    (6) <strong>Couch Stretch + 3&times;30s Ankle Tendon Iso Holds</strong> 5m.
  </div>
</div>

</body>
</html>
"""


def main(html_only=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_DOC)
    print(f"Wrote {HTML_PATH}")
    if html_only:
        return

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    for pdf_out in (PDF_PATH_GEN, PDF_PATH_ROOT):
        cmd = [
            chrome_bin,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={pdf_out}",
            "--no-pdf-header-footer",
            f"file://{HTML_PATH}",
        ]
        subprocess.run(cmd, check=True)
        print(f"Generated {pdf_out} ({os.path.getsize(pdf_out)} bytes)")


if __name__ == "__main__":
    main(html_only="--html-only" in sys.argv)
