# Apache Kafka — Complete Interview Notes

> **Purpose:** Simple, structured Kafka documentation for Data Engineering study and interview preparation.  
> **Primary references:** Apache Kafka and Confluent Kafka documentation.

## Official Documentation

- Apache Kafka Documentation: https://kafka.apache.org/documentation/
- Apache Kafka 4.3 Getting Started: https://kafka.apache.org/43/getting-started/introduction/
- Apache Kafka 4.3 Streams: https://kafka.apache.org/43/streams/developer-guide/
- Confluent Kafka Documentation: https://docs.confluent.io/kafka/introduction.html
- Confluent Documentation: https://docs.confluent.io/kafka/index.html

---

# 1. What is Kafka?

**Apache Kafka is a distributed event streaming platform.**

Kafka allows applications to:

- Publish events
- Subscribe to events
- Store events durably
- Process events in real time or later

Simple model:

```text
Producer
   |
   | Event
   v
Kafka Topic
   |
   | Event
   v
Consumer
```

Kafka is commonly used for:

- Real-time data pipelines
- Event-driven architectures
- Microservices communication
- Streaming analytics
- Data integration
- CDC pipelines

---

# 2. Kafka Architecture

```text
                    Kafka Cluster
        +----------------------------------+
        |                                  |
        |  Broker 1   Broker 2   Broker 3 |
        |                                  |
        +----------------------------------+
                 |              |
                 v              v
              Topics         Topics
                 |
                 v
             Partitions
                 |
                 v
          Consumer Groups
                 |
                 v
             Consumers
```

Main concepts:

```text
Producer
   ↓
Topic
   ↓
Partition
   ↓
Offset
   ↓
Consumer Group
   ↓
Consumer
```

---

# 3. Broker

A **broker** is a Kafka server.

A Kafka cluster contains multiple brokers.

```text
+----------+    +----------+    +----------+
| Broker 1 |    | Broker 2 |    | Broker 3 |
+----------+    +----------+    +----------+
```

Brokers store partitions and handle producer and consumer requests.

---

# 4. Topic

A **topic** is a named stream/category of events.

Examples:

```text
orders
payments
customers
inventory
```

A topic can have multiple producers and consumers.

Kafka retains events according to the topic's retention configuration.

---

# 5. Partition

A topic is divided into partitions.

```text
orders topic

Partition 0:
[Event 1] [Event 4] [Event 7]

Partition 1:
[Event 2] [Event 5] [Event 8]

Partition 2:
[Event 3] [Event 6] [Event 9]
```

Partitions provide:

- Parallelism
- Scalability
- Distribution
- Ordering within a partition

---

# 6. Partition Key

A producer can send a record with a **key**.

Example:

```text
Key = customer_id
Value = order details
```

Records with the same key are normally routed to the same partition when the default partitioning behavior is used.

This is useful when ordering is required for a particular entity.

```text
customer_101
     |
     +----> Partition 2
     |
     +----> Partition 2
     |
     +----> Partition 2
```

---

# 7. Ordering

Kafka guarantees ordering within a partition.

```text
Partition 0

Offset 0 -> Event A
Offset 1 -> Event B
Offset 2 -> Event C
Offset 3 -> Event D
```

Kafka does not provide global ordering across multiple partitions.

> **Interview point:** Ordering is guaranteed within a partition.

---

# 8. Producer

A **producer** is a client application that publishes events to Kafka.

```text
Application
     |
     v
 Producer
     |
     v
 Kafka Topic
```

Example:

```text
Order Application
       |
       | Order Created
       v
   orders topic
```

---

# 9. Consumer

A **consumer** reads and processes events from Kafka.

```text
Kafka Topic
     |
     v
 Consumer
     |
     v
Processing
```

Consumers use offsets to remember their position.

---

# 10. Consumer Group

A **consumer group** is a set of consumers working together.

```text
Topic: orders

P0 ---> Consumer 1
P1 ---> Consumer 2
P2 ---> Consumer 3

Consumer Group: order-processing
```

Within a consumer group, a partition is assigned to at most one consumer at a time.

---

# 11. Consumer Group Scaling

Example:

```text
Partitions = 4
Consumers = 4

P0 -> C1
P1 -> C2
P2 -> C3
P3 -> C4
```

