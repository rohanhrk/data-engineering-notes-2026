---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is AWS Glue and what are its main components?**
Glue is a serverless data integration service with: the **Data Catalog** (metadata for databases/tables/partitions), **crawlers** and **classifiers** (schema discovery), **ETL jobs** (Spark, Python shell, streaming, Ray) running on managed workers, **triggers/workflows** (scheduling), **connections** (to JDBC/Kafka sources), **Glue Studio** (visual authoring), and **Glue Data Quality** (DQDL rules). It removes cluster management: you set a worker type and count, and pay for DPU-time. *Keywords: serverless, Spark, Data Catalog, DPU.* Typical story: crawl S3 → catalog → Glue job → Parquet → Athena.

**Q2. What is the Glue Data Catalog and who uses it?**
It is a central, Hive-metastore-compatible metadata repository: databases contain tables, tables describe schema, location, format and partition keys, and partitions map key values to S3 prefixes. It stores metadata, not data. Athena, Redshift Spectrum, EMR, Glue jobs and Lake Formation all read it, which makes a table definition reusable across engines. Deleting a table from the catalog does not delete S3 files. Important features: encryption of metadata, resource policies, partition indexes for tables with many partitions.

**Q3. What do crawlers and classifiers do, and when should you not use a crawler?**
A crawler scans a data store, uses classifiers (built-in or custom) to recognise formats and infer schema, then creates or updates catalog tables and partitions. Configure schedules, include/exclude patterns, schema-change and delete behaviour, and incremental recrawl of new folders. Don't use crawlers when the schema is known and stable (define tables via DDL/IaC), when the prefix contains mixed schemas (you get many odd tables), or for very large datasets where recrawling is slow/costly — use partition projection, `MSCK REPAIR TABLE`, or explicit `batch_create_partition`.

**Q4. What is a DynamicFrame and how does it differ from a Spark DataFrame?**
A DynamicFrame is Glue's self-describing distributed collection: each record carries its own schema, so inconsistent types in a column become a **choice type** (e.g. `int` or `string`) resolved by `ResolveChoice`. It also integrates with the catalog, bookmarks and file grouping. A DataFrame has a single strict schema, offers richer SQL/ML APIs and the Catalyst optimiser. Common practice: read with DynamicFrame (messy inputs), resolve types, convert to DataFrame for joins/aggregations, convert back for Glue sinks if needed. Interviewers like "DynamicFrame = schema flexibility at read time, DataFrame = performance and rich API."

**Q5. Explain Glue worker types, DPUs and how you size a job.**
A DPU is 4 vCPU and 16 GB RAM. Worker types (G.1X = 1 DPU, G.2X = 2 DPU, larger G.4X/G.8X, G.025X for small streaming) differ in CPU/memory per worker. You choose type and number of workers (Spark jobs need at least two); with **auto scaling** the number is a maximum. Sizing approach: start small, watch CloudWatch/Spark UI metrics (executors used, memory, shuffle spill, job runtime), scale **out** for parallel workloads and scale **up** (bigger worker) for memory-heavy tasks such as large joins. Billing is per DPU-second, so right-sizing and the **Flex** class for non-urgent jobs save money.

**Q6. What are job bookmarks and what are their limitations?**
Bookmarks let a job process only new data since the last successful run (for supported sources such as S3 files and some JDBC with a monotonic key). They use `transformation_ctx` identifiers and job state saved on `job.commit()`. Limitations: don't detect updates to existing rows, depend on stable `transformation_ctx`, complicate reprocessing (need `reset-job-bookmark`), and can hide data issues. A robust alternative is parameterised runs (`--run_date`) with idempotent partition overwrites, which makes backfills trivial.

**Q7. How do you reduce the data a Glue job reads? Explain partition pruning and pushdown predicates.**
Store data partitioned by commonly filtered columns and read with `push_down_predicate` (e.g. `"order_date='2026-11-18'"`) from catalog tables so Glue lists and reads only matching partitions. For tables with thousands of partitions, add catalog **partition indexes** to speed partition retrieval. Use columnar formats (Parquet) so Spark prunes columns and uses predicate pushdown inside files. For many small files, use `groupFiles`/`groupSize`. These reduce S3 requests, memory and runtime.

