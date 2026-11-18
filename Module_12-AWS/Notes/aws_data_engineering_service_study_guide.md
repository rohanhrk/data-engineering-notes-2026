# AWS Data Engineering Service Study Guide

> **Target:** 0--2 years Data Engineering \| **Focus:** AWS
> fundamentals, architecture, practical implementation, and interviews

## How to use this guide

-   Study the service overview and architecture before opening the full
    API reference.
-   Use the core-concept list as a documentation reading checklist;
    verify feature details and quotas in the current AWS documentation
    because service capabilities change.
-   Complete the mini-project in a low-cost test account. Set billing
    alerts, use least privilege, and delete lab resources after testing.
-   Explain the service aloud: problem → architecture → data flow →
    security → failure handling → cost/performance.
-   Treat the interview questions as prompts to practise, not memorized
    scripts.

## Suggested learning order

1.  **S3** -- storage foundation.
2.  **IAM** -- security foundation used by every service.
3.  **Glue** -- catalog and managed ETL.
4.  **Athena** -- SQL over the data lake.
5.  **Redshift** -- warehouse and analytical serving.
6.  **Kinesis** -- streaming ingestion.
7.  **Lambda** -- event-driven compute.
8.  **EMR** -- distributed processing with Spark/Hadoop.

## Service comparison at a glance

  -----------------------------------------------------------------------
  Service                 Primary role in a data  Typical output/use
                          platform                
  ----------------------- ----------------------- -----------------------
  S3                      Object storage / data   Raw, curated, archive
                          lake                    datasets

  IAM                     Identity and access     Secure service and user
                          control                 access

  Glue                    Catalog and ETL         Metadata, transformed
                                                  datasets

  Athena                  Serverless SQL query    Ad hoc analytics over
                                                  S3

  Redshift                Data warehouse          Curated analytical
                                                  tables and marts

  Kinesis                 Streaming               Continuous event
                          ingestion/delivery      streams

  Lambda                  Event-driven compute    Lightweight validation,
                                                  routing, automation

  EMR                     Distributed compute     Spark/Hadoop batch and
                                                  streaming workloads
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 1. Amazon S3

## 1. Introduction

Amazon Simple Storage Service (S3) is AWS object storage. It stores data
as objects inside buckets and is designed for high durability, elastic
scale, and access through APIs, SDKs, the console, and CLI.

**Why it exists:** Applications need storage that scales without
managing disks or file servers. S3 separates storage capacity from
compute and makes data accessible to many AWS services.

**Problem solved:** Durable, cost-aware storage for files, backups,
logs, application assets, and data-lake datasets. S3 is object storage,
not a traditional block device or a POSIX file system.

## 2. Architecture

A producer uploads an object to a bucket. S3 stores the object and its
metadata; consumers retrieve it directly or through integrated services.
Events can notify downstream services when objects are created or
removed.

``` mermaid
flowchart LR
    A[Producers: apps / Kinesis / Glue] --> B[S3 bucket]
    B --> C[Raw prefix]
    C --> D[Glue crawler or catalog]
    D --> E[Athena / EMR / Redshift]
    B --> F[Event notification]
    F --> G[Lambda / SQS / SNS]
    B --> H[Lifecycle / replication / archive]
```

**Important components:** bucket, object, key, prefix, object metadata,
bucket policy, access point, storage class, version, multipart upload,
event notification, lifecycle rule, replication configuration.

## 3. Core concepts

-   **Buckets and objects:** A bucket is a regional container; an object
    consists of data, a key, and metadata. Keys are names;
    slash-delimited prefixes create a folder-like convention, not real
    directories.
-   **Storage classes:** S3 Standard, Intelligent-Tiering, Standard-IA,
    One Zone-IA, Glacier Instant/Flexible/Deep Archive. Choose based on
    access frequency, retrieval latency, resilience, and cost.
-   **Security:** IAM identity policies, bucket policies, access points,
    Block Public Access, ACLs (legacy/limited use), SSE-S3, SSE-KMS, and
    client-side encryption.
-   **Data protection:** Versioning, Object Lock, replication, lifecycle
    transitions/expiration, and MFA Delete where applicable.
-   **Performance and transfer:** multipart upload, byte-range GET,
    Transfer Acceleration, S3 Transfer Family, and AWS CLI/SDK transfer
    tools.
-   **Events and querying:** event notifications to
    Lambda/SQS/SNS/EventBridge; S3 Inventory; S3 Select
    availability/feature constraints should be checked before designing
    around it.
-   **Useful configuration:** bucket Region, encryption defaults,
    versioning, public-access block, lifecycle rules, ownership
    controls, logging/monitoring, and least-privilege policy.

## 4. Data Engineering use cases

-   **Pipeline position:** landing/raw zone for batch files;
    curated/serving zone for Parquet, Iceberg, and other analytical
    data; checkpoint and archive storage.
-   **Real examples:** ingest partner CSV/JSON files, retain application
    logs, store CDC exports, host data-lake tables, and archive
    historical partitions.
-   **Integrations:** Glue Data Catalog and ETL, Athena, EMR, Redshift
    Spectrum/COPY, Lambda, Kinesis Data Firehose, Step Functions, Lake
    Formation, CloudTrail, CloudWatch, and IAM/KMS.
-   **Design tip:** organize datasets by domain/table/date or another
    query-friendly partition scheme. Prefer columnar formats such as
    Parquet for analytical workloads; avoid creating excessive tiny
    files.

## 5. Hands-on implementation

**Mini-project: Build a small S3 data lake landing zone**

1.  Create a private bucket in a chosen Region with Block Public Access
    enabled.
2.  Enable default encryption and (for the lab) versioning.
3.  Create prefixes such as `raw/orders/`, `processed/orders/`, and
    `archive/orders/`.
4.  Upload a sample CSV with a date column; verify object key, size,
    metadata, and encryption.
5.  Configure a lifecycle rule for a test prefix (use a short test
    lifecycle only if safe; lifecycle actions can be irreversible).
6.  Create a least-privilege IAM policy allowing a role to list the
    required prefix and read/write only the lab objects.
7.  Optionally configure an object-created notification to SQS or Lambda
    and observe the event.

**Workflow:** source file → private S3 raw prefix → event/ETL trigger →
transformed Parquet in processed prefix → Athena query.

**Common errors and troubleshooting** - `AccessDenied`: inspect identity
policy, bucket policy, explicit denies, SCPs, KMS key policy, and Block
Public Access. - `NoSuchBucket` / wrong endpoint: verify bucket name,
account, Region, and endpoint. - `AccessDenied` on SSE-KMS objects:
grant required KMS permissions and key-policy access. - Athena returns
no rows: check table location, partition registration, file format,
schema, and SerDe. - Slow/expensive queries: use Parquet, compression,
sensible partitioning, and avoid tiny files or scanning unnecessary
data.

## 6. Interview preparation

### 10 conceptual questions

1.  What is the difference between object, key, bucket, and prefix in
    S3?

2.  Why is S3 considered object storage rather than block or file
    storage?

3.  What durability and availability mean, and how are they different?

