"""
Builds index.html - a self-contained, dependency-free analytics dashboard.

All figures are hand-computed SVG generated from analysis/results.json, so the
page renders identically offline, on GitHub Pages, or inside a PDF export.
No JavaScript, no CDN, no tracking.

    python analysis/run_analysis.py && python analysis/build_dashboard.py
"""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = json.loads((ROOT / "analysis" / "results.json").read_text(encoding="utf-8"))

INK = "#0B2027"
TEAL = "#147D7A"
TEAL_L = "#5FB3AE"
GOLD = "#E4B363"
CORAL = "#D96C5F"
SLATE = "#5C6B73"
GRID = "#E1E6E4"

KPI = RES["kpi"][0]
CITY = RES["by_city"]
ADMIT = {r["Admission_Type"]: r for r in RES["by_admission_type"]}
AGE = {r["age_group"]: r["patients"] for r in RES["age_group"]}
COND = RES["by_condition"]
DOCS = RES["doctor_workload"]
STAY = {r["stay_category"]: r["patients"] for r in RES["stay_category"]}
PATIENTS = RES["los_detail"]

LONG_BED = sum(p["Length_of_Stay"] for p in PATIENTS if p["stay_category"] == "Long Stay")
BED = KPI["bed_days"]
AGE_LOS = {}
for p in PATIENTS:
    a = p["Age"]
    g = "Young" if a < 40 else ("Middle-aged" if a < 60 else "Senior")
    AGE_LOS.setdefault(g, []).append(p["Length_of_Stay"])
AGE_LOS = {k: round(sum(v) / len(v), 2) for k, v in AGE_LOS.items()}


def esc(s: object) -> str:
    return html.escape(str(s))


def svg(w: int, h: int, label: str, body: str, extra: str = "") -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" '
        f'preserveAspectRatio="xMidYMid meet" {extra}>{body}</svg>'
    )


def t(x, y, s, size=12, fill=SLATE, weight=400, anchor="start", cls="", style=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" text-anchor="{anchor}" class="{cls}" style="{style}">{esc(s)}</text>'
    )


# --------------------------------------------------------------------------- #
# Chart builders
# --------------------------------------------------------------------------- #
def chart_admission_type() -> str:
    plan = [
        ("Emergency", ADMIT["Emergency"]["avg_los"], ADMIT["Emergency"]["patients"], CORAL),
        ("Scheduled", ADMIT["Scheduled"]["avg_los"], ADMIT["Scheduled"]["patients"], TEAL),
    ]
    base, top, vmax = 250, 40, 7.5
    k = (base - top) / vmax
    body = [f'<line x1="70" y1="{base}" x2="610" y2="{base}" stroke="{GRID}" stroke-width="1"/>']
    for gv in (2, 4, 6):
        y = base - gv * k
        body.append(f'<line x1="70" y1="{y:.1f}" x2="610" y2="{y:.1f}" stroke="{GRID}" stroke-width="1" stroke-dasharray="2 4"/>')
        body.append(t(62, y + 4, f"{gv}", 11, SLATE, 400, "end"))
    bw, gap = 104, 150
    x0 = 190
    for i, (name, val, n, color) in enumerate(plan):
        x = x0 + i * gap
        y = base - val * k
        body.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{val * k:.1f}" rx="4" fill="{color}"/>')
        body.append(t(x + bw / 2, y - 12, f"{val:.1f}", 26, INK, 700, "middle"))
        body.append(t(x + bw / 2, y - 34, "days", 11, SLATE, 400, "middle"))
        body.append(t(x + bw / 2, base + 24, name, 13, INK, 600, "middle"))
        body.append(t(x + bw / 2, base + 42, f"{n} admissions", 11, SLATE, 400, "middle"))
    # threshold
    ty = base - 4 * k
    body.append(f'<line x1="70" y1="{ty:.1f}" x2="610" y2="{ty:.1f}" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="7 5"/>')
    body.append(t(606, ty - 9, "HAVING > 4 days", 11, "#A8791E", 600, "end"))
    body.append(t(70, 26, "Average length of stay (days)", 11, SLATE))
    return svg(640, 300, "Average length of stay by admission type", "".join(body))


