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
