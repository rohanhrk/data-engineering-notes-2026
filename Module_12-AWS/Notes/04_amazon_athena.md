# Amazon Athena — Data Engineering Study Notes (0–2 YOE)

> Self-contained notes: fundamentals → implementation → interview preparation.
> Pricing, quotas and engine versions change; confirm in the official docs linked at the end.

**Contents**
1. Introduction
2. Architecture and Working Mechanism
3. Core Concepts and Terminology
4. Data Engineering Use Cases
5. Hands-on Implementation (mini-project)
6. Interview Preparation (10 conceptual + 5 scenario + 3 troubleshooting, all answered)
7. Revision and Quick Reference

---

## 1. Introduction

### What is Amazon Athena?
**Amazon Athena** is a serverless, interactive query service that lets you run standard **SQL directly on data stored in Amazon S3** — no servers, no loading step. You define table metadata (usually in the Glue Data Catalog) that points at S3 locations, then query CSV, JSON, Parquet, ORC, Avro and other formats. The SQL engine is based on Trino (Presto family) and DDL uses Hive syntax. With the default on-demand model you pay for the amount of data your queries scan.

### Why was it introduced and what problem does it solve?
Analyzing S3 data used to require standing up a Hadoop/Presto cluster or loading data into a warehouse first. Athena removes cluster management and lets analysts and engineers query data **where it lives**, within seconds, using SQL they already know.

### Why is it important in Data Engineering?
- Fast way to **explore, validate and debug** data lake files.
- Used for **ELT**: `CTAS` and `INSERT INTO` create curated datasets.
- Backbone of cost-effective ad hoc analytics on a lake; integrates with the Glue Catalog, Lake Formation, QuickSight and BI tools via JDBC/ODBC.

### When should you use it?
- Ad hoc and exploratory SQL on S3 data; infrequent queries.
- Data validation/QA queries on pipeline outputs.
- Lightweight transformations producing Parquet via CTAS.
- Log analysis (CloudTrail, ALB, VPC Flow Logs).

### When should you avoid it?
| Situation | Better option |
|---|---|
| Hundreds of concurrent dashboard users with strict low-latency SLAs | Redshift (provisioned/Serverless) or caching layer |
| Heavy repeated joins on huge tables where predictable performance matters | Redshift, EMR/Spark |
| Row-level OLTP workloads | Databases (RDS/DynamoDB) |
| Complex multi-step ETL with custom code | Glue/EMR (though Athena Spark exists) |
| Querying millions of tiny CSV/JSON files unprepared | Convert to Parquet first |

### Simple real-world example
After a Glue job writes Parquet to S3, an analyst runs
`SELECT region, SUM(amount) FROM sales WHERE order_date = DATE '2026-11-18' GROUP BY region;`
in Athena. Because the table is partitioned and columnar, Athena scans a few MB and returns in seconds.

### Brief comparison with alternatives
| | Athena | Redshift | EMR (Presto/Spark) | BigQuery (GCP) |
|---|---|---|---|---|
| Infrastructure | Serverless | Cluster or Serverless | Managed clusters | Serverless |
| Data location | S3 (external) | Warehouse storage + Spectrum | S3/HDFS | Native storage |
| Billing | Per TB scanned (or provisioned capacity) | Per node-hour / RPU-hour | Per instance | Per TB / slots |
| Best for | Ad hoc, lake queries | Repeated BI workloads, complex joins | Custom big data jobs | Equivalent to Athena+warehouse |

---

## 2. Architecture and Working Mechanism

### Overall architecture
Athena separates **metadata**, **compute** and **storage**. Metadata comes from the Glue Data Catalog (or a Hive metastore/external catalog), compute is a pool of Athena-managed workers that run distributed SQL, and storage is S3. Results are written to an S3 **query result location**.

### Major components
- **Query engine** — distributed SQL (Trino-based) executing DML; Hive-style DDL.
- **Data Catalog** — databases/tables/partitions (Glue by default).
- **Workgroups** — isolate users/teams, set result locations, cost controls and engine versions.
- **Data sources** — S3 primarily; **federated query** via Lambda connectors to RDS, DynamoDB, Redshift, etc.
- **Result location** — S3 prefix storing CSV results and metadata.
- **Athena for Apache Spark** — notebook sessions running Spark code (separate capability).
- **Capacity reservations/provisioned capacity** — optional dedicated DPUs instead of per-TB pricing.

### End-to-end flow of a query
1. User/app submits SQL (console, JDBC, SDK `StartQueryExecution`).
2. Athena parses the query, looks up table metadata/partitions in the Glue Catalog.
3. The planner prunes partitions using `WHERE` filters on partition columns.
4. Worker nodes read only the required S3 objects (for Parquet/ORC only needed columns/row groups), process data in parallel, and join/aggregate.
5. Results are written to the S3 result location and returned; `GetQueryResults` reads them.
6. Billing is based on bytes scanned (rounded up; a minimum per query applies) — DDL statements are free and failed queries are not charged for scanned data.

