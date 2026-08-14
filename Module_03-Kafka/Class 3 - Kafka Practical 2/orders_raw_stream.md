# Create Stream in ksqlDB

## Purpose

`CREATE STREAM` is used to create a logical stream in ksqlDB that continuously reads data from a Kafka topic.

A **Stream** represents an **unbounded sequence of events** where new records keep arriving.

---

## Syntax

```sql
CREATE STREAM stream_name (
    column1 DATA_TYPE,
    column2 DATA_TYPE,
    ...
)
WITH (
    KAFKA_TOPIC = 'topic_name',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'event_ts'
);
```

---

## Column Definitions

```sql
event_id VARCHAR,
```

- Unique identifier for each event.

```sql
event_ts BIGINT,
```

- Event timestamp stored in **Epoch milliseconds**.
- Used for **event-time processing** instead of Kafka's default timestamp.

```sql
event_type VARCHAR,
```

- Specifies the type of event.
- Example:
  - ORDER_CREATED
  - ORDER_CANCELLED
  - ORDER_DELIVERED

```sql
order_id VARCHAR,
customer_id VARCHAR,
```

- Order and customer identifiers.

```sql
product_id VARCHAR,
product_name VARCHAR,
category VARCHAR,
```

- Product-related information.

```sql
quantity INTEGER,
```

- Number of products ordered.

```sql
unit_price DOUBLE,
order_total DOUBLE,
```

- Price of a single product and total order value.

```sql
payment_method VARCHAR,
order_status VARCHAR,
sales_channel VARCHAR,
city VARCHAR,
country VARCHAR
```

- Additional business information.

---

# WITH Clause

The `WITH` clause tells ksqlDB **where the data is located and how it should interpret the messages.**

## KAFKA_TOPIC

```sql
KAFKA_TOPIC = 'ecomm_order_events_raw'
```

- Kafka topic from which the stream reads data.
- Every new message arriving in this topic becomes a new record in the stream.

**Remember:** Where is my data?

---

## KEY_FORMAT

```sql
KEY_FORMAT = 'KAFKA'
```

- Defines the serialization format of the Kafka message key.
- Use `KAFKA` when:
  - the key has no schema
  - or you're unsure about the key format.

**Remember:** How is the key stored?

---

## VALUE_FORMAT

```sql
VALUE_FORMAT = 'JSON'
```

- Defines the serialization format of the message value.
- Here, each Kafka message is stored as JSON.

**Remember:** How is the message body stored?

---

## TIMESTAMP

```sql
TIMESTAMP = 'event_ts'
```

- Uses the `event_ts` column as the event timestamp.
- Required for:
  - Windowing
  - Time-based aggregations
  - Event-time processing

If not specified, ksqlDB uses Kafka's message timestamp.

**Remember:** Which column represents event time?

---

# Memory Trick

Think of the `WITH` clause as answering four questions:

| Property | Question |
|----------|----------|
| KAFKA_TOPIC | Where is the data? |
| KEY_FORMAT | How is the key stored? |
| VALUE_FORMAT | How is the value stored? |
| TIMESTAMP | Which field contains the event time? |

👉 **Memory Formula**

```
Where → Key → Value → Time
```

---

# Interview Definition

`CREATE STREAM` creates a logical stream in ksqlDB that continuously consumes records from a Kafka topic by defining the schema of the incoming data and specifying the topic name, serialization formats, and event timestamp.


```SQL CODE

CREATE STREAM order_raw_events_stream (
    event_id VARCHAR,
    event_ts BIGINT,
    event_type VARCHAR,
    order_id VARCHAR,
    customer_id VARCHAR,
    product_id VARCHAR,
    product_name VARCHAR,
    category VARCHAR,
    quantity INTEGER,
    unit_price DOUBLE,
    order_total DOUBLE,
    payment_method VARCHAR,
    order_status VARCHAR,
    sales_channel VARCHAR,
    city VARCHAR,
    country VARCHAR
) WITH (
    KAFKA_TOPIC = 'ecomm_order_events_raw',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'event_ts'
);

```===========================================================================================================
```sql
-- Displays detailed metadata about the stream.
-- Useful for understanding how the stream is configured.

DESCRIBE order_raw_events_stream EXTENDED;
```