4.  Compare S3 Standard, Standard-IA, One Zone-IA, and Glacier classes.

5.  What is versioning, and how does it help recover deleted or
    overwritten objects?

6.  Compare SSE-S3, SSE-KMS, and client-side encryption.

7.  How do IAM policies and bucket policies work together?

8.  What is a lifecycle policy, and when would you use transitions or
    expiration?

9.  What is multipart upload, and when is it useful?

10. How can S3 notify downstream services when an object is created?

### 5 scenario-based questions

1.  Design an S3 layout for daily customer and transaction files from
    multiple source systems.

2.  A partner should upload files but must not read other partners'
    data. How would you isolate access?

3.  A data lake contains millions of tiny files and Athena queries are
    slow. What would you change?

4.  An object was overwritten accidentally. How would you recover the
    previous version?

5.  New files must trigger processing, but duplicate notifications are
    possible. How would you design idempotent processing?

### 3 troubleshooting questions

1.  A Glue job gets AccessDenied reading an encrypted S3 object. How do
    you isolate the permission failure?

2.  An S3 event-triggered Lambda processes the same object more than
    once. How do you prevent duplicate output?

3.  An Athena table exists but returns zero rows after files were
    uploaded. What do you check?

## 7. Revision

-   S3 stores objects in buckets; prefixes are naming conventions, not
    directories.
-   Keep buckets private by default; use least privilege, Block Public
    Access, and encryption.
-   Choose storage class based on access pattern and retrieval needs,
    not just storage price.
-   Versioning helps recovery but does not replace backups or lifecycle
    planning.
-   For analytics, use columnar compressed formats, partition
    thoughtfully, and control file sizes.
-   Remember S3 is commonly the storage layer; Glue, Athena, EMR, and
    Redshift provide cataloging, processing, or querying.

------------------------------------------------------------------------

# 2. AWS IAM

## 1. Introduction

AWS Identity and Access Management (IAM) controls who can authenticate
to AWS and what authenticated identities are allowed to do. It provides
identities, credentials, and policy-based authorization.

**Why it exists:** Cloud resources are accessed by people, applications,
and AWS services. A centralized authorization system is needed to grant
only the permissions each identity requires.

**Problem solved:** Secure access across AWS accounts and services,
including temporary credentials for workloads and federated users. IAM
is global in scope, although some policy conditions and service
resources are regional.

## 2. Architecture

A principal makes a signed request to an AWS service. AWS evaluates
applicable policies and other controls before allowing or denying the
action.

``` mermaid
flowchart TD
    A[Human / workload] --> B[Identity: user, role, federated principal]
    B --> C[Credentials: password, access keys, STS session]
    C --> D[Signed API request]
    D --> E[Policy evaluation]
    E --> F{Explicit deny?}
    F -->|Yes| G[Deny]
    F -->|No| H{Allow and no other block?}
    H -->|Yes| I[Service action allowed]
    H -->|No| G
    J[Identity policy / resource policy / SCP / boundary / session policy] --> E
```

**Important components:** users, groups, roles, policies, trust
policies, permissions policies, STS, MFA, identity providers, permission
boundaries, service control policies (SCPs), and access analyzer.

## 3. Core concepts

-   **User:** long-term IAM identity, generally avoid for workloads;
    prefer federation and roles for people.
-   **Group:** collection of IAM users; groups cannot be principals
    assumed by services.
-   **Role:** assumable identity with temporary credentials. Workloads
    and federated users commonly use roles.
-   **Trust policy:** who can assume a role. **Permissions policy:**
    what the role can do after assumption.
-   **Policy structure:** Effect, Action/NotAction,
    Resource/NotResource, and optional Condition. Explicit Deny
    overrides Allow.
-   **Policy types:** identity-based, resource-based, permissions
    boundary, session policy, and organization SCP. Their interaction is
    not a simple union; evaluate all applicable restrictions.
-   **STS:** issues temporary credentials through operations such as
    AssumeRole and federation flows.
-   **Security practices:** least privilege, MFA, short-lived
    credentials, role-based access, no hard-coded keys, rotation where
    long-term keys are unavoidable, and CloudTrail auditing.
-   **Useful tools:** IAM Policy Simulator, Access Analyzer, credential
    report, and CloudTrail.

## 4. Data Engineering use cases

-   **Pipeline position:** cross-cutting security and access layer for
    every pipeline stage.
-   **Real examples:** Glue execution role reads raw S3 and writes
    curated S3; Lambda role reads a queue and writes a status record;
    analysts receive read-only Athena access.
-   **Integrations:** all AWS services, IAM Identity Center, STS,
    Organizations/SCPs, KMS, S3, Glue, Athena, Redshift, Lambda, EMR,
    and CloudTrail.
-   **Design tip:** separate human access from workload roles; separate
    deployment permissions from runtime permissions; scope S3 and KMS
    permissions to the exact resources needed.

## 5. Hands-on implementation

**Mini-project: Secure a simple S3-to-Lambda data workflow**

1.  Create a private S3 lab bucket and a test object prefix.
2.  Create an IAM role trusted by Lambda (the trust policy permits the
    Lambda service to assume it).
3.  Attach a narrowly scoped permissions policy allowing `s3:GetObject`
    only on the lab prefix and the minimum logging actions required.
4.  Create a Lambda function using that execution role; read an object
    or log the event metadata.
5.  Test the function and inspect CloudWatch Logs.
6.  Remove a required permission, rerun, and inspect the AccessDenied
    error; restore the permission.
7.  Review CloudTrail events and use the policy simulator or Access
    Analyzer to validate access.

**Workflow:** service assumes role → receives temporary credentials →
calls permitted APIs → CloudTrail records supported management events.

**Common errors and troubleshooting** - `AccessDenied`: identify the
principal and exact action/resource; check explicit denies, resource
policies, SCPs, boundaries, session policies, and conditions. - Role
cannot be assumed: inspect trust policy, principal ARN, external ID, and
service trust relationship. - S3 access works but KMS decrypt fails: S3
permission alone is insufficient; check KMS key policy and IAM
permissions. - Policy appears correct: verify ARN, wildcard placement,
Region/account, condition context, and whether the request uses the
expected role. - Avoid solving errors by attaching
`AdministratorAccess`; grant the missing minimum permission.

## 6. Interview preparation

### 10 conceptual questions

1.  What is IAM, and what is the difference between authentication and
    authorization?

2.  Compare IAM users, groups, and roles.

3.  What is the difference between a role trust policy and a permissions
    policy?

4.  How does AWS evaluate an explicit Deny and an Allow?

5.  What are temporary credentials, and what does AWS STS do?

6.  What is the principle of least privilege?

7.  Compare identity-based and resource-based policies.

8.  What are permission boundaries and service control policies?

9.  How should an application running on AWS obtain credentials?

10. What is MFA, and why should it be enabled for privileged human
    access?

### 5 scenario-based questions

1.  A Glue job must read from one S3 prefix and write to another. How
    would you design its role?

2.  A Lambda function needs to access a KMS-encrypted S3 object. Which
    permissions and policies are relevant?

3.  An analyst should query Athena but must not modify S3 source data.
    How would you scope access?

