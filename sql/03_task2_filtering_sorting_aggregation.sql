/*
================================================================================
 03_task2_filtering_sorting_aggregation.sql
 TASK 2 - Sorting and aggregation
--------------------------------------------------------------------------------
 Concepts: TOP, ORDER BY, DISTINCT, COUNT, AVG, GROUP BY
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. The 3 patients with the longest stays, longest first
      -> Grace Eze (8), David Mensah (7), Mary Johnson (6)                    */
SELECT TOP (3) *
FROM dbo.Patients
ORDER BY Length_of_Stay DESC;
GO

/* 2. Every distinct city represented in the dataset
      -> 8 cities                                                             */
SELECT DISTINCT City
FROM dbo.Patients
ORDER BY City;
GO

/* 3. Total number of patients                                                 */
SELECT COUNT(*) AS Total_Patients
FROM dbo.Patients;
GO

/* 4. Average patient age
      AVG() on an INT column performs integer division in SQL Server, so the
      column is multiplied by 1.0 first and the result cast back to 2 decimals. */
SELECT CAST(AVG(Age * 1.0) AS DECIMAL(10, 2)) AS Avg_Age
FROM dbo.Patients;
GO

/* 5. Number of patients per medical condition                                  */
SELECT Condition,
       COUNT(*) AS Patients_Count
FROM dbo.Patients
GROUP BY Condition
ORDER BY Patients_Count DESC, Condition;
GO