**Q8. Compare Glue workflows/triggers with Step Functions and Airflow (MWAA).**
Glue workflows chain crawlers/jobs with triggers and show run graphs — simple, native, cheap. Step Functions is a general orchestrator for AWS services: retries, branching, parallel maps, waits, error handling, rich visualisation. MWAA (Apache Airflow) suits teams wanting Python DAGs, many integrations and backfills. Choose Glue workflows for small Glue-only pipelines; Step Functions/MWAA for cross-service, conditional, long or auditable pipelines.

**Q9. What is Glue Data Quality?**
A feature to define rule sets in **DQDL** (e.g. `IsComplete "id"`, `ColumnValues "amount" > 0`, `RowCount > 0`) and evaluate them on catalog tables or within ETL jobs. Results give rule-level pass/fail and scores and can publish CloudWatch metrics or stop a job. Use it as a gate before publishing curated data; decide what happens on failure (fail the job, quarantine records, alert) and track trends. It complements, not replaces, unit tests and source-side validation.

**Q10. When would you choose Glue vs EMR vs Lambda?**
Glue: serverless Spark ETL and catalog with minimal ops, good for routine batch. EMR: need control over cluster, libraries, Spark/Hadoop tuning, long-running or interactive clusters, Spot/Graviton optimisation, non-Spark frameworks (Hive, Presto, HBase). Lambda: small, short (≤15 min), event-driven transformations or glue code. Rule of thumb: tiny → Lambda; standard big batch → Glue; custom/huge/cost-optimised steady workloads → EMR. Consider operational skill and cost per run.

### B. Scenario-Based Questions (5)

**S1. A Glue job reading 3 million small JSON files takes 6 hours.**
*Problem:* per-file overhead dominates (listing, opening, task scheduling). *Solution:* use `groupFiles`/`groupSize` to batch small files into 128 MB read tasks; better, fix upstream (Firehose buffering, compaction job) so files are ≥128 MB, and write Parquet. Use partitioned layouts and `push_down_predicate`. *Why:* fewer, larger tasks cut overhead; columnar output speeds downstream. *Alternatives:* Iceberg with compaction, S3 Inventory to avoid listing. *Trade-off:* compaction adds a step but saves ongoing cost.

**S2. You need daily incremental loads without reprocessing the whole history.**
*Options:* (1) job bookmarks on the S3 source; (2) explicit `--run_date` parameter reading only that partition and overwriting the target partition. *Recommendation:* option 2 for deterministic reruns and backfills; use bookmarks only for simple append-only file landing. For database sources use a watermark column (`updated_at`) stored in a control table (DynamoDB/S3) or DMS CDC. *Why:* idempotency and observability beat hidden state. *Trade-off:* you must manage parameters/state yourself.

**S3. The upstream team adds a column and sometimes changes `amount` from int to string; jobs and Athena break.**
*Solution:* land raw data unchanged; in Glue read as DynamicFrame and use `ResolveChoice`/explicit casts to the contract type; configure crawlers with a schema-change policy (add new columns only, log otherwise) or manage schemas explicitly; add Glue Data Quality or schema checks that alert on breaking changes; consider Iceberg for safe schema evolution. *Why:* separate ingestion from strict curated schemas. *Alternatives:* Glue Schema Registry for streaming schemas. *Trade-off:* governance process needed to agree on contracts.

**S4. The monthly Glue bill doubled.**
*Approach:* identify costly jobs in Cost Explorer/CloudWatch (DPU-seconds); check job run insights/Spark UI for skew, spill, long idle executors; right-size worker type/count, enable auto scaling, use Flex for non-urgent jobs, cut data read with partition pruning, avoid reprocessing history, stop crawlers running too often, remove retries that rerun large jobs. *Why:* cost = DPUs × time. *Alternatives:* move steady heavy workloads to EMR on Spot. *Trade-off:* tuning time vs savings.

