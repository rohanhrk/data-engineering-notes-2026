# Python JSON & Payload Handling -- Data Engineering Cookbook

A practical reference for Python JSON operations, nested payloads, file
handling, validation, AWS event formats, Pandas, and PySpark.

## Table of Contents

1.  [JSON vs Python Dictionary](#1-json-vs-python-dictionary)
2.  [Python json module](#2-python-json-module)
3.  [Serialization and
    deserialization](#3-serialization-and-deserialization)
4.  [Accessing and manipulating
    JSON](#4-accessing-and-manipulating-json)
5.  [Nested JSON](#5-nested-json)
6.  [JSON files and JSONL](#6-json-files-and-jsonl)
7.  [Validation and error handling](#7-validation-and-error-handling)
8.  [Data types and serialization](#8-data-types-and-serialization)
9.  [AWS payload examples](#9-aws-payload-examples)
10. [AWS Lambda event formats](#10-aws-lambda-event-formats)
11. [Pandas and PySpark](#11-pandas-and-pyspark)
12. [Payload design best practices](#12-payload-design-best-practices)
13. [Hands-on project](#13-hands-on-project)
14. [Mastery checklist](#14-mastery-checklist)

------------------------------------------------------------------------

## 1. JSON vs Python Dictionary

JSON (JavaScript Object Notation) is a text-based data interchange
format. A Python dictionary is an in-memory Python data structure. They
look similar but are not the same.

**JSON**

``` json
{
    "order_id": "ORD101",
    "amount": 2500,
    "status": "PLACED"
}
```

**Python dictionary**

``` python
order = {
    "order_id": "ORD101",
    "amount": 2500,
    "status": "PLACED"
}
```

  JSON      Python
  --------- -----------------
  Object    `dict`
  Array     `list`
  String    `str`
  Number    `int` / `float`
  `true`    `True`
  `false`   `False`
  `null`    `None`

## 2. Python json module

Python includes a built-in `json` module; no installation is required.

``` python
import json
```

  Function         Conversion                    Purpose
  ---------------- ----------------------------- ---------------------
  `json.dumps()`   Python object → JSON string   Serialize in memory
  `json.dump()`    Python object → JSON file     Write a file
  `json.loads()`   JSON string → Python object   Parse in memory
  `json.load()`    JSON file → Python object     Read a file

``` text
Python dictionary/list --json.dumps()--> JSON string
Python dictionary/list <--json.loads()-- JSON string
```

## 3. Serialization and deserialization

### 3.1 Dictionary to JSON string: `json.dumps()`

``` python
import json

order = {
    "order_id": "ORD101",
    "customer": "Rohan",
    "amount": 2500,
    "status": "PLACED"
}

payload = json.dumps(order)
print(payload)
print(type(payload))  # <class 'str'>
```

### 3.2 Pretty-print JSON

``` python
payload = json.dumps(order, indent=4)
print(payload)
```

### 3.3 Sort keys

``` python
payload = json.dumps(order, sort_keys=True)
```

### 3.4 Compact JSON

``` python
payload = json.dumps(order, separators=(",", ":"))
```

### 3.5 Serialize a list of dictionaries

``` python
orders = [
    {"order_id": "ORD101", "amount": 2500},
    {"order_id": "ORD102", "amount": 3500},
    {"order_id": "ORD103", "amount": 1500}
]

payload = json.dumps(orders, indent=4)
```

### 3.6 JSON string to Python dictionary: `json.loads()`

\`\`\`python payload =
