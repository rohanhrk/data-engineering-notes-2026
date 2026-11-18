---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is AWS Lambda and how does its billing/scaling model work?**
Lambda runs your function code in response to events with no servers to manage. It scales automatically by creating more execution environments as events arrive (up to account/function concurrency limits) and scales to zero when idle. Billing is per request plus duration (milliseconds × configured memory, i.e. GB-seconds), with a monthly free tier. More memory also gives proportionally more CPU. *Keywords: serverless, event-driven, execution environment, concurrency, GB-seconds, 15-minute max.* It suits short, event-driven data tasks; heavy long-running ETL belongs in Glue/EMR.

**Q2. Explain the Lambda execution environment lifecycle and cold starts.**
When there's no warm environment, Lambda performs **init**: downloads code, starts the runtime and runs code outside the handler (cold start). Then it runs the handler (**invoke**). The environment is reused for later invocations (warm) until it is frozen/recycled. Cold-start time depends on runtime, package size, VPC networking and initialisation work. Mitigation: keep packages small, lazy-load heavy libraries, reuse clients created outside the handler, use provisioned concurrency or SnapStart where latency-critical. In batch pipelines, cold starts are usually insignificant.

**Q3. What are the three invocation models (sync, async, poll-based) and how do retries differ?**
Sync: the caller waits (API Gateway, SDK) and handles errors itself. Async: Lambda queues the event and returns 202 (S3, SNS, EventBridge); Lambda retries failures (default two retries, configurable) and can send failed events to a DLQ or on-failure destination after retries or max event age. Poll-based event source mappings (SQS, Kinesis, DynamoDB Streams, MSK): Lambda polls and invokes with batches; for SQS failed messages become visible again after the visibility timeout; for streams a failing batch blocks that shard until success or record expiry unless you configure bisect/retries/destinations.

**Q4. What are Lambda's key limits and configuration knobs?**
Memory 128 MB–10,240 MB (CPU scales with memory); timeout up to 900 s; ephemeral `/tmp` 512 MB–10,240 MB; synchronous payload up to 6 MB request/response; asynchronous event payload limited (historically 256 KB — AWS has increased it in 2025, check the current quota); deployment package 50 MB zipped (direct upload)/250 MB unzipped, container images up to 10 GB; environment variables up to 4 KB; default account concurrency 1,000 per Region (soft limit). Know these exist, but quote current values from the quotas page in an interview.

**Q5. Explain reserved concurrency vs provisioned concurrency.**
**Reserved concurrency** sets aside a portion of the account's concurrency pool for a function *and* acts as its maximum — useful to guarantee capacity or to protect a downstream database from too many parallel invocations. **Provisioned concurrency** keeps a number of execution environments initialised and ready so invocations avoid cold starts (extra cost). A function can use both: reserved defines the cap; provisioned pre-warms part of it. When all concurrency is used, new invocations are throttled (429 for sync, retried for async).

**Q6. How does Lambda process SQS messages and what is a partial batch response?**
Lambda polls the queue with multiple pollers and sends batches (up to the configured batch size, with an optional batching window). If the function returns success the whole batch is deleted; if it throws, **all messages** in the batch become visible again after the visibility timeout, causing reprocessing of already successful items. With `ReportBatchItemFailures` the function returns `batchItemFailures` listing only failed message IDs, so successes are deleted and only failures retry. Also set visibility timeout ≥ function timeout (AWS recommends 6×), configure a DLQ on the queue and a max concurrency to protect downstream systems.

**Q7. What permissions are involved in S3 → Lambda?**
Two sides: the **resource-based policy on the function** allowing `s3.amazonaws.com` to invoke it (with `SourceArn` of the bucket and `SourceAccount` to prevent confused deputy), and the **execution role** that lets the function read/write S3, DynamoDB, etc., plus CloudWatch Logs. The bucket's notification configuration points to the function ARN with event types and prefix/suffix filters. Missing the resource policy is the commonest reason a trigger silently doesn't fire when configured via CLI/IaC (the console adds it automatically).