### Mermaid architecture
```mermaid
flowchart LR
    U["Analyst / BI tool / Boto3"] --> ATH["Athena engine (serverless)"]
    ATH --> CAT[("Glue Data Catalog")]
    ATH --> S3D[("S3 data lake Parquet/ORC/CSV")]
    ATH --> FQ["Federated connectors (Lambda)"]
    FQ --> RDS[("RDS / DynamoDB / Redshift")]
    ATH --> RES[("S3 query results")]
    WG["Workgroup: limits, tags, result location"] -. governs .-> ATH
    LF["Lake Formation / IAM"] -. permissions .-> ATH
```

### Explanation of components
- **Athena engine** runs distributed SQL; no clusters visible to you.
- **Catalog** defines schema and partitions; Athena does not store data.
- **S3 data lake** is the actual storage; format and layout drive performance/cost.
- **Federated connectors** let a query join S3 data with operational stores.
- **Results bucket** keeps every query's output; manage its lifecycle.
- **Workgroup** enforces settings and limits; **IAM/Lake Formation** control access.

### Practical Data Engineering architecture
```mermaid
flowchart LR
    SRC["Sources"] --> RAW[("S3 raw")]
    RAW --> GL["Glue ETL"]
    GL --> CUR[("S3 curated Parquet + Catalog")]
    CUR --> ATH["Athena: ad hoc + CTAS aggregates"]
    ATH --> AGG[("S3 aggregates")]
    ATH --> QS["QuickSight"]
    SFN["Step Functions / EventBridge schedule"] --> ATH
```

---

## 3. Core Concepts and Important Terminologies

### 3.1 Serverless SQL and the pricing model
- **Definition:** Athena executes SQL without infrastructure; you pay per query based on **data scanned** (on-demand) — historically about $5 per TB scanned with a small minimum per query; DDL and failed queries are free of scan charges. Check the pricing page for current figures. **Provisioned capacity** is an alternative for predictable, high-volume workloads.
- **Why it matters:** Optimising scan volume directly optimises cost.
- **Mistakes:** Believing `LIMIT 10` reduces cost (usually not; the scan can still be large unless the format/partition allows early termination); querying large CSV/JSON repeatedly instead of Parquet.

### 3.2 Glue Data Catalog integration and external tables
- **Definition:** An **external table** stores only metadata; data stays in S3. `DROP TABLE` removes the definition, not the files.
- **How:** DDL such as `CREATE EXTERNAL TABLE ... LOCATION 's3://bucket/prefix/'` registers the table in the catalog.
- **Example:**
```sql
CREATE DATABASE IF NOT EXISTS retail_athena;

CREATE EXTERNAL TABLE retail_athena.orders_parquet (
  order_id    string,
  customer_id bigint,
  amount      double
)
PARTITIONED BY (order_date string)
STORED AS PARQUET
LOCATION 's3://my-lake/curated/orders/';
```
- **Mistakes:** Pointing `LOCATION` at a file instead of a prefix; schema mismatch with the files; forgetting to register partitions.

### 3.3 Supported formats, SerDes and compression
| Format | Type | Notes |
|---|---|---|
| CSV/TSV | Text | Use OpenCSVSerDe (quotes) or LazySimpleSerDe; all strings with OpenCSV; header via `skip.header.line.count` |
| JSON | Text | JSON SerDe (OpenX or Hive); nested data via `struct`/`array`/`map` |
| Parquet | Columnar | Best for analytics; snappy default, ZSTD supported |
| ORC | Columnar | Good alternative, Hive ecosystems |
| Avro | Row | Schema evolution friendly |
| Iceberg/Hudi/Delta | Table formats | Iceberg has the richest Athena support (DML, time travel) |
Prefer **Parquet/ORC** with compression for cost/performance.

### 3.4 Partitioning and partition management
- **Definition:** Splitting data into folders by column values (`order_date=2026-11-18/`) and declaring them as partition columns.
- **Why:** Athena skips folders that don't match `WHERE` filters (partition pruning), reducing bytes scanned.
- **Ways to register partitions:**
  1. `MSCK REPAIR TABLE t;` — scans S3 for Hive-style folders (can be slow on many partitions).
  2. `ALTER TABLE t ADD IF NOT EXISTS PARTITION (order_date='2026-11-18') LOCATION 's3://...';`
  3. **Glue crawler** or Glue API (`batch_create_partition`).
  4. **Partition projection** — Athena computes partition values and locations from table properties (no catalog partition lookup):
```sql
CREATE EXTERNAL TABLE events (
  event_id string, user_id string, payload string)
PARTITIONED BY (dt string)
STORED AS PARQUET
LOCATION 's3://my-lake/curated/events/'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.dt.type'='date',
  'projection.dt.format'='yyyy-MM-dd',
  'projection.dt.range'='2026-01-01,NOW',
  'storage.location.template'='s3://my-lake/curated/events/dt=${dt}/'
);
```
- **Mistakes:** Filtering with functions on the partition column (e.g. `date(order_date)`), which can prevent pruning; too many tiny partitions; data folder names not matching the projection template.

