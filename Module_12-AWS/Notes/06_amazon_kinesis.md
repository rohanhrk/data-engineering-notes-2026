# Amazon Kinesis — Data Engineering Study Notes (0–2 YOE)

> Self-contained notes: fundamentals → implementation → interview preparation.
> Kinesis limits, capacity modes and service names have changed over time (e.g. "Kinesis Data Firehose" is now "Amazon Data Firehose" and "Kinesis Data Analytics" is now "Amazon Managed Service for Apache Flink"). Always confirm numbers on the quotas page linked at the end.

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

### What is Amazon Kinesis?
**Amazon Kinesis** is AWS's family of services for collecting, processing and delivering **streaming data** (continuously generated events such as clicks, logs, IoT readings and transactions). The data-engineering members of the family are:

| Service | What it does |
|---|---|
| **Kinesis Data Streams (KDS)** | Durable, ordered, replayable stream you write to and read from with your own consumers |
| **Amazon Data Firehose** (formerly Kinesis Data Firehose) | Fully managed delivery of streaming data to S3, Redshift, OpenSearch, Iceberg tables, Splunk, HTTP endpoints, etc. — no consumer code |
| **Amazon Managed Service for Apache Flink** (formerly Kinesis Data Analytics) | Run Apache Flink applications for stateful stream processing (windows, joins, aggregations) |
| Kinesis Video Streams | Video ingestion (not covered here) |

### Why was it introduced and what problem does it solve?
Batch pipelines process data hours after it is created. Many use cases (fraud detection, monitoring, personalisation) need seconds-level latency. Running your own Kafka/Flume cluster is operationally heavy. Kinesis offers managed, scalable ingestion and delivery with durability across multiple Availability Zones.

### Why is it important in Data Engineering?
It is the AWS-native building block for **real-time ingestion**: applications write events once, and several consumers (Lambda, Flink, Firehose, KCL apps) can read them independently. Data engineers choose capacity mode, partition keys, consumers and delivery formats, and monitor lag and throttling.

### When should you use it?
- Real-time analytics or alerts (seconds latency).
- Continuous log/clickstream/IoT ingestion into S3, Redshift or OpenSearch.
- Multiple independent consumers need the same event stream, with replay for a retention window.
- Event-driven architectures with ordered events per key.

### When should you avoid it?
| Situation | Better option |
|---|---|
| Simple message queue between two components, one consumer per message, no replay | SQS |
| Fan-out notifications (email/SMS/Lambda) with no stream replay | SNS / EventBridge |
| Kafka ecosystem compatibility, long retention, many topics, Kafka Connect | Amazon MSK |
| Daily/hourly batch files | S3 + Glue; streaming is unnecessary complexity |
| Exactly-once semantic requirements without idempotent sinks | Design idempotency or use Flink with exactly-once sinks |

### Simple real-world example
A mobile app sends click events to a Kinesis data stream. Firehose reads the stream and writes compressed files to S3 every minute for analysts, while a Lambda function reads the same stream to update a real-time counter in DynamoDB.

### Brief comparison with alternatives
| | Kinesis Data Streams | Amazon MSK (Kafka) | SQS | SNS |
|---|---|---|---|---|
| Model | Ordered sharded log | Kafka topics/partitions | Queue | Pub/sub |
| Replay | Yes (retention up to 365 days) | Yes | No (deleted after processing) | No |
| Ops | Fully managed, simple | Managed Kafka, more concepts | Simplest | Simplest |
| Multiple consumers | Yes (shared or enhanced fan-out) | Yes (consumer groups) | One consumer per message (competing) | Fan-out push |
| Ordering | Per shard (partition key) | Per partition | FIFO queues only | FIFO topics only |

---

## 2. Architecture and Working Mechanism

### Overall architecture
A **data stream** is a set of **shards**. Producers write **records** (data blob + partition key); Kinesis hashes the partition key to pick a shard and appends the record there with an increasing **sequence number**. Consumers read records from shards in order. Data is replicated across three AZs and retained for the retention period (default 24 hours, extendable).

