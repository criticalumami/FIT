#!/usr/bin/env python3
"""
Generate the complete, Darebee-inspired Recommended Routine (RR) Form & Instruction PDF
(`RR_Complete_Form_Guide.pdf` and `RR_Form_Guide.pdf`).
Features custom anatomical multi-frame Darebee-style vector illustrations (Start & End pose
in each panel), muscle-engagement highlights, directional motion arrows, and complete
instructions for every RR exercise and alternate pathway.
"""
import math
import os
import shutil
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(DIR, "rr_complete_form_guide.html")
PDF_PATH = os.path.join(DIR, "RR_Complete_Form_Guide.pdf")
PDF_ALIAS_PATH = os.path.join(DIR, "RR_Form_Guide.pdf")


def capsule(x1, y1, x2, y2, r1, r2, fill="#cbd5e1", stroke="#0f172a", sw=1.2):
    """Render an anatomical tapered limb/torso capsule between (x1,y1) and (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-3:
        return f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{max(r1,r2):.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    nx, ny = -dy / L, dx / L
    p1x, p1y = x1 + nx * r1, y1 + ny * r1
    p2x, p2y = x2 + nx * r2, y1 + dy + ny * r2
    p3x, p3y = x2 - nx * r2, y1 + dy - ny * r2
    p4x, p4y = x1 - nx * r1, y1 - ny * r1
    return (
        f'<path d="M {p1x:.1f} {p1y:.1f} L {p2x:.1f} {p2y:.1f} '
        f'A {r2:.1f} {r2:.1f} 0 0 1 {p3x:.1f} {p3y:.1f} '
        f'L {p4x:.1f} {p4y:.1f} A {r1:.1f} {r1:.1f} 0 0 1 {p1x:.1f} {p1y:.1f} Z" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
    )


def athlete_side(
    head,
    shoulder,
    hip,
    knee,
    ankle,
    elbow,
    hand,
    foot=None,
    knee2=None,
    ankle2=None,
    foot2=None,
    elbow2=None,
    hand2=None,
    mid_spine=None,
    scale=0.82,
    skin="#cbd5e1",
    shirt="#94a3b8",
    shorts="#1e293b",
    active_muscle=None,
    opacity=1.0,
):
    """
    Draw a clean Darebee-style side-view anatomical human figure.
    active_muscle can be: 'lats', 'chest', 'quads', 'hamstrings', 'core', 'glutes', 'shoulders', 'triceps'
    """
    s = scale
    out = [f'<g opacity="{opacity}">']

    # Colors with Darebee red muscle highlight
    c_shirt = "#f87171" if active_muscle in ("lats", "chest", "core") else shirt
    c_thigh = "#ef4444" if active_muscle in ("quads", "hamstrings") else skin
    c_shorts = "#dc2626" if active_muscle == "glutes" else shorts
    c_arm = "#f87171" if active_muscle in ("shoulders", "triceps") else skin

    # Far-side arm
    if elbow2 and hand2:
        out.append(capsule(shoulder[0], shoulder[1], elbow2[0], elbow2[1], 3.8 * s, 2.9 * s, fill="#94a3b8"))
        out.append(capsule(elbow2[0], elbow2[1], hand2[0], hand2[1], 2.8 * s, 2.0 * s, fill="#94a3b8"))
        out.append(f'<circle cx="{hand2[0]:.1f}" cy="{hand2[1]:.1f}" r="{2.4*s:.1f}" fill="#94a3b8" stroke="#0f172a" stroke-width="1"/>')

    # Far-side leg
    if knee2 and ankle2:
        out.append(capsule(hip[0], hip[1], knee2[0], knee2[1], 5.2 * s, 3.6 * s, fill="#94a3b8"))
        out.append(capsule(knee2[0], knee2[1], ankle2[0], ankle2[1], 3.5 * s, 2.3 * s, fill="#94a3b8"))
        if foot2:
            out.append(capsule(ankle2[0], ankle2[1], foot2[0], foot2[1], 2.4 * s, 1.8 * s, fill="#334155"))

    # Neck
    out.append(capsule(shoulder[0], shoulder[1], head[0], head[1], 2.8 * s, 2.4 * s, fill=skin))

    # Torso
    if mid_spine:
        out.append(capsule(shoulder[0], shoulder[1], mid_spine[0], mid_spine[1], 6.4 * s, 5.4 * s, fill=c_shirt))
        out.append(capsule(mid_spine[0], mid_spine[1], hip[0], hip[1], 5.4 * s, 5.0 * s, fill=c_shirt))
    else:
        out.append(capsule(shoulder[0], shoulder[1], hip[0], hip[1], 6.4 * s, 5.0 * s, fill=c_shirt))

    # Shorts / Pelvis
    mid_thigh = (hip[0] * 0.55 + knee[0] * 0.45, hip[1] * 0.55 + knee[1] * 0.45)
    out.append(capsule(hip[0], hip[1], knee[0], knee[1], 5.5 * s, 3.8 * s, fill=c_thigh))
    out.append(capsule(hip[0], hip[1], mid_thigh[0], mid_thigh[1], 5.7 * s, 4.6 * s, fill=c_shorts))

    # Lower leg & foot
    out.append(capsule(knee[0], knee[1], ankle[0], ankle[1], 3.7 * s, 2.4 * s, fill=skin))
    if foot:
        out.append(capsule(ankle[0], ankle[1], foot[0], foot[1], 2.5 * s, 1.9 * s, fill="#1e293b"))
    else:
        # Default foot pointing slightly forward
        dx, dy = ankle[0] - knee[0], ankle[1] - knee[1]
        L = max(1.0, math.hypot(dx, dy))
        fx, fy = ankle[0] - (dy / L) * 6.5 * s, ankle[1] + (dx / L) * 6.5 * s
        out.append(capsule(ankle[0], ankle[1], fx, fy, 2.5 * s, 1.9 * s, fill="#1e293b"))

    # Head
    out.append(f'<circle cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="{5.8*s:.1f}" fill="{skin}" stroke="#0f172a" stroke-width="1.2"/>')

    # Near-side arm
    out.append(capsule(shoulder[0], shoulder[1], elbow[0], elbow[1], 4.1 * s, 3.1 * s, fill=c_arm))
    out.append(capsule(elbow[0], elbow[1], hand[0], hand[1], 3.0 * s, 2.1 * s, fill=skin))
    out.append(f'<circle cx="{hand[0]:.1f}" cy="{hand[1]:.1f}" r="{2.5*s:.1f}" fill="{skin}" stroke="#0f172a" stroke-width="1.1"/>')

    out.append("</g>")
    return "\n".join(out)


def athlete_front_back(
    head,
    sh_l,
    sh_r,
    hip_l,
    hip_r,
    el_l,
    ha_l,
    el_r,
    ha_r,
    kn_l,
    an_l,
    kn_r,
    an_r,
    scale=0.80,
    skin="#cbd5e1",
    shirt="#94a3b8",
    shorts="#1e293b",
    active_muscle=None,
):
    """Draw a Darebee-style front/back anatomical figure (ideal for Pull-ups, Scapular pulls, Dips, Archer)."""
    s = scale
    out = ["<g>"]
    c_shirt = "#f87171" if active_muscle in ("lats", "chest", "core") else shirt
    c_arm = "#f87171" if active_muscle in ("shoulders", "triceps") else skin

    sh_c = ((sh_l[0] + sh_r[0]) / 2, (sh_l[1] + sh_r[1]) / 2)
    hip_c = ((hip_l[0] + hip_r[0]) / 2, (hip_l[1] + hip_r[1]) / 2)

    # Legs
    out.append(capsule(hip_l[0], hip_l[1], kn_l[0], kn_l[1], 4.5 * s, 3.3 * s, fill=skin))
    out.append(capsule(kn_l[0], kn_l[1], an_l[0], an_l[1], 3.2 * s, 2.2 * s, fill=skin))
    out.append(capsule(hip_r[0], hip_r[1], kn_r[0], kn_r[1], 4.5 * s, 3.3 * s, fill=skin))
    out.append(capsule(kn_r[0], kn_r[1], an_r[0], an_r[1], 3.2 * s, 2.2 * s, fill=skin))

    # Shorts polygon
    mt_l = (hip_l[0] * 0.55 + kn_l[0] * 0.45, hip_l[1] * 0.55 + kn_l[1] * 0.45)
    mt_r = (hip_r[0] * 0.55 + kn_r[0] * 0.45, hip_r[1] * 0.55 + kn_r[1] * 0.45)
    out.append(capsule(hip_l[0], hip_l[1], mt_l[0], mt_l[1], 4.7 * s, 3.9 * s, fill=shorts))
    out.append(capsule(hip_r[0], hip_r[1], mt_r[0], mt_r[1], 4.7 * s, 3.9 * s, fill=shorts))
    out.append(capsule(hip_l[0], hip_l[1], hip_r[0], hip_r[1], 4.8 * s, 4.8 * s, fill=shorts))

    # V-Taper Torso polygon
    out.append(
        f'<polygon points="{sh_l[0]:.1f},{sh_l[1]:.1f} {sh_r[0]:.1f},{sh_r[1]:.1f} '
        f'{hip_r[0]+2*s:.1f},{hip_r[1]:.1f} {hip_l[0]-2*s:.1f},{hip_l[1]:.1f}" '
        f'fill="{c_shirt}" stroke="#0f172a" stroke-width="1.2" stroke-linejoin="round"/>'
    )

    # Neck & Head
    out.append(capsule(sh_c[0], sh_c[1], head[0], head[1], 2.8 * s, 2.5 * s, fill=skin))
    out.append(f'<circle cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="{5.8*s:.1f}" fill="{skin}" stroke="#0f172a" stroke-width="1.2"/>')

    # Arms
    out.append(capsule(sh_l[0], sh_l[1], el_l[0], el_l[1], 3.8 * s, 2.9 * s, fill=c_arm))
    out.append(capsule(el_l[0], el_l[1], ha_l[0], ha_l[1], 2.8 * s, 2.0 * s, fill=skin))
    out.append(f'<circle cx="{ha_l[0]:.1f}" cy="{ha_l[1]:.1f}" r="{2.4*s:.1f}" fill="{skin}" stroke="#0f172a" stroke-width="1"/>')

    out.append(capsule(sh_r[0], sh_r[1], el_r[0], el_r[1], 3.8 * s, 2.9 * s, fill=c_arm))
    out.append(capsule(el_r[0], el_r[1], ha_r[0], ha_r[1], 2.8 * s, 2.0 * s, fill=skin))
    out.append(f'<circle cx="{ha_r[0]:.1f}" cy="{ha_r[1]:.1f}" r="{2.4*s:.1f}" fill="{skin}" stroke="#0f172a" stroke-width="1"/>')

    out.append("</g>")
    return "\n".join(out)


def svg_wrap(inner, label_l="1. START", label_r="2. FINISH", cue="", split=True):
    """Wrap a two-panel Darebee-style illustration card (160x100 viewBox)."""
    divider = '<line x1="80" y1="13" x2="80" y2="86" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="2,2"/>' if split else ""
    hdr_r = f'<text x="120" y="9.5" font-size="5.1" font-weight="800" fill="#dc2626" text-anchor="middle">{label_r}</text>' if label_r else ""
    footer = (
        f'<rect x="0" y="87" width="160" height="13" fill="#0f172a"/>'
        f'<text x="80" y="95.2" font-size="5.1" font-weight="700" fill="#f8fafc" text-anchor="middle">{cue}</text>'
    )
    return f"""<svg class="move-svg" viewBox="0 0 160 100">
      <defs>
        <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>
        </marker>
        <marker id="arr-g" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a"/>
        </marker>
      </defs>
      <rect x="0" y="0" width="160" height="87" fill="#f8fafc"/>
      <text x="40" y="9.5" font-size="5.1" font-weight="800" fill="#475569" text-anchor="middle">{label_l}</text>
      {hdr_r}
      {divider}
      {inner}
      {footer}
    </svg>"""


# ==================== BUILD DAREBEE-STYLE ILLUSTRATIONS FOR EVERY MOVE ====================

DIAGRAMS = {}

# 1. Hollow Body vs Arch (Part 0A)
DIAGRAMS["hollow"] = svg_wrap(
    # Left: Good Hollow Body on floor
    '<line x1="4" y1="74" x2="76" y2="74" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(14, 62), shoulder=(23, 66), mid_spine=(38, 70), hip=(50, 69),
        knee=(63, 64), ankle=(74, 60), elbow=(16, 56), hand=(7, 50),
        scale=0.68, active_muscle="core"
    )
    + '<text x="16" y="45" font-size="5.8" font-weight="bold" fill="#15803d">Ribs &amp; Pelvis Tucked</text>'
    + '<path d="M 38 52 L 38 64" stroke="#16a34a" stroke-width="1.5" marker-end="url(#arr-g)"/>'
    # Right: Bad Banana Back
    + '<line x1="84" y1="74" x2="156" y2="74" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(94, 68), shoulder=(103, 69), mid_spine=(116, 62), hip=(130, 70),
        knee=(143, 71), ankle=(154, 71), elbow=(95, 64), hand=(86, 62),
        scale=0.68
    )
    + '<text x="95" y="45" font-size="5.8" font-weight="bold" fill="#dc2626">Low Back Gap (Bad!)</text>'
    + '<circle cx="116" cy="69" r="4" fill="none" stroke="#dc2626" stroke-width="1.4"/>',
    label_l="✓ HOLLOW (PPT)",
    label_r="✗ BANANA ARCH",
    cue="CRUSH LOWER BACK FLAT — TUCK TAILBONE",
)

# 2. Scapular Control (Part 0B)
DIAGRAMS["scapula"] = svg_wrap(
    # Left: Depressed Active Hang
    '<line x1="8" y1="16" x2="72" y2="16" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 31), sh_l=(31, 41), sh_r=(49, 41), hip_l=(35, 62), hip_r=(45, 62),
        el_l=(29, 28), ha_l=(28, 16), el_r=(51, 28), ha_r=(52, 16),
        kn_l=(36, 74), an_l=(36, 84), kn_r=(44, 74), an_r=(44, 84),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 62 34 L 62 48" stroke="#16a34a" stroke-width="1.8" marker-end="url(#arr-g)"/>'
    # Right: Shrugged Passive Hang
    + '<line x1="88" y1="16" x2="152" y2="16" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(120, 38), sh_l=(112, 39), sh_r=(128, 39), hip_l=(115, 60), hip_r=(125, 60),
        el_l=(110, 27), ha_l=(108, 16), el_r=(130, 27), ha_r=(132, 16),
        kn_l=(116, 73), an_l=(116, 84), kn_r=(124, 73), an_r=(124, 84),
        scale=0.68
    )
    + '<circle cx="120" cy="38" r="9" fill="none" stroke="#dc2626" stroke-width="1.3" stroke-dasharray="2,2"/>',
    label_l="✓ DEPRESSED (ACTIVE)",
    label_r="✗ SHRUGGED (EARS)",
    cue="PULL SHOULDERS DOWN AWAY FROM EARS",
)

# 3. Warmup 1: Yuri's Shoulder Band Warmup
DIAGRAMS["yuri"] = svg_wrap(
    # Left: Band in front -> overhead
    '<path d="M 22 48 A 24 24 0 1 1 58 48" fill="none" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,2" marker-end="url(#arr)"/>'
    + athlete_front_back(
        head=(40, 34), sh_l=(31, 44), sh_r=(49, 44), hip_l=(35, 65), hip_r=(45, 65),
        el_l=(23, 30), ha_l=(16, 18), el_r=(57, 30), ha_r=(64, 18),
        kn_l=(35, 76), an_l=(35, 85), kn_r=(45, 76), an_r=(45, 85),
        scale=0.68, active_muscle="shoulders"
    )
    + '<line x1="16" y1="18" x2="64" y2="18" stroke="#dc2626" stroke-width="2.2"/>'
    # Right: Side view passing behind back
    + '<path d="M 102 44 A 24 24 0 1 1 138 56" fill="none" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,2" marker-end="url(#arr)"/>'
    + athlete_side(
        head=(118, 32), shoulder=(118, 43), hip=(118, 64),
        knee=(118, 75), ankle=(118, 84),
        elbow=(130, 34), hand=(140, 26),
        elbow2=(106, 34), hand2=(96, 26),
        scale=0.68, active_muscle="shoulders"
    ),
    label_l="1. OVERHEAD RAISE",
    label_r="2. PASS BEHIND BACK",
    cue="KEEP ELBOWS 100% LOCKED — RIBS TUCKED",
)

# 4. Warmup 2: Squat Sky Reaches
DIAGRAMS["sky_reach"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(44, 46), shoulder=(40, 55), hip=(26, 72),
        knee=(46, 62), ankle=(38, 80), foot=(47, 81),
        elbow=(39, 68), hand=(38, 79),
        scale=0.72
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(122, 42), shoulder=(118, 52), hip=(104, 72),
        knee=(124, 62), ankle=(116, 80), foot=(125, 81),
        elbow=(126, 34), hand=(134, 18),
        elbow2=(116, 66), hand2=(116, 79),
        scale=0.72, active_muscle="lats"
    )
    + '<path d="M 134 45 A 22 22 0 0 0 137 22" fill="none" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arr)"/>',
    label_l="1. DEEP SQUAT GRIP",
    label_r="2. SKY REACH TWIST",
    cue="HEELS FLAT — TWIST UPPER BACK TO CEILING",
)

# 5. Warmup 3: GMB Wrist Prep
DIAGRAMS["wrist_prep"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(64, 44), shoulder=(54, 48), hip=(24, 52),
        knee=(24, 78), ankle=(10, 78), foot=(6, 78),
        elbow=(52, 64), hand=(48, 78), foot2=(56, 78),
        scale=0.72, active_muscle="shoulders"
    )
    + '<path d="M 44 36 L 62 36" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>'
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(134, 46), shoulder=(124, 50), hip=(98, 54),
        knee=(102, 78), ankle=(88, 78), foot=(84, 78),
        elbow=(128, 64), hand=(132, 78),
        scale=0.72, active_muscle="shoulders"
    )
    + '<path d="M 116 36 L 98 36" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. LEAN PAST FINGERS",
    label_r="2. FINGERS BACK ROCK",
    cue="LOCK ELBOWS STRAIGHT — ROCK SMOOTHLY",
)

# 6. Warmup 4: Deadbugs
DIAGRAMS["deadbug"] = svg_wrap(
    '<line x1="6" y1="78" x2="74" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(14, 71), shoulder=(24, 73), mid_spine=(37, 74), hip=(50, 73),
        knee=(50, 52), ankle=(68, 52),
        elbow=(24, 56), hand=(24, 40),
        scale=0.68, active_muscle="core"
    )
    + '<line x1="86" y1="78" x2="156" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(96, 71), shoulder=(105, 73), mid_spine=(118, 74), hip=(130, 73),
        knee=(142, 69), ankle=(154, 66),
        knee2=(130, 52), ankle2=(144, 52),
        elbow=(95, 68), hand=(84, 64),
        elbow2=(105, 56), hand2=(105, 42),
        scale=0.68, active_muscle="core"
    )
    + '<path d="M 118 60 L 118 70" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arr)"/>',
    label_l="1. 90° TABLETOP",
    label_r="2. EXTEND OPPOSITES",
    cue="ZERO GAP UNDER LOWER BACK AT ALL TIMES",
)

# 7. Warmup 5 & Pullup L2: Arch Hangs
DIAGRAMS["arch_hang"] = svg_wrap(
    '<line x1="12" y1="15" x2="68" y2="15" stroke="#334155" stroke-width="3"/>'
    + athlete_side(
        head=(38, 36), shoulder=(40, 44), hip=(40, 65),
        knee=(40, 76), ankle=(40, 84),
        elbow=(40, 29), hand=(40, 15),
        scale=0.68
    )
    + '<line x1="92" y1="15" x2="148" y2="15" stroke="#334155" stroke-width="3"/>'
    + athlete_side(
        head=(134, 34), shoulder=(126, 40), mid_spine=(116, 52), hip=(112, 65),
        knee=(108, 76), ankle=(105, 84),
        elbow=(122, 27), hand=(118, 15),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 114 38 L 104 28" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arr)"/>',
    label_l="1. DEAD HANG",
    label_r="2. ARCH HANG",
    cue="ELBOWS STRAIGHT — PULL CHEST TO CEILING",
)

# 8. Warmup 6 & Dip L1: Support Hold
DIAGRAMS["support_hold"] = svg_wrap(
    '<line x1="12" y1="50" x2="68" y2="50" stroke="#475569" stroke-width="3.2"/>'
    + '<line x1="20" y1="50" x2="20" y2="85" stroke="#94a3b8" stroke-width="2"/>'
    + '<line x1="60" y1="50" x2="60" y2="85" stroke="#94a3b8" stroke-width="2"/>'
    + athlete_front_back(
        head=(40, 22), sh_l=(30, 32), sh_r=(50, 32), hip_l=(35, 54), hip_r=(45, 54),
        el_l=(29, 41), ha_l=(29, 50), el_r=(51, 41), ha_r=(51, 50),
        kn_l=(36, 68), an_l=(36, 81), kn_r=(44, 68), an_r=(44, 81),
        scale=0.68, active_muscle="shoulders"
    )
    + '<path d="M 64 26 L 64 40" stroke="#16a34a" stroke-width="1.8" marker-end="url(#arr-g)"/>'
    # Right side view showing hollow body
    + '<line x1="92" y1="50" x2="148" y2="50" stroke="#475569" stroke-width="3.2"/>'
    + athlete_side(
        head=(120, 22), shoulder=(120, 32), hip=(118, 54),
        knee=(121, 68), ankle=(124, 81),
        elbow=(120, 41), hand=(120, 50),
        scale=0.68, active_muscle="core"
    ),
    label_l="FRONT: DEPRESS SCAP",
    label_r="SIDE: HOLLOW LOCK",
    cue="PUSH BARS DOWN — LOCK ELBOWS — GLUTES TIGHT",
)

# 9. Pullup L1: Scapular Pulls
DIAGRAMS["scap_pull"] = DIAGRAMS["scapula"]

# 10. Pullup L3: Negative Pull-Ups
DIAGRAMS["neg_pullup"] = svg_wrap(
    '<line x1="10" y1="18" x2="70" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 14), sh_l=(30, 24), sh_r=(50, 24), hip_l=(35, 48), hip_r=(45, 48),
        el_l=(22, 33), ha_l=(26, 18), el_r=(58, 33), ha_r=(54, 18),
        kn_l=(36, 63), an_l=(36, 76), kn_r=(44, 63), an_r=(44, 76),
        scale=0.68, active_muscle="lats"
    )
    + '<line x1="90" y1="18" x2="150" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(120, 31), sh_l=(110, 41), sh_r=(130, 41), hip_l=(115, 63), hip_r=(125, 63),
        el_l=(108, 29), ha_l=(106, 18), el_r=(132, 29), ha_r=(134, 18),
        kn_l=(116, 75), an_l=(116, 85), kn_r=(124, 75), an_r=(124, 85),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 144 26 L 144 68" stroke="#dc2626" stroke-width="2" stroke-dasharray="3,2" marker-end="url(#arr)"/>'
    + '<text x="147" y="50" font-size="5.5" font-weight="bold" fill="#dc2626">3-5s</text>',
    label_l="1. TOP HOLD (1s)",
    label_r="2. 3–5s SLOW LOWER",
    cue="JUMP TO CHEST-TO-BAR — LOWER EVENLY OVER 3–5s",
)

# 11. Pullup L4: Full Pull-Ups
DIAGRAMS["pullup"] = svg_wrap(
    '<line x1="10" y1="18" x2="70" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 31), sh_l=(30, 41), sh_r=(50, 41), hip_l=(35, 63), hip_r=(45, 63),
        el_l=(28, 29), ha_l=(26, 18), el_r=(52, 29), ha_r=(54, 18),
        kn_l=(36, 75), an_l=(36, 85), kn_r=(44, 75), an_r=(44, 85),
        scale=0.68, active_muscle="lats"
    )
    + '<line x1="90" y1="18" x2="150" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(120, 14), sh_l=(110, 24), sh_r=(130, 24), hip_l=(115, 48), hip_r=(125, 48),
        el_l=(102, 33), ha_l=(106, 18), el_r=(138, 33), ha_r=(134, 18),
        kn_l=(116, 63), an_l=(116, 76), kn_r=(124, 63), an_r=(124, 76),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 144 64 L 144 26" stroke="#dc2626" stroke-width="2" marker-end="url(#arr)"/>',
    label_l="1. ACTIVE HANG",
    label_r="2. CHEST TO BAR",
    cue="DRIVE ELBOWS TO RIBS — CHIN/CHEST TO BAR",
)

# 12. Pullup L5A: L-Sit Pull-Up
DIAGRAMS["lsit_pullup"] = svg_wrap(
    '<circle cx="34" cy="16" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(36, 30), shoulder=(36, 40), hip=(36, 62),
        knee=(54, 62), ankle=(70, 62), foot=(72, 56),
        elbow=(35, 28), hand=(34, 16),
        scale=0.68, active_muscle="core"
    )
    + '<circle cx="114" cy="18" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(120, 14), shoulder=(118, 24), hip=(116, 48),
        knee=(134, 48), ankle=(150, 48), foot=(152, 42),
        elbow=(108, 32), hand=(114, 18),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 98 62 L 98 28" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. L-SIT HANG",
    label_r="2. L-SIT PULL-UP",
    cue="LOCK LEGS AT 90° HORIZONTAL THROUGHOUT",
)

# 13. Pullup L5B: Weighted Pull-Up
DIAGRAMS["weighted_pullup"] = svg_wrap(
    '<line x1="10" y1="18" x2="70" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 31), sh_l=(30, 41), sh_r=(50, 41), hip_l=(35, 62), hip_r=(45, 62),
        el_l=(28, 29), ha_l=(26, 18), el_r=(52, 29), ha_r=(54, 18),
        kn_l=(35, 74), an_l=(35, 84), kn_r=(45, 74), an_r=(45, 84),
        scale=0.68, active_muscle="lats"
    )
    + '<circle cx="40" cy="72" r="5.5" fill="#dc2626" stroke="#0f172a" stroke-width="1"/>'
    + '<text x="35" y="74" font-size="4.8" font-weight="bold" fill="#fff">+KG</text>'
    + '<line x1="90" y1="18" x2="150" y2="18" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(120, 14), sh_l=(110, 24), sh_r=(130, 24), hip_l=(115, 47), hip_r=(125, 47),
        el_l=(102, 33), ha_l=(106, 18), el_r=(138, 33), ha_r=(134, 18),
        kn_l=(115, 62), an_l=(115, 74), kn_r=(125, 62), an_r=(125, 74),
        scale=0.68, active_muscle="lats"
    )
    + '<circle cx="120" cy="58" r="5.5" fill="#dc2626" stroke="#0f172a" stroke-width="1"/>'
    + '<text x="115" y="60" font-size="4.8" font-weight="bold" fill="#fff">+KG</text>',
    label_l="1. WEIGHTED HANG",
    label_r="2. FULL ROM PULL",
    cue="DIP BELT OR VEST — KEEP STRICT CHEST-TO-BAR ROM",
)

# 14. Pullup L5C: Arch Hanger Pull-Up
DIAGRAMS["arch_pullup"] = svg_wrap(
    '<circle cx="36" cy="18" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(52, 32), shoulder=(44, 38), mid_spine=(34, 50), hip=(30, 63),
        knee=(26, 74), ankle=(23, 83),
        elbow=(40, 27), hand=(36, 18),
        scale=0.68, active_muscle="lats"
    )
    + '<circle cx="114" cy="20" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(134, 20), shoulder=(124, 24), mid_spine=(112, 36), hip=(104, 48),
        knee=(98, 60), ankle=(92, 72),
        elbow=(112, 32), hand=(114, 20),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 134 52 L 122 32" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. ARCH HANG LOCK",
    label_r="2. STERNUM TO BAR",
    cue="MAINTAIN DEEP THORACIC ARCH ALL THE WAY UP",
)

# 15. Pullup L5D: Archer / Typewriter Pull-Up
DIAGRAMS["archer_pullup"] = svg_wrap(
    '<line x1="6" y1="20" x2="74" y2="20" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 15), sh_l=(30, 25), sh_r=(50, 25), hip_l=(35, 49), hip_r=(45, 49),
        el_l=(20, 32), ha_l=(16, 20), el_r=(60, 32), ha_r=(64, 20),
        kn_l=(36, 64), an_l=(36, 77), kn_r=(44, 64), an_r=(44, 77),
        scale=0.68, active_muscle="lats"
    )
    + '<line x1="86" y1="20" x2="154" y2="20" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(104, 15), sh_l=(95, 25), sh_r=(115, 25), hip_l=(100, 49), hip_r=(110, 49),
        el_l=(89, 34), ha_l=(94, 20), el_r=(132, 23), ha_r=(148, 20),
        kn_l=(101, 64), an_l=(101, 77), kn_r=(109, 64), an_r=(109, 77),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 126 42 L 104 42" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. WIDE PULL",
    label_r="2. ARCHER SHIFT",
    cue="PULL TO ONE HAND — OPPOSITE ARM 100% STRAIGHT",
)

# 16. Squat L1-2: Full Squat
DIAGRAMS["squat"] = svg_wrap(
    '<line x1="8" y1="82" x2="72" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(40, 20), shoulder=(40, 31), hip=(40, 52),
        knee=(40, 67), ankle=(40, 80), foot=(48, 81),
        elbow=(40, 42), hand=(48, 46),
        scale=0.72
    )
    + '<line x1="88" y1="82" x2="152" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(120, 34), shoulder=(116, 44), hip=(98, 66),
        knee=(126, 62), ankle=(114, 80), foot=(124, 81),
        elbow=(128, 46), hand=(144, 44),
        scale=0.72, active_muscle="quads"
    )
    + '<path d="M 92 40 L 92 64" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. STAND TALL",
    label_r="2. BELOW PARALLEL",
    cue="HIP CREASE BELOW KNEE — HEELS FLAT ON FLOOR",
)

# 17. Squat L3: Bulgarian Split Squat
DIAGRAMS["bss"] = svg_wrap(
    '<line x1="4" y1="82" x2="76" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="8" y="58" width="16" height="24" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(48, 19), shoulder=(46, 30), hip=(44, 51),
        knee=(50, 66), ankle=(52, 80), foot=(60, 81),
        knee2=(32, 64), ankle2=(16, 58), foot2=(12, 62),
        elbow=(46, 41), hand=(54, 44),
        scale=0.70
    )
    + '<line x1="84" y1="82" x2="156" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="88" y="58" width="16" height="24" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(128, 30), shoulder=(124, 41), hip=(116, 62),
        knee=(136, 60), ankle=(132, 80), foot=(141, 81),
        knee2=(110, 79), ankle2=(96, 58), foot2=(92, 62),
        elbow=(132, 46), hand=(146, 44),
        scale=0.70, active_muscle="quads"
    )
    + '<path d="M 148 54 L 148 76" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. REAR FOOT UP",
    label_r="2. DEEP SPLIT SQUAT",
    cue="TORSO MATCHES FRONT SHIN — 85% WEIGHT IN FRONT",
)

# 18. Squat L4: Beginner Shrimp Squat
DIAGRAMS["beg_shrimp"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(44, 19), shoulder=(42, 30), hip=(40, 51),
        knee=(42, 66), ankle=(42, 80), foot=(50, 81),
        knee2=(36, 66), ankle2=(22, 66), foot2=(20, 72),
        elbow=(48, 36), hand=(62, 34),
        scale=0.70
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(128, 32), shoulder=(122, 42), hip=(112, 62),
        knee=(136, 60), ankle=(126, 80), foot=(135, 81),
        knee2=(108, 80), ankle2=(90, 80), foot2=(88, 82),
        elbow=(132, 44), hand=(148, 42),
        scale=0.70, active_muscle="quads"
    ),
    label_l="1. 1-LEG BALANCE",
    label_r="2. KNEE &amp; TOES KISS",
    cue="REAR KNEE &amp; REAR TOES TOUCH SIMULTANEOUSLY",
)

# 19. Squat L5-6: Int / Adv Shrimp Squat
DIAGRAMS["adv_shrimp"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(44, 19), shoulder=(42, 30), hip=(40, 51),
        knee=(42, 66), ankle=(42, 80), foot=(50, 81),
        knee2=(36, 66), ankle2=(24, 56),
        elbow=(32, 44), hand=(24, 56),
        elbow2=(50, 34), hand2=(64, 34),
        scale=0.70
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(128, 32), shoulder=(122, 42), hip=(112, 62),
        knee=(136, 60), ankle=(126, 80), foot=(135, 81),
        knee2=(108, 80), ankle2=(94, 64),
        elbow=(106, 54), hand=(94, 64),
        scale=0.70, active_muscle="quads"
    ),
    label_l="1. GRAB ANKLE HIGH",
    label_r="2. ONLY KNEE KISSES",
    cue="HOLD REAR ANKLE — ONLY REAR KNEE TOUCHES FLOOR",
)

# 20. Squat Alt A: Pistol Squat
DIAGRAMS["pistol"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(36, 19), shoulder=(36, 30), hip=(36, 51),
        knee=(38, 66), ankle=(38, 80), foot=(46, 81),
        knee2=(50, 54), ankle2=(64, 56), foot2=(66, 50),
        elbow=(46, 34), hand=(60, 34),
        scale=0.70
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(116, 40), shoulder=(110, 50), hip=(98, 72),
        knee=(124, 58), ankle=(112, 80), foot=(122, 81),
        knee2=(124, 72), ankle2=(146, 70), foot2=(148, 63),
        elbow=(124, 52), hand=(142, 50),
        scale=0.70, active_muscle="quads"
    ),
    label_l="1. EXTEND FREE LEG",
    label_r="2. FULL PISTOL DEPTH",
    cue="HAMSTRING TO CALF — WORKING HEEL GLUED DOWN",
)

# 21. Squat Alt B: Deep Step-Ups
DIAGRAMS["step_up"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="42" y="54" width="24" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(38, 22), shoulder=(34, 32), hip=(24, 52),
        knee=(48, 38), ankle=(50, 54), foot=(58, 54),
        knee2=(24, 66), ankle2=(22, 80), foot2=(29, 76),
        elbow=(42, 36), hand=(54, 36),
        scale=0.68, active_muscle="quads"
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="118" y="54" width="24" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(128, 12), shoulder=(128, 22), hip=(128, 38),
        knee=(128, 46), ankle=(128, 54), foot=(136, 54),
        knee2=(118, 50), ankle2=(116, 62),
        elbow=(128, 30), hand=(134, 34),
        scale=0.68, active_muscle="glutes"
    )
    + '<path d="M 104 56 L 104 24" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. DORSIFLEX REAR TOE",
    label_r="2. DRIVE THROUGH BOX",
    cue="PULL BOTTOM TOES UP — ZERO REAR LEG PUSH-OFF",
)

# 22. Dip L2 & L3: Parallel Bar Dips / Negatives
DIAGRAMS["dip"] = svg_wrap(
    '<line x1="10" y1="50" x2="70" y2="50" stroke="#475569" stroke-width="3.2"/>'
    + athlete_side(
        head=(40, 20), shoulder=(40, 31), hip=(38, 53),
        knee=(41, 67), ankle=(44, 80),
        elbow=(40, 40), hand=(40, 50),
        scale=0.70, active_muscle="triceps"
    )
    + '<line x1="90" y1="52" x2="150" y2="52" stroke="#475569" stroke-width="3.2"/>'
    + athlete_side(
        head=(134, 28), shoulder=(126, 36), hip=(110, 58),
        knee=(114, 72), ankle=(118, 83),
        elbow=(110, 34), hand=(112, 52),
        scale=0.70, active_muscle="chest"
    )
    + '<path d="M 142 26 L 142 50" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. LOCKED SUPPORT",
    label_r="2. SHOULDER ≤ ELBOW",
    cue="FOREARMS VERTICAL — SLIGHT FORWARD TORSO LEAN",
)

# 23. Dip L4: L-Sit Dips
DIAGRAMS["lsit_dip"] = svg_wrap(
    '<line x1="10" y1="50" x2="70" y2="50" stroke="#475569" stroke-width="3.2"/>'
    + athlete_side(
        head=(34, 20), shoulder=(34, 31), hip=(32, 53),
        knee=(50, 53), ankle=(66, 53), foot=(68, 47),
        elbow=(34, 40), hand=(34, 50),
        scale=0.68, active_muscle="core"
    )
    + '<line x1="90" y1="52" x2="150" y2="52" stroke="#475569" stroke-width="3.2"/>'
    + athlete_side(
        head=(122, 28), shoulder=(114, 36), hip=(102, 58),
        knee=(120, 58), ankle=(138, 58), foot=(140, 52),
        elbow=(100, 34), hand=(102, 52),
        scale=0.68, active_muscle="chest"
    ),
    label_l="1. L-SIT SUPPORT",
    label_r="2. L-SIT DIP",
    cue="KEEP LEGS HORIZONTAL — DEEP CHEST &amp; DELT LOAD",
)

# 24. Dip Alt A: Ring Dips (RTO)
DIAGRAMS["ring_dip"] = svg_wrap(
    '<line x1="28" y1="12" x2="28" y2="48" stroke="#64748b" stroke-width="1.6"/>'
    + '<line x1="52" y1="12" x2="52" y2="48" stroke="#64748b" stroke-width="1.6"/>'
    + '<circle cx="28" cy="50" r="3.5" fill="none" stroke="#dc2626" stroke-width="1.8"/>'
    + '<circle cx="52" cy="50" r="3.5" fill="none" stroke="#dc2626" stroke-width="1.8"/>'
    + athlete_front_back(
        head=(40, 20), sh_l=(30, 30), sh_r=(50, 30), hip_l=(35, 53), hip_r=(45, 53),
        el_l=(29, 40), ha_l=(28, 50), el_r=(51, 40), ha_r=(52, 50),
        kn_l=(36, 67), an_l=(36, 80), kn_r=(44, 67), an_r=(44, 80),
        scale=0.68, active_muscle="chest"
    )
    + '<line x1="108" y1="12" x2="108" y2="50" stroke="#64748b" stroke-width="1.6"/>'
    + '<line x1="132" y1="12" x2="132" y2="50" stroke="#64748b" stroke-width="1.6"/>'
    + athlete_front_back(
        head=(120, 32), sh_l=(110, 42), sh_r=(130, 42), hip_l=(115, 63), hip_r=(125, 63),
        el_l=(104, 34), ha_l=(108, 50), el_r=(136, 34), ha_r=(132, 50),
        kn_l=(116, 74), an_l=(116, 84), kn_r=(124, 74), an_r=(124, 84),
        scale=0.68, active_muscle="chest"
    ),
    label_l="1. RTO 45° LOCKOUT",
    label_r="2. DEEP RING DIP",
    cue="RINGS TIGHT TO RIBS — TURN RINGS OUT AT TOP",
)

# 25. Dip Alt B: Pike / Wall HSPU
DIAGRAMS["pike_hspu"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="8" y="48" width="18" height="34" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(52, 56), shoulder=(48, 48), hip=(36, 28),
        knee=(24, 38), ankle=(16, 48), foot=(12, 48),
        elbow=(52, 65), hand=(54, 80),
        scale=0.68, active_muscle="shoulders"
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="88" y="48" width="18" height="34" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(142, 74), shoulder=(134, 62), hip=(116, 34),
        knee=(104, 42), ankle=(96, 48), foot=(92, 48),
        elbow=(128, 64), hand=(130, 80),
        scale=0.68, active_muscle="shoulders"
    )
    + '<path d="M 134 48 L 142 68" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. INVERTED PIKE",
    label_r="2. TRIPOD HEAD TOUCH",
    cue="HEAD LANDS IN FRONT OF HANDS (TRIPOD TRIANGLE)",
)

# 26. Hinge L1: Romanian Deadlift (RDL)
DIAGRAMS["rdl"] = svg_wrap(
    '<line x1="8" y1="82" x2="72" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(40, 19), shoulder=(40, 30), hip=(40, 51),
        knee=(40, 66), ankle=(40, 80), foot=(48, 81),
        elbow=(40, 41), hand=(42, 52),
        scale=0.72
    )
    + '<line x1="88" y1="82" x2="152" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(142, 44), shoulder=(132, 45), hip=(102, 48),
        knee=(108, 65), ankle=(110, 80), foot=(118, 81),
        elbow=(130, 58), hand=(128, 70),
        scale=0.72, active_muscle="hamstrings"
    )
    + '<path d="M 102 36 L 88 36" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. STAND TALL",
    label_r="2. HIPS PUSH BACK",
    cue="SHINS VERTICAL — FLAT BACK — DEEP HAMSTRING STRETCH",
)

# 27. Hinge L2: Single-Leg RDL
DIAGRAMS["sl_rdl"] = svg_wrap(
    '<line x1="8" y1="82" x2="72" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(40, 19), shoulder=(40, 30), hip=(40, 51),
        knee=(40, 66), ankle=(40, 80), foot=(48, 81),
        knee2=(46, 62), ankle2=(46, 74),
        elbow=(40, 41), hand=(42, 52),
        scale=0.70
    )
    + '<line x1="84" y1="82" x2="156" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(148, 45), shoulder=(138, 45), hip=(116, 46),
        knee=(118, 64), ankle=(118, 80), foot=(126, 81),
        knee2=(98, 46), ankle2=(84, 46), foot2=(84, 53),
        elbow=(136, 58), hand=(136, 70),
        scale=0.70, active_muscle="hamstrings"
    ),
    label_l="1. 1-LEG STANCE",
    label_r="2. CAPITAL 'T' HINGE",
    cue="HEAD TO REAR HEEL 180° — REAR TOES POINT DOWN",
)

# 28. Hinge L3-5: Nordic Hamstring Curl
DIAGRAMS["nordic"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="10" y="68" width="12" height="14" fill="#475569"/>'
    + athlete_side(
        head=(44, 24), shoulder=(44, 34), hip=(44, 56),
        knee=(44, 78), ankle=(20, 78), foot=(18, 82),
        elbow=(48, 44), hand=(52, 38),
        scale=0.68, active_muscle="hamstrings"
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="90" y="68" width="12" height="14" fill="#475569"/>'
    + athlete_side(
        head=(146, 48), shoulder=(138, 54), hip=(124, 66),
        knee=(110, 78), ankle=(98, 78), foot=(96, 82),
        elbow=(142, 66), hand=(146, 76),
        scale=0.68, active_muscle="hamstrings"
    )
    + '<path d="M 118 30 A 32 32 0 0 1 142 42" fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. TALL KNEEL LOCK",
    label_r="2. HIPS STRAIGHT LOWER",
    cue="SQUEEZE GLUTES — ZERO BEND AT HIPS ON DESCENT",
)

# 29. Hinge Alt A: Towel Sliding Leg Curls
DIAGRAMS["sliding_curl"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="56" y="77" width="14" height="3" fill="#dc2626"/>'
    + athlete_side(
        head=(12, 72), shoulder=(20, 74), hip=(38, 68),
        knee=(52, 72), ankle=(64, 77), foot=(68, 71),
        elbow=(24, 76), hand=(34, 78),
        scale=0.68, active_muscle="hamstrings"
    )
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="122" y="77" width="14" height="3" fill="#dc2626"/>'
    + athlete_side(
        head=(92, 72), shoulder=(100, 74), hip=(116, 58),
        knee=(130, 50), ankle=(128, 77), foot=(134, 73),
        elbow=(104, 76), hand=(114, 78),
        scale=0.68, active_muscle="hamstrings"
    )
    + '<path d="M 148 72 L 134 72" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. BRIDGE &amp; SLIDE OUT",
    label_r="2. CURL HEELS TO BUTT",
    cue="KEEP HIPS BRIDGED HIGH AS HEELS CURL IN",
)

# 30. Hinge Alt B: Single-Leg Hip Thrust
DIAGRAMS["hip_thrust"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="8" y="54" width="16" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(18, 44), shoulder=(22, 54), hip=(38, 70),
        knee=(54, 54), ankle=(56, 80), foot=(64, 81),
        knee2=(48, 50), ankle2=(56, 40),
        elbow=(22, 58), hand=(16, 54),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="88" y="54" width="16" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(98, 46), shoulder=(102, 54), hip=(120, 54),
        knee=(138, 54), ankle=(138, 80), foot=(146, 81),
        knee2=(126, 38), ankle2=(134, 28),
        elbow=(102, 58), hand=(96, 54),
        scale=0.68, active_muscle="glutes"
    )
    + '<path d="M 120 74 L 120 58" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. HIPS LOWERED",
    label_r="2. FULL GLUTE LOCKOUT",
    cue="SHIN VERTICAL AT TOP — TUCK CHIN — SQUEEZE GLUTE",
)

# 31. Row L1-2: Incline Row
DIAGRAMS["incline_row"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="54" y1="20" x2="54" y2="82" stroke="#94a3b8" stroke-width="2.5"/>'
    + '<circle cx="54" cy="36" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(26, 30), shoulder=(30, 39), hip=(42, 60),
        knee=(48, 70), ankle=(54, 80), foot=(60, 80),
        elbow=(42, 38), hand=(54, 36),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="134" y1="20" x2="134" y2="82" stroke="#94a3b8" stroke-width="2.5"/>'
    + '<circle cx="134" cy="36" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(124, 24), shoulder=(126, 34), hip=(130, 57),
        knee=(132, 69), ankle=(134, 80), foot=(140, 80),
        elbow=(116, 42), hand=(134, 36),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 104 42 L 120 36" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. ARMS EXTENDED",
    label_r="2. CHEST TO BAR",
    cue="BODY STRAIGHT LIKE A PLANK — PINCH SCAPULAE",
)

# 32. Row L3: Horizontal Inverted Row
DIAGRAMS["horiz_row"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="28" y1="32" x2="28" y2="82" stroke="#94a3b8" stroke-width="2.5"/>'
    + '<circle cx="28" cy="34" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(16, 54), shoulder=(24, 58), hip=(44, 68),
        knee=(56, 74), ankle=(68, 80), foot=(72, 74),
        elbow=(26, 46), hand=(28, 34),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="108" y1="32" x2="108" y2="82" stroke="#94a3b8" stroke-width="2.5"/>'
    + '<circle cx="108" cy="34" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(98, 34), shoulder=(106, 39), hip=(126, 56),
        knee=(138, 68), ankle=(148, 80), foot=(152, 74),
        elbow=(102, 50), hand=(108, 34),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 116 68 L 116 48" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. HANG UNDER BAR",
    label_r="2. STERNUM TOUCHES BAR",
    cue="GLUTES SQUEEZED — PULL CHEST ALL THE WAY TO BAR",
)

# 33. Row L4: Wide / Feet-Elevated Row
DIAGRAMS["elev_row"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="56" y="54" width="14" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + '<circle cx="24" cy="32" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(12, 54), shoulder=(20, 56), hip=(38, 56),
        knee=(50, 55), ankle=(62, 54), foot=(64, 48),
        elbow=(22, 44), hand=(24, 32),
        scale=0.66
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="136" y="54" width="14" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + '<circle cx="104" cy="32" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(94, 34), shoulder=(102, 36), hip=(120, 44),
        knee=(132, 49), ankle=(142, 54), foot=(144, 48),
        elbow=(98, 48), hand=(104, 32),
        scale=0.66, active_muscle="lats"
    ),
    label_l="1. FEET ON CHAIR HANG",
    label_r="2. HORIZONTAL ROW",
    cue="WIDE GRIP (90° ELBOWS) OR FEET AT BAR HEIGHT",
)

# 34. Row L5A: Weighted Inverted Row
DIAGRAMS["weighted_row"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="26" cy="32" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(14, 54), shoulder=(22, 58), hip=(42, 68),
        knee=(54, 74), ankle=(66, 80), foot=(70, 74),
        elbow=(24, 45), hand=(26, 32),
        scale=0.68
    )
    + '<rect x="28" y="54" width="12" height="5" rx="1.5" fill="#dc2626" transform="rotate(26 34 56)"/>'
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="106" cy="32" r="3.2" fill="#0f172a"/>'
    + athlete_side(
        head=(96, 34), shoulder=(104, 39), hip=(124, 56),
        knee=(136, 68), ankle=(146, 80), foot=(150, 74),
        elbow=(100, 50), hand=(106, 32),
        scale=0.68, active_muscle="lats"
    )
    + '<rect x="110" y="38" width="12" height="5" rx="1.5" fill="#dc2626" transform="rotate(38 116 40)"/>',
    label_l="1. VEST / CHEST PLATE",
    label_r="2. FULL TOUCH AT TOP",
    cue="PLATE ON CHEST (NEVER BELLY) — TOUCH BAR EVERY REP",
)

# 35. Row Alt A: Archer / One-Arm Row
DIAGRAMS["archer_row"] = svg_wrap(
    '<line x1="8" y1="22" x2="72" y2="22" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(40, 36), sh_l=(30, 45), sh_r=(50, 45), hip_l=(35, 65), hip_r=(45, 65),
        el_l=(24, 34), ha_l=(20, 22), el_r=(56, 34), ha_r=(60, 22),
        kn_l=(34, 75), an_l=(32, 84), kn_r=(46, 75), an_r=(48, 84),
        scale=0.68
    )
    + '<line x1="88" y1="22" x2="152" y2="22" stroke="#334155" stroke-width="3"/>'
    + athlete_front_back(
        head=(106, 26), sh_l=(96, 34), sh_r=(116, 34), hip_l=(101, 56), hip_r=(111, 56),
        el_l=(90, 42), ha_l=(96, 22), el_r=(132, 28), ha_r=(148, 22),
        kn_l=(100, 70), an_l=(98, 82), kn_r=(112, 70), an_r=(114, 82),
        scale=0.68, active_muscle="lats"
    ),
    label_l="1. WIDE SETUP",
    label_r="2. 1-ARM / ARCHER ROW",
    cue="ASSIST ARM STRAIGHT — KEEP SHOULDERS &amp; HIPS SQUARE",
)

# 36. Row Alt B: Tuck Front Lever Row
DIAGRAMS["tuck_fl_row"] = svg_wrap(
    '<circle cx="40" cy="18" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(22, 54), shoulder=(32, 54), hip=(52, 54),
        knee=(44, 38), ankle=(56, 40), foot=(60, 44),
        elbow=(36, 36), hand=(40, 18),
        scale=0.68, active_muscle="lats"
    )
    + '<circle cx="120" cy="18" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(102, 34), shoulder=(112, 34), hip=(132, 34),
        knee=(124, 20), ankle=(136, 22), foot=(140, 26),
        elbow=(108, 46), hand=(120, 18),
        scale=0.68, active_muscle="lats"
    )
    + '<path d="M 122 62 L 122 42" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. TUCK FRONT LEVER",
    label_r="2. MID-AIR TUCK ROW",
    cue="BACK HORIZONTAL IN AIR — ROW HIPS TO BAR",
)

# 37. Push-Up L1-2: Incline Push-Up
DIAGRAMS["incline_pushup"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="52" y="54" width="16" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(52, 26), shoulder=(44, 34), hip=(28, 56),
        knee=(18, 68), ankle=(10, 80), foot=(14, 82),
        elbow=(50, 44), hand=(56, 54),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="132" y="54" width="16" height="28" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(142, 42), shoulder=(132, 48), hip=(112, 64),
        knee=(100, 72), ankle=(90, 80), foot=(94, 82),
        elbow=(122, 48), hand=(136, 54),
        scale=0.68, active_muscle="chest"
    ),
    label_l="1. INCLINE PLANK",
    label_r="2. STERNUM TO EDGE",
    cue="STRAIGHT BODY LINE — ELBOWS TUCKED 45°",
)

# 38. Push-Up L3: Full Push-Up
DIAGRAMS["pushup"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(64, 44), shoulder=(54, 48), hip=(32, 62),
        knee=(20, 70), ankle=(10, 77), foot=(12, 80),
        elbow=(54, 63), hand=(54, 78),
        scale=0.68, active_muscle="core"
    )
    + '<path d="M 54 38 L 54 28" stroke="#16a34a" stroke-width="1.6" marker-end="url(#arr-g)"/>'
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(146, 68), shoulder=(134, 71), hip=(112, 74),
        knee=(100, 76), ankle=(90, 77), foot=(92, 80),
        elbow=(122, 62), hand=(134, 78),
        scale=0.68, active_muscle="chest"
    ),
    label_l="1. PROTRACTED PLANK",
    label_r="2. CHEST TOUCHES FLOOR",
    cue="45° ARROW ELBOW ANGLE — PPT LOCKED — PROTRACT TOP",
)

# 39. Push-Up L4: Diamond Push-Up
DIAGRAMS["diamond_pushup"] = svg_wrap(
    # Left: Close-up Diamond Hand Geometry + Top Plank
    '<rect x="14" y="18" width="52" height="58" rx="5" fill="#eff6ff" stroke="#93c5fd"/>'
    + '<polygon points="40,26 52,42 40,58 28,42" fill="#ffffff" stroke="#dc2626" stroke-width="2"/>'
    + '<text x="40" y="71" font-size="5.6" font-weight="bold" fill="#1e40af" text-anchor="middle">Thumbs &amp; Index Touch</text>'
    # Right: Bottom of Diamond Push-Up with elbows brushing ribs
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(146, 66), shoulder=(134, 70), hip=(112, 73),
        knee=(100, 75), ankle=(90, 77), foot=(92, 80),
        elbow=(120, 62), hand=(132, 78),
        scale=0.68, active_muscle="triceps"
    ),
    label_l="1. DIAMOND HAND GRIP",
    label_r="2. CHEST LANDS ON HANDS",
    cue="HANDS UNDER STERNUM — ELBOWS HUG RIBS TIGHTLY",
)

# 40. Push-Up L5: Pseudo Planche Push-Up (PPPU)
DIAGRAMS["pppu"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="38" y1="22" x2="38" y2="80" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2,2"/>'
    + athlete_side(
        head=(66, 42), shoulder=(56, 46), hip=(32, 60),
        knee=(20, 68), ankle=(10, 77), foot=(12, 80),
        elbow=(46, 62), hand=(38, 78),
        scale=0.68, active_muscle="shoulders"
    )
    + '<path d="M 38 28 L 58 28" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>'
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="118" y1="22" x2="118" y2="80" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2,2"/>'
    + athlete_side(
        head=(148, 66), shoulder=(138, 69), hip=(114, 72),
        knee=(100, 75), ankle=(90, 77), foot=(92, 80),
        elbow=(112, 60), hand=(118, 78),
        scale=0.68, active_muscle="shoulders"
    ),
    label_l="1. LEAN SHOULDERS AHEAD",
    label_r="2. HANDS BY WAIST/HIPS",
    cue="KEEP SHOULDERS FAR AHEAD OF WRISTS AT TOP &amp; BOTTOM",
)

# 41. Push-Up Alt A: Archer Push-Up
DIAGRAMS["archer_pushup"] = svg_wrap(
    '<line x1="6" y1="78" x2="74" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_front_back(
        head=(40, 42), sh_l=(28, 48), sh_r=(52, 48), hip_l=(36, 56), hip_r=(44, 56),
        el_l=(22, 62), ha_l=(16, 76), el_r=(58, 62), ha_r=(64, 76),
        kn_l=(37, 66), an_l=(37, 76), kn_r=(43, 66), an_r=(43, 76),
        scale=0.66
    )
    + '<line x1="86" y1="78" x2="154" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_front_back(
        head=(106, 58), sh_l=(96, 62), sh_r=(118, 62), hip_l=(106, 66), hip_r=(114, 66),
        el_l=(88, 66), ha_l=(96, 76), el_r=(134, 69), ha_r=(150, 76),
        kn_l=(108, 72), an_l=(108, 76), kn_r=(114, 72), an_r=(114, 76),
        scale=0.66, active_muscle="chest"
    ),
    label_l="1. WIDE HAND STANCE",
    label_r="2. SHIFT TO 1 ARM",
    cue="WORKING ARM BENDS — ASSISTING ARM LOCKED STRAIGHT",
)

# 42. Push-Up Alt B: Ring / RTO Push-Up
DIAGRAMS["ring_pushup"] = svg_wrap(
    '<line x1="54" y1="14" x2="54" y2="72" stroke="#64748b" stroke-width="1.6"/>'
    + '<circle cx="54" cy="74" r="3.5" fill="none" stroke="#dc2626" stroke-width="1.8"/>'
    + '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(64, 42), shoulder=(54, 46), hip=(32, 60),
        knee=(20, 68), ankle=(10, 77), foot=(12, 80),
        elbow=(54, 60), hand=(54, 74),
        scale=0.68, active_muscle="chest"
    )
    + '<line x1="134" y1="14" x2="134" y2="72" stroke="#64748b" stroke-width="1.6"/>'
    + '<circle cx="134" cy="74" r="3.5" fill="none" stroke="#dc2626" stroke-width="1.8"/>'
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(146, 64), shoulder=(134, 68), hip=(112, 71),
        knee=(100, 74), ankle=(90, 77), foot=(92, 80),
        elbow=(122, 58), hand=(134, 74),
        scale=0.68, active_muscle="chest"
    ),
    label_l="1. RTO LOCKOUT TOP",
    label_r="2. DEEP RING STRETCH",
    cue="TURN RINGS OUT (RTO 45–90°) &amp; PROTRACT AT TOP",
)

# 43. Core 1A: Ring / Towel Ab Rollout
DIAGRAMS["ab_rollout"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="52" y="77" width="12" height="3" fill="#dc2626"/>'
    + athlete_side(
        head=(54, 42), shoulder=(46, 46), mid_spine=(34, 50), hip=(24, 58),
        knee=(22, 78), ankle=(10, 78), foot=(8, 80),
        elbow=(52, 62), hand=(58, 77),
        scale=0.68, active_muscle="core"
    )
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="140" y="77" width="12" height="3" fill="#dc2626"/>'
    + athlete_side(
        head=(134, 54), shoulder=(124, 56), mid_spine=(110, 58), hip=(98, 64),
        knee=(92, 78), ankle=(84, 78), foot=(82, 80),
        elbow=(136, 66), hand=(146, 77),
        scale=0.68, active_muscle="core"
    )
    + '<path d="M 126 42 L 146 42" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. KNEELING PPT TUCK",
    label_r="2. EXTEND WITHOUT ARCH",
    cue="KEEP RIBS &amp; TAILBONE TUCKED — PULL BACK WITH LATS/ABS",
)

# 44. Core 1B: Hanging Leg Raise (Toes to Bar)
DIAGRAMS["leg_raise"] = svg_wrap(
    '<circle cx="36" cy="15" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(36, 30), shoulder=(36, 40), hip=(36, 60),
        knee=(50, 58), ankle=(50, 72), foot=(56, 72),
        elbow=(36, 27), hand=(36, 15),
        scale=0.68, active_muscle="core"
    )
    + '<circle cx="116" cy="15" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(112, 30), shoulder=(114, 40), mid_spine=(116, 52), hip=(124, 56),
        knee=(126, 36), ankle=(124, 18), foot=(130, 16),
        elbow=(115, 27), hand=(116, 15),
        scale=0.68, active_muscle="core"
    )
    + '<path d="M 138 56 A 24 24 0 0 0 134 22" fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. HANGING KNEE RAISE",
    label_r="2. PELVIC CURL (T2B)",
    cue="CURL TAILBONE UP AT TOP — ZERO SWINGING",
)

# 45. Core 2A: Banded Pallof Press
DIAGRAMS["pallof"] = svg_wrap(
    '<circle cx="10" cy="48" r="3.5" fill="#dc2626"/>'
    + '<line x1="10" y1="48" x2="42" y2="48" stroke="#dc2626" stroke-width="2" stroke-dasharray="2,2"/>'
    + athlete_front_back(
        head=(42, 24), sh_l=(32, 34), sh_r=(52, 34), hip_l=(35, 56), hip_r=(49, 56),
        el_l=(30, 46), ha_l=(42, 48), el_r=(54, 46), ha_r=(42, 48),
        kn_l=(34, 70), an_l=(33, 82), kn_r=(50, 70), an_r=(51, 82),
        scale=0.68, active_muscle="core"
    )
    + '<circle cx="90" cy="48" r="3.5" fill="#dc2626"/>'
    + '<line x1="90" y1="48" x2="124" y2="48" stroke="#dc2626" stroke-width="2" stroke-dasharray="2,2"/>'
    + athlete_front_back(
        head=(124, 24), sh_l=(114, 34), sh_r=(134, 34), hip_l=(117, 56), hip_r=(131, 56),
        el_l=(118, 44), ha_l=(124, 48), el_r=(130, 44), ha_r=(124, 48),
        kn_l=(116, 70), an_l=(115, 82), kn_r=(132, 70), an_r=(133, 82),
        scale=0.68, active_muscle="core"
    )
    + '<circle cx="124" cy="48" r="4.5" fill="#dc2626"/>',
    label_l="1. BAND AT STERNUM",
    label_r="2. PRESS OUT &amp; HOLD 2s",
    cue="RESIST ROTATION — SHOULDERS &amp; HIPS STAY SQUARE",
)

# 46. Core 2B: Copenhagen Side Plank
DIAGRAMS["copenhagen"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(14, 54), shoulder=(22, 58), hip=(44, 66),
        knee=(56, 72), ankle=(68, 78), foot=(70, 73),
        elbow=(22, 78), hand=(28, 78),
        scale=0.68, active_muscle="core"
    )
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + '<rect x="136" y="54" width="14" height="26" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(94, 52), shoulder=(102, 56), hip=(122, 55),
        knee=(134, 54), ankle=(144, 54), foot=(146, 48),
        knee2=(132, 64), ankle2=(142, 68),
        elbow=(102, 78), hand=(108, 78),
        scale=0.68, active_muscle="core"
    )
    + '<path d="M 122 72 L 122 60" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. SIDE PLANK",
    label_r="2. COPENHAGEN PLANK",
    cue="TOP ANKLE ON CHAIR — LIFT HIPS &amp; BOTTOM LEG HIGH",
)

# 47. Core 3A: Reverse Hyperextension
DIAGRAMS["rev_hyper"] = svg_wrap(
    '<rect x="8" y="48" width="34" height="34" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(14, 42), shoulder=(24, 44), hip=(42, 46),
        knee=(46, 62), ankle=(48, 76), foot=(54, 76),
        elbow=(26, 54), hand=(36, 54),
        scale=0.68
    )
    + '<rect x="88" y="48" width="34" height="34" fill="#cbd5e1" stroke="#475569"/>'
    + athlete_side(
        head=(94, 42), shoulder=(104, 44), hip=(122, 46),
        knee=(138, 45), ankle=(152, 44), foot=(154, 50),
        elbow=(106, 54), hand=(116, 54),
        scale=0.68, active_muscle="glutes"
    )
    + '<path d="M 142 70 A 24 24 0 0 0 148 50" fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arr)"/>',
    label_l="1. HIPS ON TABLE EDGE",
    label_r="2. LIFT LEGS TO 180°",
    cue="SQUEEZE GLUTES &amp; LOW BACK TO HORIZONTAL LINE",
)

# 48. Core 3B: Arch Body Hold / Rocks
DIAGRAMS["arch_hold"] = svg_wrap(
    '<line x1="6" y1="78" x2="74" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(62, 60), shoulder=(52, 66), mid_spine=(38, 73), hip=(26, 70),
        knee=(16, 64), ankle=(6, 58), foot=(4, 63),
        elbow=(42, 60), hand=(30, 58),
        scale=0.66, active_muscle="glutes"
    )
    + '<line x1="86" y1="78" x2="154" y2="78" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(136, 58), shoulder=(126, 65), mid_spine=(114, 73), hip=(102, 70),
        knee=(92, 64), ankle=(82, 58), foot=(80, 63),
        elbow=(138, 54), hand=(150, 48),
        scale=0.66, active_muscle="glutes"
    ),
    label_l="1. ARMS BACK ARCH",
    label_r="2. SUPERMAN ARCH ROCK",
    cue="LIFT CHEST &amp; STRAIGHT THIGHS OFF MAT — LOOK DOWN",
)

# 49. Skill 1: Chest-to-Wall Handstand
DIAGRAMS["handstand"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="12" y1="12" x2="12" y2="82" stroke="#475569" stroke-width="3"/>'
    + athlete_side(
        head=(46, 56), shoulder=(42, 46), hip=(28, 30),
        knee=(20, 26), ankle=(14, 22), foot=(12, 26),
        elbow=(46, 64), hand=(48, 80),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<line x1="138" y1="12" x2="138" y2="82" stroke="#475569" stroke-width="3"/>'
    + athlete_side(
        head=(128, 60), shoulder=(128, 50), hip=(128, 34),
        knee=(129, 24), ankle=(132, 15), foot=(137, 15),
        elbow=(128, 66), hand=(128, 80),
        scale=0.68, active_muscle="shoulders"
    )
    + '<path d="M 114 66 L 114 48" stroke="#16a34a" stroke-width="1.8" marker-end="url(#arr-g)"/>',
    label_l="1. WALK FEET UP WALL",
    label_r="2. CHEST-TO-WALL HOLD",
    cue="SHRUG SHOULDERS TALL — PPT — ONLY TOES TOUCH WALL",
)

# 50. Skill 2: Crow / Crane Pose
DIAGRAMS["crow"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(54, 48), shoulder=(44, 52), mid_spine=(32, 46), hip=(22, 54),
        knee=(40, 62), ankle=(24, 70), foot=(20, 66),
        elbow=(38, 66), hand=(44, 80),
        scale=0.68, active_muscle="shoulders"
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(136, 44), shoulder=(126, 48), mid_spine=(114, 42), hip=(104, 50),
        knee=(122, 58), ankle=(106, 64), foot=(102, 60),
        elbow=(125, 64), hand=(124, 80),
        scale=0.68, active_muscle="shoulders"
    ),
    label_l="1. CROW (BENT ARMS)",
    label_r="2. CRANE (LOCKED ARMS)",
    cue="KNEES ON TRICEPS — LOOK SLIGHTLY AHEAD — GRIP FLOOR",
)

# 51. Skill 3: L-Sit & Compression
DIAGRAMS["lsit"] = svg_wrap(
    '<line x1="6" y1="80" x2="74" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(30, 32), shoulder=(30, 43), hip=(30, 66),
        knee=(46, 54), ankle=(46, 68), foot=(52, 68),
        elbow=(30, 60), hand=(30, 78),
        scale=0.68, active_muscle="core"
    )
    + '<line x1="86" y1="80" x2="154" y2="80" stroke="#64748b" stroke-width="2"/>'
    + athlete_side(
        head=(110, 32), shoulder=(110, 43), hip=(110, 66),
        knee=(128, 66), ankle=(146, 66), foot=(148, 60),
        elbow=(110, 60), hand=(110, 78),
        scale=0.68, active_muscle="core"
    ),
    label_l="1. TUCK L-SIT",
    label_r="2. FULL FLOOR L-SIT",
    cue="PALMS BESIDE HIPS — PUSH SHOULDERS DOWN HARD",
)

# 52. Skill 4: Skin the Cat / German Hang
DIAGRAMS["skin_cat"] = svg_wrap(
    '<circle cx="40" cy="16" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(26, 46), shoulder=(34, 48), mid_spine=(44, 52), hip=(48, 42),
        knee=(36, 34), ankle=(42, 26), foot=(46, 26),
        elbow=(37, 32), hand=(40, 16),
        scale=0.68, active_muscle="core"
    )
    + '<circle cx="120" cy="16" r="3.2" fill="#334155"/>'
    + athlete_side(
        head=(106, 50), shoulder=(114, 48), hip=(120, 66),
        knee=(126, 76), ankle=(132, 83),
        elbow=(117, 32), hand=(120, 16),
        scale=0.68, active_muscle="shoulders"
    ),
    label_l="1. INVERTED TUCK PASS",
    label_r="2. GERMAN HANG STRETCH",
    cue="OVERHAND GRIP — ELBOWS LOCKED 100% STRAIGHT",
)

# 53. Bonus 1: BW Tricep Extensions & Bar Curls
DIAGRAMS["bw_arms"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="58" cy="48" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(54, 54), shoulder=(44, 54), hip=(26, 66),
        knee=(18, 73), ankle=(10, 80), foot=(12, 82),
        elbow=(52, 60), hand=(58, 48),
        scale=0.68, active_muscle="triceps"
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="108" cy="36" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(102, 36), shoulder=(110, 44), hip=(126, 60),
        knee=(136, 70), ankle=(146, 80), foot=(150, 75),
        elbow=(116, 36), hand=(108, 36),
        scale=0.68, active_muscle="shoulders"
    ),
    label_l="1. BW SKULLCRUSHER",
    label_r="2. BAR BICEP CURL",
    cue="FREEZE UPPER ARMS — PIVOT PURELY AT ELBOW JOINT",
)

# 54. Bonus 2: Inverted Face Pulls
DIAGRAMS["face_pull"] = svg_wrap(
    '<line x1="6" y1="82" x2="74" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="28" cy="36" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(18, 52), shoulder=(26, 56), hip=(44, 68),
        knee=(54, 74), ankle=(64, 80), foot=(68, 75),
        elbow=(27, 46), hand=(28, 36),
        scale=0.68
    )
    + '<line x1="86" y1="82" x2="154" y2="82" stroke="#64748b" stroke-width="2"/>'
    + '<circle cx="108" cy="36" r="3" fill="#0f172a"/>'
    + athlete_side(
        head=(102, 34), shoulder=(110, 42), hip=(126, 58),
        knee=(136, 69), ankle=(146, 80), foot=(150, 75),
        elbow=(112, 28), hand=(108, 36),
        scale=0.68, active_muscle="shoulders"
    )
    + '<path d="M 122 28 L 108 22" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arr)"/>',
    label_l="1. WIDE OVERHAND HANG",
    label_r="2. FACE PULL TO FOREHEAD",
    cue="ELBOWS HIGH (90°) — EXTERNALLY ROTATE TO FOREHEAD",
)


HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>/r/bodyweightfitness Recommended Routine — Darebee-Inspired Form &amp; Progression Manual</title>
<style>
  @page {{
    size: A4;
    margin: 8mm 10mm 8mm 10mm;
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
    font-size: 8.1pt;
    line-height: 1.29;
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

  /* Darebee-Inspired Header Banner */
  .hero {{
    background: #0f172a;
    color: #ffffff;
    padding: 9px 14px;
    border-radius: 7px;
    border-bottom: 3.5px solid #dc2626;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .hero h1 {{
    font-size: 13.5pt;
    font-weight: 900;
    letter-spacing: 0.2px;
    text-transform: uppercase;
    margin-bottom: 2px;
  }}
  .hero p {{
    font-size: 7.8pt;
    color: #cbd5e1;
  }}
  .hero-badge {{
    background: #1e293b;
    border: 1px solid #475569;
    border-left: 3px solid #dc2626;
    border-radius: 5px;
    padding: 5px 9px;
    text-align: right;
    font-size: 7.1pt;
    line-height: 1.35;
    white-space: nowrap;
  }}
  .hero-badge strong {{
    color: #f87171;
    font-size: 7.8pt;
  }}

  /* Section Banner */
  .section-bar {{
    background: #0f172a;
    color: #ffffff;
    padding: 4.5px 11px;
    border-radius: 5px;
    border-left: 4px solid #dc2626;
    font-size: 9pt;
    font-weight: 800;
    margin: 5px 0 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    letter-spacing: 0.3px;
  }}
  .section-bar .sub {{
    font-size: 7.2pt;
    font-weight: 500;
    color: #fca5a5;
  }}

  /* Sub-header for Alternate Paths */
  .path-bar {{
    background: #1e293b;
    color: #ffffff;
    padding: 3.5px 10px;
    border-radius: 4px;
    font-size: 7.8pt;
    font-weight: 700;
    margin: 5px 0 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .path-bar span {{
    font-size: 6.9pt;
    font-weight: 400;
    color: #cbd5e1;
  }}

  /* Rules Grid */
  .rules-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-bottom: 5px;
  }}
  .rule-card {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-top: 2.5px solid #dc2626;
    border-radius: 5px;
    padding: 4.5px 7px;
  }}
  .rule-card h4 {{
    font-size: 7.4pt;
    color: #991b1b;
    text-transform: uppercase;
    margin-bottom: 1.5px;
  }}
  .rule-card p {{
    font-size: 6.9pt;
    color: #334155;
  }}

  /* Move Grid (2 columns of detailed Darebee-style cards) */
  .move-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
    margin-bottom: 4px;
  }}
  .move-card {{
    border: 1.2px solid #cbd5e1;
    border-radius: 6px;
    padding: 5.5px 7px;
    background: #ffffff;
    display: flex;
    gap: 7px;
    align-items: flex-start;
    page-break-inside: avoid;
  }}
  .move-card.highlight {{
    border: 1.5px solid #0f172a;
    background: #fcfcfd;
  }}
  .move-svg {{
    width: 142px;
    height: 89px;
    flex-shrink: 0;
    border: 1.2px solid #94a3b8;
    border-radius: 5px;
    overflow: hidden;
  }}
  .move-body {{
    flex: 1;
    min-width: 0;
  }}
  .move-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2px;
    gap: 4px;
  }}
  .move-title-row h3 {{
    font-size: 7.9pt;
    font-weight: 800;
    color: #0f172a;
  }}
  .pill {{
    background: #0f172a;
    color: #ffffff;
    font-size: 6.2pt;
    font-weight: 700;
    padding: 1px 4.5px;
    border-radius: 3px;
    white-space: nowrap;
  }}
  .pill.red {{ background: #dc2626; }}
  .pill.green {{ background: #15803d; }}
  .pill.blue {{ background: #1d4ed8; }}

  .move-body ul {{
    padding-left: 10px;
    font-size: 6.95pt;
    color: #1e293b;
  }}
  .move-body li {{
    margin-bottom: 1.2px;
  }}
  .good {{
    color: #15803d;
    font-weight: 700;
  }}
  .bad {{
    color: #b91c1c;
    font-weight: 700;
  }}
  .note-bar {{
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-left: 3.5px solid #dc2626;
    border-radius: 4px;
    padding: 5px 9px;
    font-size: 7pt;
    color: #1e293b;
    margin-top: 4px;
  }}
</style>
</head>
<body>

<!-- ==================== PAGE 1: RULES, BODY MECHANICS & WARM-UP ==================== -->
<div class="page">
  <div class="hero">
    <div>
      <h1>Recommended Routine (RR) — Visual Form Guide</h1>
      <p>Darebee-Inspired Two-Step Anatomical Diagrams (1. Start &rarr; 2. Finish), Form Cues &amp; All Alternate Pathways</p>
    </div>
    <div class="hero-badge">
      <strong>9 Exercises (3 Pairs + 1 Triplet)</strong><br>
      Frequency: <strong>3x / Week Full Body</strong><br>
      Tempo: <strong>1-0-X-0</strong> | Sets: <strong>3 &times; 5–8 (1 RIR)</strong>
    </div>
  </div>

  <!-- 3 Official RR Rules -->
  <div class="rules-grid">
    <div class="rule-card">
      <h4>1. Pairing &amp; Triplet Structure</h4>
      <p><strong>Pairs (1–3):</strong> Set 1 of Ex A &rarr; Rest 90s &rarr; Set 1 of Ex B &rarr; Rest 90s &rarr; Repeat for 3 sets.<br>
      <strong>Core Triplet:</strong> Ex 1 &rarr; 60s &rarr; Ex 2 &rarr; 60s &rarr; Ex 3 &rarr; 60s &times; 3 rounds. (Rest up to 3m if needed).</p>
    </div>
    <div class="rule-card">
      <h4>2. Tempo (1-0-X-0) &amp; Failure-1</h4>
      <p><strong>1s</strong> down, <strong>0s</strong> bottom pause, <strong>X</strong> explode up, <strong>0s</strong> top pause. Stop <strong>1 rep short of failure</strong> on Sets 1–2 (e.g., <strong>7-7-7</strong> instead of 8-6-5) to maximize clean volume.</p>
    </div>
    <div class="rule-card">
      <h4>3. Progression &amp; Red Highlights</h4>
      <p>Start a level where you can do <strong>5,5,5</strong>. Build to <strong>8,8,8</strong>, then level up! <strong style="color:#dc2626">Red muscle shading</strong> in each diagram shows the primary target muscles &amp; motion vector.</p>
    </div>
  </div>

  <!-- Fundamental Body Positions -->
  <div class="section-bar">
    <span>PART 0: FUNDAMENTAL BODY MECHANICS (REQUIRED FOR ALL MOVES)</span>
    <span class="sub">Master Hollow Body (PPT) &amp; Scapular Control</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["hollow"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Hollow Body &amp; Posterior Pelvic Tilt (PPT)</h3>
          <span class="pill red">Core Lock</span>
        </div>
        <ul>
          <li><strong>How to Lock In:</strong> Tuck your tailbone under (pull belt buckle toward chin), squeeze glutes 100%, and pull lower ribs down into abs.</li>
          <li><span class="good">&#10003; Good:</span> Rigid cylinder from shoulders to ankles on Push-Ups, Rows, Pull-Ups, Dips, and Rollouts.</li>
          <li><span class="bad">&#10007; Avoid:</span> Banana-back arch (flared ribs, sagging belly).</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["scapula"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>4 Scapular Positions (Shoulder Control)</h3>
          <span class="pill red">Joint Safety</span>
        </div>
        <ul>
          <li><strong>Depress (Down):</strong> Pull shoulders away from ears (Pull-Ups, Dips, Support).</li>
          <li><strong>Retract (Pinch Back):</strong> Pinch blades together (top of Rows, Arch Hangs).</li>
          <li><strong>Protract (Push Apart):</strong> Spread blades wide (top of Push-Ups, Rollouts).</li>
          <li><strong>Elevate (Shrug Up):</strong> Push shoulders into ears (Handstands).</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- PART 1: DYNAMIC WARM-UP (ALL 8 MOVES) -->
  <div class="section-bar">
    <span>PART 1: DYNAMIC WARM-UP — ALL 8 EXERCISES (5–10 MINS)</span>
    <span class="sub">Do Moves 1–6 Every Session + Moves 7–8 Before Squat/Hinge Pairs</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["yuri"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>1. Yuri's Shoulder Band / Towel Warmup</h3>
          <span class="pill">5–10 Reps</span>
        </div>
        <ul>
          <li>Hold a band, towel, or broomstick with a wide overhand grip.</li>
          <li>Keep <strong>elbows 100% locked</strong>, shrug slightly overhead, pass behind back to glutes, then reverse smoothly.</li>
          <li><span class="good">&#10003; Good:</span> Ribs tucked down. <span class="bad">&#10007; Bad:</span> Bending elbows.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["sky_reach"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>2. Squat Sky Reaches</h3>
          <span class="pill">5–10 / Side</span>
        </div>
        <ul>
          <li>Sit into a deep squat with heels flat on the floor. Grab left ankle with left hand, pinning left knee outward with elbow.</li>
          <li>Rotate upper back and reach right arm straight to the sky, following fingertips with eyes.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["wrist_prep"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>3. GMB Wrist Prep (4 Directions)</h3>
          <span class="pill">10+ Reps</span>
        </div>
        <ul>
          <li>On all fours with <strong>elbows locked straight</strong> and fingers spread wide:</li>
          <li><strong>(1)</strong> Fingers forward, lean shoulders past fingertips; <strong>(2)</strong> Fingers facing knees, sit hips back; <strong>(3)</strong> Back of hands on floor; <strong>(4)</strong> First-knuckle palm pulses.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["deadbug"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>4. Deadbugs</h3>
          <span class="pill">30 Seconds</span>
        </div>
        <ul>
          <li>Lie on back, arms vertical, knees 90&deg;. <strong>Crush lower back flat into the floor</strong> (posterior pelvic tilt).</li>
          <li>Extend opposite arm and leg just above floor while exhaling. <span class="bad">&#10007; Stop if</span> lower back arches off mat!</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["arch_hang"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>5. Arch Hangs (Add after Negative Pull-Ups)</h3>
          <span class="pill">10 Reps</span>
        </div>
        <ul>
          <li>Hang from pull-up bar with locked straight arms. Pull shoulder blades <strong>down and together</strong>, lifting sternum toward the ceiling.</li>
          <li><span class="good">&#10003; Good:</span> Arch upper back while keeping abs braced.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["support_hold"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>6–8. Support Hold + Warm-Up Squat/Hinge</h3>
          <span class="pill">30s + 10 Reps</span>
        </div>
        <ul>
          <li><strong>6. Parallel Bar Support Hold (30s):</strong> Lock elbows, push shoulders down away from ears, hollow body.</li>
          <li><strong>7 &amp; 8. Easier Squat &amp; Hinge (10 reps each):</strong> Warm up knees &amp; hamstrings before Bulgarian Split Squats / Nordics.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 2: PAIR 1A — PULL-UP PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 1A: PULL-UP PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps | Tempo: 1-0-X-0 | Pair with Squats (90s Rest Between Exercises)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR PULL-UP PROGRESSION (LEVELS 1 TO 5)</div>
    <span>Primary Muscles Highlighted in Red: Latissimus Dorsi, Lower Traps, Rhomboids, Biceps</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["scap_pull"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Scapular Pulls</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Hang from bar with overhand shoulder-width grip and <strong>locked elbows</strong>.</li>
          <li>Without bending elbows, pull shoulder blades down away from ears (reverse shrug) so body rises 2–3 inches. Pause 1–2s at top, lower smoothly.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["arch_hang"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 2: Arch Hangs</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Perform a Scapular Pull, then continue retracting shoulder blades to <strong>arch your upper back</strong> until your sternum faces the bar/ceiling.</li>
          <li>Keep elbows locked straight and abs/glutes tight. Build to <strong>3&times;8</strong> with 2s top pauses.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["neg_pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Negative Pull-Ups</h3>
          <span class="pill">3 &times; 5–8 (3–5s)</span>
        </div>
        <ul>
          <li>Use a chair or jump to the top position (chin over bar, chest touching bar, shoulders depressed).</li>
          <li>Hold top for <strong>1s</strong>, then lower at an <strong>even pace over 3–5 seconds</strong> to a full dead hang. Build to 3&times;8 controlled 5s reps.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: Full Pull-Ups (or Chin-Ups)</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Start in a dead hang (elbows locked). Lock legs straight in a <strong>hollow body</strong> slightly in front of torso.</li>
          <li>Depress scapulae and drive elbows down into your ribs until chin clears bar (or upper chest touches bar). Lower under control to full lockout.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>LEVEL 5 &amp; ALL OFFICIAL ALTERNATE PULL-UP PATHWAYS (WEIGHTED vs. BODYWEIGHT / BWF WIKI)</div>
    <span>Choose Your Path After Mastering 3&times;8 Clean Pull-Ups</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["lsit_pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path A: L-Sit Pull-Ups (Equipment-Free)</h3>
          <span class="pill green">3 &times; 5–8</span>
        </div>
        <ul>
          <li>From a dead hang, lift straight legs to a <strong>90&deg; horizontal L-Sit</strong> (or start with a <strong>Tuck L-Sit</strong>).</li>
          <li>Hold the L-Sit strictly horizontal throughout every pull-up. Shifts center of gravity forward for massive lat &amp; core overload without weights.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["weighted_pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path B: Weighted Pull-Ups (PDF Summary Path)</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Attach external weight via a dip belt, weight vest, or dumbbell held between ankles/thighs.</li>
          <li>Start light (+2.5 kg), build from <strong>3&times;5 &rarr; 3&times;8</strong> with full chest-to-bar range of motion, then increase load.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["arch_pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path C: Chest-to-Bar &amp; Arch Hanger Pull-Ups</h3>
          <span class="pill blue">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>High Chest-to-Bar:</strong> Pull explosively so the bar touches your lower sternum below the pecs.</li>
          <li><strong>Arch Hanger Pull-Ups:</strong> Lock in an Arch Hang and pull your sternum to the bar while <strong>maintaining that 45&deg; thoracic arch</strong> all the way up and down.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["archer_pullup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path D: Typewriter &amp; Archer Pull-Ups</h3>
          <span class="pill blue">3 &times; 5–8 / Side</span>
        </div>
        <ul>
          <li><strong>Typewriter Pull-Ups:</strong> Pull chin above wide bar, slide horizontally left-to-right across the bar keeping chin above bar level, then lower.</li>
          <li><strong>Archer Pull-Ups:</strong> Pull toward one hand while keeping the opposite arm <strong>100% locked straight</strong> on the bar (or on a towel).</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 3: PAIR 1B — SQUAT PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 1B: SQUAT PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps / Leg | Tempo: 1-0-X-0 | Pair with Pull-Ups (90s Rest)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR SQUAT PROGRESSION (LEVELS 1 TO 6 — SHRIMP SQUAT PATHWAY)</div>
    <span>Primary Muscles Highlighted in Red: Quadriceps, Gluteus Maximus, Gluteus Medius, Adductors</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["squat"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Assisted Squat &rarr; Level 2: Squat</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Level 1 (Assisted):</strong> Hold a post/frame in front of you for balance as you sit into a full-depth squat.</li>
          <li><strong>Level 2 (Full Squat):</strong> Feet shoulder-width, toes out 15–30&deg;. Track knees over toes until <strong>hip crease drops below knee height</strong> with flat back and flat heels.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["bss"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Split Squat &rarr; Bulgarian Split Squat</h3>
          <span class="pill red">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li><strong>Split Squat (Wiki Lvl 3a):</strong> Stationary lunge with both feet on floor; rear knee kisses floor.</li>
          <li><strong>Bulgarian Split Squat (PDF Lvl 3):</strong> Elevate rear foot (laces down) on a chair behind you. Lower under control until rear knee nearly touches floor; match torso lean to front shin angle.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["beg_shrimp"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: Beginner Shrimp Squat</h3>
          <span class="pill red">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li>Stand on one leg, lift non-working foot behind you (knee bent 90&deg;), and reach arms forward for counterbalance.</li>
          <li>Squat down until your <strong>rear knee and rear toes touch the floor at the exact same time</strong>, then drive up through the front mid-foot.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["adv_shrimp"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 5: Intermediate &rarr; Level 6: Adv. Shrimp</h3>
          <span class="pill">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li><strong>Level 5 (Intermediate Shrimp):</strong> Hold rear ankle behind you with <strong>one hand</strong>. Lower until <strong>only your rear knee kisses the floor</strong> (rear foot stays in the air).</li>
          <li><strong>Level 6 (Advanced Shrimp):</strong> Hold rear ankle behind your back with <strong>BOTH hands</strong> as rear knee kisses floor.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>ALL OFFICIAL ALTERNATE SQUAT PATHWAYS (PISTOL SQUATS, DEEP STEP-UPS &amp; BARBELL SQUATS)</div>
    <span>Can Be Used Alongside or Instead of Shrimp Squats at Levels 4–6</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["pistol"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path A: Pistol Squat Progression</h3>
          <span class="pill green">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li><strong>Step 1 (Box Pistol):</strong> Sit back on one leg to touch a chair while extending free leg straight ahead; lower surface height over time.</li>
          <li><strong>Step 2 (Counterbalanced / Assisted):</strong> Hold a light book/weight forward or lightly touch a doorframe at the bottom.</li>
          <li><strong>Step 3 (Full Pistol Squat):</strong> Descend until hamstring rests on calf with working heel glued flat to the floor.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["step_up"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path B: Deep Step-Ups &amp; Barbell Squats</h3>
          <span class="pill blue">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li><strong>Deep Step-Ups (Wiki Alternate):</strong> Place working foot on a high box/chair. Lean torso over front knee and press all the way up. <strong>Crucial Rule:</strong> Pull bottom toes UP (dorsiflexion) so the rear leg cannot push off the floor!</li>
          <li><strong>Barbell Back / Front Squat (Gym Alternate):</strong> If a barbell is available, perform 3&times;5–8 Barbell Squats.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 4: PAIR 2A — DIP PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 2A: DIP PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps | Tempo: 1-0-X-0 | Pair with Hinges (90s Rest Between Exercises)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR DIP PROGRESSION (LEVELS 1 TO 4)</div>
    <span>Primary Muscles Highlighted in Red: Pectoralis Major, Anterior Deltoids, Triceps Brachii</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["support_hold"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Parallel Bar Support Hold</h3>
          <span class="pill">Build to 60s</span>
        </div>
        <ul>
          <li>Jump to straight-arm support on parallel bars. Lock elbows 100% and push shoulders down away from ears (<strong>scapular depression</strong>).</li>
          <li>Squeeze glutes and hold a hollow body for a solid <strong>60-second hold</strong> before progressing.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["dip"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 2: Negative Dips</h3>
          <span class="pill">3 &times; 5–8 (3–5s)</span>
        </div>
        <ul>
          <li>Start in top Support Hold. Lean torso slightly forward (~15&deg;), keep forearms vertical, and lower slowly over <strong>3–5 seconds</strong> until shoulders drop below elbow level.</li>
          <li>Step onto floor/box to return to top support for each rep.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["dip"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Parallel Bar Dips</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Lower under control with elbows tucked close to sides and forearms vertical until your shoulder crease passes elbow height (90&deg;+ bend).</li>
          <li>Press forcefully back to locked elbows and depressed shoulders at the top. Keep legs straight (not crossed behind butt).</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["lsit_dip"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: L-Sit Dips OR Weighted Dips</h3>
          <span class="pill green">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Bodyweight Path (L-Sit Dips):</strong> Hold legs straight out in front (Tuck L-Sit &rarr; Full L-Sit) throughout the entire dip set.</li>
          <li><strong>Weighted Path (Weighted Dips):</strong> Add weight progressively on a dip belt (+2.5 kg increments) once 3&times;8 dips are clean.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>ALL OFFICIAL ALTERNATE DIP PATHWAYS (RING DIPS &amp; OVERHEAD HANDSTAND PUSH-UP PATH)</div>
    <span>Wiki Alternates for Gymnastic Rings OR Overhead Pressing Replacement</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["ring_dip"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path A: Ring Support &rarr; Ring Dips &rarr; Bulgarian</h3>
          <span class="pill blue">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Prerequisite:</strong> 60s Ring Support Hold with Rings Turned Out (RTO 45&deg;).</li>
          <li><strong>Ring Dips:</strong> Keep rings tight against ribs as you lower to 90&deg;, press up, and turn rings out (RTO) at the top of every rep.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["pike_hspu"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path B: Overhead HSPU Path (No Dip Bars)</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Official RR replacement if you lack dip bars: <strong>Lvl 1: Floor Pike Push-Ups</strong> &rarr; <strong>Lvl 2: Box-Elevated Pike Push-Ups</strong> &rarr; <strong>Lvl 3–4: Wall Headstand Push-Ups (HeSPU)</strong>.</li>
          <li><span class="good">&#10003; Crucial Cue:</span> Lean forward at bottom so your head lands <strong>in front of your hands</strong> forming an Equilateral Tripod Triangle!</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 5: PAIR 2B — HINGE PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 2B: HINGE PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps | Tempo: 1-0-X-0 | Pair with Dips (90s Rest Between Exercises)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR HINGE PROGRESSION (LEVELS 1 TO 5 — RDL TO NORDIC CURL PATHWAY)</div>
    <span>Primary Muscles Highlighted in Red: Hamstrings (Biceps Femoris, Semitendinosus), Glutes, Erectors</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["rdl"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Romanian Deadlift (Two-Leg Hip Hinge)</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Stand hip-width apart. Unlock knees slightly (~15&deg;) and freeze shins vertical.</li>
          <li>Brace core and <strong>push your hips straight back toward the wall behind you</strong> until your flat torso reaches parallel with the floor. Squeeze glutes to return.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["sl_rdl"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 2: Single-Legged Deadlift (SL-RDL)</h3>
          <span class="pill red">3 &times; 5–8 / Leg</span>
        </div>
        <ul>
          <li>Balance on one leg with a soft 15&deg; knee bend. Hinge at the hip while extending your non-working leg straight behind you like a seesaw into a <strong>Capital "T"</strong>.</li>
          <li><span class="good">&#10003; Crucial Cue:</span> Point the toes of your raised back foot <strong>straight down at the floor</strong> to keep your hips square!</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["nordic"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Banded / Eccentric Nordic Negatives</h3>
          <span class="pill red">3 &times; 5–8 (4–5s)</span>
        </div>
        <ul>
          <li>Kneel on a pad with ankles anchored firmly under a heavy couch, bed frame, or strap.</li>
          <li>Squeeze glutes into PPT so <strong>knees, hips, and shoulders form one straight line</strong>. Lower slowly over <strong>4–5 seconds</strong> toward the floor, catch gently with hands, and push back up.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["nordic"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: Banded Nordic &rarr; Level 5: Full Nordic Curl</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Level 4 (Banded / Assisted Nordic):</strong> Hold a band anchored behind you (or slide hands over an elevated box) to assist the bottom reversal.</li>
          <li><strong>Level 5 (Full Nordic Curl):</strong> Lower to the floor and curl your entire bodyweight back up using pure hamstring knee flexion with zero hip bend.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>ALL OFFICIAL ALTERNATE HINGE PATHWAYS (SLIDING HAMSTRING CURLS &amp; HIP THRUSTS)</div>
    <span>100% Equipment-Free Bridges Between Level 2 (SL-RDL) and Level 3–5 (Nordic Curls)</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["sliding_curl"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path A: Slick Floor / Towel Hamstring Curls</h3>
          <span class="pill green">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Lie on back on a wood/tile floor with heels on a folded towel. Bridge hips up, slide heels out until legs are nearly straight, then <strong>dig heels down and curl them back under your glutes</strong> while keeping hips bridged high.</li>
          <li><strong>Progression:</strong> Two-Leg Sliding Curl &rarr; Single-Leg Sliding Hamstring Curl.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["hip_thrust"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path B: Single-Leg Hip Thrust &amp; Harop Curl</h3>
          <span class="pill blue">3 &times; 8–12</span>
        </div>
        <ul>
          <li><strong>Single-Leg Shoulder-Elevated Hip Thrust:</strong> Rest upper back on couch edge, plant one foot so shin is <strong>vertical at top</strong>, tuck chin, and drive hips to full glute lockout (2s pause).</li>
          <li><strong>Harop Curl:</strong> Nordic curl with a slight hip hinge on the descent to bridge the gap to strict Nordics.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 6: PAIR 3A — ROW PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 3A: ROW PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps | Tempo: 1-0-X-0 | Pair with Push-Ups (90s Rest Between Exercises)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR ROW PROGRESSION (LEVELS 1 TO 5)</div>
    <span>Primary Muscles Highlighted in Red: Mid-Traps, Rhomboids, Rear Delts, Lats, Biceps</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["incline_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Vertical Row &rarr; Level 2: Incline Row</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Level 1 (Vertical):</strong> Stand facing a post/doorframe with feet close to base; lean back and pull chest to hands.</li>
          <li><strong>Level 2 (Incline Row):</strong> Use a chest-high bar at ~45&deg; body angle. Keep body rigid and pull chest to bar.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["horiz_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Horizontal Rows (Inverted Row)</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Hang under a waist-high bar with heels on the floor and body in a straight reverse plank (glutes squeezed).</li>
          <li>Depress shoulders, retract shoulder blades, and drive elbows back (~45&deg;) until your <strong>lower chest physically touches the bar</strong>.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["elev_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: Wide Rows &amp; Feet-Elevated Rows</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Wide Rows (PDF Lvl 4):</strong> Grip 1.5&times; shoulder width and flare elbows out at <strong>90&deg;</strong>, pulling upper chest to bar (hits rear delts &amp; upper back).</li>
          <li><strong>Feet-Elevated Rows:</strong> Prop heels on a chair at bar height so body is horizontal at the top.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["weighted_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 5A: Weighted Inverted Rows (PDF Path)</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Wear a weight vest or rest a weight plate on your chest (never on your belly where it causes hip sag).</li>
          <li>Pull chest all the way to the bar on every rep with full scapular retraction.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>ALL OFFICIAL ALTERNATE ROW PATHWAYS (ARCHER / ONE-ARM ROWS &amp; FRONT LEVER ROWS)</div>
    <span>100% Bodyweight Mastery Pathways After Level 4 Horizontal / Wide Rows</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["archer_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path A: Archer Rows &rarr; One-Arm Rows</h3>
          <span class="pill green">3 &times; 5–8 / Side</span>
        </div>
        <ul>
          <li><strong>Archer Rows:</strong> Row up with one arm while keeping the assisting arm <strong>100% locked straight</strong> out to the side.</li>
          <li><strong>One-Arm Rows:</strong> Hold bar with one hand, take a wider foot stance, and row chest to bar while keeping shoulders and hips completely square.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["tuck_fl_row"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path B: Tuck Front Lever Pulls &amp; Rows</h3>
          <span class="pill blue">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Done on Pull-Up Bar!</strong> Hang from bar, tuck knees to chest, and press down with straight arms until your <strong>back is horizontal to the floor in mid-air</strong>.</li>
          <li>From that horizontal hang, row your hips/chest up toward the bar while keeping your torso parallel to the floor!</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 7: PAIR 3B — PUSH-UP PROGRESSION & ALL ALTERNATES ==================== -->
<div class="page">
  <div class="section-bar">
    <span>STRENGTH PAIR 3B: PUSH-UP PROGRESSION — MAIN LADDER &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">3 Sets &times; 5–8 Reps | Tempo: 1-0-X-0 | Pair with Rows (90s Rest Between Exercises)</span>
  </div>

  <div class="path-bar">
    <div>MAIN RR PUSH-UP PROGRESSION (LEVELS 1 TO 5)</div>
    <span>Primary Muscles Highlighted in Red: Pectoralis Major, Anterior Delts, Triceps, Serratus Anterior</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["incline_pushup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 1: Vertical &rarr; Level 2: Incline Push-Up</h3>
          <span class="pill">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Place hands on an elevated surface (wall &rarr; counter &rarr; table &rarr; chair) rather than doing knee push-ups so you train full-body hollow tension.</li>
          <li>Lower until sternum touches the edge with elbows tucked ~45&deg;, then press to full protraction.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["pushup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 3: Full Push-Up</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Hands shoulder-width, externally rotate arms ("screw hands into floor"). Lock pelvis in <strong>Posterior Pelvic Tilt (PPT)</strong>.</li>
          <li>Lower with elbows at a <strong>45&deg; arrow angle</strong> until chest touches floor. Press up and <strong>protract scapulae</strong> at top.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["diamond_pushup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 4: Diamond Push-Up</h3>
          <span class="pill red">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Place hands close together directly underneath your sternum so index fingers and thumbs form a diamond (or sit 1–2" apart).</li>
          <li>Keep elbows brushing your ribs as your chest lowers onto your hands, then press to full lockout and protraction.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["pppu"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Level 5: Pseudo Planche Push-Up (PPPU)</h3>
          <span class="pill green">3 &times; 5–8</span>
        </div>
        <ul>
          <li>Turn fingers <strong>45–90&deg; outward</strong> (or backward). <strong>Lean shoulders far forward past your wrists</strong> so hands sit down near your waist/hips.</li>
          <li><span class="good">&#10003; Crucial Rule:</span> Maintain that forward shoulder lean at both bottom AND top without rocking backward!</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>ALL OFFICIAL ALTERNATE PUSH-UP PATHWAYS (ARCHER / ONE-ARM PUSH-UPS &amp; RING PUSH-UPS)</div>
    <span>Wiki Alternates for Unilateral Pushing Strength OR Gymnastic Rings</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["archer_pushup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path A: Archer &rarr; One-Arm Push-Up</h3>
          <span class="pill blue">3 &times; 5–8 / Side</span>
        </div>
        <ul>
          <li><strong>Archer Push-Ups:</strong> Hands 2&times; shoulder width. Shift weight over one hand and lower chest to that hand while keeping the <strong>assisting arm 100% locked straight</strong>.</li>
          <li><strong>One-Arm Push-Up:</strong> Straddle feet wide, place one hand under sternum, keep hips/shoulders square, and press with one arm.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["ring_pushup"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Alt Path B: Ring Push-Ups &rarr; RTO Push-Ups</h3>
          <span class="pill blue">3 &times; 5–8</span>
        </div>
        <ul>
          <li><strong>Ring Push-Ups:</strong> Lower into a deep chest stretch on floor-level rings, press up, and <strong>Turn Rings Out (RTO 45–90&deg;)</strong> at the top.</li>
          <li><strong>RTO Push-Ups / Ring PPPU:</strong> Keep rings turned out (palms forward) throughout the entire descent AND ascent.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 8: CORE TRIPLET — ALL MAIN & ALTERNATE PATHWAYS ==================== -->
<div class="page">
  <div class="section-bar">
    <span>PART 3: CORE TRIPLET — ALL 3 CATEGORIES &amp; ALL ALTERNATE PATHWAYS</span>
    <span class="sub">Circuit: Do C1 &rarr; 60s Rest &rarr; C2 &rarr; 60s Rest &rarr; C3 &rarr; 60s Rest &times; 3 Rounds (Target: 3 &times; 8–12 or 30s)</span>
  </div>

  <div class="path-bar">
    <div>CORE 1: ANTI-EXTENSION PROGRESSION (RING/TOWEL AB ROLLOUTS OR HANGING LEG RAISES)</div>
    <span>Resists Lumbar Hyperextension &amp; Strengthens Rectus Abdominis, Transverse Abdominis &amp; Lats</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["ab_rollout"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path A: Plank &rarr; Ring / Towel Ab Rollouts</h3>
          <span class="pill red">3 &times; 8–12</span>
        </div>
        <ul>
          <li><strong>Lvl 1: RKC Plank (30s):</strong> Forearm plank with glutes/quads squeezed 100% and tailbone tucked (PPT).</li>
          <li><strong>Lvl 2–4: Kneeling Ab Rollouts (Rings, Wheel, or Towel on Slick Floor):</strong> Lock pelvis in PPT, slide hands forward only as far as lower back stays flat/hollow, then pull back through lats &amp; abs.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["leg_raise"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path B: Hanging Knee / Leg Raises (Toes-to-Bar)</h3>
          <span class="pill green">3 &times; 8–12</span>
        </div>
        <ul>
          <li><strong>Progression:</strong> Lying Tuck &rarr; <strong>Hanging Knee Raises</strong> &rarr; <strong>Hanging Straight-Leg Raises (90&deg;)</strong> &rarr; <strong>Toes-to-Bar</strong>.</li>
          <li><span class="good">&#10003; Crucial Cue:</span> At the top of every rep, <strong>curl your tailbone/pelvis upward</strong> so your lower back rounds and your abs contract fully. Zero swinging!</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>CORE 2: ANTI-ROTATION PROGRESSION (BANDED PALLOF PRESS OR COPENHAGEN / SIDE PLANK)</div>
    <span>Resists Torso Twist &amp; Lateral Pelvic Drop — Obliques, Quadratus Lumborum, Glute Medius, Adductors</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["pallof"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path A: Banded Pallof Press (or Ring Pallof)</h3>
          <span class="pill">3 &times; 8–12 / Side</span>
        </div>
        <ul>
          <li>Stand sideways to a chest-high band anchor, pull band to sternum, press straight out in front of chest, pause 2s resisting rotation, and return.</li>
          <li>Can also be performed as a single-arm Ring Pallof plank rollout.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["copenhagen"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path B: Side Plank &rarr; Copenhagen Side Plank</h3>
          <span class="pill green">3 &times; 8–12 or 30s</span>
        </div>
        <ul>
          <li><strong>100% Equipment-Free Path:</strong> Start with <strong>Side Plank (30s/side)</strong> with elbow directly under shoulder.</li>
          <li><strong>Copenhagen Plank (Knee &rarr; Ankle Lever):</strong> Rest top knee or top ankle on a chair seat, drive hips up into a straight line, and lift bottom leg off the floor for <strong>30s holds or 8–12 hip lifts</strong>.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>CORE 3: EXTENSION PROGRESSION (REVERSE HYPEREXTENSION OR ARCH BODY HOLDS / ROCKS)</div>
    <span>Strengthens Posterior Chain — Spinal Erectors, Multifidus, Gluteus Maximus, Upper Back</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["rev_hyper"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path A: Reverse Hyperextension (PDF Path)</h3>
          <span class="pill red">3 &times; 8–12</span>
        </div>
        <ul>
          <li>Lie prone on a sturdy table, counter, or high bed with your <strong>hip crease right on the edge</strong> so legs hang down. Grip sides firmly.</li>
          <li>Squeeze <strong>glutes + lower back</strong> to lift straight legs until parallel with torso (180&deg;). Pause 1s at top, lower slowly.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["arch_hold"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Path B: Arch Body Hold &rarr; Arch Body Rocks</h3>
          <span class="pill green">3 &times; 30s / 8–12</span>
        </div>
        <ul>
          <li><strong>Floor Alternate:</strong> Lie face down on floor. Squeeze glutes, lock knees, and lift chest, arms, and thighs off floor so only belly rests on mat.</li>
          <li><strong>Progression:</strong> Arms behind back &rarr; Arms overhead (Superman) &rarr; <strong>Arch Body Rocks</strong>.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PAGE 9: SKILL DAY ROUTINE & PHASE 2 BODYWEIGHT ISOLATION ==================== -->
<div class="page">
  <div class="section-bar">
    <span>PART 4: OFFICIAL RR SKILL DAY ROUTINE &amp; PHASE 2 BODYWEIGHT ISOLATION MOVES</span>
    <span class="sub">Practiced on Rest Days (e.g., Sunday) OR Before Strength Work</span>
  </div>

  <div class="path-bar">
    <div>OFFICIAL /R/BODYWEIGHTFITNESS SKILL DAY MOVES (BALANCE, COMPRESSION &amp; SHOULDER MOBILITY)</div>
    <span>Focus on Motor Control &amp; Balance — Stop Before Fatigue!</span>
  </div>

  <div class="move-grid">
    <div class="move-card highlight">
      {DIAGRAMS["handstand"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>1. Wall Plank &rarr; Chest-to-Wall Handstand</h3>
          <span class="pill red">5–10 Min Practice</span>
        </div>
        <ul>
          <li>Walk feet up the wall facing the wall until hands are 2–4" from baseboard (<strong>Chest-to-Wall</strong>, never back-to-wall).</li>
          <li><strong>3 Key Cues:</strong> <strong>(1)</strong> Push floor away to <strong>elevate shoulders into ears</strong>; <strong>(2)</strong> Lock pelvis in <strong>PPT</strong>; <strong>(3)</strong> Press fingertips into floor ("heel pulls") to float toes off wall.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["crow"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>2. Frog Stand / Crow Pose &rarr; Crane Pose</h3>
          <span class="pill">5 Min Practice</span>
        </div>
        <ul>
          <li>Place palms shoulder-width on floor, rest knees on backs of triceps, and lean shoulders forward until feet float up. Look slightly ahead on floor.</li>
          <li><strong>Crane Pose Upgrade:</strong> Perform with <strong>100% locked straight elbows</strong> and strong scapular protraction.</li>
        </ul>
      </div>
    </div>

    <div class="move-card highlight">
      {DIAGRAMS["lsit"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>3. L-Sit Progression &amp; Pike Compression</h3>
          <span class="pill red">60s Total Hold</span>
        </div>
        <ul>
          <li><strong>Floor/Bar L-Sit:</strong> Sit tall, place palms beside hips, lock elbows, and push shoulders DOWN hard to lift hips &amp; legs.</li>
          <li><strong>Levels:</strong> Foot-Supported &rarr; 1-Leg Supported &rarr; Tuck L-Sit &rarr; Full L-Sit (+ 3&times;10s Seated Pike Leg Lifts).</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["skin_cat"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>4. Skin the Cat &amp; German Hang (Pull-Up Bar)</h3>
          <span class="pill">2–3 &times; 3–5 Reps</span>
        </div>
        <ul>
          <li>Hang with an <strong>overhand grip</strong> and locked elbows. Tuck knees to chest and invert backward through your arms.</li>
          <li>Lower slowly into a mild shoulder-extension stretch (<strong>German Hang</strong>), then pull hips up and rotate back to dead hang.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="path-bar">
    <div>BONUS (FROM PROGRAM.MD): 5-MINUTE BODYWEIGHT V-TAPER &amp; ARM ISOLATION FINISHER</div>
    <span>Optional Post-RR Finisher (2–3 Sets &times; 10–15 Reps — Zero Dumbbells or Bands Required)</span>
  </div>

  <div class="move-grid">
    <div class="move-card">
      {DIAGRAMS["bw_arms"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Bodyweight Tricep Extensions &amp; Bar Bicep Curls</h3>
          <span class="pill blue">2–3 &times; 10–15</span>
        </div>
        <ul>
          <li><strong>BW Tricep Extensions (Skullcrushers):</strong> Incline plank on bar; freeze upper arms and bend ONLY at elbows to lower forehead under bar, then extend.</li>
          <li><strong>Underhand Bar Bicep Curls:</strong> Hang under row bar with supinated grip; keep elbows high in front of torso and curl forehead to bar.</li>
        </ul>
      </div>
    </div>

    <div class="move-card">
      {DIAGRAMS["face_pull"]}
      <div class="move-body">
        <div class="move-title-row">
          <h3>Inverted Face Pulls &amp; Side-Plank Powell Raises</h3>
          <span class="pill blue">2–3 &times; 12–15</span>
        </div>
        <ul>
          <li><strong>Wide-Grip Inverted Face Pulls:</strong> Lean back on row bar at 45&deg;, flare elbows high (90&deg;), and externally rotate shoulders to pull bar to your <strong>forehead</strong> (1s pause).</li>
          <li><strong>Side-Plank Powell Raise / Wall Lateral Press:</strong> Isolate lateral &amp; rear delts with zero equipment.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="note-bar">
    <strong>Darebee-Inspired RR Form Manual:</strong> Every move features 2-step anatomical vector poses (<strong>1. Start &rarr; 2. Finish</strong>), <strong style="color:#dc2626">Red Target Muscle Shading</strong>, directional motion vectors, and bottom cue banners.
  </div>
</div>

</body>
</html>
"""


def main():
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"Wrote {HTML_PATH}")

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={PDF_PATH}",
        "--no-pdf-header-footer",
        f"file://{HTML_PATH}",
    ]
    subprocess.run(cmd, check=True)
    shutil.copyfile(PDF_PATH, PDF_ALIAS_PATH)
    print(f"Generated {PDF_PATH} and {PDF_ALIAS_PATH} ({os.path.getsize(PDF_PATH)} bytes)")


if __name__ == "__main__":
    main()