### 3.5 CTAS, INSERT INTO and views
- **CTAS (`CREATE TABLE AS SELECT`):** creates a new table and writes data in a chosen format/partitioning — the core Athena ELT tool.
```sql
CREATE TABLE retail_athena.daily_revenue
WITH (
  format = 'PARQUET',
  write_compression = 'SNAPPY',
  external_location = 's3://my-lake/aggregates/daily_revenue/',
  partitioned_by = ARRAY['order_date']
) AS
SELECT customer_id, SUM(amount) AS revenue, order_date
FROM retail_athena.orders_parquet
GROUP BY customer_id, order_date;
```
Partition columns must be the **last** columns in the `SELECT`.
- **INSERT INTO:** appends new rows to an existing table (writes new files).
- **Limits:** a single CTAS/INSERT can write at most **100 partitions** (`HIVE_TOO_MANY_OPEN_PARTITIONS`); split by date ranges or use bucketing. Check the docs for the current limit.
- **Views:** stored queries (no data); good for stable business logic and column-level exposure.
```sql
CREATE OR REPLACE VIEW retail_athena.v_big_orders AS
SELECT * FROM retail_athena.orders_parquet WHERE amount > 400;
```

### 3.6 Bucketing
Clustering data by hash of a column into a fixed number of files (`bucketed_by`, `bucket_count` in CTAS) to speed filters/joins on high-cardinality columns. Use sparingly; partition first.

### 3.7 Query optimisation techniques
- Select only needed columns (never `SELECT *` on wide tables).
- Filter on partition columns; store common filter columns sorted.
- Use Parquet/ORC; target ~128 MB+ files; avoid small files.
- Put the **larger table on the left** of a join and the smaller on the right (Trino broadcasts the right side).
- Use `approx_distinct()` for large distinct counts when exactness isn't required.
- Avoid `ORDER BY` on huge results without `LIMIT`; avoid multiple `regexp_like` on big text if possible; use `UNLOAD` to export results efficiently.
- Check `EXPLAIN` and the query stats (`DataScannedInBytes`, `EngineExecutionTimeInMillis`).

### 3.8 Workgroups and cost control
- **Definition:** Logical grouping of queries with settings: result location, encryption, **per-query data scanned limit**, **workgroup data usage controls** with alarms, CloudWatch metrics, tags for cost allocation, engine version.
- **Why:** Separate teams (analysts vs ETL), prevent runaway scans, allocate cost.
- **Config:** `EnforceWorkGroupConfiguration=true` forces the workgroup's result location/encryption on all queries.

### 3.9 Iceberg tables in Athena
Athena can create and query **Apache Iceberg** tables, supporting `INSERT`, `UPDATE`, `DELETE`, `MERGE`, time travel and schema evolution, plus maintenance commands (`OPTIMIZE`, `VACUUM`).
```sql
CREATE TABLE retail_athena.orders_iceberg (
  order_id string, customer_id bigint, amount double, order_date date)
PARTITIONED BY (order_date)
LOCATION 's3://my-lake/iceberg/orders/'
TBLPROPERTIES ('table_type'='ICEBERG');
```
Use for GDPR deletes, CDC merges and slowly changing data.

### 3.10 Federated queries and Athena for Apache Spark
- **Federated query** uses Lambda-based data source connectors so one SQL statement can join S3 data with RDS, DynamoDB, etc. Good for small lookups, not for heavy joins.
- **Athena for Apache Spark** provides notebook sessions for PySpark analysis without managing clusters.

### 3.11 Query results, reuse and security
- Results stored as CSV in S3; set a lifecycle rule to expire old results.
- **Query result reuse** can return cached results for identical queries within a time window.
- Security: IAM (Athena + Glue + S3 + KMS permissions), Lake Formation, encryption of results (SSE-S3/KMS), workgroup enforcement, optional VPC endpoints.

### 3.12 Run Athena from Python (Boto3)
```python
import time, boto3
athena = boto3.client("athena", region_name="ap-south-1")

def run(sql, workgroup, database):
    qid = athena.start_query_execution(
        QueryString=sql, WorkGroup=workgroup,
        QueryExecutionContext={"Database": database})["QueryExecutionId"]
    while True:
        q = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]
        state = q["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        raise RuntimeError(q["Status"].get("StateChangeReason", state))
    scanned = q["Statistics"]["DataScannedInBytes"]
    rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
    return rows, scanned
```

---

## 4. Data Engineering Use Cases

### Real-world use cases
- **Data lake exploration and validation** after each pipeline run.
- **Log analytics** (ALB/CloudTrail/VPC flow logs) with partition projection.
- **Lightweight ELT** — CTAS to create aggregates and Parquet conversions.
- **Self-service BI** via QuickSight/JDBC.
- **Data quality checks** with SQL assertions on S3 tables.

### Batch processing
EventBridge/Step Functions run Athena queries (`startQueryExecution.sync` integration) to build daily aggregates from curated Parquet into new partitions; downstream tools read the aggregates. Backfills are re-runs for specific dates.

