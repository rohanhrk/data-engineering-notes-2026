# Amazon EMR — Data Engineering Study Notes (0–2 YOE)

> Self-contained notes: fundamentals → implementation → interview preparation.
> EMR release labels, application versions, instance types and pricing change frequently. Use a currently supported release from the EMR Release Guide (the `emr-7.x` placeholder below is an example) and confirm details in the docs linked at the end.

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

### What is Amazon EMR?
**Amazon EMR** (formerly Elastic MapReduce) is a managed big data platform that runs open-source frameworks — **Apache Spark, Hadoop (HDFS, YARN, MapReduce), Hive, Presto/Trino, HBase, Flink** and more — on AWS. You can run EMR in three ways:

| Deployment option | What you get |
|---|---|
| **EMR on EC2** | A cluster of EC2 instances (primary, core, task nodes) that EMR provisions, configures and monitors |
| **EMR Serverless** | No clusters: create an *application*, submit *job runs*; EMR provisions and scales workers automatically |
| **EMR on EKS** | Run Spark jobs on an existing Amazon EKS (Kubernetes) cluster |

### Why was it introduced and what problem does it solve?
Setting up Hadoop/Spark clusters is difficult: installing software, tuning configurations, handling failed nodes, scaling. EMR (launched in 2009) automates provisioning and configuration so you can start a cluster in minutes and pay per second. Because data can live in **S3** rather than inside the cluster, you can create clusters only when needed and delete them afterwards.

### Why is it important in Data Engineering?
EMR is the AWS home of **large-scale Spark and Hadoop processing**. It is used when you need more control or lower cost than Glue for big, long-running, or specialised jobs: custom Spark configurations, special libraries, Hive/Presto, HBase, Spot-based cost optimisation, or migrating existing on-premises Hadoop workloads.

### When should you use it?
- Large batch ETL (hundreds of GB to PB) with Spark.
- Migrating Hadoop/Hive/Spark jobs from on-premises with minimal rewrite.
- Workloads that need control over cluster size, instance types, Spot usage, Spark/Hadoop configuration or non-Spark engines.
- Interactive analytics/notebooks (EMR Studio) on big data.

### When should you avoid it?
| Situation | Better option |
|---|---|
| Small/medium ETL and you want minimum ops | AWS Glue |
| Ad hoc SQL on S3 | Athena |
| Warehouse-style BI with many concurrent users | Redshift |
| Tiny event-driven tasks | Lambda |
| Team with no cluster tuning skills and sporadic jobs | EMR Serverless or Glue |

### Simple real-world example
Every night a transient EMR cluster starts, runs a Spark job that reads 2 TB of clickstream Parquet from S3, aggregates it and writes results back to S3, then terminates itself. The company pays for a few hours of compute instead of a 24/7 cluster.

### Brief comparison with alternatives
| | EMR | Glue | Databricks | Dataproc (GCP) |
|---|---|---|---|---|
| Model | Managed clusters or Serverless/EKS | Serverless Spark ETL | Managed lakehouse platform | Managed Spark/Hadoop |
| Control | High (instance types, configs, software) | Medium | High | High |
| Ops effort | Medium (EC2) / Low (Serverless) | Lowest | Medium | Medium |
| Cost levers | Spot, Graviton, transient clusters | Worker count, Flex | DBU + cloud | Preemptible VMs |
| Best for | Custom/large big data | Standard ETL + Catalog | Collaborative lakehouse/ML | Same role on GCP |

---

## 2. Architecture and Working Mechanism

### Overall architecture (EMR on EC2)
An EMR cluster contains three node types:
- **Primary node (master):** coordinates the cluster, runs YARN ResourceManager, HDFS NameNode, web UIs and, with Spark in cluster mode, often the Spark driver application master.
- **Core nodes:** run tasks **and** store HDFS data (DataNode + NodeManager).
- **Task nodes (optional):** run tasks only (no HDFS), ideal for Spot instances and elastic scaling.

**YARN** allocates cluster CPU/memory as containers to applications; Spark executors run inside YARN containers. Persistent data usually lives in **S3** accessed through **EMRFS** (`s3://`), while HDFS on instance/EBS storage is for temporary intermediate data and is lost when the cluster terminates.

### EMR Serverless architecture
You create an **application** (type Spark or Hive, release label, optional pre-initialised capacity, auto start/stop). Each **job run** executes with an **execution role**; EMR provisions workers (drivers/executors) on demand and releases them after the job. No nodes to manage.

### Major components
- **Release label** (e.g. `emr-7.x.y`) — a bundle of compatible application versions.
- **Applications** — Spark, Hive, Hadoop, Presto/Trino, HBase, Flink, Livy, Jupyter, etc.
- **Steps** — units of work submitted to a cluster (e.g. `spark-submit`).
- **Bootstrap actions** — scripts run on each node at startup (install libraries).
- **Instance groups/fleets** — how node capacity is defined.
- **Managed scaling / auto scaling** — adjusts nodes with workload.
- **EMR Studio / notebooks** — interactive development.
- **Glue Data Catalog integration** — shared Hive metastore.
- **IAM roles** — service role, EC2 instance profile, (Serverless: job execution role).
- **Logs** — to S3 (`--log-uri`), plus CloudWatch/Spark History Server.