4.  Two AWS accounts need to share access to a data bucket. How would
    you implement cross-account access?

5.  A developer requests AdministratorAccess to fix a pipeline. How
    would you investigate and provide safer access?

### 3 troubleshooting questions

1.  A workload receives AccessDenied even though its role has an Allow
    policy. What controls might still deny it?

2.  A service cannot assume its execution role. What do you inspect?

3.  An S3 GetObject succeeds for an unencrypted file but fails for a
    KMS-encrypted file. Why?

## 7. Revision

-   Authentication establishes identity; authorization decides permitted
    actions.
-   Trust policy answers **who can assume this role**; permissions
    policy answers **what the role can do**.
-   Explicit Deny overrides Allow.
-   Prefer roles and temporary credentials over embedded access keys.
-   Evaluate identity policies, resource policies, SCPs, boundaries,
    session policies, and conditions.
-   IAM is the security foundation connecting S3, Glue, Lambda, Athena,
    Redshift, and EMR.

------------------------------------------------------------------------

# 3. AWS Glue

## 1. Introduction

AWS Glue is a serverless data integration service for discovering,
preparing, moving, and integrating data. It includes a Data Catalog,
crawlers, ETL jobs, workflows, triggers, and related integration
capabilities.

**Why it exists:** Data lakes and analytics platforms need metadata
discovery and repeatable ETL without teams provisioning and managing all
the underlying infrastructure.

**Problem solved:** Cataloging datasets and running managed batch or
streaming transformations across data sources and targets.

## 2. Architecture

A crawler or API defines metadata in the Glue Data Catalog. A Glue job
uses a script and execution role to read sources, transform records, and
write to targets. Workflows or external orchestrators coordinate
execution.

``` mermaid
flowchart LR
    A[S3 / JDBC / other sources] --> B[Crawler or catalog API]
    B --> C[Glue Data Catalog]
    C --> D[Glue ETL job: Spark / Python]
    D --> E[Transform / validate]
    E --> F[S3 curated data]
    F --> G[Athena / Redshift / EMR]
    H[Workflow / trigger / Step Functions] --> D
    I[CloudWatch Logs and metrics] --- D
```

**Important components:** Data Catalog, databases, tables, crawlers,
classifiers, connections, jobs, job bookmarks, triggers, workflows,
development endpoints/notebooks where available, Glue Studio, Data
Quality, and execution roles.

## 3. Core concepts

-   **Data Catalog:** centralized technical metadata store containing
    databases, tables, schemas, and partition information.
-   **Crawler:** inspects data stores and infers schema/partitions;
    review its output because inference can be imperfect.
-   **Job types:** Spark ETL, Python shell, and supported streaming ETL
    options. Choose based on scale and processing requirements.
-   **DynamicFrames and DataFrames:** DynamicFrames handle
    semi-structured/schema inconsistencies; Spark DataFrames provide the
    standard Spark API and optimizations.
-   **Job bookmarks:** track processed source data for supported sources
    to avoid reprocessing; they are not a universal exactly-once
    guarantee.
-   **Partitions and pushdown:** partition pruning and pushdown
    predicates can reduce scanned data.
-   **Connections and VPC:** configure connectivity to JDBC databases
    and private resources; security groups, routes, DNS, and subnet
    capacity matter.
-   **Operational controls:** worker type/count, Glue version, retries,
    timeout, concurrency, arguments, temp directory, role, logs,
    metrics, and job parameters.
-   **Data quality:** rules and quality checks can validate
    completeness, uniqueness, ranges, and other expectations.

## 4. Data Engineering use cases

-   **Pipeline position:** metadata/catalog layer and managed
    transformation layer, commonly between S3 raw and curated zones.
-   **Real examples:** crawl incoming CSV/JSON, convert raw data to
    partitioned Parquet, deduplicate records, apply schema mapping, and
    load warehouse-ready data.
-   **Integrations:** S3, Lake Formation, IAM, KMS, CloudWatch,
    EventBridge, Step Functions, Athena, Redshift, JDBC databases, and
    streaming sources.
-   **Design tip:** define schemas deliberately for production-critical
    datasets; use crawlers for discovery but avoid uncontrolled schema
    changes. Make transformations idempotent and monitor job runs.

## 5. Hands-on implementation

**Mini-project: Convert raw CSV orders into curated Parquet**

1.  Upload sample `orders.csv` files to `s3://<bucket>/raw/orders/`.
2.  Create a Glue database in the Data Catalog.
3.  Create and run a crawler over the raw prefix; inspect the inferred
    table schema.
4.  Create a Glue ETL job with an execution role that can read raw data,
    write curated data, access required catalog metadata, and publish
    logs.
5.  Transform data: parse timestamps, cast amount to decimal, remove
    invalid rows, and derive a `year/month/day` partition.
6.  Write Snappy-compressed Parquet to `s3://<bucket>/curated/orders/`.
7.  Catalog the curated output and query it with Athena.
8.  Rerun the job and evaluate bookmark behavior, duplicate handling,
    and idempotency.

**Workflow:** raw CSV → crawler/catalog → Glue Spark ETL → validated
partitioned Parquet → Athena.

**Common errors and troubleshooting** - Job cannot access S3: check
execution role, bucket policy, KMS permissions, and VPC endpoint/network
path. - JDBC connection timeout: verify subnet, security group rules,
routes, DNS, database firewall, and credentials. - Schema mismatch:
inspect crawler classifiers, schema evolution, data types, and malformed
records. - Job runs slowly: inspect Spark UI/logs, partition skew, file
sizes, worker capacity, shuffle, and pushdown. - Duplicate data after
rerun: understand bookmark state and design idempotent writes/partition
replacement or merge logic. - `No space left`/shuffle failures: reduce
skew, tune partitions, increase appropriate worker capacity, and avoid
oversized transformations.

## 6. Interview preparation

### 10 conceptual questions

1.  What is AWS Glue, and which problems does it solve?

2.  What is the AWS Glue Data Catalog?

3.  What is the difference between a crawler and an ETL job?

4.  What are DynamicFrames, and how do they differ from Spark
    DataFrames?

5.  What are Glue job bookmarks, and what are their limitations?

6.  What is a Glue connection, and when is a VPC connection needed?

7.  How do Glue crawlers infer schemas and partitions?

8.  What is partition pruning, and how can Glue support it?

9.  What are Glue workflows, triggers, and job dependencies?

10. How would you monitor and troubleshoot a failed Glue job?

### 5 scenario-based questions

1.  Daily CSV files arrive in S3 and must become partitioned Parquet.
    Design the Glue workflow.

2.  A source adds a new nullable column. How would you handle schema
    evolution safely?

3.  A job reprocesses old files and creates duplicates. How would you
    investigate bookmarks and write strategy?

4.  A Glue job must connect to a database in a private subnet. What
    networking and security setup is needed?

5.  A job is slow on a large dataset with uneven customer distribution.
    How would you diagnose data skew?

### 3 troubleshooting questions

1.  A Glue job fails with AccessDenied while reading an S3 source. What
    do you check?

2.  A Glue JDBC job times out before connecting. What network components
    do you inspect?

