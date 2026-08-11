# Kafka Interview Questions — Simple Explanations

> **Purpose:** Simple, interview-friendly explanations of all 50 Kafka questions from the uploaded interview-question PDF.
>
> **Style:** First understand the simple idea, then remember the important interview points.

---

# Section 1 — Architecture and Internals

## Q1. Explain Kafka's overall architecture and the role of each core component.

### Simple Explanation

Kafka is a **distributed, durable event-streaming platform**.

Think of Kafka as a large distributed log:

```text
Producer
   |
   v
 Topic
   |
   +---- Partition 0
   +---- Partition 1
   +---- Partition 2
             |
             v
          Consumer
```

### Main Components

- **Broker** — A Kafka server that stores partitions and handles producer/consumer requests.
- **Cluster** — Multiple Kafka brokers working together.
- **Topic** — A logical name/category for events.
- **Partition** — An ordered log inside a topic.
- **Producer** — Writes records to Kafka.
- **Consumer** — Reads records from Kafka.
- **Consumer Group** — Multiple consumers sharing partition-processing work.
- **Controller** — Manages cluster metadata, leadership and broker coordination.
- **KRaft** — Modern Kafka metadata-management architecture.

### Important Point

Kafka is **not a traditional queue where a message disappears after being consumed**.

The event remains according to the retention policy, and consumers track their own offsets.

---

## Q2. What is a partition and why is it the fundamental unit of parallelism and ordering?

A **partition** is an ordered sequence of records inside a topic.

```text
Topic: orders

Partition 0:
0 -> Order A
1 -> Order B
2 -> Order C

Partition 1:
0 -> Order D
1 -> Order E
```

### Why partitions matter

**1. Ordering**

Kafka guarantees ordering **within a partition**.

**2. Parallelism**

Different partitions can be processed by different consumers.

```text
P0 -> C1
P1 -> C2
P2 -> C3
```

**3. Scalability**

Partitions can be distributed across brokers.

### Interview Point

> Partitions are the fundamental unit of Kafka's ordering, parallelism and distribution.

---

## Q3. How does Kafka guarantee message ordering, and what can silently break it?

Kafka guarantees ordering **within one partition**.

If customer ID is used as the key:

```text
customer_101
     |
     v
Partition 2

Order 1
Order 2
Order 3
```

The orders for that customer stay ordered within that partition.

### What can break ordering?

- Multiple producers writing the same key concurrently
- Producer retries when idempotence is disabled and multiple requests are in flight
- Increasing the number of partitions can change key-to-partition mapping
- Consumer-side parallel processing can reorder records

### Important

> Kafka does not guarantee global ordering across all partitions.

---

## Q4. Explain leader, follower, ISR, High Watermark and LEO.

Suppose:

```text
Partition 0

Broker 1 -> Leader
Broker 2 -> Follower
Broker 3 -> Follower
```

### Leader

Handles normal produce and fetch requests.

### Follower

Copies data from the leader.

### ISR — In-Sync Replicas

Replicas that are sufficiently caught up with the leader.

```text
ISR = Broker 1 + Broker 2 + Broker 3
```

If Broker 3 falls too far behind, it can leave the ISR.

### LEO — Log End Offset

The next offset that would be written on a replica.

Think:

> **LEO = end/tail of that replica's log.**

### High Watermark

The highest point that Kafka considers safely replicated.

Consumers cannot normally read beyond this durability boundary.

### Easy mental model

```text
LEO = How far a replica has written

High Watermark = How far Kafka considers safely committed
```

---

## Q5. What is the controller, and how does KRaft change it compared to ZooKeeper?

The **controller** handles important cluster-wide tasks such as:

- Partition leader election
- Broker membership
- Metadata changes
- Replica reassignment

### Older architecture

```text
Kafka Brokers
      |
      v
 ZooKeeper
```

### Modern architecture

```text
Kafka
  |
  +---- Brokers
  |
  +---- Controller Quorum
             |
             v
            KRaft
```

KRaft stores Kafka metadata in a replicated Raft-based log instead of relying on ZooKeeper.

### Interview Point

> KRaft removes Kafka's dependency on ZooKeeper and gives Kafka an integrated metadata-management system.

---

## Q6. Why did Kafka move to KRaft?

Main reasons:

### 1. Simpler architecture

Instead of operating:

```text
Kafka + ZooKeeper
```

you operate Kafka with its own controller quorum.

### 2. Better scalability

KRaft was designed to handle very large metadata workloads.

### 3. Faster controller failover

Controllers already replicate metadata, so a new controller does not need to rebuild everything from an external system.

### 4. Operational simplicity

Fewer systems to deploy, secure, monitor and maintain.

---