### Real-time pipelines
Athena is not a streaming engine. It queries **near-real-time** data once Firehose/Glue streaming writes files to S3 (latency = buffering interval). Use partition projection so new time partitions are queryable immediately.

### Pipeline example 1 — Daily aggregate build
```mermaid
flowchart LR
    EB["EventBridge 03:00"] --> SF["Step Functions"]
    SF --> Q1["Athena: INSERT INTO daily_revenue for yesterday"]
    Q1 --> Q2["Athena: row-count assertion"]
    Q2 -- pass --> QS["QuickSight refresh"]
    Q2 -- fail --> SNS["SNS alert"]
```

### Pipeline example 2 — Log analytics
```mermaid
flowchart LR
    ALB["ALB / CloudTrail logs"] --> S3L[("S3 log bucket")]
    S3L --> T["Athena table with partition projection"]
    T --> Q["Ad hoc security / error analysis"]
    T --> CTAS["CTAS -> Parquet daily summaries"]
```

### Why a Data Engineer chooses Athena
Zero infrastructure, pay-per-query, direct S3 access, instant start and easy CTAS-based ELT. Choose Redshift for heavy concurrent BI, Glue/EMR for complex transformations, and keep Athena for exploration, validation, and moderate analytical queries.

---

## 5. Hands-on Implementation

### Mini-project: Compare CSV vs Parquet scan cost and build a daily revenue aggregate

**1. Objective:** Create Athena tables over raw CSV and curated Parquet (with partition projection), measure bytes scanned, and publish a partitioned aggregate with CTAS.

**2. Business problem:** Analysts need daily revenue by customer. Querying raw CSV is expensive and slow; you must prove the savings and publish a reusable aggregate.

**3. Architecture**
```mermaid
flowchart LR
    RAW[("s3://bucket/raw/orders/ CSV")] --> TCSV["Athena table orders_csv"]
    CUR[("s3://bucket/curated/orders/ Parquet")] --> TPQ["Athena table orders_parquet (projection)"]
    TPQ --> CTAS["CTAS daily_revenue"]
    CTAS --> AGG[("s3://bucket/aggregates/daily_revenue/")]
    WG["Workgroup retail-wg + scan limit"] -.-> TCSV
    WG -.-> TPQ
```

**4. Prerequisites and setup**
- The S3 bucket and sample data from the S3 notes (`raw/orders/ingest_date=.../orders.csv` and `curated/orders/order_date=.../part-0000.parquet`).
- An identity allowed to use Athena, read the Glue catalog and S3, and write to the result/aggregate prefixes.
- `BUCKET` and `REGION` shell variables. Athena charges per data scanned — this data is tiny, so cost is negligible.

**5–6. Implementation and code**

*Step 1 — Workgroup with result location and scan guardrail*
```bash
aws athena create-work-group --name retail-wg \
  --configuration "ResultConfiguration={OutputLocation=s3://$BUCKET/athena-results/},EnforceWorkGroupConfiguration=true,BytesScannedCutoffPerQuery=1073741824,PublishCloudWatchMetricsEnabled=true"
```

*Step 2 — Create the database and tables (run each statement via console or the Python helper in 3.12)*
```sql
CREATE DATABASE IF NOT EXISTS retail_athena;

-- RAW CSV (header row, partitioned by ingest_date folder)
CREATE EXTERNAL TABLE retail_athena.orders_csv (
  order_id string, customer_id string, amount string, order_date string
)
PARTITIONED BY (ingest_date string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
LOCATION 's3://<BUCKET>/raw/orders/'
TBLPROPERTIES ('skip.header.line.count'='1');

MSCK REPAIR TABLE retail_athena.orders_csv;

-- CURATED Parquet with partition projection (no crawler needed)
CREATE EXTERNAL TABLE retail_athena.orders_parquet (
  order_id string, customer_id bigint, amount double
)
PARTITIONED BY (order_date string)
STORED AS PARQUET
LOCATION 's3://<BUCKET>/curated/orders/'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.order_date.type'='date',
  'projection.order_date.format'='yyyy-MM-dd',
  'projection.order_date.range'='2026-11-01,NOW',
  'storage.location.template'='s3://<BUCKET>/curated/orders/order_date=${order_date}/'
);
```
Replace `<BUCKET>` with your bucket name.

*Step 3 — Run comparison queries and capture scan size (`compare_scan.py`)*
```python
import sys, time, boto3
athena = boto3.client("athena")
WG, DB = "retail-wg", "retail_athena"

def run(sql):
    qid = athena.start_query_execution(
        QueryString=sql, WorkGroup=WG,
        QueryExecutionContext={"Database": DB})["QueryExecutionId"]
    while True:
        q = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]
        if q["Status"]["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if q["Status"]["State"] != "SUCCEEDED":
        raise RuntimeError(q["Status"].get("StateChangeReason"))
    return q["Statistics"]["DataScannedInBytes"], qid

csv_sql = """SELECT order_date, SUM(CAST(amount AS double)) rev
             FROM orders_csv WHERE order_date = '2026-11-16' GROUP BY order_date"""
pq_sql  = """SELECT order_date, SUM(amount) rev
             FROM orders_parquet WHERE order_date = '2026-11-16' GROUP BY order_date"""

for name, sql in [("CSV", csv_sql), ("Parquet", pq_sql)]:
    scanned, qid = run(sql)
    print(f"{name:8} scanned {scanned:>8} bytes  (query {qid})")
```