### Major components
- **Stream / shard / record** — the stream is the container; a shard is the unit of capacity and ordering; a record has data, partition key, sequence number.
- **Producers** — SDK (`PutRecord(s)`), **KPL** (Kinesis Producer Library, batching/aggregation/retries), Kinesis Agent, AWS services (CloudWatch Logs, DMS, IoT).
- **Consumers** — Lambda, KCL applications, Flink, Firehose, custom `GetRecords` clients.
- **Enhanced fan-out (EFO)** — dedicated throughput per consumer.
- **Capacity mode** — provisioned (you set shard count) or on-demand (automatic scaling).
- **Firehose delivery stream** — buffers and delivers to destinations with optional transformation.
- **DynamoDB lease table (KCL)** — stores checkpoints/leases for KCL consumers.

### End-to-end flow
1. A producer calls `PutRecords` with data and a **partition key** (e.g. `user_id`).
2. Kinesis applies an MD5 hash to the key; the hash maps to a shard's hash-key range.
3. The record is stored durably in that shard with a sequence number; all records with the same key go to the same shard, preserving order per key.
4. Consumers get a **shard iterator** (e.g. `LATEST`, `TRIM_HORIZON`) and call `GetRecords` (shared throughput), or subscribe with EFO (push over HTTP/2).
5. Consumers process records and **checkpoint** progress (KCL stores it in DynamoDB; Lambda tracks it internally).
6. Records expire after the retention period; consumers can replay from a timestamp or sequence number within it.

### Mermaid architecture
```mermaid
flowchart LR
    P1["Producers: apps, KPL, agents, IoT"] --> KDS["Kinesis Data Stream (shards)"]
    KDS --> L["Lambda consumer"]
    KDS --> FH["Firehose delivery stream"]
    KDS --> FL["Managed Flink app"]
    KDS --> KCL["KCL app (checkpoints in DynamoDB)"]
    FH --> S3[("S3 / Iceberg")]
    FH --> RS[("Redshift")]
    L --> DDB[("DynamoDB")]
    FL --> OS[("OpenSearch / S3 / another stream")]
```

### Explanation of components
- **Shards** provide parallelism and ordering per partition key.
- **Lambda/KCL/Flink** are independent consumers reading the same data.
- **Firehose** is the zero-code route to storage and warehouses.
- **Destinations** store curated or aggregated outputs.

### Practical Data Engineering architecture
```mermaid
flowchart LR
    APP["Web/mobile app"] --> KDS["Kinesis Data Streams"]
    KDS --> FH["Firehose: JSON -> Parquet, buffer 5 min"]
    FH --> RAWS3[("S3 raw/clickstream dt=...")]
    RAWS3 --> GL["Glue catalog"]
    GL --> ATH["Athena / Redshift Spectrum"]
    KDS --> FLK["Flink: 1-min window aggregates"]
    FLK --> DDB[("DynamoDB real-time metrics")]
    FLK --> OSS["OpenSearch dashboards"]
```

---

## 3. Core Concepts and Important Terminologies

### 3.1 Records, partition keys and sequence numbers
- **Record:** a data blob (opaque bytes; JSON/Avro/etc.), a **partition key** (string up to 256 chars) and a **sequence number** assigned by Kinesis. Each record's data size is limited (historically 1 MiB; check current quotas).
- **Partition key:** determines the shard via MD5 hash; records with the same key stay ordered within a shard.
- **Sequence number:** increasing per shard (not global).
- **Why it matters:** key choice controls ordering, balance and hot shards.
- **Mistakes:** Using a constant key (all data in one shard); using extremely skewed keys (one customer dominates); assuming ordering across shards.

### 3.2 Shards and capacity limits (provisioned mode)
- **Definition:** A shard is the base throughput unit. Per shard: writes up to **1 MiB/s or 1,000 records/s**; reads up to **2 MiB/s** (shared across all standard consumers) and up to 5 `GetRecords` calls per second.
- **How to size:** `shards = max(ceil(MB/s in), ceil(records/s ÷ 1000), ceil(MB/s out total ÷ 2))`.
- **Resharding:** split a shard (more capacity) or merge adjacent shards (less cost); `UpdateShardCount` automates uniform scaling.
- **Errors:** `ProvisionedThroughputExceededException` (read side) and `WriteProvisionedThroughputExceeded` metric/error (write side) mean a shard is saturated.