**S5. A join between a 400 GB fact table and a 50 MB dimension is slow.**
*Solution:* broadcast the small table (`broadcast(dim_df)`) to avoid shuffling the large table; filter early and select needed columns; make sure partitions are pruned; check for skew on join key and enable Spark adaptive query execution (default in recent Glue versions) or salt hot keys. *Why:* a broadcast hash join avoids shuffling 400 GB. *Alternatives:* bucket both tables on the key (preparation cost), pre-join once into a curated table. *Trade-off:* broadcasting too large a table can cause OOM.

### C. Troubleshooting Questions (3)

**T1. Glue job fails with `AccessDeniedException` or "Insufficient Lake Formation permission(s)".**
*Root causes:* role lacks S3 object/list permissions on source/target/script/temp paths; KMS decrypt missing; Glue catalog actions (`glue:GetTable`, `GetPartitions`, `BatchCreatePartition`) missing; Lake Formation controls the table and the role has no grants; cross-account bucket policy missing. *Debug approach:* read the exact error in CloudWatch logs (`/aws-glue/jobs/error`); note whether the service is S3, KMS, Glue or Lake Formation; check the role's policies and the bucket policy; use `aws iam simulate-principal-policy`; for Lake Formation grant `SELECT` and data location access. *Fix:* add the missing permission (prefer least privilege) and rerun.

**T2. Job fails with "Container killed by YARN for exceeding memory limits" or OOM.**
*Root causes:* skewed join/aggregation, huge partitions, `collect()`/`toPandas()` on large data, too many columns, wide shuffles with too few partitions, undersized worker type, UDF memory use. *Debug:* Spark UI (stage with max task time/spill), CloudWatch memory metrics, job run insights. *Fixes:* use a larger worker type (G.2X/G.4X), increase shuffle partitions or repartition, filter/select earlier, broadcast small dimensions, handle skew (salting/AQE), remove driver-side collection, tune `spark.executor.memoryOverhead` via `--conf` where supported, write intermediate results to S3 rather than caching everything.
```python
spark.conf.set("spark.sql.shuffle.partitions", "400")
df = df.repartition(400, "customer_id")
```

**T3. Crawler produced the wrong schema, many unwanted tables or missed partitions.**
*Root causes:* mixed formats/schemas under one prefix, header not detected for CSV, inconsistent column types between files, crawler grouping policy, exclude patterns missing, partitions detected as columns because folder names are not `key=value`, crawler role lacks S3 access. *Debug:* review crawler run logs (`/aws-glue/crawlers`), inspect the created tables (`get-table`), list the S3 layout. *Fix:* restructure S3 into one dataset per prefix with consistent schema, add a custom classifier (CSV with header), use include/exclude patterns, set `TableGroupingPolicy`, or create tables with DDL and add partitions via `MSCK REPAIR TABLE`/API; rerun.

---

## 7. Revision and Quick Reference

### Key takeaways
- Glue = Data Catalog + crawlers + serverless Spark ETL (+ workflows, DQ).
- The catalog holds metadata only; Athena/Redshift Spectrum/EMR reuse it.
- Cost = DPU-hours; right-size, partition, avoid small files.
- Prefer explicit parameters + idempotent partition overwrites over opaque state.

### Commonly forgotten details
- Spark jobs need at least 2 workers; one is the driver.
- `job.commit()` is required for bookmarks.
- Changing `transformation_ctx` loses bookmark state.
- Job role needs access to script, temp dir, data, catalog and logs.
- Jobs in a VPC need routes to S3/Glue endpoints.
- Deleting a catalog table doesn't delete S3 data.
- Crawlers cost money — schedule thoughtfully.

### Important commands and syntax
```bash
aws glue start-job-run --job-name J --arguments '{"--run_date":"2026-11-18"}'
aws glue get-job-run --job-name J --run-id jr_xxx
aws glue get-tables --database-name db
aws glue start-crawler --name C ; aws glue get-crawler --name C
aws glue reset-job-bookmark --job-name J
aws logs tail /aws-glue/jobs/error --follow
```
```python
from awsglue.utils import getResolvedOptions
args = getResolvedOptions(sys.argv, ["JOB_NAME", "run_date"])
glueContext.create_dynamic_frame.from_catalog(database="db", table_name="t",
    push_down_predicate="order_date='2026-11-18'", transformation_ctx="src")
```