*Step 4 — Publish an aggregate with CTAS*
```sql
CREATE TABLE retail_athena.daily_revenue
WITH (
  format = 'PARQUET',
  write_compression = 'SNAPPY',
  external_location = 's3://<BUCKET>/aggregates/daily_revenue/',
  partitioned_by = ARRAY['order_date']
) AS
SELECT customer_id, ROUND(SUM(amount), 2) AS revenue, COUNT(*) AS orders, order_date
FROM retail_athena.orders_parquet
GROUP BY customer_id, order_date;
```
Note: `external_location` must be an **empty** S3 prefix. To append later days use `INSERT INTO retail_athena.daily_revenue SELECT ... WHERE order_date = DATE_FORMAT(...)`.

**7. Explanation of the code**
- The workgroup enforces a result location and caps each query at 1 GB scanned.
- The CSV table uses OpenCSVSerDe (all columns are strings, hence the cast); `MSCK REPAIR` registers `ingest_date` partitions.
- The Parquet table uses **partition projection**, so no crawler or `MSCK` is required. The `WHERE order_date = ...` filter prunes to one folder.
- The script prints `DataScannedInBytes` for each query so you can quantify savings.
- CTAS writes partitioned Parquet aggregates (partition column last in the `SELECT`).

**8. Expected output** (numbers vary with your data)
```
CSV      scanned     5600 bytes  (query abc...)
Parquet  scanned     1900 bytes  (query def...)
```
Parquet should scan less because it reads only the needed columns and one partition. With real datasets the gap is dramatically larger.

**9. Validation and testing**
```sql
SELECT COUNT(*) FROM retail_athena.orders_parquet;     -- equals rows loaded
SELECT * FROM retail_athena.daily_revenue ORDER BY order_date LIMIT 10;
SELECT "$path", COUNT(*) FROM retail_athena.orders_parquet GROUP BY 1;  -- shows source files
```
Compare totals between CSV and Parquet tables, and verify `aws s3 ls s3://$BUCKET/aggregates/daily_revenue/` shows partition folders.

**10. Common errors and troubleshooting**
| Error | Cause | Fix |
|---|---|---|
| `HIVE_BAD_DATA` / zero rows on Parquet | Column type mismatch (e.g. `customer_id` int vs string) or wrong location | Match the Parquet schema (`int64` → `bigint`) |
| `TABLE_NOT_FOUND` | Wrong database in the context | Set `QueryExecutionContext` or qualify names |
| `No output location provided` | Workgroup/result location missing | Use the workgroup or pass `ResultConfiguration` |
| CTAS `HIVE_PATH_ALREADY_EXISTS` | `external_location` not empty | Use a new/empty prefix |
| `AccessDenied` | Missing S3/Glue/KMS permissions | Add permissions for data, results bucket and catalog |
| Query cancelled | Scan limit exceeded | Add partition filters or raise the workgroup limit |

**11. Cost considerations and cleanup**
Queries cost per data scanned (tiny here); S3 result files accumulate — remove them. Clean up:
```sql
DROP TABLE retail_athena.daily_revenue;
DROP TABLE retail_athena.orders_parquet;
DROP TABLE retail_athena.orders_csv;
DROP DATABASE retail_athena;
```
```bash
aws s3 rm s3://$BUCKET/aggregates/ --recursive
aws s3 rm s3://$BUCKET/athena-results/ --recursive
aws athena delete-work-group --work-group retail-wg --recursive-delete-option
```
(Dropping a CTAS-created *external-location* table does not delete its S3 data, hence the explicit `s3 rm`.)

---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is Amazon Athena and how does it work?**
Athena is a serverless SQL query service for data in S3. Table definitions live in the Glue Data Catalog (metadata only). When you submit a query, Athena looks up the table and partitions, prunes partitions using your filters, reads the necessary S3 objects in parallel on managed workers (reading only required columns for Parquet/ORC), computes the result and writes it to an S3 result location. You never manage servers. The SQL engine is Trino-based, DDL uses Hive syntax. *Keywords: serverless, schema-on-read, external table, Glue Catalog, query result location, pay per data scanned.*

**Q2. How is Athena priced and how do you reduce cost?**
On-demand pricing charges per amount of data scanned (rounded up, with a per-query minimum); DDL and failed queries incur no scan charge; alternatively, **provisioned capacity** bills for dedicated DPUs. To reduce cost: store data as compressed **Parquet/ORC**, **partition** by common filter columns, select only needed columns, avoid many tiny files, use `CTAS` to precompute aggregates, enforce **workgroup scan limits**, and reuse query results. Remember `LIMIT` does not generally reduce scanned bytes. Track cost with workgroup tags and CloudWatch metrics.