If:

```text
Partitions = 4
Consumers = 6
```

then:

```text
P0 -> C1
P1 -> C2
P2 -> C3
P3 -> C4

C5 -> idle
C6 -> idle
```

So, for a single consumer group, the number of active consumers cannot exceed the number of partitions.

---

# 12. Multiple Consumer Groups

Different consumer groups can consume the same topic independently.

```text
                  orders topic
                       |
             +---------+---------+
             |                   |
             v                   v
        Consumer Group A    Consumer Group B
             |                   |
             v                   v
        Order Service        Analytics
```

Each group maintains its own offsets.

---

# 13. Offset

An **offset** is the position of a record within a partition.

```text
Partition 0

Offset 0 -> Event A
Offset 1 -> Event B
Offset 2 -> Event C
Offset 3 -> Event D
```

Think of the offset as a bookmark.

```text
Consumer
   |
   v
Offset 2
   |
   v
Continue reading
```

---

# 14. Offset Management

Offset management is one of the most important Kafka interview topics.

A consumer needs to know:

> **Which records have I already processed?**

Kafka consumers use offsets to track this position.

## Consumer Position vs Committed Offset

```text
Partition

0    1    2    3    4    5
|    |    |    |    |    |
A    B    C    D    E    F
               ^
               |
         Consumer position
```

The **current position** is where the consumer is currently reading.

The **committed offset** is the position the consumer has stored as its progress.

```text
Current position
       |
       v
      5

Committed offset
       |
       v
      4
```

If the consumer crashes, it can resume from the committed position.

---

# 15. Automatic Offset Commit

Kafka consumers can automatically commit offsets.

Important configuration:

```text
enable.auto.commit=true
```

When automatic commits are enabled, the consumer periodically commits offsets.

Conceptually:

```text
Consumer reads records
        |
        v
Processes records
        |
        v
Commits offsets periodically
```

Automatic commits are convenient but need careful configuration because a crash can occur between processing and committing.

---

# 16. Manual Offset Commit

A consumer can commit offsets explicitly.

```text
Read record
    |
    v
Process record
    |
    v
Processing successful
    |
    v
Commit offset
```

This gives the application more control over processing and offset management.

---

# 17. Why Offset Management Matters

Consider:

```text
Kafka
 |
 +--> Event A
 +--> Event B
 +--> Event C
```

Consumer processes:

```text
A ✓
B ✓
C ✗
```

If the committed offset is before `C`, the consumer can restart and process `C` again.

This is why offset management is closely related to **delivery semantics**.

---

# 18. `auto.offset.reset`

This configuration determines what happens when the consumer has no valid committed offset for a partition.

Common values:

```text
earliest
latest
none
```

### `earliest`

Start from the earliest available offset.

```text
0 -> 1 -> 2 -> 3 -> 4
^
|
Start
```

Useful when you want to process available historical data.

### `latest`

Start from the latest position.

```text
0 -> 1 -> 2 -> 3 -> 4
                  ^
                  |
                Start
```

Useful when you primarily want new events.

### `none`

Throw an error if no committed offset exists.

---

# 19. Offset Reset and Reprocessing

Because Kafka retains events, a consumer can move its offsets and process events again.

```text
Original:

0 -> 1 -> 2 -> 3 -> 4
               ^
               |
             Current
```

Reset:

```text
0 -> 1 -> 2 -> 3 -> 4
     ^
     |
   Start again
```

This is useful for:

- Reprocessing
- Backfilling
- Bug recovery
- Rebuilding downstream data

---

# 20. Consumer Rebalancing

A **rebalance** happens when partition ownership needs to change within a consumer group.

Examples:

- Consumer joins the group
- Consumer leaves
- Consumer crashes
- Number of partitions changes

Example:

```text
Before:

P0 -> C1
P1 -> C2
P2 -> C3
```

If C2 fails:

```text
After rebalance:

P0 -> C1
P1 -> C3
P2 -> C1
```

Kafka redistributes partitions among available consumers.

---

# 21. Replication

Kafka can replicate partitions across brokers.

```text
Partition 0

Broker 1 -> Leader
Broker 2 -> Replica
Broker 3 -> Replica
```

Replication provides:

- Fault tolerance
- High availability
- Data durability

---

