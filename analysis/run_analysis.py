'''
Hospital Data Analytics - reproducible analysis layer
====================================================
Loads data/patients.csv and data/doctors.csv into an in-memory SQLite database and
runs the analytical queries used in the report and dashboard.

The T-SQL scripts in sql/ are the primary deliverable; this script exists so that
every number quoted in docs/report.md and index.html can be reproduced without
SQL Server:

    python analysis/run_analysis.py            # writes analysis/results.json
    python analysis/run_analysis.py --figures  # also regenerates images/*.png
'''

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IMAGES = ROOT / "images"
RESULTS = ROOT / "analysis" / "results.json"

PALETTE = {
    "ink": "#0B2027",
    "teal": "#147D7A",
    "teal_light": "#5FB3AE",
    "gold": "#E4B363",
    "coral": "#D96C5F",
    "slate": "#5C6B73",
    "grid": "#DCE3E6",
    "paper": "#F7F9FA",
}


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
def build_db() -> sqlite3.Connection:
    """Mirror the SQL Server schema (VARCHAR -> TEXT, FLOAT -> REAL)."""
    con = sqlite3.connect(":memory:")
    con.execute(
        """
        CREATE TABLE Doctors (
            Doctor_ID      INTEGER PRIMARY KEY,
            Doctor_Name    TEXT    NOT NULL,
            Specialization TEXT    NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE TABLE Patients (
            Patient_ID       INTEGER PRIMARY KEY,
            Patient_Name     TEXT    NOT NULL,
            Age              INTEGER NOT NULL CHECK (Age BETWEEN 0 AND 120),
            Gender           TEXT    NOT NULL,
            City             TEXT    NOT NULL,
            Condition        TEXT    NOT NULL,
            Admission_Type   TEXT    NOT NULL,
            Doctor_ID        INTEGER NOT NULL,
            Admission_Date   TEXT    NOT NULL,
            Length_of_Stay   INTEGER NOT NULL CHECK (Length_of_Stay > 0),
            Treatment_Status TEXT    NOT NULL,
            FOREIGN KEY (Doctor_ID) REFERENCES Doctors (Doctor_ID)
        )
        """
    )
    for table, file in (("Doctors", "doctors.csv"), ("Patients", "patients.csv")):
        df = pd.read_csv(DATA / file)
        df.to_sql(table, con, if_exists="append", index=False)
    return con


