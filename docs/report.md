---
title: "Hospital Admissions Analytics"
subtitle: "A SQL Server case study of ten January admissions — and what the numbers imply for capacity"
author: "Amandi Delight Chukwuebuka"
date: "November 2026"
lang: en-GB
---

\newpage

## Executive summary

Ten admissions over twenty-three days is a small dataset. It is also enough to show that the most
useful operational question in the extract is not *who* was admitted, but *how long they stayed* —
and that the answer splits cleanly by admission channel.

Scheduled admissions average **6.5 days** against **3.0 days** for emergencies. They are only 40% of
the caseload, yet they generate 59% of all bed-days. Six patients stay longer than three days, and
those six account for **77% of occupancy**. Everything else in this report is a variation on that
finding: the hospital's occupancy is driven by a minority of long, largely planned stays, not by the
volume of emergency arrivals.

The analysis was built in Microsoft SQL Server as five task sets — filtering, aggregation, string and
date handling, conditional logic, and joins — covering 27 queries. Each query is stored as a numbered
script with its expected result in a comment, and the headline figures are reproduced in Python so a
reviewer can verify them without a SQL Server instance.

| Metric | Value | Note |
|---|---:|---|
| Admissions | 10 | 5–27 January 2026 |
| Physicians | 3 | General, Internal and Family Medicine |
| Average age | 44.6 years | range 23–68, median 41.5 |
| Average length of stay | 4.4 days | median 4, maximum 8 |
| Total bed-days | 44 | 34 of them long-stay |
| Recovery at extract | 60% | 6 recovered, 4 recovering |
| Admission channels | 6 emergency / 4 scheduled | 60% / 40% |

## 1. The question behind the queries

The brief is a set of SQL exercises. Answered literally, it produces ten result grids and stops. That
is not useful to a hospital, so the queries were organised around three operational questions that
the data can actually answer:

1. **Where does occupancy come from?** Volume, length of stay, or a small number of outliers?
2. **Which patient groups and channels drive it?** Admission type, age band, condition, city.
3. **Is the workload spread sensibly across physicians?** Panel size and average stay per doctor.

Every query in the repository maps to one of these. Where a query exists purely to demonstrate syntax
(for example `UPPER()` and `LOWER()`), it is kept in the task scripts but excluded from the findings.

## 2. Schema and method

The extract is modelled as two tables with a single one-to-many relationship. `Doctors` is the parent;
`Patients` holds one row per admission and references the treating physician through `Doctor_ID`.

![Entity relationship diagram. The foreign key `FK_Patients_Doctors` makes orphan admissions
impossible and lets Task 5 use an inner join without defensive filtering.](images/erd.png){width=100%}

Three design choices matter for the analysis that follows.

**The grain is the admission, not the patient.** A readmission would appear as a second row. This is
the right grain for bed-day accounting, and it is why every count in this report is described as
"admissions" rather than "patients" wherever the distinction matters.

**Business rules live in constraints.** Age, length of stay, gender, admission channel and treatment
status are all validated at insert time by `CHECK` constraints. The eight validation queries in
`08_data_quality_checks.sql` therefore concentrate on cross-row problems — orphans, duplicates,
reconciliation — rather than basic domain checks.

**Bandings live in a view.** The age groups (Young / Middle-aged / Senior) and stay bands
(Short / Long) are `CASE` expressions defined once in `vw_PatientAdmissions`. The report, the charts
and the dashboard all read from that definition, so "long stay" cannot mean two different things in
two places.

> **Reproducibility.** `analysis/run_analysis.py` loads the same CSV extracts into SQLite and re-runs
the aggregations with identical `CASE` logic, emitting `analysis/results.json`. Every figure quoted
here comes from that file. The T-SQL scripts remain the source of truth; the Python layer exists so
the numbers can be checked in continuous integration.

## 3. What the five task sets produced

### 3.1 Retrieving and filtering

Five filters, each isolating a clinically meaningful slice. Lagos returns three admissions; a stay
longer than five days returns three (7, 8 and 6 days); ages 30–50 return five; the three-way filter
(female, Lagos, emergency) returns exactly one patient; and the `IN` list returns the four chronic
cases (Diabetes and Hypertension, two each).

The strict inequality in the second query is worth noting: two patients stayed exactly five days and
are correctly excluded. A reviewer skimming the output might expect five rows; the comment in the
script explains why there are three.

