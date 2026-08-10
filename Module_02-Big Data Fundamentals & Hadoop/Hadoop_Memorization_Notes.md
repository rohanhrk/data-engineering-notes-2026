# Apache Hadoop — Memorization & Interview Notes

> **Source:** Apache Hadoop official documentation  
> **Current documentation:** https://hadoop.apache.org/docs/current/  
> **Purpose:** Fast revision, conceptual understanding, and interview preparation.

---

## 1. Hadoop in One Minute

**Hadoop = Distributed Storage + Distributed Resource Management + Distributed Processing**

Remember the 3 core parts:

| Component | Main job | Easy memory |
|---|---|---|
| **HDFS** | Stores big data across machines | **Storage** |
| **YARN** | Manages cluster resources and applications | **Resource Manager** |
| **MapReduce** | Processes data in parallel | **Processing** |
| **Hadoop Common** | Shared libraries/utilities | **Foundation** |

### One-line memory trick

> **HDFS stores → YARN manages → MapReduce processes**

---

# 2. Why Hadoop?

Traditional single-machine systems struggle when data becomes very large.

Hadoop addresses this by distributing data and computation across multiple machines.

### Key characteristics

- Distributed
- Scalable
- Fault tolerant
- Designed for large datasets
- Works with commodity hardware
- Data can be processed in parallel
- Easy to expand by adding machines

### Remember

> **More data → More machines → Distributed storage + processing**

---

# 3. HDFS — Hadoop Distributed File System

HDFS is Hadoop's primary distributed storage system.

Its main idea:

> **Split large files into blocks and distribute those blocks across DataNodes.**

## Main components

### NameNode

**NameNode = Master + Metadata Manager**

It manages:

- File-system namespace
- File and directory metadata
- File → block mapping
- Block → DataNode information
- Permissions and related metadata

### DataNode

**DataNode = Worker + Actual Data Storage**

It:

- Stores actual HDFS blocks
- Serves read/write requests
- Creates/deletes/replicates blocks as instructed
- Reports information to the NameNode

### Client

The client:

1. Contacts NameNode for metadata
2. Gets information about where blocks are located
3. Performs actual data I/O with DataNodes

### Golden rule

> **NameNode knows WHERE the data is.  
> DataNode stores the actual data.**

---

# 4. HDFS Read Flow

Suppose:

```text
file.txt
   ↓
NameNode
   ↓
Find block locations
   ↓
DataNode(s)
   ↓
Read actual blocks
```

### Memorize

> **Metadata from NameNode → Data from DataNode**

The client does **not** send the entire file through the NameNode.

---

# 5. HDFS Write Flow

Simplified flow:

```text
Client
  ↓
NameNode
  ↓
Get block allocation / DataNode locations
  ↓
DataNode pipeline
  ↓
Block replicas
```

The NameNode handles metadata and allocation decisions while DataNodes handle actual block storage.

---

# 6. HDFS Blocks

Large files are divided into blocks.

Example:

```text
Large File
   |
   +-- Block 1
   +-- Block 2
   +-- Block 3
   +-- Block 4
```

Blocks can be distributed across multiple DataNodes.

### Why blocks?

- Enables distributed storage
- Enables parallel processing
- Makes large files manageable
- Supports fault tolerance through replication

### Important

Do not confuse:

```text
File ≠ Block ≠ Record
```

A file is divided into blocks; processing frameworks can then process the data contained in those blocks.

---

# 7. Replication

HDFS can keep multiple copies of blocks.

Example with replication factor 3:

```text
Block A
 ├── DataNode 1
 ├── DataNode 2
 └── DataNode 3
```

### Why replication?

If one DataNode fails, another copy can be used.

### Memory trick

> **Replication = copies for fault tolerance**

---

# 8. Rack Awareness

Hadoop can understand the physical/network rack location of DataNodes.

Why?

If replicas were placed on only one rack and that rack failed, all copies could become unavailable.

Therefore, replica placement considers rack topology.

### Remember

> **Rack awareness protects against rack-level failure.**

---

# 9. NameNode Metadata

Important concept:

```text
Namespace
   +
File → Block mapping
   +
Block → DataNode location information
```

The NameNode manages metadata; it does not normally store the actual user file blocks.

---

# 10. fsimage vs Edit Logs

This is a very important interview topic.

### fsimage

A persistent snapshot of the HDFS namespace/metadata.

Think:

> **fsimage = saved snapshot**

### Edit logs

Record changes made to the namespace.

Examples:

- Create file
- Delete file
- Rename file
- Change metadata

Think:

> **EditLog = changes after the snapshot**

### Easy analogy

```text
fsimage = saved game
EditLog = actions after saving
```

---

# 11. Checkpointing

Checkpointing combines the namespace snapshot and edits into a newer snapshot.

Conceptually:

```text
Old fsimage
     +
Edit logs
     ↓
New checkpoint
```

This keeps metadata recovery manageable.

---

# 12. Secondary NameNode

### Very important misconception

> **Secondary NameNode is NOT a backup NameNode.**

Its major role is related to **checkpointing**.

It periodically obtains namespace information and edit information and creates checkpoints.

### Remember

```text
Secondary NameNode
        ↓
Checkpointing
        ↓
Helps control EditLog growth
```

---

# 13. NameNode High Availability

In an HA configuration, Hadoop can use:

- **Active NameNode**
- **Standby NameNode**

The goal is to avoid a single NameNode failure taking down the namespace service.

### Remember

> **Secondary NameNode ≠ Standby NameNode**

| Secondary NameNode | Standby NameNode |
|---|---|
| Checkpointing role | HA failover role |
| Not a hot backup | Part of HA architecture |
| Does not simply replace failed NameNode | Can become Active |

---

# 14. HDFS Safe Mode

Safe mode is a NameNode state in which normal namespace changes are restricted.

It is primarily associated with startup and block-replication safety checks.

### Remember

> **Safe mode = protect the filesystem while checking cluster/block state**

---

# 15. HDFS Fault Tolerance

HDFS achieves fault tolerance using mechanisms such as:

- Block replication
- Failure detection
- Re-replication
- Rack-aware placement
- NameNode HA where configured

### Memory

> **Failure happens → detect → recover/re-replicate**

---

# 16. HDFS Commands — Must Know

### List files

```bash
hdfs dfs -ls /
```

### Create directory

```bash
hdfs dfs -mkdir /data
```

### Upload local file to HDFS

```bash
hdfs dfs -put file.txt /data/
```

### Download from HDFS

```bash
hdfs dfs -get /data/file.txt .
```

### View file

```bash
hdfs dfs -cat /data/file.txt
```

### Delete

```bash
hdfs dfs -rm /data/file.txt
```

### Check disk usage

```bash
hdfs dfs -du -h /data
```

### HDFS filesystem status

```bash
hdfs dfsadmin -report
```

### Memory

> **ls → mkdir → put → get → cat → rm**

---

# 17. YARN

YARN = **Yet Another Resource Negotiator**

Its fundamental purpose is to separate:

> **Resource management** from **application/job execution**

The main components are:

```text
ResourceManager
      |
      +------ NodeManager
      |
      +------ ApplicationMaster
```

---

# 18. ResourceManager

**ResourceManager = Global cluster resource authority**

It manages resources across the cluster.

It has two important conceptual parts:

### Scheduler

Allocates resources among applications.

It considers things such as:

- Queues
- Capacity
- Resource requirements

### ApplicationsManager

Handles application submission and management of ApplicationMasters.

### Memory

> **RM = Resource Manager for the whole cluster**

---

# 19. NodeManager

**NodeManager = Per-machine agent**

Runs on each worker machine.

Responsibilities include:

- Managing containers
- Monitoring resource usage
- CPU
- Memory
- Disk
- Network
- Reporting information to ResourceManager

### Memory

> **One NodeManager per worker node**

---

# 20. ApplicationMaster

**ApplicationMaster = One per application**

It:

- Negotiates resources from ResourceManager
- Works with NodeManagers
- Coordinates application execution
- Monitors application tasks

### Remember

```text
Cluster → ResourceManager
Machine → NodeManager
Application → ApplicationMaster
```

This is one of the best Hadoop interview mnemonics.

---

# 21. Container

A YARN **Container** represents allocated resources on a node.

Resources can include:

- Memory
- CPU
- Disk
- Network

Think:

> **Container = allocated resource package**

---

# 22. YARN Job Flow

Simplified:

```text
Client
  ↓
ResourceManager
  ↓
ApplicationMaster
  ↓
Resource requests
  ↓
ResourceManager Scheduler
  ↓
Containers on NodeManagers
  ↓
Tasks execute
```

### Easy memory

