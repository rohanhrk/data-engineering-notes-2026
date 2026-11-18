# AWS Lambda — Data Engineering Study Notes (0–2 YOE)

> Self-contained notes: fundamentals → implementation → interview preparation.
> Lambda limits, runtimes and pricing change regularly (for example, payload limits and runtime versions have been updated in recent years). Confirm numbers on the quotas and pricing pages linked at the end.

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

### What is AWS Lambda?
**AWS Lambda** is a serverless compute service that runs your code (a **function**) in response to **events**, without you provisioning or managing servers. You upload code (or a container image), choose memory and timeout, and attach a trigger such as an S3 upload, an SQS message, a Kinesis record, an EventBridge schedule or an HTTP request through API Gateway. You pay for requests and execution time (billed in milliseconds, scaled by memory).

### Why was it introduced and what problem does it solve?
Before Lambda, even small tasks (resize an image, react to a file upload) required a running server or cron machine. Lambda removes idle capacity, patching and scaling work: it automatically runs as many copies of your function as there are events (within limits) and scales to zero when idle.

### Why is it important in Data Engineering?
Lambda is the **glue** of event-driven data pipelines: validating or routing files as they land in S3, transforming small records from queues/streams, starting Glue/EMR/Step Functions workflows, calling APIs for ingestion, and sending alerts. It is cheap, fast to build and integrates natively with S3, Kinesis, SQS, DynamoDB, EventBridge and Step Functions.

### When should you use it?
- Small to medium event-driven tasks that complete within 15 minutes.
- File validation/routing, lightweight transformations, enrichment via APIs.
- Triggering and orchestrating other services.
- Scheduled jobs (via EventBridge Scheduler) with short runtimes.
- Stream/queue consumers with modest per-record processing.

### When should you avoid it?
| Situation | Better option |
|---|---|
| Jobs running longer than 15 minutes | Glue, EMR, ECS/Fargate, Step Functions with chunking |
| Large-scale distributed transformations (GBs–TBs) | Glue/EMR (Spark) |
| Long-lived connections, stateful servers | ECS/EC2 |
| Predictable, constant heavy load with strict latency | Containers/EC2 may be cheaper |
| Heavy native/GPU workloads | Batch/ECS/SageMaker |

### Simple real-world example
A partner uploads `orders.csv` to S3. S3 triggers a Lambda that checks the header and row values; valid files are copied to `validated/` and invalid ones to `quarantine/`, with an entry saved in DynamoDB. No server runs when no files arrive.

### Brief comparison with alternatives
| | Lambda | Glue | ECS/Fargate | EC2 |
|---|---|---|---|---|
| Model | Event-driven functions | Serverless Spark ETL | Containers | Virtual servers |
| Max runtime | 15 min | Hours | Unlimited | Unlimited |
| Scale | Automatic per event | Per job | Service scaling | Manual/ASG |
| Best for | Small event tasks, glue logic | Big batch ETL | Long-running services/batch | Custom workloads |

---

## 2. Architecture and Working Mechanism

### Overall architecture
Lambda runs your code inside lightweight, isolated **execution environments** (Firecracker microVMs) managed by AWS. You define the function (code, runtime, handler, memory, timeout, role, environment variables, networking) and event sources. When an event arrives, Lambda finds or creates an execution environment and runs the handler; multiple events run in parallel in multiple environments up to the concurrency limit.

### Major components
- **Function** — code + configuration; versions and aliases for releases.
- **Runtime** — language environment (Python, Node.js, Java, .NET, Ruby, custom, or a container image).
- **Handler** — the entry point (e.g. `handler.lambda_handler`).
- **Event source / trigger** — what invokes the function.
- **Execution role** — IAM role Lambda assumes to call other AWS services.
- **Resource-based policy** — who may invoke the function (e.g. S3 service principal).
- **Layers** — shared libraries/dependencies.
- **Concurrency controls** — reserved and provisioned concurrency.
- **Destinations / DLQ** — handle failed asynchronous invocations.
- **CloudWatch Logs/Metrics/X-Ray** — observability.

### Invocation types
| Type | How | Examples | Retries |
|---|---|---|---|
| **Synchronous** | Caller waits for the response | API Gateway, SDK `RequestResponse` | Caller handles errors |
| **Asynchronous** | Lambda queues the event and returns immediately | S3, SNS, EventBridge | Lambda retries (default 2 retries) and can send failures to a DLQ/on-failure destination |
| **Poll-based (event source mapping)** | Lambda polls and invokes in batches | SQS, Kinesis, DynamoDB Streams, MSK | Retry behaviour depends on the source (stream shard blocks; SQS message returns after visibility timeout) |

