# Findings

**Dataset:** 10 admissions, 3 physicians, 5–27 January 2026.
**Method:** T-SQL in `sql/`, reproduced in Python/SQLite so every figure is auditable.
**Caveat that applies to everything below:** n = 10. These are descriptions of one month's extract,
not estimates of hospital-wide performance.

---

## 1. Admission channel is the strongest predictor of length of stay

| Admission type | Patients | Bed-days | Average stay |
|---|---:|---:|---:|
| Emergency | 6 | 18 | **3.0 days** |
| Scheduled | 4 | 26 | **6.5 days** |

Scheduled admissions stay **2.2× longer**. They are only 40% of the caseload but generate 59% of all
bed-days. The `HAVING AVG(Length_of_Stay * 1.0) > 4` query returns `Scheduled` alone — a clean
demonstration that filtering on an aggregate separates the two channels without any manual inspection.

**Why it matters.** Emergency demand is largely outside the hospital's control; scheduled volume is not.
Pre-admission planning, discharge targeting and theatre/procedure scheduling all sit on the scheduled
pathway, which is where a bed-day reduction would actually land.

## 2. Six patients account for three quarters of occupancy

Applying the brief's banding rule (≤ 3 days = short stay, > 3 days = long stay):

| Band | Patients | Bed-days | Share of bed-days |
|---|---:|---:|---:|
| Short stay (≤ 3 d) | 4 | 10 | 23% |
| Long stay (> 3 d) | 6 | 34 | **77%** |

Length of stay, not admission volume, is the lever. A 10% reduction in long-stay days saves 3.4
bed-days; the same relative cut across short stays saves 1.0.

## 3. Lagos dominates a highly dispersed catchment

| City | Patients |
|---|---:|
| Lagos | 3 |
| Abuja · Kano · Accra · Ibadan · Enugu · Kaduna · Port Harcourt | 1 each |

Eight cities, but only one with repeat volume. Lagos contributes 30% of admissions; the other seven
cities contribute one each. For referral planning this is a concentration risk: a single-city
capacity constraint would affect a third of the caseload, while the remaining two-thirds would be
expensive to serve because each origin is a one-off.

## 4. Older patients stay materially longer (signal, not proof)

| Age band | Rule | Patients | Average stay |
|---|---|---:|---:|
| Young | < 40 | 4 | 3.50 days |
| Middle-aged | 40–59 | 4 | 3.75 days |
| Senior | 60+ | 2 | **7.50 days** |

The two senior patients (61 and 68) stayed 7 and 8 days respectively — the second and first longest
stays in the dataset. The effect size is large enough to justify a dedicated older-patient pathway,
but with two observations it is a hypothesis to test at scale, not a planning input.

## 5. Physician workload is uneven but not extreme

| Physician | Specialization | Patients | Bed-days | Average stay |
|---|---|---:|---:|---:|
| Dr. Ade | General Medicine | 4 | 20 | 5.00 days |
| Dr. Bello | Family Medicine | 3 | 13 | 4.33 days |
| Dr. Musa | Internal Medicine | 3 | 11 | 3.67 days |

Dr. Ade carries 40% of patients and 45% of bed-days. That is consistent with general medicine acting
as the front door, and it is not yet a capacity problem — but it is the number to watch as volume grows.
Note the inversion: the physician with the **fewest** bed-days per patient (Dr. Musa) treats the
Internal Medicine panel, which is often assumed to be the heaviest.

## 6. Case mix is perfectly flat — and that is a data artefact

| Condition | Patients | Average stay |
|---|---:|---:|
| Diabetes | 2 | 6.50 days |
| Hypertension | 2 | 6.50 days |
| Typhoid | 2 | 4.00 days |
| Malaria | 2 | 3.00 days |
| Asthma | 2 | 2.00 days |

Every condition appears exactly twice, so `HAVING COUNT(*) > 1` returns the entire list. In a real
extract this query would surface the chronic conditions that dominate volume; here it demonstrates
the syntax without saying anything about disease prevalence.

The chronic pair (Diabetes, Hypertension) shows the longest average stay at 6.5 days — a directional
hint that matches clinical expectation, but n = 2 per condition.

---

## Recommendations

1. **Instrument the scheduled pathway first.** It is 40% of admissions and 59% of bed-days. Even a
   one-day reduction in average scheduled stay frees roughly 4 bed-days per 10 admissions.
2. **Build an older-patient discharge plan.** Seniors average 7.5 days on two cases. Add an age-band
   flag to the admission record and monitor it monthly.
3. **Treat catchment concentration as an operational risk.** Lagos is 30% of volume; the other seven
   origins are single events. Referral logistics, not bed capacity, is the binding constraint there.
4. **Keep the banding rules in a view, not in queries.** `vw_PatientAdmissions` defines age and stay
   bands once, so every report agrees on what "long stay" means.
5. **Re-run on a 12-month extract before any decision.** All five findings should be re-tested at
   n ≥ 300 before they influence staffing or scheduling.

## Threats to validity

| Risk | Effect | Mitigation |
|---|---|---|
| n = 10 | Percentages are unstable; one patient moves a rate by 10 points | Report counts alongside percentages |
| Single month | No seasonality; January may be atypical | Extend to 12 months |
| Synthetic data | Findings may not reflect real case mix | Treat as methodology demonstration |
| Balanced conditions | Condition comparisons are not informative | Explicitly labelled as an artefact |
| No cost data | Occupancy cannot be converted to financial impact | Add cost per bed-day |