### What does `EXTENDED` show?

- Stream schema (columns and data types)
- Kafka topic associated with the stream
- Key and value formats
- Timestamp column used by the stream
- Partition and replication information
- Any persistent queries reading from or writing to the stream
- Other stream metadata and configuration details

> **Memory Trick:** Think of `DESCRIBE ... EXTENDED` as the stream's **"Profile Card"** or **"Resume"**. It tells you everything about the stream—its structure, configuration, and metadata.

```===========================================================================================================
```sql
-- Reads all records from the stream in real time.
-- `*` selects all columns.
-- `EMIT CHANGES` makes this a **Transient Push Query**, meaning:
--   • Continuously listens for new events.
--   • Automatically displays new records as they arrive.
--   • Runs until you stop it (Ctrl + C) or disconnect.
--   • Does NOT create a new Kafka topic or store any results.

SELECT *
FROM order_raw_events_stream
EMIT CHANGES;
```

### What happens?

1. ksqlDB starts listening to `order_raw_events_stream`.
2. Existing records (depending on the query context) and new incoming records are displayed.
3. Every new event produced to the underlying Kafka topic is immediately shown in the output.
4. The query keeps running until it is manually stopped.

### Example Output

| event_id | order_id | customer_id | order_total |
|----------|----------|-------------|-------------|
| E101 | O1001 | C001 | 2500.00 |
| E102 | O1002 | C002 | 799.00 |
| E103 | O1003 | C003 | 1500.00 |

If a new order arrives:

```json
{
  "event_id": "E104",
  "order_id": "O1004",
  "customer_id": "C004",
  "order_total": 3200.00
}
```

The query automatically prints:

| event_id | order_id | customer_id | order_total |
|----------|----------|-------------|-------------|
| E104 | O1004 | C004 | 3200.00 |


```====================================================================================
```sql
-- Create a new stream by filtering valid order events from an existing stream.
-- This is a Persistent Query (CSAS - CREATE STREAM AS SELECT).
-- It continuously reads data from the source stream and writes the filtered
-- records to a new Kafka topic.

CREATE STREAM validated_raw_order_events_stream

WITH (

    -- Destination Kafka topic where the validated records will be stored.
    KAFKA_TOPIC = 'validated_orders',

    -- Serialization format of the Kafka message key.
    KEY_FORMAT = 'KAFKA',

    -- Serialization format of the Kafka message value.
    VALUE_FORMAT = 'JSON',

    -- Number of partitions for the new Kafka topic.
    -- More partitions allow higher parallelism and throughput.
    PARTITIONS = 3

)

AS

SELECT
    -- Select all columns from the source stream.
    *

FROM order_raw_events_stream

WHERE

    -- Ignore records with missing Event ID.
    event_id IS NOT NULL

    -- Ignore records with missing Order ID.
    AND order_id IS NOT NULL

    -- Ignore records with missing Product ID.
    AND product_id IS NOT NULL

    -- Quantity must be greater than zero.
    AND quantity > 0

    -- Unit price must be greater than zero.
    AND unit_price > 0

    -- Total order value must be greater than zero.
    AND order_total > 0

    -- Ignore cancelled orders.
    AND order_status <> 'cancelled'

-- Keep processing every new incoming event continuously.
EMIT CHANGES;
```

---

# What does this query do?

This query continuously:

1. Reads data from `order_raw_events_stream`.
2. Validates each incoming order.
3. Removes invalid records.
4. Writes only valid records into the `validated_orders` Kafka topic.
5. Creates a new stream named `validated_raw_order_events_stream` over that topic.

---

# Data Flow

```
ecomm_order_events_raw
            │
            ▼
order_raw_events_stream
            │
      Validation Rules
            │
            ▼
validated_raw_order_events_stream
            │
            ▼
validated_orders (Kafka Topic)
```

---

# Validation Rules

A record is accepted only if:

- `event_id` is not NULL
- `order_id` is not NULL
- `product_id` is not NULL
- `quantity > 0`
- `unit_price > 0`
- `order_total > 0`
- `order_status` is not `cancelled`

