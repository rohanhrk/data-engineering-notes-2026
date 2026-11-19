# AWS Data Engineering Study Notes (0–2 YOE)

Eight self-contained Markdown study guides covering the core AWS services used in Data Engineering. Each file follows the same seven-part structure and can be read on its own.

## Files

| # | File | Service | What you will learn |
|---|---|---|---|
| 1 | [01_amazon_s3.md](01_amazon_s3.md) | Amazon S3 | Buckets/objects, storage classes, lifecycle, versioning, replication, encryption, policies, events, multipart upload, partitioning and data lake design. Project: secure, partitioned retail data lake. |
| 2 | [02_aws_iam.md](02_aws_iam.md) | AWS IAM | Users, groups, roles, policy types, trust vs permission policies, STS/AssumeRole, cross-account access, PassRole, least privilege. Project: least-privilege Glue role and assumable analyst role. |
| 3 | [03_aws_glue.md](03_aws_glue.md) | AWS Glue | Data Catalog, crawlers, ETL jobs, DynamicFrames, bookmarks, workers/DPUs, workflows, Data Quality. Project: CSV → partitioned Parquet with catalog registration. |
| 4 | [04_amazon_athena.md](04_amazon_athena.md) | Amazon Athena | Serverless SQL on S3, external tables, partitioning and projection, CTAS, workgroups, optimisation, Iceberg. Project: CSV vs Parquet scan-cost comparison and CTAS aggregate. |
| 5 | [05_amazon_redshift.md](05_amazon_redshift.md) | Amazon Redshift | MPP architecture, Serverless, distribution/sort keys, COPY/UNLOAD, Spectrum, materialised views, WLM. Project: Redshift Serverless load, MERGE upsert and materialised view. |
| 6 | [06_amazon_kinesis.md](06_amazon_kinesis.md) | Amazon Kinesis | Data Streams, shards, partition keys, consumers, enhanced fan-out, KCL, Firehose, Flink overview. Project: real-time clickstream to S3. |
| 7 | [07_aws_lambda.md](07_aws_lambda.md) | AWS Lambda | Execution model, triggers, concurrency, retries/DLQs, idempotency, SQS/Kinesis integration, packaging. Project: S3-triggered validation with an idempotency ledger. |
| 8 | [08_amazon_emr.md](08_amazon_emr.md) | Amazon EMR | Cluster nodes, EMRFS vs HDFS, YARN/Spark, steps, scaling, Spot, EMR Serverless/EKS. Project: PySpark job on EMR Serverless. |

## Structure of every file
1. Introduction
2. Architecture and working mechanism (Mermaid diagrams)
3. Core concepts and terminology
4. Data Engineering use cases (two end-to-end pipelines)
5. Hands-on mini-project (objective → cleanup)
6. Interview preparation: 10 conceptual, 5 scenario-based and 3 troubleshooting questions, each fully answered
7. Revision and quick reference (cheat sheet + 10 rapid-fire questions)

## Suggested study order
S3 → IAM → Glue → Athena → Redshift → Lambda → Kinesis → EMR. The mini-projects reuse one S3 bucket and sample dataset created in the S3 file, so do the S3 project first.

## Notes
- **Costs:** several projects create billable resources (Glue, Redshift Serverless, Kinesis, EMR Serverless, Secrets Manager). Each project ends with cleanup commands — run them.
- **Verify before relying on numbers:** quotas, prices, runtimes, release labels and defaults change. Each file links the official documentation and quotas pages.
- **Mermaid:** diagrams render in GitHub, VS Code (with a Mermaid extension), Obsidian and most Markdown viewers.
