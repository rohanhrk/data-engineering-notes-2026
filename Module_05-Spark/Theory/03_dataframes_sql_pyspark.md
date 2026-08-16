# DataFrames, Spark SQL & PySpark

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