def chart_city() -> str:
    rows = sorted(CITY, key=lambda r: (-r["patients"], r["City"]))
    n = len(rows)
    top, step, bar_h = 26, 34, 20
    h = top + n * step + 34
    k = 420 / max(r["patients"] for r in rows)
    body = []
    for i, r in enumerate(rows):
        y = top + i * step
        color = GOLD if r["patients"] > 1 else TEAL_L
        body.append(t(112, y + 14, r["City"], 12.5, INK, 600 if r["patients"] > 1 else 400, "end"))
        body.append(f'<rect x="122" y="{y + 2}" width="{430}" height="{bar_h}" rx="3" fill="#F1F3F2"/>')
        body.append(f'<rect x="122" y="{y + 2}" width="{r["patients"] * k:.1f}" height="{bar_h}" rx="3" fill="{color}"/>')
        body.append(t(122 + r["patients"] * k + 9, y + 17, r["patients"], 12.5, INK, 700))
    body.append(t(122, h - 8, f"{n} cities  ·  Lagos holds {CITY[0]['patients'] / KPI['total_patients']:.0%} of the caseload", 11, SLATE))
    return svg(640, h, "Patients by city", "".join(body))


def chart_age() -> str:
    order = [("Young", TEAL), ("Middle-aged", GOLD), ("Senior", CORAL)]
    total = sum(AGE.get(k, 0) for k, _ in order)
    r, cx, cy, sw = 74, 118, 122, 30
    circ = 2 * 3.14159265 * r
    offset = 0.0
    body = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#F1F3F2" stroke-width="{sw}"/>']
    for name, color in order:
        v = AGE.get(name, 0)
        frac = v / total
        dash = frac * circ - 3
        body.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-dasharray="{max(dash, 0):.2f} {circ - max(dash, 0):.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})" stroke-linecap="butt">'
            f'<title>{esc(name)}: {v} patients</title></circle>'
        )
        offset += frac * circ
    body.append(t(cx, cy + 4, total, 30, INK, 700, "middle"))
    body.append(t(cx, cy + 24, "patients", 11, SLATE, 400, "middle"))
    lx, ly = 238, 58
    for i, (name, color) in enumerate(order):
        y = ly + i * 46
        body.append(f'<rect x="{lx}" y="{y - 11}" width="11" height="11" rx="3" fill="{color}"/>')
        body.append(t(lx + 20, y, name, 13, INK, 600))
        body.append(t(lx + 20, y + 18, f"{AGE.get(name, 0)} patients · {AGE.get(name, 0) / total:.0%} · avg {AGE_LOS[name]:.1f} d stay", 11, SLATE))
    return svg(640, 250, "Age group distribution", "".join(body))


def chart_conditions() -> str:
    rows = sorted(COND, key=lambda r: r["Condition"])
    base, top = 178, 34
    k = (base - top) / 2.6
    bw, step = 62, 96
    x0 = 70
    body = [f'<line x1="54" y1="{base}" x2="614" y2="{base}" stroke="{GRID}"/>']
    for i, r in enumerate(rows):
        x = x0 + i * step
        hgt = r["patients"] * k
        body.append(f'<rect x="{x}" y="{base - hgt:.1f}" width="{bw}" height="{hgt:.1f}" rx="3" fill="{TEAL}"/>')
        body.append(t(x + bw / 2, base - hgt - 9, r["patients"], 15, INK, 700, "middle"))
        body.append(t(x + bw / 2, base + 20, r["Condition"], 11.5, INK, 600, "middle"))
        body.append(t(x + bw / 2, base + 37, f"{r['avg_los']:.1f} d avg", 10.5, SLATE, 400, "middle"))
    body.append(t(54, 24, "Patients per condition (all equal 2 · HAVING > 1 returns all five)", 11, SLATE))
    return svg(640, 226, "Patients per medical condition", "".join(body))