### End-to-end flow (S3 upload example)
1. A file is uploaded to S3; S3 sends an event notification to Lambda (asynchronous invocation).
2. Lambda queues the event, finds a warm execution environment or creates one (**cold start**: download code, start runtime, run initialisation code outside the handler).
3. The handler runs with `event` and `context`, using the execution role to call S3/DynamoDB.
4. The result is returned; logs go to CloudWatch Logs; metrics (Invocations, Errors, Duration, Throttles, ConcurrentExecutions) are published.
5. The environment stays warm for a while and is reused for later invocations; otherwise it is frozen/terminated.
6. On errors Lambda retries (async) and, if retries are exhausted, delivers the event to a DLQ or on-failure destination.

### Mermaid architecture
```mermaid
flowchart LR
    S3["S3 upload"] -->|"async event"| L["Lambda function"]
    SQS["SQS queue"] -->|"event source mapping (poll)"| L
    KDS["Kinesis stream"] -->|"event source mapping (poll)"| L
    EB["EventBridge schedule"] -->|"async"| L
    API["API Gateway"] -->|"sync"| L
    L -->|"execution role"| DDB[("DynamoDB")]
    L --> S3O[("S3 outputs")]
    L --> SFN["Step Functions / Glue start"]
    L -. "failed async events" .-> DLQ["SQS DLQ / on-failure destination"]
    L --> CW["CloudWatch Logs and metrics"]
```

### Explanation of components
- **Triggers** differ in how they call Lambda (async, poll, sync) which determines retry behaviour.
- **Execution role** gives least-privilege access to downstream services.
- **DLQ/destination** stores events that still fail after retries.
- **CloudWatch** provides logs/metrics for debugging.

### Practical Data Engineering architecture
```mermaid
flowchart LR
    P["Partner uploads CSV"] --> LZ[("S3 incoming/")]
    LZ --> LV["Lambda: validate + route"]
    LV -->|"valid"| V[("S3 validated/")]
    LV -->|"invalid"| Q[("S3 quarantine/")]
    LV --> LED[("DynamoDB ledger")]
    V --> GL["Glue job (EventBridge rule)"]
    GL --> CUR[("S3 curated")]
    CUR --> ATH["Athena"]
```

---

## 3. Core Concepts and Important Terminologies

### 3.1 Functions, handlers and the programming model
- **Definition:** A function is your code plus configuration. In Python the handler receives `event` (JSON data from the trigger) and `context` (runtime info such as remaining time).
- **Best practice:** initialise SDK clients and read configuration **outside** the handler so warm invocations reuse them.
```python
import boto3, os
s3 = boto3.client("s3")                 # created once per execution environment
BUCKET = os.environ["BUCKET"]

def lambda_handler(event, context):
    print("remaining ms:", context.get_remaining_time_in_millis())
    return {"statusCode": 200, "body": "ok"}
```
- **Mistakes:** Creating clients inside the handler on every call; storing state in globals and assuming it persists (it may or may not).

### 3.2 Triggers and event sources
S3, SQS, SNS, Kinesis, DynamoDB Streams, MSK/Kafka, EventBridge (rules/scheduler), API Gateway/Function URLs, ALB, CloudWatch Logs subscriptions, Step Functions tasks and more. For each, understand the event shape (`event["Records"]` for S3/SQS/Kinesis) and the invocation type.

### 3.3 Execution role vs resource-based policy
- **Execution role:** what the function **can do** (call S3, DynamoDB, CloudWatch Logs) — trust policy for `lambda.amazonaws.com` + permission policies (e.g. `AWSLambdaBasicExecutionRole` for logs).
- **Resource-based (function) policy:** who **can invoke** the function (e.g. `s3.amazonaws.com` for a bucket, with `source-arn`/`source-account` conditions).
- **Mistakes:** adding an S3 trigger via CLI but forgetting `lambda add-permission`; granting `s3:*` on `*` to the role.

