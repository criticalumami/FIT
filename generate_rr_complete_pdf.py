#!/usr/bin/env python3
"""
Generate the complete Darebee & GMB-inspired Recommended Routine (RR) + Skill Day
Visual Form & Progression Manual (generated/RR_Complete_Form_Guide.pdf & RR_Complete_Form_Guide.pdf).
`--html-only` skips the PDF step (used by CI).
Uses clean black-and-white anatomical ink line-art illustrations from assets/art/.
"""
import base64
import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(DIR, "generated")
ART_DIR = os.path.join(DIR, "assets", "art")
HTML_PATH = os.path.join(OUT_DIR, "rr_complete_form_guide.html")
PDF_PATH_GEN = os.path.join(OUT_DIR, "RR_Complete_Form_Guide.pdf")
PDF_PATH_ROOT = os.path.join(DIR, "RR_Complete_Form_Guide.pdf")


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


def dual_img_card(file_left, file_right, label_top, cue_bottom):
    """Embed two sequential Darebee-style anatomical poses side-by-side in one card."""
    p1 = os.path.join(ART_DIR, file_left)
    p2 = os.path.join(ART_DIR, file_right)
    with open(p1, "rb") as f1, open(p2, "rb") as f2:
        b1 = base64.b64encode(f1.read()).decode("ascii")
        b2 = base64.b64encode(f2.read()).decode("ascii")
    return f"""
    <div class="art-box">
      <div class="art-top">{label_top}</div>
      <div class="art-img-wrap dual">
        <img src="data:image/jpeg;base64,{b1}" alt="{label_top} Start">
        <div class="art-divider"></div>
        <img src="data:image/jpeg;base64,{b2}" alt="{label_top} Finish">
      </div>
      <div class="art-cue">{cue_bottom}</div>
    </div>
    """