**Q3. What is an external table and what happens when you drop it?**
An external table is just metadata describing how to interpret files at an S3 `LOCATION`. Athena applies the schema when reading (schema-on-read). Dropping it deletes only the catalog entry; the S3 files remain. This is also true for tables created by CTAS with `external_location` — you must delete the data in S3 yourself. This design lets multiple engines (Athena, Glue, EMR, Redshift Spectrum) share the same data and catalog.

**Q4. Explain partitioning in Athena and the different ways to add partitions.**
Partitioning stores data in folders by column values (e.g. `order_date=2026-11-18/`) and declares those columns as `PARTITIONED BY`. Athena only reads folders matching the `WHERE` filter (partition pruning). Ways to register partitions: `MSCK REPAIR TABLE` (discovers Hive-style folders, slow on huge numbers), `ALTER TABLE ADD PARTITION`, Glue crawlers/API, and **partition projection** (table properties tell Athena how to compute partition values/locations, so no catalog lookups and no maintenance — ideal for time-based partitions). Avoid over-partitioning, which creates too many small files.

**Q5. Why are Parquet/ORC better than CSV/JSON in Athena?**
Columnar formats store each column separately with compression and statistics, so Athena reads only the referenced columns and can skip row groups using min/max values; they also embed schema/types. CSV/JSON are row-oriented text: every query reads all bytes of the files, requires parsing, and types are not enforced. Typical savings are 90%+ in bytes scanned and large runtime reductions. Use snappy/zstd compression and target ~128 MB or larger files; convert with Glue or Athena CTAS.

**Q6. Compare CTAS, INSERT INTO and views.**
**CTAS** creates a new table (and its S3 data) from a query — you choose format, compression, partitioning, bucketing and location; used for conversions and aggregates. **INSERT INTO** appends the results of a query to an existing table (new files; no overwrite) — used for incremental loads. A **view** stores only the query text and always reflects current data, with no storage or scan until used. Limits: a single CTAS/INSERT may write only a limited number of partitions (100 at the time of writing), so batch by date range; partition columns must be last in the `SELECT`; CTAS `external_location` must be empty.

**Q7. What are workgroups and why use them?**
Workgroups isolate queries by team/use case. Each can set a result location and encryption, enforce those settings, cap bytes scanned per query, define data-usage alarms, publish CloudWatch metrics, apply tags for cost allocation and select engine versions. They enable governance — e.g. analysts get a workgroup with a 100 GB per-query limit, ETL gets a larger one — and cost visibility (tag workgroups by department). IAM policies can restrict users to specific workgroups.

**Q8. When would you pick Athena over Redshift or EMR?**
Athena: ad hoc, infrequent, exploratory queries and light ELT on S3; zero infrastructure; cost per scan. Redshift: sustained, concurrent BI workloads, complex joins on warehouse tables, predictable performance, materialised views, workload management. EMR: heavy custom processing with Spark/Hive, ML pipelines, fine control over resources. Many architectures combine them: Glue/EMR for ETL → S3 Parquet → Athena for exploration and Redshift for the curated dimensional model.

**Q9. How does Athena support updates and deletes?**
Plain Hive-style tables on S3 are append-only files — no row-level updates. **Apache Iceberg tables** in Athena support `INSERT`, `UPDATE`, `DELETE` and `MERGE INTO`, time travel (`FOR TIMESTAMP AS OF`/`FOR VERSION AS OF`), schema evolution and maintenance (`OPTIMIZE` for compaction, `VACUUM` to remove old snapshots). Use Iceberg for GDPR deletes, CDC merges and slowly changing data. Note that Iceberg's maintenance operations are needed to keep performance and storage in check.

