# MLlib, GraphX, Spark Connect & Declarative Pipelines

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