### End-to-end flow (EMR on EC2 transient cluster)
1. You (or an orchestrator) call `RunJobFlow`/`aws emr create-cluster` with release, applications, instance configuration, steps and log location.
2. EMR launches EC2 instances in your VPC subnet, runs bootstrap actions, installs applications and starts YARN/HDFS daemons.
3. Cluster state moves to `RUNNING`; steps execute (e.g. `spark-submit` through `command-runner.jar`).
4. Executors read input from S3 via EMRFS, process data in parallel, shuffle between nodes, and write results to S3.
5. After steps complete, the cluster terminates automatically (`--auto-terminate`) or waits for more work (`WAITING`).
6. Logs are archived to S3; you pay per second of EC2 + EMR charges while running.

### Mermaid — EMR on EC2 cluster
```mermaid
flowchart LR
    ORCH["Step Functions / MWAA / CLI"] --> API["EMR service API"]
    API --> PRI["Primary node: YARN RM, NameNode"]
    PRI --> CORE["Core nodes: HDFS + tasks"]
    PRI --> TASK["Task nodes (Spot): tasks only"]
    CORE <--> S3[("S3 via EMRFS")]
    TASK <--> S3
    PRI --> LOGS[("S3 logs")]
    CAT[("Glue Data Catalog")] -.-> PRI
```

### Mermaid — EMR Serverless
```mermaid
flowchart LR
    SUB["start-job-run"] --> APP["EMR Serverless application"]
    APP --> DRV["Driver worker"]
    APP --> EXE["Executor workers (auto-scaled)"]
    EXE <--> S3[("S3 data and scripts")]
    DRV --> LOG[("S3 / CloudWatch logs")]
```

### Explanation of components
- **Primary/core/task** — control plane, storage+compute, elastic compute.
- **S3 + EMRFS** — durable storage separate from cluster life.
- **Glue Catalog** — shared table metadata with Athena/Glue.
- **Serverless application/job run** — compute created on demand with an execution role.
- **Logs on S3** — essential because cluster nodes disappear.

### Practical Data Engineering architecture
```mermaid
flowchart LR
    RAW[("S3 raw")] --> EMR["EMR Spark job (transient cluster or Serverless)"]
    EMR --> CUR[("S3 curated Parquet + Glue Catalog")]
    CUR --> ATH["Athena"]
    CUR --> RS["Redshift Spectrum / COPY"]
    SF["Step Functions: create cluster -> add step -> terminate"] --> EMR
    CW["CloudWatch alarms -> SNS"] -.-> EMR
```

---

## 3. Core Concepts and Important Terminologies

### 3.1 Cluster lifecycle: transient vs long-running
- **Transient cluster:** created for a job and terminated when done (`--auto-terminate`). Cheapest for scheduled batch.
- **Long-running cluster:** stays up for interactive use, streaming or frequent jobs; needs scaling, patching and monitoring.
- **States:** `STARTING` → `BOOTSTRAPPING` → `RUNNING` → `WAITING` → `TERMINATING` → `TERMINATED` (or `TERMINATED_WITH_ERRORS`).
- **Mistake:** forgetting termination on a transient cluster (continued billing); keeping data only in HDFS.

### 3.2 Node types and what runs where
| Node | Runs | Data | Spot-safe? |
|---|---|---|---|
| Primary | Resource manager, NameNode, web UIs | Metadata | No (single point; use on-demand) |
| Core | NodeManager + DataNode | HDFS blocks | Risky (losing core loses HDFS data) |
| Task | NodeManager only | None | Yes — ideal |
Use **on-demand** for primary and core, **Spot** for task nodes (diversified instance types).

### 3.3 Storage: HDFS vs EMRFS (S3) vs EBS/instance store
- **HDFS:** distributed file system on core nodes; fast, but ephemeral and sized by the cluster.
- **EMRFS/S3:** durable, cheap, decoupled — **store inputs/outputs in S3** so clusters can be deleted.
- **Instance store/EBS:** local disks hosting HDFS, Spark shuffle and temp data; size EBS volumes appropriately.
- **Mistake:** relying on HDFS for final data; undersized disks causing "No space left on device".

### 3.4 YARN and Spark on EMR
- **YARN** schedules containers across NodeManagers. Spark runs on YARN with a **driver** (coordinates) and **executors** (workers).
- **Deploy mode:** `cluster` (driver on a core/task node — recommended for steps, survives submitter disconnect) vs `client` (driver where submitted, e.g. primary node/notebook).
- **Executor sizing:** pick cores/memory per executor to fit instance capacity (leave memory for OS/YARN/overhead). `maximizeResourceAllocation` classification can auto-configure Spark based on instance type; **dynamic allocation** (default on EMR) scales executors with workload.
```bash
spark-submit --deploy-mode cluster \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.executor.memory=8g --conf spark.executor.cores=4 \
  s3://my-lake/scripts/job.py s3://my-lake/curated/orders/ s3://my-lake/aggregates/orders/
```

### 3.5 Steps and bootstrap actions
- **Step:** a unit of work run on the cluster, e.g. a Spark application via `command-runner.jar`. `ActionOnFailure` can be `CANCEL_AND_WAIT`, `CONTINUE`, or `TERMINATE_CLUSTER`.
- **Bootstrap action:** script executed on every node at launch (install Python packages, configure OS). Runs before applications start.
```bash
aws emr add-steps --cluster-id j-XXXX --steps \
  Type=Spark,Name=orders-agg,ActionOnFailure=CONTINUE,\
Args=[--deploy-mode,cluster,s3://my-lake/scripts/orders_agg.py,s3://my-lake/curated/orders/,s3://my-lake/aggregates/orders/]
```
- **Mistake:** installing packages in the step instead of bootstrap/packaged environment (slow/failing); bootstrap scripts that fail and block cluster startup.