### 3.3 Capacity modes: provisioned vs on-demand
| | Provisioned | On-demand |
|---|---|---|
| You manage | Shard count and scaling | Nothing (stream scales to throughput) |
| Billing | Per shard-hour + PUT payload units | Per stream-hour + data in/out |
| Best for | Predictable throughput, lowest cost at steady load | Unpredictable/spiky traffic, simplicity |
| Caveat | Under-provision → throttling | Scaling is automatic but has limits relative to previous peaks; check docs |
Switching modes is possible with limits on frequency.

### 3.4 Retention and replay
Default retention is 24 hours; extend (up to 365 days) at extra cost. Within retention you can reread data by starting a new iterator at `TRIM_HORIZON` (oldest), `LATEST`, `AT_TIMESTAMP` or sequence numbers — enabling reprocessing after a bug fix. **Mistake:** assuming data is kept forever or that retention extension is free.

### 3.5 Producers
- **`PutRecord` / `PutRecords`:** SDK calls; `PutRecords` batches many records per request (check limits), and **partial failures** must be retried (`FailedRecordCount` > 0).
- **KPL:** library with aggregation (many user records packed into one Kinesis record), batching and retry logic — improves shard utilisation; consumers must de-aggregate (KCL does).
- **Kinesis Agent:** installs on servers to tail log files.
- **Mistakes:** sending one record per request (inefficient, throttles by requests); ignoring partial failures.
```python
import json, boto3
kinesis = boto3.client("kinesis", region_name="ap-south-1")

def send(events, stream="clicks"):
    entries = [{"Data": (json.dumps(e) + "\n").encode(),
                "PartitionKey": str(e["user_id"])} for e in events]
    resp = kinesis.put_records(StreamName=stream, Records=entries)
    failed = resp["FailedRecordCount"]
    if failed:
        # retry only the failed ones
        retry = [r for r, res in zip(entries, resp["Records"]) if "ErrorCode" in res]
        kinesis.put_records(StreamName=stream, Records=retry)
```

### 3.6 Consumers: shared throughput vs enhanced fan-out
- **Shared (standard):** consumers call `GetRecords`; all consumers on a shard split 2 MiB/s and 5 calls/s. Latency typically ~200 ms+ to a second.
- **Enhanced fan-out (EFO):** each registered consumer gets its own 2 MiB/s per shard pushed over HTTP/2 (`SubscribeToShard`), lower latency (~70 ms) at extra cost; there is a limit on registered consumers per stream (check quotas).
- **When to use EFO:** several consumers, latency sensitivity, or when consumers slow each other down.

### 3.7 Kinesis Client Library (KCL) and checkpointing
- **KCL** handles worker coordination, shard leases (stored in a **DynamoDB table**), load balancing, resharding and **checkpointing** (saving the last processed sequence number).
- **Delivery semantics:** at-least-once — after a crash, a worker resumes from the last checkpoint, reprocessing records after it, so processing must be **idempotent**.
- **Mistakes:** checkpointing before finishing processing (data loss) or too rarely (large reprocessing); not giving the app DynamoDB/CloudWatch permissions.

### 3.8 Lambda as a Kinesis consumer
An **event source mapping** polls shards and invokes your function with batches. Key settings: `BatchSize`, `MaximumBatchingWindowInSeconds`, `StartingPosition` (`LATEST`/`TRIM_HORIZON`), `ParallelizationFactor` (1–10 concurrent batches per shard, order maintained per key), `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds`, **on-failure destination** (SQS/SNS), `ReportBatchItemFailures` (partial batch response). **Important:** a failing batch blocks that shard until it succeeds or expires (unless you limit retries and use a failure destination).
```python
def handler(event, context):
    failures = []
    for rec in event["Records"]:
        try:
            import base64, json
            payload = json.loads(base64.b64decode(rec["kinesis"]["data"]))
            process(payload)                       # your idempotent logic
        except Exception:
            failures.append({"itemIdentifier": rec["kinesis"]["sequenceNumber"]})
    return {"batchItemFailures": failures}          # needs ReportBatchItemFailures enabled
```

