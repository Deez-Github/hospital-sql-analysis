/*
================================================================================
 08_data_quality_checks.sql
 Validation queries - every check should return an empty result set
--------------------------------------------------------------------------------
 These are the checks a reviewer runs before trusting any dashboard number.
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. Orphan admissions - a Doctor_ID with no matching doctor.                  */
SELECT P.Patient_ID, P.Doctor_ID
FROM dbo.Patients AS P
LEFT JOIN dbo.Doctors AS D ON D.Doctor_ID = P.Doctor_ID
WHERE D.Doctor_ID IS NULL;
GO

/* 2. Duplicate primary keys (PK should prevent them; proves it does).          */
SELECT Patient_ID, COUNT(*) AS Occurrences
FROM dbo.Patients
GROUP BY Patient_ID
HAVING COUNT(*) > 1;
GO

/* 3. Duplicate admissions - same person, same admission date.                  */
SELECT Patient_Name, Admission_Date, COUNT(*) AS Occurrences
FROM dbo.Patients
GROUP BY Patient_Name, Admission_Date
HAVING COUNT(*) > 1;
GO

/* 4. Missing critical fields.                                                  */
SELECT Patient_ID
FROM dbo.Patients
WHERE Patient_Name     IS NULL
   OR City             IS NULL
   OR Condition        IS NULL
   OR Admission_Date   IS NULL
   OR Length_of_Stay   IS NULL;
GO

/* 5. Out-of-range values (age, length of stay, admission date).                */
SELECT Patient_ID, Age, Length_of_Stay, Admission_Date
FROM dbo.Patients
WHERE Age NOT BETWEEN 0 AND 120
   OR Length_of_Stay <= 0
   OR Admission_Date < '2000-01-01'
   OR Admission_Date > GETDATE();
GO

/* 6. Values outside the allowed domains.                                       */
SELECT DISTINCT Gender         FROM dbo.Patients WHERE Gender         NOT IN ('Male', 'Female');
SELECT DISTINCT Admission_Type FROM dbo.Patients WHERE Admission_Type NOT IN ('Emergency', 'Scheduled');
SELECT DISTINCT Treatment_Status FROM dbo.Patients WHERE Treatment_Status NOT IN ('Recovered', 'Recovering');
GO

/* 7. Reconciliation - row counts and bed-days must match the source extract.    */
SELECT (SELECT COUNT(*) FROM dbo.Patients)  AS Patient_Rows,
       (SELECT COUNT(*) FROM dbo.Doctors)   AS Doctor_Rows,
       (SELECT SUM(Length_of_Stay) FROM dbo.Patients) AS Bed_Days;
GO

/* 8. Referential completeness - every doctor is used by at least one admission.
      A row here is not an error, only a flag for the workload report.           */
SELECT D.Doctor_Name, COUNT(P.Patient_ID) AS Patients
FROM dbo.Doctors AS D
LEFT JOIN dbo.Patients AS P ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_Name
HAVING COUNT(P.Patient_ID) = 0;
GO