**Q10. List key Athena query optimisation best practices.**
Select only needed columns; filter on partition columns (don't wrap them in functions); use columnar formats and compression; keep files reasonably large; place the larger table on the left of joins; use `approx_distinct`; avoid unbounded `ORDER BY`; precompute aggregates with CTAS; use `UNLOAD` to write large result sets in Parquet rather than downloading CSV; examine `EXPLAIN` and query statistics; use partition projection for many partitions; use bucketing for high-cardinality joins/filters; consider query result reuse for repeated dashboards.

### B. Scenario-Based Questions (5)

**S1. Athena costs $4,000/month; analysts mostly query last-30-day logs stored as gzip JSON.**
*Problem:* full scans of row-oriented text. *Solution:* convert logs to partitioned Parquet (Glue or CTAS), partition by `dt` (and maybe `service`), enable partition projection, add lifecycle for old raw logs, enforce workgroup scan limits, educate analysts to filter by `dt` and select columns. *Why:* partition pruning + columnar reads cut bytes scanned by an order of magnitude. *Alternatives:* provisioned capacity if usage is heavy and constant; Redshift for heavy repeated dashboards. *Trade-off:* ETL step and storage of two copies (raw + curated).

**S2. Build a daily revenue aggregate automatically.**
*Solution:* EventBridge Scheduler triggers Step Functions; a task runs `INSERT INTO daily_revenue SELECT ... WHERE order_date = DATE '{{yesterday}}'` via the Athena `startQueryExecution.sync` integration, a second task verifies row counts/quality, failures notify SNS. Make it idempotent by writing to a date-specific location or deleting the partition before reinsertion (with Iceberg use `MERGE`). *Why:* serverless, cheap, simple SQL. *Alternatives:* Glue job, dbt-athena. *Trade-off:* Hive-style INSERT can duplicate on retries unless you control partition overwrites.

**S3. A team of 30 analysts shares one account; costs and runaway queries must be controlled.**
*Solution:* create per-team workgroups with enforced result locations, per-query scan cutoff and daily data-usage alarms, tag workgroups for chargeback, restrict IAM so each team uses only its workgroup, apply Lake Formation permissions for data access, expire result files via S3 lifecycle. *Why:* guardrails and visibility without blocking work. *Alternatives:* provisioned capacity per team. *Trade-off:* hard limits can cancel legitimate queries; need an exception process.

**S4. Nested JSON clickstream data is slow and awkward to query.**
*Solution:* use CTAS (or Glue) to flatten and convert to Parquet; use `UNNEST` for arrays and dot notation for structs; define explicit struct types in DDL; partition by date; keep raw JSON as the source of truth. Example:
```sql
SELECT e.user_id, item.sku, item.qty
FROM events_json e CROSS JOIN UNNEST(e.items) AS t(item);
```
*Why:* columnar flattened data is cheaper and simpler. *Alternatives:* Iceberg with nested types; keep as `json` strings and parse with `json_extract` (more CPU). *Trade-off:* flattening may duplicate data and requires schema management.

**S5. Legal requires deleting a customer's records across a lake of Parquet tables queried by Athena.**
*Solution:* migrate the relevant tables to **Iceberg** and run `DELETE FROM t WHERE customer_id = ...`; then run `VACUUM`/snapshot expiry so removed files physically disappear; log the deletion. For legacy Hive tables you'd have to rewrite affected partitions with CTAS/Glue. *Why:* Iceberg supports row-level deletes with snapshot isolation. *Alternatives:* Delta/Hudi with Glue/EMR; redesign data to isolate PII. *Trade-off:* maintenance overhead and table-format migration effort.

### C. Troubleshooting Questions (3)

**T1. Query returns zero rows (or fewer rows than expected) on a partitioned table after new data arrives.**
*Root causes:* new partitions not registered in the catalog; partition folders not Hive-style (`key=value`); wrong `LOCATION`; partition projection template/range excludes the data; case/format mismatch in partition values (e.g. `2026-1-5`). *Debug:* `SHOW PARTITIONS table`; `aws s3 ls` the prefix; run `SELECT "$path" ...` to see which files are read; check table properties with `SHOW CREATE TABLE`. *Fix:* run `MSCK REPAIR TABLE`, add partitions via `ALTER TABLE ADD PARTITION`/Glue crawler, correct projection properties, or fix folder naming.

**T2. `HIVE_TOO_MANY_OPEN_PARTITIONS` (or 100-partition limit) during CTAS/INSERT INTO.**
*Root cause:* a single statement writes more partitions than the supported maximum. *Debug:* count distinct partition values in the source query. *Fix:* split the load into batches that each write ≤100 partitions (e.g. one CTAS for the first slice then `INSERT INTO` for subsequent date ranges), reduce partition granularity (month instead of day), or use bucketing/Glue Spark for larger conversions.
```sql
CREATE TABLE t WITH (format='PARQUET', partitioned_by=ARRAY['dt'],
  external_location='s3://b/t/') AS
SELECT ..., dt FROM src WHERE dt BETWEEN DATE '2026-01-01' AND DATE '2026-03-31';
INSERT INTO t SELECT ..., dt FROM src WHERE dt BETWEEN DATE '2026-04-01' AND DATE '2026-06-30';
```

**T3. `Query exhausted resources at this scale factor` or a query is cancelled/times out.**
*Root causes:* huge `ORDER BY`, `DISTINCT`, window functions or joins with a large right-hand table; skewed keys; too many small files; regex over large text; very wide results. *Debug:* review `EXPLAIN` and stage stats; check scanned bytes and workgroup limits; try on a smaller date range. *Fix:* filter early and reduce columns, put the smaller table on the right side, replace exact distinct with `approx_distinct`, pre-aggregate with CTAS, compact files, add `LIMIT` with `ORDER BY`, use Iceberg/bucketing, or move the workload to Spark/Redshift. If it is a service limit (e.g. timeouts) request an increase or split the query.

---

## 7. Revision and Quick Reference

### Key takeaways
- Athena = serverless SQL on S3; pay per data scanned.
- Cost/performance = format (Parquet) + partitioning + column selection.
- Catalog stores metadata only; dropping an external table keeps S3 data.
- CTAS is the ELT workhorse; Iceberg enables row-level changes.
- Workgroups control cost and governance.

### Commonly forgotten details
- `LIMIT` doesn't necessarily reduce scan cost.
- Partition columns must be last in CTAS `SELECT`.
- CTAS `external_location` must be empty; CTAS/INSERT is limited to a number of partitions per statement.
- Every query writes results to S3 — manage that bucket.
- Functions on partition columns can disable pruning.
- Parquet column types must match DDL.
- Athena DML queries have a runtime limit (check the quota).
- OpenCSVSerDe reads every column as string.

### Important commands and syntax
```sql
SHOW PARTITIONS t;          MSCK REPAIR TABLE t;
ALTER TABLE t ADD IF NOT EXISTS PARTITION (dt='2026-11-18') LOCATION 's3://b/t/dt=2026-11-18/';
SHOW CREATE TABLE t;        DESCRIBE t;        EXPLAIN SELECT ...;
UNLOAD (SELECT ...) TO 's3://b/out/' WITH (format='PARQUET');
SELECT "$path", "$file_size" FROM t LIMIT 5;
```
```bash
aws athena start-query-execution --query-string "SELECT 1" --work-group wg
aws athena get-query-execution --query-execution-id <id>
aws athena get-query-results --query-execution-id <id>
```

### Frequently used configurations
Workgroup: result location + `EnforceWorkGroupConfiguration`, `BytesScannedCutoffPerQuery`, CloudWatch metrics, tags. Table properties: `projection.*`, `skip.header.line.count`, `parquet.compression`, `table_type='ICEBERG'`.

### Common errors and solutions
| Error | Solution |
|---|---|
| `HIVE_PARTITION_SCHEMA_MISMATCH` | Align partition/table schema; recreate partitions |
| `HIVE_BAD_DATA` / `HIVE_CURSOR_ERROR` | Fix type mismatch or corrupt files |
| `HIVE_TOO_MANY_OPEN_PARTITIONS` | Batch partitions |
| `TABLE_NOT_FOUND` | Wrong DB/Region/workgroup catalog |
| `AccessDenied` | Check IAM, Lake Formation, KMS, S3 result location |
| `SlowDown` (S3) | Reduce request rate; compact files |

### Service limitations
Not for low-latency high-concurrency serving; query runtime/quota limits; DDL query limits; limited partitions per write statement; result sets via API are paginated; performance depends on layout; federated queries add Lambda limits.

### Performance and cost optimisation
Parquet/ORC; partitions + projection; larger files; column selection; precomputed aggregates; workgroup limits; result reuse; lifecycle on result bucket; compare `DataScannedInBytes` while tuning.

### Security best practices
Least-privilege IAM per workgroup; Lake Formation for table/column/row control; encrypt results (SSE-S3/KMS) and enforce via workgroup; private access via VPC endpoints; log with CloudTrail; expire result files; avoid sensitive data in query strings.

### Connections with other AWS services
S3 (data and results), Glue (catalog, ETL), Lake Formation (governance), QuickSight (BI), Step Functions/EventBridge (orchestration), Lambda (federated connectors), CloudWatch (metrics), KMS (encryption), Redshift Spectrum (shared catalog).

### Quick revision cheat sheet
```
S3 data + Glue Catalog metadata -> Athena SQL -> S3 results
Cost: bytes scanned  -> Parquet + partitions + select columns
Partitions: MSCK | ADD PARTITION | crawler | PROJECTION
CTAS: format, partitioned_by (last cols), external_location (empty)
Iceberg: MERGE/UPDATE/DELETE, time travel, OPTIMIZE/VACUUM
Workgroup: result loc, scan cutoff, tags
```

### 10 rapid-fire revision questions
1. **What does Athena charge for (on-demand)?** Data scanned per query.
2. **Does dropping an external table delete S3 data?** No.
3. **Best file format for Athena?** Parquet (or ORC) with compression.
4. **How to avoid maintaining partitions manually?** Partition projection.
5. **Which statements are free?** DDL (and failed queries incur no scan charge).
6. **Where must partition columns appear in CTAS?** Last in the `SELECT`.
7. **What does a workgroup's scan cutoff do?** Cancels queries exceeding the limit.
8. **Which table format supports MERGE/DELETE in Athena?** Apache Iceberg.
9. **Where are query results stored?** In the S3 result location.
10. **Does `LIMIT` reduce bytes scanned?** Generally no.

---

## Official AWS documentation
- Amazon Athena User Guide — https://docs.aws.amazon.com/athena/latest/ug/what-is.html
- Performance tuning — https://docs.aws.amazon.com/athena/latest/ug/performance-tuning.html
- Partitioning data — https://docs.aws.amazon.com/athena/latest/ug/partitions.html
- Partition projection — https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html
- CTAS — https://docs.aws.amazon.com/athena/latest/ug/ctas.html
- Workgroups — https://docs.aws.amazon.com/athena/latest/ug/workgroups-manage-queries-control-costs.html
- Iceberg tables in Athena — https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html
- Service quotas — https://docs.aws.amazon.com/athena/latest/ug/service-limits.html
- Athena pricing — https://aws.amazon.com/athena/pricing/
- Boto3 Athena reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/athena.html