# 22. Leader and Followers

For a replicated partition:

```text
Partition 0

Broker 1 -> Leader
Broker 2 -> Follower
Broker 3 -> Follower
```

The leader handles normal requests for the partition.

Followers replicate the leader's data.

If the leader fails, an eligible replica can become leader.

---

# 23. Retention

Kafka does not normally delete an event after a consumer reads it.

Instead, events are retained according to topic configuration.

```text
Event written
     |
     v
Kafka stores event
     |
     v
Consumer reads event
     |
     v
Event remains
     |
     v
Retention policy removes it
```

This allows consumers to process events at different times.

---

# 24. Log Compaction

Kafka supports **log compaction**.

With compaction, Kafka keeps the latest value for a key, subject to compaction semantics and configuration.

Example:

```text
Key = customer_101

customer_101 -> Address A
customer_101 -> Address B
customer_101 -> Address C
```

After compaction, the latest value can be retained:

```text
customer_101 -> Address C
```

Useful for:

- Current state
- Customer profiles
- Configuration
- Database change streams

### Retention vs Compaction

```text
Retention:
Remove old records based on time/size policy.

Compaction:
Keep the latest record for a key.
```

---

# 25. Kafka Record Structure

A Kafka record can conceptually contain:

```text
Record
+----------------+
| Key            |
| Value          |
| Timestamp      |
| Headers        |
| Partition      |
| Offset         |
+----------------+
```

Example:

```text
Key       = customer_101
Value     = {"order_id": 5001, "amount": 2000}
Timestamp = event timestamp
Headers   = optional metadata
```

Partition and offset identify where the record is stored/read.

---

# 26. Producer Configuration

Important producer configurations:

### `acks`

Controls the producer acknowledgment behavior.

Common values:

```text
acks=0
acks=1
acks=all
```

`acks=all` provides the strongest acknowledgment level.

### `retries`

Controls retry behavior for transient failures.

### `enable.idempotence`

Supports idempotent producing to help avoid duplicate records caused by producer retries.

### `batch.size`

Controls the batch size used for records.

### `linger.ms`

Controls how long the producer can wait to build a larger batch.

### Compression

Kafka producers can compress batches to reduce network/storage usage.

Common codecs include:

```text
gzip
snappy
lz4
zstd
```

---

# 27. Consumer Configuration

Important consumer configurations:

```text
group.id
auto.offset.reset
enable.auto.commit
max.poll.records
```

### `group.id`

Identifies the consumer group.

### `auto.offset.reset`

Determines where to start when no valid committed offset exists.

### `enable.auto.commit`

Controls automatic offset commits.

### `max.poll.records`

Controls the maximum number of records returned by a poll.

---

# 28. Delivery Semantics

Kafka applications commonly discuss three processing guarantees.

## At-most-once

```text
Read
 |
 v
Commit
 |
 v
Process
```

A record may be lost, but it should not normally be processed more than once.

## At-least-once

```text
Read
 |
 v
Process
 |
 v
Commit
```

If a failure happens before commit, the record may be processed again.

Possible result:

```text
Event A -> processed
Event A -> processed again
```

Duplicates are possible.

## Exactly-once

The goal is to ensure processing results are not duplicated within Kafka's supported exactly-once processing model.

Kafka provides mechanisms for exactly-once processing, especially with Kafka Streams and transactions.

---

# 29. Kafka Connect

**Kafka Connect** is a framework for integrating Kafka with external systems.

### Source Connector

External system → Kafka

```text
Database
   |
   v
Source Connector
   |
   v
Kafka
```

### Sink Connector

Kafka → External system

```text
Kafka
  |
  v
Sink Connector
  |
  v
Database / Data Lake
```

Kafka Connect supports reusable connectors for importing/exporting data.

---

# 30. Kafka Streams

**Kafka Streams** is a client library for building stream-processing applications.

```text
Input Topic
     |
     v
Kafka Streams Application
     |
     +---- Filter
     |
     +---- Transform
     |
     +---- Aggregate
     |
     +---- Join
     |
     v
Output Topic
```

Kafka Streams can:

- Transform records
- Filter records
- Aggregate data
- Join streams/tables
- Perform windowing
- Maintain state
- Write results back to Kafka

---

# 31. KStream

A **KStream** represents a stream of events.

