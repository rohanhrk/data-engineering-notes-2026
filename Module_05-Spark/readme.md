# Apache Spark — End-to-End Notes

> **Source:** Apache Spark Official Documentation  
> **Documentation version checked:** Spark **4.2.0**  
> **Official docs:** https://spark.apache.org/docs/latest/

These notes turn the official Apache Spark documentation into a practical, study-friendly reference for Data Engineering. They emphasize concepts, execution, PySpark, Spark SQL/DataFrames, optimization, deployment, and Structured Streaming, while also covering RDDs, MLlib, GraphX, security, monitoring, and Spark Declarative Pipelines.

---

## Table of Contents

1. [What is Apache Spark?](#1-what-is-apache-spark)
2. [Spark Ecosystem](#2-spark-ecosystem)
3. [Spark Architecture](#3-spark-architecture)
4. [Spark Application Execution](#4-spark-application-execution)
5. [SparkSession and SparkContext](#5-sparksession-and-sparkcontext)
6. [RDDs](#6-rdds)
7. [Transformations and Actions](#7-transformations-and-actions)
8. [Narrow vs Wide Transformations](#8-narrow-vs-wide-transformations)
9. [Lazy Evaluation](#9-lazy-evaluation)
10. [DAG, Jobs, Stages and Tasks](#10-dag-jobs-stages-and-tasks)
11. [Partitions and Parallelism](#11-partitions-and-parallelism)
12. [Caching and Persistence](#12-caching-and-persistence)
13. [Broadcast Variables and Accumulators](#13-broadcast-variables-and-accumulators)
14. [DataFrames and Spark SQL](#14-dataframes-and-spark-sql)
15. [PySpark](#15-pyspark)
16. [Common DataFrame Operations](#16-common-dataframe-operations)
17. [Joins](#17-joins)
18. [Aggregations and Window Functions](#18-aggregations-and-window-functions)
19. [Data Sources and File Formats](#19-data-sources-and-file-formats)
20. [Spark SQL Execution and Optimization](#20-spark-sql-execution-and-optimization)
21. [Shuffle](#21-shuffle)
22. [Performance Tuning](#22-performance-tuning)
23. [Memory Management](#23-memory-management)
24. [Deployment and Cluster Managers](#24-deployment-and-cluster-managers)
25. [spark-submit](#25-spark-submit)
26. [Monitoring and Spark UI](#26-monitoring-and-spark-ui)
27. [Job Scheduling](#27-job-scheduling)
28. [Structured Streaming](#28-structured-streaming)
29. [Streaming State, Windows and Watermarks](#29-streaming-state-windows-and-watermarks)
30. [Checkpointing and Fault Tolerance](#30-checkpointing-and-fault-tolerance)
31. [Legacy Spark Streaming / DStreams](#31-legacy-spark-streaming--dstreams)
32. [MLlib](#32-mllib)
33. [GraphX](#33-graphx)
34. [Spark Connect](#34-spark-connect)
35. [Spark Declarative Pipelines](#35-spark-declarative-pipelines)
36. [Security](#36-security)
37. [Configuration](#37-configuration)
38. [Testing and Application Development](#38-testing-and-application-development)
39. [Common Mistakes](#39-common-mistakes)
40. [Data Engineer Interview Cheat Sheet](#40-data-engineer-interview-cheat-sheet)
41. [Official Documentation Map](#41-official-documentation-map)

---

# 1. What is Apache Spark?

Apache Spark is a distributed data processing engine designed to process large datasets across a cluster.

Spark provides APIs for:

- Python (PySpark)
- Scala
- Java
- R (deprecated in the current documentation)
- SQL

Spark can run locally or on a cluster managed by Spark Standalone, Hadoop YARN, or Kubernetes.

### Why Spark?

Spark is useful when:

- data is too large or processing is too expensive for a single machine;
- the workload needs distributed computation;
- batch and streaming processing need a common API;
- SQL-style transformations need distributed execution;
- iterative processing benefits from caching.

### Important point

Modern Spark applications generally use **DataFrames / Dataset APIs and Spark SQL** rather than low-level RDD APIs. RDDs remain supported and are still important for understanding Spark internals and for some specialized workloads.

---

# 2. Spark Ecosystem

The current documentation exposes several major Spark components.

| Component | Purpose | Priority for Data Engineering |
|---|---|---|
| Spark Core / RDD | Distributed execution primitives | High for fundamentals |
| Spark SQL | Structured data and SQL | Very High |
| DataFrames / Datasets | Structured distributed processing | Very High |
| PySpark | Python API | Very High |
| Structured Streaming | Streaming data processing | Very High |
| MLlib | Machine learning | Medium |
| GraphX | Graph processing | Low-Medium |
| SparkR | R API | Low; deprecated |
| Spark Connect | Client-server architecture | Medium |
| Declarative Pipelines | Declarative data pipelines | Emerging / useful |

### Recommended learning order for a Data Engineer

```text
Spark fundamentals
    ↓
RDD concepts
    ↓
Transformations / actions / lazy evaluation
    ↓
DAG / stages / tasks / partitions
    ↓
DataFrames + Spark SQL
    ↓
Joins + aggregations + windows
    ↓
Shuffle + performance tuning
    ↓
PySpark application development
    ↓
Structured Streaming
    ↓
Deployment / monitoring
```

---

# 3. Spark Architecture

A Spark application consists primarily of a **driver** and **executors**.

## 3.1 Driver

The driver process:

- contains the application logic;
- creates the `SparkSession` / `SparkContext`;
- builds the execution plan;
- communicates with the cluster manager;
- schedules work on executors;
- coordinates jobs, stages and tasks.

Conceptually:

```text
User Application
      |
      v
   Driver
      |
      v
Cluster Manager
      |
      +------------------+
      |                  |
      v                  v
 Executor 1          Executor 2
```

## 3.2 Executors

Executors are processes launched for a Spark application on worker nodes.

They:

- execute tasks;
- store cached / persisted data;
- perform shuffle work;
- return task results to the driver.

## 3.3 Cluster Manager

The cluster manager allocates resources.

Spark supports:

- Spark Standalone
- YARN
- Kubernetes

The cluster manager is separate from Spark's scheduling logic.

---

# 4. Spark Application Execution

A typical flow is:

```text
User submits application
        ↓
Driver starts
        ↓
SparkSession / SparkContext created
        ↓
Transformations build a logical computation
        ↓
An action triggers execution
        ↓
Spark creates a job
        ↓
DAG Scheduler splits the job into stages
        ↓
Stages are divided into tasks
        ↓
Tasks execute on executor processes
        ↓
Results are returned / written
```

### Key terms

- **Application** = complete user program.
- **Job** = computation triggered by an action.
- **Stage** = set of tasks separated by shuffle boundaries.
- **Task** = smallest unit of work sent to an executor, normally processing one partition.
- **Partition** = logical chunk of distributed data.

---

# 5. SparkSession and SparkContext

## 5.1 SparkSession

`SparkSession` is the main entry point for modern Spark SQL and DataFrame work.

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("MySparkApp")
    .getOrCreate()
)
```

Common uses:

```python
spark.read...
spark.sql(...)
spark.createDataFrame(...)
spark.conf...
```

## 5.2 SparkContext

`SparkContext` is the lower-level connection to the Spark cluster and execution environment.

It is particularly important for:

- RDD operations;
- broadcast variables;
- accumulators;
- lower-level Spark configuration.

In modern applications, access is often obtained through:

```python
sc = spark.sparkContext
```

### Rule of thumb

Use:

```text
SparkSession → DataFrames / SQL / Structured Streaming
SparkContext → low-level Spark functionality / RDD-related APIs
```

---

# 6. RDDs

RDD = **Resilient Distributed Dataset**.

It is a distributed collection of objects partitioned across cluster nodes and designed to support fault-tolerant parallel operations.

## RDD properties

### Resilient

RDDs can be recomputed after lost partitions using lineage.

### Distributed

Data is partitioned across multiple nodes.

### Dataset

RDD represents a collection of records.

## Creating RDDs

From a collection:

```python
rdd = sc.parallelize([1, 2, 3, 4, 5])
```

From a text file:

```python
rdd = sc.textFile("data.txt")
```

## Common RDD transformations

```python
map()
flatMap()
filter()
distinct()
union()
groupByKey()
reduceByKey()
sortByKey()
join()
```

## Common RDD actions

```python
collect()
count()
first()
take(n)
reduce()
foreach()
countByKey()
```

### Important warning

Avoid `collect()` on large datasets because it moves all returned data to the driver and can cause driver memory failure.

---

# 7. Transformations and Actions

Spark operations are broadly divided into **transformations** and **actions**.

## 7.1 Transformation

A transformation creates a new dataset from an existing dataset.

Examples:

```python
df.filter(...)
df.select(...)
df.withColumn(...)
rdd.map(...)
rdd.filter(...)
```

Transformations are generally lazy.

## 7.2 Action

An action asks Spark to actually execute the computation and produce a result or side effect.

Examples:

```python
df.count()
df.show()
df.collect()
df.write...
rdd.reduce(...)
```

### Simple mental model

```text
Transformation → Build plan
Action         → Execute plan
```

---

# 8. Narrow vs Wide Transformations

This distinction is central to Spark performance.

## 8.1 Narrow transformation

Each output partition depends on a small number of input partitions, often one.

Examples:

- `map`
- `filter`
- `select`
- `withColumn`
- `coalesce` in the common non-shuffle use

Conceptually:

```text
Partition 1 → Partition 1
Partition 2 → Partition 2
Partition 3 → Partition 3
```

No major redistribution of records is required.

## 8.2 Wide transformation

An output partition can depend on many input partitions. Data must usually be redistributed.

Examples:

- `groupBy`
- `groupByKey`
- `reduceByKey`
- many joins
- `distinct`
- `orderBy`
- `repartition`

Conceptually:

```text
P1 ──┐
P2 ──┼──> shuffle ──> Q1
P3 ──┘               Q2
```

### Why wide transformations matter

They can introduce:

- network transfer;
- disk I/O;
- serialization overhead;
- additional stages;
- skew-related bottlenecks.

---

# 9. Lazy Evaluation

Spark does not immediately execute most transformations.

Example:

```python
df2 = df.filter(df.age > 18)
df3 = df2.select("name", "age")
```

At this point Spark can build an execution plan without reading every record into memory.

When an action happens:

```python
df3.count()
```

Spark optimizes and executes the plan.

## Benefits

Lazy evaluation lets Spark:

- combine operations;
- eliminate unnecessary work;
- optimize execution;
- avoid materializing intermediate data unnecessarily.

### Interview statement

> Spark transformations are lazy; execution begins when an action requires a result.

---

# 10. DAG, Jobs, Stages and Tasks

## 10.1 DAG

DAG = **Directed Acyclic Graph**.

Spark builds a graph representing dependencies between computations.

Example:

```text
Read
  ↓
Filter
  ↓
Select
  ↓
GroupBy
  ↓
Count
```

## 10.2 Job

An action creates a Spark job.

Example:

```python
df.count()
```

is an action and can trigger a job.

## 10.3 Stage

A job is divided into stages, with shuffle boundaries commonly separating stages.

Example:

```text
Stage 1
Read → Filter → Select
        ↓
      Shuffle
        ↓
Stage 2
GroupBy → Aggregate
```

## 10.4 Task

A stage contains tasks.

A useful approximation is:

```text
1 partition ≈ 1 task for that stage
```

So if a stage has 200 partitions, it generally has around 200 tasks.

---

# 11. Partitions and Parallelism

A partition is a chunk of distributed data.

Spark processes partitions in parallel through tasks.

## 11.1 Why partitions matter

Too few partitions:

- poor parallelism;
- under-utilized cluster;
- long-running tasks.

Too many partitions:

- scheduling overhead;
- too many tiny tasks;
- excessive shuffle metadata / file overhead in some workloads.

## 11.2 `repartition`

```python
df2 = df.repartition(200)
```

Typically causes a full shuffle.

Use it when you need to redistribute data.

## 11.3 `coalesce`

```python
df2 = df.coalesce(20)
```

Primarily useful when reducing the number of partitions without requiring a full shuffle.

### Key difference

```text
repartition → generally shuffle
coalesce    → can reduce partitions without full shuffle
```

---

# 12. Caching and Persistence

If the same dataset is reused, recomputation can be expensive.

## Cache

```python
df.cache()
```

Equivalent to persisting using the default storage level for the API.

## Persist

```python
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_AND_DISK)
```

Choose persistence based on workload and memory availability.

## Remove cached data

```python
df.unpersist()
```

## When to cache

Good use cases:

- reused DataFrame/RDD;
- iterative algorithm;
- interactive analysis;
- expensive upstream computation used multiple times.

Poor use case:

```text
Dataset used once + large enough to create memory pressure
```

### Important concept

Caching is not automatically faster. It costs memory/storage and can increase pressure on the cluster if applied blindly.

---

# 13. Broadcast Variables and Accumulators

## 13.1 Broadcast variables

Broadcast variables allow a read-only value to be efficiently distributed to executors rather than repeatedly shipping it with tasks.

Example:

```python
lookup = {1: "US", 2: "IN", 3: "UK"}
broadcast_lookup = sc.broadcast(lookup)

rdd.map(lambda x: broadcast_lookup.value.get(x)).collect()
```

Useful when:

- a lookup table is relatively small;
- many tasks need the same read-only data.

Do not use a broadcast variable when its size is too large for executor memory.

## 13.2 Accumulators

Accumulators are variables that tasks can add to and whose aggregated value can be read by the driver.

Conceptual example:

```python
counter = sc.accumulator(0)
```

Typical use cases:

- counters;
- diagnostic metrics.

They should not be treated as the primary mechanism for implementing business logic because task retries can make side-effect reasoning tricky.

---

# 14. DataFrames and Spark SQL

DataFrames are distributed tables with named columns.

Example:

```python
df = spark.read.parquet("/data/sales")
```

A DataFrame provides:

- named columns;
- schema information;
- SQL-style operations;
- optimized execution through Spark SQL.

Spark SQL can execute the same underlying execution engine regardless of whether the user expresses the operation through SQL or DataFrame APIs.

## SQL example

```python
df.createOrReplaceTempView("sales")

result = spark.sql("""
    SELECT customer_id, SUM(amount) AS total_amount
    FROM sales
    GROUP BY customer_id
""")
```

## DataFrame equivalent

```python
from pyspark.sql import functions as F

result = (
    df.groupBy("customer_id")
      .agg(F.sum("amount").alias("total_amount"))
)
```

### Which should you use?

Use whichever expresses the transformation most clearly. Both use Spark's SQL execution engine for structured workloads.

---

# 15. PySpark

PySpark is Spark's Python API.

## Basic installation

For a compatible Python environment:

```bash
pip install pyspark
```

For the current Spark 4.2.0 documentation, the supported baseline includes Python 3.10+.

## Start PySpark

```bash
pyspark
```

Or, using Spark binaries:

```bash
./bin/pyspark
```

## Minimal application

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Example")
    .getOrCreate()
)

sales = spark.read.parquet("sales.parquet")

sales.groupBy("country").count().show()

spark.stop()
```

## Python-specific considerations

Python code runs through the PySpark API and may involve communication between Python and JVM processes.

For performance-sensitive Python transformations:

- prefer built-in Spark SQL functions;
- avoid unnecessary Python UDFs;
- use vectorized / Arrow-based options where supported and appropriate;
- reduce Python-side loops over distributed data.

---

# 16. Common DataFrame Operations

## Select

```python
df.select("name", "age")
```

## Filter

```python
df.filter(df.age > 18)
```

or:

```python
df.where("age > 18")
```

## Add / replace a column

```python
from pyspark.sql import functions as F

df = df.withColumn("age_plus_1", F.col("age") + 1)
```

## Rename

```python
df = df.withColumnRenamed("old_name", "new_name")
```

## Drop

```python
df = df.drop("temporary_column")
```

## Sort

```python
df.orderBy(F.col("amount").desc())
```

## Distinct

```python
df.select("customer_id").distinct()
```

## Limit

```python
df.limit(20)
```

## Sample

```python
df.sample(withReplacement=False, fraction=0.1, seed=42)
```

## Explain

```python
df.explain()
```

Use `explain()` to inspect the query plan when debugging performance.

---

# 17. Joins

Joins combine rows using matching keys or join conditions.

## Common join types

- inner
- left
- right
- full / outer
- left semi
- left anti
- cross

Example:

```python
result = orders.join(
    customers,
    on="customer_id",
    how="inner"
)
```

## Left join

```python
orders.join(customers, "customer_id", "left")
```

## Left anti join

Useful for finding rows in one side that do not match the other side.

```python
orders.join(customers, "customer_id", "left_anti")
```

## Join performance

Important considerations:

- size of each relation;
- partitioning;
- join keys;
- skew;
- broadcast opportunities;
- shuffle volume.

### Broadcast join concept

If one side is sufficiently small, broadcasting it can avoid a large shuffle of that side.

---

# 18. Aggregations and Window Functions

## 18.1 Grouped aggregation

```python
result = (
    df.groupBy("department")
      .agg(
          F.count("*").alias("employees"),
          F.avg("salary").alias("avg_salary"),
          F.max("salary").alias("max_salary")
      )
)
```

## 18.2 Common aggregation functions

```text
count
countDistinct
sum
avg
min
max
first
last
collect_list
collect_set
```

## 18.3 Window functions

Window functions calculate values over a related set of rows without collapsing the rows like `groupBy` does.

Example:

```python
from pyspark.sql.window import Window

window = Window.partitionBy("department").orderBy(F.col("salary").desc())

df = df.withColumn("rank", F.row_number().over(window))
```

Common window functions:

```text
row_number
rank
dense_rank
lag
lead
sum over window
avg over window
```

### `groupBy` vs window

```text
groupBy → reduces many rows into fewer rows
window  → keeps row-level output while adding calculations based on neighboring/related rows
```

---

# 19. Data Sources and File Formats

Spark SQL supports multiple data sources and connectors through its data source architecture.

Common formats:

- Parquet
- ORC
- JSON
- CSV
- text
- JDBC databases

## Read CSV

```python
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("sales.csv")
)
```

## Read JSON

```python
df = spark.read.json("events.json")
```

## Read Parquet

```python
df = spark.read.parquet("sales.parquet")
```

## Write Parquet

```python
df.write.mode("overwrite").parquet("output/sales")
```

## Read JDBC

Conceptually:

```python
df = (
    spark.read
    .format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "sales")
    .option("user", username)
    .option("password", password)
    .load()
)
```

### Data engineering preference

For analytic data pipelines, columnar formats such as Parquet or ORC are typically much more efficient than raw CSV for repeated distributed analytics because they support schema information and column-oriented access.

---

# 20. Spark SQL Execution and Optimization

Spark SQL knows more about structured data than a generic RDD computation.

This enables query planning and optimization.

A conceptual lifecycle is:

```text
SQL / DataFrame code
        ↓
Logical plan
        ↓
Analyzed logical plan
        ↓
Optimized logical plan
        ↓
Physical plan
        ↓
Executed plan
```

## Inspect a plan

```python
df.explain(True)
```

Use this to understand:

- filters;
- projections;
- joins;
- exchanges / shuffles;
- scans;
- aggregation operators;
- physical execution choices.

## Catalyst and execution

Spark SQL's optimizer can apply logical optimizations before the physical plan is selected.

The underlying execution engine is shared by SQL and DataFrame APIs for structured workloads.

### Practical lesson

Prefer expressions using built-in DataFrame / SQL functions because Spark can understand and optimize them better than opaque custom Python logic in many cases.

---

# 21. Shuffle

Shuffle is the redistribution of data across partitions, usually across executors, so records can be grouped or aligned by a key or ordering requirement.

Typical operations that can cause shuffle:

- `groupBy`
- `join`
- `distinct`
- `orderBy`
- `repartition`
- some window operations

Conceptually:

```text
Executor A ──┐
Executor B ──┼──> Network shuffle ──> New partition layout
Executor C ──┘
```

## Why shuffle is expensive

Shuffle can involve:

- network transfer;
- serialization;
- disk I/O;
- sorting / aggregation;
- large intermediate data;
- skewed partitions.

### Interview question

**Why is `groupBy` slower than `filter`?**

Because `groupBy` usually requires data redistribution by key, while `filter` can normally operate independently on each input partition.

---

# 22. Performance Tuning

Spark performance optimization is mostly about reducing unnecessary data movement and making effective use of cluster resources.

## 22.1 Filter early

Instead of:

```python
df.join(big_df, "id").filter(F.col("country") == "IN")
```

Prefer pushing the filter as early as correctness permits:

```python
filtered = df.filter(F.col("country") == "IN")
result = filtered.join(big_df, "id")
```

Spark SQL can perform some predicate pushdown / reordering automatically, but expressing efficient logic clearly still matters.

## 22.2 Select only required columns

Avoid carrying unnecessary columns through joins and shuffles.

```python
df = df.select("id", "amount")
```

## 22.3 Avoid unnecessary `collect()`

Bad for large data:

```python
rows = df.collect()
```

The data is brought to the driver.

## 22.4 Avoid unnecessary repartitioning

Every shuffle has a cost.

## 22.5 Use broadcast joins where appropriate

For a small dimension table, broadcasting can significantly reduce shuffle work.

## 22.6 Handle data skew

One partition containing far more records than others can create straggler tasks.

Symptoms:

```text
Most tasks complete quickly
One or a few tasks remain running for much longer
```

Possible techniques include:

- better partitioning;
- filtering useless data early;
- broadcasting small sides;
- key salting for appropriate skewed joins;
- adaptive query execution features where applicable;
- avoiding poorly distributed keys.

## 22.7 Partition sizing

Tune partition counts so work is balanced without creating an excessive number of tiny tasks.

## 22.8 Cache only when reuse justifies it

Caching a dataset used only once can waste memory.

---

# 23. Memory Management

Spark executors need memory for several categories of work, including:

- execution;
- cached data;
- shuffle structures;
- JVM overhead;
- Python worker processes where applicable.

## Common memory failures

### Executor OOM

A task or executor requires more memory than available.

Possible causes:

- oversized partitions;
- large aggregations;
- skew;
- excessive caching;
- large broadcasts.

### Driver OOM

Often caused by collecting too much data to the driver.

Common examples:

```python
df.collect()
df.toPandas()
```

on unexpectedly large datasets.

### Practical fixes

- reduce data before collecting;
- increase partition count when tasks are oversized;
- avoid unnecessary caching;
- address skew;
- select fewer columns;
- use appropriate executor memory and overhead settings.

---

# 24. Deployment and Cluster Managers

Spark can run:

- locally;
- in Spark Standalone mode;
- on YARN;
- on Kubernetes.

## 24.1 Local mode

```bash
pyspark --master local[*]
```

Useful for development and testing.

## 24.2 Spark Standalone

Spark provides its own cluster manager.

Master URL example:

```text
spark://HOST:PORT
```

## 24.3 YARN

Spark can run as an application on Hadoop YARN.

Master URL:

```text
yarn
```

## 24.4 Kubernetes

Spark applications can run on Kubernetes.

Master URL begins with a Kubernetes API server endpoint such as:

```text
k8s://...
```

---

# 25. spark-submit

`spark-submit` is the standard command-line mechanism for launching Spark applications.

Generic structure:

```bash
spark-submit \
  --master <master-url> \
  --deploy-mode <deploy-mode> \
  --conf key=value \
  application.py
```

## Important options

### `--master`

Selects the cluster manager / execution mode.

### `--deploy-mode`

Common values:

```text
client
cluster
```

### `--executor-memory`

Controls executor memory.

### `--num-executors`

Commonly used with YARN and some deployment environments.

### `--conf`

Pass Spark configuration settings.

## Example

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --executor-memory 4g \
  --num-executors 4 \
  app.py
```

### Configuration precedence

A configuration explicitly set in the application generally has higher precedence than command-line settings, which in turn take precedence over default configuration files such as `spark-defaults.conf`.

---

# 26. Monitoring and Spark UI

Spark provides a Web UI for monitoring applications.

## Application UI

The application Web UI is normally available on port `4040` while an application is running.

It provides information about:

- jobs;
- stages;
- tasks;
- executors;
- storage / cached data;
- SQL queries;
- environment information.

## Why the Spark UI is important

When debugging a slow job, inspect:

```text
SQL tab
Jobs tab
Stages tab
Executors tab
Environment tab
Storage tab
```

Look for:

- long-running stages;
- high shuffle read/write;
- skewed task durations;
- spill to disk;
- executor failures;
- excessive GC;
- uneven partition sizes.

## Event logs and History Server

For historical application analysis, enable event logging and configure a Spark History Server.

Typical configuration:

```text
spark.eventLog.enabled=true
spark.eventLog.dir=<shared-event-log-location>
```

The History Server uses those event logs to reconstruct application UIs after the application has finished.

---

# 27. Job Scheduling

Spark has scheduling mechanisms for:

- scheduling stages within an application;
- sharing cluster resources across applications;
- controlling resource allocation.

## Important ideas

### FIFO

First-in-first-out scheduling is a common default behavior for jobs in an application.

### Fair scheduling

Fair scheduling can allow concurrent jobs to receive a more balanced share of resources.

### Multiple applications

Cluster managers also determine how resources are allocated between applications.

### Key interview point

There are two useful levels to distinguish:

```text
Cluster manager → allocates cluster resources to applications
Spark scheduler → schedules jobs / stages / tasks inside the Spark application
```

---

# 28. Structured Streaming

Structured Streaming is Spark's modern stream-processing engine built on the Spark SQL engine.

It lets you express streaming computations using DataFrame / Dataset-style APIs.

Conceptually:

```text
Streaming source
      ↓
Streaming DataFrame
      ↓
Transformations
      ↓
Aggregation / Join / Window
      ↓
Streaming sink
```

## Batch vs streaming

### Batch

Input is bounded.

### Streaming

Input is continuously arriving / unbounded.

Structured Streaming lets the same structured APIs be used across static and streaming data in many cases.

## Example

```python
from pyspark.sql import functions as F

stream_df = (
    spark.readStream
    .format("rate")
    .option("rowsPerSecond", 10)
    .load()
)

result = stream_df.groupBy(
    F.window("timestamp", "1 minute")
).count()
```

Start the query:

```python
query = (
    result.writeStream
    .format("console")
    .outputMode("complete")
    .start()
)

query.awaitTermination()
```

---

# 29. Streaming State, Windows and Watermarks

## 29.1 Event time

Event time is the timestamp carried by the event itself.

This matters when records arrive late or out of order.

## 29.2 Processing time

Processing time is when Spark processes the record.

These can differ significantly in real systems.

## 29.3 Windowing

A window groups data according to time intervals.

Example:

```python
F.window("event_time", "10 minutes")
```

Common concepts:

- tumbling windows;
- sliding windows;
- session-style windows, depending on API/workload.

## 29.4 Watermark

A watermark tells Spark how far it can advance event-time state while tolerating late-arriving records.

Example concept:

```python
stream_df.withWatermark("event_time", "10 minutes")
```

The important idea is:

```text
Watermark = bound used to control state for late events
```

A watermark is not simply a statement that events can never arrive late. It is used by the engine to determine when old state can be considered safe to remove according to the query semantics.

## 29.5 Stateful operations

Examples include:

- streaming aggregations;
- stream-stream joins;
- operations that maintain information across micro-batches.

State must be stored reliably so a query can recover.

---

# 30. Checkpointing and Fault Tolerance

Structured Streaming uses checkpointing for recovery.

Example:

```python
query = (
    result.writeStream
    .option("checkpointLocation", "/checkpoints/my-query")
    .start()
)
```

Checkpointing can store information such as:

- progress / offsets;
- state information for stateful queries;
- metadata required for recovery.

## Important rule

A checkpoint directory belongs to the logical query and should be treated carefully. Changing certain query-defining configurations can make an old checkpoint incompatible.

The official documentation also notes that some state-partitioning-related configurations should not be changed after a query has already run with an existing checkpoint.

---

# 31. Legacy Spark Streaming / DStreams

Spark also has an older streaming API called **Spark Streaming**, based on DStreams.

DStreams represent a continuous stream as a sequence of RDDs.

Conceptually:

```text
DStream
 ↓
RDD batch 1
RDD batch 2
RDD batch 3
...
```

### Modern recommendation

For new structured streaming workloads, **Structured Streaming** is the preferred API.

DStreams remain useful when maintaining legacy systems or when studying Spark history.

---

# 32. MLlib

MLlib is Spark's machine-learning library.

The current documentation provides a machine-learning guide covering topics such as:

- classification;
- regression;
- clustering;
- collaborative filtering;
- feature engineering;
- pipelines;
- model evaluation;
- tuning.

For a Data Engineer, the main value is understanding how Spark can support distributed feature preparation and ML pipelines.

### Typical pipeline idea

```text
Raw data
   ↓
Cleaning
   ↓
Feature engineering
   ↓
Feature vector
   ↓
Model
   ↓
Evaluation
   ↓
Prediction
```

---

# 33. GraphX

GraphX is Spark's graph-processing API.

A graph contains:

- vertices;
- edges;
- properties / attributes.

Example concepts:

```text
User A ──follows──> User B
User B ──follows──> User C
```

Graph processing can support use cases such as:

- network analysis;
- relationship analysis;
- graph algorithms.

For most modern Data Engineer preparation, GraphX is lower priority than Spark SQL, DataFrames, and Structured Streaming.

---

# 34. Spark Connect

Spark Connect is a client-server architecture introduced in Spark 3.4.

The architecture separates the client application from the Spark execution environment.

Conceptually:

```text
Client application
       |
       | Spark Connect protocol
       v
Spark Connect server
       |
       v
Spark execution cluster
```

Benefits include:

- remote connectivity;
- separation of client and server;
- easier integration of Spark into applications.

PySpark DataFrame API support is part of Spark Connect's modern architecture.

---

# 35. Spark Declarative Pipelines

Spark 4.2 documentation includes Spark Declarative Pipelines.

The goal is to define data pipelines declaratively rather than manually managing every execution step.

Conceptually:

```text
Define pipeline / tables
        ↓
Spark determines execution
        ↓
Maintain data products
```

This is an emerging part of the Spark ecosystem compared with the long-established DataFrame and SQL APIs.

For traditional Data Engineering preparation, prioritize:

```text
DataFrames → SQL → transformations → joins → partitions → shuffle → tuning → streaming
```

Then learn Declarative Pipelines as an advanced topic.

---

# 36. Security

Spark security configuration can address areas such as:

- authentication;
- network encryption;
- authorization-related controls;
- UI security;
- RPC security;
- local filesystem permissions;
- secret handling / credentials.

## Security mindset

A production Spark environment should consider:

```text
Who can submit jobs?
Who can access the Spark UI?
Who can read event logs?
How is executor/driver communication protected?
Where are credentials stored?
Which data sources are accessible?
```

Never place plaintext secrets directly in application source code.

---

# 37. Configuration

Spark configuration can be supplied through several mechanisms, including:

- `SparkConf` / application configuration;
- `spark-submit --conf`;
- `spark-defaults.conf`;
- environment / deployment configuration;
- cluster-manager-specific settings.

## Examples

```python
spark.conf.set("spark.sql.shuffle.partitions", 200)
```

or:

```bash
spark-submit \
  --conf spark.sql.shuffle.partitions=200 \
  app.py
```

## Important categories

### Application settings

Example:

```text
spark.app.name
```

### SQL settings

Examples:

```text
spark.sql.shuffle.partitions
spark.sql.adaptive.enabled
```

### Executor settings

Examples:

```text
spark.executor.memory
spark.executor.cores
```

### Driver settings

Examples:

```text
spark.driver.memory
spark.driver.cores
```

### Streaming settings

Examples include state-store and streaming behavior settings.

### Rule

Do not tune random configuration values blindly. First identify the bottleneck through the Spark UI, query plan, metrics, and workload characteristics.

---

# 38. Testing and Application Development

A production Spark application should separate:

```text
Configuration
Business logic
Spark session creation
Input/output
Tests
```

## Development pattern

```python
from pyspark.sql import SparkSession


def build_spark():
    return (
        SparkSession.builder
        .appName("SalesPipeline")
        .getOrCreate()
    )


def transform(df):
    # Business logic here
    return df.filter("amount > 0")


def main():
    spark = build_spark()

    df = spark.read.parquet("input")
    result = transform(df)
    result.write.mode("overwrite").parquet("output")

    spark.stop()


if __name__ == "__main__":
    main()
```

This structure makes transformations easier to unit-test.

---

# 39. Common Mistakes

## Mistake 1 — `collect()` on huge data

```python
df.collect()
```

Can overload the driver.

## Mistake 2 — Too many `withColumn` chains blindly

Sometimes a large number of transformations can make plans harder to reason about. Prefer clear expressions and inspect plans when necessary.

## Mistake 3 — Unnecessary `repartition`

Each repartition can create a shuffle.

## Mistake 4 — Using Python UDFs everywhere

Built-in Spark functions often allow more optimization than opaque Python code.

## Mistake 5 — Caching everything

Cache only reused data when the storage cost is justified.

## Mistake 6 — Ignoring data skew

One oversized partition can dominate total job time.

## Mistake 7 — Ignoring the execution plan

Use:

```python
df.explain(True)
```

## Mistake 8 — Ignoring Spark UI

The UI is one of the best sources of evidence when diagnosing a performance issue.

---

# 40. Data Engineer Interview Cheat Sheet

## Spark basics

### What is Spark?

A distributed data processing engine that supports batch, SQL, structured streaming, machine learning, and other distributed workloads.

### Why is Spark fast?

It uses distributed execution, lazy evaluation, query optimization, in-memory persistence when useful, parallel processing, and efficient execution strategies.

### What is an RDD?

A fault-tolerant distributed collection of records partitioned across a cluster.

### What is a DataFrame?

A distributed dataset organized into named columns, with Spark SQL providing structural information used for optimization.

### What is a transformation?

An operation that builds a new dataset / plan from an existing one and is generally lazy.

### What is an action?

An operation that triggers execution and produces a result or side effect.

### What is lazy evaluation?

Spark delays executing transformations until an action requires the result.

### What is a shuffle?

Redistribution of data across partitions, typically involving network and disk I/O.

### What is a stage?

A group of tasks that can execute without crossing a shuffle boundary.

### What is a task?

The unit of execution for a partition of data within a stage.

### What is a partition?

A logical chunk of distributed data processed by a task.

### What is the difference between `repartition` and `coalesce`?

`repartition` generally causes a shuffle; `coalesce` can reduce partitions without a full shuffle.

### What is broadcast?

Distribution of a read-only value to executors so it can be reused efficiently by tasks.

### What is caching?

Persisting a computed dataset so reused computations can avoid recomputation.

### What causes a job to become slow?

Common causes include:

- large shuffles;
- data skew;
- too few / too many partitions;
- expensive joins;
- excessive serialization;
- Python overhead;
- executor memory pressure;
- unnecessary recomputation;
- inefficient file layouts.

### How do you debug a slow Spark job?

A practical sequence:

```text
1. Inspect Spark UI
2. Identify slow stage
3. Check task skew
4. Check shuffle read/write
5. Check spills and memory
6. Inspect physical plan
7. Check partition counts
8. Inspect joins / aggregations
9. Optimize data volume and partitioning
10. Re-run and compare metrics
```

---

# 41. Official Documentation Map

Use the official documentation for details beyond these notes.

| Topic | Official Documentation |
|---|---|
| Main documentation | https://spark.apache.org/docs/latest/ |
| Quick Start | https://spark.apache.org/docs/latest/quick-start.html |
| RDD Programming Guide | https://spark.apache.org/docs/latest/rdd-programming-guide.html |
| SQL / DataFrames / Datasets | https://spark.apache.org/docs/latest/sql-programming-guide.html |
| SQL Reference | https://spark.apache.org/docs/latest/sql-ref.html |
| PySpark | https://spark.apache.org/docs/latest/api/python/ |
| PySpark Tutorials | https://spark.apache.org/docs/latest/api/python/tutorial/index.html |
| Structured Streaming | https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html |
| Tuning | https://spark.apache.org/docs/latest/tuning.html |
| Configuration | https://spark.apache.org/docs/latest/configuration.html |
| Cluster Overview | https://spark.apache.org/docs/latest/cluster-overview.html |
| Submitting Applications | https://spark.apache.org/docs/latest/submitting-applications.html |
| Monitoring | https://spark.apache.org/docs/latest/monitoring.html |
| Job Scheduling | https://spark.apache.org/docs/latest/job-scheduling.html |
| Security | https://spark.apache.org/docs/latest/security.html |
| MLlib | https://spark.apache.org/docs/latest/ml-guide.html |
| GraphX | https://spark.apache.org/docs/latest/graphx-programming-guide.html |
| Spark Connect | https://spark.apache.org/docs/latest/spark-connect-overview.html |
| Declarative Pipelines | https://spark.apache.org/docs/latest/declarative-pipelines-programming-guide.html |
| Migration Guide | https://spark.apache.org/docs/latest/migration-guide.html |

---

# Recommended Study Path

For Data Engineering, study these notes in this order:

```text
01. Spark architecture
02. SparkSession / SparkContext
03. RDD fundamentals
04. Transformations and actions
05. Narrow vs wide transformations
06. Lazy evaluation
07. DAG → Job → Stage → Task
08. Partitions and parallelism
09. Cache / persist
10. Broadcast / accumulators
11. DataFrames
12. Spark SQL
13. Joins
14. Aggregations
15. Window functions
16. File formats and data sources
17. Query plans
18. Shuffle
19. Performance tuning
20. Memory and skew
21. spark-submit
22. Cluster deployment
23. Spark UI / monitoring
24. Structured Streaming
25. Watermarks / state / checkpointing
26. Advanced topics
```

---

# One-Page Mental Model

```text
                         APACHE SPARK
                              |
        +---------------------+---------------------+
        |                     |                     |
      Batch                  SQL               Streaming
        |                     |                     |
      RDDs               DataFrames           Structured Streaming
        |                Datasets                    |
        +-------------------+------------------------+
                            |
                       Spark Engine
                            |
                    +-------+-------+
                    |               |
                 Driver         Executors
                    |               |
             DAG / Scheduler    Tasks / Cache
                    |
             Jobs → Stages
                    |
               Partitions
                    |
              Shuffle when needed
```

## Core idea to remember

> **Spark turns a high-level data transformation into a distributed execution plan, divides the work across partitions, schedules tasks on executors, and uses optimization plus parallelism to process large datasets efficiently.**

---

## Notes vs Official Documentation

These notes are a **study-oriented synthesis** of the official documentation, not a replacement for the API reference. For exact syntax, configuration defaults, supported options, version-specific behavior, and migration details, always consult the official Spark 4.2.0 documentation.

### Primary source

Apache Spark Official Documentation:  
https://spark.apache.org/docs/latest/

### Version note

The official documentation currently identifies itself as **Spark 4.2.0**. Spark APIs and configuration behavior can change between releases, so version-specific documentation should be checked when working on a production project.
