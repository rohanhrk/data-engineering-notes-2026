---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. Explain Redshift's architecture.**
A Redshift cluster has a **leader node** (accepts connections, parses and optimises SQL, compiles code, coordinates) and **compute nodes** divided into **slices**; each slice processes a portion of the data in parallel (MPP). Data is stored **column-wise and compressed**. RA3 nodes store data in Redshift Managed Storage (S3-backed) with local SSD caching, decoupling compute from storage. Serverless replaces nodes with a namespace + workgroup measured in RPUs. Queries scan only needed columns, skip blocks via zone maps, and redistribute data between slices only when joins require it. *Keywords: leader, compute nodes, slices, columnar, MPP, RA3, Spectrum.*

**Q2. Provisioned cluster vs Redshift Serverless — how do you choose?**
Provisioned: you select node type/count; good for steady, predictable high-utilisation workloads, reserved-instance discounts, and fine tuning with WLM. Serverless: capacity (RPUs) scales automatically and pauses when idle; good for spiky, intermittent or new workloads and teams that don't want capacity planning; control cost with base capacity and maximum RPU/usage limits. Both use the same SQL engine and features. Decision factors: utilisation pattern, operational skill, cost predictability. Pitfall: serverless without limits can overspend on heavy queries; provisioned idle clusters waste money.

**Q3. What are distribution styles and how do you choose a distribution key?**
Distribution style defines how rows are placed on slices: **EVEN** (round-robin), **KEY** (hash of a column), **ALL** (copy on every node), **AUTO** (Redshift picks and adapts). Choose KEY on the column used to join the largest tables so matching rows are co-located (avoids network redistribution), with high cardinality and even spread (avoid skew); ALL for small, slowly changing dimensions; EVEN when there is no dominant join; AUTO if unsure. Check `SVV_TABLE_INFO` (skew) and `EXPLAIN` for `DS_DIST_*`/`DS_BCAST_*` steps to validate.

**Q4. What are sort keys and zone maps?**
Sort keys define how rows are ordered on disk. Redshift stores min/max per 1 MB block (zone maps); when data is sorted on a filter column (commonly a date), queries skip blocks outside the range. **Compound** sort keys help when queries filter on the leading column(s); **interleaved** gives equal weight to several columns but is rarely recommended and needs heavier maintenance; **AUTO** lets Redshift choose. Pick columns used in range filters and merge joins; avoid sorting on high-cardinality, unused columns.

**Q5. What are best practices for loading data with `COPY`?**
Use `COPY` instead of many `INSERT`s; load from S3 in **multiple compressed files of similar size** (ideally a multiple of the slice count; 1 MB–1 GB each) so slices work in parallel; use columnar formats (Parquet/ORC) where possible; use a **manifest** for an exact file list; use an IAM role (not keys); load into a **staging table** and then `MERGE`/insert into the target; use `COMPUPDATE`/`STATUPDATE` appropriately (stats update after large loads); check `SYS_LOAD_ERROR_DETAIL`/`STL_LOAD_ERRORS` for failures; keep the cluster and S3 bucket in compatible Regions.

**Q6. What is Redshift Spectrum and how does it differ from Athena?**
Spectrum lets Redshift query S3 data through external tables in the Glue Catalog, using a fleet of Spectrum workers; results combine with local tables in one SQL statement. Athena is a separate serverless service for S3 data. Differences: Spectrum requires a Redshift cluster/workgroup and charges Spectrum scan fees plus Redshift compute; it's ideal for joining cold lake data with warehouse tables and for extending storage. Athena is better for standalone ad hoc analysis. Both benefit from Parquet and partitioning.

**Q7. How do WLM, concurrency scaling and short query acceleration work?**
**Automatic WLM** assigns memory/concurrency dynamically and prioritises queries by queue priority; **manual WLM** uses fixed queues and slots. **Query monitoring rules** log, change priority or abort queries that exceed thresholds. **Concurrency scaling** provisions extra transient capacity to handle bursts of concurrent read queries (some free daily credits apply for provisioned clusters; check docs). **SQA** speeds up short queries by running them in a dedicated space. Serverless manages scaling automatically within RPU limits. The goal: protect BI dashboards from long ETL queries.