Think:

```text
Event 1
Event 2
Event 3
Event 4
```

Every record is treated as an independent event.

Example:

```text
payments topic
      |
      v
    KStream
      |
      v
filter(amount > 1000)
```

---

# 32. KTable

A **KTable** represents the latest state for each key.

Example events:

```text
customer_101 -> Address A
customer_101 -> Address B
customer_101 -> Address C
```

Conceptually, the current state becomes:

```text
customer_101 -> Address C
```

### KStream vs KTable

| KStream | KTable |
|---|---|
| Stream of events | Current state/table |
| Each record is an event | Records represent updates |
| Append-like event interpretation | Latest value per key |
| Example: transactions | Example: customer state |

---

# 33. Kafka Streams Transformations

### Stateless transformations

Do not require persistent state for the operation.

Examples:

```text
filter
map
mapValues
branch
```

Example:

```text
Orders
  |
  v
filter(amount > 1000)
  |
  v
High Value Orders
```

### Stateful transformations

Maintain state.

Examples:

```text
count
reduce
aggregate
join
windowing
```

---

# 34. Kafka Streams Internal Topics

Kafka Streams can use internal topics.

Examples:

- Repartition topics
- Changelog topics

```text
Input Topic
     |
     v
Kafka Streams
     |
     +----> Repartition Topic
     |
     +----> Changelog Topic
     |
     v
Output Topic
```

Internal topics support stream-processing operations and state recovery.

---

# 35. ksqlDB

**ksqlDB is a streaming database built around Kafka that allows you to process Kafka data using SQL.**

Instead of writing a full Java Kafka Streams application, developers can use SQL-like statements.

Simple model:

```text
Kafka Topic
     |
     v
   ksqlDB
     |
     +----> Filter
     |
     +----> Transform
     |
     +----> Aggregate
     |
     +----> Join
     |
     v
Kafka Topic
```

Example:

```sql
CREATE STREAM orders_stream
WITH (
    KAFKA_TOPIC='orders',
    VALUE_FORMAT='JSON'
);
```

Then:

```sql
SELECT *
FROM orders_stream
WHERE amount > 1000;
```

---

# 36. ksqlDB Streams and Tables

ksqlDB works with concepts such as:

```text
Stream
Table
```

### Stream

Represents a sequence of events.

```text
Order Created
Order Created
Order Created
```

### Table

Represents current state.

```text
customer_101 -> current state
customer_102 -> current state
```

---

# 37. ksqlDB Example

Suppose Kafka has:

```text
orders topic
```

ksqlDB can create a stream:

```text
Kafka: orders
      |
      v
ksqlDB Stream
      |
      v
Filter / Transform
      |
      v
Kafka: high_value_orders
```

Example SQL:

```sql
CREATE STREAM high_value_orders AS
SELECT *
FROM orders_stream
WHERE amount > 10000;
```

---

# 38. Kafka Streams vs ksqlDB

| Kafka Streams | ksqlDB |
|---|---|
| Java/Scala library | SQL-based streaming platform |
| Application code | SQL statements |
| More programming control | Easier for SQL users |
| Good for custom applications | Good for SQL-based streaming |
| Runs as application instances | Runs as ksqlDB server(s) |
| Supports KStream/KTable | Provides stream/table abstractions |

Simple interview answer:

> **Kafka Streams is a programming library for building stream-processing applications, while ksqlDB provides a SQL-based interface for processing Kafka streams and tables.**

---

# 39. Schema Registry

A schema defines the structure of data.

Example:

```json
{
  "order_id": 101,
  "customer_id": 500,
  "amount": 2500
}
```

Schema Registry stores and manages schemas used by producers and consumers.

Common formats include:

- Avro
- JSON Schema
- Protobuf

Architecture:

```text
Producer
   |
   +------> Schema Registry
   |
   v
Kafka Topic
   |
   v
Consumer
   |
   +------> Schema Registry
```

---

# 40. Schema Evolution

Data structures can change over time.

Example:

```text
Version 1

order_id
amount
```

Later:

```text
Version 2

order_id
amount
currency
```

Schema compatibility rules help producers and consumers evolve safely.

---

# 41. Kafka Security

Kafka security commonly includes:

- Authentication
- Authorization
- Encryption