## Q7. What is the High Watermark?

The **High Watermark (HW)** is the point up to which Kafka considers records safely replicated.

```text
Partition

0  1  2  3  4  5
         ^
         |
    High Watermark
```

Consumers should not see records beyond the safe visibility boundary.

### Why is it important?

It protects consumers from seeing data that could disappear after a leader failure.

### Easy comparison

```text
LEO -> current end of a replica
HW  -> safe visibility/durability boundary
```

---

## Q8. Explain leader election and unclean leader election.

If a partition leader fails, Kafka needs another replica to become leader.

### Normal leader election

Kafka prefers an in-sync replica.

```text
Leader fails
    |
    v
ISR replica becomes leader
```

This protects committed data.

### Unclean leader election

If no suitable ISR replica is available, Kafka can optionally elect an out-of-sync replica.

This improves availability but can cause data loss.

### Trade-off

```text
Clean election
-> Better durability
-> Possible temporary unavailability

Unclean election
-> Better availability
-> Possible data loss
```

For important financial/audit data, durability is usually more important than keeping a partition available at any cost.

---

## Q9. How does Kafka achieve high throughput?

Kafka uses several techniques:

### Sequential I/O

Records are appended to logs sequentially.

### Batching

Producers send records in batches.

### Compression

Batches can be compressed.

### Page Cache

Kafka benefits from the operating system's page cache.

### Zero-copy

Kafka can efficiently transfer data from storage/cache to the network.

### Parallelism

Multiple partitions can be processed concurrently.

### Simple log-based design

Kafka does not need to delete a record immediately after a consumer reads it.

### Mental model

```text
Sequential I/O
+
Batching
+
Compression
+
Parallel partitions
+
Efficient network transfer
=
High throughput
```

---

## Q10. What is a log segment? How does Kafka find a record by offset?

A partition is not stored as one giant file.

It is divided into **log segments**.

```text
Partition 0

Segment 1
Segment 2
Segment 3
Segment 4 <- Active
```

Older segments become immutable.

Kafka uses indexes to locate records efficiently.

### Offset lookup

Conceptually:

```text
Offset
  |
  v
Find correct segment
  |
  v
Use offset index
  |
  v
Jump near the record
  |
  v
Scan a small range
```

### Why segments matter

Segments are also important for retention and deletion because Kafka generally removes old segments rather than individual records one by one.

---

# Section 2 — Producers

## Q11. Walk through the lifecycle of a produce request from `send()` to acknowledgement.

When a producer calls:

```python
producer.send(...)
```

the flow is approximately:

```text
send()
  |
  v
Serialize key/value
  |
  v
Choose partition
  |
  v
Add to producer batch
  |
  v
Sender thread
  |
  v
Broker leader
  |
  v
Followers replicate
  |
  v
Acknowledgement
```

### Important configurations involved

- `batch.size`
- `linger.ms`
- `buffer.memory`
- `acks`
- `retries`
- `delivery.timeout.ms`
- `enable.idempotence`

The producer can retry transient failures.

---

## Q12. Explain `acks=0`, `acks=1`, and `acks=all`.

`acks` controls when the producer considers a message successfully written.

### `acks=0`

Producer does not wait for an acknowledgement.

```text
Producer -> Broker
```

Fast, but data can be lost.

### `acks=1`

Leader acknowledges after writing locally.

```text
Producer
   |
   v
Leader -> ACK
   |
   v
Followers replicate later
```

A leader failure before replication can cause loss.

### `acks=all`

Leader waits for the required in-sync replicas.

This gives stronger durability.

### `min.insync.replicas`

Defines the minimum number of in-sync replicas required for a write to succeed.

Common durable configuration:

```text
replication.factor = 3
min.insync.replicas = 2
acks = all
```

---

## Q13. What is the idempotent producer?

An idempotent producer helps prevent duplicate records caused by producer retries.

Imagine:

```text
Producer -> Broker
             |
             v
          Message saved
             |
             X
        ACK lost
```

Producer thinks the message failed and sends it again.

Without idempotence:

```text
Message A
Message A
```

With idempotence, Kafka uses producer identity and sequence information to detect duplicate sends.

### Important

> Idempotence prevents retry-related duplicates from the same producer session/partition. It is not the same as end-to-end exactly-once processing.

---

## Q14. Explain producer batching: `batch.size`, `linger.ms`, and `buffer.memory`.

Kafka producers batch records to improve throughput.

### `batch.size`

Maximum size of a batch for a partition.

Larger batches can improve:

- Throughput
- Compression efficiency

### `linger.ms`

How long the producer can wait for additional records before sending a batch.

```text
linger = small
-> Lower latency

linger = larger
-> Better batching
-> Higher throughput
```

