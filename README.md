# Hospital Database SQL Analysis

A SQL Server (T-SQL) assignment analysing a small hospital dataset of patients and doctors, completed as part of an LMS SQL course.

**Author:** Amandi Delight Chukwuebuka

## Dataset

| File | Description |
|------|-------------|
| `data/Patients.csv` | 10 patient records: demographics, city, condition, admission type, doctor, admission date, length of stay, treatment status |
| `data/Doctors.csv` | 3 doctors: ID, name, specialization |

`Patients.Doctor_ID` links to `Doctors.Doctor_ID`.

## What's covered

| Task | Topics |
|------|--------|
| 1. Retrieving & filtering | `WHERE`, `BETWEEN`, `IN`, `AND` |
| 2. Sorting & aggregating | `TOP`, `ORDER BY`, `DISTINCT`, `COUNT`, `AVG`, `GROUP BY` |
| 3. String functions & dates | `UPPER`, `LOWER`, `CONCAT`, `YEAR`, `MONTH`, `DATENAME` |
| 4. Advanced aggregation | `HAVING`, `CASE WHEN`, CTEs |
| 5. Keys & joins | `INNER JOIN`, joins with aggregation |

## How to run

1. Open SQL Server Management Studio (SSMS).
2. Import `data/Doctors.csv` and `data/Patients.csv` into a database named `HospitalDataBase` (right-click the database → Tasks → Import Flat File).
3. Open and run `sql/hospital_analysis.sql`.

## Repository structure

```
hospital-sql-analysis/
├── data/
│   ├── Doctors.csv
│   └── Patients.csv
├── sql/
│   └── hospital_analysis.sql
└── README.md
```

## Tools

SQL Server, SSMS