**Q8. How do you handle dependencies: layers, packages and container images?**
Small pure-Python dependencies can be zipped with the code; shared or large libraries can go into **layers** (up to five per function, counted in the 250 MB unzipped limit); AWS provides managed layers such as the AWS SDK for pandas (pandas/pyarrow). Compiled dependencies must be built for Amazon Linux and the correct architecture (x86_64 or arm64). For very large dependencies (ML libraries) use **container images** (up to 10 GB). Common failure: building wheels on a laptop OS and seeing import errors in Lambda.

**Q9. What is idempotency and how do you implement it in Lambda?**
Idempotent processing means handling the same event more than once yields the same result. Needed because S3 notifications, async retries, SQS standard queues and stream retries can deliver duplicates. Implementations: use a stable key (bucket+key+version/ETag, message ID) with a conditional DynamoDB write (`attribute_not_exists`) as a ledger/lock; make downstream writes upserts or overwrite deterministic paths; use the Powertools for AWS Lambda idempotency utility. Also handle partial failures by releasing/expiring the claim so retries can proceed.

**Q10. What are Lambda best practices for data engineering workloads?**
Initialise clients outside the handler; keep functions single-purpose and small; set appropriate memory/timeout (use power tuning to find the cost/performance sweet spot); least-privilege roles; environment variables/Secrets Manager for config; structured logging and alarms (`Errors`, `Throttles`, DLQ depth, `IteratorAge`); make handlers idempotent; use DLQs/destinations; limit concurrency to protect downstream systems; avoid long synchronous waits (use Step Functions); don't process huge files in memory — stream or delegate to Glue/EMR; deploy via IaC with versions/aliases.

### B. Scenario-Based Questions (5)

**S1. A Lambda must process a 20 GB CSV landing in S3 but times out at 15 minutes.**
*Problem:* size/time exceed Lambda's limits. *Solution:* hand off to a service built for large data: S3 event → Lambda starts a **Glue job** (or EMR Serverless) which processes the file in Spark; alternatively split the file into chunks (S3 byte-range reads + Step Functions Distributed Map) to process in parallel Lambdas. Lambda remains the lightweight trigger/validator. *Why:* right tool for volume. *Alternatives:* ECS/Fargate task for sequential processing. *Trade-off:* Glue has startup time and cost per run; chunking adds orchestration complexity.

**S2. Each S3 upload sometimes triggers the function twice, creating duplicate output rows.**
*Problem:* at-least-once event delivery. *Solution:* make the function idempotent: derive a key from `bucket/key/versionId` or ETag and perform a conditional put in DynamoDB before processing; write outputs to deterministic paths/overwrite; use upserts downstream. Add alarms on duplicates skipped. *Why:* duplicates cannot be eliminated at the source. *Alternatives:* route events through SQS FIFO with deduplication IDs, or use EventBridge with idempotent consumers. *Trade-off:* extra DynamoDB call per event and need for TTL cleanup.

**S3. An SQS-triggered Lambda scales out and overwhelms your RDS database with connections.**
*Solution:* limit concurrency: set **maximum concurrency** on the SQS event source mapping and/or **reserved concurrency** on the function; use **RDS Proxy** for connection pooling; reduce batch frequency; make queries efficient. *Why:* Lambda scales faster than databases. *Alternatives:* move writes to a data store designed for high concurrency (DynamoDB), batch writes. *Trade-off:* lower concurrency raises queue latency; SQS holds the backlog.

**S4. A Kinesis-triggered Lambda stops advancing; `IteratorAge` rises.**
*Problem:* a poison record repeatedly fails and blocks the shard. *Solution:* enable `BisectBatchOnFunctionError`, set `MaximumRetryAttempts` and `MaximumRecordAgeInSeconds`, configure an on-failure destination (SQS/SNS) for failed batches, return partial batch failures, validate input and handle exceptions per record, and alarm on `IteratorAge`. *Why:* isolates the bad record so the rest of the shard flows. *Alternatives:* skip bad records to a DLQ in code. *Trade-off:* you must reprocess records from the DLQ and accept possible out-of-order handling.