# --------------------------------------------------------------------------- #
# Queries
# --------------------------------------------------------------------------- #
QUERIES: dict[str, str] = {
    "kpi": """
        SELECT COUNT(*)                                   AS total_patients,
               ROUND(AVG(Age * 1.0), 2)                   AS avg_age,
               ROUND(AVG(Length_of_Stay * 1.0), 2)        AS avg_los,
               SUM(Length_of_Stay)                        AS bed_days,
               SUM(CASE WHEN Treatment_Status = 'Recovered' THEN 1 ELSE 0 END) AS recovered,
               COUNT(DISTINCT City)                       AS cities,
               COUNT(DISTINCT Condition)                  AS conditions
        FROM Patients
    """,
    "by_city": """
        SELECT City, COUNT(*) AS patients
        FROM Patients GROUP BY City ORDER BY patients DESC, City
    """,
    "by_admission_type": """
        SELECT Admission_Type,
               COUNT(*)                            AS patients,
               ROUND(AVG(Length_of_Stay * 1.0), 2) AS avg_los
        FROM Patients GROUP BY Admission_Type ORDER BY avg_los DESC
    """,
    "age_group": """
        SELECT CASE WHEN Age < 40 THEN 'Young'
                    WHEN Age < 60 THEN 'Middle-aged'
                    ELSE 'Senior' END     AS age_group,
               COUNT(*)                   AS patients
        FROM Patients GROUP BY age_group
    """,
    "by_condition": """
        SELECT Condition, COUNT(*) AS patients,
               ROUND(AVG(Length_of_Stay * 1.0), 2) AS avg_los
        FROM Patients GROUP BY Condition ORDER BY patients DESC, Condition
    """,
    "doctor_workload": """
        SELECT D.Doctor_ID, D.Doctor_Name, D.Specialization,
               COUNT(*)                            AS patients,
               ROUND(AVG(P.Length_of_Stay * 1.0), 2) AS avg_los,
               SUM(P.Length_of_Stay)               AS bed_days
        FROM Patients P
        JOIN Doctors  D ON P.Doctor_ID = D.Doctor_ID
        GROUP BY D.Doctor_ID, D.Doctor_Name, D.Specialization
        ORDER BY patients DESC, bed_days DESC
    """,
    "stay_category": """
        SELECT CASE WHEN Length_of_Stay <= 3 THEN 'Short Stay' ELSE 'Long Stay' END AS stay_category,
               COUNT(*) AS patients
        FROM Patients GROUP BY stay_category
    """,
    "los_detail": """
        SELECT Patient_ID, Patient_Name, Age, Gender, City, Condition, Admission_Type,
               Doctor_ID, Admission_Date, Length_of_Stay, Treatment_Status,
               CASE WHEN Length_of_Stay <= 3 THEN 'Short Stay' ELSE 'Long Stay' END AS stay_category
        FROM Patients ORDER BY Admission_Date
    """,
    "top3_los": """
        SELECT Patient_Name, Length_of_Stay FROM Patients
        ORDER BY Length_of_Stay DESC, Patient_Name LIMIT 3
    """,
    "after_15_jan": """
        SELECT Patient_Name, Admission_Date FROM Patients
        WHERE Admission_Date > '2026-01-15' ORDER BY Admission_Date
    """,
    "internal_medicine": """
        SELECT P.Patient_Name, D.Specialization, D.Doctor_Name
        FROM Patients P JOIN Doctors D ON P.Doctor_ID = D.Doctor_ID
        WHERE D.Specialization = 'Internal Medicine'
        ORDER BY P.Patient_Name
    """,
    "gender_status": """
        SELECT Gender, Treatment_Status, COUNT(*) AS patients
        FROM Patients GROUP BY Gender, Treatment_Status ORDER BY Gender, Treatment_Status
    """,
}