### 3.2 Sorting and aggregation

`TOP (3)` with a descending sort returns the three longest stays — Grace Eze (8 days), David Mensah
(7) and Mary Johnson (6). `DISTINCT City` returns eight cities. The average age is 44.60, and the
condition counts return five rows of two.

The average deserves a technical note. `AVG()` applied to an `INT` column performs integer division
in T-SQL, so `AVG(Age)` returns 44 and silently discards the remainder. Multiplying by `1.0` before
casting to `DECIMAL(10,2)` is not cosmetic — it is the difference between a correct and an incorrect
answer.

### 3.3 Strings and dates

Uppercase, lowercase, concatenation, a strict date filter and a year/month breakdown. The date filter
(`> '2026-01-15'`) returns five admissions because Zainab Ali was admitted on the 15th; using `>=`
would return six. This is documented in the script rather than left as an ambiguity.

### 3.4 Advanced aggregation

The core of the analysis. Average stay by channel gives 3.00 (emergency) and 6.50 (scheduled). The
`HAVING` clause then filters groups rather than rows, returning Scheduled alone — the query that
produces the report's headline finding.

The `CASE` banding splits patients 4 / 4 / 2 across Young, Middle-aged and Senior; the stay bands
split 4 / 6 between short and long; and `HAVING COUNT(*) > 1` returns all five conditions, because
every condition appears exactly twice.

### 3.5 Keys and joins

The inner join returns all ten admissions with their physician's specialisation, which also proves the
foreign key holds: no admission fails to match a doctor. Three patients sit under Internal Medicine
(all with Dr. Musa). Average stay by physician is 5.00 (Dr. Ade), 4.33 (Dr. Bello) and 3.67
(Dr. Musa). The busiest physician is Dr. Ade with four patients.

| Physician | Specialization | Admissions | Bed-days | Average stay |
|---|---|---:|---:|---:|
| Dr. Ade | General Medicine | 4 | 20 | 5.00 d |
| Dr. Bello | Family Medicine | 3 | 13 | 4.33 d |
| Dr. Musa | Internal Medicine | 3 | 11 | 3.67 d |

## 4. Findings

### 4.1 Scheduled admissions stay twice as long

![Average length of stay by admission channel. The dashed line marks the four-day threshold used by
the `HAVING` clause.](images/fig02_los_by_admission_type.png){width=82%}

This is the finding with operational consequences. Emergency admissions are frequent and short;
scheduled admissions are fewer and long. Since scheduled volume is the part of demand a hospital can
plan, it is also the part where a bed-day reduction is achievable.

### 4.2 Six patients account for three quarters of occupancy

Four short-stay patients (≤ 3 days) consume 10 bed-days; six long-stay patients consume 34. A 10%
reduction in long-stay days saves 3.4 bed-days, against 1.0 for the same relative cut among short
stays. Length of stay, not arrival volume, is the lever.

![Length-of-stay distribution. Stays cluster at two to four days with a tail to eight.](images/fig07_los_distribution.png){width=78%}

### 4.3 The catchment is concentrated and dispersed at the same time

Lagos supplies 30% of admissions. The remaining seven patients come from seven different cities —
Abuja, Kano, Accra, Ibadan, Enugu, Kaduna and Port Harcourt. In referral terms this is the worst of
both worlds: one dominant origin that could strain a single site, and a long tail of one-off origins
that is expensive to serve.

![Admissions per city. Lagos is the only city with repeat volume.](images/fig01_patients_by_city.png){width=80%}

### 4.4 Older patients stay materially longer

Seniors average 7.5 days on two cases, against 3.5 for under-40s and 3.75 for the 40–59 band. The two
senior patients hold the two longest stays in the extract. With n = 2 this is a hypothesis, not an
estimate — but it is a specific and testable one, and it points at discharge planning for older
patients rather than at admission volume.

![Age band composition, with average stay per band.](images/fig03_age_groups.png){width=70%}

### 4.5 Workload is uneven but not yet a capacity problem

Dr. Ade carries 40% of admissions and 45% of bed-days. That is consistent with general medicine acting
as the front door. The interesting inversion is Dr. Musa: the Internal Medicine panel, usually assumed
to be the heaviest, has the *shortest* average stay at 3.67 days.

