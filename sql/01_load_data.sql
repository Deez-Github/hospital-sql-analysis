/*
================================================================================
 01_load_data.sql
 Hospital Data Analytics - data load
--------------------------------------------------------------------------------
 Two ways to load the sample extracts kept in /data:
   A. BULK INSERT  - preferred, uses the CSV files as-is
   B. Inline INSERT - self-contained, no file-path permissions needed
 Both produce exactly the same 3 doctors and 10 admissions.
================================================================================
*/
USE HospitalDataBase;
GO

/* ---------------------------------------------------------------------------
   A. BULK INSERT  (edit the paths to match your machine)
   --------------------------------------------------------------------------- */
-- BULK INSERT dbo.Doctors
-- FROM 'C:\SQLData\doctors.csv'
-- WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', TABLOCK);

-- BULK INSERT dbo.Patients
-- FROM 'C:\SQLData\patients.csv'
-- WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', TABLOCK);

/* UTF-8 CSVs need a code page hint on some builds; use this form if you see
   mojibake in names:  WITH (FIRSTROW = 2, FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '0x0a', CODEPAGE = '65001'); */

/* ---------------------------------------------------------------------------
   B. Inline load - parent table first, then the child table
   --------------------------------------------------------------------------- */
INSERT INTO dbo.Doctors (Doctor_ID, Doctor_Name, Specialization) VALUES
    (1, 'Dr. Ade',   'General Medicine'),
    (2, 'Dr. Musa',  'Internal Medicine'),
    (3, 'Dr. Bello', 'Family Medicine');
GO

INSERT INTO dbo.Patients
    (Patient_ID, Patient_Name, Age, Gender, City, Condition,
     Admission_Type, Doctor_ID, Admission_Date, Length_of_Stay, Treatment_Status)
VALUES
    ( 1, 'Aisha Bello',    34, 'Female', 'Lagos',         'Malaria',      'Emergency', 1, '2026-01-05', 3, 'Recovered'),
    ( 2, 'Chinedu Okafor', 52, 'Male',   'Abuja',         'Hypertension', 'Scheduled', 2, '2026-01-07', 5, 'Recovering'),
    ( 3, 'Fatima Yusuf',   27, 'Female', 'Kano',          'Typhoid',      'Emergency', 3, '2026-01-10', 4, 'Recovered'),
    ( 4, 'David Mensah',   61, 'Male',   'Accra',         'Diabetes',     'Scheduled', 1, '2026-01-12', 7, 'Recovering'),
    ( 5, 'Zainab Ali',     45, 'Female', 'Lagos',         'Asthma',       'Emergency', 2, '2026-01-15', 2, 'Recovered'),
    ( 6, 'Tunde Adeyemi',  39, 'Male',   'Ibadan',        'Malaria',      'Emergency', 3, '2026-01-18', 3, 'Recovered'),
    ( 7, 'Grace Eze',      68, 'Female', 'Enugu',         'Hypertension', 'Scheduled', 1, '2026-01-20', 8, 'Recovering'),
    ( 8, 'Ibrahim Musa',   23, 'Male',   'Kaduna',        'Typhoid',      'Emergency', 2, '2026-01-22', 4, 'Recovered'),
    ( 9, 'Mary Johnson',   56, 'Female', 'Lagos',         'Diabetes',     'Scheduled', 3, '2026-01-24', 6, 'Recovering'),
    (10, 'Samuel Obi',     41, 'Male',   'Port Harcourt', 'Asthma',       'Emergency', 1, '2026-01-27', 2, 'Recovered');
GO

/* ---------------------------------------------------------------------------
   Verification - should return 3 and 10
   --------------------------------------------------------------------------- */
SELECT 'Doctors' AS Table_Name, COUNT(*) AS Rows_Loaded FROM dbo.Doctors
UNION ALL
SELECT 'Patients', COUNT(*) FROM dbo.Patients;
GO