Examples:

```text
SSL/TLS
SASL
ACLs
```

Simple architecture:

```text
Client
  |
  | Authentication
  v
Kafka
  |
  | Authorization
  v
Topic
```

---

# 42. KRaft

Modern Kafka uses **KRaft** for Kafka's metadata management instead of depending on ZooKeeper.

High-level model:

```text
Kafka Cluster

+--------------------------+
| Controllers              |
|                          |
| Manage Kafka metadata    |
+--------------------------+

+--------------------------+
| Brokers                  |
|                          |
| Store topic partitions   |
+--------------------------+
```

KRaft simplifies Kafka architecture by integrating metadata management into Kafka itself.

---

# 43. Kafka vs Traditional Message Queue

Traditional queue:

```text
Producer
   |
   v
Queue
   |
   v
Consumer
```

Kafka:

```text
Producer
   |
   v
Kafka Topic
   |
   +----> Consumer Group A
   |
   +----> Consumer Group B
   |
   +----> Consumer Group C
```

Important difference:

> Kafka retains events according to retention policies rather than normally deleting them immediately after consumption.

---

# 44. Kafka vs Database

Kafka is not a replacement for an operational database.

### Database

```text
Application
     |
     v
Operational DB
```

Used primarily for transactional storage and querying.

### Kafka

```text
Application
     |
     v
Kafka
     |
     +----> Spark
     +----> Flink
     +----> Analytics
     +----> Other Applications
```

Kafka is primarily an event-streaming platform.

---

# 45. Amazon-like E-commerce Example

Imagine an e-commerce application.

```text
Customer
   |
   v
Checkout
   |
   +----> Payment Program
   +----> Order Program
   +----> Inventory Program
   +----> Notification Program
```

Instead of tightly coupling these programs to downstream systems:

```text
Checkout Program ---> checkout topic
Payment Program  ---> payment topic
Order Program    ---> orders topic
Inventory Program ---> inventory topic
```

Then:

```text
                         KAFKA
              +-------------------------+
              |                         |
Checkout -----> checkout topic ---------+
              |                         |
Payment ------> payment topic ----------+----> Spark / Flink
              |                         |
Order --------> orders topic -----------+
              |                         |
Inventory ----> inventory topic --------+
```

Producers publish events.

Spark/Flink can consume and process those events.

---

# 46. Paytm-like Operational Database Example

Imagine an e-commerce operational database:

```text
+----------------+
| orders         |
+----------------+

+----------------+
| order_returns  |
+----------------+

+----------------+
| payments       |
+----------------+

+----------------+
| customers      |
+----------------+
```

Producer/CDC processes can capture data changes:

```text
orders
   |
   v
Producer / CDC
   |
   v
Kafka: orders
```

```text
order_returns
   |
   v
Producer / CDC
   |
   v
Kafka: order_returns
```

```text
payments
   |
   v
Producer / CDC
   |
   v
Kafka: payments
```

```text
customers
   |
   v
Producer / CDC
   |
   v
Kafka: customers
```

Then:

```text
Kafka
  |
  v
Spark / Flink
  |
  v
Data Lake / Warehouse
```

---

# 47. Production CDC Architecture

A common Data Engineering architecture is:

```text
Operational Database
        |
        | Change Data Capture
        v
CDC Tool / Kafka Connect
        |
        v
Kafka Topics
        |
        v
Spark / Flink
        |
        v
Data Lake / Warehouse
```

For example:

```text
Database
   |
   v
Debezium
   |
   v
Kafka Connect
   |
   v
Kafka
   |
   v
Spark / Flink
```

---

# 48. Kafka as a Data Engineering Backbone

A typical architecture:

```text
                 Source Systems
                      |
          +-----------+-----------+
          |                       |
          v                       v
     Applications              Databases
          |                       |
          v                       v
       Producers              CDC / Connect
          |                       |
          +-----------+-----------+
                      |
                      v
                    Kafka
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Spark       Flink       ksqlDB
          |           |           |
          +-----------+-----------+
                      |
                      v
              Data Lake / Warehouse
```

Kafka acts as the event-streaming layer connecting source systems and downstream consumers.

---

# 49. Messaging Patterns in Kafka

Kafka can provide both **queue-like** and **publish-subscribe** behavior.