**S5. Costs for a data-validation Lambda are higher than expected and runtime is long.**
*Solution:* tune memory — more memory gives more CPU and can reduce duration enough to lower cost (use AWS Lambda Power Tuning or test several sizes); consider arm64 (Graviton) where supported; reduce package/init time; avoid unnecessary reads (use S3 ranges/streaming); batch operations; filter events upstream (S3 prefix/suffix, SQS batching). *Why:* cost = memory × duration. *Alternatives:* move steady heavy loads to Fargate/Glue. *Trade-off:* tuning effort and risk of under-sizing causing timeouts.

### C. Troubleshooting Questions (3)

**T1. Logs show `Task timed out after X seconds` or `Runtime exited with error: signal: killed` (out of memory).**
*Root causes:* work exceeds the timeout; downstream API/database slow; large file loaded entirely into memory; VPC networking without NAT/endpoint (hanging connections); insufficient memory (max memory used equals configured). *Debug approach:* CloudWatch `Duration` vs timeout; the `REPORT` log line shows `Max Memory Used`; add timing logs around calls; check VPC route/NAT; test with smaller input. *Fix:* increase timeout/memory; stream data in chunks; add connection/read timeouts with retries; fix networking (VPC endpoints for S3/DynamoDB or NAT); offload to Glue/Step Functions when the job can't fit.

**T2. `Unable to import module` / `ImportModuleError` or "No module named pandas/numpy".**
*Root causes:* dependency not packaged; zip structure wrong (handler not at root; layer packages must be under `python/`); wheels built for a different OS/architecture; mismatch between function runtime/architecture and layer; package exceeds size limits. *Debug:* test locally with the same Python version; inspect the zip (`unzip -l`); verify the layer's compatible runtime/architecture. *Fix:* build dependencies in Amazon Linux or with `pip install --platform manylinux2014_x86_64 --only-binary=:all: -t python/`; use the AWS SDK for pandas managed layer or a container image; ensure the handler path is `file.function`.

**T3. The trigger exists but the function isn't invoked (S3/EventBridge) or is throttled.**
*Root causes:* missing `lambda:InvokeFunction` permission for the source; wrong event type or prefix/suffix filter; notification configured in a different Region/bucket; concurrency limit reached (429 `Throttles`); function disabled or reserved concurrency set to 0; event source mapping disabled/failing; destination/DLQ misconfigured. *Debug:* `aws lambda get-policy`; `aws s3api get-bucket-notification-configuration`; EventBridge rule metrics and target configuration; CloudWatch `Invocations`, `Throttles`, `ConcurrentExecutions`; event source mapping state (`aws lambda list-event-source-mappings`). *Fix:* add the missing resource policy (`add-permission`), correct filters, raise reserved/account concurrency, enable the mapping, test by invoking manually with a sample event (`aws lambda invoke`).

---

## 7. Revision and Quick Reference

### Key takeaways
- Lambda = event-driven, serverless functions; scale automatically; pay per request and GB-second.
- Know invocation types and their retry behaviour.
- Idempotency, DLQs/destinations and concurrency control are essential for data pipelines.
- Use Lambda for small/fast tasks and orchestration glue; Glue/EMR for heavy ETL.

### Commonly forgotten details
- Max timeout 15 minutes; CPU scales with memory.
- Create clients outside the handler; `/tmp` isn't persistent across environments.
- S3 trigger needs a function resource policy (`add-permission`) — the CLI doesn't add it automatically.
- Writing back to the triggering prefix causes infinite loops.
- Async retries default to 2; failures disappear without DLQ/destination.
- SQS: visibility timeout should exceed the function timeout; use partial batch responses.
- Stream failures block the shard.
- VPC functions need NAT or VPC endpoints.
- Layers/zips count toward the 250 MB unzipped limit.

### Important commands and syntax
```bash
aws lambda create-function --function-name f --runtime python3.12 --role <arn> --handler app.handler --zip-file fileb://f.zip
aws lambda update-function-code --function-name f --zip-file fileb://f.zip
aws lambda update-function-configuration --function-name f --timeout 120 --memory-size 512 --environment "Variables={K=V}"
aws lambda invoke --function-name f --payload '{"a":1}' --cli-binary-format raw-in-base64-out out.json
aws lambda add-permission --function-name f --statement-id s3 --action lambda:InvokeFunction --principal s3.amazonaws.com --source-arn <bucket-arn>
aws lambda put-function-concurrency --function-name f --reserved-concurrent-executions 10
aws lambda create-event-source-mapping --function-name f --event-source-arn <queue-arn> --batch-size 10
aws logs tail /aws/lambda/f --follow
```
```python
def lambda_handler(event, context):
    # event["Records"] for S3/SQS/Kinesis; context.get_remaining_time_in_millis()
    return {"statusCode": 200}
```