3.  A crawler changes a column type unexpectedly. How do you prevent bad
    schema inference from breaking downstream queries?

## 7. Revision

-   Glue provides managed integration/ETL plus a central Data Catalog.
-   Crawler discovers metadata; job transforms data.
-   DynamicFrames help with semi-structured data; DataFrames provide
    Spark APIs.
-   Bookmarks help track supported source processing but do not
    automatically guarantee exactly-once output.
-   Use partitioning, Parquet, compression, pushdown, and sensible file
    sizes.
-   Glue integrates naturally with S3, Athena, Redshift, IAM, Lake
    Formation, and Step Functions.

------------------------------------------------------------------------

# 4. Amazon Athena

## 1. Introduction

Amazon Athena is a serverless interactive query service that uses SQL to
analyze data in S3. It commonly uses Trino-based engine capabilities and
reads table metadata from the AWS Glue Data Catalog or compatible
catalogs.

**Why it exists:** Teams need to explore and query data lakes without
provisioning a database cluster.

**Problem solved:** Ad hoc SQL analytics over files in S3, with pricing
commonly based on data scanned for on-demand queries (pricing and
workgroup features vary by engine and configuration).

## 2. Architecture

Athena receives SQL, resolves table metadata from a catalog, reads
matching objects in S3, executes the query, and writes results to a
configured result location.

``` mermaid
flowchart TD
    A[Analyst / BI / SDK] --> B[Athena workgroup]
    B --> C[SQL engine]
    C --> D[Glue Data Catalog]
    C --> E[S3 data files]
    C --> F[S3 query results]
    G[IAM / Lake Formation] --> B
    H[CloudWatch / usage controls] --- B
```

**Important components:** workgroups, query editor/API, engine version,
Data Catalog, databases/tables, SerDes, partitions, CTAS, views,
federated connectors, result location, encryption, and query limits.

## 3. Core concepts

-   **Schema-on-read:** table definitions describe how files should be
    interpreted; data remains in S3.
-   **Catalog and table:** metadata points to S3 locations and defines
    columns, formats, SerDe, and partitions.
-   **File formats:** CSV/JSON are easy to ingest; Parquet and ORC are
    columnar and usually better for analytics; compression reduces
    scanned bytes.
-   **Partitioning:** organize data by common filter columns such as
    date or region; use partition projection where appropriate to avoid
    large metadata registration workloads.
-   **Workgroups:** separate workloads, enforce result settings,
    encryption, and data-scan limits.
-   **CTAS/INSERT:** create tables from query results and write
    transformed datasets, subject to engine and format support.
-   **Federated query:** query supported external data sources through
    connectors; consider latency and cost.
-   **Cost/performance:** reduce bytes scanned with columnar formats,
    compression, partition pruning, selecting needed columns, and
    avoiding `SELECT *`.
-   **Security:** IAM, S3 permissions, KMS, Lake Formation permissions,
    workgroup settings, and result-bucket access.

## 4. Data Engineering use cases

-   **Pipeline position:** SQL exploration and serverless analytics
    layer over S3 data-lake zones.
-   **Real examples:** validate daily ingestion, profile raw data,
    analyze curated Parquet, create derived datasets with CTAS, and
    power lightweight BI queries.
-   **Integrations:** S3, Glue Data Catalog, Lake Formation, IAM, KMS,
    QuickSight, CloudWatch, and supported federated connectors.
-   **Design tip:** Athena is not a replacement for every OLTP database
    or a continuously loaded warehouse. Use Redshift for workloads
    needing warehouse capabilities, concurrency, and managed performance
    patterns beyond ad hoc S3 querying.

## 5. Hands-on implementation

**Mini-project: Query a partitioned S3 sales data lake**

1.  Put sample CSV files under `raw/sales/` and convert them to Parquet
    using Glue or a small preprocessing script.
2.  Create a Glue database/table (crawler or explicit DDL) pointing to
    the curated S3 location.
3.  Configure an Athena workgroup with an encrypted S3 query-results
    location and a per-query scan limit.
4.  Run basic SQL: counts, totals, date filters, grouping, and null
    checks.
5.  Compare a query on CSV with the equivalent Parquet dataset; compare
    bytes scanned.
6.  Add date partitions and query with partition filters.
7.  Use CTAS to create a derived dataset, then inspect the output in S3.

**Workflow:** S3 curated Parquet → Glue Catalog metadata → Athena SQL →
S3 query results / BI.

**Common errors and troubleshooting** - `HIVE_BAD_DATA`: source values
do not match declared schema; clean/cast data or use a safer schema. -
`TABLE_NOT_FOUND`: check catalog, database, Region, workgroup/catalog
selection, and table name. - Query returns no rows: check S3 location,
partition metadata, partition values, and file contents. -
`AccessDenied`: verify data bucket, result bucket, KMS, IAM, and Lake
Formation permissions. - High cost/slow query: inspect bytes scanned;
use Parquet, compression, partitions, column selection, and appropriate
workgroups.

## 6. Interview preparation

### 10 conceptual questions

1.  What is Amazon Athena, and how is it different from a provisioned
    database?

2.  How does Athena query data stored in S3?

3.  What is schema-on-read?

4.  What is the role of the Glue Data Catalog in Athena?

5.  Why are Parquet and ORC often preferred over CSV for analytics?

6.  What is partition pruning, and how does it reduce query cost?

7.  What is an Athena workgroup?

8.  What are CTAS and views, and when would you use them?

9.  How does Athena pricing generally relate to data scanned?

10. What security controls can restrict Athena data access?

### 5 scenario-based questions

1.  Your daily Athena bill is increasing. How would you reduce scanned
    data and control cost?

2.  An analyst needs access to one dataset but not other S3 data. How
    would you implement access controls?

3.  Design a queryable data lake for sales data partitioned by date and
    region.

4.  A query over millions of small JSON files is slow. What changes
    would you make?

5.  Business users need both ad hoc lake queries and high-concurrency
    dashboards. Would Athena alone be sufficient?

### 3 troubleshooting questions

1.  Athena reports HIVE_BAD_DATA for a column. What could cause it?

2.  A table exists but a query returns no records after a new partition
    lands. What do you inspect?

3.  A query fails writing results even though the source data is
    readable. What permissions or settings might be missing?

## 7. Revision

-   Athena is serverless SQL over data, commonly in S3.
-   Glue Data Catalog stores table metadata; it does not store the
    underlying dataset.
-   Parquet/ORC, compression, partition pruning, and selecting fewer
    columns reduce scans.
-   Workgroups help isolate workloads and enforce settings/limits.
-   Source-data access and query-result-bucket access are separate
    permission concerns.
-   Athena complements S3 and Glue; Redshift is often better suited to
    sustained warehouse workloads.

------------------------------------------------------------------------

# 5. Amazon Redshift

## 1. Introduction

Amazon Redshift is a managed cloud data warehouse for analytical SQL
workloads. It supports provisioned clusters and serverless options, with
columnar storage, massively parallel processing (MPP), and integrations
with S3 data lakes.

**Why it exists:** Organizations need a platform optimized for
analytical queries across large datasets and many users, rather than
transactional row-by-row workloads.