### 3.5b Creating a classic EMR on EC2 cluster (CLI)
```bash
aws emr create-default-roles     # creates EMR_DefaultRole and EMR_EC2_DefaultRole (once)

aws emr create-cluster --name "orders-batch" \
  --release-label emr-7.5.0 \                # example: use a current emr-7.x release
  --applications Name=Spark \
  --instance-groups \
    InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m5.xlarge \
    InstanceGroupType=CORE,InstanceCount=2,InstanceType=m5.xlarge \
    InstanceGroupType=TASK,InstanceCount=2,InstanceType=m5.xlarge,Market=SPOT \
  --use-default-roles --log-uri s3://my-lake/emr-logs/ \
  --auto-terminate \
  --steps Type=Spark,Name=orders-agg,ActionOnFailure=TERMINATE_CLUSTER,Args=[--deploy-mode,cluster,s3://my-lake/scripts/orders_agg.py,s3://my-lake/curated/orders/,s3://my-lake/aggregates/orders/]
```
(Instance types and availability vary by Region; the cluster needs a subnet — the default VPC is used if not specified. Verify syntax with `aws emr create-cluster help`.)

### 3.6 Instance groups vs instance fleets
- **Instance groups:** one instance type per group (simple).
- **Instance fleets:** up to several instance types per node role with a **target capacity** mixing on-demand and Spot units; EMR picks available capacity — improves Spot availability and cost.
- **Mistake:** a single Spot instance type in one AZ → capacity failures.

### 3.7 Scaling: managed scaling and auto scaling
- **EMR managed scaling:** EMR automatically resizes the cluster (within min/max you set) based on workload metrics, optimising for core/task mix.
- **Custom auto scaling policies** (instance groups): CloudWatch-metric rules.
- **Serverless:** automatic scale-out/in per job; optional **pre-initialised capacity** for fast start.
- **Mistake:** scaling core nodes down (HDFS decommissioning delays) instead of task nodes.

### 3.8 Spot instances best practices
Use Spot for **task nodes**; keep primary/core on-demand; diversify instance types/AZs (fleets); use shorter jobs/checkpointing; allow graceful decommissioning; accept interruptions with Spark's retry behaviour; set max Spot price at on-demand cap. Savings can be large but jobs must tolerate node loss.

### 3.9 EMR Serverless essentials
- **Application:** type (Spark/Hive), release label, architecture, network config (optional VPC), pre-initialised capacity, `autoStart`/`autoStop` (idle timeout), max capacity limits.
- **Job run:** `sparkSubmit` entry point + args + Spark parameters; run under an **execution role**; logs to S3/CloudWatch.
- **Billing:** per vCPU-hour, memory GB-hour and storage while workers run.
- **Why it matters:** no cluster management, great for intermittent jobs. **Limits:** less low-level control, some applications/config unsupported — check docs.
```bash
aws emr-serverless create-application --name retail-spark --type SPARK \
  --release-label emr-7.5.0 \
  --auto-stop-configuration '{"enabled":true,"idleTimeoutMinutes":5}'
```

### 3.10 EMR on EKS (know the idea)
Run Spark jobs as pods on EKS using **virtual clusters** mapped to Kubernetes namespaces; useful when your organisation standardises on Kubernetes and wants shared, multi-tenant capacity.

### 3.11 Glue Data Catalog as Hive metastore
EMR can use the Glue Data Catalog for Spark/Hive/Presto metadata so tables are shared with Athena and Glue. Enable via the cluster configuration classification (`spark-hive-site`: `hive.metastore.client.factory.class=com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory`) or console option.

### 3.12 Security: roles, encryption, networking
- **EMR service role** (EMR_DefaultRole): lets EMR manage EC2/other resources.
- **EC2 instance profile** (EMR_EC2_DefaultRole): permissions of code running on nodes (access S3/Glue/DynamoDB). Restrict it to least privilege; EMRFS can map different S3 roles per user/prefix.
- **Security configuration:** encryption at rest (EBS/local disk/S3 with SSE/CSE) and in transit (TLS), Kerberos.
- **Network:** run in private subnets; use VPC endpoints for S3; security groups; **EMR Block Public Access**.
- **Serverless:** execution role defines job permissions.

### 3.13 Logging and debugging
- Cluster logs to S3 (`--log-uri`): `steps/<id>/stderr.gz`, `controller.gz`, `containers/application_*/container_*/stderr.gz`.
- **Spark History Server** and YARN ResourceManager UIs (via persistent app UI or SSH tunnel/EMR console links).
- CloudWatch metrics (YARN memory available, HDFS utilisation, apps running).
- **Mistake:** not enabling log URI, then losing logs when the cluster terminates.

### 3.14 Performance optimisation checklist
- Use **Parquet/ORC** with snappy/zstd; partition by common filters; avoid tiny files (compact).
- Use the **EMRFS S3-optimized committer** (default for Spark on recent releases) for faster, safer S3 writes.
- Enable **adaptive query execution (AQE)** for skew/partition coalescing; broadcast small tables.
- Right-size executors/partitions; avoid collecting data to the driver; cache only reused data.
- Use Graviton instances for price-performance where supported; keep compute in the same Region/AZ as S3 and use a S3 gateway endpoint.

---

## 4. Data Engineering Use Cases

### Real-world use cases
- Large-scale ETL/ELT from raw to curated lake tables.
- Hive/Presto SQL on big data; Hadoop workload migrations.
- Feature engineering and large-scale ML preprocessing.
- Log processing and clickstream sessionisation.
- Streaming with Spark Structured Streaming or Flink on long-running clusters.
- Interactive analysis with EMR Studio notebooks.

### Batch processing
Orchestrator creates a transient cluster (or submits an EMR Serverless job), runs Spark steps reading S3, writes partitioned Parquet back, registers partitions, and terminates. Backfills are parameterised reruns.

