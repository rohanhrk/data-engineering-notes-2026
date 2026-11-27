-- ============================================================
-- 02. CREATE SCHEMAS
-- Reconnect to database: redshift_practical
-- This script creates a layered structure often used in
-- real data engineering projects.
-- Core logic:
-- Instead of keeping everything in one schema, we separate objects
-- by purpose so Redshift environments are
-- organized in production.
-- ============================================================

-- staging   : temporary/raw landing area for new incoming data
-- sales     : curated core business tables
-- analytics : reporting-ready derived objects such as materialized views
-- sandbox   : safe area for experiments and reload validation
create schema if not exists staging;
create schema if not exists sales;
create schema if not exists analytics;
create schema if not exists sandbox