**Problem solved:** Centralized warehouse analytics, reporting,
dimensional models, aggregations, and data marts.

## 2. Architecture

Data is loaded from operational sources or S3 into Redshift, distributed
across compute, stored columnarly, and queried by BI tools or
applications. Redshift can also query data in S3 through lake
integration features.

``` mermaid
flowchart LR
    A[Operational DB / CDC / files] --> B[S3 staging / ingestion]
    B --> C[Redshift COPY / streaming / integration]
    C --> D[Redshift warehouse]
    D --> E[Staging tables]
    E --> F[Dimensions and facts]
    F --> G[BI / dashboards / SQL clients]
    H[Glue Catalog / Lake Formation] --> I[Redshift Spectrum]
    I --> B
```

**Important components:** cluster or serverless workgroup,
nodes/compute, databases, schemas, tables, distribution styles/keys,
sort keys, COPY, UNLOAD, snapshots, workload management, materialized
views, Spectrum, and concurrency scaling/serverless capacity concepts.

## 3. Core concepts

-   **MPP:** query work is distributed across compute resources; design
    data distribution to reduce data movement.
-   **Columnar storage:** stores column values efficiently for
    analytical scans and compression.
-   **Provisioned vs Serverless:** provisioned uses managed cluster
    capacity; Serverless manages capacity for workloads with usage-based
    billing. Compare operational and cost patterns.
-   **Loading/unloading:** COPY loads from S3; UNLOAD exports query
    results to S3. IAM roles commonly authorize access.
-   **Distribution:** AUTO, EVEN, KEY, and ALL choices affect data
    placement and joins. Prefer AUTO unless workload evidence supports
    manual tuning.
-   **Sort keys:** influence data ordering and block skipping; choose
    based on filter/join patterns and table design.
-   **Workload management:** queues, priorities, concurrency, and query
    monitoring help manage mixed workloads.
-   **Operations:** snapshots, restore, resize, maintenance, monitoring,
    vacuum/analyze behavior depending on table type and workload.
-   **Lake integration:** Spectrum and related features query data in
    S3; check current catalog, permission, and format support for the
    chosen design.
-   **Security:** IAM roles, database users/roles, network controls,
    encryption, audit logging, and fine-grained access.

## 4. Data Engineering use cases

-   **Pipeline position:** analytical serving/warehouse layer after
    ingestion and transformation.
-   **Real examples:** combine sales, customer, and product data into
    fact/dimension models; serve BI dashboards; calculate KPIs; create
    governed data marts.
-   **Integrations:** S3, Glue Data Catalog, Lake Formation, IAM, KMS,
    DMS, Kinesis Data Firehose, Lambda, Step Functions, QuickSight, and
    BI/ETL tools.
-   **Design tip:** use a warehouse for curated, repeated, multi-user
    analytics. Keep raw history in S3 where appropriate; load only what
    benefits from warehouse serving.

## 5. Hands-on implementation

**Mini-project: Load sales data from S3 into a Redshift warehouse**

1.  Create a Redshift Serverless workgroup/namespace or a small
    provisioned test environment; review cost and delete it after the
    lab.
2.  Create an S3 staging prefix containing sample CSV files.
3.  Configure an IAM role for Redshift to read the staging prefix.
4.  Create a database schema and staging table with suitable data types.
5.  Use `COPY` to load data from S3; validate row counts and rejected
    records.
6.  Transform staging data into a simple `fact_sales` table and
    dimension table.
7.  Run analytical queries with joins, aggregations, and date filters.
8.  Optionally use `UNLOAD` to export an aggregate back to S3.

Example pattern (adapt credentials, Region, role ARN, file format, and
table definition):

``` sql
COPY staging.sales
FROM 's3://YOUR_BUCKET/staging/sales/'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_REDSHIFT_ROLE'
FORMAT AS CSV
IGNOREHEADER 1;
```

**Workflow:** source files → S3 staging → Redshift COPY → staging tables
→ warehouse model → BI.

**Common errors and troubleshooting** - COPY authorization failure:
verify Redshift IAM role association, trust relationship, S3 policy, KMS
permissions, and Region. - Load errors: inspect `STL_LOAD_ERRORS` where
applicable or current system views, file format, delimiter, encoding,
and type compatibility. - Slow joins: inspect query plan, distribution,
data skew, statistics, sort design, and data movement. - High
concurrency/queue time: inspect workload management, query priorities,
and capacity. - Unexpected cost: review Serverless usage or provisioned
node hours, snapshots, data transfer, and idle resources.

## 6. Interview preparation

### 10 conceptual questions

1.  What is Amazon Redshift, and what workloads is it designed for?

2.  Explain MPP and why it helps analytical queries.

3.  Compare a data warehouse with a data lake.

4.  What is the difference between Redshift provisioned and Serverless?

5.  What does the COPY command do, and why is S3 commonly used with it?

6.  What are distribution styles and distribution keys?

7.  What are sort keys, and how do they affect query performance?

8.  What is Redshift Spectrum?

9.  What are snapshots and how are they used for recovery?

10. What is workload management, and why does concurrency matter?

### 5 scenario-based questions

1.  Design a warehouse for sales reporting across customers, products,
    and orders.

2.  A COPY command must load encrypted files from S3. What IAM and KMS
    configuration is required?

3.  A large fact-to-dimension join is slow. How would you diagnose data
    movement and skew?

4.  Many dashboards run concurrently and queue. How would you
    investigate workload and capacity?

5.  Some data is queried rarely while other curated data powers daily
    dashboards. How might you split S3 lake and Redshift
    responsibilities?

### 3 troubleshooting questions

1.  COPY fails with authorization errors. Which role, trust, bucket, and
    key policies do you check?

2.  COPY completes but fewer rows load than expected. How do you inspect
    rejected rows and input formatting?

3.  A query becomes slow after data growth. What query-plan and
    table-design factors do you examine?

## 7. Revision

-   Redshift is an analytical MPP warehouse, not an OLTP database.
-   COPY loads from S3; UNLOAD exports to S3.
-   Distribution affects data movement; sort keys affect scan
    efficiency. Use evidence before manual tuning.
-   Separate staging, transformation, and presentation schemas/tables.
-   Monitor query plans, skew, concurrency, and workload capacity.
-   Redshift integrates with S3, Glue, Lake Formation, DMS, Firehose,
    and BI tools.

------------------------------------------------------------------------

# 6. Amazon Kinesis

## 1. Introduction

Amazon Kinesis is a family of services for collecting, processing, and
analyzing streaming data in near real time. Common components include
Kinesis Data Streams, Data Firehose, and Data Analytics
capabilities/related streaming options; feature names and availability
evolve, so check current AWS documentation.

**Why it exists:** Batch processing alone cannot support use cases that
need data to be ingested and acted on continuously.

**Problem solved:** Durable streaming ingestion, buffering, and delivery
of event data to analytics and storage destinations.

## 2. Architecture

Producers publish records to a stream. Consumers read records, process
them, and write results to downstream systems. Firehose can buffer and
deliver streaming data to supported destinations.