**Q8. What are `VACUUM` and `ANALYZE`, and do you still need them?**
Deletes/updates mark rows as deleted and rewrite changed rows; `VACUUM` reclaims space and re-sorts rows. `ANALYZE` refreshes table statistics so the optimiser plans well. Redshift now runs **automatic vacuum delete, automatic table sort and automatic analyze** in the background during low-load periods, so manual runs are mostly for large delete/update jobs or after big loads when performance matters immediately. Monitor `unsorted` and `stats_off` in `SVV_TABLE_INFO`. Design tip: prefer append-and-partition-by-time patterns (or truncate/insert) over heavy updates.

**Q9. What are materialised views and when do you use them?**
A materialised view stores the result of a query; refresh updates it (manually or auto, incremental when the query shape supports it). Use for expensive aggregations and joins repeatedly read by dashboards. The optimiser may automatically rewrite queries to use an MV (when applicable). Trade-offs: storage, refresh cost/latency, and not all SQL constructs support incremental refresh. They also power **streaming ingestion** from Kinesis/MSK into Redshift.

**Q10. Why are primary/foreign keys "informational" in Redshift and how do you handle duplicates?**
Redshift does not enforce primary key, unique or foreign key constraints (only NOT NULL is enforced). The optimiser can use declared keys as hints, but duplicates are possible if loads aren't careful. Prevent duplicates with idempotent load patterns: load into a staging table, deduplicate (e.g. `ROW_NUMBER()` over business key), and use `MERGE` or delete-insert inside a transaction; add data quality checks (`COUNT(*)` vs `COUNT(DISTINCT key)`). This is a common interview trap.

### B. Scenario-Based Questions (5)

**S1. A dashboard query joining a 2-billion-row fact table to a 10-million-row customer dimension takes minutes.**
*Problem:* data redistribution (`DS_DIST_BOTH`/`DS_BCAST_INNER`) on every run. *Solution:* review `EXPLAIN`; set `DISTKEY(customer_id)` on both tables so the join is co-located (`DS_DIST_NONE`), keep the filter column (date) as sort key, ensure statistics are current, avoid `SELECT *`, and consider a materialised view for the dashboard aggregation. If the dimension is small, `DISTSTYLE ALL`. *Why:* removing network movement dominates MPP performance. *Alternatives:* AUTO table optimisation to recommend keys; concurrency scaling won't fix per-query slowness. *Trade-off:* a key suiting one join may hurt others; watch skew.

**S2. Load 300 GB of daily CSV files into Redshift reliably.**
*Solution:* land files in S3 split into many compressed files (e.g. 128 MB–1 GB gzip each, count a multiple of slices), `COPY` into a staging table with a manifest/prefix and an IAM role, validate counts and error tables, then `MERGE` into the target in a transaction; orchestrate with Step Functions and the Data API; alert on failure and make the load idempotent (truncate staging first, key-based merge). Better still convert to Parquet. *Why:* parallel loading uses all slices. *Alternatives:* auto-copy jobs, Glue ETL to Redshift, zero-ETL for supported sources. *Trade-off:* compression/splitting step vs load speed.

**S3. You receive CDC (inserts, updates, deletes) from a source database into S3 and must reflect it in Redshift.**
*Solution:* load change files into a staging table with an operation column (`I/U/D`) and a sequence/timestamp; keep only the latest change per key using `ROW_NUMBER()`; run `MERGE` (`WHEN MATCHED AND op='D' THEN DELETE`, `WHEN MATCHED THEN UPDATE`, `WHEN NOT MATCHED THEN INSERT`) in one transaction; truncate staging. *Why:* atomic, idempotent upserts. *Alternatives:* zero-ETL integration if the source is Aurora/RDS/DynamoDB; Iceberg in the lake queried via Spectrum. *Trade-off:* ordering and late events need careful handling.

**S4. Workload is quiet most of the day but spikes at 9 am with 200 dashboard users; cost is high.**
*Solution:* move to Redshift Serverless with a modest base capacity and a max RPU limit (it scales for spikes and pauses when idle), or keep provisioned with concurrency scaling; add materialised views/result caching for repeated dashboard queries, short-query acceleration, query monitoring rules to stop runaway queries, and schedule heavy ETL off-peak. *Why:* matches capacity to demand. *Alternatives:* resize/pause-resume provisioned clusters on a schedule, reserved instances if usage is steady. *Trade-off:* serverless cold start/ramp-up and cost variability vs fixed predictable cost.

