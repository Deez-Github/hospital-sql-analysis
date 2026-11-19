/*
================================================================================
 06_task5_keys_and_joins.sql
 TASK 5 - Primary & foreign keys, and SQL JOINs
--------------------------------------------------------------------------------
 Concepts: PK/FK integrity, INNER JOIN, table aliases, aggregate over a join
================================================================================
*/
USE HospitalDataBase;
GO

/* 1. Verify both imported tables loaded correctly
      -> Doctors 3 rows | Patients 10 rows                                  */
SELECT * FROM dbo.Doctors;
SELECT * FROM dbo.Patients;
GO

/* 1b. Prove the foreign key is enforced: every Doctor_ID in Patients
       resolves to a real physician (returns 0 rows when the data is clean).   */
SELECT P.Patient_ID, P.Doctor_ID
FROM dbo.Patients AS P
LEFT JOIN dbo.Doctors AS D ON D.Doctor_ID = P.Doctor_ID
WHERE D.Doctor_ID IS NULL;
GO

/* 2. Each patient's name alongside their doctor's specialization              */
SELECT P.Patient_Name,
       D.Specialization
FROM dbo.Patients AS P
INNER JOIN dbo.Doctors AS D
        ON P.Doctor_ID = D.Doctor_ID;
GO

/* 3. All patients treated by doctors specialising in Internal Medicine
      -> 3 rows, all under Dr. Musa                                          */
SELECT P.Patient_Name,
       D.Specialization,
       D.Doctor_Name
FROM dbo.Patients AS P
INNER JOIN dbo.Doctors AS D
        ON P.Doctor_ID = D.Doctor_ID
WHERE D.Specialization = 'Internal Medicine';
GO

/* 4. Average length of stay per doctor
      -> Dr. Ade 5.00 | Dr. Bello 4.33 | Dr. Musa 3.67                        */
SELECT D.Doctor_ID,
       D.Doctor_Name,
       COUNT(*)                                          AS Patients,
       CAST(AVG(P.Length_of_Stay * 1.0) AS DECIMAL(10, 2)) AS Avg_LOS
FROM dbo.Patients AS P
INNER JOIN dbo.Doctors AS D
        ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_ID, D.Doctor_Name
ORDER BY Avg_LOS DESC;
GO

/* 5. Doctor who treated the highest number of patients
      -> Dr. Ade with 4 patients                                             */
SELECT TOP (1)
       D.Doctor_ID,
       D.Doctor_Name,
       COUNT(*) AS Patient_Count
FROM dbo.Patients AS P
INNER JOIN dbo.Doctors AS D
        ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_ID, D.Doctor_Name
ORDER BY COUNT(*) DESC;
GO

/* 6. Same ranking, but keeping every doctor (LEFT JOIN) and using a window
      function so ties are visible instead of silently dropped by TOP 1.      */
SELECT D.Doctor_Name,
       D.Specialization,
       COUNT(P.Patient_ID) AS Patient_Count,
       RANK() OVER (ORDER BY COUNT(P.Patient_ID) DESC) AS Workload_Rank
FROM dbo.Doctors AS D
LEFT JOIN dbo.Patients AS P ON P.Doctor_ID = D.Doctor_ID
GROUP BY D.Doctor_Name, D.Specialization
ORDER BY Workload_Rank;
GO