### 3.9 Amazon Data Firehose
- **Definition:** Managed service that **buffers and delivers** streaming data to destinations with no consumers to write.
- **Sources:** Direct PUT, Kinesis Data Streams, MSK, CloudWatch Logs/Events, IoT, etc.
- **Destinations:** S3, Redshift (via S3 COPY), OpenSearch, Splunk, HTTP endpoint, Snowflake, Apache Iceberg tables.
- **Buffering:** delivery occurs when the **buffer size** (MiB) or **buffer interval** (seconds) is reached first — larger buffers mean fewer/larger files, more latency. Check docs for allowed ranges.
- **Features:** Lambda **transformation**, **record format conversion** (JSON → Parquet/ORC using a Glue table schema), **dynamic partitioning** (partition S3 prefixes by record fields), compression, encryption, backup of failed records, custom S3 prefixes with timestamp expressions (e.g. `dt=!{timestamp:yyyy-MM-dd}/`) and an **error output prefix**.
- **Semantics:** at-least-once; latency is seconds–minutes depending on buffering.
- **Mistakes:** tiny buffers causing small files; missing error prefix when using expressions; not checking `DeliveryToS3.Success`.

### 3.10 Amazon Managed Service for Apache Flink (conceptual)
Runs Flink applications (Java/Scala/Python/SQL) for **stateful stream processing**: windows (tumbling/sliding/session), joins, aggregations, exactly-once processing with checkpoints/state. Typical pattern: read from Kinesis → compute 1-minute aggregates → write to S3/DynamoDB/OpenSearch/another stream. Choose it over Lambda when you need long windows, large state or complex event processing.

### 3.11 Monitoring and key metrics
| Metric | Meaning |
|---|---|
| `IncomingBytes`, `IncomingRecords` | Producer throughput |
| `WriteProvisionedThroughputExceeded` | Producer throttling |
| `ReadProvisionedThroughputExceeded` | Consumer throttling |
| `GetRecords.IteratorAgeMilliseconds` | How far consumers lag behind (key health metric) |
| Firehose `DeliveryToS3.Success`, `DataFreshness` | Delivery health/latency |
Enable **enhanced shard-level metrics** to find hot shards.

### 3.12 Security
IAM policies for producers/consumers (`kinesis:PutRecord(s)`, `GetRecords`, `GetShardIterator`, `DescribeStream`, `ListShards`, `SubscribeToShard`), server-side encryption with KMS, VPC endpoints (PrivateLink), CloudTrail for API auditing.

---

## 4. Data Engineering Use Cases

### Real-world use cases
- Clickstream analytics and personalisation.
- Application/infrastructure log ingestion and monitoring.
- IoT telemetry pipelines.
- Fraud/anomaly detection with windows.
- CDC/event streaming from DynamoDB (DynamoDB Streams → Kinesis) or databases.
- Feeding real-time dashboards (OpenSearch/QuickSight/DynamoDB).

### Batch-adjacent processing
Firehose is a streaming-to-batch bridge: continuous events become partitioned S3 files (e.g. every 5 minutes) that Glue/Athena process in batch. Replay from KDS can rebuild downstream stores.

### Real-time / streaming pipelines
Lambda for lightweight per-record/batch logic; Flink for stateful windows and joins; Firehose for no-code delivery; KCL apps for custom long-running consumers.

### Pipeline example 1 — Clickstream to data lake
```mermaid
flowchart LR
    W["Web app events"] --> K["Kinesis Data Streams"]
    K --> F["Firehose (buffer 5 MB / 60 s, gzip)"]
    F --> S[("S3 clicks/dt=YYYY-MM-DD/")]
    S --> A["Athena table + partition projection"]
    A --> Q["QuickSight"]
```

### Pipeline example 2 — Real-time metrics and alerts
```mermaid
flowchart LR
    SENS["IoT sensors"] --> K["Kinesis Data Streams"]
    K --> FL["Flink: 1-min sliding avg, threshold"]
    FL --> SNS["SNS alert"]
    FL --> DDB[("DynamoDB latest state")]
    K --> FH["Firehose -> S3 archive"]
```

### Why a Data Engineer chooses Kinesis
Fully managed (no brokers), tight integration with Lambda/Firehose/Flink/S3/IAM, replay and ordering per key, simple scaling (on-demand). Choose MSK if you need Kafka APIs/ecosystem, SQS for simple work queues, EventBridge for event routing across SaaS/accounts.

---

## 5. Hands-on Implementation

### Mini-project: Real-time clickstream ingestion to S3 with Kinesis Data Streams and Firehose

**1. Objective:** Create a Kinesis stream, send click events with a Python producer, deliver them to S3 through Firehose (partitioned by date), and read from the stream with a simple consumer.

**2. Business problem:** The product team wants website click events available for analysis within minutes, without managing servers.

