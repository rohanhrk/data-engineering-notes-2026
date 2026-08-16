# Monitoring & Job Scheduling

# 26. Monitoring and Spark UI

Spark provides a Web UI for monitoring applications.

## Application UI

The application Web UI is normally available on port `4040` while an application is running.

It provides information about:

- jobs;
- stages;
- tasks;
- executors;
- storage / cached data;
- SQL queries;
- environment information.

## Why the Spark UI is important

When debugging a slow job, inspect:

```text
SQL tab
Jobs tab
Stages tab
Executors tab
Environment tab
Storage tab
```

Look for:

- long-running stages;
- high shuffle read/write;
- skewed task durations;
- spill to disk;
- executor failures;
- excessive GC;
- uneven partition sizes.

## Event logs and History Server

For historical application analysis, enable event logging and configure a Spark History Server.

Typical configuration:

```text
spark.eventLog.enabled=true
spark.eventLog.dir=<shared-event-log-location>
```

The History Server uses those event logs to reconstruct application UIs after the application has finished.

---

---

# 27. Job Scheduling

Spark has scheduling mechanisms for:

- scheduling stages within an application;
- sharing cluster resources across applications;
- controlling resource allocation.

## Important ideas

### FIFO

First-in-first-out scheduling is a common default behavior for jobs in an application.

### Fair scheduling

Fair scheduling can allow concurrent jobs to receive a more balanced share of resources.

### Multiple applications

Cluster managers also determine how resources are allocated between applications.

### Key interview point

There are two useful levels to distinguish:

```text
Cluster manager → allocates cluster resources to applications
Spark scheduler → schedules jobs / stages / tasks inside the Spark application
```

---
