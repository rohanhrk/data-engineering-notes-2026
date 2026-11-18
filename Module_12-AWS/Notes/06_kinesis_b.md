---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is Amazon Kinesis Data Streams and what are shards?**
KDS is a managed, durable, ordered stream service. A stream is made of **shards**; each shard is a unit of capacity and ordering. Records (data blob + partition key + sequence number) are routed to shards by hashing the partition key. In provisioned mode each shard supports up to 1 MiB/s or 1,000 records/s of writes and 2 MiB/s of shared reads. Records are replicated across AZs and retained 24 hours by default (up to 365 days). *Keywords: shard, partition key, sequence number, retention, replay, ordering per shard.* Data engineers size shards, pick keys and monitor throttling and iterator age.

**Q2. How do partition keys work, and what is a hot shard?**
Kinesis computes an MD5 hash of the partition key and maps it into the hash-key range owned by a shard. Same key → same shard, so order is preserved per key but not across keys. A **hot shard** occurs when keys are skewed (one customer or a constant key) so one shard exceeds its limits while others are idle, causing `WriteProvisionedThroughputExceeded`. Fixes: choose high-cardinality keys, add a random suffix/salt for very hot keys (accepting loss of strict per-key ordering), split the hot shard, or use on-demand mode (it still can't fix extreme single-key skew).

**Q3. Compare provisioned and on-demand capacity modes.**
Provisioned: you choose the shard count (and reshard as needed); billing per shard-hour plus payload; cheapest for steady, predictable traffic; risk of throttling if under-provisioned. On-demand: no capacity planning, the stream scales with throughput; billing per stream-hour and data volume; best for spiky/unknown workloads; scaling follows traffic patterns and has documented limits, so check quotas. Interview tip: mention cost at steady load vs operational simplicity and that you can switch modes with restrictions.

**Q4. How do retention and replay work?**
Records stay in the stream for the retention period (default 24 h; extend up to 365 days at extra cost). Consumers can read from `TRIM_HORIZON` (oldest available), `LATEST`, `AT_TIMESTAMP` or a sequence number, so after a bug fix you can replay recent history without asking producers to resend. Unlike SQS, reading does not delete records. After retention expires, data is gone, so long-term storage needs Firehose/S3 as an archive.

**Q5. What is the difference between shared-throughput consumers and enhanced fan-out?**
With shared throughput, all consumers of a shard use `GetRecords` and split the shard's 2 MiB/s read capacity and 5 calls/s; adding consumers slows each one. With **enhanced fan-out**, each registered consumer gets its own dedicated 2 MiB/s per shard delivered by push (`SubscribeToShard` over HTTP/2) with lower latency, at additional cost and with a limit on consumers per stream. Choose EFO for multiple consumers, strict latency or heavy read volume; standard is cheaper for one or two light consumers.

**Q6. What does the Kinesis Client Library (KCL) do, and how does checkpointing work?**
KCL simplifies consumer apps: it distributes shards among workers using **leases** stored in a DynamoDB table, balances load, handles resharding and de-aggregates KPL records. Checkpointing records the last processed sequence number so a restarted worker resumes after it. Because a crash can happen after processing but before checkpointing, delivery is **at-least-once** — records after the last checkpoint are reprocessed, so processing must be idempotent. Checkpoint after processing a batch successfully, not before.

**Q7. Explain Kinesis Data Firehose (Amazon Data Firehose) and how it differs from KDS.**
Firehose is a managed delivery service: it buffers streaming data (by size/time) and loads it into S3, Redshift (via S3), OpenSearch, Splunk, HTTP endpoints, Iceberg or Snowflake, optionally transforming with Lambda, converting JSON to Parquet/ORC, compressing and dynamically partitioning. You write no consumer code and there is no replay or shard management. KDS is a stream you build consumers for, with replay and per-key ordering. Common combo: producers → KDS → Firehose (archive) + other consumers.

**Q8. What delivery semantics does Kinesis provide and how do you handle duplicates?**
Producers can create duplicates (retries after timeouts) and consumers reprocess after failures: Kinesis is **at-least-once** end to end. To get effectively-once results use **idempotent sinks** — deterministic keys with upserts (MERGE, DynamoDB conditional writes), deduplication by event ID in downstream processing, or Flink with checkpointing and exactly-once supported sinks. Include a unique `event_id` in each record so deduplication is possible.

**Q9. How do you monitor a Kinesis stream and consumers?**
Key CloudWatch metrics: `IncomingBytes/Records` (load), `WriteProvisionedThroughputExceeded` (producer throttling), `ReadProvisionedThroughputExceeded` (consumer throttling), `GetRecords.IteratorAgeMilliseconds` (consumer lag), `GetRecords.Success`. Enable enhanced shard-level metrics to spot hot shards. For Lambda consumers watch `IteratorAge`, errors and throttles; for Firehose `DeliveryToS3.Success`, `DataFreshness` and error logs. Alarm on iterator age growing and on throttling.

**Q10. When would you choose Kinesis vs SQS vs SNS vs MSK vs Flink?**
Kinesis Data Streams: ordered, replayable event streams with multiple consumers. SQS: decoupling/work queue, each message handled once by one consumer, no replay. SNS: fan-out push notifications. MSK: Kafka-compatible streaming when you need Kafka APIs/ecosystem or longer, larger-scale topics. Managed Service for Apache Flink: stateful stream **processing** (windows/joins) that reads from Kinesis/MSK. Often combined, e.g. KDS for ingestion + Flink for computation + Firehose for archive.

### B. Scenario-Based Questions (5)

**S1. One customer generates 70% of traffic and writes are throttled although total throughput is under the limit.**
*Problem:* hot shard from skewed partition key (`customer_id`). *Solution:* use a more granular key (e.g. `customer_id + session_id`) or salt the key (`customer_id#0..N`) for that customer, spreading load across shards; reshard/split; use batching/KPL aggregation to improve utilisation; implement producer retries with backoff. *Why:* throughput is per shard, not stream-wide. *Alternatives:* a dedicated stream for the heavy customer. *Trade-off:* ordering is only guaranteed per final key; consumers must aggregate across salted keys.

**S2. Ingest 10,000 JSON events/s from IoT devices into S3 as Parquet for Athena.**
*Solution:* devices → KDS (on-demand or enough shards: 10k records/s ≈ at least 10 shards if each record is small; check MiB/s too) → Firehose with **record format conversion** to Parquet using a Glue table schema, buffering 128 MB/300 s (or balanced for latency), dynamic partitioning by date/device type, error prefix; catalog partitions via projection. *Why:* managed, no code, columnar output. *Alternatives:* Lambda/Flink writing Parquet; Iceberg destination for upserts. *Trade-off:* larger buffers = fewer files but higher latency; conversion requires consistent schemas.

**S3. Three teams read the same stream and each says their app is slow.**
*Problem:* shared-throughput consumers split 2 MiB/s per shard and 5 calls/s. *Solution:* register consumers with **enhanced fan-out** so each gets dedicated throughput; or reduce polling inefficiency (larger batches); check `ReadProvisionedThroughputExceeded` and `IteratorAge`. *Why:* EFO removes read contention. *Alternatives:* fan out to separate streams via Firehose/Lambda. *Trade-off:* additional EFO cost and per-stream consumer limits.

**S4. Downstream totals are inflated because some events appear twice.**
*Problem:* at-least-once delivery from producer retries and consumer reprocessing. *Solution:* include a unique `event_id`; dedupe in the consumer using a conditional write to DynamoDB (`attribute_not_exists(event_id)`) or MERGE on event ID in the warehouse; make aggregations idempotent; use Flink with checkpoints if windows require it. *Why:* you cannot fully prevent duplicates, so make processing idempotent. *Alternatives:* Kafka transactions on MSK. *Trade-off:* extra state/lookup cost and latency.

**S5. Detect when sensor readings exceed a threshold for 5 minutes, in near real time.**
*Solution:* KDS → Managed Service for Apache Flink with a sliding or session window keyed by device, maintaining state, emitting alerts to SNS/EventBridge and results to DynamoDB; archive raw data via Firehose. *Why:* windows and state are Flink's strengths; Lambda would struggle to maintain multi-minute state. *Alternatives:* Lambda + DynamoDB counters for simple rules; Kinesis Data Analytics SQL (legacy). *Trade-off:* Flink adds operational/learning complexity and cost.

### C. Troubleshooting Questions (3)

**T1. Producers receive `ProvisionedThroughputExceededException` / high `WriteProvisionedThroughputExceeded`.**
*Root causes:* too few shards for the incoming bytes or records/s; hot shard from skewed keys; many tiny `PutRecord` calls; bursts exceeding capacity; retries amplifying load. *Debug approach:* compare `IncomingBytes`/`IncomingRecords` with capacity (shards × limits); enable shard-level metrics (`IncomingBytes` per shard) to detect imbalance; review partition key distribution. *Fix:* add shards (`update-shard-count` or split hot shards) or switch to on-demand; improve key distribution; batch with `PutRecords`/KPL aggregation; use exponential backoff with jitter.
```bash
aws kinesis update-shard-count --stream-name clicks --target-shard-count 4 --scaling-type UNIFORM_SCALING
```

**T2. Lambda consumer's `IteratorAge` keeps increasing and the same errors repeat.**
*Root causes:* a poison record repeatedly fails the batch, and with default retry settings Lambda retries until the record expires, blocking the shard; function too slow/timeouts; downstream throttling; insufficient `ParallelizationFactor`/batch size; reserved concurrency too low. *Debug:* CloudWatch Logs for the error and failing record; `IteratorAge`, `Errors`, `Throttles`, `Duration` metrics; check event source mapping settings. *Fix:* enable `ReportBatchItemFailures`, `BisectBatchOnFunctionError`, set `MaximumRetryAttempts` and `MaximumRecordAgeInSeconds`, configure an **on-failure destination** (SQS/SNS) to capture bad records; increase batch size/parallelization or memory; make downstream writes resilient with backoff; validate data to avoid poison records.

**T3. Firehose shows the stream as ACTIVE but nothing appears in S3 (or delivery failures).**
*Root causes:* buffer size/interval not reached yet; source stream has no new data (starting position); IAM role lacks `s3:PutObject`/`kinesis:GetRecords`/KMS permissions; Lambda transformation errors; record format conversion schema mismatch (Glue table missing/wrong types); S3 bucket policy or wrong bucket/Region; prefix expression without an error prefix; destination encryption issues. *Debug:* CloudWatch metrics (`DeliveryToS3.Success`, `DataFreshness`, `IncomingRecords`), Firehose error logging to CloudWatch Logs, look in the **error output prefix** in S3 for failed records and reasons; check the role policy and trust. *Fix:* correct permissions/schema, wait for the buffer interval or lower buffer settings, fix the transformation function, ensure producers send newline-delimited valid JSON, and reprocess failed records from the error prefix.

---

## 7. Revision and Quick Reference

### Key takeaways
- Kinesis Data Streams = ordered, replayable, sharded stream; Firehose = managed delivery; Flink = stateful processing.
- Throughput is per shard: write 1 MiB/s or 1,000 records/s; read 2 MiB/s shared.
- Partition key controls ordering and balance — avoid hot keys.
- At-least-once everywhere → idempotent consumers and sinks.
- Monitor iterator age and throttling.

### Commonly forgotten details
- Ordering is only guaranteed within a shard.
- `PutRecords` can partially fail — check `FailedRecordCount`.
- Retention is not infinite (24 h default; up to 365 days).
- A failing Lambda batch blocks a shard until retries/age limits are reached.
- Firehose buffering: whichever of size/interval is hit first; small buffers → many small files.
- Firehose needs an `ErrorOutputPrefix` when custom prefix expressions are used.
- Add newline delimiters to JSON written to Firehose/S3.
- Shard-hours cost money even without traffic.

### Important commands and syntax
```bash
aws kinesis create-stream --stream-name s --stream-mode-details StreamMode=ON_DEMAND
aws kinesis describe-stream-summary --stream-name s
aws kinesis put-record --stream-name s --partition-key k --data "$(echo -n hello | base64)"
aws kinesis list-shards --stream-name s
aws kinesis get-shard-iterator --stream-name s --shard-id shardId-000000000000 --shard-iterator-type TRIM_HORIZON
aws kinesis update-shard-count --stream-name s --target-shard-count 4 --scaling-type UNIFORM_SCALING
aws kinesis increase-stream-retention-period --stream-name s --retention-period-hours 72
aws firehose describe-delivery-stream --delivery-stream-name d
aws lambda create-event-source-mapping --function-name f --event-source-arn <stream-arn> --starting-position LATEST --batch-size 100
```

### Frequently used configurations
Stream mode and retention; Lambda mapping: `BatchSize`, `MaximumBatchingWindowInSeconds`, `ParallelizationFactor`, `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds`, on-failure destination; Firehose: buffer hints, compression, prefix/error prefix, format conversion, dynamic partitioning, backup.

### Common errors and solutions
| Error | Solution |
|---|---|
| `ProvisionedThroughputExceeded` | Add shards/on-demand, fix hot keys, batch + backoff |
| Rising `IteratorAge` | Scale consumers (parallelization/EFO), fix slow/failing processing |
| Duplicates | Idempotent sinks, event IDs |
| `ExpiredIteratorException` | Iterator older than 5 minutes — get a new one |
| Firehose delivery failure | Permissions, schema, error prefix, logs |
| `AccessDeniedException` | Producer/consumer IAM policy or KMS key access |

### Service limitations
Per-shard throughput limits; ordering only within a shard; limited retention window; at-least-once delivery; consumers per stream for EFO limited; record size limits; resharding limits and cost; Firehose is not a replay store and has buffering latency; Firehose Lambda transformation has size/time constraints (check quotas).

### Performance and cost optimisation
Batch writes (`PutRecords`/KPL aggregation); compress payloads; choose on-demand for spiky vs provisioned for steady; right-size shards and delete unused streams; use EFO only when needed; larger Firehose buffers/Parquet conversion; extend retention only when needed; reduce small-file counts in S3.

### Security best practices
Least-privilege IAM per producer/consumer; KMS server-side encryption; VPC endpoints; separate roles for Firehose; avoid logging sensitive payloads; CloudTrail auditing; encrypt destinations; restrict who can `PutRecord`.

### Connections with other AWS services
S3, Firehose, Lambda, Managed Service for Apache Flink, DynamoDB (KCL leases/state), Redshift (streaming ingestion/COPY), OpenSearch, Glue (schema for format conversion), IAM/KMS, CloudWatch, EventBridge/SNS/SQS, DMS and DynamoDB Streams as sources.

### Quick revision cheat sheet
```
Producer --PutRecords(partition key)--> Stream(shards: 1MiB/s or 1000 rec/s in; 2MiB/s out)
Consumers: shared (GetRecords) | EFO (own 2MiB/s per shard) | Lambda | KCL(DynamoDB leases) | Flink
Retention 24h..365d ; replay with TRIM_HORIZON / AT_TIMESTAMP
Firehose: buffer size|interval -> S3/Redshift/OpenSearch/Iceberg ; format conversion ; dynamic partitions
At-least-once => idempotent
Metrics: IteratorAge, WriteProvisionedThroughputExceeded
```

### 10 rapid-fire revision questions
1. **What routes a record to a shard?** MD5 hash of the partition key.
2. **Write limit per shard (provisioned)?** 1 MiB/s or 1,000 records/s.
3. **Default retention?** 24 hours.
4. **Metric showing consumer lag?** `GetRecords.IteratorAgeMilliseconds`.
5. **What does EFO give each consumer?** Dedicated 2 MiB/s per shard, push-based.
6. **Where does KCL store leases/checkpoints?** A DynamoDB table.
7. **Which service delivers streams to S3 with no consumer code?** Firehose.
8. **Delivery semantics of Kinesis?** At-least-once.
9. **How do you check partial `PutRecords` failures?** `FailedRecordCount` and per-record `ErrorCode`.
10. **Which service does stateful windowing?** Managed Service for Apache Flink.

---

## Official AWS documentation
- Kinesis Data Streams Developer Guide — https://docs.aws.amazon.com/streams/latest/dev/introduction.html
- Quotas and limits — https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html
- Choosing capacity mode — https://docs.aws.amazon.com/streams/latest/dev/how-do-i-size-a-stream.html
- Enhanced fan-out — https://docs.aws.amazon.com/streams/latest/dev/enhanced-consumers.html
- Using Lambda with Kinesis — https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html
- Amazon Data Firehose Developer Guide — https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html
- Managed Service for Apache Flink — https://docs.aws.amazon.com/managed-flink/latest/java/what-is.html
- Kinesis pricing — https://aws.amazon.com/kinesis/data-streams/pricing/
- Boto3 Kinesis reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html