![Physician workload: admissions, bed-days and average stay.](images/fig05_doctor_workload.png){width=80%}

### 4.6 A perfectly flat case mix — and why that matters for reading the rest

Malaria, Typhoid, Hypertension, Diabetes and Asthma each appear exactly twice. In a real extract,
`HAVING COUNT(*) > 1` would surface the conditions that dominate volume. Here it returns the whole
list, which is a useful reminder that a query returning a plausible answer can still be telling you
nothing about the population.

The chronic pair (Diabetes, Hypertension) shows the longest average stay at 6.5 days. That matches
clinical expectation, but with two cases per condition it is illustration, not evidence.

![Case mix by condition, with average stay.](images/fig04_conditions.png){width=82%}

### 4.7 The month in one view

Ten admissions across five weeks, with the two longest stays falling in the second half of January —
both scheduled. Nothing in the timeline contradicts the channel finding: the tall points are teal.

![Admission timeline. Height is length of stay; colour is admission channel.](images/fig06_admissions_timeline.png){width=90%}

## 5. Recommendations

**1. Instrument the scheduled pathway.** It is 40% of admissions and 59% of bed-days. A one-day
reduction in average scheduled stay frees roughly four bed-days per ten admissions — more than any
plausible reduction in emergency volume.

**2. Add an age-band flag to the admission record.** The 60+ group averages 7.5 days on two cases.
Monitor it monthly before building a pathway around it; if the pattern holds at n ≥ 50, it justifies
dedicated discharge planning.

**3. Treat catchment concentration as a logistics risk.** Lagos is 30% of volume. Referral transport
and accommodation, not bed count, is the binding constraint for the other seven origins.

**4. Keep banding rules in a view, and publish the view.** One definition of "long stay" prevents
the dashboard and the report from disagreeing — the most common failure mode in hospital reporting.

**5. Re-test before acting.** Every finding here should be re-run on a twelve-month extract before it
influences staffing, scheduling or capital planning.

## 6. Limitations

- **Sample size.** Ten admissions cannot support inference. Percentages describe this extract only.
- **Single month.** January 2026; no seasonality, no year-on-year comparison.
- **Synthetic data.** No cost, laboratory, readmission or discharge-destination fields, so occupancy
  cannot be converted into financial or clinical outcome impact.
- **Point-in-time status.** `Treatment_Status` is a snapshot at extract date, not a discharge outcome.
- **Stored length of stay.** The source provides `Length_of_Stay` directly rather than admission and
  discharge dates, so the figure cannot be audited against a calendar.

## Appendix A — Query index

| File | Contents | Queries |
|---|---|---:|
| `00_create_schema.sql` | Database, tables, PK/FK, checks, indexes | — |
| `01_load_data.sql` | Bulk insert and inline load, row-count check | — |
| `02_task1_retrieving_and_filtering.sql` | Filters: city, stay, age, compound, `IN` | 5 |
| `03_task2_filtering_sorting_aggregation.sql` | `TOP`, `DISTINCT`, `COUNT`, `AVG`, `GROUP BY` | 5 |
| `04_task3_string_functions_and_dates.sql` | `UPPER`, `LOWER`, `CONCAT`, `YEAR`, `MONTH`, `DATENAME` | 5 |
| `05_task4_advanced_aggregation.sql` | `HAVING`, `CASE`, CTE, banding | 6 |
| `06_task5_keys_and_joins.sql` | Integrity proof, `INNER`/`LEFT JOIN`, `RANK()` | 6 |
| `07_reporting_views.sql` | Five reusable reporting views | 5 views |
| `08_data_quality_checks.sql` | Eight validations, zero rows when clean | 8 |

## Appendix B — Verification

```sql
SELECT COUNT(*) AS Doctors  FROM dbo.Doctors;   -- 3
SELECT COUNT(*) AS Patients FROM dbo.Patients;  -- 10
SELECT SUM(Length_of_Stay) AS Bed_Days FROM dbo.Patients;  -- 44

SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10,2)) AS Avg_LOS
FROM dbo.Patients
GROUP BY Admission_Type
HAVING AVG(Length_of_Stay * 1.0) > 4;
-- Scheduled | 6.50
```

All figures in this report are reproduced in `analysis/results.json` and visualised in `index.html`.