**S5. The data science team needs live access to the warehouse tables without affecting dashboard performance.**
*Solution:* use **Redshift data sharing** to give a separate consumer workgroup/cluster read access to the producer's schemas (no data copy, live data), with permissions via GRANT; consumers have their own compute so workloads are isolated. Cold history can stay in S3 and be queried via Spectrum. *Why:* workload isolation without ETL duplication. *Alternatives:* snapshot restore (stale), UNLOAD to S3 + Athena, Lake Formation sharing. *Trade-off:* some limitations on shared objects and cross-region/account setup.

### C. Troubleshooting Questions (3)

**T1. `COPY` fails with "Load into table failed" or `S3ServiceException: Access Denied`.**
*Root causes:* IAM role not attached to the cluster/namespace or lacks `s3:GetObject`/`s3:ListBucket`; trust policy missing Redshift principals; bucket in a different Region without the `REGION` option; KMS-encrypted objects without `kms:Decrypt`; malformed rows, wrong delimiter, header not skipped, type mismatch, too many errors. *Debug:* read the error message; `SELECT * FROM sys_load_error_detail ORDER BY start_time DESC` (or `stl_load_errors`) for file/line/column and reason; test a small file; check role association (`SELECT * FROM svv_iam_roles`? or the console) and policy simulation; check Region. *Fix:* attach/correct the role, add permissions, use `REGION`, fix data or options (`IGNOREHEADER`, `DELIMITER`, `TRUNCATECOLUMNS`, `MAXERROR`), rerun.

**T2. A previously fast query is now slow or the cluster shows high disk usage.**
*Root causes:* stale statistics after a big load; many unsorted rows/deleted rows needing vacuum; data skew on the distribution key; a bad plan with large redistributions; concurrent heavy ETL consuming resources; temporary-table spill from huge joins. *Debug approach:* `EXPLAIN` the query (look for `DS_DIST_BOTH`, `DS_BCAST_INNER`, nested loop joins); `SVV_TABLE_INFO` for `skew_rows`, `unsorted`, `stats_off`, `size`; `SYS_QUERY_HISTORY` and `SYS_QUERY_DETAIL` for runtime, queue and spill; check WLM queue times. *Fix:* run `ANALYZE`/`VACUUM` (or `VACUUM SORT ONLY`), change distribution/sort keys (or use automatic table optimisation), rewrite the query (filter early, avoid cross joins), tune WLM/priorities or add concurrency scaling.