Otherwise, the record is discarded.

---

# Why use `PARTITIONS = 3`?

- Creates the destination Kafka topic with **3 partitions**.
- Allows multiple consumers or stream tasks to process data in parallel.
- Improves scalability and throughput.

---

# Memory Trick

Think of this query as a **quality filter**.

```
Raw Orders
     │
     ▼
Validation Rules
     │
     ▼
Only Valid Orders
```

**Formula:**

```
CREATE STREAM
        +
AS SELECT
        +
WHERE
        =
New Stream with Filtered Data
```

---

# Interview Definition

`CREATE STREAM ... AS SELECT (CSAS)` is a **persistent query** in ksqlDB that continuously reads records from a source stream, applies transformations or filters, and writes the resulting records into a new Kafka topic while creating a new stream over that topic.

```========================================================================================

```sql
-- Create a TABLE that stores sales summary for each product category.
-- This is a Persistent Query (CTAS - CREATE TABLE AS SELECT).
-- The table is continuously updated as new order events arrive.

CREATE TABLE category_sales_summary_table

WITH (

    -- Kafka topic where the aggregated results will be stored.
    KAFKA_TOPIC = 'category_sales_summary',

    -- Serialization format of the Kafka message key.
    KEY_FORMAT = 'KAFKA',

    -- Serialization format of the Kafka message value.
    VALUE_FORMAT = 'JSON',

    -- Number of partitions for the output Kafka topic.
    PARTITIONS = 3

)

AS

SELECT

    -- Group records based on product category.
    category,

    -- Total number of orders for each category.
    COUNT(*) AS total_orders,

    -- Total quantity of products sold in each category.
    SUM(quantity) AS total_units,

    -- Total revenue generated by each category.
    SUM(order_total) AS gross_revenue

FROM validated_raw_order_events_stream

-- Create one row per category.
GROUP BY category

-- Continuously update the table whenever new events arrive.
EMIT CHANGES;
```

---

# What does this query do?

This query continuously:

1. Reads valid order events.
2. Groups records by **category**.
3. Calculates:
   - Total number of orders
   - Total units sold
   - Total revenue
4. Stores the latest aggregated values in a table.
5. Writes the results to the `category_sales_summary` Kafka topic.

---

# Data Flow

```
validated_raw_order_events_stream
                │
                ▼
         GROUP BY category
                │
      Aggregate Functions
                │
                ▼
category_sales_summary_table
                │
                ▼
category_sales_summary (Kafka Topic)
```

---

# Understanding the Aggregations

Suppose the stream contains:

| Category | Quantity | Order Total |
|----------|---------:|------------:|
| Electronics | 2 | 1000 |
| Grocery | 5 | 500 |
| Electronics | 1 | 700 |
| Grocery | 3 | 300 |

The table becomes:

| Category | Total Orders | Total Units | Gross Revenue |
|----------|-------------:|------------:|--------------:|
| Electronics | 2 | 3 | 1700 |
| Grocery | 2 | 8 | 800 |

Now suppose another event arrives:

| Category | Quantity | Order Total |
|----------|---------:|------------:|
| Electronics | 4 | 2000 |

The table is automatically updated:

| Category | Total Orders | Total Units | Gross Revenue |
|----------|-------------:|------------:|--------------:|
| Electronics | 3 | 7 | 3700 |
| Grocery | 2 | 8 | 800 |

Notice that **no new row is added for Electronics**. Instead, the existing row is updated.

---

# Why `GROUP BY` is Required?

A table stores **one row per key**.

Here, the key is:

```sql
GROUP BY category
```

So each category has exactly one row containing the latest aggregated values.

Without `GROUP BY`, ksqlDB would not know how to organize the rows in the table.

---

# Memory Trick

Think of this query as a **live sales dashboard**.

```
Incoming Orders
        │
        ▼
Group by Category
        │
        ▼
Calculate Totals
        │
        ▼
Update Dashboard
```

**Formula:**

```
GROUP BY
      +
COUNT()
      +
SUM()
      =
