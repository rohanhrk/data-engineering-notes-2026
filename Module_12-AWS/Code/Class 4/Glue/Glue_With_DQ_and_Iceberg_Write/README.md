# AWS Glue Data Quality to Apache Iceberg demo

This example reads crawler-cataloged CSV orders, evaluates row-level AWS Glue
Data Quality rules, publishes the native results, transforms only passing rows,
and writes them to an Apache Iceberg v2 table registered in the AWS Glue Data
Catalog.

The included CSV has 1,200 rows and 25 source columns. A small, intentional set
of bad values (a duplicate key, missing values, invalid categories, zero or
negative amounts, and an invalid timestamp) makes failures visible during a
classroom demonstration.

## Files

- `data/customer_orders.csv` - crawler-ready input data.
- `generate_sample_orders.py` - deterministic generator for that CSV.
- `data_quality_ruleset.dqdl` - readable copy of the DQDL used by the job.
- `glue_data_quality_to_iceberg.py` - Glue ETL job script.

The DQDL is embedded in the Glue job because a deployed job cannot read this
local file. Keep the standalone copy synchronized if rules are changed.

## 1. Create S3 prefixes

Use one bucket or separate buckets. These example names are placeholders:

```text
s3://YOUR-BUCKET/glue-dq-demo/source/orders/
s3://YOUR-BUCKET/glue-dq-demo/data-quality-results/
s3://YOUR-BUCKET/glue-dq-demo/iceberg-warehouse/
s3://YOUR-BUCKET/glue-dq-demo/scripts/
```

Upload `data/customer_orders.csv` to the source prefix and
`glue_data_quality_to_iceberg.py` to the scripts prefix.

Do not point the source crawler at the parent `glue-dq-demo/` prefix. Doing so
can mix CSV input, DQ output, and Iceberg metadata into the same crawler scope.

## 2. Create and run the source crawler

Create a Glue database such as `retail_raw`, then create a crawler with:

- Data source: `s3://YOUR-BUCKET/glue-dq-demo/source/orders/`
- Target database: `retail_raw`
- Table name: use the table the crawler creates, for example `orders`
- Header handling: the built-in CSV classifier should use the first line as
  headers; confirm the resulting columns before running the job.

Run the crawler once. The ETL job reads this Catalog table rather than reading
the S3 object directly.

## 3. Create the Glue Spark job

Use AWS Glue 4.0 or later. Glue 5.0 is a good default. Set the script location
to the uploaded Python file and add these job parameters:

| Key | Example value |
| --- | --- |
| `--SOURCE_DATABASE` | `retail_raw` |
| `--SOURCE_TABLE` | `orders` |
| `--TARGET_DATABASE` | `retail_curated` |
| `--TARGET_TABLE` | `customer_orders_iceberg` |
| `--ICEBERG_WAREHOUSE` | `s3://YOUR-BUCKET/glue-dq-demo/iceberg-warehouse/` |
| `--DQ_RESULTS_S3_PATH` | `s3://YOUR-BUCKET/glue-dq-demo/data-quality-results/` |
| `--datalake-formats` | `iceberg` |
| `--conf` | `spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions` |

`--JOB_NAME` is supplied by Glue. Keep Iceberg database and table names lower
case.

The script creates the target Catalog database and Iceberg table if they do not
exist. For simplicity, `createOrReplace()` replaces the target table contents on
later runs. Use append or merge logic for an incremental production pipeline.

## 4. IAM permissions

The Glue job role needs, at minimum:

- `s3:GetObject` and `s3:ListBucket` on the source data.
- S3 read/write/delete permissions on the DQ result and Iceberg warehouse
  prefixes. Iceberg commits and maintenance need more than only `PutObject`.
- Glue Data Catalog read access to the source database/table and create/update
  access for the target database/table.
- CloudWatch Logs permissions and CloudWatch metric publishing permissions for
  native Data Quality observability.

The exact IAM policy should be scoped to your bucket, Region, account, and
database rather than copied as a wildcard classroom policy.

## 5. Expected run behavior

The job performs the following flow:

```text
CSV in S3 -> Glue crawler/Catalog table
          -> Glue Data Quality (native result publishing)
          -> reject failed rows -> derive business columns
          -> Iceberg v2 table in S3 + Glue Catalog registration
```

In the Glue job run, inspect CloudWatch logs for sample rejected order IDs and
their failed rules.

In Glue Studio, open the job run's **Data quality** results. The
`resultsS3Prefix` also preserves the native result artifacts in S3, and enabling
CloudWatch metrics makes the evaluation context available for monitoring.

After a successful run, query the curated table in Athena (with an Athena workgroup
and query-result location already configured):

```sql
SELECT
    order_status,
    product_category,
    COUNT(*) AS order_count,
    ROUND(SUM(net_amount), 2) AS revenue
FROM retail_curated.customer_orders_iceberg
GROUP BY order_status, product_category
ORDER BY revenue DESC;
```

Inspect Iceberg metadata through Athena:

```sql
SELECT *
FROM "retail_curated"."customer_orders_iceberg$snapshots"
ORDER BY committed_at DESC;
```

## Optional: publish DQ history as Catalog Iceberg tables

The job already publishes native Glue Data Quality results to the Glue run UI,
S3, and CloudWatch. Newer Glue releases can additionally persist rule,
profiling, and row-level DQ history into Glue Catalog-managed Iceberg tables via
`dataQualityResultsPublishing.resultsFormat.*` options. That feature is kept out
of the default job so this example remains usable on Glue 4.0/5.0 accounts.