### 3.4 Memory, CPU, timeout and ephemeral storage
- **Memory:** 128 MB up to 10,240 MB; **CPU scales proportionally** with memory — more memory often means faster, sometimes cheaper, runs.
- **Timeout:** configurable up to 15 minutes (900 s).
- **Ephemeral storage (`/tmp`):** 512 MB default, configurable up to 10,240 MB; per execution environment, not persistent.
- **Billing:** requests + GB-seconds (memory × duration, per millisecond). Free tier includes monthly requests and GB-seconds (check pricing).
- **Mistake:** leaving the default 128 MB and 3-second timeout for data tasks; not using `context.get_remaining_time_in_millis()` for graceful exit.

### 3.5 Concurrency, scaling and throttling
- **Concurrency** = number of function instances processing events at the same time. Account-level default limit (typically 1,000 per Region, adjustable).
- **Reserved concurrency:** guarantees capacity for a function **and caps it** (protects downstream systems; also stops it from consuming the entire account pool).
- **Provisioned concurrency:** pre-warmed environments to avoid cold starts (costs extra).
- **Throttling:** when the limit is hit, sync callers get HTTP 429 (`TooManyRequestsException`); async events are retried for up to 6 hours; poll-based sources slow down.
- **SQS mapping:** configure `ScalingConfig.MaximumConcurrency` to cap concurrency from a queue.

### 3.6 Cold starts and warm starts
A **cold start** creates a new environment: download package, start runtime, run init code. It adds latency (tens of ms to seconds, depending on runtime, package size, VPC and init work). **Warm** invocations reuse an environment. Reduce cold starts by keeping packages small, lazy-loading heavy imports, using provisioned concurrency or SnapStart (supported runtimes) where latency matters. For batch/data pipelines cold starts rarely matter.

### 3.7 Asynchronous invocation, retries, DLQs and destinations
- Async invocations get **two retries by default** (configurable 0–2) with a maximum event age (default 6 hours, configurable down to 60 seconds). After that the event is discarded unless a **DLQ** (SQS/SNS) or **on-failure destination** (SQS, SNS, EventBridge, Lambda) is configured. **On-success destinations** can chain workflows.
```bash
aws lambda put-function-event-invoke-config --function-name validate-orders \
  --maximum-retry-attempts 1 --maximum-event-age-in-seconds 3600 \
  --destination-config '{"OnFailure":{"Destination":"arn:aws:sqs:ap-south-1:111122223333:validate-dlq"}}'
```
- **Mistake:** assuming failures are retried forever or that errors are visible without a DLQ/alarm.

### 3.8 Event source mappings: SQS and Kinesis
- **SQS:** Lambda polls the queue and sends batches; successful batches are deleted; on error messages reappear after the **visibility timeout** (set it to at least 6× the function timeout as AWS recommends) and may go to a queue DLQ after `maxReceiveCount`. Use **partial batch responses** (`ReportBatchItemFailures`) so only failed messages return.
- **Kinesis/DynamoDB Streams:** ordered per shard; a failing batch **blocks the shard** until success/expiry. Use `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds`, an on-failure destination and `ParallelizationFactor`.
```python
def handler(event, context):
    failures = []
    for r in event["Records"]:              # SQS records
        try:
            process(r["body"])
        except Exception:
            failures.append({"itemIdentifier": r["messageId"]})
    return {"batchItemFailures": failures}
```

### 3.9 Idempotency
Events may be delivered more than once (S3 notifications, async retries, SQS standard queues, stream retries). Make handlers **idempotent**: use natural keys, conditional writes (`attribute_not_exists`) to a DynamoDB ledger, upserts, or the **Powertools for AWS Lambda** idempotency utility.
```python
try:
    ddb.put_item(TableName="ledger",
                 Item={"file_id": {"S": file_id}},
                 ConditionExpression="attribute_not_exists(file_id)")
except ddb.exceptions.ConditionalCheckFailedException:
    return  # already processed
```

### 3.10 Environment variables, secrets and configuration
Environment variables (up to 4 KB total) configure behaviour; encrypt sensitive values with KMS or, better, fetch secrets from **Secrets Manager/Parameter Store** at init time and cache them. **Mistake:** hard-coding credentials or bucket names in code.

### 3.11 Layers, packaging and container images
- **Zip deployment** (up to 50 MB zipped via direct upload; 250 MB unzipped including layers) — dependencies must match the runtime architecture (x86_64 vs arm64) and OS (Amazon Linux).
- **Layers** share libraries (e.g. the **AWS SDK for pandas** managed layer provides pandas/pyarrow).
- **Container images** up to 10 GB for large dependencies.
- **Mistake:** building native wheels on macOS/Windows and getting `ImportModuleError` in Lambda.