def chart_doctors() -> str:
    base, top = 190, 40
    k = (base - top) / 4.6
    step, bw = 178, 74
    x0 = 96
    body = [f'<line x1="66" y1="{base}" x2="612" y2="{base}" stroke="{GRID}"/>']
    for gv in (2, 4):
        y = base - gv * k
        body.append(f'<line x1="66" y1="{y:.1f}" x2="612" y2="{y:.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
        body.append(t(58, y + 4, gv, 10.5, SLATE, 400, "end"))
    for i, d in enumerate(DOCS):
        x = x0 + i * step
        hgt = d["patients"] * k
        body.append(f'<rect x="{x}" y="{base - hgt:.1f}" width="{bw}" height="{hgt:.1f}" rx="3" fill="{TEAL}" opacity="{1 if d['patients'] == 4 else 0.82}"/>')
        body.append(t(x + bw / 2, base - hgt - 9, d["patients"], 16, INK, 700, "middle"))
        body.append(t(x + bw / 2, base + 20, d["Doctor_Name"], 12, INK, 600, "middle"))
        body.append(t(x + bw / 2, base + 36, d["Specialization"], 10, SLATE, 400, "middle"))
        body.append(t(x + bw / 2, base + 52, f"{d['bed_days']} bed-days · {d['avg_los']:.1f} d avg", 10, SLATE, 400, "middle"))
    body.append(t(66, 24, "Patients treated per physician", 11, SLATE))
    return svg(640, 250, "Workload and average stay per physician", "".join(body))


def chart_timeline() -> str:
    pts = sorted(PATIENTS, key=lambda p: p["Admission_Date"])
    base, top = 200, 40
    k = (base - top) / 9
    x0, x1 = 78, 604
    d0, d1 = date(2026, 1, 1), date(2026, 1, 31)
    span = (d1 - d0).days

    def sx(iso: str) -> float:
        y, m, dd = map(int, iso.split("-"))
        return x0 + (date(y, m, dd) - d0).days / span * (x1 - x0)

    body = [f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{GRID}"/>']
    for gv in (2, 4, 6, 8):
        y = base - gv * k
        body.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
        body.append(t(x0 - 9, y + 4, gv, 10.5, SLATE, 400, "end"))
    for dd in (1, 10, 20, 30):
        x = sx(f"2026-01-{dd:02d}")
        body.append(f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{base + 5}" stroke="{GRID}"/>')
        body.append(t(x, base + 21, f"{dd} Jan", 10.5, SLATE, 400, "middle"))
    for p in pts:
        x = sx(p["Admission_Date"])
        y = base - p["Length_of_Stay"] * k
        color = CORAL if p["Admission_Type"] == "Emergency" else TEAL
        body.append(
            f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="1.6" opacity="0.35"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{color}" stroke="#fff" stroke-width="1.6">'
            f'<title>{esc(p["Patient_Name"])} · {p["Length_of_Stay"]} days · {esc(p["Admission_Type"])}</title></circle>'
        )
        body.append(t(x, y - 12, p["Length_of_Stay"], 10.5, INK, 700, "middle"))
    body.append(t(x0, 24, "Length of stay (days) by admission date — January 2026", 11, SLATE))
    body.append(f'<circle cx="{x1 - 150}" cy="16" r="4.5" fill="{CORAL}"/>')
    body.append(t(x1 - 140, 20, "Emergency", 10.5, SLATE))
    body.append(f'<circle cx="{x1 - 62}" cy="16" r="4.5" fill="{TEAL}"/>')
    body.append(t(x1 - 52, 20, "Scheduled", 10.5, SLATE))
    return svg(640, 232, "Admission timeline", "".join(body))


def chart_los_dist() -> str:
    counts: dict[int, int] = {}
    for p in PATIENTS:
        counts[p["Length_of_Stay"]] = counts.get(p["Length_of_Stay"], 0) + 1
    days = sorted(counts)
    base, top = 180, 34
    k = (base - top) / 2.6
    bw, step = 46, 66
    x0 = 84
    body = [f'<line x1="66" y1="{base}" x2="600" y2="{base}" stroke="{GRID}"/>']
    for i, d in enumerate(days):
        x = x0 + i * step
        hgt = counts[d] * k
        color = GOLD if d <= 3 else TEAL
        body.append(f'<rect x="{x}" y="{base - hgt:.1f}" width="{bw}" height="{hgt:.1f}" rx="3" fill="{color}">'
                    f'<title>{d} days: {counts[d]} patients</title></rect>')
        body.append(t(x + bw / 2, base - hgt - 8, counts[d], 12, INK, 700, "middle"))
        body.append(t(x + bw / 2, base + 20, d, 11.5, INK, 600, "middle"))
    body.append(t((x0 + (len(days) - 1) * step + bw) / 2, base + 42, "length of stay (days)", 10.5, SLATE, 400, "middle"))
    body.append(t(66, 22, "Patients by length of stay", 11, SLATE))
    return svg(640, 236, "Patients by length of stay", "".join(body))


# --------------------------------------------------------------------------- #
# Tables
# --------------------------------------------------------------------------- #
def patient_rows() -> str:
    out = []
    for p in PATIENTS:
        band = "gold" if p["stay_category"] == "Short Stay" else "teal"
        out.append(
            "<tr>"
            f'<td class="num">{p["Patient_ID"]}</td>'
            f'<td class="strong">{esc(p["Patient_Name"])}</td>'
            f'<td class="num">{p["Age"]}</td>'
            f'<td>{esc(p["Gender"])}</td>'
            f'<td>{esc(p["City"])}</td>'
            f'<td>{esc(p["Condition"])}</td>'
            f'<td>{esc(p["Admission_Type"])}</td>'
            f'<td class="num">{p["Admission_Date"][5:]}</td>'
            f'<td class="num strong">{p["Length_of_Stay"]}</td>'
            f'<td><span class="pill {band}">{p["stay_category"]}</span></td>'
            f'<td>{esc(p["Treatment_Status"])}</td>'
            "</tr>"
        )
    return "".join(out)


def doctor_rows() -> str:
    out = []
    for d in DOCS:
        out.append(
            "<tr>"
            f'<td class="num">{d["Doctor_ID"]}</td>'
            f'<td class="strong">{esc(d["Doctor_Name"])}</td>'
            f'<td>{esc(d["Specialization"])}</td>'
            f'<td class="num">{d["patients"]}</td>'
            f'<td class="num">{d["bed_days"]}</td>'
            f'<td class="num strong">{d["avg_los"]:.2f}</td>'
            "</tr>"
        )
    return "".join(out)


def condition_rows() -> str:
    rec = {r["Condition"]: r for r in COND}
    out = []
    for c in sorted(COND, key=lambda r: (-r["avg_los"], r["Condition"])):
        r = rec[c["Condition"]]
        out.append(
            "<tr>"
            f'<td class="strong">{esc(r["Condition"])}</td>'
            f'<td class="num">{r["patients"]}</td>'
            f'<td class="num">{r["avg_los"]:.2f}</td>'
            f'<td class="num">{r["patients"] * 1}</td>'
            "</tr>"
        )
    return "".join(out)


# --------------------------------------------------------------------------- #
# SQL snippets
# --------------------------------------------------------------------------- #
SNIPPETS = [
    ("01", "Retrieving and filtering", "5 queries", "WHERE, AND, BETWEEN, IN",
     """SELECT *
FROM Patients
WHERE Gender = 'Female'
  AND City = 'Lagos'
  AND Admission_Type = 'Emergency';   -- 1 row: Aisha Bello

SELECT *
FROM Patients
WHERE Condition IN ('Diabetes', 'Hypertension');   -- 4 rows"""),
    ("02", "Sorting and aggregation", "5 queries", "TOP, DISTINCT, COUNT, AVG, GROUP BY",
     """SELECT TOP (3) *
FROM Patients
ORDER BY Length_of_Stay DESC;      -- 8, 7, 6 days

SELECT CAST(AVG(Age * 1.0) AS DECIMAL(10,2)) AS Avg_Age
FROM Patients;                     -- 44.60 (× 1.0 avoids integer division)"""),
    ("03", "Strings and dates", "5 queries", "UPPER, LOWER, CONCAT, YEAR, MONTH, DATENAME",
     """SELECT Patient_ID,
       Patient_Name,
       YEAR(Admission_Date)            AS Admission_Year,
       DATENAME(MONTH, Admission_Date) AS Admission_Month_Name
FROM Patients;"""),
    ("04", "Advanced aggregation", "6 queries", "HAVING, CASE, CTE, business rules",
     """WITH AgeGroup AS
(
    SELECT CASE WHEN Age < 40 THEN 'Young'
                WHEN Age < 60 THEN 'Middle-aged'
                ELSE 'Senior' END AS Age_Group
    FROM Patients
)
SELECT Age_Group, COUNT(*) AS PatientCount
FROM AgeGroup
GROUP BY Age_Group;                -- Young 4 | Middle-aged 4 | Senior 2"""),
    ("05", "Keys and joins", "6 queries", "PRIMARY KEY, FOREIGN KEY, INNER JOIN, RANK()",
     """SELECT D.Doctor_ID,
       D.Doctor_Name,
       COUNT(*) AS Patient_Count
FROM Patients AS P
INNER JOIN Doctors AS D ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_ID, D.Doctor_Name
ORDER BY COUNT(*) DESC;            -- Dr. Ade, 4 patients"""),
]


def query_cards() -> str:
    out = []
    for num, title, count, concepts, sql in SNIPPETS:
        out.append(
            f'<article class="qcard">'
            f'<div class="qhead"><span class="qnum">{num}</span>'
            f'<div><h3>{esc(title)}</h3><p>{esc(count)} · {esc(concepts)}</p></div></div>'
            f'<pre><code>{esc(sql.strip())}</code></pre>'
            f'</article>'
        )
    return "".join(out)


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #
CSS = """
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#FBFAF7;color:#0B2027;font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;font-weight:600;letter-spacing:-.01em;margin:0}
a{color:inherit;text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 32px}

/* nav */
nav{border-bottom:1px solid #E5E3DB;background:#FBFAF7;position:sticky;top:0;z-index:20}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:24px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:14px;letter-spacing:.14em;text-transform:uppercase}
.brand .mark{width:22px;height:22px;border-radius:6px;background:#147D7A;display:inline-block;position:relative}
.brand .mark::after{content:"";position:absolute;inset:6px 6px auto 6px;height:2px;background:#FBFAF7;box-shadow:0 4px 0 #FBFAF7,0 8px 0 #FBFAF7}
nav ul{display:flex;gap:26px;list-style:none;margin:0;padding:0;font-size:13.5px;color:#5C6B73}
nav li a:hover{color:#147D7A}

/* hero */
.hero{background:#0B2027;color:#F7F6F1;padding:64px 0 88px;position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;right:-120px;top:-160px;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,rgba(20,125,122,.55),rgba(11,32,39,0) 68%)}
.hero .wrap{position:relative;z-index:1;max-width:1180px}
.eyebrow{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:#E4B363;font-weight:700;margin-bottom:20px}
.hero h1{font-size:clamp(34px,4.4vw,56px);line-height:1.08;max-width:15ch;color:#FFFFFF}
.hero p.lede{max-width:62ch;color:#C6D3D4;font-size:17px;margin:22px 0 0}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:30px}
.chip{border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:6px 14px;font-size:12.5px;color:#DDE7E7;background:rgba(255,255,255,.04)}

/* kpis */
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:-46px;position:relative;z-index:2}
.kpi{background:#fff;border:1px solid #E9E6DE;border-radius:12px;padding:20px 20px 18px;box-shadow:0 10px 30px rgba(11,32,39,.06)}
.kpi .v{font-family:Georgia,serif;font-size:34px;line-height:1.1;font-weight:600}
.kpi .v small{font-size:15px;color:#5C6B73;margin-left:3px}
.kpi .k{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:#5C6B73;margin-top:10px;font-weight:600}
.kpi .n{font-size:12px;color:#8A959A;margin-top:4px}
.kpi.accent{background:#0F2E35;border-color:#0F2E35;color:#fff}
.kpi.accent .k{color:#9CC2C1}
.kpi.accent .n{color:#7E9B9C}

/* sections */
section{padding:72px 0 8px}
.shead{display:flex;align-items:flex-end;justify-content:space-between;gap:32px;border-bottom:1px solid #E5E3DB;padding-bottom:18px;margin-bottom:36px}
.shead .num{font-size:12px;letter-spacing:.18em;color:#147D7A;font-weight:700}
.shead h2{font-size:30px;margin-top:6px}
.shead p{max-width:46ch;color:#5C6B73;font-size:14.5px;margin:0;text-align:right}

/* findings */
.findings{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.finding{background:#fff;border:1px solid #E9E6DE;border-radius:14px;padding:26px 28px;display:grid;grid-template-columns:104px 1fr;gap:20px;align-items:start}
.finding>div:last-child{display:flex;flex-direction:column;height:100%}
.finding .big{font-family:Georgia,serif;font-size:40px;line-height:1;color:#147D7A;font-weight:600}
.finding.coral .big{color:#D96C5F}
.finding.gold .big{color:#C08A2E}
.finding h3{font-size:18.5px;line-height:1.3;margin-bottom:8px}
.finding p{margin:0;font-size:14px;color:#4A585F}
.finding .tag{display:inline-block;margin-top:auto;padding-top:0;align-self:flex-start;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:#147D7A;background:#E8F2F1;padding:4px 9px;border-radius:5px;font-weight:700}

/* charts */
.charts{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.card{background:#fff;border:1px solid #E9E6DE;border-radius:14px;padding:26px 26px 18px;display:flex;flex-direction:column}
.card h3,.card .sub,.card svg{flex:none}
.card.wide{grid-column:1/-1}
.card h3{font-size:17px}
.card .sub{font-size:12.5px;color:#7A878D;margin:6px 0 16px}
.card svg{width:100%;height:auto;display:block;overflow:visible}
.card .note{font-size:12px;color:#7A878D;border-top:1px dashed #E5E3DB;padding-top:12px;margin-top:auto}

/* tables */
.tablewrap{background:#fff;border:1px solid #E9E6DE;border-radius:14px;overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#F4F3EE;text-align:left;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:#5C6B73;padding:12px 14px;font-weight:700;white-space:nowrap}
td{padding:11px 14px;border-top:1px solid #EFEDE7;color:#34444B}
tbody tr:hover{background:#FAFAF7}
td.num{text-align:right;font-variant-numeric:tabular-nums}
td.strong{font-weight:600;color:#0B2027}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:600}
.pill.gold{background:#FBF1DC;color:#96701F}
.pill.teal{background:#E8F2F1;color:#147D7A}
.two{display:grid;grid-template-columns:1.15fr .85fr;gap:22px;align-items:start}

/* queries */
.qgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.qcard{background:#fff;border:1px solid #E9E6DE;border-radius:14px;padding:22px 24px}
.qhead{display:flex;gap:14px;align-items:flex-start;margin-bottom:14px}
.qnum{font-family:Georgia,serif;font-size:22px;color:#147D7A;line-height:1;font-weight:600}
.qcard h3{font-size:16px}
.qcard .qhead p{margin:2px 0 0;font-size:11.5px;color:#7A878D}
pre{margin:0;background:#0B2027;border-radius:10px;padding:16px 18px;overflow-x:auto}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:11.5px;line-height:1.7;color:#D8E4E3;white-space:pre}

/* reproduce */
.repro{background:#0F2E35;color:#DDE7E7;border-radius:16px;padding:36px 38px;margin:56px 0 0;display:grid;grid-template-columns:1fr 1.05fr;gap:36px;align-items:center}
.repro h2{color:#fff;font-size:26px;margin-bottom:12px}
.repro p{font-size:14px;color:#A9C0C1;margin:0 0 18px}
.repro ol{margin:0;padding-left:18px;font-size:13.5px;color:#A9C0C1}
.repro li{margin-bottom:7px}
.repro pre{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.08)}
.repro code{color:#CFE3E2;font-size:12px}

footer{margin-top:72px;border-top:1px solid #E5E3DB;padding:34px 0 48px;color:#7A878D;font-size:12.5px}
footer .wrap{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap}

@media(max-width:900px){
 .kpis{grid-template-columns:repeat(2,1fr)}
 .findings,.charts,.qgrid,.two{grid-template-columns:1fr}
 .repro{grid-template-columns:1fr}
 .shead{flex-direction:column;align-items:flex-start}
 .shead p{text-align:left}
 nav ul{display:none}
 .wrap{padding:0 20px}
}
@media print{
 nav{display:none}.hero{padding:32px 0 56px}.kpis{margin-top:20px}
 section{padding:32px 0 8px;break-inside:avoid}
 body{font-size:12px}.card{break-inside:avoid}
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hospital Admissions Analytics · SQL Server / T-SQL</title>
<meta name="description" content="A SQL analytics case study of 10 hospital admissions: filtering, aggregation, CASE logic and joins in Microsoft SQL Server, with findings, charts and a query catalogue.">
<style>{CSS}</style>
</head>
<body>
<nav><div class="wrap">
  <div class="brand"><span class="mark"></span>Hospital Analytics</div>
  <ul>
    <li><a href="#findings">Findings</a></li>
    <li><a href="#visuals">Visuals</a></li>
    <li><a href="#data">Data</a></li>
    <li><a href="#queries">Query catalogue</a></li>
    <li><a href="#reproduce">Reproduce</a></li>
  </ul>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="eyebrow">SQL Server 17.0 · T-SQL · SSMS</div>
  <h1>Hospital admissions, analysed in SQL</h1>
  <p class="lede">A 10-admission teaching dataset taken end to end: schema design, primary and
  foreign keys, filtering, aggregation, CASE banding and joins — then translated into
  findings a hospital operations team could actually act on.</p>
  <div class="chips">
    <span class="chip">27 analytical queries</span>
    <span class="chip">2 tables · 1 foreign key</span>
    <span class="chip">5 reporting views</span>
    <span class="chip">8 validation checks</span>
    <span class="chip">January 2026 cohort</span>
  </div>
</div></header>

<div class="wrap">
  <div class="kpis">
    <div class="kpi accent"><div class="v">{KPI['total_patients']}</div><div class="k">Admissions</div><div class="n">Jan 5 – Jan 27, 2026</div></div>
    <div class="kpi"><div class="v">{KPI['avg_age']:.1f}<small>yrs</small></div><div class="k">Average age</div><div class="n">median 41.5 · range 23–68</div></div>
    <div class="kpi"><div class="v">{KPI['avg_los']:.1f}<small>days</small></div><div class="k">Average stay</div><div class="n">median 4 · max 8 days</div></div>
    <div class="kpi"><div class="v">{BED}<small>bed-days</small></div><div class="k">Total occupancy</div><div class="n">{LONG_BED} from long-stay cases</div></div>
    <div class="kpi"><div class="v">2.2<small>×</small></div><div class="k">Scheduled vs emergency</div><div class="n">6.5 d vs 3.0 d average</div></div>
  </div>
</div>

<section id="findings"><div class="wrap">
  <div class="shead">
    <div><div class="num">01 — FINDINGS</div><h2>Five things the data says</h2></div>
    <p>Every figure below is produced by the queries in <code style="background:none;color:#147D7A;font-family:inherit">/sql</code> and reproduced in <code style="background:none;color:#147D7A;font-family:inherit">analysis/results.json</code>.</p>
  </div>
  <div class="findings">
    <article class="finding coral"><div class="big">6.5d</div><div>
      <h3>Scheduled admissions stay more than twice as long as emergencies</h3>
      <p>Scheduled cases average 6.5 days against 3.0 for emergencies. With only four
      scheduled admissions they still generate 26 of the 44 bed-days — 59% of total
      occupancy from 40% of the caseload.</p>
      <span class="tag">Capacity planning</span></div></article>

    <article class="finding gold"><div class="big">77%</div><div>
      <h3>Six long-stay patients consume three quarters of all bed-days</h3>
      <p>Using the ≤3-day / &gt;3-day rule, 6 patients are long stay and account for 34 of
      44 bed-days. Length of stay, not admission volume, is the lever that moves
      occupancy in this dataset.</p>
      <span class="tag">Resource use</span></div></article>

    <article class="finding"><div class="big">30%</div><div>
      <h3>Lagos is the catchment, but seven cities send one patient each</h3>
      <p>3 of 10 admissions come from Lagos; the remaining 7 are spread across Abuja,
      Kano, Accra, Ibadan, Enugu, Kaduna and Port Harcourt. Geographic concentration
      matters more than city count when planning referral capacity.</p>
      <span class="tag">Catchment</span></div></article>

    <article class="finding"><div class="big">7.5d</div><div>
      <h3>Patients aged 60+ stay twice as long on average</h3>
      <p>Seniors average 7.5 days versus 3.5 for under-40s and 3.75 for the 40–59 band.
      Only two patients fall in the senior group, so this is a signal to test on a
      larger extract rather than a conclusion.</p>
      <span class="tag">Age banding · small n</span></div></article>

    <article class="finding"><div class="big">4</div><div>
      <h3>One physician carries 40% of the panel and the longest average stay</h3>
      <p>Dr. Ade (General Medicine) treats 4 patients for 20 bed-days and a 5.0-day
      average; Dr. Musa (Internal Medicine) sees 3 with the shortest average stay at
      3.67 days. Panel balance is worth reviewing as volume grows.</p>
      <span class="tag">Workforce</span></div></article>

    <article class="finding"><div class="big">2</div><div>
      <h3>Case mix is perfectly flat — every condition appears twice</h3>
      <p>Malaria, Typhoid, Hypertension, Diabetes and Asthma each affect exactly two
      patients, so <code style="background:none;font-family:inherit;color:#147D7A">HAVING COUNT(*) &gt; 1</code>
      returns the full list. Condition-level comparison is therefore illustrative, not
      statistically meaningful.</p>
      <span class="tag">Data limitation</span></div></article>
  </div>
</div></section>

<section id="visuals"><div class="wrap">
  <div class="shead">
    <div><div class="num">02 — VISUALS</div><h2>What the queries look like as charts</h2></div>
    <p>Rendered as inline SVG from the same result set — no chart library, no external
    requests, prints cleanly to PDF.</p>
  </div>
  <div class="charts">
    <div class="card"><h3>Admission channel drives length of stay</h3>
      <div class="sub">Average length of stay · days</div>
      {chart_admission_type()}
      <div class="note">The <code style="background:none;color:#147D7A;font-family:inherit">HAVING AVG(...) &gt; 4</code> filter returns Scheduled only — the single most useful query in the set.</div></div>

    <div class="card"><h3>Patient catchment by city</h3>
      <div class="sub">Admissions per city · 8 cities</div>
      {chart_city()}
      <div class="note">Highlighted bar: Lagos is the only city with more than one admission.</div></div>

    <div class="card"><h3>Age bands</h3>
      <div class="sub">CASE-based classification · 4 / 4 / 2</div>
      {chart_age()}
      <div class="note">Age bands follow the brief: Young &lt; 40, Middle-aged 40–59, Senior 60+.</div></div>

    <div class="card"><h3>Case mix</h3>
      <div class="sub">Patients per condition, with average stay</div>
      {chart_conditions()}
      <div class="note">Diabetes and Hypertension carry the longest average stays at 6.5 days.</div></div>

    <div class="card"><h3>Physician workload</h3>
      <div class="sub">Patients treated · bed-days · average stay</div>
      {chart_doctors()}
      <div class="note">INNER JOIN on Doctor_ID — every admission resolves to a valid physician.</div></div>

    <div class="card"><h3>Admission timeline</h3>
      <div class="sub">One point per admission · height = length of stay</div>
      {chart_timeline()}
      <div class="note">The two longest stays (8 and 7 days) both belong to scheduled admissions.</div></div>

    <div class="card wide"><h3>Length-of-stay distribution</h3>
      <div class="sub">Patients by exact stay length · the ≤3 / &gt;3 day split</div>
      {chart_los_dist()}
      <div class="note">Stays cluster at 2–4 days with a long tail to 8 days; the distribution is bimodal enough to justify banding rather than averaging alone.</div></div>
  </div>
</div></section>

<section id="data"><div class="wrap">
  <div class="shead">
    <div><div class="num">03 — DATA</div><h2>The register behind the numbers</h2></div>
    <p>Ten admissions, three physicians, January 2026. Enriched with the same CASE
    logic used in Task 4.</p>
  </div>
  <div class="tablewrap">
    <table>
      <thead><tr><th>ID</th><th>Patient</th><th>Age</th><th>Gender</th><th>City</th><th>Condition</th>
      <th>Channel</th><th>Admitted</th><th>Stay</th><th>Band</th><th>Status</th></tr></thead>
      <tbody>{patient_rows()}</tbody>
    </table>
  </div>
  <div class="two" style="margin-top:22px">
    <div class="tablewrap">
      <table>
        <thead><tr><th>ID</th><th>Physician</th><th>Specialization</th><th class="num">Patients</th><th class="num">Bed-days</th><th class="num">Avg stay</th></tr></thead>
        <tbody>{doctor_rows()}</tbody>
      </table>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Condition</th><th class="num">Patients</th><th class="num">Avg stay</th><th class="num">Bed-days</th></tr></thead>
        <tbody>{condition_rows()}</tbody>
      </table>
    </div>
  </div>
</div></section>

<section id="queries"><div class="wrap">
  <div class="shead">
    <div><div class="num">04 — QUERY CATALOGUE</div><h2>27 queries, five task sets</h2></div>
    <p>Each file in <code style="background:none;color:#147D7A;font-family:inherit">/sql</code> is numbered for run order and carries the expected
    row count in a comment.</p>
  </div>
  <div class="qgrid">{query_cards()}</div>
</div></section>

<div class="wrap">
  <div class="repro" id="reproduce">
    <div>
      <h2>Reproduce it locally</h2>
      <p>Any SQL Server instance from 2016 onwards, or Azure SQL. The script set is idempotent —
      it drops and rebuilds the objects, so it can be re-run safely.</p>
      <ol>
        <li>Open <code style="background:none;color:#9CC2C1">sql/00_create_schema.sql</code> in SSMS and execute it.</li>
        <li>Run <code style="background:none;color:#9CC2C1">sql/01_load_data.sql</code> (inline inserts, no file paths needed).</li>
        <li>Execute tasks <code style="background:none;color:#9CC2C1">02 → 06</code> in order.</li>
        <li>Optional: <code style="background:none;color:#9CC2C1">07_reporting_views.sql</code> and <code style="background:none;color:#9CC2C1">08_data_quality_checks.sql</code>.</li>
      </ol>
    </div>
    <pre><code>-- verify the load (expect 3 and 10)
SELECT COUNT(*) AS Doctors FROM dbo.Doctors;
SELECT COUNT(*) AS Patients FROM dbo.Patients;

-- the headline query
SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10,2)) AS Avg_LOS
FROM dbo.Patients
GROUP BY Admission_Type
HAVING AVG(Length_of_Stay * 1.0) &gt; 4;

-- Emergency | 3.00
-- Scheduled | 6.50</code></pre>
  </div>
</div>

<footer><div class="wrap">
  <div>Hospital Data Analytics · SQL Server / T-SQL case study</div>
  <div>Dataset: January 2026 teaching extract (10 admissions) · MIT licensed</div>
</div></footer>
</body>
</html>
"""

if __name__ == "__main__":
    (ROOT / "index.html").write_text(HTML, encoding="utf-8")
    print("wrote index.html", len(HTML), "bytes")
