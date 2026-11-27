-- ============================================================
-- 01. CREATE DATABASE
-- Run this script while connected to the current admin database
-- such as 'dev' or another existing Redshift database.
-- After creation, reconnect to redshift_practical and continue.
-- Core logic:
-- We create a dedicated database first so the rest of the objects
-- are isolated from any existing project objects.
-- ============================================================

-- Create a fresh database that will hold all schemas, tables,
-- external objects, and example queries in this pack.
create database redshift_practical;

-- Validation query:
-- pg_database is a system catalog that stores database metadata.
-- This confirms that the create statement actually
-- registered the new database at the cluster level.
select datname
from pg_database
where datname = 'redshift_practical';
