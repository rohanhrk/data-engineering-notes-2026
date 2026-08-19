# Running PySpark Jobs on Amazon EMR using Spark Submit

This guide explains how to:

1. Connect to an EMR Application Master using SSH
2. Create a PySpark application
3. Upload the Python file to the EMR master node
4. Validate the Python file
5. Run the application using `spark-submit`
6. Run the job locally for debugging
7. Submit the job on YARN
8. Monitor and troubleshoot the application

---

# 1. Architecture

When running a Spark job on EMR using YARN:

```text
                    AWS
                     |
                     v
              +-------------+
              | EMR Cluster |
              +-------------+
                     |
              +-------------+
              | Application |
              |    Master   |
              |  (EC2 Node) |
              +-------------+
                     |
          SSH        |
        ------------>
                     |
              spark-submit
                     |
                     v
              +-------------+
              |    YARN     |
              | ResourceMgr |
              +-------------+
                     |
          +----------+----------+
          |                     |
          v                     v
    +-----------+         +-----------+
    | Executor 1|         | Executor 2|
    +-----------+         +-----------+
          |
          v
       Amazon S3
```

The Application Master/EMR primary node is where we normally execute:

```bash
spark-submit
```

YARN then manages the Spark application's resources.

---

# 2. SSH into the EMR Application Master

First, connect to the EMR primary node.

From your local machine:

```bash
ssh -i your-key.pem hadoop@<EMR-PUBLIC-DNS>
```

Example:

```bash
ssh -i my-key.pem hadoop@ec2-xx-xx-xx-xx.compute.amazonaws.com
```

Depending on the EMR setup, the user may be:

```text
hadoop
```

or:

```text
ec2-user
```

After connecting, verify the machine:

```bash
hostname
```

Example:

```text
ip-172-31-79-200.ec2.internal
```

---

# 3. Move to the Application Directory

For example:

```bash
cd /home/ec2-user
```

Check the current directory:

```bash
pwd
```

List files:

```bash
ls -lh
```

---

# 4. Create the PySpark Application

Create a Python file:

```bash
vi fhvhv_zone_analytics_unoptimized.py
```

Or:

```bash
nano fhvhv_zone_analytics_unoptimized.py
```

If using `vi`:

### Enter editing mode

Press:

```text
i
```

Now you can type or paste your Python code.

### Save and exit

Press:

```text
Esc
```

Then type:

```text
:wq
```

and press:

```text
Enter
```

---

# 5. Exit vi Without Saving Changes

If you opened the file and don't want to save your changes:

```text
Esc
:q!
```

Then press:

```text
Enter
```

Meaning:

```text
:q!     → Quit without saving
:wq     → Save and quit
```

---

# 6. Validate the Python Syntax

Before submitting the Spark application, first check whether Python syntax is valid.

Run:

```bash
python3 -m py_compile fhvhv_zone_analytics_unoptimized.py
```

If there is no output, the Python syntax is valid.

You can also check:

```bash
echo $?
```

Expected:

```text
0
```

---

# 7. Important: Python vs PySpark

Do not use:

```bash
python3 test.py
```

to test a PySpark application unless the machine has PySpark configured for the normal Python interpreter.

For example:

```bash
python3 -c "from pyspark.sql.types import StructType, StructField; print('OK')"
```

may return:

```text
ModuleNotFoundError: No module named 'pyspark'
```

This does **not necessarily mean Spark is broken**.

On EMR, PySpark is commonly configured through:

```bash
spark-submit
```

Therefore, test the Spark application using:

```bash
spark-submit
```

rather than directly using:

```bash
python3
```

---

# 8. Upload the Python File to EMR

There are two common approaches.

## Option 1: Create the file directly on EMR

SSH into the EMR node:

```bash
ssh -i your-key.pem hadoop@<EMR-PUBLIC-DNS>
```

Then:

```bash
cd /home/ec2-user
vi fhvhv_zone_analytics_unoptimized.py
```

Paste the Python code and save it.

---

## Option 2: Upload the file using SCP

From your local machine:

```bash
scp -i your-key.pem fhvhv_zone_analytics_unoptimized.py \
ec2-user@<EMR-PUBLIC-DNS>:/home/ec2-user/
```

Then SSH into EMR:

```bash
ssh -i your-key.pem ec2-user@<EMR-PUBLIC-DNS>
```

Check:

```bash
ls -lh /home/ec2-user/
```

You should see:

```text
fhvhv_zone_analytics_unoptimized.py
```

---