### Real-time / streaming
Spark Structured Streaming or Flink on a long-running EMR cluster consuming Kinesis/MSK, writing to S3/Iceberg/OpenSearch. For fully managed alternatives consider Managed Service for Apache Flink or Glue streaming.

### Pipeline example 1 — Nightly transient cluster
```mermaid
flowchart LR
    EB["EventBridge 01:00"] --> SF["Step Functions"]
    SF --> C["Create EMR cluster (Spot task nodes)"]
    C --> S1["Step 1: Spark ETL"]
    S1 --> S2["Step 2: data quality checks"]
    S2 --> T["Terminate cluster"]
    S1 --> OUT[("S3 curated")]
    S2 -- "failure" --> SNS["SNS alert"]
```

### Pipeline example 2 — Hadoop migration
```mermaid
flowchart LR
    ONP["On-prem HDFS / Hive"] -- "S3DistCp / DataSync / Snowball" --> S3[("S3 data lake")]
    S3 --> EMR["EMR Hive/Spark jobs (existing code)"]
    EMR --> S3O[("S3 results")]
    GCAT["Glue Data Catalog (migrated metastore)"] -.-> EMR
    S3O --> ATH["Athena / BI"]
```

### Why a Data Engineer chooses EMR
Control over software and hardware, strong cost optimisation (Spot, Graviton, transient clusters), compatibility with open-source ecosystems and existing Hadoop/Hive jobs, and scale to petabytes. Choose Glue for simple serverless ETL, Athena for ad hoc SQL, Redshift for warehouse BI.

---

## 5. Hands-on Implementation

### Mini-project: Aggregate daily revenue with a PySpark job on EMR Serverless

**1. Objective:** Run a PySpark job on **EMR Serverless** that reads partitioned Parquet orders from S3, computes daily revenue/orders/customers and writes Parquet results back to S3.

**2. Business problem:** The business wants a daily revenue summary generated by a scalable Spark job without managing clusters; jobs run intermittently so serverless billing fits.

**3. Architecture**
```mermaid
flowchart LR
    SCR[("s3://bucket/scripts/orders_agg.py")] --> JOB["EMR Serverless job run"]
    CUR[("s3://bucket/curated/orders/ Parquet")] --> JOB
    JOB --> OUT[("s3://bucket/aggregates/emr_daily_revenue/")]
    JOB --> LOG[("s3://bucket/emr-logs/")]
    ROLE["Execution role"] -. assumed .-> JOB
```

**4. Prerequisites and setup**
- The S3 bucket and curated Parquet from the S3 notes (`curated/orders/order_date=.../part-0000.parquet`).
- Permissions to create IAM roles and EMR Serverless applications.
- Variables: `ACCOUNT`, `REGION`, `BUCKET`, and `RELEASE` — a currently supported EMR release label (EMR Serverless supports EMR releases 6.6.0 and above; check the docs, e.g. `emr-7.5.0`).
- **Costs:** EMR Serverless charges per vCPU-hour/GB-hour while workers run (a small job costs cents) plus S3. The application stops when idle if auto-stop is enabled. Delete everything afterwards.

**5–6. Implementation and code**

*Step 1 — PySpark script `orders_agg.py`*
```python
import sys
from pyspark.sql import SparkSession, functions as F

if len(sys.argv) != 3:
    raise SystemExit("usage: orders_agg.py <input_path> <output_path>")
src, dst = sys.argv[1], sys.argv[2]

spark = SparkSession.builder.appName("orders-daily-revenue").getOrCreate()

df = spark.read.parquet(src)             # partition column order_date is discovered from folders
print("Input rows:", df.count())

daily = (df.groupBy("order_date")
           .agg(F.round(F.sum("amount"), 2).alias("revenue"),
                F.count("*").alias("orders"),
                F.countDistinct("customer_id").alias("customers"))
           .orderBy("order_date"))

daily.show(truncate=False)
daily.coalesce(1).write.mode("overwrite").parquet(dst)    # small result: one file
spark.stop()
```
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=ap-south-1
BUCKET=retail-datalake-$ACCOUNT-$REGION
RELEASE=emr-7.5.0          # example; choose a supported release
aws s3 cp orders_agg.py s3://$BUCKET/scripts/orders_agg.py
```

*Step 2 — Job execution role*
```bash
cat > emrs-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"emr-serverless.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
cat > emrs-perms.json <<EOF
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:GetObject","s3:ListBucket"],
  "Resource":["arn:aws:s3:::$BUCKET","arn:aws:s3:::$BUCKET/scripts/*","arn:aws:s3:::$BUCKET/curated/*"]},
 {"Effect":"Allow","Action":["s3:PutObject","s3:GetObject","s3:DeleteObject"],
  "Resource":["arn:aws:s3:::$BUCKET/aggregates/*","arn:aws:s3:::$BUCKET/emr-logs/*"]}]}
EOF
aws iam create-role --role-name EmrServerlessJobRole --assume-role-policy-document file://emrs-trust.json
aws iam put-role-policy --role-name EmrServerlessJobRole --policy-name s3-access --policy-document file://emrs-perms.json
ROLE_ARN=arn:aws:iam::$ACCOUNT:role/EmrServerlessJobRole
```

*Step 3 — Create and start the application*
```bash
APP_ID=$(aws emr-serverless create-application --name retail-spark --type SPARK \
  --release-label $RELEASE \
  --auto-stop-configuration '{"enabled":true,"idleTimeoutMinutes":5}' \
  --query applicationId --output text)