``` mermaid
flowchart LR
    A[Apps / devices / logs] --> B[Kinesis Data Streams]
    B --> C[Consumer: Lambda / KCL app]
    C --> D[Real-time transform]
    D --> E[S3 / Redshift / OpenSearch]
    A --> F[Kinesis Data Firehose]
    F --> G[Buffer / optional transform]
    G --> H[S3 / supported destinations]
    I[CloudWatch metrics] --- B
```

**Important components:** stream, shard, partition key, record, sequence
number, producer, consumer, retention, enhanced fan-out, Kinesis Client
Library (KCL), checkpoint, iterator, Firehose delivery stream,
buffering, and retry/error destination.

## 3. Core concepts

-   **Data Streams:** ordered records within a shard; partition key maps
    records to shards. Ordering is guaranteed within a shard, not
    globally across the stream.
-   **Capacity modes:** provisioned shard capacity or on-demand mode,
    subject to current service limits and pricing.
-   **Consumers:** shared-throughput consumers or enhanced fan-out
    consumers with dedicated read throughput.
-   **Retention and replay:** records are retained for a configurable
    period within service limits; consumers can replay while records
    remain available.
-   **Scaling:** shard count/capacity, partition-key distribution, hot
    shards, throughput limits, and consumer lag matter.
-   **Delivery semantics:** retries can lead to duplicate processing;
    design idempotent consumers. Checkpointing tracks consumer progress.
-   **Firehose:** managed delivery with buffering by size/time, optional
    transformation, compression, format conversion where supported, and
    backup/error handling.
-   **Monitoring:** incoming records/bytes, throttling, iterator
    age/consumer lag, delivery failures, and destination errors.
-   **Security:** IAM, encryption, VPC connectivity options, and
    destination permissions.

## 4. Data Engineering use cases

-   **Pipeline position:** real-time ingestion layer before stream
    processing, storage, or analytics.
-   **Real examples:** clickstream events, application logs, IoT
    telemetry, transaction events, operational monitoring, and
    near-real-time dashboards.
-   **Integrations:** Lambda, Firehose, S3, Redshift, Managed Service
    for Apache Flink (formerly Kinesis Data Analytics naming has
    evolved), CloudWatch, Glue streaming ETL, and OpenSearch
    destinations where supported.
-   **Design tip:** choose Data Streams when you need custom consumers,
    replay, and control; choose Firehose for managed buffering and
    delivery with less consumer infrastructure.

## 5. Hands-on implementation

**Mini-project: Stream application events into S3**

1.  Create a Kinesis Data Stream using an appropriate test capacity
    mode.
2.  Write a small producer (AWS CLI, SDK, or Python/boto3) that sends
    JSON records with a stable partition key such as `customer_id`.
3.  Read records with a consumer or Lambda trigger; log
    sequence/partition metadata.
4.  Configure a Firehose delivery stream to buffer and deliver records
    to an S3 prefix.
5.  Inspect output files and query them with Athena after cataloging.
6.  Test a burst of records and observe throttling/lag metrics.
7.  Add idempotency using a unique event ID in the consumer output.

**Workflow:** producer → Data Streams → consumer/Firehose → S3 → Glue
Catalog → Athena.

**Common errors and troubleshooting** -
`ProvisionedThroughputExceededException`: inspect shard capacity, hot
partition keys, producer retries, and backoff. - Consumer lag grows:
inspect processing time, consumer count, iterator age, downstream
throttling, and shard parallelism. - Duplicate records: use event IDs
and idempotent writes; retries are expected in distributed systems. -
Firehose delivery failures: inspect destination permissions, buffering,
transformation errors, backup prefix, and CloudWatch logs. - Uneven
throughput: choose a high-cardinality partition key with an even
distribution; avoid a single constant key.

## 6. Interview preparation

### 10 conceptual questions

1.  What is Amazon Kinesis, and which streaming problems does it solve?

2.  Compare Kinesis Data Streams and Kinesis Data Firehose.

3.  What is a shard?

4.  What is a partition key, and how does it affect record distribution
    and ordering?

5.  What ordering guarantees does Kinesis Data Streams provide?

6.  What are sequence numbers and checkpoints?

7.  What is enhanced fan-out?

8.  What is consumer lag/iterator age, and why is it important?

9.  Why should stream consumers be idempotent?

10. How does Firehose buffering affect delivery latency?

### 5 scenario-based questions

1.  Design ingestion for millions of clickstream events with multiple
    independent consumers.

2.  One partition key receives most events and causes throttling. How
    would you fix the hot shard?

3.  A downstream database is temporarily unavailable. How should the
    streaming pipeline handle retries and recovery?

4.  Business users need data in S3 within a few minutes without managing
    consumers. Which Kinesis component fits?

5.  A consumer falls behind during a traffic spike. What metrics and
    scaling options would you examine?

### 3 troubleshooting questions

1.  Producers receive ProvisionedThroughputExceededException. What do
    you investigate?

2.  Iterator age keeps increasing. How do you isolate consumer
    processing versus downstream bottlenecks?

3.  Firehose reports delivery failures. Which logs, permissions, and
    destination settings do you inspect?

## 7. Revision

-   Data Streams is for durable stream ingestion and custom consumers;
    Firehose is managed delivery.
-   A shard is a capacity and ordering unit; ordering is per shard, not
    global.
-   Partition-key distribution is critical; hot keys create hot shards.
-   Consumers should checkpoint and handle retries/duplicates safely.
-   Monitor throttling, iterator age, delivery success, and destination
    errors.
-   Kinesis commonly feeds Lambda, S3, Redshift, Glue, and streaming
    analytics.

------------------------------------------------------------------------

# 7. AWS Lambda

## 1. Introduction

AWS Lambda is a serverless compute service that runs code in response to
events or direct invocations. AWS manages the underlying server fleet
and scales execution according to configured concurrency and service
behavior.

**Why it exists:** Many workloads need short-lived event-driven compute
without provisioning and maintaining servers.

**Problem solved:** Lightweight transformations, event handling,
orchestration steps, and automation triggered by changes or messages.

## 2. Architecture

An event source invokes a Lambda function directly or through an event
source mapping. Lambda runs the handler with an execution role, emits
logs/metrics, and may write to downstream services.

``` mermaid
flowchart LR
    A[S3 / SQS / Kinesis / API] --> B[Event source or mapping]
    B --> C[Lambda invocation]
    D[IAM execution role] --> C
    C --> E[Handler code]
    E --> F[S3 / DynamoDB / SNS / other API]
    C --> G[CloudWatch Logs and metrics]
    C --> H[Retry / DLQ or failure destination]
```

**Important components:** function, handler, runtime, deployment
package/container image, execution role, environment variables, layers,
memory, timeout, concurrency, event source mapping, versions, aliases,
destinations, DLQ, and CloudWatch logs.

## 3. Core concepts

-   **Invocation models:** synchronous request/response, asynchronous
    event invocation, and poll-based event source mappings.
-   **Execution role:** permissions granted to the function; separate
    from the caller's permission to invoke it.
