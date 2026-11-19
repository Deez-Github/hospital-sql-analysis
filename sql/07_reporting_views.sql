/*
================================================================================
 07_reporting_views.sql
 Reusable reporting layer built on top of the assignment queries
--------------------------------------------------------------------------------
 The dashboard and the written report are driven by these views, so the
 business rules (age bands, stay bands) are defined exactly once.
================================================================================
*/
USE HospitalDataBase;
GO

/* One row per admission, already enriched with doctor and banding logic. */
CREATE OR ALTER VIEW dbo.vw_PatientAdmissions
AS
SELECT P.Patient_ID,
       P.Patient_Name,
       P.Age,
       CASE WHEN P.Age < 40 THEN 'Young'
            WHEN P.Age < 60 THEN 'Middle-aged'
            ELSE 'Senior' END              AS Age_Group,
       P.Gender,
       P.City,
       P.Condition,
       P.Admission_Type,
       D.Doctor_ID,
       D.Doctor_Name,
       D.Specialization,
       P.Admission_Date,
       P.Length_of_Stay,
       CASE WHEN P.Length_of_Stay <= 3 THEN 'Short Stay'
            ELSE 'Long Stay' END           AS Stay_Category,
       P.Treatment_Status
FROM dbo.Patients AS P
INNER JOIN dbo.Doctors AS D ON D.Doctor_ID = P.Doctor_ID;
GO

/* Physician scorecard: volume, average stay and total bed-days. */
CREATE OR ALTER VIEW dbo.vw_DoctorWorkload
AS
SELECT D.Doctor_ID,
       D.Doctor_Name,
       D.Specialization,
       COUNT(P.Patient_ID)                                AS Patients,
       SUM(P.Length_of_Stay)                              AS Bed_Days,
       CAST(AVG(P.Length_of_Stay * 1.0) AS DECIMAL(10, 2)) AS Avg_LOS
FROM dbo.Doctors AS D
LEFT JOIN dbo.Patients AS P ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_ID, D.Doctor_Name, D.Specialization;
GO

/* Service-line summary: caseload and resource use per condition. */
CREATE OR ALTER VIEW dbo.vw_ConditionSummary
AS
SELECT Condition,
       COUNT(*)                                            AS Patients,
       SUM(Length_of_Stay)                                 AS Bed_Days,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10, 2))    AS Avg_LOS,
       SUM(CASE WHEN Treatment_Status = 'Recovered' THEN 1 ELSE 0 END) AS Recovered
FROM dbo.Patients
GROUP BY Condition;
GO

/* Admission channel summary - the core operational finding. */
CREATE OR ALTER VIEW dbo.vw_AdmissionTypeSummary
AS
SELECT Admission_Type,
       COUNT(*)                                            AS Patients,
       SUM(Length_of_Stay)                                 AS Bed_Days,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10, 2))    AS Avg_LOS,
       CAST(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dbo.Patients) AS DECIMAL(5, 1)) AS Pct_Of_Caseload
FROM dbo.Patients
GROUP BY Admission_Type;
GO

/* Monthly admission volume for trend reporting. */
CREATE OR ALTER VIEW dbo.vw_MonthlyAdmissions
AS
SELECT YEAR(Admission_Date)                   AS Admission_Year,
       MONTH(Admission_Date)                  AS Admission_Month,
       DATENAME(MONTH, Admission_Date)        AS Month_Name,
       COUNT(*)                               AS Admissions,
       SUM(Length_of_Stay)                    AS Bed_Days
FROM dbo.Patients
GROUP BY YEAR(Admission_Date), MONTH(Admission_Date), DATENAME(MONTH, Admission_Date);
GO

/* Usage examples */
SELECT * FROM dbo.vw_AdmissionTypeSummary ORDER BY Avg_LOS DESC;
SELECT * FROM dbo.vw_DoctorWorkload        ORDER BY Patients DESC, Bed_Days DESC;
SELECT * FROM dbo.vw_ConditionSummary      ORDER BY Avg_LOS DESC;
SELECT * FROM dbo.vw_MonthlyAdmissions     ORDER BY Admission_Year, Admission_Month;
GO