aws emr-serverless start-application --application-id $APP_ID
aws emr-serverless get-application --application-id $APP_ID --query application.state
```
Wait until the state is `STARTED`.

*Step 4 — Submit the job run*
```bash
JOB_ID=$(aws emr-serverless start-job-run --application-id $APP_ID \
  --execution-role-arn $ROLE_ARN --name orders-daily-revenue \
  --job-driver "{
    \"sparkSubmit\": {
      \"entryPoint\": \"s3://$BUCKET/scripts/orders_agg.py\",
      \"entryPointArguments\": [\"s3://$BUCKET/curated/orders/\", \"s3://$BUCKET/aggregates/emr_daily_revenue/\"],
      \"sparkSubmitParameters\": \"--conf spark.executor.cores=2 --conf spark.executor.memory=4g --conf spark.executor.instances=2 --conf spark.driver.cores=2 --conf spark.driver.memory=4g\"
    }}" \
  --configuration-overrides "{\"monitoringConfiguration\":{\"s3MonitoringConfiguration\":{\"logUri\":\"s3://$BUCKET/emr-logs/\"}}}" \
  --query jobRunId --output text)

# poll until a terminal state
while true; do
  S=$(aws emr-serverless get-job-run --application-id $APP_ID --job-run-id $JOB_ID --query jobRun.state --output text)
  echo "state: $S"; [[ "$S" =~ ^(SUCCESS|FAILED|CANCELLED)$ ]] && break; sleep 15
done
```

**7. Explanation of the code**
- The script reads the partitioned Parquet directory; Spark discovers `order_date` from folder names, groups by date and computes revenue, order count and distinct customers. `coalesce(1)` writes one small output file (don't do this for large outputs).
- The execution role (trusted by `emr-serverless.amazonaws.com`) grants read access to the script and data and write access to outputs and logs — least privilege by prefix.
- The application auto-stops after 5 idle minutes to avoid charges. `sparkSubmitParameters` size one driver and two executors for this tiny job.

**8. Expected output**
Job run ends in `SUCCESS`. The driver log (`stdout`) shows:
```
Input rows: 200
+----------+-------+------+---------+
|order_date|revenue|orders|customers|
+----------+-------+------+---------+
|2026-11-15|12345.67|50   |18       |
...
```
(Values depend on your generated data.) An output Parquet file appears under `aggregates/emr_daily_revenue/`.

**9. Validation and testing**
```bash
aws s3 ls s3://$BUCKET/aggregates/emr_daily_revenue/ --recursive
aws s3 ls s3://$BUCKET/emr-logs/applications/$APP_ID/jobs/$JOB_ID/ --recursive
aws s3 cp s3://$BUCKET/emr-logs/applications/$APP_ID/jobs/$JOB_ID/SPARK_DRIVER/stdout.gz - | gunzip | head -30
```
Cross-check the totals with the Athena or Glue results from earlier notes — the numbers should match. Rerun the job; output is overwritten (idempotent).

**10. Common errors and troubleshooting**
| Error | Cause | Fix |
|---|---|---|
| Job `FAILED`: `AccessDenied` on S3 | Execution role missing prefixes | Update role policy for script/data/output/log paths |
| `ValidationException` on release label | Unsupported/misspelled release | Use a supported `emr-x.y.z` label |
| Application stays `CREATED`/won't start | Capacity/limits or network config | Check application `stateDetails`, service quotas, subnets if VPC configured |
| `Path does not exist` | Wrong input path/prefix | Verify S3 paths; ensure data exists |
| Job cancelled for exceeding limits | Maximum capacity/timeouts | Adjust application maximum capacity/job timeout |

**11. Cost considerations and cleanup**
Workers are billed while jobs run; stopped applications do not incur compute charges (storage of pre-initialised capacity would). Clean up:
```bash
aws emr-serverless stop-application --application-id $APP_ID
# wait until STOPPED, then:
aws emr-serverless delete-application --application-id $APP_ID
aws iam delete-role-policy --role-name EmrServerlessJobRole --policy-name s3-access
aws iam delete-role --role-name EmrServerlessJobRole
aws s3 rm s3://$BUCKET/aggregates/emr_daily_revenue/ --recursive
aws s3 rm s3://$BUCKET/emr-logs/ --recursive
aws s3 rm s3://$BUCKET/scripts/orders_agg.py
```

**Optional extension:** run the same script as a step on a transient EMR on EC2 cluster using the `create-cluster` command in section 3.5b and compare startup time, control and cost. Remember to terminate the cluster (`--auto-terminate`) and delete logs.

---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is Amazon EMR and which deployment options exist?**
EMR is a managed platform for running big data frameworks (Spark, Hadoop/Hive, Presto/Trino, HBase, Flink) on AWS. Options: **EMR on EC2** (clusters with primary, core, task nodes you configure), **EMR Serverless** (create an application and submit job runs; EMR provisions workers automatically), and **EMR on EKS** (Spark jobs on Kubernetes). EMR handles provisioning, configuration, monitoring and integration with S3, Glue, IAM and CloudWatch. *Keywords: managed Hadoop/Spark, transient clusters, EMRFS, YARN, Spot.* Use it for large or customised processing; Glue for simpler serverless ETL.

**Q2. Explain primary, core and task nodes.**
The **primary node** runs cluster coordination (YARN ResourceManager, HDFS NameNode) and web UIs; one per cluster (a multi-primary option exists for high availability). **Core nodes** run YARN NodeManagers and **store HDFS data**; scaling them down needs HDFS decommissioning and losing them risks data. **Task nodes** run only compute (no HDFS) so they can be added/removed or run on **Spot** safely. Best practice: on-demand for primary and core, Spot for task nodes, and keep durable data in S3.

**Q3. HDFS vs EMRFS/S3 — where should data live?**
HDFS is cluster-local, ephemeral and sized by the nodes; it's fast for iterative intermediate data. EMRFS lets Hadoop/Spark read/write S3 as a file system (`s3://`), giving durable, cheap, unlimited storage that outlives the cluster and is shared with Athena/Glue/Redshift. Modern EMR designs keep **inputs and outputs in S3** and use HDFS/local disks only for temporary shuffle data. This enables transient clusters and independent scaling of compute and storage. Mention S3 consistency is strong, and the S3-optimised committer for safe writes.

