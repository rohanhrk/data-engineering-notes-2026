# Security, Configuration & Testing

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