### `buffer.memory`

Memory available for buffering records before they are sent.

### Simple rule

```text
More batching
-> Better throughput
-> Potentially higher latency
```

---

## Q15. How does the default partitioner work, including the sticky partitioner?

### Keyed record

If a key is supplied:

```text
key
 |
 v
partitioner
 |
 v
partition
```

The key determines the partition according to the producer's partitioning algorithm.

Same key normally goes to the same partition while the partition count remains unchanged.

### Keyless record

Modern Kafka uses sticky partitioning behavior for keyless records to improve batching.

Instead of changing partitions for every record, the producer can keep sending to a partition until the batch is ready, then move to another partition.

### Why?

Better batching means:

- Fewer requests
- Better throughput
- Better compression

---

## Q16. How does `max.in.flight.requests.per.connection` interact with retries and ordering?

This setting controls how many produce requests can be outstanding at once.

Suppose:

```text
Request A
Request B
```

are both in flight.

If A fails and B succeeds first, a retry of A could arrive after B.

Without idempotence:

```text
B
A
```

Ordering can break.

### With idempotence

Kafka uses sequence numbers to maintain correct ordering and avoid duplicates within the supported in-flight window.

### Interview shortcut

> Without idempotence, more than one in-flight request plus retries can cause reordering. Idempotence allows pipelining while preserving ordering.

---

## Q17. Explain producer-side compression.

Kafka compresses **batches**, not individual records.

Common codecs:

| Codec | Simple idea |
|---|---|
| gzip | Strong compression, more CPU |
| snappy | Fast |
| lz4 | Fast and efficient |
| zstd | Excellent ratio with good speed |

### Flow

```text
Producer
   |
   v
Create batch
   |
   v
Compress batch
   |
   v
Kafka
```

Compression reduces:

- Network traffic
- Disk usage
- Replication traffic

---

# Section 3 — Consumers and Consumer Groups

## Q18. Explain consumer groups and partition assignment.

A consumer group is a set of consumers sharing the same `group.id`.

```text
Topic

P0 -> C1
P1 -> C2
P2 -> C3

Consumer Group = order-processing
```

Each partition is assigned to one consumer within the group at a time.

### Important consequences

If:

```text
Partitions = 3
Consumers = 5
```

then only up to 3 consumers can actively consume those partitions.

```text
C1 -> P0
C2 -> P1
C3 -> P2
C4 -> idle
C5 -> idle
```

Different consumer groups can all read the same topic independently.

---

## Q19. Walk through the consumer `poll()` loop.

A typical consumer repeatedly calls:

```text
poll()
```

Conceptually:

```text
poll()
  |
  +--> Group management
  |
  +--> Fetch records
  |
  +--> Return records
  |
  +--> Process
  |
  +--> Commit
  |
  +--> poll() again
```

`poll()` is not simply "read one message."

It participates in:

- Fetching records
- Consumer-group management
- Rebalancing
- Offset handling

### Important setting

`max.poll.interval.ms` controls the maximum allowed time between poll calls.

If processing takes too long, the consumer may be considered stuck and a rebalance can happen.

---

## Q20. Explain offset management: `__consumer_offsets`, auto vs manual commit, `commitSync()` vs `commitAsync()`.

Kafka stores consumer-group offsets in:

```text
__consumer_offsets
```

### Auto Commit

```text
enable.auto.commit=true
```

Kafka periodically commits offsets.

Simple, but it may commit progress before processing has successfully completed.

### Manual Commit

```text
enable.auto.commit=false
```

Application controls when the offset is committed.

Recommended pattern for at-least-once:

```text
Read
 |
 v
Process successfully
 |
 v
Commit
```

### `commitSync()`

- Blocking
- Waits for commit result
- More reliable
- Can reduce throughput

### `commitAsync()`

- Non-blocking
- Better throughput
- Failure handled asynchronously
- Does not automatically retry in the same way as `commitSync()`

### Key idea

> Process first, commit second when you want at-least-once behavior.

---

## Q21. Explain `auto.offset.reset` and exactly when it takes effect.

This setting tells Kafka where to start when the consumer has **no valid committed offset**.

### `earliest`

Read from the earliest available retained record.

```text
0 -> 1 -> 2 -> 3 -> 4
^
|
Start
```

### `latest`

Start from the latest position and consume new records.

### `none`

Throw an error if no valid offset exists.

### Important

`auto.offset.reset` does **not** mean "start from earliest every time the consumer starts."

If a valid committed offset exists, Kafka resumes from it.

---

## Q22. Explain consumer rebalancing. Eager vs cooperative.

A **rebalance** redistributes partitions among consumers in a group.

Triggered by events such as:

- Consumer joins
- Consumer leaves
- Consumer failure
- Partition changes
- Subscription changes

### Eager rebalance

```text
Stop
 |
 v
Revoke all partitions
 |
 v
Reassign
 |
 v
Start again
```

This can cause a noticeable pause.

### Cooperative incremental rebalance

Only partitions that need to move are reassigned.

```text
Keep current work
       +
Move only necessary partitions
```

This reduces disruption.

---

## Q23. Explain `session.timeout.ms`, `heartbeat.interval.ms`, and `max.poll.interval.ms`.

These settings solve different problems.

### `heartbeat.interval.ms`

How frequently the consumer sends heartbeats.

### `session.timeout.ms`

How long the coordinator waits without receiving heartbeats before declaring the consumer dead.

### `max.poll.interval.ms`

Maximum time between calls to `poll()`.

### Easy distinction

```text
Heartbeat
   |
   v
"Am I alive?"

max.poll.interval
   |
   v
"Am I making processing progress?"
```

A consumer can be alive but stuck processing. `max.poll.interval.ms` helps detect that case.

---

## Q24. What is static group membership?

Static membership gives a consumer a stable identity using:

```text
group.instance.id
```

Without static membership:

```text
Consumer restarts
      |
      v
Leave group
      |
      v
Rebalance
```

With static membership, a short restart can allow the same consumer identity to return without immediately causing a full reassignment.

### Useful for

- Stateful consumers
- Kafka Streams
- Kubernetes deployments
- Frequent restarts

---

## Q25. Compare Range, RoundRobin, Sticky and CooperativeSticky assignment.

These are partition-assignment strategies.

### Range

Assigns ranges of partitions.

Simple, but can cause uneven distribution across multiple topics.

### RoundRobin

Distributes partitions in round-robin order.

Usually more evenly distributed, but may move many assignments during rebalancing.

### Sticky

Tries to keep the existing assignments while maintaining balance.

### CooperativeSticky

Combines sticky assignment with cooperative incremental rebalancing.

It reduces unnecessary movement and avoids a complete stop-the-world rebalance.

### Easy memory

```text
Range            -> Simple range assignment
RoundRobin       -> Spread partitions evenly
Sticky           -> Keep assignments where possible
CooperativeSticky-> Sticky + less disruptive rebalance
```

---

# Section 4 — Delivery Semantics and Reliability

## Q26. Explain at-most-once, at-least-once and exactly-once.

### At-most-once

Commit before processing.

```text
Read
 |
 v
Commit
 |
 v
Process
```

If the application crashes after commit but before processing:

```text
Record lost
```

### At-least-once

Process before committing.

```text
Read
 |
 v
Process
 |
 v
Commit
```

If the application crashes after processing but before commit:

```text
Record processed again
```

Duplicates are possible.

### Exactly-once

The goal is for each record to affect the result once despite failures.

Kafka supports exactly-once processing within Kafka using transactions and appropriate consumer isolation.

### Important

> Exactly-once becomes more complicated when an external database or API is involved.

---

## Q27. Explain Kafka transactions and exactly-once consume-transform-produce.

Suppose:

```text
Input Topic
    |
    v
Consumer
    |
    v
Transform
    |
    v
Output Topic
```

Without transactions, the application could:

```text
Write output
   |
   X
Crash before committing input offset
```

After restart, input is processed again and output may be duplicated.

### With Kafka transactions

The output records and input offsets can be committed atomically.

Conceptually:

```text
Begin Transaction
      |
      v
Read input
      |
      v
Process
      |
      v
Write output
      |
      v
Commit input offsets
      |
      v
Commit Transaction
```

Either the transaction succeeds as a whole or it does not.

---

## Q28. What is the transaction coordinator and `__transaction_state`?

Kafka uses a **transaction coordinator** to manage transactional producers.

The coordinator tracks transaction metadata in:

```text
__transaction_state
```

It manages things such as:

- Transaction state
- Participating partitions
- Producer identity/epoch
- Commit/abort information

### Why?

If a broker fails, Kafka needs durable transaction metadata to recover correctly.

---

## Q29. What do `read_committed` and `read_uncommitted` mean?

These control what a consumer sees when Kafka transactions are used.

### `read_uncommitted`

Consumer can see transactional records even if the transaction later aborts.

### `read_committed`

Consumer only sees committed transactional records.

```text
Transaction A -> COMMITTED -> visible
Transaction B -> ABORTED   -> hidden
```

### Important

For exactly-once Kafka pipelines, downstream consumers should generally use:

```text
isolation.level=read_committed
```

---

## Q30. What can cause data loss in Kafka?

Data loss can occur at multiple layers.

### Producer

Weak settings such as:

```text
acks=0
acks=1
```

can reduce durability.

### Broker

Poor replication configuration can cause loss.

### Unclean leader election

An out-of-sync replica may become leader and be missing previously committed records.

### Consumer

Committing offsets before processing can cause skipped records.

### Retention

A consumer that stays behind longer than retention may lose access to old records.

### Durable design

A common strong design includes:

```text
acks=all
+
idempotence
+
RF=3
+
min.insync.replicas=2
+
appropriate retention
+
process-then-commit
```

---

## Q31. How do duplicates occur, and how do you make a sink idempotent?

### Duplicate source

A common scenario:

```text
Process record
     |
     v
Write to DB
     |
     X
Crash before Kafka offset commit
     |
     v
Record processed again
```

### Make sink idempotent

Use:

- Unique business keys
- Upserts
- `MERGE`
- Unique constraints
- Event IDs
- Deduplication tables

Example:

```text
event_id = 1001

First processing -> INSERT
Second processing -> already exists -> ignore/update
```

### Interview point

> You often don't eliminate duplicates completely; instead, you design the destination so duplicates are harmless.

---

# Section 5 — Storage, Retention and Compaction

## Q32. Explain time-based vs size-based retention and `cleanup.policy`.

Retention controls how long Kafka keeps data.

### Time-based

```text
retention.ms
```

Example:

```text
Keep data for 7 days
```

### Size-based

```text
retention.bytes
```

Example:

```text
Keep up to X GB per partition
```

If both are configured, whichever limit is reached first can cause old data to become eligible for deletion.

### `cleanup.policy`

Common values:

```text
delete
compact
compact,delete
```

---

## Q33. Explain log compaction, tombstones and use cases.

Log compaction is **key-based cleanup**.

Example:

```text
customer_101 -> Address A
customer_101 -> Address B
customer_101 -> Address C
```

After compaction, Kafka can retain the latest value:

```text
customer_101 -> Address C
```

### Tombstone

A record with:

```text
key = customer_101
value = null
```

is a tombstone indicating that the key should be deleted from the compacted state.

### Use cases

- Database CDC
- Customer state
- Configuration
- Kafka Streams changelogs
- Current-state topics

---

## Q34. When do you choose compaction vs deletion vs both?

### `delete`

Use when every event represents an important historical occurrence.

Examples:

```text
clicks
transactions
logs
```

### `compact`

Use when the latest value for each key matters.

Examples:

```text
customer_id -> current customer details
```

### `compact,delete`

Use when you want:

- Latest value per key
- But also a time/size limit

### Simple question to ask

> Is this topic an **event history** or a **current-state store**?

---

## Q35. What is tiered storage and why does it matter?

Tiered storage separates recent data from older data.

Conceptually:

```text
Kafka Broker
   |
   +--> Local Storage
   |     Recent / hot data
   |
   +--> Remote Storage
         Older / cold data
```

Older data can be moved to cheaper storage such as object storage.

### Benefits

- Longer retention
- Lower local disk requirements
- Faster broker recovery/reassignment
- Better scalability for large histories

### Trade-off

Remote reads can have higher latency than local reads.

---

# Section 6 — Kafka Ecosystem

## Q36. When do you use Consumer API vs Kafka Streams vs Kafka Connect vs ksqlDB?

Think about what you are trying to do.

### Consumer API

Use when you need low-level control.

```text
Kafka
  |
  v
Your custom application
```

### Kafka Streams

Use for stream processing inside a JVM application.

```text
Kafka
  |
  v
Kafka Streams App
  |
  v
Kafka
```

Good for:

- Transformations
- Aggregations
- Joins
- Windowing
- Stateful processing

### Kafka Connect

Use for moving data between Kafka and external systems.

```text
Database -> Connect -> Kafka
Kafka -> Connect -> Data Lake
```

### ksqlDB

Use SQL for Kafka stream processing.

```sql
SELECT *
FROM orders
WHERE amount > 1000;
```

### Easy rule

```text
Move data       -> Kafka Connect
Custom code     -> Consumer API
Stream process  -> Kafka Streams
SQL processing  -> ksqlDB
```

---

## Q37. Explain Kafka Streams internals: state stores, changelog topics and standby replicas.

Kafka Streams can perform stateful operations.

Example:

```text
Orders
  |
  v
Group By
  |
  v
Count
```

The application needs to remember the count.

### State Store

Local storage that holds processing state.

```text
Kafka Streams instance
        |
        v
   Local State Store
```

### Changelog Topic

Kafka Streams backs state with a Kafka changelog.

```text
Local State
    |
    v
Changelog Topic
```

If the application fails, it can rebuild state from the changelog.

### Standby Replica