**T3. Clients cannot connect to the cluster (timeout or "could not connect to server").**
*Root causes:* cluster not publicly accessible but client is outside the VPC; security group missing inbound port 5439 from the client CIDR; subnet route/NACL issues; wrong endpoint/port/database; Serverless workgroup not publicly accessible; DNS/VPN problems; user lacks credentials. *Debug:* confirm the endpoint, port (default 5439), and `PubliclyAccessible` setting; test from a bastion/EC2 in the VPC (`nc -zv endpoint 5439`); inspect security group and route tables; use the **Query Editor v2** or **Data API** to confirm the database itself works (these don't need direct network access). *Fix:* update security groups/NACLs, use VPN/PrivateLink, enable public access only if required with restricted IPs, correct connection settings.

---

## 7. Revision and Quick Reference

### Key takeaways
- Redshift = columnar MPP warehouse; leader + compute slices; RA3 separates storage; Serverless uses RPUs.
- Performance = distribution keys + sort keys + statistics + good loading (COPY).
- Keys are informational — enforce uniqueness in pipelines.
- Spectrum extends queries to S3; data sharing isolates workloads.

### Commonly forgotten details
- Use multiple files for `COPY`; one huge file loads on one slice.
- `COPY` from Parquet does not populate Hive partition columns from folder names.
- IAM roles must be associated with the cluster/namespace for COPY/Spectrum.
- Primary/foreign/unique keys aren't enforced.
- External-table partitions must be added/registered.
- Spectrum bills per TB scanned in addition to Redshift compute.
- `DISTSTYLE ALL` multiplies storage by node count.
- Temporary/staging tables should use `EVEN` or the target's key to speed merges.

### Important commands and syntax
```sql
CREATE TABLE t (...) DISTSTYLE KEY DISTKEY(c) COMPOUND SORTKEY(d);
COPY t FROM 's3://b/p/' IAM_ROLE '<arn>' FORMAT AS PARQUET;
UNLOAD ('SELECT ...') TO 's3://b/out/' IAM_ROLE '<arn>' FORMAT AS PARQUET;
MERGE INTO tgt USING stg ON ... WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...;
ANALYZE t;  VACUUM t;  EXPLAIN SELECT ...;
SELECT * FROM svv_table_info; SELECT * FROM sys_query_history ORDER BY start_time DESC;
SELECT * FROM sys_load_error_detail;
CREATE MATERIALIZED VIEW mv AUTO REFRESH YES AS SELECT ...;
```
```bash
aws redshift-data execute-statement --workgroup-name wg --database dev --sql "select 1"
aws redshift-data describe-statement --id <id>
aws redshift-serverless list-workgroups
```

### Frequently used configurations
Distribution/sort keys, `ENCODE AUTO`, automatic WLM with priorities, query monitoring rules, concurrency scaling, base/max RPU (serverless), enhanced VPC routing, encryption with KMS, auto-copy jobs, scheduled queries/snapshots.

### Common errors and solutions
| Error | Solution |
|---|---|
| COPY access denied | Associate/correct IAM role, S3/KMS permissions, Region |
| Load error in `sys_load_error_detail` | Fix data/types/options |
| Slow join (`DS_DIST_BOTH`) | Align distribution keys / use ALL for small tables |
| Disk full / spill | Fix skew, filter earlier, resize, vacuum |
| Cannot connect | Security group, subnet, public access, endpoint |
| Duplicates | Staging + MERGE + checks |

### Service limitations
Not for OLTP; no enforced constraints; leader-node-bound functions; some PostgreSQL features unsupported; concurrency limits per queue/slot (automatic WLM adjusts); maximum limits on columns/row size; resize/pause considerations on provisioned; Spectrum limitations on formats/features; verify current quotas.

### Performance and cost optimisation
Right keys and encodings; compress and split loads; keep statistics fresh; use materialised views/result caching; Spectrum/UNLOAD for cold data; Serverless usage limits; pause/resize provisioned clusters; reserved instances for steady loads; monitor with CloudWatch and system views.

### Security best practices
Private subnets, security groups, SSL; KMS encryption; IAM roles instead of keys; least-privilege GRANTs, row-level security and column-level access; audit logging; rotate/manage admin credentials via Secrets Manager; restrict public access; use data sharing instead of copies.

### Connections with other AWS services
S3 (COPY/UNLOAD/Spectrum), Glue (catalog, ETL), IAM/KMS (access, encryption), Kinesis/MSK (streaming ingestion), DMS and zero-ETL (replication), Step Functions/MWAA (orchestration), QuickSight (BI), CloudWatch/CloudTrail (monitoring, audit), Lake Formation (governance).

### Quick revision cheat sheet
```
Leader (plan) + compute slices (parallel) ; columnar + compression ; RA3 managed storage
DIST: KEY (big join) | ALL (small dim) | EVEN | AUTO     SORT: date/range filters
Load: COPY from S3 (many compressed files) -> staging -> MERGE
Keys not enforced -> dedupe yourself
Spectrum = S3 external tables ; MV = precomputed ; Data share = live cross-cluster
Tune: EXPLAIN, svv_table_info, ANALYZE/VACUUM, WLM/concurrency scaling
```

### 10 rapid-fire revision questions
1. **What coordinates query execution?** The leader node.
2. **What is a slice?** A unit of compute/storage on a node working in parallel.
3. **Best way to bulk load?** `COPY` from S3.
4. **Which distribution style copies a table to every node?** `ALL`.
5. **Are primary keys enforced?** No — informational only.
6. **What do zone maps store?** Min/max values per block.
7. **What does Spectrum query?** External tables on S3 via the Glue Catalog.
8. **How do you check load errors?** `SYS_LOAD_ERROR_DETAIL` (`STL_LOAD_ERRORS`).
9. **Serverless capacity unit?** RPU (Redshift Processing Unit).
10. **Share live data without copying?** Redshift data sharing.

---

## Official AWS documentation
- Amazon Redshift Database Developer Guide — https://docs.aws.amazon.com/redshift/latest/dg/welcome.html
- Management Guide — https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html
- Redshift Serverless — https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-whatis.html
- Distribution styles — https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html
- COPY command — https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html
- Redshift Spectrum — https://docs.aws.amazon.com/redshift/latest/dg/c-using-spectrum.html
- Workload management — https://docs.aws.amazon.com/redshift/latest/dg/c_workload_mngmt_classification.html
- Materialized views — https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-overview.html
- Data API — https://docs.aws.amazon.com/redshift/latest/mgmt/data-api.html
- Redshift pricing — https://aws.amazon.com/redshift/pricing/
- Boto3 Redshift Data API — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data.html