**Q4. How do steps and bootstrap actions differ? What are transient vs long-running clusters?**
A **step** is a unit of work submitted to a running cluster, e.g. `spark-submit` via `command-runner.jar`, with `ActionOnFailure` controlling what happens on failure. A **bootstrap action** is a script run on every node before applications start (install libraries/OS tweaks). A **transient** cluster is created for a batch run and terminates after its steps (cost-efficient, no idle time); a **long-running** cluster remains for interactive/streaming/frequent workloads and needs scaling and maintenance. Use IaC/Step Functions to create and terminate clusters per job.

**Q5. How does Spark run on YARN in EMR? What is deploy mode?**
Spark requests containers from YARN: one for the application master/driver and others for executors. In **cluster mode** the driver runs inside the cluster (on a core/task node), so the job continues if the submitting client disconnects — recommended for production steps. In **client mode** the driver runs where you submit (primary node/notebook) — good for interactive sessions but ties the job to the client. EMR enables **dynamic allocation** by default, and `maximizeResourceAllocation` can set executor sizes from instance types. Right-size executors (cores/memory) to fit nodes with overhead.

**Q6. How does EMR scaling work?**
EMR **managed scaling** adjusts the cluster size between configured minimum/maximum limits automatically, intelligently balancing core and task nodes (and Spot vs on-demand) based on metrics like YARN memory and containers pending. Older **custom auto scaling policies** use CloudWatch-based rules per instance group. **Instance fleets** let you mix instance types and purchase options for capacity. **EMR Serverless** scales workers per job automatically, with optional pre-initialised capacity. Caveats: scaling down core nodes is slow; ensure applications tolerate nodes leaving.

**Q7. How do you use Spot instances safely on EMR?**
Run **task nodes on Spot** and keep primary/core on-demand; use **instance fleets** to diversify instance types and AZs so EMR can find capacity; set reasonable timeouts and use Spark's task retry/graceful decommissioning; avoid long single-stage tasks that lose too much work on interruption; for critical SLA jobs, mix on-demand capacity. Savings can reach large percentages but plan for interruptions and "insufficient capacity" cases with fallback to on-demand. Monitor Spot interruption rates and job duration.

**Q8. Explain EMR security: roles, networking and encryption.**
Roles: the **EMR service role** (EMR manages resources), the **EC2 instance profile** (permissions for code on nodes — scope to needed S3/Glue/KMS), and for Serverless the **job execution role**. Networking: launch in private subnets, use security groups and S3 gateway endpoints, enable **EMR Block Public Access**. Data protection: **security configurations** for at-rest (S3 SSE/CSE, EBS/local disk encryption) and in-transit (TLS) encryption, Kerberos for authentication, Lake Formation for fine-grained catalog access, CloudTrail/log auditing. Avoid broad `s3:*` on instance profiles.

**Q9. How do you monitor and debug an EMR job?**
Enable the S3 **log URI**, then inspect step logs (`controller`, `stderr`, `stdout`) and container logs for Spark executors. Use the **Spark History Server**/YARN ResourceManager UI (persistent app UIs) to check stages, skew, shuffle spill and failed tasks; CloudWatch metrics for YARN memory, HDFS utilisation and running apps; EMR console step status. For Serverless use job run logs in S3/CloudWatch and the Spark UI link. Common root causes: executor memory limits, skew, disk full, S3 permissions, bad inputs.

**Q10. What are the main performance and cost optimisation techniques on EMR?**
Performance: Parquet/ORC + partitioning, compaction of small files, AQE and broadcast joins, proper executor sizing and shuffle partitions, S3-optimised committer, local compute near S3, avoiding driver collects, Graviton instances. Cost: transient clusters, EMR Serverless for intermittent jobs, Spot task nodes, managed scaling with sensible min/max, right-sized instances, shutting down idle clusters, reserved/Savings Plans for steady use, S3 lifecycle for logs and intermediates. Measure with job duration, resource utilisation and cost per run.

### B. Scenario-Based Questions (5)

**S1. A 24/7 EMR cluster running a nightly 2-hour Spark job costs thousands per month.**
*Problem:* paying for idle capacity. *Solution:* switch to **transient clusters** orchestrated by Step Functions/MWAA (create → run step → terminate) with Spot task nodes and managed scaling; or use **EMR Serverless** if the job tolerates serverless constraints. Store all data and scripts in S3, ship logs to S3, parameterise runs by date. *Why:* billing only during the 2 hours. *Alternatives:* Glue if the job is simple. *Trade-off:* cluster startup time (minutes) and orchestration setup; interactive users need a separate shared cluster/EMR Studio.

