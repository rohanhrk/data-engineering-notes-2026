## What This Practical Covers

- Create database
- Create schemas
- Create internal tables
- Distribution style and sort keys
- `COPY` based loading
- `UNLOAD` to S3
- Multipart `UNLOAD`
- Manifest-based reload
- External schema and external tables
- Redshift Spectrum
- Materialized views
- CTAS and temporary tables
- Incremental loading with `MERGE`
- Semi-structured data with `SUPER`
- Monitoring, statistics, and maintenance commands

## Folder Structure

- `sql/` - all Redshift SQL scripts in execution order
- `data/internal/` - sample CSV data for internal Redshift tables
- `data/spectrum/` - sample partitioned data for Spectrum external tables

## Before You Start

Replace these placeholders everywhere in the SQL scripts:

- `<YOUR_IAM_ROLE_ARN>`
- `<YOUR_BUCKET>`
- `<YOUR_REGION>`

Example bucket layout expected by these scripts:

- `s3://<YOUR_BUCKET>/redshift-practical/internal/customers.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/internal/products.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/internal/orders.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/internal/order_items.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/internal/orders_delta.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/spectrum/event_date=2026-03-01/events_2026_03_01.csv`
- `s3://<YOUR_BUCKET>/redshift-practical/spectrum/event_date=2026-03-02/events_2026_03_02.csv`

Upload the local `data/` files to S3 by preserving the same file names and partition folder names.

## Suggested Teaching Order

1. Run [sql/01_create_database.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/01_create_database.sql) from your current admin database.
2. Reconnect to the new database `redshift_practical`.
3. Run [sql/02_create_schemas.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/02_create_schemas.sql).
4. Run [sql/03_create_internal_tables.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/03_create_internal_tables.sql).
5. Load data with [sql/04_copy_load_internal_data.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/04_copy_load_internal_data.sql).
6. Explore modeling and performance with [sql/05_querying_and_design_validation.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/05_querying_and_design_validation.sql).
7. Demonstrate `UNLOAD` using [sql/06_unload_single_file.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/06_unload_single_file.sql).
8. Demonstrate multipart `UNLOAD` and manifest reload using [sql/07_unload_multipart_and_manifest.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/07_unload_multipart_and_manifest.sql).
9. Create external schema and external table using [sql/08_external_schema_and_spectrum.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/08_external_schema_and_spectrum.sql).
10. Show Spectrum queries through [sql/09_spectrum_queries.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/09_spectrum_queries.sql).
11. Create and refresh materialized views with [sql/10_materialized_views.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/10_materialized_views.sql).
12. Cover engineering patterns with [sql/11_data_engineering_patterns.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/11_data_engineering_patterns.sql).
13. Finish with monitoring and housekeeping using [sql/12_maintenance_and_monitoring.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/12_maintenance_and_monitoring.sql).
14. Optionally show semi-structured analytics with [sql/13_bonus_super_and_semi_structured.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/13_bonus_super_and_semi_structured.sql).
15. Use [sql/99_cleanup.sql](/Users/shashankmishra/Desktop/AWS_Services_Mastery_Bootcamp/Class-8/redshift_practical_masterclass/sql/99_cleanup.sql) only if you want to remove the created objects.