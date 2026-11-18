"""
Lambda 1 — SQS Producer (Mock Data Generator)
================================================
Trigger : Amazon EventBridge Scheduler (runs on a cron/rate schedule)
Purpose : Generates fake e-commerce order records and publishes them to an
          SQS queue so downstream consumers can process them.

Architecture:
    EventBridge Schedule  ──▶  This Lambda  ──▶  SQS Queue

Environment variables required:
    SQS_QUEUE_URL : The URL of the target SQS queue.

IAM permissions required:
    sqs:SendMessage on the target queue.
"""

import json
import logging
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3

# ---------------------------------------------------------------------------
# Logger setup — CloudWatch will capture everything at INFO level and above.
# ---------------------------------------------------------------------------
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Boto3 SQS client — created at module level so it is reused across warm
# invocations (saves ~100-200 ms on subsequent calls).
# ---------------------------------------------------------------------------
sqs_client = boto3.client("sqs")

# The queue URL is injected via an environment variable during deployment.
QUEUE_URL = os.environ["SQS_QUEUE_URL"]

# ---------------------------------------------------------------------------
# Sample data pools — used to build realistic-looking order records.
# ---------------------------------------------------------------------------
PRODUCTS = [
    {"id": "P001", "name": "Wireless Mouse",       "price": 29.99},
    {"id": "P002", "name": "Mechanical Keyboard",   "price": 79.99},
    {"id": "P003", "name": "USB-C Hub",             "price": 45.00},
    {"id": "P004", "name": "Monitor Stand",          "price": 35.50},
    {"id": "P005", "name": "Webcam HD",              "price": 64.99},
    {"id": "P006", "name": "Noise Cancelling Headphones", "price": 199.99},
    {"id": "P007", "name": "Laptop Sleeve",          "price": 24.99},
    {"id": "P008", "name": "Portable SSD 1TB",       "price": 109.99},
]

CUSTOMERS = [
    {"id": "C101", "name": "Alice Johnson",  "city": "Mumbai"},
    {"id": "C102", "name": "Bob Smith",      "city": "Delhi"},
    {"id": "C103", "name": "Charlie Lee",    "city": "Bangalore"},
    {"id": "C104", "name": "Diana Patel",    "city": "Hyderabad"},
    {"id": "C105", "name": "Eve Martinez",   "city": "Pune"},
]

ORDER_STATUSES = ["PLACED", "CONFIRMED", "SHIPPED", "DELIVERED"]

def generate_order() -> dict[str, Any]:
    """
    Build a single mock e-commerce order.

    Each order contains:
      - A unique order_id (UUID)
      - A randomly chosen customer
      - 1–3 randomly chosen products with random quantities
      - A calculated total_amount
      - A random order status
      - An ISO-8601 timestamp
    """
    customer = random.choice(CUSTOMERS)

    # Pick 1-3 unique products for this order
    num_items = random.randint(1, 3)
    selected_products = random.sample(PRODUCTS, num_items)

    # Build line items with random quantities (1–5)
    items = []
    total_amount = 0.0
    for product in selected_products:
        quantity = random.randint(1, 5)
        line_total = round(product["price"] * quantity, 2)
        total_amount += line_total
        items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "unit_price": product["price"],
            "quantity": quantity,
            "line_total": line_total,
        })

    order = {
        "order_id": str(uuid.uuid4()),
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "customer_city": customer["city"],
        "items": items,
        "total_amount": round(total_amount, 2),
        "order_status": random.choice(ORDER_STATUSES),
        "order_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return order

def send_to_sqs(order: dict[str, Any]) -> dict[str, Any]:
    """
    Send a single order message to the SQS queue.

    MessageGroupId is NOT set because this example uses a Standard queue.
    If you switch to a FIFO queue, you must add:
        MessageGroupId   — logical grouping key
        MessageDeduplicationId — or enable content-based dedup on the queue
    """
    response = sqs_client.send_message(
        QueueUrl=QUEUE_URL,
        # The message body is the JSON-serialized order
        MessageBody=json.dumps(order),
        # MessageAttributes let consumers filter/inspect metadata without
        # parsing the body — useful with SQS filter policies.
        MessageAttributes={
            "order_status": {
                "DataType": "String",
                "StringValue": order["order_status"],
            },
            "customer_city": {
                "DataType": "String",
                "StringValue": order["customer_city"],
            },
        },
    )
    return response

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Entry point invoked by EventBridge Scheduler.

    The EventBridge event payload is not used — this Lambda simply generates
    a batch of mock orders on every invocation.
    """
    LOGGER.info("EventBridge trigger received. Event: %s", json.dumps(event))

    # Number of mock orders to generate per invocation
    batch_size = int(os.environ.get("BATCH_SIZE", "20"))
    LOGGER.info("Generating %d mock orders...", batch_size)

    results = []

    for i in range(batch_size):
        order = generate_order()
        LOGGER.info(
            "Order %d/%d generated — order_id=%s, total=%.2f",
            i + 1, batch_size, order["order_id"], order["total_amount"],
        )

        # Send each order as a separate SQS message
        sqs_response = send_to_sqs(order)
        message_id = sqs_response["MessageId"]
        LOGGER.info("Message sent to SQS — MessageId=%s", message_id)

        results.append({
            "order_id": order["order_id"],
            "sqs_message_id": message_id,
        })

    summary = {
        "statusCode": 200,
        "body": {
            "message": f"Successfully published {batch_size} orders to SQS.",
            "orders": results,
        },
    }

    LOGGER.info("Producer Lambda completed. Summary: %s", json.dumps(summary))
    return summary