**S2. Spark jobs intermittently fail when Spot task nodes are reclaimed.**
*Problem:* losing nodes mid-stage. *Solution:* keep core nodes on-demand; use **instance fleets** with several instance types/AZs; enable Spark retry (`spark.task.maxFailures`, stage retries), use external shuffle/graceful decommissioning settings available in EMR, split long tasks into smaller partitions, checkpoint intermediate results to S3 for long pipelines, and set an on-demand fallback or a mix (e.g. 30% on-demand) for SLAs. *Why:* reduces blast radius of interruptions. *Alternatives:* Serverless to avoid managing Spot. *Trade-off:* higher cost with more on-demand.

**S3. Migrate an on-premises Hadoop cluster (500 TB in HDFS, Hive jobs) to AWS.**
*Solution:* land data in **S3** using DataSync/Snowball/S3DistCp over Direct Connect; migrate the Hive metastore to the **Glue Data Catalog**; run existing Hive/Spark jobs on EMR with minimal changes pointing to `s3://` paths; decouple compute so clusters are transient; validate with data checksums and job output comparisons; later modernise to Parquet/Iceberg and Athena. *Why:* S3 replaces HDFS as the durable store and enables elasticity. *Alternatives:* lift HDFS onto EMR HDFS (costly, loses decoupling). *Trade-off:* initial transfer time and testing for S3 semantics (rename costs, listing) and committers.

**S4. A Spark join job fails with executor OOM and one task runs far longer than others.**
*Problem:* data skew on the join key. *Solution:* enable AQE skew handling (`spark.sql.adaptive.skewJoin.enabled`), broadcast the small side if possible, **salt** the hot keys, increase `spark.sql.shuffle.partitions`, filter early, use larger executors (memory) for that stage, and examine the Spark UI for the skewed key. *Why:* a few huge partitions overload single executors; adding nodes alone doesn't fix it. *Alternatives:* pre-aggregate or split hot keys into a separate path. *Trade-off:* salting complicates logic and increases data size for the small side.

**S5. A small team with occasional (weekly) Spark jobs asks whether to use Glue, EMR on EC2 or EMR Serverless.**
*Recommendation:* start with **Glue** (lowest ops, integrated catalog) if jobs are standard and fit its limits; choose **EMR Serverless** if they need specific Spark versions/configurations, libraries or Hive but still want no clusters; choose EMR on EC2 only if they need cluster-level control, special frameworks (HBase, Presto) or very large steady workloads where Spot/Reserved capacity lowers cost. *Why:* ops overhead should match job frequency. *Alternatives:* Databricks if they want a collaborative platform. *Trade-off:* Glue/Serverless give less low-level tuning than EC2 clusters.

### C. Troubleshooting Questions (3)

