# Query catalogue

27 analytical queries across five task sets, plus five reporting views and eight validation checks.
Each row links the business question to the clause that answers it and the result the script should
return. Row counts are the regression test: if a number changes, the script comment is wrong.

Run order: `00` → `01` → `02…06`.

---

## Task 1 — Retrieving and filtering (5 queries)

File: [`sql/02_task1_retrieving_and_filtering.sql`](../sql/02_task1_retrieving_and_filtering.sql)

| # | Question | Key clause | Expected |
|---|---|---|---|
| 1 | All patients from Lagos | `WHERE City = 'Lagos'` | 3 rows |
| 2 | Patients staying longer than 5 days | `WHERE Length_of_Stay > 5` | 3 rows (7, 8, 6 days) |
| 3 | Patients aged 30–50 | `BETWEEN 30 AND 50` | 5 rows |
| 4 | Female, Lagos, emergency | `AND` × 3 | 1 row (Aisha Bello) |
| 5 | Diabetes or hypertension | `IN ('Diabetes','Hypertension')` | 4 rows |

> `BETWEEN` is inclusive on both bounds in T-SQL. Query 2 uses a strict `>`: the two 5-day patients
> are excluded, which is why the result is 3 rows and not 5.

## Task 2 — Sorting and aggregation (5 queries)

File: [`sql/03_task2_filtering_sorting_aggregation.sql`](../sql/03_task2_filtering_sorting_aggregation.sql)

| # | Question | Key clause | Expected |
|---|---|---|---|
| 1 | Three longest stays, longest first | `TOP (3) … ORDER BY Length_of_Stay DESC` | 8, 7, 6 days |
| 2 | All unique cities | `DISTINCT` | 8 cities |
| 3 | Total patients | `COUNT(*)` | 10 |
| 4 | Average patient age | `AVG(Age * 1.0)` | 44.60 |
| 5 | Patients per condition | `GROUP BY Condition` | 5 rows, 2 each |

> `AVG()` on an `INT` column does integer division, so the aggregate is multiplied by `1.0` before
> being cast to `DECIMAL(10,2)`. Omitting this returns `44` instead of `44.60`.

## Task 3 — String functions and dates (5 queries)

File: [`sql/04_task3_string_functions_and_dates.sql`](../sql/04_task3_string_functions_and_dates.sql)

| # | Question | Key clause | Expected |
|---|---|---|---|
| 1 | Names in uppercase | `UPPER()` | 10 rows |
| 2 | Names in lowercase | `LOWER()` | 10 rows |
| 3 | ID + name in one column | `CONCAT(Patient_ID,' ',Patient_Name)` | `1 Aisha Bello` … |
| 4 | Admitted after 15 Jan 2026 | `WHERE Admission_Date > '2026-01-15'` | 5 rows |
| 5 | Year / month / month name | `YEAR`, `MONTH`, `DATENAME` | 10 rows |

> Query 4 is strict: Zainab Ali was admitted on 15 January and is excluded. Switching to `>=`
> returns 6 rows. The comment in the script records this so the choice is deliberate.

## Task 4 — Advanced aggregation (6 queries)

File: [`sql/05_task4_advanced_aggregation.sql`](../sql/05_task4_advanced_aggregation.sql)

| # | Question | Key clause | Expected |
|---|---|---|---|
| 1 | Average stay per admission type | `GROUP BY Admission_Type` | Emergency 3.00 · Scheduled 6.50 |
| 2 | Channels averaging more than 4 days | `HAVING AVG(...) > 4` | 1 row: Scheduled |
| 3 | Age band per patient | `CASE` | 10 rows |
| 4 | Patients per age band | CTE + `GROUP BY` | Young 4 · Middle 4 · Senior 2 |
| 5 | Short vs long stay | `CASE WHEN Length_of_Stay <= 3` | Short 4 · Long 6 |
| 6 | Conditions with > 1 patient | `HAVING COUNT(*) > 1` | 5 rows |

> `WHERE` filters rows before aggregation; `HAVING` filters groups after it. Query 2 is the textbook
> case: no single row has a 6.5-day stay, so the filter can only exist at group level.

## Task 5 — Keys and joins (6 queries)

File: [`sql/06_task5_keys_and_joins.sql`](../sql/06_task5_keys_and_joins.sql)

| # | Question | Key clause | Expected |
|---|---|---|---|
| 1 | Verify both imports | `SELECT *` | 3 doctors · 10 patients |
| 1b | Prove referential integrity | `LEFT JOIN … WHERE D.Doctor_ID IS NULL` | 0 rows |
| 2 | Patient name + specialization | `INNER JOIN` | 10 rows |
| 3 | Internal Medicine patients | `WHERE Specialization = …` | 3 rows (all Dr. Musa) |
| 4 | Average stay per doctor | `GROUP BY` over a join | 5.00 · 4.33 · 3.67 |
| 5 | Busiest doctor | `TOP (1) … ORDER BY COUNT(*) DESC` | Dr. Ade, 4 |
| 6 | Full ranking with ties | `LEFT JOIN` + `RANK()` | 3 rows, ranks 1–3 |

> Query 5 uses `TOP (1)`, which silently drops ties. Query 6 is the production-safe version: it keeps
> every physician, including any with zero admissions, and makes ties visible.

## Reporting views (5)

File: [`sql/07_reporting_views.sql`](../sql/07_reporting_views.sql)

| View | Grain | Answers |
|---|---|---|
| `vw_PatientAdmissions` | admission | Joined, banded base table for charts |
| `vw_DoctorWorkload` | physician | Panel size, bed-days, average stay |
| `vw_ConditionSummary` | condition | Caseload and resource use per diagnosis |
| `vw_AdmissionTypeSummary` | channel | Channel comparison incl. % of caseload |
| `vw_MonthlyAdmissions` | month | Volume and bed-days by month |

## Validation checks (8)

File: [`sql/08_data_quality_checks.sql`](../sql/08_data_quality_checks.sql)

| # | Check | Pass condition |
|---|---|---|
| 1 | Orphan `Doctor_ID` | 0 rows |
| 2 | Duplicate `Patient_ID` | 0 rows |
| 3 | Duplicate name + admission date | 0 rows |
| 4 | Nulls in critical fields | 0 rows |
| 5 | Out-of-range age / stay / date | 0 rows |
| 6 | Values outside allowed domains | 0 rows |
| 7 | Row-count and bed-day reconciliation | 10 · 3 · 44 |
| 8 | Physicians with no admissions | 0 rows (flag only, not an error) |

## Python mirror

`analysis/run_analysis.py` reproduces the aggregations that feed the report and dashboard using
SQLite, with identical `CASE` logic. It is a convenience layer for CI and for readers without SQL
Server — the T-SQL files remain the source of truth.