**3. Architecture**
```mermaid
flowchart LR
    PR["Python producer (Boto3)"] --> KDS["Kinesis stream: clicks (1 shard)"]
    KDS --> FH["Firehose: clicks-to-s3"]
    FH --> S3[("s3://bucket/streaming/clicks/dt=YYYY-MM-DD/")]
    KDS --> CON["Python consumer (GetRecords)"]
    FH -. "failures" .-> ERR[("s3://bucket/streaming/errors/")]
```

**4. Prerequisites and setup**
- S3 bucket from the S3 notes; AWS CLI and Boto3; an admin-like identity for learning.
- `ACCOUNT`, `REGION`, `BUCKET` shell variables.
- **Costs (not free):** Kinesis Data Streams charges per shard-hour (~a few cents/hour for 1 provisioned shard) plus data; Firehose charges per GB ingested; S3 storage. Run the lab for ~30 minutes and delete everything.

**5–6. Implementation and code**

*Step 1 — Create the stream (1 provisioned shard for a low-cost lab)*
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=ap-south-1
BUCKET=retail-datalake-$ACCOUNT-$REGION
aws kinesis create-stream --stream-name clicks \
  --stream-mode-details StreamMode=PROVISIONED --shard-count 1 --region $REGION
aws kinesis wait stream-exists --stream-name clicks --region $REGION
STREAM_ARN=$(aws kinesis describe-stream-summary --stream-name clicks \
  --query StreamDescriptionSummary.StreamARN --output text)
```

*Step 2 — IAM role for Firehose (read the stream, write S3)*
```bash
cat > fh-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"firehose.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
cat > fh-perms.json <<EOF
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["kinesis:DescribeStream","kinesis:GetShardIterator",
  "kinesis:GetRecords","kinesis:ListShards"],"Resource":"$STREAM_ARN"},
 {"Effect":"Allow","Action":["s3:AbortMultipartUpload","s3:GetBucketLocation","s3:GetObject",
  "s3:ListBucket","s3:ListBucketMultipartUploads","s3:PutObject"],
  "Resource":["arn:aws:s3:::$BUCKET","arn:aws:s3:::$BUCKET/*"]}]}
EOF
aws iam create-role --role-name FirehoseClicksRole --assume-role-policy-document file://fh-trust.json
aws iam put-role-policy --role-name FirehoseClicksRole --policy-name access --policy-document file://fh-perms.json
FH_ROLE=arn:aws:iam::$ACCOUNT:role/FirehoseClicksRole
```

*Step 3 — Create the Firehose delivery stream (Kinesis stream as source, S3 destination)*
```bash
sleep 10   # allow IAM propagation
aws firehose create-delivery-stream --delivery-stream-name clicks-to-s3 \
  --delivery-stream-type KinesisStreamAsSource \
  --kinesis-stream-source-configuration "KinesisStreamARN=$STREAM_ARN,RoleARN=$FH_ROLE" \
  --extended-s3-destination-configuration "{
    \"RoleARN\":\"$FH_ROLE\",
    \"BucketARN\":\"arn:aws:s3:::$BUCKET\",
    \"Prefix\":\"streaming/clicks/dt=!{timestamp:yyyy-MM-dd}/\",
    \"ErrorOutputPrefix\":\"streaming/errors/!{firehose:error-output-type}/dt=!{timestamp:yyyy-MM-dd}/\",
    \"BufferingHints\":{\"SizeInMBs\":5,\"IntervalInSeconds\":60},
    \"CompressionFormat\":\"GZIP\"}"
aws firehose describe-delivery-stream --delivery-stream-name clicks-to-s3 \
  --query 'DeliveryStreamDescription.DeliveryStreamStatus'
```
Wait for `ACTIVE`.

*Step 4 — Producer (`producer.py`)*
```python
import json, random, time, uuid
from datetime import datetime, timezone
import boto3

kinesis = boto3.client("kinesis", region_name="ap-south-1")
PAGES = ["/home", "/product/1", "/product/2", "/cart", "/checkout"]

def make_event():
    return {"event_id": str(uuid.uuid4()),
            "user_id": random.randint(1, 50),
            "page": random.choice(PAGES),
            "ts": datetime.now(timezone.utc).isoformat()}