**T1. The cluster is stuck in `STARTING`/`BOOTSTRAPPING` or terminates with errors immediately.**
*Root causes:* bootstrap action failing or taking too long; subnet without capacity or wrong AZ for instance type (`INSUFFICIENT_INSTANCE_CAPACITY`); service quota limits on instances/vCPUs; invalid security group/VPC settings or missing route to S3 (bootstrap scripts can't download); IAM service role/instance profile missing or lacking permissions; invalid release label or application configuration JSON. *Debug approach:* `aws emr describe-cluster --cluster-id j-XXXX --query Cluster.Status.StateChangeReason`; read the bootstrap action logs in S3 (`node/<instance>/bootstrap-actions/`); check EC2 capacity/quotas in the console; verify roles with `aws emr create-default-roles` or the proper custom roles; ensure subnet has S3 access (endpoint/NAT). *Fix:* correct the failing script/permissions, choose different instance types/AZ or use instance fleets, raise quotas, fix the config.

**T2. A Spark step fails: `ExecutorLostFailure`, "Container killed by YARN for exceeding memory limits" or `java.lang.OutOfMemoryError`.**
*Root causes:* executor memory/overhead too small; skewed partitions; too few shuffle partitions causing huge partitions; large broadcast; Python (PySpark) memory beyond JVM settings; cores per executor too high leading to memory pressure; Spot loss. *Debug:* step `stderr` and container logs; Spark UI stage details (task time distribution, spill); YARN diagnostics message; check partition sizes. *Fix:* increase `spark.executor.memory` and `spark.executor.memoryOverhead` (or `spark.executor.memoryOverhead` for PySpark), reduce executor cores, increase `spark.sql.shuffle.partitions`, enable AQE, repartition by a better key, avoid collecting large data on the driver, use larger instance types.
```bash
spark-submit --conf spark.executor.memory=8g --conf spark.executor.memoryOverhead=2g \
  --conf spark.sql.shuffle.partitions=800 --conf spark.sql.adaptive.enabled=true job.py
```

**T3. Jobs fail with "No space left on device", unhealthy nodes, or S3 `AccessDenied`/slow writes.**
*Root causes:* undersized EBS/instance storage for shuffle/spill or HDFS (nodes marked unhealthy by YARN at ~90% disk); logs/temp files filling disks; the EC2 instance profile or Serverless execution role lacks S3/KMS permissions; S3 request throttling (`503 SlowDown`) from too many small files/high request rates; wrong bucket Region. *Debug:* CloudWatch `HDFSUtilization` and YARN `UnhealthyNodes`; `df -h` via SSM/SSH; step logs for the exact exception; check the instance-profile policy (`aws iam simulate-principal-policy`); S3 request metrics. *Fix:* increase EBS volume size/instance types, clean temp data, reduce shuffle volume, store outputs in S3; fix IAM/KMS permissions; reduce file counts, use the S3-optimised committer and spread prefixes; keep cluster and bucket in the same Region.

---

## 7. Revision and Quick Reference

### Key takeaways
- EMR = managed Spark/Hadoop ecosystem on EC2, Serverless or EKS.
- Keep data in S3 (EMRFS); use HDFS only for temporary data.
- Transient clusters + Spot task nodes + managed scaling = cost efficiency.
- Primary/core on-demand; task nodes Spot.
- Logs to S3 and Spark History Server for debugging.

### Commonly forgotten details
- Always set a log URI before the cluster terminates.
- `--auto-terminate` for transient clusters; otherwise billing continues.
- EMR needs both a service role and an EC2 instance profile (Serverless uses an execution role).
- Core node loss = HDFS data loss risk; don't put critical data only in HDFS.
- Bootstrap failures stop cluster creation.
- Default `cluster` deploy mode for production steps.
- EMR Serverless apps stop when idle only if auto-stop is enabled.
- Spark's `coalesce(1)` on big outputs is a bottleneck.

### Important commands and syntax
```bash
aws emr create-default-roles
aws emr create-cluster --name n --release-label emr-7.x.y --applications Name=Spark \
  --instance-groups InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m5.xlarge InstanceGroupType=CORE,InstanceCount=2,InstanceType=m5.xlarge \
  --use-default-roles --log-uri s3://b/logs/ --auto-terminate --steps Type=Spark,Name=s,Args=[...]
aws emr list-clusters --active
aws emr describe-cluster --cluster-id j-XXXX
aws emr add-steps --cluster-id j-XXXX --steps Type=Spark,Name=s,ActionOnFailure=CONTINUE,Args=[--deploy-mode,cluster,s3://b/job.py]
aws emr terminate-clusters --cluster-ids j-XXXX
aws emr-serverless create-application --name a --type SPARK --release-label emr-7.x.y
aws emr-serverless start-job-run --application-id <id> --execution-role-arn <arn> --job-driver '{"sparkSubmit":{...}}'
aws emr-serverless get-job-run --application-id <id> --job-run-id <jr>
```

### Frequently used configurations
Release label; instance groups/fleets; managed scaling min/max; Spot allocation strategy; `maximizeResourceAllocation`; Spark: `spark.executor.memory/cores/memoryOverhead`, `spark.sql.shuffle.partitions`, `spark.sql.adaptive.enabled`; Glue Catalog metastore classification; security configuration; EBS volume size; log URI; Serverless: auto-stop idle timeout, pre-initialised capacity, max capacity.

### Common errors and solutions
| Error | Solution |
|---|---|
| Cluster fails at bootstrap | Fix script/permissions/network to S3 |
| `INSUFFICIENT_INSTANCE_CAPACITY` | Other instance types/AZs, instance fleets |
| Executor memory exceeded | Tune memory/overhead, partitions, AQE |
| `No space left on device` | Bigger EBS/instance, reduce spill |
| `AccessDenied` on S3 | Fix instance profile/execution role/KMS |
| Spot interruption failures | On-demand core, diversified fleets, retries |

### Service limitations
Cluster start takes minutes; HDFS is ephemeral; you manage tuning on EC2; EMR Serverless has fewer knobs and supports specific applications/releases; vCPU/instance quotas; security group/subnet constraints; software versions tied to release labels.

### Performance and cost optimisation
Parquet/ORC; partitioning/compaction; AQE; broadcast; right-size executors; Graviton; Spot task nodes; managed scaling; transient clusters; Serverless for intermittent jobs; clean up logs/intermediate data; monitor cost per run.

### Security best practices
Private subnets and endpoints; least-privilege instance profile/execution roles; security configuration for encryption; Kerberos/Lake Formation where required; EMR Block Public Access; restrict SSH, prefer SSM; patch via new releases; audit with CloudTrail.

### Connections with other AWS services
S3/EMRFS, Glue Data Catalog, IAM/KMS, Lake Formation, Athena/Redshift (consumers), Step Functions/MWAA/EventBridge (orchestration), CloudWatch/SNS (monitoring), Kinesis/MSK (streaming sources), DynamoDB, EKS, Secrets Manager.

### Quick revision cheat sheet
```
Primary (coordinate) | Core (HDFS+compute) | Task (compute only, Spot)
Data in S3 via EMRFS ; HDFS temporary ; logs to S3
Transient cluster: create -> steps -> auto-terminate ; Serverless: application + job runs
YARN: driver + executors ; cluster deploy mode ; dynamic allocation ; AQE
Cost: Spot task nodes, managed scaling, Graviton, transient/Serverless
Debug: log URI, Spark History Server, YARN diagnostics
```

### 10 rapid-fire revision questions
1. **Which node types store HDFS data?** Core nodes.
2. **Which nodes are best for Spot?** Task nodes.
3. **Where should durable data live?** In S3 (via EMRFS).
4. **What makes a cluster transient?** It terminates automatically after its steps (`--auto-terminate`).
5. **What is a bootstrap action?** A script executed on each node at startup.
6. **How do you submit work to a running cluster?** Add a step (e.g. `spark-submit` via `command-runner.jar`).
7. **What role gives code on EMR nodes access to S3?** The EC2 instance profile role.
8. **What does EMR Serverless use for permissions?** A job execution role.
9. **What lets EMR share table metadata with Athena?** The Glue Data Catalog as Hive metastore.
10. **Which deploy mode is recommended for production steps?** Cluster mode.

---

## Official AWS documentation
- Amazon EMR Management Guide — https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html
- EMR Release Guide (versions) — https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html
- Cluster configuration and node types — https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-instances.html
- Managed scaling — https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-managed-scaling.html
- EMR Serverless User Guide — https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless.html
- EMR on EKS — https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/emr-eks.html
- Security — https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-security.html
- Spark on EMR performance — https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-performance.html
- EMR pricing — https://aws.amazon.com/emr/pricing/
- Boto3 EMR reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/emr.html