A standby keeps a copy of state on another instance.

```text
Instance A -> Active state
Instance B -> Standby state
```

If A fails, B can recover much faster.

---

## Q38. Explain KStream, KTable, GlobalKTable and stream-table duality.

### KStream

Represents a stream of independent events.

```text
Order 1
Order 2
Order 3
```

Every record is an event.

### KTable

Represents the latest value for each key.

```text
customer_101 -> Address C
```

If a new value arrives for the same key, it updates the state.

### GlobalKTable

A KTable replicated to every Kafka Streams instance.

Useful for small reference/lookup data.

### Stream-table duality

Think:

```text
Stream = changes/events

Table = current state after applying those changes
```

Example:

```text
Stream:
A -> 100
A -> 200
A -> 300

Table:
A -> 300
```

---

## Q39. Explain Kafka Connect architecture: workers, connectors, tasks, converters and SMTs.

Kafka Connect is a framework for integrating Kafka with external systems.

```text
Source System
     |
     v
Source Connector
     |
     v
Kafka
     |
     v
Sink Connector
     |
     v
Target System
```

### Connector

Defines how to connect to the external system.

### Task

Actual unit of work performed by a connector.

Multiple tasks provide parallelism.

### Worker

Process that runs connector tasks.

### Converter

Converts Kafka bytes to/from data formats such as:

- JSON
- Avro
- Protobuf

### SMT — Single Message Transform

Small record-level transformation.

Examples:

- Rename field
- Add metadata
- Route records
- Mask data

---

## Q40. Explain Schema Registry compatibility modes and safe schema evolution.

Schema Registry stores and manages schemas.

Example:

```text
Version 1:
order_id
amount

Version 2:
order_id
amount
currency
```

Compatibility rules help old and new applications work safely.

### Common modes

**BACKWARD**

New schema can read old data.

**FORWARD**

Old schema can read new data.

**FULL**

Supports both backward and forward compatibility.

**NONE**

No compatibility checking.

### Safe strategy

Prefer compatible changes such as:

```text
Add optional field
+
Provide default value
```

Avoid casually:

```text
Rename field
Change data type
Remove required field
```

### Interview point

> Schema compatibility should be enforced before production, ideally through Schema Registry and CI/CD validation.

---

# Section 7 — Scenario-Based Questions

## Q41. One partition has growing consumer lag while others are fine. How do you diagnose and fix it?

This usually suggests a **partition-specific problem**, not simply insufficient total consumers.

### Check 1 — Hot key

Example:

```text
customer_999
customer_999
customer_999
customer_999
```

All records go to one partition.

```text
P0 -> Normal
P1 -> Normal
P2 -> Very Busy
```

### Check 2 — Poison message

One record repeatedly fails processing.

### Check 3 — Slow downstream system

Maybe that partition's records call a slow API or database shard.

### Fix

- Fix partition-key skew
- Handle poison messages
- Use retry/DLQ strategy
- Optimize slow downstream processing
- Add partitions only when partition-level parallelism is actually the problem

### Important

> Adding consumers does not help if the problem is one hot partition, because one partition is processed by only one consumer in the group.

---

## Q42. Guarantee strict ordering per customer while maintaining high throughput. How?

Use:

```text
customer_id
     |
     v
Kafka record key
     |
     v
Partition
```

All events for the same customer go to the same partition.

```text
Customer A -> P0
Customer B -> P1
Customer C -> P2
```

Different customers can be processed in parallel.

### Design

- Key records by customer ID
- Use enough partitions for throughput
- Enable producer idempotence
- Avoid multiple producers independently ordering the same customer's events
- Don't parallelize processing of one partition in a way that reorders records

### Core idea

> Per-customer ordering + many customers across many partitions = high throughput with scoped ordering.

---

## Q43. Need exactly-once delivery from Kafka into a relational database. How?

Kafka's native exactly-once guarantee does not automatically make an arbitrary database write exactly-once.

### Common approach 1 — Idempotent database writes

```text
Kafka
  |
  v
Consumer
  |
  v
DB UPSERT
  |
  v
Commit Kafka offset
```

Use a stable event/business ID.

If the event is processed twice:

```text
First -> INSERT/UPSERT
Second -> same key -> UPDATE/ignore
```

### Approach 2 — Store offset with DB data

Store the Kafka offset in the same database transaction as the business data.

```text
DB Transaction
   |
   +--> Business data
   |
   +--> Kafka offset
```

Both succeed or both fail.

### Key point

> For external systems, exactly-once usually requires an idempotent sink or a transaction that includes the offset and business data.

---

## Q44. Consumer group keeps rebalancing and processing stalls. What is happening?

Repeated rebalances usually mean consumers are repeatedly leaving or being considered dead.