-   **Limits and sizing:** memory also affects CPU allocation; set
    timeout and ephemeral storage based on workload; understand payload,
    duration, and concurrency limits.
-   **Concurrency:** reserved concurrency protects capacity; provisioned
    concurrency can reduce cold-start latency for supported use cases.
-   **Retries and failures:** behavior differs by invocation type and
    event source. Configure retry, visibility timeout, partial batch
    response, DLQ/destination, and idempotency appropriately.
-   **Deployment:** ZIP packages or container images, layers, versions,
    aliases, environment variables, and infrastructure as code.
-   **Networking:** VPC attachment enables private-resource access but
    requires correct subnets, routes, security groups, and egress.
-   **Observability:** CloudWatch Logs, metrics, tracing, structured
    logs, and alarms.
-   **Design limits:** not ideal for very long-running, highly stateful,
    or continuously running compute; consider Glue, EMR, ECS, or other
    services.

## 4. Data Engineering use cases

-   **Pipeline position:** event-driven glue between ingestion, storage,
    and orchestration components.
-   **Real examples:** validate an uploaded file, normalize a small
    event, route an SQS message, start a Glue job, or enrich a record
    before storage.
-   **Integrations:** S3, SQS, SNS, Kinesis, EventBridge, Step
    Functions, DynamoDB, API Gateway, Glue, CloudWatch, IAM, and VPC
    resources.
-   **Design tip:** keep handlers small, stateless, idempotent,
    observable, and safe to retry. Move heavy Spark-scale
    transformations to Glue or EMR.

## 5. Hands-on implementation

**Mini-project: Validate an S3 upload and publish a notification**

1.  Create a private S3 bucket and a prefix such as `incoming/`.
2.  Create a Lambda execution role with only required S3 read and
    CloudWatch logging permissions.
3.  Create a Python Lambda handler that receives an S3 event, extracts
    bucket/key, validates file extension/name, and logs the result.
4.  Configure an S3 ObjectCreated notification for the `incoming/`
    prefix.
5.  Upload a test file and inspect CloudWatch Logs.
6.  Add error handling and an idempotency strategy (for example, track
    processed object version/ETag in a state store if the workflow
    requires it).
7.  Optionally publish a success/failure message to SNS or SQS.

**Workflow:** S3 object created → Lambda event → validate
metadata/content → log or route result.

**Common errors and troubleshooting** - Function times out: inspect
duration, network calls, memory/CPU, timeout, and downstream response
times. - `AccessDenied`: check execution role, resource policy, KMS key
policy, and event-source permissions. - Function not triggered: verify
event notification prefix/suffix, destination permission, Region, and
event type. - Duplicate processing: event delivery/retries can duplicate
work; implement idempotency. - VPC function cannot reach a service:
inspect subnet routes, NAT/VPC endpoints, DNS, and security groups. -
Cold starts: review package size, runtime initialization, VPC needs, and
provisioned concurrency if latency justifies cost.

## 6. Interview preparation

### 10 conceptual questions

1.  What is AWS Lambda, and what does serverless mean in this context?

2.  What are the main Lambda invocation models?

3.  What is the difference between an execution role and invoke
    permission?

4.  What is a cold start?

5.  How do memory, CPU, timeout, and concurrency relate?

6.  What is an event source mapping?

7.  How do asynchronous retries and failure destinations work at a high
    level?

8.  What is idempotency, and why is it important for Lambda handlers?

9.  When would you use Lambda layers or container images?

10. When should you choose Glue or EMR instead of Lambda?

### 5 scenario-based questions

1.  An S3 upload should trigger validation and start a Glue job. Design
    the event-driven flow.

2.  A Lambda function processes SQS messages but sometimes fails halfway
    through a batch. How would you avoid losing successful messages?

3.  A function receives duplicate events and must not create duplicate
    records. What design would you use?

4.  A Lambda function in a VPC cannot reach a public API. What
    networking options would you examine?

5.  A transformation runs longer and uses more memory than Lambda is
    suited for. What AWS service would you consider?

### 3 troubleshooting questions

1.  A Lambda invocation times out. How do you identify whether code,
    network, or downstream service is responsible?

2.  An S3 event is not invoking Lambda. What configuration and
    permission checks do you perform?

3.  A function has intermittent AccessDenied errors when reading
    encrypted objects. What policies are involved?

## 7. Revision

-   Lambda is event-driven serverless compute; it is not a permanent
    server.
-   Execution role grants the function's AWS permissions; invoke
    permission controls who can call it.
-   Invocation type and event source determine retry and failure
    behavior.
-   Design for duplicate delivery with idempotency.
-   Monitor duration, errors, throttles, concurrency, and logs.
-   Use Lambda for lightweight event processing; use Glue/EMR for larger
    distributed data transformations.

------------------------------------------------------------------------

# 8. Amazon EMR

## 1. Introduction

Amazon EMR is a managed big-data platform for running frameworks such as
Apache Spark, Hadoop, Hive, and related open-source tools on AWS
infrastructure. EMR is available in different deployment models,
including clusters and serverless options; select based on workload and
operational needs.

**Why it exists:** Large-scale data processing frameworks require
distributed compute and coordination that can be complex to provision
and operate.

**Problem solved:** Managed infrastructure for distributed processing,
ETL, analytics, and big-data workloads using familiar open-source
ecosystems.

## 2. Architecture

Data is stored in S3 or another supported storage layer. EMR provisions
or allocates compute, runs distributed applications, and writes
transformed results back to durable storage.

``` mermaid
flowchart LR
    A[S3 data lake / sources] --> B[EMR cluster or EMR Serverless]
    B --> C[Driver / coordinator]
    C --> D[Executors / worker nodes]
    D --> E[Spark / Hive / Hadoop jobs]
    E --> F[S3 curated output]
    F --> G[Athena / Redshift / downstream jobs]
    H[Bootstrap / configs / IAM / network] --> B
    I[CloudWatch / logs] --- B
```

**Important components:** cluster, primary/core/task nodes (cluster
model), instance fleets/groups, applications, steps, bootstrap actions,
release labels, EMR roles, security configuration, managed scaling,
logs, and EMR Serverless application/job runs.

## 3. Core concepts

-   **EMR cluster:** provisions EC2-backed infrastructure for big-data
    frameworks. Node roles and storage choices influence resilience and
    performance.
-   **EMR Serverless:** runs supported analytics applications without
    managing cluster capacity directly; understand startup, worker
    sizing, and billing.
-   **Spark fundamentals:** driver plans work; executors run tasks;
    transformations are lazy until an action; shuffles move data between
    partitions.
-   **Storage:** S3 is commonly used for durable input/output; HDFS may
    be used for cluster-local/intermediate data but should not be
    treated as durable across cluster termination.
-   **Scaling:** instance groups/fleets, managed scaling, executor
    sizing, partition count, and workload characteristics.
-   **Job execution:** steps, notebooks/studio options, CLI/SDK
    submission, bootstrap actions, configuration classifications, and
    release labels.
-   **Reliability:** retries, checkpoints where applicable, output
    commit behavior, logs, and job monitoring.
-   **Security:** IAM roles for EMR, EC2 instance profile, service role,
    security configuration, encryption, VPC/subnets, security groups,
    and private connectivity.