### 3.12 Versions, aliases and deployment
Publish immutable **versions**; use **aliases** (`prod`, `dev`) to route traffic and enable weighted canary releases. Use IaC (SAM/CloudFormation/Terraform/CDK) for repeatable deployment.

### 3.13 VPC access
Place a function in a VPC (subnets + security groups) to reach private resources (RDS). Then it needs a route to AWS services (NAT gateway or VPC endpoints for S3/DynamoDB/etc.). **Mistake:** function in a private subnet without NAT/endpoint times out calling S3.

### 3.14 Observability
CloudWatch Logs (`print`/`logging`), metrics (`Invocations`, `Errors`, `Duration`, `Throttles`, `ConcurrentExecutions`, `IteratorAge` for streams), X-Ray tracing, Lambda Insights. Use structured JSON logs with correlation IDs. Alarm on `Errors`, `Throttles` and DLQ depth.

### 3.15 Lambda in orchestration
Step Functions invokes Lambda tasks (and handles retries/branching); EventBridge Scheduler triggers scheduled runs; Lambda can start Glue jobs (`glue.start_job_run`), EMR steps, or Athena queries — typical orchestration glue.

---

## 4. Data Engineering Use Cases

### Real-world use cases
- File arrival processing: validate, rename, partition-route, catalog update.
- API ingestion on a schedule (pull data from SaaS APIs to S3).
- Lightweight stream/queue transformations and enrichment.
- Triggering Glue/EMR/Step Functions pipelines.
- Data quality checks and notifications.
- Metadata/ledger maintenance (DynamoDB, Glue Catalog partitions).

### Batch processing
EventBridge schedules Lambda to call a REST API each hour and store JSON in S3; Lambda starts a Glue job after files arrive; Lambda adds new partitions to the Glue Catalog (`glue.batch_create_partition`).

### Real-time / streaming
Kinesis → Lambda for per-record transforms and writes to DynamoDB/OpenSearch; SQS → Lambda for buffered, rate-controlled processing; DynamoDB Streams → Lambda for change propagation.

### Pipeline example 1 — File-triggered ingestion
```mermaid
flowchart LR
    U["Upload to S3 incoming/"] --> L["Lambda validate"]
    L --> V[("validated/")]
    L --> Q[("quarantine/")]
    V --> EB["EventBridge rule"]
    EB --> G["Glue ETL job"]
    G --> C[("curated Parquet")]
```

### Pipeline example 2 — API ingestion on a schedule
```mermaid
flowchart LR
    SCH["EventBridge Scheduler: every hour"] --> L["Lambda: call API, paginate"]
    L --> RAW[("S3 raw/api/dt=.../hour=.../")]
    L --> SM["Secrets Manager: API key"]
    L -. "failure" .-> SNS["SNS alert"]
```

### Why a Data Engineer chooses Lambda
Minimal ops, automatic scaling, pay-per-use, easy event integration, and fast iteration. Choose it for small, short tasks and orchestration glue; use Glue/EMR for big distributed processing, and Fargate for longer-running containers.

---

## 5. Hands-on Implementation

### Mini-project: Event-driven CSV validation and routing with an idempotency ledger

**1. Objective:** Build an S3-triggered Lambda that validates incoming CSV files, routes them to `validated/` or `quarantine/`, and records each file in DynamoDB to avoid duplicate processing.

**2. Business problem:** Partners upload order files at unpredictable times. Bad files must not reach the lake; duplicate S3 events must not cause duplicate work.

**3. Architecture**
```mermaid
flowchart LR
    U["aws s3 cp orders.csv"] --> IN[("s3://bucket/incoming/")]
    IN -- "ObjectCreated (.csv)" --> L["Lambda validate-orders"]
    L --> LED[("DynamoDB ingest_ledger")]
    L -->|"valid"| VAL[("validated/orders/ingest_date=...")]
    L -->|"invalid"| QUA[("quarantine/ + reason json")]
    L --> CW["CloudWatch Logs"]
```

**4. Prerequisites and setup**
- The S3 bucket from the S3 notes; AWS CLI; Python 3.
- Variables: `ACCOUNT`, `REGION`, `BUCKET`.
- **Costs:** Lambda free tier covers this lab; DynamoDB on-demand costs pennies; S3 negligible. Notification setup below **replaces** any existing bucket notification configuration — use a test bucket if unsure.

**5–6. Implementation and code**