### Common cause 1 — Processing takes too long

```text
poll()
 |
 v
Long processing
 |
 X
max.poll.interval.ms exceeded
 |
 v
Rebalance
```

### Fix

- Reduce `max.poll.records`
- Optimize processing
- Increase `max.poll.interval.ms` if appropriate
- Offload work carefully while continuing to poll

### Cause 2 — Heartbeat/session issue

Possible:

- Long GC pause
- Network issue
- Bad timeout configuration

### Cause 3 — Deployment churn

Frequent restarts can cause repeated membership changes.

### Fix

- Static membership
- Cooperative rebalancing
- Correct timeout tuning

---

## Q45. A new schema breaks existing consumers. How do you prevent it?

This is a **schema governance** problem.

### Prevention

Use Schema Registry compatibility checks.

```text
Developer
   |
   v
CI/CD
   |
   v
Schema compatibility check
   |
   +---- FAIL -> Do not deploy
   |
   +---- PASS -> Deploy
```

### Good practices

- Use BACKWARD/FULL compatibility as appropriate
- Add fields with defaults
- Avoid breaking type changes
- Avoid unsafe renames
- Validate schemas in CI
- Define schema ownership

### Goal

> A breaking schema should fail during development/deployment, not after reaching production.

---

## Q46. One broker is overloaded while others are underutilized. How do you rebalance?

First diagnose the reason.

### Check 1 — Leader imbalance

Produce and fetch traffic goes through partition leaders.

### Check 2 — Hot partitions

One partition may have much higher traffic.

### Check 3 — Replica distribution

Partitions may be unevenly distributed.

### Possible actions

- Rebalance partition leadership
- Reassign partitions
- Move replicas to other brokers
- Throttle reassignment
- Fix producer key skew if a hot key is the root cause

### Important

> Moving partitions treats the symptom. If the root cause is a hot key, fix the partitioning strategy.

---

## Q47. Reprocess the last 3 days without disturbing live consumers. How?

Create a **new consumer group**.

```text
Production Group
    |
    +----> Live processing

Replay Group
    |
    +----> Last 3 days
```

Why?

Consumer offsets are maintained per consumer group.

Therefore:

```text
Live Group offsets
        !=
Replay Group offsets
```

### Process

1. Create a separate `group.id`.
2. Find the offsets corresponding to 3 days ago.
3. Start the replay consumer from those offsets.
4. Keep live consumers unchanged.
5. Make the destination idempotent if writing to the same sink.

### Core idea

> Kafka's replayability comes from retained data plus independent consumer-group offsets.

---

## Q48. How do you decide the partition count for a high-volume topic?

Partition count affects:

- Throughput
- Consumer parallelism
- Storage
- Rebalancing
- Recovery time
- Operational complexity

### Think about consumer throughput

Suppose:

```text
One consumer = 10,000 records/sec

Required = 50,000 records/sec
```

You may need approximately:

```text
5 partitions
```

to support that level of parallel consumer processing, assuming the workload is evenly distributed.

In practice, add reasonable headroom.

### Too few partitions

```text
Low parallelism
Low throughput
```

### Too many partitions

```text
More metadata
More resources
More replication work
Longer recovery/reassignment
```

### Important

Adding partitions later can change keyed partition mapping, so partition count should be chosen carefully.

---

## Q49. Acknowledged messages appear to have been lost. How do you root-cause it?

Do not immediately assume Kafka lost the data.

Check each layer.

### Step 1 — Producer

Check:

```text
acks
retries
enable.idempotence
delivery.timeout.ms
```

### Step 2 — Replication

Check:

```text
replication.factor
min.insync.replicas
ISR
```

### Step 3 — Unclean election

Check whether an out-of-sync replica became leader.

### Step 4 — Consumer

Maybe the data exists but the consumer skipped it because of:

- Premature offset commit
- New group starting at latest
- Incorrect offset reset

### Step 5 — Retention

Maybe the record aged out before the consumer read it.

### Mental model

```text
Producer
   ↓
Broker
   ↓
Replication
   ↓
Consumer
   ↓
Retention
```

Root-cause the entire path instead of blaming Kafka immediately.

---

## Q50. Stateful Kafka Streams application is slow to recover after failure. How do you make failover fast?

The main problem is often:

```text
Large local state
      |
      v
Failure
      |
      v
Rebuild state from changelog
      |
      v
Slow recovery
```

### Solution 1 — Standby replicas

Configure:

```text
num.standby.replicas
```

A standby keeps a warm copy of state.

```text
Instance A -> Active
Instance B -> Standby
```

If A fails:

```text
B -> Take over quickly
```

### Solution 2 — Static membership

