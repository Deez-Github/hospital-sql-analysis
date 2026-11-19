# Data dictionary

Two tables in `HospitalDataBase`. Both are loaded from the CSV extracts in [`/data`](../data).

---

## `dbo.Doctors` — 3 rows

Parent table. One row per physician.

| Column | Type | Key | Nullable | Description | Allowed values |
|---|---|---|---|---|---|
| `Doctor_ID` | `INT` | **PK** | no | Surrogate identifier | 1–3 |
| `Doctor_Name` | `VARCHAR(100)` | UQ | no | Display name used in reports | `Dr. Ade`, `Dr. Musa`, `Dr. Bello` |
| `Specialization` | `VARCHAR(60)` | | no | Clinical service line | General / Internal / Family Medicine |

## `dbo.Patients` — 10 rows

Child table. One row per admission.

| Column | Type | Key | Nullable | Description | Allowed values |
|---|---|---|---|---|---|
| `Patient_ID` | `INT` | **PK** | no | Admission identifier | 1–10 |
| `Patient_Name` | `VARCHAR(100)` | | no | Patient display name | free text |
| `Age` | `INT` | | no | Age in years at admission | `CHECK 0–120` |
| `Gender` | `VARCHAR(10)` | | no | Recorded gender | `Male`, `Female` |
| `City` | `VARCHAR(60)` | | no | City of residence | 8 distinct values |
| `Condition` | `VARCHAR(60)` | | no | Primary diagnosis | Malaria, Typhoid, Hypertension, Diabetes, Asthma |
| `Admission_Type` | `VARCHAR(20)` | | no | Admission channel | `Emergency`, `Scheduled` |
| `Doctor_ID` | `INT` | **FK** → `Doctors` | no | Treating physician | 1–3 |
| `Admission_Date` | `DATE` | | no | Date of admission | Jan 2026 |
| `Length_of_Stay` | `INT` | | no | Days admitted | `CHECK > 0` |
| `Treatment_Status` | `VARCHAR(20)` | | no | Status at extract date | `Recovered`, `Recovering` |

## Constraints

| Name | Type | Rule |
|---|---|---|
| `PK_Doctors` | Primary key | `Doctor_ID` |
| `UQ_Doctors_Name` | Unique | `Doctor_Name` |
| `PK_Patients` | Primary key | `Patient_ID` |
| `FK_Patients_Doctors` | Foreign key | `Patients.Doctor_ID → Doctors.Doctor_ID` |
| `CK_Patients_Age` | Check | `Age BETWEEN 0 AND 120` |
| `CK_Patients_LOS` | Check | `Length_of_Stay > 0` |
| `CK_Patients_Gender` | Check | `Gender IN ('Male','Female')` |
| `CK_Patients_Admit` | Check | `Admission_Type IN ('Emergency','Scheduled')` |
| `CK_Patients_Status` | Check | `Treatment_Status IN ('Recovered','Recovering')` |
| `IX_Patients_Doctor` | Index | `Doctor_ID` (join) |
| `IX_Patients_City` | Index | `City` (filter) |
| `IX_Patients_Admitted` | Index | `Admission_Date` (range filter) |

## Derived fields

These are never stored — they are computed in `CASE` expressions so the definition cannot drift
between reports. `vw_PatientAdmissions` exposes both.

| Field | Rule | Values |
|---|---|---|
| `Age_Group` | `< 40` → Young; `< 60` → Middle-aged; else Senior | Young / Middle-aged / Senior |
| `Stay_Category` | `<= 3` → Short Stay; else Long Stay | Short Stay / Long Stay |
| `Admission_Month_Name` | `DATENAME(MONTH, Admission_Date)` | `January` |

## Grain and integrity notes

- **Grain of `Patients` is one admission**, not one person. A readmitted patient would appear twice;
  the duplicate check in `08_data_quality_checks.sql` catches same-name / same-date collisions.
- **`Doctor_ID` is mandatory.** There is no "unassigned" state, which is why the join in Task 5 can
  safely be an `INNER JOIN`.
- **`Length_of_Stay` is stored, not derived** from admission and discharge dates. This matches the
  source extract; a production model would store `Discharge_Date` and compute the difference.
- **`Treatment_Status` is a point-in-time snapshot** at extract date, not a discharge outcome.