sent = 0
for batch in range(20):                       # 20 batches x 25 records = 500 events
    events = [make_event() for _ in range(25)]
    entries = [{"Data": (json.dumps(e) + "\n").encode(),
                "PartitionKey": str(e["user_id"])} for e in events]
    resp = kinesis.put_records(StreamName="clicks", Records=entries)
    failed = resp["FailedRecordCount"]
    if failed:
        retry = [r for r, res in zip(entries, resp["Records"]) if "ErrorCode" in res]
        kinesis.put_records(StreamName="clicks", Records=retry)
    sent += len(entries)
    time.sleep(1)
print("sent", sent, "events")
```

*Step 5 — Simple consumer (`consumer.py`) using `GetRecords`*
```python
import json, time, boto3
kinesis = boto3.client("kinesis", region_name="ap-south-1")
shards = kinesis.list_shards(StreamName="clicks")["Shards"]
it = kinesis.get_shard_iterator(StreamName="clicks",
        ShardId=shards[0]["ShardId"], ShardIteratorType="TRIM_HORIZON")["ShardIterator"]
total = 0
for _ in range(10):
    out = kinesis.get_records(ShardIterator=it, Limit=200)
    it = out["NextShardIterator"]
    for r in out["Records"]:
        evt = json.loads(r["Data"])
        total += 1
    print("batch:", len(out["Records"]), "behind(ms):", out["MillisBehindLatest"])
    time.sleep(1)
print("read", total, "events")
```

**7. Explanation of the code**
- The producer batches 25 events per `PutRecords` call, uses `user_id` as the partition key (so each user's events stay ordered), appends `\n` so S3 files contain newline-delimited JSON, and retries failed records.
- The stream has one shard, enough for this small load (1 MiB/s or 1,000 records/s).
- Firehose reads from the stream, buffers up to 5 MiB or 60 seconds, compresses with gzip and writes to `streaming/clicks/dt=YYYY-MM-DD/`.
- The consumer reads from `TRIM_HORIZON` (oldest) and prints `MillisBehindLatest` to show lag.

**8. Expected output**
```
sent 500 events
batch: 200 behind(ms): 0
batch: 200 behind(ms): 0
batch: 100 behind(ms): 0
read 500 events
```
After 1–2 minutes S3 contains files like `streaming/clicks/dt=2026-11-18/clicks-to-s3-1-2026-11-18-10-05-33-....gz`.

**9. Validation and testing**
```bash
aws s3 ls s3://$BUCKET/streaming/clicks/ --recursive
aws s3 cp s3://$BUCKET/streaming/clicks/dt=$(date -u +%F)/ . --recursive --exclude "*" --include "*.gz"
zcat *.gz | wc -l                      # should equal 500 events in total
aws cloudwatch get-metric-statistics --namespace AWS/Firehose --metric-name DeliveryToS3.Success \
  --dimensions Name=DeliveryStreamName,Value=clicks-to-s3 --start-time $(date -u -d '15 min ago' +%FT%TZ) \
  --end-time $(date -u +%FT%TZ) --period 300 --statistics Average
```
(`date -d` is GNU/Linux syntax; adjust on macOS.) You can also create an Athena JSON table on `streaming/clicks/` to query the events.

**10. Common errors and troubleshooting**
| Error | Cause | Fix |
|---|---|---|
| `ResourceNotFoundException` | Wrong stream name/Region | Check `--region` and names |
| `ProvisionedThroughputExceededException` | Too many writes/reads per shard | Add shards/EFO, batch, back off |
| Firehose `ACTIVE` but no S3 files | Buffer interval not reached, no data, or role lacks permissions | Wait 60–120 s; check role; check errors prefix and CloudWatch logs |
| Firehose creation fails on role | IAM propagation delay / trust policy | Wait and retry; verify trust principal `firehose.amazonaws.com` |
| Files contain concatenated JSON without newlines | Producer omitted `\n` | Append newline delimiters |

**11. Cost considerations and cleanup**
Delete promptly — shard-hours accrue even when idle:
```bash
aws firehose delete-delivery-stream --delivery-stream-name clicks-to-s3
aws kinesis delete-stream --stream-name clicks --enforce-consumer-deletion
aws iam delete-role-policy --role-name FirehoseClicksRole --policy-name access
aws iam delete-role --role-name FirehoseClicksRole
aws s3 rm s3://$BUCKET/streaming/ --recursive
```

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