## Point-to-Point / Queue-like Model

Within a consumer group, partitions are shared among consumers.

```text
              orders topic
                   |
          +--------+--------+
          |        |        |
         P0       P1       P2
          |        |        |
         C1       C2       C3
          \        |        /
           Consumer Group
```

Each partition is consumed by only one consumer from that group at a time.

## Publish-Subscribe Model

Multiple consumer groups can independently consume the same topic.

```text
                    orders topic
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Consumer Group A        Consumer Group B
             |                       |
             v                       v
       Order Processing          Analytics
```

The same event can therefore be consumed independently by different applications.

---

# 50. Kafka Cluster

A **Kafka cluster** is a group of Kafka brokers working together.

```text
                    Kafka Cluster
          +-------------------------------+
          |                               |
          | Broker 1   Broker 2   Broker 3|
          |    |          |          |    |
          +----+----------+----------+----+
               |          |          |
               v          v          v
             Partitions / Replicas
```

A cluster provides:

- Scalability
- Fault tolerance
- Distributed storage
- High availability

---

# 51. Producer Message Partitioning Strategies

The producer determines which partition receives a record.

### 1. No Key / Default Partitioning

When no key is supplied, the producer's partitioning strategy distributes records among available partitions.

```text
Producer
   |
   +----> P0
   +----> P1
   +----> P2
```

### 2. Keyed Records

When a key is supplied, the key is used by the partitioner to determine the partition.

```text
Key = customer_101
          |
          v
      Partition 2
```

Records with the same key are normally routed to the same partition, which helps preserve ordering for that key.

### 3. Custom Partitioner

A producer can use custom partitioning logic when application-specific routing is required.

---

# 52. Why Consumer Groups Are Important

Consumer groups provide:

### Load Balancing

```text
P0 -> C1
P1 -> C2
P2 -> C3
```

### Fault Tolerance

If C2 fails:

```text
Before:
P0 -> C1
P1 -> C2
P2 -> C3

After Rebalance:
P0 -> C1
P1 -> C3
P2 -> C1
```

### Scalability

More consumers can process partitions in parallel, up to the available partition count.

### Parallelism

Different partitions can be processed concurrently.

### Ordering

A partition is assigned to only one consumer within a group at a time, helping preserve partition ordering.

---

# 53. Detailed Offset Management

Kafka stores consumer group offsets in the internal Kafka topic:

```text
__consumer_offsets
```

This allows Kafka to maintain consumer progress.

## Current Position

The current position represents the next record the consumer will read.

```text
Partition

0   1   2   3   4   5
|   |   |   |   |   |
A   B   C   D   E   F
            ^
            |
       Consumer position
```

## Committed Offset

The committed offset is the progress stored for the consumer group.

If a consumer fails, a new consumer can continue from the committed position.

---

# 54. Auto Commit

Important configuration:

```text
enable.auto.commit=true
```

The commit interval is controlled by:

```text
auto.commit.interval.ms
```

Conceptually:

```text
Poll
 |
 v
Process
 |
 v
Periodic offset commit
```

### Problem with Auto Commit

Suppose:

```text
Consumer reads 10 records
        |
        v
Processes 10 records
        |
        X
Consumer crashes before commit
```

Another consumer may start from the previous committed offset and process those records again.

Therefore, **duplicate processing can occur**.

---

# 55. Manual Commit

Disable automatic commits:

```text
enable.auto.commit=false
```

Then the application decides when to commit.

Recommended processing sequence for at-least-once processing:

```text
Poll
 |
 v
Process records
 |
 v
Processing successful
 |
 v
Commit offset
```

If processing fails before the commit, the records can be processed again.

---

# 56. `commitSync()` vs `commitAsync()`

## `commitSync()`

Synchronous and blocking.

```text
Consumer
   |
   v
commitSync()
   |
   | waits
   v
Commit completed
```

Characteristics:

- Blocks until the commit completes or fails
- Can retry recoverable errors
- More reliable
- Can reduce processing throughput

## `commitAsync()`

Asynchronous and non-blocking.

```text
Consumer
   |
   +----> commitAsync()
   |
   +----> Continue processing
```

Characteristics:

- Does not block normal processing
- Does not automatically retry a failed asynchronous commit
- Faster
- Failure can be handled through a callback