def run_queries(con: sqlite3.Connection) -> dict:
    out = {}
    for name, sql in QUERIES.items():
        df = pd.read_sql_query(sql, con)
        out[name] = df.to_dict(orient="records")
    return out


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #
def _style(plt) -> None:
    plt.rcParams.update(
        {
            "font.family": "Cabin",
            "font.size": 11,
            "axes.edgecolor": "#B9C4C9",
            "axes.labelcolor": PALETTE["slate"],
            "axes.titlecolor": PALETTE["ink"],
            "xtick.color": PALETTE["slate"],
            "ytick.color": PALETTE["slate"],
            "axes.grid": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _clean(ax, grid_axis: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=PALETTE["grid"], linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)


def _title(fig, title: str, subtitle: str) -> None:
    fig.text(0.012, 0.975, title, fontsize=16, fontweight="bold", color=PALETTE["ink"], va="top")
    fig.text(0.012, 0.905, subtitle, fontsize=10.5, color=PALETTE["slate"], va="top")


def _save(fig, name: str) -> None:
    IMAGES.mkdir(exist_ok=True)
    fig.savefig(IMAGES / name, dpi=200, bbox_inches="tight", pad_inches=0.18)
    print(f"  wrote images/{name}")


def make_figures(res: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    _style(plt)
    P = PALETTE

    # 1. Patients by city ----------------------------------------------------
    rows = res["by_city"]
    labels = [r["City"] for r in rows][::-1]
    values = [r["patients"] for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    bars = ax.barh(labels, values, color=[P["teal"] if v > 1 else P["teal_light"] for v in values],
                   height=0.62, zorder=3)
    for b, v in zip(bars, values):
        ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2, str(v),
                va="center", fontsize=11, fontweight="bold", color=P["ink"])
    ax.set_xlim(0, max(values) + 0.7)
    ax.set_xlabel("Patients")
    _clean(ax, "x")
    _title(fig, "Patient catchment by city",
           "Lagos accounts for 3 of 10 admissions; the remaining 7 cities contribute one each")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig01_patients_by_city.png")
    plt.close(fig)

    # 2. Average length of stay by admission type ----------------------------
    rows = res["by_admission_type"]
    labels = [r["Admission_Type"] for r in rows]
    values = [r["avg_los"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    bars = ax.bar(labels, values, color=[P["coral"], P["teal"]][: len(labels)], width=0.45, zorder=3)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v:.1f} days",
                ha="center", fontsize=11.5, fontweight="bold", color=P["ink"])
    ax.axhline(4, color=P["gold"], linestyle="--", linewidth=1.3, zorder=2)
    ax.text(1.42, 4.12, "4-day threshold", fontsize=9, color=P["gold"], ha="right")
    ax.set_ylim(0, max(values) + 1.6)
    ax.set_ylabel("Average length of stay (days)")
    _clean(ax)
    _title(fig, "Scheduled admissions stay twice as long",
           "Emergency 3.0 days vs Scheduled 6.5 days - the HAVING > 4 filter isolates Scheduled only")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig02_los_by_admission_type.png")
    plt.close(fig)

    # 3. Age group donut -----------------------------------------------------
    order = ["Young", "Middle-aged", "Senior"]
    lookup = {r["age_group"]: r["patients"] for r in res["age_group"]}
    values = [lookup.get(k, 0) for k in order]
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    wedges, _ = ax.pie(values, colors=[P["teal"], P["gold"], P["coral"]],
                       startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.36, edgecolor="white", linewidth=2.5))
    ax.text(0, 0.08, "10", ha="center", va="center", fontsize=30, fontweight="bold", color=P["ink"])
    ax.text(0, -0.2, "patients", ha="center", va="center", fontsize=11, color=P["slate"])
    total = sum(values) or 1
    ax.legend(wedges, [f"{k} - {v} ({v / total:.0%})" for k, v in zip(order, values)],
              loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=3, frameon=False, fontsize=10)
    _title(fig, "Age distribution",
           "Young and Middle-aged patients split 4 / 4; Seniors make up 20%")
    fig.tight_layout(rect=(0, 0.04, 1, 0.86))
    _save(fig, "fig03_age_groups.png")
    plt.close(fig)

    # 4. Conditions ----------------------------------------------------------
    rows = res["by_condition"]
    labels = [r["Condition"] for r in rows]
    values = [r["patients"] for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bars = ax.bar(labels, values, color=P["teal"], width=0.55, zorder=3)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.05, str(v),
                ha="center", fontsize=11, fontweight="bold", color=P["ink"])
    ax.set_ylim(0, max(values) + 1.0)
    ax.text(0.985, 0.93, "HAVING COUNT(*) > 1  ->  all five conditions qualify",
            transform=ax.transAxes, ha="right", fontsize=9.5, color=P["coral"])
    ax.set_ylabel("Patients")
    _clean(ax)
    _title(fig, "Case mix is perfectly balanced",
           "All five conditions affect exactly two patients - no condition dominates the caseload")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig04_conditions.png")
    plt.close(fig)

    # 5. Doctor workload -----------------------------------------------------
    rows = res["doctor_workload"]
    labels = [r["Doctor_Name"] for r in rows]
    patients = [r["patients"] for r in rows]
    los = [r["avg_los"] for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    x = list(range(len(labels)))
    bars = ax.bar(x, patients, color=P["teal"], width=0.5, zorder=3, label="Patients treated")
    for b, v in zip(bars, patients):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, str(v), ha="center",
                fontsize=11, fontweight="bold", color=P["ink"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\n{r['Specialization']}" for l, r in zip(labels, rows)], fontsize=9.5)
    ax.set_ylim(0, max(patients) + 1.4)
    ax.set_ylabel("Patients treated")
    _clean(ax)

    ax2 = ax.twinx()
    ax2.plot(x, los, color=P["gold"], marker="o", markersize=7, linewidth=2.2, zorder=4)
    for xi, v in zip(x, los):
        ax2.annotate(f"{v:.1f} days", (xi, v), textcoords="offset points", xytext=(12, -3),
                     ha="left", va="center", fontsize=9.5, color="#B07E28", fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none", alpha=0.85))
    ax2.set_ylim(0, max(los) + 3.6)
    ax2.set_ylabel("Average length of stay (days)", color=P["gold"])
    ax2.tick_params(axis="y", colors=P["gold"])
    ax2.spines["top"].set_visible(False)
    ax.legend(handles=[Patch(color=P["teal"], label="Patients treated"),
                       plt.Line2D([], [], color=P["gold"], marker="o", label="Average LOS")],
              loc="upper left", frameon=False, fontsize=9.5)
    _title(fig, "Workload vs. outcome by physician",
           "Dr. Ade carries the largest panel (4) and the longest average stay (5.0 days)")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig05_doctor_workload.png")
    plt.close(fig)

    # 6. Admissions timeline -------------------------------------------------
    df = pd.DataFrame(res["los_detail"])
    df["Admission_Date"] = pd.to_datetime(df["Admission_Date"])
    df = df.sort_values("Admission_Date")
    fig, ax = plt.subplots(figsize=(9.4, 4.5))
    colors = [P["coral"] if c == "Emergency" else P["teal"] for c in df["Admission_Type"]]
    ax.vlines(df["Admission_Date"], 0, df["Length_of_Stay"], color=colors, linewidth=2, alpha=0.55, zorder=2)
    ax.scatter(df["Admission_Date"], df["Length_of_Stay"], s=110, color=colors, zorder=3,
               edgecolor="white", linewidth=1.4)
    for _, r in df.iterrows():
        ax.annotate(r["Patient_Name"].split()[0], (r["Admission_Date"], r["Length_of_Stay"]),
                    textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8.5,
                    color=P["slate"])
    ax.set_ylim(0, max(df["Length_of_Stay"]) + 2)
    ax.set_ylabel("Length of stay (days)")
    ax.set_xlabel("Admission date - January 2026")
    _clean(ax)
    ax.legend(handles=[Patch(color=P["coral"], label="Emergency"),
                       Patch(color=P["teal"], label="Scheduled")],
              loc="upper left", frameon=False, fontsize=9.5, ncol=2)
    _title(fig, "Admission timeline",
           "10 admissions across 5 January weeks; the two longest stays both belong to scheduled cases")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig06_admissions_timeline.png")
    plt.close(fig)

    # 7. Length-of-stay distribution ----------------------------------------
    df = pd.DataFrame(res["los_detail"])
    counts = df["Length_of_Stay"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8.4, 4.3))
    colors = [P["gold"] if d <= 3 else P["teal"] for d in counts.index]
    bars = ax.bar([str(d) for d in counts.index], counts.values, color=colors, width=0.6, zorder=3)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.06, str(v), ha="center",
                fontsize=10.5, fontweight="bold", color=P["ink"])
    ax.set_xlabel("Length of stay (days)")
    ax.set_ylabel("Patients")
    ax.set_ylim(0, counts.max() + 1)
    _clean(ax)
    ax.legend(handles=[Patch(color=P["gold"], label="Short stay (<= 3 days)"),
                       Patch(color=P["teal"], label="Long stay (> 3 days)")],
              frameon=False, fontsize=9.5, loc="upper right")
    _title(fig, "Length-of-stay distribution",
           "Median stay is 4 days; 6 of 10 patients are long-stay cases")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    _save(fig, "fig07_los_distribution.png")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", action="store_true", help="regenerate images/*.png")
    args = ap.parse_args()

    con = build_db()
    res = run_queries(con)
    RESULTS.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"wrote {RESULTS.relative_to(ROOT)}")

    k = res["kpi"][0]
    print(f"\nKPI  patients={k['total_patients']}  avg_age={k['avg_age']}  "
          f"avg_los={k['avg_los']}  bed_days={k['bed_days']}  cities={k['cities']}")
    for name in ("by_city", "by_admission_type", "age_group", "by_condition", "doctor_workload", "stay_category"):
        print(f"\n{name}:")
        for row in res[name]:
            print("   ", row)

    if args.figures:
        print("\nfigures:")
        make_figures(res)


if __name__ == "__main__":
    main()