Stable instance identity reduces unnecessary reassignment during short restarts.

### Solution 3 — Cooperative rebalancing

Move only the work that actually needs to move.

### Solution 4 — Healthy changelog topics

Make sure state-store changelogs are appropriately configured and compacted.

### Solution 5 — Balance state

Avoid one instance holding an unusually large amount of state.

### Core idea

> Fast Kafka Streams recovery means avoiding a full state rebuild whenever possible.

---

# Quick Revision — 50 Questions

| Q | Topic | Remember |
|---|---|---|
| 1 | Architecture | Broker, topic, partition, producer, consumer, controller |
| 2 | Partition | Ordering + parallelism |
| 3 | Ordering | Ordering is per partition |
| 4 | Replication | Leader, follower, ISR, HW, LEO |
| 5 | Controller | Cluster metadata/coordination |
| 6 | KRaft | Removes ZooKeeper dependency |
| 7 | High Watermark | Safe visibility/durability boundary |
| 8 | Leader Election | ISR preferred; unclean election can lose data |
| 9 | Throughput | Batching, sequential I/O, compression, zero-copy |
| 10 | Log Segment | Partition split into segments + indexes |
| 11 | Produce Flow | Serialize → partition → batch → broker → ACK |
| 12 | acks | 0 / 1 / all |
| 13 | Idempotence | Prevent retry duplicates |
| 14 | Batching | batch.size + linger.ms + buffer.memory |
| 15 | Partitioner | Keyed + sticky keyless partitioning |
| 16 | In-flight | Retries can reorder without idempotence |
| 17 | Compression | Compress batches |
| 18 | Consumer Group | One consumer per partition within group |
| 19 | poll() | Fetch + group management + records |
| 20 | Offset | Commit consumer progress |
| 21 | offset.reset | Used when no valid committed offset |
| 22 | Rebalance | Redistribute partitions |
| 23 | Timeouts | Heartbeat vs session vs poll |
| 24 | Static Membership | Stable consumer identity |
| 25 | Assignors | Range, RR, Sticky, CooperativeSticky |
| 26 | Delivery | At-most / At-least / Exactly once |
| 27 | Transactions | Atomic output + offset |
| 28 | Transaction Coordinator | Manages Kafka transactions |
| 29 | Isolation | read_committed vs read_uncommitted |
| 30 | Data Loss | Producer + broker + consumer + retention |
| 31 | Duplicates | Use idempotent sinks |
| 32 | Retention | Time / size / cleanup policy |
| 33 | Compaction | Latest value per key |
| 34 | Policy Choice | Events → delete; state → compact |
| 35 | Tiered Storage | Local hot + remote cold data |
| 36 | Ecosystem | API / Streams / Connect / ksqlDB |
| 37 | Streams Internals | State store + changelog + standby |
| 38 | KStream/KTable | Events vs current state |
| 39 | Connect | Worker + connector + task + converter + SMT |
| 40 | Schema Registry | Schema compatibility |
| 41 | Hot Partition | Fix skew/slow processing |
| 42 | Ordering Design | Key by customer |
| 43 | DB Exactly Once | Idempotent sink or DB transaction |
| 44 | Rebalance Incident | Check poll processing and timeouts |
| 45 | Schema Incident | Registry + CI compatibility checks |
| 46 | Broker Imbalance | Leadership/partition skew |
| 47 | Replay | Separate consumer group |
| 48 | Partition Count | Capacity + parallelism + headroom |
| 49 | Lost Messages | Check producer, ISR, elections, consumer, retention |
| 50 | Streams Recovery | Standby replicas + stable membership |

---

# Final Mental Models

## Kafka Core

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

## Reliability

```text
Producer
   ↓
acks + idempotence
   ↓
Replication
   ↓
ISR + min.insync.replicas
   ↓
Consumer
   ↓
Process
   ↓
Commit Offset
```

## Kafka Ecosystem

```text
              Kafka
                |
     +----------+----------+----------+
     |          |          |          |
 Consumer   Streams     Connect    ksqlDB
     |          |          |          |
Custom App   Process    Integrate    SQL
```

## Data Engineering

```text
Database / Application
          |
       CDC / Producer
          |
          v
        Kafka
          |
     +----+----+
     |    |    |
   Spark Flink ksqlDB
     |    |    |
     +----+----+
          |
          v
   Data Lake / Warehouse
```

---

# Source

The questions and concepts in this document are based on the uploaded:

**Kafka_Interview_Questions.pdf**

The original document contains 50 questions covering Kafka architecture, producers, consumers, delivery semantics, storage, Kafka Streams, Kafka Connect, Schema Registry and scenario-based problems. fileciteturn5file0L15-L82

