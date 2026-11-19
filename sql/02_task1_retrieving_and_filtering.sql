/*
================================================================================
 02_task1_retrieving_and_filtering.sql
 TASK 1 - Retrieving and filtering data
--------------------------------------------------------------------------------
 Concepts: SELECT *, WHERE, AND, BETWEEN, IN
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. Retrieve all patients from Lagos
      -> 3 rows: Aisha Bello, Zainab Ali, Mary Johnson                        */
SELECT *
FROM dbo.Patients
WHERE City = 'Lagos';
GO

/* 2. Find all patients whose length of stay is greater than 5 days
      -> 3 rows: David Mensah (7), Grace Eze (8), Mary Johnson (6)            */
SELECT *
FROM dbo.Patients
WHERE Length_of_Stay > 5;
GO

/* 3. Find patients whose age is between 30 and 50 (inclusive)
      -> 5 rows                                                               */
SELECT *
FROM dbo.Patients
WHERE Age BETWEEN 30 AND 50;
GO

/* 4. Female patients from Lagos admitted through Emergency
      -> 1 row: Aisha Bello                                                   */
SELECT *
FROM dbo.Patients
WHERE Gender         = 'Female'
  AND City           = 'Lagos'
  AND Admission_Type = 'Emergency';
GO

/* 5. Patients diagnosed with Diabetes or Hypertension
      -> 4 rows                                                               */
SELECT *
FROM dbo.Patients
WHERE Condition IN ('Diabetes', 'Hypertension');
GO
