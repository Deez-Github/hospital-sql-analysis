-- =====================================================
-- Hospital Database SQL Assignment (SQL Server / T-SQL)
-- Author: Amandi Delight Chukwuebuka
-- =====================================================

-- Create the HospitalDataBase database
CREATE DATABASE HospitalDataBase;
GO
USE HospitalDataBase;
GO

-- Import the Doctors and Patients CSV files (SSMS Import Flat File wizard), then verify
SELECT * FROM Doctors;
SELECT * FROM Patients;

-- =====================================================
-- TASK 1: RETRIEVING AND FILTERING DATA
-- =====================================================

-- 1. Retrieve all patients from Lagos
SELECT *
FROM Patients
WHERE City = 'Lagos';

-- 2. Find all patients whose length of stay is greater than 5 days
SELECT *
FROM Patients
WHERE Length_of_Stay > 5;

-- 3. Find patients whose age is between 30 and 50
SELECT *
FROM Patients
WHERE Age BETWEEN 30 AND 50;

-- 4. Retrieve all female patients from Lagos admitted through Emergency
SELECT *
FROM Patients
WHERE Gender = 'Female'
  AND City = 'Lagos'
  AND Admission_Type = 'Emergency';

-- 5. Retrieve all patients diagnosed with Diabetes or Hypertension
SELECT *
FROM Patients
WHERE Condition IN ('Diabetes', 'Hypertension');

-- =====================================================
-- TASK 2: SORTING AND AGGREGATING DATA
-- =====================================================

-- 1. Find the 3 patients with the longest stays, ordered from longest to shortest
SELECT TOP 3 *
FROM Patients
ORDER BY Length_of_Stay DESC;

-- 2. List all unique cities in the Patients table
SELECT DISTINCT City
FROM Patients;

-- 3. Count the total number of patients
SELECT COUNT(*) AS Total_Patients
FROM Patients;

-- 4. Calculate the average patient age
SELECT CAST(AVG(Age * 1.0) AS DECIMAL(10,2)) AS Avg_Age
FROM Patients;

-- 5. Count the number of patients for each medical condition
SELECT Condition, COUNT(*) AS Patients_Count
FROM Patients
GROUP BY Condition;

-- =====================================================
-- TASK 3: STRING FUNCTIONS AND DATES
-- =====================================================

-- 1. Display each patient's name in uppercase
SELECT Patient_ID, Patient_Name, UPPER(Patient_Name) AS Name_Upper
FROM Patients;

-- 2. Display each patient's name in lowercase
SELECT Patient_ID, Patient_Name, LOWER(Patient_Name) AS Name_Lower
FROM Patients;

-- 3. Combine Patient_ID and Patient_Name into one value
SELECT CONCAT(Patient_ID, ' ', Patient_Name) AS Patient_Details
FROM Patients;

-- 4. Find all patients admitted after January 15, 2026
SELECT *
FROM Patients
WHERE Admission_Date > '2026-01-15';

-- 5. Display the year and month in which each patient was admitted
SELECT Patient_ID,
       Patient_Name,
       YEAR(Admission_Date)  AS Admission_Year,
       MONTH(Admission_Date) AS Admission_Month,
       DATENAME(MONTH, Admission_Date) AS Admission_Month_Name
FROM Patients;

-- =====================================================
-- TASK 4: ADVANCED AGGREGATION AND CONDITIONAL ANALYSIS
-- =====================================================

-- 1. Average length of stay for each admission type
SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10,2)) AS Avg_LOS
FROM Patients
GROUP BY Admission_Type;

-- 2. Admission types with an average length of stay greater than 4 days
SELECT Admission_Type,
       CAST(AVG(Length_of_Stay * 1.0) AS DECIMAL(10,2)) AS Avg_LOS
FROM Patients
GROUP BY Admission_Type
HAVING AVG(Length_of_Stay * 1.0) > 4;

-- 3. Classify patients as Young (under 40), Middle-aged (40-59), or Senior (60+)
SELECT Patient_Name,
       Age,
       CASE
           WHEN Age < 40 THEN 'Young'
           WHEN Age < 60 THEN 'Middle-aged'
           ELSE 'Senior'
       END AS Age_Group
FROM Patients;

-- 4. Count the number of patients in each age group
WITH AgeGroup AS (
    SELECT CASE
               WHEN Age < 40 THEN 'Young'
               WHEN Age < 60 THEN 'Middle-aged'
               ELSE 'Senior'
           END AS Age_Group
    FROM Patients
)
SELECT Age_Group, COUNT(*) AS PatientCount
FROM AgeGroup
GROUP BY Age_Group;

-- 5. Categorise patients as Short Stay (3 days or less) or Long Stay (more than 3 days)
SELECT Patient_ID,
       Patient_Name,
       Length_of_Stay,
       CASE
           WHEN Length_of_Stay <= 3 THEN 'Short Stay'
           ELSE 'Long Stay'
       END AS Stay_Category
FROM Patients;

-- 6. Find medical conditions affecting more than one patient
SELECT Condition, COUNT(*) AS Patient_Count
FROM Patients
GROUP BY Condition
HAVING COUNT(*) > 1;

-- =====================================================
-- TASK 5: PRIMARY & FOREIGN KEYS AND SQL JOINS
-- =====================================================

-- 1. Import the Doctors table and verify it loaded correctly
SELECT * FROM Doctors;
SELECT * FROM Patients;

-- 2. Display each patient's name and their doctor's specialization
SELECT P.Patient_Name, D.Specialization
FROM Patients AS P
INNER JOIN Doctors AS D
    ON P.Doctor_ID = D.Doctor_ID;

-- 3. Find all patients treated by doctors specialising in Internal Medicine
SELECT P.Patient_Name, D.Specialization, D.Doctor_Name
FROM Patients AS P
INNER JOIN Doctors AS D
    ON P.Doctor_ID = D.Doctor_ID
WHERE D.Specialization = 'Internal Medicine';

-- 4. Average length of stay for patients treated by each doctor
SELECT D.Doctor_ID,
       D.Doctor_Name,
       CAST(AVG(P.Length_of_Stay * 1.0) AS DECIMAL(10,2)) AS Avg_LOS
FROM Patients AS P
INNER JOIN Doctors AS D
    ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_Name, D.Doctor_ID;

-- 5. Identify the doctor who has treated the highest number of patients
SELECT TOP 1
       D.Doctor_ID,
       D.Doctor_Name,
       COUNT(*) AS Patient_Count
FROM Patients AS P
INNER JOIN Doctors AS D
    ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_ID, D.Doctor_Name
ORDER BY COUNT(*) DESC;
