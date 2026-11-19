/*
================================================================================
 05_task4_advanced_aggregation.sql
 TASK 4 - Advanced aggregation and conditional analysis
--------------------------------------------------------------------------------
 Concepts: GROUP BY + aggregate, HAVING, CASE, CTE (WITH), business rules
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. Average length of stay per admission type
      -> Emergency 3.00 | Scheduled 6.50                                     */
SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10, 2)) AS Avg_LOS
FROM dbo.Patients
GROUP BY Admission_Type;
GO

/* 2. Admission types with an average stay longer than 4 days
      -> Scheduled only - this is what HAVING is for                         */
SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10, 2)) AS Avg_LOS
FROM dbo.Patients
GROUP BY Admission_Type
HAVING AVG(Length_of_Stay * 1.0) > 4;
GO

/* 3. Classify patients as Young (<40), Middle-aged (40-59) or Senior (60+)  */
SELECT Patient_Name,
       Age,
       CASE
           WHEN Age < 40 THEN 'Young'
           WHEN Age < 60 THEN 'Middle-aged'
           ELSE 'Senior'
       END AS Age_Group
FROM dbo.Patients;
GO

/* 4. Count patients per age group using a CTE
      -> Young 4 | Middle-aged 4 | Senior 2                                  */
WITH AgeGroup AS
(
    SELECT CASE
               WHEN Age < 40 THEN 'Young'
               WHEN Age < 60 THEN 'Middle-aged'
               ELSE 'Senior'
           END AS Age_Group
    FROM dbo.Patients
)
SELECT Age_Group,
       COUNT(*) AS PatientCount
FROM AgeGroup
GROUP BY Age_Group
ORDER BY PatientCount DESC, Age_Group;
GO

/* 5. Short stay (<= 3 days) vs Long stay (> 3 days)
      -> Short 4 | Long 6                                                    */
SELECT Patient_ID,
       Patient_Name,
       Length_of_Stay,
       CASE
           WHEN Length_of_Stay <= 3 THEN 'Short Stay'
           ELSE 'Long Stay'
       END AS Stay_Category
FROM dbo.Patients;
GO

/* 6. Conditions affecting more than one patient
      -> all five conditions (two patients each)                             */
SELECT Condition,
       COUNT(*) AS Patient_Count
FROM dbo.Patients
GROUP BY Condition
HAVING COUNT(*) > 1
ORDER BY Patient_Count DESC, Condition;
GO
