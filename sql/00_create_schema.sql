/*
================================================================================
 00_create_schema.sql
 Hospital Data Analytics - schema definition (Microsoft SQL Server / T-SQL)
--------------------------------------------------------------------------------
 Creates the database, both tables, keys and constraints.
 Run order: 00 -> 01 -> 02..06 (tasks). Safe to re-run: objects are dropped first.
================================================================================
*/

IF DB_ID('HospitalDataBase') IS NULL
    CREATE DATABASE HospitalDataBase;
GO

USE HospitalDataBase;
GO

/* Drop in child -> parent order so the foreign key never blocks the re-run. */
IF OBJECT_ID('dbo.Patients', 'U') IS NOT NULL DROP TABLE dbo.Patients;
IF OBJECT_ID('dbo.Doctors',  'U') IS NOT NULL DROP TABLE dbo.Doctors;
GO

/* ---------------------------------------------------------------------------
   Doctors - one row per physician (parent table)
   --------------------------------------------------------------------------- */
CREATE TABLE dbo.Doctors
(
    Doctor_ID       INT           NOT NULL,
    Doctor_Name     VARCHAR(100)  NOT NULL,
    Specialization  VARCHAR(60)   NOT NULL,
    CONSTRAINT PK_Doctors      PRIMARY KEY (Doctor_ID),
    CONSTRAINT UQ_Doctors_Name UNIQUE (Doctor_Name)
);
GO

/* ---------------------------------------------------------------------------
   Patients - one row per admission (child table)
   Doctor_ID is a foreign key to Doctors, so every admission must reference
   a physician that actually exists.
   --------------------------------------------------------------------------- */
CREATE TABLE dbo.Patients
(
    Patient_ID        INT           NOT NULL,
    Patient_Name      VARCHAR(100)  NOT NULL,
    Age               INT           NOT NULL,
    Gender            VARCHAR(10)   NOT NULL,
    City              VARCHAR(60)   NOT NULL,
    Condition         VARCHAR(60)   NOT NULL,
    Admission_Type    VARCHAR(20)   NOT NULL,
    Doctor_ID         INT           NOT NULL,
    Admission_Date    DATE          NOT NULL,
    Length_of_Stay    INT           NOT NULL,
    Treatment_Status  VARCHAR(20)   NOT NULL,
    CONSTRAINT PK_Patients          PRIMARY KEY (Patient_ID),
    CONSTRAINT FK_Patients_Doctors  FOREIGN KEY (Doctor_ID)
                                    REFERENCES dbo.Doctors (Doctor_ID),
    CONSTRAINT CK_Patients_Age      CHECK (Age BETWEEN 0 AND 120),
    CONSTRAINT CK_Patients_LOS      CHECK (Length_of_Stay > 0),
    CONSTRAINT CK_Patients_Gender   CHECK (Gender IN ('Male', 'Female')),
    CONSTRAINT CK_Patients_Admit    CHECK (Admission_Type IN ('Emergency', 'Scheduled')),
    CONSTRAINT CK_Patients_Status   CHECK (Treatment_Status IN ('Recovered', 'Recovering'))
);
GO

/* Helpful indexes for the filters and joins used in the analysis. */
CREATE INDEX IX_Patients_Doctor   ON dbo.Patients (Doctor_ID);
CREATE INDEX IX_Patients_City     ON dbo.Patients (City);
CREATE INDEX IX_Patients_Admitted ON dbo.Patients (Admission_Date);
GO

/* Sanity check: 2 tables, 6 constraints on Patients, 1 on Doctors. */
SELECT t.name AS Table_Name, k.name AS Constraint_Name, k.type_desc
FROM sys.tables t
JOIN sys.key_constraints k ON k.parent_object_id = t.object_id
ORDER BY t.name, k.name;
GO
