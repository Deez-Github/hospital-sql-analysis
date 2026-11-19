/*
================================================================================
 04_task3_string_functions_and_dates.sql
 TASK 3 - String functions and date handling
--------------------------------------------------------------------------------
 Concepts: UPPER, LOWER, CONCAT, YEAR, MONTH, DATENAME, date literals
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. Patient names in uppercase                                               */
SELECT Patient_ID,
       Patient_Name,
       UPPER(Patient_Name) AS Name_Upper
FROM dbo.Patients;
GO

/* 2. Patient names in lowercase                                               */
SELECT Patient_ID,
       Patient_Name,
       LOWER(Patient_Name) AS Name_Lower
FROM dbo.Patients;
GO

/* 3. Combine Patient_ID and Patient_Name into a single label
      -> '1 Aisha Bello'                                                      */
SELECT CONCAT(Patient_ID, ' ', Patient_Name) AS Patient_Details
FROM dbo.Patients;
GO

/* 4. Patients admitted after 15 January 2026
      '>' is strict, so Zainab Ali (15 Jan) is excluded. Use '>=' to include her.
      -> 5 rows                                                               */
SELECT *
FROM dbo.Patients
WHERE Admission_Date > '2026-01-15';
GO

/* 5. Admission year, month number and month name for every patient           */
SELECT Patient_ID,
       Patient_Name,
       YEAR(Admission_Date)            AS Admission_Year,
       MONTH(Admission_Date)           AS Admission_Month,
       DATENAME(MONTH, Admission_Date) AS Admission_Month_Name
FROM dbo.Patients;
GO