---

# 57. Sync vs Async Commit

| Commit | Behavior | Advantage | Trade-off |
|---|---|---|---|
| `commitSync()` | Blocking | Stronger reliability | Can slow consumer |
| `commitAsync()` | Non-blocking | Better throughput | Failed commit is not automatically retried |
| Combination | Async during processing + Sync at shutdown | Balance | More implementation complexity |

A common strategy is:

```text
Normal processing
      |
      v
commitAsync()

Shutdown / final commit
      |
      v
commitSync()
```

---

# 58. Async Commit Failure

An asynchronous commit can fail because of conditions such as:

- Broker temporarily unavailable
- Consumer removed from group
- Invalid offset
- Rebalance-related conditions

A callback can be supplied to monitor success/failure.

```text
commitAsync(callback)

        |
        +---- Success
        |
        +---- Failure -> Log / Alert / Handle
```

A failed async commit does not automatically update the committed offset.

---

# 59. Reading Strategies

Kafka consumers can control where they read from.

## Read from Beginning

```text
auto.offset.reset=earliest
```

```text
0 -> 1 -> 2 -> 3 -> 4
^
|
Start
```

Useful when processing available historical records.

## Read from Latest

```text
auto.offset.reset=latest
```

```text
0 -> 1 -> 2 -> 3 -> 4
                  ^
                  |
                Start
```

Useful when the application is primarily interested in new events.

## Read from Specific Offset

A consumer can use `seek()` to move its position.

```text
0 -> 1 -> 2 -> 3 -> 4 -> 5
              ^
              |
           seek(3)
```

## Read from Committed Offset

When a consumer restarts, it can continue from its committed group offset.

```text
Processed -> Commit -> Failure
                    |
                    v
              Restart consumer
                    |
                    v
          Read from committed offset
```

---

# 60. Rebalancing and Offset Management — Interview Scenario

Suppose:

```text
Partition:
0 1 2 3 4 5 6 7 8 9
```

Consumer processes the first 10 records but has not committed the offset yet.

Then a rebalance occurs:

```text
Consumer C1
    |
    X
  Fails
```

The partition is assigned to C2.

If the last committed offset was before those records:

```text
C2
 |
 v
Reads the records again
```

Result:

```text
Duplicate processing
```

This is one reason manual offset management is important when the application needs precise control over processing and committing.

---

# 61. Kafka in Data Engineering

Kafka is commonly used for:

### Data Ingestion

```text
Application / Database
        |
        v
      Kafka
        |
        v
Data Processing
```

### Real-Time Analytics

```text
Events
  |
  v
Kafka
  |
  v
Spark / Flink / ksqlDB
  |
  v
Real-Time Analytics
```

### Event Sourcing

Kafka can maintain a durable stream of events representing changes occurring in a system.

```text
Event 1
Event 2
Event 3
Event 4
  |
  v
Kafka Event Log
```

### Decoupling

Kafka acts as a buffer between producers and consumers.

```text
Producer
   |
   v
 Kafka
   |
   +----> Consumer A
   +----> Consumer B
   +----> Consumer C
```

### Other Use Cases

- Transaction/event processing
- Log aggregation
- IoT data
- Recommendations
- Real-time monitoring
- Data integration

# References

## Apache Kafka

- Apache Kafka Documentation: https://kafka.apache.org/documentation/
- Apache Kafka 4.3 Getting Started: https://kafka.apache.org/43/getting-started/introduction/
- Apache Kafka 4.3 Streams Developer Guide: https://kafka.apache.org/43/streams/developer-guide/

## Confluent

- Confluent Kafka Introduction: https://docs.confluent.io/kafka/introduction.html
- Confluent Kafka Documentation: https://docs.confluent.io/kafka/index.html

# References

## Apache Kafka

- Apache Kafka Documentation: https://kafka.apache.org/documentation/
- Apache Kafka 4.3 Getting Started: https://kafka.apache.org/43/getting-started/introduction/
- Apache Kafka 4.3 Streams Developer Guide: https://kafka.apache.org/43/streams/developer-guide/

## Confluent

- Confluent Kafka Introduction: https://docs.confluent.io/kafka/introduction.html
- Confluent Kafka Documentation: https://docs.confluent.io/kafka/index.html