CARDS = {
    # Page 1: Body Mechanics & Warm-Up
    "hollow": img_card("warmup_hollow.jpg", "0A. HOLLOW BODY HOLD (PPT)", "TUCK TAILBONE — CRUSH LOWER BACK FLAT"),
    "scapula": img_card("pull_hang.jpg", "0B. ACTIVE SCAPULAR HANG", "DEPRESS SHOULDERS DOWN AWAY FROM EARS"),
    "dislocate": img_card("warmup_dislocate.jpg", "W1. STICK / TOWEL DISLOCATES", "ELBOWS LOCKED — SHRUG UP OVERHEAD"),
    "sky_reach": img_card("warmup_sky_reach.jpg", "W2. SQUAT SKY REACHES", "DEEP SQUAT — ROTATE CHEST TO CEILING"),
    "wrist_prep": img_card("warmup_wrist.jpg", "W3. GMB QUADRUPED WRIST PREP", "ELBOWS STRAIGHT — ROCK OVER FINGERS"),
    "support_hold": img_card("dip_bar.jpg", "W4. PARALLEL BAR SUPPORT HOLD", "LOCK ELBOWS — DEPRESS SHOULDERS 30–60s"),

    # Page 2: Pair 1 (Pull + Squat) & Pair 2 (Dip + Hinge)
    "pull_foundation": img_card("pull_hang.jpg", "1A-1. ARCH HANG & NEGATIVES", "RETRACT SCAPULAE & 5–10s SLOW DESCENT"),
    "pull_main": img_card("pull_up.jpg", "1A-2. STRICT PULL-UP / CHIN-UP", "DEAD HANG TO CHIN OVER BAR — ELBOWS DOWN"),
    "squat_split": img_card("squat_split.jpg", "1B-1. STEP-UP & SPLIT SQUAT", "ZERO BACK-LEG PUSH — 3s ECCENTRIC"),
    "squat_pistol": img_card("squat_pistol.jpg", "1B-2. SHRIMP & PISTOL SQUAT", "KNEE TRACKS OVER TOES — FULL DEPTH"),
    "dip_main": img_card("dip_bar.jpg", "2A. PARALLEL BAR DIPS (3×5–8)", "SLIGHT FORWARD LEAN — DESCEND TO 90°"),
    "hinge_slide": img_card("hinge_slide.jpg", "2B-1. FLOOR SLIDE HAMSTRING CURL", "HIPS EXTENDED IN PPT — SLIDE & CURL HEELS"),
    "hinge_rdl": img_card("hinge_rdl.jpg", "2B-2. SINGLE-LEG RDL HINGE", "FLAT BACK T-SHAPE — HINGE AT HIPS"),

    # Page 3: Pair 3 (Row + Push) & Core Triplet
    "row_progression": dual_img_card("row_hang.jpg", "row_top.jpg", "3A. INVERTED ROW (1. HANG → 2. PULL)", "RIGID PLANK LINE — PULL BAR TO LOWER CHEST"),
    "push_diamond": img_card("push_diamond.jpg", "3B-1. STANDARD → DIAMOND PUSH-UP", "ELBOWS TUCKED 30–45° — HOLLOW CORE"),
    "push_pppu": img_card("push_pppu.jpg", "3B-2. PSEUDO PLANCHE PUSH-UP", "LEAN SHOULDERS AHEAD OF WRISTS — PROTRACT"),
    "core_plank": img_card("core_plank.jpg", "C1. HOLLOW FOREARM PLANK (2×30–60s)", "POSTERIOR PELVIC TILT — SQUEEZE GLUTES"),
    "core_side": img_card("core_side_plank.jpg", "C2. SIDE PLANK → COPENHAGEN (2×15–45s)", "STACK HIPS & SHOULDERS — NO SAG"),
    "core_arch": img_card("core_arch.jpg", "C3. ARCH HOLD / REV HYPER (2×8–12)", "LIFT WITH GLUTES & SPINAL ERECTORS"),

    # Page 4: Sunday Skill & Mobility Day
    "skill_hs": dual_img_card("skill_handstand.jpg", "skill_heel_pull.jpg", "S1. CHEST-TO-WALL & HEEL PULLS", "ELEVATE SHOULDERS — CLAW FINGERS TO FLOAT"),
    "skill_crow": dual_img_card("skill_crow.jpg", "skill_crane.jpg", "S2. CROW (BENT) → CRANE (STRAIGHT)", "GAZE 30 CM AHEAD — PROTRACT SCAPULAE"),
    "skill_lsit": dual_img_card("skill_lsit.jpg", "skill_pike.jpg", "S3. FLOOR L-SIT & PIKE LIFTS", "DEPRESS SHOULDERS — COMPRESS HIP FLEXORS"),
    "skill_stc": dual_img_card("skill_skinthecat.jpg", "skill_germanhang.jpg", "S4. SKIN THE CAT → GERMAN HANG", "ELBOWS 100% LOCKED — MILD 5/10 STRETCH"),
    "rehab_couch": img_card("rehab_couch.jpg", "S5-A. KNEELING COUCH STRETCH", "TUCK PELVIS (PPT) & SQUEEZE REAR GLUTE 60s"),
    "rehab_ankle": img_card("rehab_ankle.jpg", "S5-B. SOLEUS + ISO ANKLE HOLD", "60s SOLEUS DRIVE + 3×30s ISO CALF HOLD"),
}


HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>/r/bodyweightfitness Recommended Routine &amp; Skill Day — Illustrated Form Manual</title>
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
    max-width: 980px;
    margin: 0 auto;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  @media screen {{
    body {{
      padding: 16px;
      background: #f4f4f5;
    }}
    .page {{
      background: #ffffff;
      border: 1px solid #d4d4d8;
      padding: 16px;
      margin-bottom: 18px;
    }}
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
    font-size: 12.6pt;
    font-weight: 900;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .hero p {{
    font-size: 7.3pt;
    color: #d4d4d8;
  }}
  .hero-badge {{
    background: #27272a;
    border: 1px solid #52525b;
    border-left: 3px solid #dc2626;
    padding: 4px 9px;
    text-align: right;
    font-size: 6.8pt;
    line-height: 1.3;
    white-space: nowrap;
  }}
  .hero-badge strong {{
    color: #f87171;
    font-size: 7.4pt;
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
    font-size: 7.0pt;
    color: #111111;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .rule-card p {{
    font-size: 6.6pt;
    color: #3f3f46;
  }}
  .section-bar {{
    background: #111111;
    color: #ffffff;
    padding: 3.5px 9px;
    border-left: 4px solid #dc2626;
    font-size: 8.2pt;
    font-weight: 800;
    margin: 4px 0 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    letter-spacing: 0.3px;
  }}
  .section-bar .sub {{
    font-size: 6.7pt;
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
  .move-card.span-2 {{
    grid-column: span 2;
  }}
  .art-box {{
    width: 156px;
    flex-shrink: 0;
    border: 1px solid #a1a1aa;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}
  .move-card.span-2 .art-box {{
    width: 240px;
  }}
  .art-top {{
    background: #f4f4f5;
    border-bottom: 1px solid #e4e4e7;
    color: #18181b;
    font-size: 5.4pt;
    font-weight: 800;
    text-align: center;
    padding: 2px 3px;
    letter-spacing: 0.2px;
  }}
  .art-img-wrap {{
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    padding: 3px;
  }}
  .art-img-wrap.dual {{
    gap: 4px;
  }}
  .art-img-wrap.dual img {{
    max-width: 48%;
    max-height: 100%;
  }}
  .art-divider {{
    width: 1px;
    height: 82%;
    border-left: 1px dashed #d4d4d8;
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
    font-size: 5.0pt;
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
    font-size: 7.6pt;
    font-weight: 800;
    color: #111111;
  }}
  .pill {{
    background: #111111;
    color: #ffffff;
    font-size: 5.9pt;
    font-weight: 700;
    padding: 1px 4.5px;
    white-space: nowrap;
  }}
  .pill.red {{ background: #dc2626; }}
  .pill.green {{ background: #15803d; }}
  .pill.blue {{ background: #1d4ed8; }}
  .move-body ul {{
    padding-left: 10px;
    font-size: 6.65pt;
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
    font-size: 6.15pt;
    color: #27272a;
  }}
  .good {{ color: #15803d; font-weight: 700; }}
  .bad {{ color: #b91c1c; font-weight: 700; }}
  .note-bar {{
    background: #fafafa;
    border: 1px solid #d4d4d8;
    border-left: 3.5px solid #dc2626;
    padding: 4.5px 8px;
    font-size: 6.8pt;
    color: #18181b;
    margin-top: 4px;
  }}
</style>
</head>
<body>

<!-- ==================== PAGE 1: RULES, BODY MECHANICS & DYNAMIC WARM-UP ==================== -->
<div class="page">
  <div class="hero">
    <div>
      <h1>Recommended Routine (RR) — Illustrated Form &amp; Progression Manual</h1>
      <p>100% Bodyweight-Only Edition (Zero Barbells / Zero Bands) — Darebee &amp; Overcoming Gravity Line-Art</p>
    </div>
    <div class="hero-badge">
      <strong>Mon / Wed / Fri: Full RR</strong><br>
      Tempo: <strong>1-0-X-0</strong> | Rest: <strong>90s Pairs</strong><br>
      Sets: <strong>3&times;5–8 / 3&times;8–12 (1 RIR)</strong>
    </div>
  </div>

  <div class="rules-grid">
    <div class="rule-card">
      <h4>1. Alternating Pair Protocol (90s Rest)</h4>
      <p><strong>Pairs 1–3:</strong> Perform Set 1 of Exercise A &rarr; Rest 90s &rarr; Set 1 of Exercise B &rarr; Rest 90s &rarr; Repeat for 3 sets. Gives each muscle group <strong>3+ minutes of local recovery</strong> in half the time.</p>
    </div>
    <div class="rule-card">
      <h4>2. Tempo (10X0) &amp; 1 Rep in Reserve</h4>
      <p><strong>1–2s</strong> controlled lowering, <strong>0s</strong> bounce, <strong>X</strong> explosive drive up, <strong>0s</strong> reset. Stop <strong>1 rep short of failure</strong> on Sets 1–2 so you hit clean volume across all 3 sets.</p>
    </div>
    <div class="rule-card">
      <h4>3. Double Progression Rule</h4>
      <p>Start a variation at <strong>3&times;5</strong> (or 3&times;8 for hinges/rows). Add <strong>+1 rep per session</strong> (5,4,4 &rarr; 5,5,4 &rarr; ... &rarr; 8,8,8). Once you hit the top of the range on all 3 sets, advance to the next level.</p>
    </div>
  </div>

  <div class="section-bar">
    <span>PART 0: FUNDAMENTAL BODY MECHANICS (REQUIRED ON EVERY REP)</span>
    <span class="sub">Hollow Body Pelvis Lock (PPT) &amp; Active Scapular Control</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["hollow"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>0A. Hollow Body &amp; Posterior Pelvic Tilt (PPT)</h3>
            <span class="pill red">Core &amp; Spine Lock</span>
          </div>
          <ul>
            <li><strong>How to Lock In:</strong> Tuck your tailbone under (pull belt buckle toward chin), squeeze glutes 100%, and draw lower ribs down into abs.</li>
            <li><strong>Deadbug Warm-Up (30s):</strong> Lie supine, press lower back flat into floor with zero gap, and slowly extend opposite arm/leg.</li>
            <li><span class="bad">&#10007; Fault:</span> Banana-back arch on Push-Ups, Planks, Pull-Ups, or Handstands.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["scapula"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>0B. Active Scapular Control (4 Positions)</h3>
            <span class="pill red">Shoulder Armor</span>
          </div>
          <ul>
            <li><strong>Depress (Pull Down):</strong> Pull shoulders away from ears (Pull-Ups, Dips, Support Hold, L-Sit).</li>
            <li><strong>Retract (Pinch Back):</strong> Pinch blades together (top of Rows, Arch Hangs).</li>
            <li><strong>Protract (Push Apart):</strong> Spread blades wide (top of Push-Ups, Plank, Crane).</li>
            <li><strong>Elevate (Shrug Up):</strong> Push floor away into ears (Handstands).</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>PART 1: DYNAMIC WARM-UP SEQUENCE (5–8 MINUTES BEFORE EVERY RR SESSION)</span>
    <span class="sub">100% Equipment-Free / Towel &amp; Bar Prep</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {CARDS["dislocate"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>W1. Towel / Stick Shoulder Dislocates</h3>
            <span class="pill">10 Slow Reps</span>
          </div>
          <ul>
            <li>Hold a broomstick or bath towel pulled taut with a wide overhand grip.</li>
            <li>Keep <strong>elbows 100% locked straight</strong>, shrug shoulders up as arms pass overhead, and keep ribs tucked down.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["sky_reach"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>W2. Squat Sky Reaches (Thoracic &amp; Hips)</h3>
            <span class="pill">10 Reps / Side</span>
          </div>
          <ul>
            <li>Drop into a deep bodyweight squat with heels flat on the floor.</li>
            <li>Grab one ankle/instep with one hand, use the elbow to pry the knee out, and <strong>rotate the other arm straight up to the ceiling</strong>, following your hand with your eyes.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["wrist_prep"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>W3. GMB Quadruped Wrist Prep</h3>
            <span class="pill red">10 Reps &times; 4 Ways</span>
          </div>
          <ul>
            <li>On hands and knees with <strong>elbows locked straight</strong>, spread fingers wide.</li>
            <li>Perform 10 gentle rocks in 4 positions: (1) Fingers forward; (2) First-knuckle palm pulses; (3) Fingers pointing back toward knees; (4) Back-of-hand stretch.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["support_hold"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>W4. Parallel Bar Support Hold (+ 8 Arch Hangs)</h3>
            <span class="pill red">30–60s Hold</span>
          </div>
          <ul>
            <li>Press up to locked arms on parallel dip bars (or two sturdy chairs).</li>
            <li><strong>Push shoulders down hard away from ears</strong> (active depression), lock elbows, and hold a hollow body for 30–60s. Pair with <strong>8–10 Scapular Arch Hangs</strong> on the pull-up bar.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 2: STRENGTH PAIR 1 (PULL + SQUAT) & PAIR 2 (DIP + HINGE) ==================== -->
<div class="page">
  <div class="section-bar">
    <span>PAIR 1: PULL-UP PROGRESSION (3&times;5–8) + SQUAT PROGRESSION (3&times;5–8 /LEG)</span>
    <span class="sub">Alternate Pull Set &rarr; 90s Rest &rarr; Squat Set &rarr; 90s Rest (3 Rounds)</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {CARDS["pull_foundation"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1A (L1–L3). Scapular Pulls, Arch Hangs &amp; Negatives</h3>
            <span class="pill">Levels 1–3</span>
          </div>
          <ul>
            <li><strong>L1–L2 (Scapular Pull / Arch Hang):</strong> From dead hang with straight arms, pull shoulders down and arch upper back toward bar (3&times;8).</li>
            <li><strong>L3 (Pull-Up Negatives):</strong> Jump/step chin over bar and lower for a <strong>strict, even 5–10 second eccentric</strong> all the way to dead hang (3&times;5).</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["pull_main"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1A (L4–L6). Strict Pull-Ups &rarr; L-Sit Pull-Ups</h3>
            <span class="pill red">ACTIVE: L4 (3&times;5–8)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Overhand grip slightly wider than shoulders, starting from a <strong>100% straight-arm dead hang</strong>.</li>
            <li><strong>Execution:</strong> Depress scapulae first, drive elbows down toward your ribs until chin clears the bar, and lower under control (1–2s) to full lockout.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: Scap Pulls &rarr; L2: Arch Hangs &rarr; L3: Negatives &rarr; <strong>L4: Pull-Ups</strong> &rarr; L5: L-Sit PU &rarr; L6: Archer PU</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["squat_split"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1B (L1–L4). Single-Leg Sofa Step-Up &amp; Split Squat</h3>
            <span class="pill red">ACTIVE: L3 (3&times;5–8/leg)</span>
          </div>
          <ul>
            <li><strong>L3 (Single-Leg Sofa Step-Up):</strong> Place working foot on sofa/box, lean torso slightly forward, and <strong>pull rear toes up (dorsiflex)</strong> so you cannot bounce off the back calf. Lower for a <strong>3-second eccentric</strong>.</li>
            <li><strong>L4 (Bulgarian Split Squat):</strong> Elevate rear laces on sofa, descend until rear knee kisses floor, and drive up through front heel.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L2: BW Squat &rarr; <strong>L3: Sofa Step-Up</strong> &rarr; L4: Bulgarian Split Squat &rarr; L5: Shrimp &rarr; L6: Pistol</div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["squat_pistol"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>1B (L5–L6). Shrimp Squat &amp; Single-Leg Pistol Squat</h3>
            <span class="pill blue">Levels 5–6</span>
          </div>
          <ul>
            <li><strong>L5 (Shrimp Squat):</strong> Hold rear ankle behind hip (or keep shin horizontal in air); descend on front leg until rear knee and toes lightly kiss the floor together.</li>
            <li><strong>L6 (Pistol Squat):</strong> Extend non-working leg straight in front, reach arms forward for counterbalance, and squat to full depth on one leg.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>PAIR 2: DIP PROGRESSION (3&times;5–8) + BODYWEIGHT HINGE PROGRESSION (3&times;8–12)</span>
    <span class="sub">Alternate Dip Set &rarr; 90s Rest &rarr; Hinge Set &rarr; 90s Rest (3 Rounds)</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight span-2">
      {CARDS["dip_main"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>2A (L1–L5). Parallel Bar Dips Progression (100% Bodyweight)</h3>
            <span class="pill red">ACTIVE: L3 Parallel Dips (3&times;5–8)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Start in locked-out support on parallel bars with shoulders depressed (long neck) and legs held tight in a hollow body.</li>
            <li><strong>Execution:</strong> Lean torso slightly forward (~15–20&deg;), tuck elbows back (~45&deg; max flare), and lower under control until your <strong>shoulder crease reaches at least elbow height (90&deg;)</strong>. Press explosively back to full lockout.</li>
            <li><span class="bad">&#10007; Avoid:</span> Shrugging shoulders into ears, flaring elbows out 90&deg;, or cutting reps above parallel.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: 60s Support Hold &rarr; L2: Negative Dips (5–8s eccentric) &rarr; <strong>L3: Parallel Bar Dips</strong> &rarr; L4: L-Sit / 2s Pause Dips &rarr; L5: Ring Dips</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["hinge_slide"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>2B (L3–L5). Floor Slide Hamstring Curl</h3>
            <span class="pill red">ACTIVE: L3 (3&times;8–12)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Lie supine with heels on sliders, wool socks, or a towel on a smooth floor.</li>
            <li><strong>Execution:</strong> Tuck pelvis (PPT), bridge hips up into a straight line from shoulders to knees, and <strong>slide heels out and curl back in</strong> without letting hips sag toward the floor.</li>
            <li><strong>L4 Upgrade:</strong> Slide out on <strong>1 leg (4s eccentric)</strong>, curl back with 2 legs.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: Single-Leg RDL &rarr; L2: Glute Bridge &rarr; <strong>L3: Floor Slide Curl</strong> &rarr; L4: 2-Up/1-Down Slide &rarr; L6: Nordic Curl</div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["hinge_rdl"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>2B (L1 &amp; L6). Single-Leg RDL &amp; Nordic Curl</h3>
            <span class="pill green">Warm-Up / Level 6</span>
          </div>
          <ul>
            <li><strong>Single-Leg RDL (Balance &amp; Hip Hinge):</strong> Keep standing knee softly unlocked (15&deg;), hinge hips backward while extending rear leg straight back into a rigid horizontal T-shape with squared hips.</li>
            <li><strong>L6 (Nordic Hamstring Curl):</strong> Anchor ankles under a heavy sofa; keep hips locked extended and lower torso slowly toward floor using pure hamstring tension.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 3: STRENGTH PAIR 3 (ROW + PUSH-UP) & CORE TRIPLET ==================== -->
<div class="page">
  <div class="section-bar">
    <span>PAIR 3: INVERTED ROW PROGRESSION (3&times;8–12) + PUSH-UP PROGRESSION (3&times;5–8)</span>
    <span class="sub">Alternate Row Set &rarr; 90s Rest &rarr; Push-Up Set &rarr; 90s Rest (3 Rounds)</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight span-2">
      {CARDS["row_progression"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>3A (L1–L5). Horizontal &amp; Feet-Elevated Inverted Rows</h3>
            <span class="pill red">ACTIVE: L2 Horizontal Rows (3&times;8–12)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Hang underneath a waist-high bar, sturdy table, or rings with heels on the floor (L2) or elevated on a sofa/chair (L3).</li>
            <li><strong>Execution:</strong> Squeeze glutes and abs to form a <strong>rigid straight plank from ankles to shoulders</strong>. Pull your lower chest/upper abs to the bar while <strong>retracting shoulder blades together</strong> (1-second pause at top), then lower to full arm extension.</li>
            <li><span class="bad">&#10007; Avoid:</span> Letting hips sag, piking hips up with momentum, or jutting chin forward to reach the bar.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: Incline Row (45&deg;) &rarr; <strong>L2: Horizontal Row</strong> &rarr; L3: Feet-Elevated Row &rarr; L4: Wide / Tuck Front Lever Row &rarr; L5: Archer Row</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["push_diamond"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>3B (L2–L4). Standard &rarr; Diamond Push-Ups</h3>
            <span class="pill red">ACTIVE: L3 Diamond (3&times;5–8)</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Place index fingers and thumbs together (or 2–3 cm apart) directly under your sternum; lock pelvis in <strong>posterior pelvic tilt (PPT)</strong>.</li>
            <li><strong>Execution:</strong> Keep elbows tracking back at <strong>30–45&deg; along your ribs</strong> (never flared 90&deg; sideways). Lower until chest touches hands, then press to full lockout with <strong>scapular protraction</strong> at the top.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: Incline PU &rarr; L2: Full Push-Up &rarr; <strong>L3: Diamond Push-Up</strong> &rarr; L4: Decline Diamond &rarr; L5: PPPU</div>
      </div>
    </div>

    <div class="move-card">
      {CARDS["push_pppu"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>3B (L5–L6). Pseudo Planche Push-Up (PPPU)</h3>
            <span class="pill blue">Levels 5–6</span>
          </div>
          <ul>
            <li><strong>Setup:</strong> Turn fingers 45–90&deg; outward (or backward) and <strong>lean your shoulders 15–25 cm forward ahead of your wrists</strong>.</li>
            <li><strong>Execution:</strong> Maintain that exact forward shoulder lean at both the bottom and top of every rep, finishing with a strong protracted hollow upper back.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="section-bar">
    <span>PART 3: CORE TRIPLET — ANTI-EXTENSION + ANTI-ROTATION + EXTENSION (2 SETS)</span>
    <span class="sub">Circuit: Core 1 &rarr; 60s Rest &rarr; Core 2 &rarr; 60s Rest &rarr; Core 3 &rarr; 60s Rest (2 Rounds)</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {CARDS["core_plank"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Core 1 (Anti-Ext): Hollow Forearm Plank</h3>
            <span class="pill red">ACTIVE: 2 &times; 30–60s</span>
          </div>
          <ul>
            <li><strong>Not a Passive Rest Plank:</strong> Tuck tailbone hard (PPT), squeeze glutes + quads 100%, protract shoulder blades, and pull elbows metaphorically toward your toes.</li>
            <li><strong>L2–L4 Upgrades:</strong> Walk elbows 10 cm ahead of eyes (<strong>Long-Lever Plank</strong>) &rarr; Plank Towel Slide-Outs &rarr; Standing Ab Walkouts.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["core_side"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Core 2 (Anti-Rot): Side Plank &rarr; Copenhagen</h3>
            <span class="pill red">ACTIVE: 2 &times; 15–45s/side</span>
          </div>
          <ul>
            <li><strong>L1 (Stacked Side Plank):</strong> Elbow directly under shoulder, feet stacked, drive bottom hip high and squeeze glutes so body forms a straight line.</li>
            <li><strong>L3 (Copenhagen Plank on Sofa):</strong> Rest top foot/ankle on your sofa seat and lift bottom leg off the floor — builds elite adductor &amp; oblique stability for running!</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight span-2">
      {CARDS["core_arch"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Core 3 (Extension): Prone Arch Hold &amp; Sofa Reverse Hyperextension</h3>
            <span class="pill red">ACTIVE: 2 &times; 8–12 Reps</span>
          </div>
          <ul>
            <li><strong>Path A (Sofa Reverse Hyperextension):</strong> Lie prone on your sofa/bed with your hip crease right at the edge and grip the frame firmly. Squeeze glutes and spinal erectors to lift straight legs to horizontal (1s pause at top), then lower under control.</li>
            <li><strong>Path B (Prone Arch Hold / Superman on Floor):</strong> Lie face down on the floor, lock knees, point toes, and lift chest, straight arms, and thighs off the floor so only your belly rests on the mat (2 &times; 30s hold or 8–12 dynamic raises with 2s top hold).</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 4: SUNDAY SKILL & MOBILITY DAY ==================== -->
<div class="page">
  <div class="section-bar">
    <span>PART 4: SUNDAY SKILL &amp; MOBILITY DAY ROUTINE (30–35 MINUTES — LOW CNS)</span>
    <span class="sub">Stop 2–3 Seconds Before Shaking — Motor Control, Straight-Arm Strength &amp; Runner Tendon Rehab</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight span-2">
      {CARDS["skill_hs"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Skill 1 (10-Min Timer): Chest-to-Wall Handstand &amp; Wall Heel Pulls</h3>
            <span class="pill red">5–6 &times; 15–30s (60s Rest)</span>
          </div>
          <ul>
            <li><strong>Chest-to-Wall Setup:</strong> Walk feet up the wall facing the wall until hands are 5–10 cm from the baseboard (never kick up back-to-wall).</li>
            <li><strong>3 Non-Negotiable Cues:</strong> (1) Push floor away hard (<strong>elevate shoulders into ears</strong>); (2) Lock pelvis in <strong>PPT</strong>; (3) Press fingertips into the floor ("finger brakes") so your toes float 1–2 cm off the wall for 2–5s at a time.</li>
          </ul>
        </div>
        <div class="ladder-strip"><strong>Ladder:</strong> L1: 45&deg; Wall Plank (60s) &rarr; <strong>L2: Chest-to-Wall Hold</strong> &rarr; L3: Wall Heel Pulls &rarr; L4: Freestanding Handstand</div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["skill_crow"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Skill 2 (5-Min Timer): Crow &rarr; Crane Pose</h3>
            <span class="pill red">4–5 &times; 15–30s</span>
          </div>
          <ul>
            <li><strong>Crow (Bent Arms):</strong> Rest knees on backs of triceps, grip floor with cambered fingers, and <strong>gaze 30 cm ahead on the floor</strong> until toes float up.</li>
            <li><strong>Crane (Straight Arms):</strong> Tuck knees into armpits, <strong>lock elbows 100% straight</strong>, and protract shoulder blades hard.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["skill_lsit"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Skill 3 (5 Min): Floor L-Sit &amp; Pike Compression</h3>
            <span class="pill red">60s Total + 3&times;10s</span>
          </div>
          <ul>
            <li><strong>Floor L-Sit (60s total):</strong> Palms beside hips, lock elbows, and <strong>push shoulders DOWN hard</strong> (Foot-Supported &rarr; 1-Leg &rarr; Tuck &rarr; Full L-Sit).</li>
            <li><strong>Seated Pike Leg Lifts (3&times;10s):</strong> Hands on floor past knees; lift locked straight legs without leaning backward.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight span-2">
      {CARDS["skill_stc"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Skill 4 (3–4 Min): Skin the Cat &amp; Controlled German Hang</h3>
            <span class="pill blue">2–3 &times; 3–5 Slow Reps</span>
          </div>
          <ul>
            <li><strong>Tuck Inversion:</strong> Hang from pull-up bar with overhand grip and locked straight arms. Depress scapulae, tuck knees to chest, and roll backward through your arms.</li>
            <li><strong>German Hang Stretch:</strong> Slowly lower hips into shoulder extension while keeping <strong>elbows 100% locked straight</strong>. Pause 3–5s at a mild 5/10 chest &amp; biceps-tendon stretch, then pull back over to dead hang.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["rehab_couch"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Mobility 5A: Kneeling Couch Stretch</h3>
            <span class="pill green">60s / Side</span>
          </div>
          <ul>
            <li>Rear knee on cushion at base of sofa/wall (shin vertical up wall), front foot in 90&deg; lunge.</li>
            <li><strong>Tuck tailbone under (PPT) and squeeze rear glute 100%</strong> before bringing torso upright to unlock psoas &amp; rectus femoris.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="move-card highlight">
      {CARDS["rehab_ankle"]}
      <div class="move-body">
        <div>
          <div class="move-title-row">
            <h3>Mobility 5B: Soleus Drive + Iso Ankle Hold</h3>
            <span class="pill green">Ankle Tendon Care</span>
          </div>
          <ul>
            <li><strong>1. Bent-Knee Soleus Wall Stretch (60s/side):</strong> Drive bent knee over toes toward wall with heel glued flat.</li>
            <li><strong>2. Isometric Calf/Ankle Hold (3&times;30s/side):</strong> Hold mid-range single-leg heel raise rock-steady for 30s to calm irritated ankle tendons and stiffen collagen.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="note-bar">
    <strong>Complete Weekly Schedule:</strong>
    <strong>Mon / Wed / Fri:</strong> Full RR (Warm-Up + Pairs 1–3 + 2x Core Triplet) &nbsp;|&nbsp;
    <strong>Tue:</strong> 7–8 km Easy Zone 2 Run (&lt;148 bpm) + Strides &nbsp;|&nbsp;
    <strong>Thu:</strong> 8–9 km Tempo Run (155–165 bpm) &nbsp;|&nbsp;
    <strong>Sat:</strong> 10–12 km Long Run (&le;155 bpm) &nbsp;|&nbsp;
    <strong>Sun:</strong> Skill &amp; Mobility Day (30–35m).
  </div>
</div>

</body>
</html>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"Wrote {HTML_PATH}")
    if "--html-only" in sys.argv:
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
    main()
