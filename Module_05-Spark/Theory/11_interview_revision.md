# Common Mistakes, Interview & Revision

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

---

# 70. Master Interview Mental Model

## Q1. Why is Spark fast?

A strong answer:

> Spark is fast because it performs distributed parallel processing, builds an execution plan from transformations, can pipeline narrow operations, minimizes unnecessary work through lazy evaluation and query optimization, and can reuse data through caching when appropriate. It also uses efficient execution strategies for structured workloads.

## Q2. What is a partition?

> A partition is a logical chunk of a distributed dataset. Spark creates tasks at the partition level, so partitions are the basic unit of parallel work.

## Q3. What creates a stage boundary?

> A shuffle dependency typically creates a stage boundary because downstream work depends on data being redistributed across partitions.

## Q4. What is a task?

> A task is a unit of execution that processes one partition for one stage.

## Q5. Why is skew dangerous?

> Skew creates uneven partition sizes. A few tasks may process much more data than the others, becoming stragglers and extending stage completion time.

## Q6. How do you fix skew?

> First identify the skew in Spark UI, then consider salting, splitting hot keys, increasing parallelism, reducing unnecessary shuffle, or broadcasting a small side of a join. For Spark SQL workloads, also evaluate Spark's skew-handling optimizations available in the deployed version.

## Q7. When should you use `cache()`?

> Cache a dataset when it is expensive to compute and is reused by multiple downstream actions. Do not cache data that is only used once.

## Q8. `repartition()` vs `coalesce()`?

> Use `repartition()` when you need a reshuffle to increase or rebalance partitions. Use `coalesce()` mainly to reduce partition count while minimizing data movement.

## Q9. Driver OOM vs executor OOM?

> Driver OOM usually comes from collecting too much data or building large driver-side objects. Executor OOM usually comes from oversized partitions/tasks, shuffles, joins, aggregation, caching, or insufficient executor/overhead memory.

## Q10. How do you debug a slow Spark job?

```text
1. Identify the slow job
2. Open Spark UI
3. Find the slow stage
4. Inspect task duration distribution
5. Check shuffle read/write
6. Check skewed tasks
7. Check spills
8. Check input/output size
9. Inspect the physical plan
10. Tune code / partitions / memory / joins
11. Re-run and compare
```

---

---

# 71. One-Stop Spark Execution Cheat Sheet

```text
                           SPARK APPLICATION
                                  |
                                  v
                              DRIVER
                                  |
                    +-------------+-------------+
                    |                           |
               Transformations               Action
                    |                           |
                    +----------- LAZY ----------+
                                  |
                                  v
                               DAG
                                  |
                         DAG / Query Scheduler
                                  |
                       +----------+----------+
                       |                     |
                  Stage 0                Stage 1
                       |                     |
              +--------+--------+     +------+------+
              |        |        |     |      |      |
             Task     Task     Task  Task   Task   Task
              |        |        |     |      |      |
          Partition Partition Partition ...  Partition
                       |
                       v
                    EXECUTORS
                       |
             +---------+---------+
             |                   |
        Execution Memory    Storage Memory
             |                   |
        shuffle/join/      cache/persist/
        sort/aggregate       broadcast
```

### The most important chain

```text
Data
 ↓
Partitions
 ↓
Transformations
 ↓
Lazy DAG
 ↓
Action
 ↓
Job
 ↓
Shuffle boundaries
 ↓
Stages
 ↓
Tasks
 ↓
Executors
 ↓
Result / Output
```

---

---

# 73. Final Revision Checklist

Use this checklist before an interview or project review:

- [ ] Explain why Spark is used over traditional MapReduce for many workloads.
- [ ] Explain Driver, Executor, Cluster Manager, Task.
- [ ] Explain RDD, DataFrame, Dataset.
- [ ] Explain partitioning and parallelism.
- [ ] Explain narrow vs wide transformations.
- [ ] Explain lazy evaluation.
- [ ] Explain DAG, Job, Stage, Task.
- [ ] Identify what causes shuffle.
- [ ] Explain `repartition()` vs `coalesce()`.
- [ ] Explain cache vs persist.
- [ ] Explain broadcast and accumulators.
- [ ] Explain `groupByKey()` vs `reduceByKey()`.
- [ ] Explain join strategies and broadcast joins.
- [ ] Explain data skew and salting.
- [ ] Explain driver OOM vs executor OOM.
- [ ] Explain executor memory at a high level.
- [ ] Explain client vs cluster deployment mode.
- [ ] Write a basic `spark-submit` command.
- [ ] Read the Spark UI to locate a bottleneck.
- [ ] Explain Structured Streaming basics.
- [ ] Explain checkpointing, state, windows, and watermarks.
- [ ] Explain why DataFrame/SQL workloads can be more optimizable than raw RDD code.

---
