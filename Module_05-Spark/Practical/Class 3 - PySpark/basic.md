# PySpark DataFrame Fundamentals

This document covers the basic PySpark DataFrame operations, including:

- Creating a Spark Session
- Creating DataFrames
- Using Schema
- Reading CSV files from Amazon S3
- Selecting Columns
- Renaming Columns using Alias
- Adding New Columns using `withColumn()`

---

# 1. Spark Session and Imports

## Purpose

A **SparkSession** is the entry point to every PySpark application.

It allows us to:

- Create DataFrames
- Read and write files
- Execute Spark SQL queries
- Access Spark Context

---

## Code

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions

spark = SparkSession.builder \
    .appName("foodapps-practical-pyspark-learning") \
    .getOrCreate()

sc = spark.sparkContext

print("Spark Version:", spark.version)
print("Application ID:", sc.applicationId)
```

---

## Explanation

### SparkSession

Creates or retrieves an existing Spark application.

```python
SparkSession.builder
```

starts configuring a Spark application.

---

### appName()

Assigns a name to the Spark application.

```python
.appName("foodapps-practical-pyspark-learning")
```

This name appears in:

- Spark UI
- YARN
- EMR
- Logs

---

### getOrCreate()

```python
.getOrCreate()
```

- Creates a new Spark Session if one does not exist.
- Otherwise returns the existing session.

---

### Spark Context

```python
sc = spark.sparkContext
```

Spark Context is the connection between your application and the Spark Cluster.

Useful for:

- Broadcast Variables
- Accumulators
- RDD operations

---

### Spark Version

```python
spark.version
```

Returns the Spark version currently running.

Example:

```
4.0.0
```

---

### Application ID

```python
sc.applicationId
```

Returns a unique identifier for the running Spark application.

Example:

```
application_1754392342342_0001
```

---

# 2. Create DataFrame Without Schema

## Sample Data

```python
dark_store_rows = [
    ("DS_001", "Bengaluru", "Koramangala", 12, True),
    ("DS_002", "Bengaluru", "Marathahalli", 15, True),
    ("DS_003", "Bengaluru", "Indiranagar", 13, True),
    ("DS_004", "Assam", "Guwahati", 19, False),
]
```

---

## Method 1: Without Column Names

```python
dark_store_df = spark.createDataFrame(dark_store_rows)
```

Spark automatically assigns column names:

```
_col0
_col1
_col2
_col3
_col4
```

### Print Schema

```python
dark_store_df.printSchema()
```

### Display Data

```python
dark_store_df.show(truncate=False)
```

---

## Method 2: With Column Names

```python
dark_store_df = spark.createDataFrame(
    dark_store_rows,
    [
        "store_id",
        "city",
        "zone",
        "target_delivery_minutes",
        "is_active"
    ]
)
```

Spark automatically infers the data types while using the provided column names.

---

## Output Schema

```
store_id                 string
city                     string
zone                     string
target_delivery_minutes  long
is_active                boolean
```

---

# 3. Create DataFrame with Custom Schema

## Why Use a Schema?

Instead of allowing Spark to infer data types, we can define them explicitly.

Benefits:

- Better performance
- Consistent data types
- Prevents incorrect inference
- Better documentation

---

## Define Schema

```python
from pyspark.sql import types as t

sla_schema = t.StructType([
    t.StructField("order_channel", t.StringType(), False),
    t.StructField("priority_level", t.StringType(), False),
    t.StructField("target_minutes", t.IntegerType(), False),
    t.StructField("free_delivery_threshold", t.DoubleType(), False)
])
```

---

## Create DataFrame

```python
sla_rules_df = spark.createDataFrame(
    sla_rows,
    schema=sla_schema
)
```

---

## Display Schema

```python
sla_rules_df.printSchema()
```

---

## Display Data

```python
sla_rules_df.show(truncate=False)
```

---

# 4. Reading CSV Files from Amazon S3

## Define S3 Paths

```python
S3_BUCKET = "spark-file-storage"
BASE_PREFIX = "spark-learning/foodapps"