Live Summary Table
```

---

# Interview Definition

`CREATE TABLE ... AS SELECT (CTAS)` creates a **persistent table** in ksqlDB by continuously reading data from a source stream or table, applying grouping and aggregations, and maintaining the latest aggregated state for each key in a new Kafka topic.

```===========================================================================
```sql
-- Create a TABLE that calculates city-wise order statistics
-- for every 15-minute time window.
--
-- This is a Persistent Query (CTAS - CREATE TABLE AS SELECT).
-- The table continuously updates as new order events arrive.

CREATE TABLE city_orders_15_minute

WITH (

    -- Kafka topic where the windowed aggregation results are stored.
    KAFKA_TOPIC = 'city_orders_15_minutes',

    -- Serialization format of the Kafka message key.
    KEY_FORMAT = 'KAFKA',

    -- Serialization format of the Kafka message value.
    VALUE_FORMAT = 'JSON',

    -- Number of partitions for the output Kafka topic.
    PARTITIONS = 3

)

AS

SELECT

    -- Group records by city.
    city,

    -- Total number of orders in each 15-minute window.
    COUNT(*) AS order_count,

    -- Total revenue generated in each 15-minute window.
    SUM(order_total) AS city_revenue

FROM validated_raw_order_events_stream

-- Divide the stream into fixed 15-minute windows.
WINDOW TUMBLING (

    -- Each window covers exactly 15 minutes.
    SIZE 15 MINUTES,

    -- Accept late events for up to 2 minutes after
    -- the window officially closes.
    GRACE PERIOD 2 MINUTES

)

-- Create one aggregated row per city for each window.
GROUP BY city

-- Continuously update the table as new events arrive.
EMIT CHANGES;
```

---

# What does this query do?

This query continuously:

1. Reads validated order events.
2. Splits the stream into **15-minute tumbling windows**.
3. Groups events by **city**.
4. Calculates:
   - Number of orders
   - Total revenue
5. Stores the aggregated results in a table.
6. Writes the results to the `city_orders_15_minutes` Kafka topic.

---

# Data Flow

```
validated_raw_order_events_stream
                │
                ▼
     15-Minute Tumbling Window
                │
                ▼
          GROUP BY city
                │
                ▼
      COUNT() + SUM(order_total)
                │
                ▼
     city_orders_15_minute
                │
                ▼
city_orders_15_minutes (Kafka Topic)
```

---

# Example

Incoming events:

| Time | City | Order Total |
|------|------|------------:|
| 10:01 | Delhi | 500 |
| 10:05 | Delhi | 1200 |
| 10:07 | Mumbai | 800 |
| 10:13 | Delhi | 700 |

Window:

```
10:00 ---------------------- 10:15
```

Table after aggregation:

| City | Order Count | City Revenue |
|------|------------:|-------------:|
| Delhi | 3 | 2400 |
| Mumbai | 1 | 800 |

---

# Grace Period Example

Window:

```
10:00 ---------------- 10:15
                 Window Ends
```

Grace Period:

```
10:15 ---------------- 10:17
```

A record with:

```
Event Time : 10:14
Arrival Time : 10:16
```

is **accepted** because it arrived within the 2-minute grace period.

A record arriving at **10:18** for that same window is **too late** and will not be included.

---

# Why is this a TABLE?

Because each row represents the **latest aggregated state** for a combination of:

- **City**
- **15-minute time window**

As new events arrive within the same window, the existing row is updated instead of creating a separate row for every event.

---

# Memory Trick

Think of this query as a **live city sales dashboard** that refreshes every 15 minutes.

```
Incoming Orders
        │
        ▼
15-Minute Window
        │
        ▼
Group by City
        │
        ▼
Count Orders + Revenue
        │
        ▼
Live Dashboard
```

**Formula:**

```
WINDOW
      +
GROUP BY
      +
COUNT()
      +
SUM()
      =
Windowed Summary Table
```

---

# Interview Definition

This query creates a **windowed table** that continuously computes city-wise order statistics for every **15-minute tumbling window**. It groups events by city, calculates the order count and total revenue, accepts late events for up to **2 minutes** using the grace period, and stores the latest aggregated results in a Kafka topic.