*Step 1 — DynamoDB ledger table*
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=ap-south-1
BUCKET=retail-datalake-$ACCOUNT-$REGION
aws dynamodb create-table --table-name ingest_ledger \
  --attribute-definitions AttributeName=file_id,AttributeType=S \
  --key-schema AttributeName=file_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region $REGION
```

*Step 2 — Execution role*
```bash
cat > lambda-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
cat > lambda-perms.json <<EOF
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:GetObject"],"Resource":"arn:aws:s3:::$BUCKET/incoming/*"},
 {"Effect":"Allow","Action":["s3:PutObject"],
  "Resource":["arn:aws:s3:::$BUCKET/validated/*","arn:aws:s3:::$BUCKET/quarantine/*"]},
 {"Effect":"Allow","Action":["dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:DeleteItem"],
  "Resource":"arn:aws:dynamodb:$REGION:$ACCOUNT:table/ingest_ledger"}]}
EOF
aws iam create-role --role-name ValidateOrdersRole --assume-role-policy-document file://lambda-trust.json
aws iam attach-role-policy --role-name ValidateOrdersRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam put-role-policy --role-name ValidateOrdersRole --policy-name data-access --policy-document file://lambda-perms.json
```

*Step 3 — Function code `handler.py`*
```python
import csv, io, json, os, urllib.parse
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
ddb = boto3.client("dynamodb")
TABLE = os.environ["LEDGER_TABLE"]
REQUIRED = ["order_id", "customer_id", "amount", "order_date"]

def validate(text):
    """Return (ok, reason, row_count)."""
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or any(c not in reader.fieldnames for c in REQUIRED):
        return False, f"missing columns; expected {REQUIRED}", 0
    n = 0
    for i, row in enumerate(reader, start=2):
        n += 1
        try:
            if not row["order_id"]:
                raise ValueError("empty order_id")
            if float(row["amount"]) <= 0:
                raise ValueError("amount must be > 0")
            datetime.strptime(row["order_date"], "%Y-%m-%d")
        except Exception as e:
            return False, f"line {i}: {e}", n
    if n == 0:
        return False, "no data rows", 0
    return True, "ok", n

def process_record(rec):
    bucket = rec["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(rec["s3"]["object"]["key"])
    version = rec["s3"]["object"].get("versionId") or rec["s3"]["object"].get("eTag", "")
    file_id = f"{bucket}/{key}#{version}"

    # Idempotency: claim the file; skip if already claimed
    try:
        ddb.put_item(TableName=TABLE,
                     Item={"file_id": {"S": file_id}, "status": {"S": "PROCESSING"}},
                     ConditionExpression="attribute_not_exists(file_id)")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(json.dumps({"msg": "duplicate event skipped", "file_id": file_id}))
            return
        raise

    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        ok, reason, rows = validate(body)
        name = key.split("/")[-1]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if ok:
            dest = f"validated/orders/ingest_date={today}/{name}"
            s3.put_object(Bucket=bucket, Key=dest, Body=body.encode())
        else:
            dest = f"quarantine/{today}/{name}"
            s3.put_object(Bucket=bucket, Key=dest, Body=body.encode())
            s3.put_object(Bucket=bucket, Key=dest + ".reason.json",
                          Body=json.dumps({"file": key, "reason": reason}).encode())
        ddb.update_item(TableName=TABLE, Key={"file_id": {"S": file_id}},
                        UpdateExpression="SET #s = :s, dest = :d, #r = :r",
                        ExpressionAttributeNames={"#s": "status", "#r": "rows"},
                        ExpressionAttributeValues={":s": {"S": "VALID" if ok else "INVALID"},
                                                   ":d": {"S": dest}, ":r": {"N": str(rows)}})
        print(json.dumps({"file_id": file_id, "valid": ok, "reason": reason, "dest": dest}))
    except Exception:
        # release the claim so a retry can process the file again
        ddb.delete_item(TableName=TABLE, Key={"file_id": {"S": file_id}})
        raise

def lambda_handler(event, context):
    for rec in event["Records"]:
        process_record(rec)
```

*Step 4 — Deploy*
```bash
zip function.zip handler.py
sleep 10   # IAM propagation
aws lambda create-function --function-name validate-orders --runtime python3.12 \
  --role arn:aws:iam::$ACCOUNT:role/ValidateOrdersRole --handler handler.lambda_handler \
  --zip-file fileb://function.zip --timeout 60 --memory-size 256 \
  --environment "Variables={LEDGER_TABLE=ingest_ledger}" --region $REGION
```
(Pick a currently supported Python runtime; `python3.12` is an example.)

*Step 5 — Allow S3 to invoke the function and add the trigger*
```bash
aws lambda add-permission --function-name validate-orders --statement-id s3invoke \
  --action lambda:InvokeFunction --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::$BUCKET --source-account $ACCOUNT

FN_ARN=$(aws lambda get-function --function-name validate-orders --query Configuration.FunctionArn --output text)
aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration "{
  \"LambdaFunctionConfigurations\": [{
    \"LambdaFunctionArn\": \"$FN_ARN\",
    \"Events\": [\"s3:ObjectCreated:*\"],
    \"Filter\": {\"Key\": {\"FilterRules\": [
      {\"Name\":\"prefix\",\"Value\":\"incoming/\"},{\"Name\":\"suffix\",\"Value\":\".csv\"}]}}}]}"
```

*Step 6 — Test with a good and a bad file*
```bash
printf 'order_id,customer_id,amount,order_date\nA1,1,10.5,2026-11-18\nA2,2,20.0,2026-11-18\n' > good.csv
printf 'order_id,customer_id,amount,order_date\nB1,1,-5,2026-11-18\n' > bad.csv
aws s3 cp good.csv s3://$BUCKET/incoming/good.csv
aws s3 cp bad.csv  s3://$BUCKET/incoming/bad.csv
sleep 15
aws logs tail /aws/lambda/validate-orders --since 5m
```

**7. Explanation of the code**
- Clients are created outside the handler (reused when warm).
- The function **claims** each file by a conditional `PutItem`; duplicate S3 notifications hit the condition and are skipped (idempotency). If processing fails, the claim is deleted so Lambda's retry can reprocess.
- `validate` checks columns, numeric amount, date format and empties.
- Valid files go to `validated/orders/ingest_date=.../`; invalid ones to `quarantine/` with a reason file. Output prefixes differ from the trigger prefix `incoming/`, preventing infinite loops.

**8. Expected output**
CloudWatch logs:
```
{"file_id": "<bucket>/incoming/good.csv#<etag>", "valid": true, "reason": "ok", "dest": "validated/orders/ingest_date=2026-11-18/good.csv"}
{"file_id": "<bucket>/incoming/bad.csv#<etag>", "valid": false, "reason": "line 2: amount must be > 0", "dest": "quarantine/2026-11-18/bad.csv"}
```

**9. Validation and testing**
```bash
aws s3 ls s3://$BUCKET/validated/ --recursive
aws s3 ls s3://$BUCKET/quarantine/ --recursive
aws dynamodb scan --table-name ingest_ledger --region $REGION
aws lambda invoke --function-name validate-orders --payload '{"Records":[]}' --cli-binary-format raw-in-base64-out out.json
```
Re-upload the same file name and content: since the ETag matches the existing ledger entry, you should see "duplicate event skipped". (If you overwrite with different content a new ETag creates a new ledger entry.)

**10. Common errors and troubleshooting**
| Error | Cause | Fix |
|---|---|---|
| Nothing happens after upload | Missing `add-permission`, wrong prefix/suffix, notification not saved | Check Lambda trigger/policy and `get-bucket-notification-configuration` |
| `AccessDenied` in logs | Execution role missing S3/DynamoDB permission | Update role policy |
| `Task timed out after 60.00 seconds` | Large file/slow call | Increase timeout/memory or stream/chunk |
| `Unable to import module 'handler'` | Handler name/zip layout wrong | Ensure `handler.py` at zip root and handler `handler.lambda_handler` |
| `ConditionalCheckFailedException` printed as error | Not handled | Catch as in code |

**11. Cost considerations and cleanup**
Within free tier for this lab; DynamoDB on-demand costs are tiny. Remove:
```bash
aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration '{}'
aws lambda delete-function --function-name validate-orders
aws dynamodb delete-table --table-name ingest_ledger
aws iam delete-role-policy --role-name ValidateOrdersRole --policy-name data-access
aws iam detach-role-policy --role-name ValidateOrdersRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name ValidateOrdersRole
aws logs delete-log-group --log-group-name /aws/lambda/validate-orders
aws s3 rm s3://$BUCKET/incoming/ --recursive; aws s3 rm s3://$BUCKET/validated/ --recursive; aws s3 rm s3://$BUCKET/quarantine/ --recursive
```