> **Client → RM → AM → Containers → Tasks**

---

# 23. Scheduler

The Scheduler is responsible for allocating resources.

Important:

> The Scheduler is a scheduler, not the application monitor.

It allocates resources according to policies and constraints.

Examples of scheduler policies include:

- CapacityScheduler
- FairScheduler

---

# 24. MapReduce

MapReduce is a distributed processing model.

Basic idea:

```text
Input
  ↓
Map
  ↓
Shuffle & Sort
  ↓
Reduce
  ↓
Output
```

### Memory trick

> **Map → Shuffle → Reduce**

---

# 25. Mapper

Mapper processes input records and produces intermediate key-value pairs.

Example:

Input:

```text
cat dog cat
```

Mapper conceptually produces:

```text
(cat, 1)
(dog, 1)
(cat, 1)
```

---

# 26. Shuffle and Sort

The framework groups mapper output by key.

Example:

```text
(cat,1)
(cat,1)
(dog,1)
```

becomes conceptually:

```text
cat → [1,1]
dog → [1]
```

### Why important?

The reducer receives values grouped by key.

### Remember

> **Shuffle = move/group mapper output for reducers**

---

# 27. Reducer

Reducer receives:

```text
key → list of values
```

and produces the final result.

Example:

```text
cat → [1,1]
dog → [1]
```

Reducer:

```text
cat → 2
dog → 1
```

---

# 28. WordCount — Classic Example

Input:

```text
hello world
hello hadoop
```

Mapper:

```text
hello → 1
world → 1
hello → 1
hadoop → 1
```

Shuffle:

```text
hadoop → [1]
hello  → [1,1]
world  → [1]
```

Reducer:

```text
hadoop → 1
hello  → 2
world  → 1
```

---

# 29. MapReduce Data Locality

A major Hadoop idea:

> **Move computation toward data whenever possible.**

Instead of moving huge datasets to the compute node, Hadoop tries to execute processing close to where the data resides.

### Memory

> **Don't move data if you can move computation.**

---

# 30. Hadoop Architecture — Big Picture

```text
                    HADOOP
                       |
        +--------------+--------------+
        |              |              |
       HDFS           YARN         MapReduce
        |              |              |
     Storage       Resources       Processing
        |              |
   +----+----+     +---+---+
   |         |     |       |
NameNode  DataNodes RM   NodeManagers
                         |
                    Containers
                         |
                  ApplicationMaster
```

---

# 31. HDFS vs YARN vs MapReduce

| Topic | HDFS | YARN | MapReduce |
|---|---|---|---|
| Main purpose | Storage | Resource management | Processing |
| Think | Files | Resources | Computation |
| Main components | NN, DN | RM, NM, AM | Mapper, Reducer |
| Handles | Data | Cluster resources | Jobs/tasks |

### One-line answer

> **HDFS stores data, YARN manages resources, and MapReduce processes data.**

---

# 32. Master vs Worker — Quick Revision

| Master/Service | Worker |
|---|---|
| NameNode | DataNode |
| ResourceManager | NodeManager |
| ApplicationMaster | Containers/tasks |

Be careful: ApplicationMaster is **per application**, not simply a permanent cluster master.

---

# 33. Most Important Differences

## NameNode vs DataNode

**NameNode:**
- Metadata
- Namespace
- Block mapping

**DataNode:**
- Actual blocks
- Read/write
- Block operations

---

## ResourceManager vs NodeManager

**ResourceManager:**
- Cluster-level resource management

**NodeManager:**
- Machine-level resource management

---

## Secondary NameNode vs Standby NameNode

**Secondary NameNode:**
- Checkpointing

**Standby NameNode:**
- High availability/failover

---

## fsimage vs EditLog

**fsimage:**
- Snapshot

**EditLog:**
- Changes

---

# 34. Important Terminology

### Block

Unit into which HDFS files are divided.

### Replication

Multiple copies of blocks.

### Namespace

Files/directories and their metadata structure.

### Metadata

Information describing the filesystem rather than the actual file contents.

### Container

YARN resource allocation.

### Application

A job/workload submitted to YARN.

### ApplicationMaster

Coordinates one application.

### Data locality

Running computation near the data.

### Rack awareness

Using rack topology for better block placement and fault tolerance.

---

# 35. Top Interview Questions

### Q1. What is Hadoop?

A distributed framework/ecosystem designed for storing and processing large datasets across clusters of machines.

