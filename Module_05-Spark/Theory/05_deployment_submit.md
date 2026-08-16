# Deployment, Cluster Managers & spark-submit

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

---

# 53. Spark Deployment Modes

## 53.1 Local mode

Spark runs on one machine. This is useful for:

- learning;
- development;
- unit testing;
- debugging.

Example:

```bash
spark-submit --master local[*] app.py
```

## 53.2 Client mode

The class deck's YARN explanation is:

```text
Submitting machine
       |
     Driver
       |
       +------> YARN ResourceManager
                       |
                  ApplicationMaster
                       |
                    Executors
                       |
                  <-----> Driver
```

The driver remains on the machine from which the application is submitted.

## 53.3 Cluster mode

The driver runs inside the cluster.

```text
YARN Cluster
   |
ApplicationMaster
   |
 Driver
   |
 Executors
```

### Interview comparison

| Mode | Driver location |
|---|---|
| Local | Your local machine |
| Client | Submission machine |
| Cluster | Inside cluster |

---

---

# 57. `spark-submit` - Class 2

`spark-submit` is the standard command-line launcher for Spark applications.

## General form

```bash
spark-submit \\
  --class <main-class> \\
  --master <master-url> \\
  --deploy-mode <client|cluster> \\
  --conf <key>=<value> \\
  <application> \\
  [application-arguments]
```

For Python:

```bash
spark-submit \\
  --master local[4] \\
  --py-files dependencies.zip \\
  app.py \\
  arg1 arg2
```

## Common options

- `--master`: cluster manager / execution target.
- `--deploy-mode`: client or cluster.
- `--executor-memory`: executor heap memory.
- `--driver-memory`: driver memory.
- `--executor-cores`: cores assigned to each executor.
- `--num-executors`: initial/static executor count on applicable cluster managers.
- `--conf`: arbitrary Spark configuration.
- `--py-files`: distribute Python dependencies.

## Example

```bash
spark-submit \\
  --master yarn \\
  --deploy-mode cluster \\
  --executor-memory 4G \\
  --driver-memory 2G \\
  --executor-cores 4 \\
  --num-executors 5 \\
  --conf spark.sql.shuffle.partitions=200 \\
  application.py
```

> **Version note:** Configuration names, defaults, cluster-manager behavior, and recommended sizing should always be checked against the Spark version and cluster platform.

---