### Frequently used configurations
Memory/timeout, environment variables, execution role, reserved/provisioned concurrency, event source mapping (`BatchSize`, `MaximumBatchingWindowInSeconds`, `ReportBatchItemFailures`, `ScalingConfig`), async config (`MaximumRetryAttempts`, `MaximumEventAgeInSeconds`, destinations), DLQ, VPC settings, architecture (x86_64/arm64), layers, aliases/versions.

### Common errors and solutions
| Error | Solution |
|---|---|
| `Task timed out` | Increase timeout/memory, optimise, offload |
| `AccessDeniedException` | Fix execution role/resource policy |
| `TooManyRequestsException` (429) | Increase concurrency limits, add queue buffering |
| `ImportModuleError` | Package dependencies correctly/layers/container |
| `Runtime exited ... killed` | Increase memory or stream data |
| Trigger not firing | `add-permission`, filters, same Region |
| Duplicate processing | Idempotency ledger |

### Service limitations
15-minute max duration; payload limits; limited ephemeral storage; no persistent local state; cold starts; concurrency limits per Region; package size limits; not ideal for heavy distributed compute or long-running connections; check the current quotas page.

### Performance and cost optimisation
Right-size memory (power tuning); arm64 where supported; reuse connections; batch event sources; filter events at source; reduce package size; provisioned concurrency only where required; avoid polling inside functions; use VPC endpoints instead of NAT for S3/DynamoDB to cut data processing charges.

### Security best practices
Least-privilege execution roles per function; resource policies with `SourceArn/SourceAccount`; secrets in Secrets Manager/Parameter Store (not plaintext env vars); encrypt env vars with KMS; VPC only when needed; code signing and image scanning; restrict function URLs/auth; log without sensitive data.

### Connections with other AWS services
S3, SQS, SNS, Kinesis, DynamoDB (+Streams), EventBridge/Scheduler, API Gateway, Step Functions, Glue/EMR/Athena (start jobs/queries), Secrets Manager/Parameter Store, KMS, CloudWatch/X-Ray, VPC/RDS Proxy.

### Quick revision cheat sheet
```
Trigger -> (sync | async | poll) -> Lambda (init once, invoke many) -> role -> services
Limits: 15 min, 128MB-10GB RAM (CPU scales), /tmp up to 10GB, 6MB sync payload
Async: retry x2 -> DLQ/destination ; SQS: partial batch + visibility timeout ; Streams: bisect, max age
Concurrency: account pool; reserved (cap+guarantee); provisioned (no cold start)
Idempotent: conditional write ledger
```

### 10 rapid-fire revision questions
1. **Maximum Lambda timeout?** 15 minutes (900 seconds).
2. **What increases CPU for a function?** Configuring more memory.
3. **Default async retry count?** Two retries.
4. **Where do you create SDK clients?** Outside the handler (init code).
5. **Which policy lets S3 invoke Lambda?** The function's resource-based policy.
6. **What stops a function from exceeding N parallel runs?** Reserved concurrency.
7. **What pre-warms environments?** Provisioned concurrency.
8. **How to avoid reprocessing successful SQS messages?** Partial batch response (`ReportBatchItemFailures`).
9. **Can Lambda keep local state between invocations reliably?** No.
10. **What do you use for failed async events?** DLQ or on-failure destination.

---

## Official AWS documentation
- AWS Lambda Developer Guide — https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- Lambda quotas — https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
- Asynchronous invocation — https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html
- Event source mappings — https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html
- Using Lambda with S3 — https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html
- Using Lambda with SQS — https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- Using Lambda with Kinesis — https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html
- Concurrency — https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html
- Lambda pricing — https://aws.amazon.com/lambda/pricing/
- Powertools for AWS Lambda (Python) — https://docs.powertools.aws.dev/lambda/python/latest/
- Boto3 Lambda reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