# 9. Check the Python File

Run:

```bash
ls -lh fhvhv_zone_analytics_unoptimized.py
```

Then:

```bash
head -20 fhvhv_zone_analytics_unoptimized.py
```

To inspect the entire file:

```bash
cat fhvhv_zone_analytics_unoptimized.py
```

For a large file, use:

```bash
less fhvhv_zone_analytics_unoptimized.py
```

Exit `less` using:

```text
q
```

---

# 10. Test the Spark Environment

Check Spark:

```bash
spark-submit --version
```

Example:

```text
version 3.5.6
```

Check Java:

```bash
java -version
```

Check Hadoop:

```bash
hadoop version
```

Check YARN:

```bash
yarn version
```

---

# 11. Verify S3 Input Data

Before running the Spark application, verify that the S3 files actually exist.

For example:

```bash
aws s3 ls s3://spark-file-storage/spark-learning/rides/tripdata/
```

Check the zone lookup:

```bash
aws s3 ls s3://spark-file-storage/spark-learning/rides/tripzone/
```

You should see files such as:

```text
taxi_zone_lookup.csv
```

---

# 12. Run Spark in Local Mode

Local mode is useful for debugging the Python application before involving YARN.

Run:

```bash
spark-submit \
  --master local[*] \
  fhvhv_zone_analytics_unoptimized.py \
  --trip-input "s3://spark-file-storage/spark-learning/rides/tripdata/*.parquet" \
  --zone-input "s3://spark-file-storage/spark-learning/rides/tripzone/taxi_zone_lookup.csv" \
  --output-base "s3://spark-file-storage/spark-learning/rides/unoptimized"
```

Here:

```text
--master local[*]
```

means:

```text
Run Spark locally on the current EMR node.
```

There is no YARN executor allocation.

The current machine acts as the Spark driver and executor.

---

# 13. Run Spark on YARN

Once the application works in local mode, submit it to YARN.

Example:

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --conf spark.dynamicAllocation.enabled=false \
  --driver-memory 5g \
  --driver-cores 1 \
  --executor-memory 4g \
  --executor-cores 2 \
  --num-executors 3 \
  --conf spark.sql.shuffle.partitions=400 \
  fhvhv_zone_analytics_unoptimized.py \
  --trip-input "s3://spark-file-storage/spark-learning/rides/tripdata/*.parquet" \
  --zone-input "s3://spark-file-storage/spark-learning/rides/tripzone/taxi_zone_lookup.csv" \
  --output-base "s3://spark-file-storage/spark-learning/rides/unoptimized"
```

---

# 14. Understand the Spark Submit Configuration

## Master

```bash
--master yarn
```

Tells Spark:

```text
Use YARN as the cluster manager.
```

---

## Deploy Mode

```bash
--deploy-mode cluster
```

The Spark driver runs inside the YARN ApplicationMaster container.

Architecture:

```text
spark-submit
     |
     v
ResourceManager
     |
     v
ApplicationMaster
     |
     +--------> Driver
     |
     +--------> Executors
```

---

## Driver Memory

```bash
--driver-memory 5g
```

The driver gets approximately:

```text
5 GB
```

of memory.

---

## Driver Cores

```bash
--driver-cores 1
```

The driver gets:

```text
1 CPU core
```

---

## Executor Memory

```bash
--executor-memory 4g
```

Each executor gets:

```text
4 GB
```

of executor memory.

---

## Executor Cores

```bash
--executor-cores 2
```

Each executor gets:

```text
2 CPU cores
```

---

## Number of Executors

```bash
--num-executors 3
```

Spark requests:

```text
3 executors
```

Therefore:

```text
3 executors
×
2 cores
=
6 executor cores
```

---

## Shuffle Partitions

```bash
--conf spark.sql.shuffle.partitions=400
```

Spark will initially create:

```text
400 shuffle partitions
```

for SQL/DataFrame shuffle operations.

This is relevant for operations such as:

```text
groupBy()
join()
orderBy()
distinct()
```

---

# 15. Check the Running Application

When running on YARN, find the application:

```bash
yarn application -list
```

Example:

```text
application_1787026250186_0001
```

You can also check:

```bash
yarn application -status application_1787026250186_0001
```

---

# 16. View YARN Logs

If the Spark application fails, get the logs using:

```bash
yarn logs -applicationId application_1787026250186_0001
```

For only the ApplicationMaster logs:

```bash
yarn logs \
  -applicationId application_1787026250186_0001 \
  -am ALL