RAW_BASE_PATH = f"s3://{S3_BUCKET}/{BASE_PREFIX}/raw"
OUTPUT_BASE_PATH = f"s3://{S3_BUCKET}/{BASE_PREFIX}/output"
```

---

## Store File Paths

```python
foodapps_files = {
    "faps_access_puf": f"{RAW_BASE_PATH}/faps_access_puf.csv",
    "faps_fafhevent_puf": f"{RAW_BASE_PATH}/faps_fafhevent_puf.csv",
    "faps_fafhitem_puf": f"{RAW_BASE_PATH}/faps_fafhitem_puf.csv"
}
```

---

## Read CSV File

```python
faps_access_puf_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("multiline", "false") \
    .option("quote", '"') \
    .option("escape", '"') \
    .csv(foodapps_files["faps_access_puf"])
```

---

## CSV Options Explained

| Option | Description |
|---------|-------------|
| header | Uses the first row as column names |
| inferSchema | Automatically detects data types |
| multiline | Reads records as single-line entries |
| quote | Specifies the quote character |
| escape | Handles escaped quote characters |

---

## Display Schema

```python
df.printSchema()
```

---

## Display Records

```python
df.show(truncate=False)
```

---

## Display Column Names

```python
print(df.columns)
```

Returns a Python list of all column names.

Example:

```python
['hhnum', 'eventid', 'athome']
```

---

# 5. Select Columns

The `select()` transformation retrieves only the required columns from a DataFrame.

```python
faps_fafhevent_puf_df = faps_fafhevent_puf_df.select(
    "hhnum",
    "eventid",
    "athome"
)
```

---

## Display Data

```python
faps_fafhevent_puf_df.show(truncate=False)
```

---

# 6. Rename Columns using Alias

The `alias()` function changes the display name of a column.

```python
from pyspark.sql import functions as f

faps_fafhevent_puf_df = faps_fafhevent_puf_df.select(
    f.col("hhnum").alias("household_id"),
    f.col("eventid").alias("event_id"),
    f.col("athome").alias("at_home")
)
```

---

## Output

| Original | New Name |
|----------|----------|
| hhnum | household_id |
| eventid | event_id |
| athome | at_home |

---

# 7. Add New Column using withColumn()

The `withColumn()` transformation creates a new column or replaces an existing one.

---

## Syntax

```python
DataFrame.withColumn(column_name, expression)
```

---

## Example

```python
faps_fafhevent_puf_df = faps_fafhevent_puf_df.withColumn(
    "event_source",
    f.lit("food_at_home")
)
```

---

## Explanation

- `withColumn()` creates a new column.
- `lit()` creates a constant (literal) value.
- Every row receives the value `"food_at_home"`.

---

## Output

| household_id | event_id | at_home | event_source |
|--------------|----------|---------|--------------|
| 101 | 201 | 1 | food_at_home |
| 102 | 202 | 0 | food_at_home |

---

# Summary

| Topic | Function Used |
|--------|---------------|
| Create Spark Session | `SparkSession.builder.getOrCreate()` |
| Create DataFrame | `createDataFrame()` |
| Define Schema | `StructType()` |
| Read CSV | `spark.read.csv()` |
| View Schema | `printSchema()` |
| Display Records | `show()` |
| View Columns | `columns` |
| Select Columns | `select()` |
| Rename Columns | `alias()` |
| Add New Column | `withColumn()` |
| Constant Value | `lit()` |

---

## Key Takeaways

- `SparkSession` is the starting point for all PySpark applications.
- `createDataFrame()` creates a DataFrame from Python collections.
- Defining a schema explicitly improves consistency and performance.
- `spark.read.csv()` is commonly used to load CSV files from Amazon S3.
- `select()` retrieves only the required columns.
- `alias()` renames columns without modifying the original data.
- `withColumn()` adds or replaces columns in a DataFrame.
- `lit()` is used to assign constant values to every row.