-   **Cost control:** choose cluster lifecycle carefully, use
    appropriate instance types/capacity options, auto-terminate idle
    clusters, and compare EMR Serverless with cluster operation.

## 4. Data Engineering use cases

-   **Pipeline position:** distributed processing/compute layer for
    large-scale batch or streaming transformations.
-   **Real examples:** large-scale Spark ETL, log processing, data
    cleansing, feature engineering, Hive analytics, and migration of
    Hadoop workloads.
-   **Integrations:** S3, Glue Data Catalog, IAM, KMS, CloudWatch, Step
    Functions, Lake Formation, Redshift, and open-source Spark/Hadoop
    ecosystem tools.
-   **Design tip:** use EMR when you need control over open-source
    frameworks, cluster configuration, or large-scale compute. For
    simpler managed Spark ETL, compare AWS Glue; for SQL over S3,
    compare Athena.

## 5. Hands-on implementation

**Mini-project: Run a PySpark batch job on EMR and write Parquet to S3**

1.  Create an S3 input prefix with a sample CSV dataset and an output
    prefix.
2.  Choose a small EMR cluster or EMR Serverless application; review
    cost and terminate/delete lab resources afterward.
3.  Configure the required service, EC2/job execution roles, network
    access, and S3 permissions.
4.  Submit a PySpark job that reads CSV, casts columns, filters invalid
    records, aggregates sales by date, and writes Parquet to S3.
5.  Inspect driver/executor logs and output files.
6.  Register the output in Glue Data Catalog and query it with Athena.
7.  Experiment with partition count and file size; compare runtime and
    output layout.

Example transformation outline:

``` python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as sum_

spark = SparkSession.builder.appName("sales-etl").getOrCreate()
df = spark.read.option("header", True).csv("s3://YOUR_BUCKET/input/sales/")
clean = df.withColumn("amount", col("amount").cast("decimal(12,2)"))
result = clean.filter(col("amount").isNotNull()).groupBy("order_date").agg(sum_("amount").alias("sales"))
result.write.mode("overwrite").parquet("s3://YOUR_BUCKET/output/sales/")
```

**Workflow:** S3 input → EMR Spark job → distributed transformation → S3
Parquet → Glue Catalog → Athena.

**Common errors and troubleshooting** - Job fails at startup: inspect
release/application compatibility, bootstrap actions, role permissions,
and logs. - Executors lost / out of memory: inspect executor memory,
partition sizes, skew, shuffle, and instance capacity. - S3
AccessDenied: verify job/instance role, bucket policy, KMS permissions,
and credential provider. - Job cannot access private source: check
subnet, route tables, security groups, DNS, and VPC endpoints. - Cluster
costs continue after job: configure auto-termination and confirm
cluster/application lifecycle. - Too many small output files: tune
partitions/coalesce appropriately and consider compaction.

## 6. Interview preparation

### 10 conceptual questions

1.  What is Amazon EMR, and which big-data frameworks can it run?

2.  Compare EMR with AWS Glue.

3.  What is the difference between an EMR cluster and EMR Serverless?

4.  Explain the roles of primary, core, and task nodes in a cluster.

5.  What are Spark driver and executors?

6.  What is a shuffle in Spark, and why can it be expensive?

7.  Why is S3 commonly used as durable storage with EMR?

8.  What are bootstrap actions and EMR steps?

9.  How do IAM roles and security configurations protect EMR workloads?

10. What factors affect EMR performance and cost?

### 5 scenario-based questions

1.  You need to process several terabytes using custom Spark libraries
    and configurations. Would you choose Glue or EMR, and why?

2.  A Spark job is slow because one key has far more records than
    others. How would you address skew?

3.  Design a pipeline that processes daily S3 files with EMR and makes
    results queryable in Athena.

4.  A cluster is idle for hours after jobs finish. How would you reduce
    cost?

5.  An EMR job must access a private database and encrypted S3 data.
    What networking and security components are needed?

### 3 troubleshooting questions

1.  Spark executors repeatedly run out of memory. What metrics and
    tuning options do you inspect?

2.  An EMR job fails with S3 AccessDenied. Which role and resource
    policies do you validate?

3.  A cluster launches successfully but cannot reach a private data
    source. What VPC configuration do you investigate?

## 7. Revision

-   EMR is managed infrastructure for distributed frameworks such as
    Spark and Hadoop.
-   Understand cluster-based EMR versus EMR Serverless and when each
    fits.
-   Spark driver coordinates; executors process partitions; shuffles are
    costly data movement.
-   S3 is durable shared storage; cluster-local HDFS is not a substitute
    for durable data-lake storage.
-   Tune partitioning, skew, executor resources, and output file sizes.
-   Compare EMR with Glue for managed Spark ETL and Athena for
    serverless SQL.

------------------------------------------------------------------------

## Final revision: connect the services in one architecture

``` mermaid
flowchart LR
    A[Producers / databases] --> B[Kinesis or S3 ingestion]
    B --> C[S3 raw zone]
    C --> D[Glue Catalog]
    C --> E[Glue ETL or EMR Spark]
    E --> F[S3 curated zone]
    F --> G[Athena]
    F --> H[Redshift]
    I[Lambda] -. event handling .-> C
    J[IAM / KMS / Lake Formation] -. access and governance .-> C
    J -. access and governance .-> E
    J -. access and governance .-> G
    J -. access and governance .-> H
```

### End-to-end explanation to practise

A source system produces batch files or streaming events. Batch files
land in S3; streaming events can arrive through Kinesis and be delivered
to S3 or processed by consumers. IAM roles control service access. Glue
catalogs the data and can run ETL to clean, validate, partition, and
convert it to Parquet. EMR can perform large-scale or customized Spark
processing. Athena supports ad hoc SQL over S3, while Redshift serves
curated warehouse workloads. Lambda handles lightweight event-driven
tasks such as validation, routing, and triggering jobs.

### Important design habits

-   Separate raw, processed, and curated data; preserve source data
    where retention requirements allow.
-   Use least-privilege IAM roles and encryption; do not hard-code
    access keys.
-   Make jobs restartable and outputs idempotent; plan for retries and
    duplicate events.
-   Use Parquet, compression, partition pruning, and sensible file sizes
    for analytics.
-   Monitor pipeline freshness, failures, data quality, cost, and
    consumer lag.
-   Choose the simplest service that meets scale, latency, control, and
    operational requirements.

### Official documentation starting points

-   [Amazon S3 User
    Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
-   [IAM User
    Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
-   [AWS Glue Developer
    Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
-   [Amazon Athena User
    Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
-   [Amazon Redshift
    Documentation](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html)
-   [Amazon Kinesis
    Documentation](https://docs.aws.amazon.com/streams/latest/dev/introduction.html)
-   [AWS Lambda Developer
    Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
-   [Amazon EMR Management
    Guide](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html)

> **Version note:** AWS consoles, limits, pricing, engine versions, and
> feature names can change. Before implementation, verify the current
> service documentation and pricing for your Region. This guide is a
> learning roadmap, not a substitute for checking production
> requirements.