```

You can also save the logs:

```bash
yarn logs \
  -applicationId application_1787026250186_0001 \
  > spark-job.log
```

Then inspect:

```bash
less spark-job.log
```

---

# 17. Exit a YARN Log Command

If you are viewing logs using:

```bash
yarn logs -applicationId <application-id>
```

and `Ctrl+C` is not working because the output is being viewed through a pager, try:

```text
q
```

If you are inside `less`:

```text
q
```

If the command is actively running and not inside a pager:

```text
Ctrl+C
```

should terminate it.

---

# 18. Spark UI

When running in local mode:

```text
http://<EMR-PUBLIC-DNS>:4040
```

The Spark UI contains:

```text
Jobs
Stages
Storage
Environment
Executors
SQL
```

For performance analysis, the most important tabs are:

```text
SQL
Stages
Executors
```

---

# 19. YARN ResourceManager UI

The YARN ResourceManager UI is usually available on:

```text
http://<EMR-MASTER>:8088
```

It allows you to see:

```text
Applications
Application State
Memory Used
VCores Used
Application Attempts
```

---

# 20. Debugging a Failed Spark Application

If Spark reports:

```text
Application ... failed
```

don't immediately assume that YARN is the problem.

Look for the actual Python exception.

For example:

```text
SparkUserAppException:
User application exited with 1
```

means the Python application itself exited with an error.

The important error is normally located earlier in the ApplicationMaster logs.

Run:

```bash
yarn logs -applicationId <APPLICATION_ID>
```

Then search:

```text
ERROR
Exception
Traceback
Caused by
```

---

# 21. Common Exit Codes

## Exit Code 1

```text
User application exited with status 1
```

Usually indicates an application-level failure.

Examples:

```text
Python error
Import error
Invalid DataFrame operation
Invalid column name
Bad input path
S3 permission issue
```

---

## Exit Code 13

You may see:

```text
Container exited with a non-zero exit code 13
```

Do not immediately assume that exit code 13 is the root cause.

Look for:

```text
User application exited with status 1
```

and then find the underlying Python exception.

---

# 22. Example: Python Import Error

Suppose the code contains:

```python
from pyspark.sql.types import IntegerType, StringType, StruckField, StruckType
```

This is incorrect.

The correct imports are:

```python
from pyspark.sql.types import IntegerType, StringType, StructField, StructType
```

Then the schema should be:

```python
ZONE_SCHEMA = StructType(
    [
        StructField("LocationID", IntegerType(), nullable=False),
        StructField("Borough", StringType(), nullable=True),
        StructField("Zone", StringType(), nullable=True),
        StructField("service_zone", StringType(), nullable=True),
    ]
)
```

---

# 23. Check Python Syntax

Run:

```bash
python3 -m py_compile fhvhv_zone_analytics_unoptimized.py
```

This checks Python syntax.

However, it does not execute Spark code.

For example, it will not verify:

```python
spark.read.parquet(...)
```

or:

```python
df.groupBy(...)
```

For that, use:

```bash
spark-submit
```

---

# 24. Remove Files from /home/ec2-user

Check files first:

```bash
ls -lh /home/ec2-user
```

Remove a specific file:

```bash
rm /home/ec2-user/file.py
```

Example:

```bash
rm /home/ec2-user/test.py
```

Remove multiple files:

```bash
rm file1.py file2.py file3.py
```

Remove a directory:

```bash
rm -r directory_name
```

For safety, use:

```bash
rm -i file.py
```

It will ask for confirmation.

**Avoid:**

```bash
rm -rf /home/ec2-user/*
```

unless you are absolutely sure you want to delete everything in that directory.

---

# 25. Useful Linux Commands

### Current directory

```bash
pwd
```

### List files

```bash
ls
```

### Detailed list

```bash
ls -lh
```

### Change directory

```bash
cd /home/ec2-user
```

### Go up one directory

```bash
cd ..
```

### Go to home directory

```bash
cd ~
```

### View file

```bash
cat file.py
```

### Edit file

```bash
vi file.py
```

### Search inside file

```bash
grep "ERROR" spark-job.log
```

### Search recursively

```bash
grep -R "Exception" .
```

### Check disk usage

```bash
df -h
```

### Check directory size

```bash
du -sh /home/ec2-user
```

---

# 26. Recommended Debugging Workflow

Use the following workflow for Spark development.

```text
             Write Python Code
                    |
                    v
             Upload to EMR
                    |
                    v
          python3 -m py_compile
                    |
                    v
             Syntax Valid?
              /          \
            No            Yes
            |              |
            v              v
        Fix Code      spark-submit
                           |
                           v
                    --master local[*]
                           |
                           v
                    Application Works?
                     /            \
                   No              Yes
                   |                |
                   v                v
              Debug Logs      Submit to YARN
                                    |
                                    v
                             spark-submit
                              --master yarn
                                    |
                                    v
                              YARN Application
                                    |
                                    v
                              Monitor Logs
```

---

# 27. Recommended Development Strategy

For learning Spark performance, avoid immediately running a large job on YARN.

Use:

```text
Step 1
Write code

        ↓

Step 2
Compile Python

        ↓

Step 3
Run small test dataset

        ↓

Step 4
Run local[*]

        ↓

Step 5
Inspect Spark UI

        ↓

Step 6
Run on YARN

        ↓

Step 7
Compare execution plans

        ↓

Step 8
Optimize the application
```

---

# 28. Important Spark Performance Concepts

For this particular FHVHV application, pay attention to:

### Wide transformations

```text
join()
groupBy()
```

These can cause shuffle.

### Late filtering

Current approach:

```text
Read
 ↓
Derive columns
 ↓
Join
 ↓
Filter
 ↓
Aggregation
```

An optimized approach would generally try to reduce data earlier:

```text
Read
 ↓
Filter
 ↓
Select required columns
 ↓
Join
 ↓
Aggregation
```

### Broadcast Join

The taxi-zone lookup is very small.

An optimized version could potentially use:

```python
F.broadcast(pickup_zones)
```

instead of forcing a shuffle join.

### AQE

Current job:

```python
.config("spark.sql.adaptive.enabled", "false")
```

Optimized job:

```python
.config("spark.sql.adaptive.enabled", "true")
```

### Caching

The current application intentionally does not cache the common upstream DataFrame.

Therefore:

```text
Daily aggregation
       |
       v
Scan → Join → Filter → Aggregate

Monthly aggregation
       |
       v
Scan → Join → Filter → Aggregate
```

The common lineage may be recomputed for the two actions.

---

# 29. Final Spark Submit Command

For the current unoptimized application:

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --conf spark.dynamicAllocation.enabled=false \
  --driver-memory 5g \
  --driver-cores 1 \
  --executor-memory 4g \
  --executor-cores 2 \
  --num-executors 3 \
  --conf spark.sql.shuffle.partitions=400 \
  fhvhv_zone_analytics_unoptimized.py \
  --trip-input "s3://spark-file-storage/spark-learning/rides/tripdata/*.parquet" \
  --zone-input "s3://spark-file-storage/spark-learning/rides/tripzone/taxi_zone_lookup.csv" \
  --output-base "s3://spark-file-storage/spark-learning/rides/unoptimized"
```

---

# 30. Quick Reference

| Task | Command |
| --- | --- |
| SSH to EMR | `ssh -i key.pem user@host` |
| Current directory | `pwd` |
| List files | `ls -lh` |
| Edit Python | `vi file.py` |
| Save vi | `Esc` → `:wq` |
| Exit vi without saving | `Esc` → `:q!` |
| Python syntax check | `python3 -m py_compile file.py` |
| Spark version | `spark-submit --version` |
| Local Spark | `spark-submit --master local[*] file.py` |
| YARN Spark | `spark-submit --master yarn ...` |
| List YARN apps | `yarn application -list` |
| Application status | `yarn application -status <id>` |
| YARN logs | `yarn logs -applicationId <id>` |
| View logs | `less spark-job.log` |
| Exit `less` | `q` |
| Delete file | `rm file.py` |
| Check disk | `df -h` |
| S3 files | `aws s3 ls s3://bucket/path/` |

---

# 31. Key Takeaway

For Spark development on EMR, remember this sequence:

```text
SSH
 ↓
Create / Upload .py
 ↓
python3 -m py_compile
 ↓
spark-submit --master local[*]
 ↓
Debug
 ↓
spark-submit --master yarn --deploy-mode cluster
 ↓
YARN logs
 ↓
Spark UI
 ↓
Analyze stages / shuffle / joins
 ↓
Optimize
```

The most important distinction is:

```text
python3
   ↓
Only normal Python environment

spark-submit
   ↓
Spark + PySpark + Hadoop + YARN environment
```

Therefore, a `ModuleNotFoundError: No module named 'pyspark'` from plain `python3` does not by itself mean that your EMR Spark environment is broken. Use `spark-submit` to execute the actual PySpark application.
