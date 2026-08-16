# Apache Spark — Topic-Wise Notes

This repository is organized into topic-wise Markdown files for end-to-end Apache Spark study. The notes combine the official Apache Spark documentation with the provided Spark Class 1 and Class 2 material.

## Structure

| File | Focus |
|---|---|
| `01-fundamentals` | Spark overview, ecosystem, architecture, application lifecycle |
| `02-rdd-execution` | RDDs, transformations, actions, lazy evaluation, DAG, jobs, stages, tasks |
| `03-dataframes-sql-pyspark` | DataFrames, Spark SQL, PySpark, joins, aggregations, windows, data sources |
| `04-shuffle-partitioning-performance` | Partitions, shuffle, skew, repartition/coalesce, tuning |
| `05-deployment-submit` | Cluster managers, deployment modes, `spark-submit` |
| `06-monitoring-scheduling` | Spark UI, monitoring and scheduling |
| `07-streaming` | Structured Streaming, state, windows, watermarks, checkpoints, DStreams |
| `08-advanced-components` | MLlib, GraphX, Spark Connect, Declarative Pipelines |
| `09-security-config-testing` | Security, configuration and testing |
| `10-failure-memory` | Executor memory, failures, driver/executor OOM |
| `11-interview-revision` | Common mistakes, interview questions, revision cheat sheets |
| `12-source-map` | Official docs, class-note source alignment and repository guidance |

## Suggested Study Order

```text
Fundamentals
   ↓
RDD + Execution Model
   ↓
DataFrame + Spark SQL + PySpark
   ↓
Partitions + Shuffle + Performance
   ↓
Deployment + spark-submit + Monitoring
   ↓
Structured Streaming
   ↓
Advanced Components
   ↓
Failure + Memory + Interview Revision
```

## Diagrams

Diagrams are written in **Mermaid** inside the Markdown files. GitHub can render Mermaid diagrams in Markdown.

## Sources

- Apache Spark Official Documentation: https://spark.apache.org/docs/latest/
- Spark Class 1 PPT supplied for these notes
- Spark Class 2 PPT supplied for these notes
