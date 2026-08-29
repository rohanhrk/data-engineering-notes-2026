# Azure Databricks Foundation — Chapterized Data Engineer Notes

> **Source:** Microsoft Learn — Azure Databricks documentation
>
> **Purpose:** Chapter-based GitHub handbook for Azure Databricks Data Engineering, including architecture, Spark internals, Delta Lake, streaming, Lakeflow, Unity Catalog, optimization, production engineering, and certification/interview revision.
>
> **Last reviewed:** 29 August 2026

## Table of Contents

1. [Platform & Lakehouse Fundamentals](01-platform-and-lakehouse-fundamentals.md)
2. [Compute & Spark Execution Internals](02-compute-and-spark-internals.md)
3. [Delta Lake & Table Internals](03-delta-lake-and-table-internals.md)
4. [Ingestion & Streaming](04-ingestion-and-streaming.md)
5. [Lakeflow & Pipeline Engineering](05-lakeflow-and-pipeline-engineering.md)
6. [Medallion Architecture & Data Modeling](06-medallion-and-data-modeling.md)
7. [Unity Catalog, Security & Governance](07-unity-catalog-and-governance.md)
8. [Performance Engineering & Optimization](08-performance-optimization.md)
9. [Orchestration, Reliability & Observability](09-orchestration-reliability-observability.md)
10. [Production Architecture, Networking & CI/CD](10-production-architecture-and-cicd.md)
11. [Mental Models, Certification & Interview Prep](11-mental-models-and-interview-prep.md)
12. [Reference Architecture & Revision](12-reference-architecture-and-revision.md)

## Recommended study path

```text
Platform & Lakehouse
   ↓
Compute & Spark Internals
   ↓
Delta Lake & Table Internals
   ↓
Ingestion & Streaming
   ↓
Lakeflow & Pipeline Engineering
   ↓
Medallion & Data Modeling
   ↓
Unity Catalog & Governance
   ↓
Performance Engineering
   ↓
Orchestration + Reliability + Observability
   ↓
Production Architecture + CI/CD
   ↓
Mental Models + Certification / Interview Revision
```

## Current terminology

Databricks has renamed **Delta Live Tables (DLT)** to **Lakeflow pipelines** and **Databricks Asset Bundles** to **Declarative Automation Bundles**. Older projects and interview questions may still use the legacy names.