### Frequently used configurations
`--job-bookmark-option`, `--TempDir`, `--enable-metrics`, `--enable-continuous-cloudwatch-log`, `--additional-python-modules`, `--enable-auto-scaling`, `--conf spark.sql.shuffle.partitions=...`, worker type/count, Glue version, `--enable-glue-datacatalog` (for Spark SQL on catalog), job timeout and retries.

### Common errors and solutions
| Error | Solution |
|---|---|
| AccessDenied / Lake Formation permission | Fix role policies/LF grants |
| OOM / container killed | Bigger workers, more partitions, fix skew |
| Job runs forever | Check skew/small files/connection hangs; set timeout |
| Crawler wrong schema | Custom classifier, consistent layout, explicit DDL |
| `EntityNotFoundException` | Wrong database/table name or Region |
| VPC connectivity timeout | Add VPC endpoint/NAT and security group rules |

### Service limitations
Spark startup time (tens of seconds+) — poor for tiny jobs; limited low-level cluster control; streaming is micro-batch; crawlers can be slow/costly at scale; workflows are basic orchestration; check quotas for concurrent runs, DPUs and catalog objects.

### Performance and cost optimisation
Parquet + partitioning; `groupFiles` for small inputs; broadcast small tables; auto scaling; Flex for non-urgent; avoid unnecessary full recrawls; limit `count()` calls (they trigger jobs); monitor with job run insights.

### Security best practices
Dedicated least-privilege roles per job; encrypt catalog/S3/job bookmarks/CloudWatch logs with KMS; keep credentials in Secrets Manager (Glue connections); VPC endpoints for private access; Lake Formation for fine-grained table/column control; avoid hardcoded secrets in scripts.

### Connections with other AWS services
S3, IAM, KMS, CloudWatch, Athena, Redshift (Spectrum/COPY), EMR (shared catalog), Lake Formation, EventBridge/Step Functions/MWAA (orchestration), Kinesis/MSK (streaming), DMS (CDC sources), Secrets Manager.

### Quick revision cheat sheet
```
Sources -> Crawler -> Catalog (metadata only) -> Glue job (Spark, GlueContext) -> S3 Parquet partitioned
DPU = 4 vCPU/16 GB ; G.1X=1 DPU, G.2X=2 ; min 2 workers
DynamicFrame (flexible schema, ResolveChoice) <-> DataFrame (Catalyst)
Bookmarks need job.init/commit + unique transformation_ctx
Idempotent: dynamic partition overwrite + run_date parameter
```

### 10 rapid-fire revision questions
1. **What is a DPU?** 4 vCPU and 16 GB memory.
2. **Does the Data Catalog store data?** No, only metadata.
3. **Minimum workers for a Spark job?** Two.
4. **What resolves mixed column types in DynamicFrames?** `ResolveChoice`.
5. **What must the script call for bookmarks to work?** `job.init()` and `job.commit()`.
6. **How to read fewer partitions?** `push_down_predicate`.
7. **How to speed up many tiny S3 files?** `groupFiles`/`groupSize` or compaction.
8. **Language for Glue Data Quality rules?** DQDL.
9. **Which engines can use the Glue Data Catalog?** Athena, Redshift Spectrum, EMR, Glue, Lake Formation.
10. **How to reprocess with bookmarks enabled?** Reset the bookmark (`reset-job-bookmark`) or use explicit parameters.

---

## Official AWS documentation
- AWS Glue Developer Guide — https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html
- Data Catalog — https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html
- Crawlers — https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html
- Glue ETL programming (PySpark) — https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python.html
- Job parameters — https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-glue-arguments.html
- Job bookmarks — https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html
- Worker types and DPUs — https://docs.aws.amazon.com/glue/latest/dg/add-job.html
- Glue Data Quality — https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html
- Glue pricing — https://aws.amazon.com/glue/pricing/
- Boto3 Glue reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html