### Q2. What is HDFS?

A distributed filesystem designed for large datasets and fault-tolerant storage.

### Q3. What does NameNode do?

Manages HDFS namespace and metadata, including mappings between files, blocks, and DataNodes.

### Q4. Does NameNode store actual file data?

No. Data blocks are stored on DataNodes.

### Q5. What does DataNode do?

Stores and serves HDFS data blocks and participates in block management.

### Q6. Why replication?

To provide fault tolerance when machines or disks fail.

### Q7. What is YARN?

Hadoop's resource-management and application-management layer.

### Q8. What is ResourceManager?

The global authority for cluster resources.

### Q9. What is NodeManager?

The per-machine agent that manages containers and monitors resources.

### Q10. What is ApplicationMaster?

The per-application component that negotiates resources and coordinates execution.

### Q11. What is MapReduce?

A distributed processing model based primarily on Map and Reduce stages.

### Q12. What happens between Map and Reduce?

Shuffle and sort/grouping of intermediate data.

### Q13. Is Secondary NameNode a backup NameNode?

No. Its major role is checkpointing.

### Q14. What is data locality?

Processing data close to where it is stored.

---

# 36. 30-Second Interview Explanation

If an interviewer asks:

**"Explain Hadoop architecture."**

Say:

> Hadoop consists primarily of HDFS, YARN, and MapReduce. HDFS provides distributed storage using NameNode and DataNodes. The NameNode manages filesystem metadata while DataNodes store actual data blocks. YARN manages cluster resources using ResourceManager, NodeManagers, and ApplicationMasters. MapReduce provides a distributed processing model using Mapper and Reducer stages, with shuffle and sort between them. Hadoop also uses concepts such as replication, rack awareness, and data locality for fault tolerance and efficient processing.

---

# 37. Ultra-Short Revision Sheet

```text
HADOOP
│
├── HDFS → STORAGE
│   ├── NameNode → Metadata
│   ├── DataNode → Actual blocks
│   ├── Block → Unit of storage
│   ├── Replication → Fault tolerance
│   └── Rack Awareness → Rack failure protection
│
├── YARN → RESOURCE MANAGEMENT
│   ├── ResourceManager → Cluster
│   ├── NodeManager → Machine
│   ├── ApplicationMaster → Application
│   └── Container → Resources
│
└── MAPREDUCE → PROCESSING
    ├── Mapper
    ├── Shuffle & Sort
    └── Reducer
```

---

# 38. Must-Memorize Lines

> **HDFS = Storage**

> **NameNode = Metadata**

> **DataNode = Actual Data**

> **Replication = Fault Tolerance**

> **Secondary NameNode = Checkpointing**

> **Standby NameNode = HA**

> **YARN = Resource Management**

> **ResourceManager = Cluster**

> **NodeManager = Machine**

> **ApplicationMaster = Application**

> **Container = Allocated Resources**

> **MapReduce = Distributed Processing**

> **Map → Shuffle/Sort → Reduce**

> **Data Locality = Move computation toward data**

---

# 39. Final Mental Model

When you see a Hadoop problem, ask:

```text
Where is the data?
        ↓
      HDFS

Who manages cluster resources?
        ↓
      YARN

Who processes the data?
        ↓
   MapReduce
```

Then remember:

```text
HDFS
  ↓
NameNode → "Where is it?"
DataNode → "I have it."

YARN
  ↓
ResourceManager → "Cluster resources"
NodeManager → "My machine resources"
ApplicationMaster → "My application"

MapReduce
  ↓
Mapper → "Create intermediate output"
Shuffle → "Group by key"
Reducer → "Create final output"
```

---

# 40. Final Memory Formula

## **Hadoop = HDFS + YARN + Processing**

### HDFS

**N → Metadata**

**D → Data**

### YARN

**R → ResourceManager**

**N → NodeManager**

**A → ApplicationMaster**

### MapReduce

**M → Map**

**S → Shuffle**

**R → Reduce**

### The complete story

> **Store → Manage → Process**

> **HDFS → YARN → MapReduce**

---

## Official Documentation

- Apache Hadoop Current Documentation:
  https://hadoop.apache.org/docs/current/
- HDFS:
  https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/
- YARN:
  https://hadoop.apache.org/docs/current/hadoop-yarn/
- MapReduce:
  https://hadoop.apache.org/docs/current/hadoop-mapreduce/

