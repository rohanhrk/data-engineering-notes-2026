"""
Lambda 2 — SQS Event-Driven Consumer (Push-Based)
====================================================
Trigger : SQS (via Event Source Mapping configured in Lambda)
Purpose : Automatically invoked when messages arrive in the SQS queue.
          Processes each order record, performs business logic, and logs
          the results.

Architecture:
    SQS Queue  ──(Event Source Mapping)──▶  This Lambda

How SQS triggers Lambda:
    1. AWS polls the SQS queue on your behalf (you do NOT write polling code).
    2. Messages are delivered in BATCHES (configurable: 1–10 for standard,
       up to 10,000 for FIFO).
    3. If Lambda returns SUCCESS, AWS deletes the messages from the queue.
    4. If Lambda THROWS an exception, messages become visible again after
       the Visibility Timeout expires → automatic retry.
    5. After maxReceiveCount retries, messages move to the Dead-Letter Queue
       (DLQ) if one is configured.

Environment variables required:
    (none — this Lambda only reads from the event payload)

IAM permissions required:
    sqs:ReceiveMessage, sqs:DeleteMessage, sqs:GetQueueAttributes
    (these are granted automatically by the Event Source Mapping)
"""

import json
import logging
from typing import Any

# ---------------------------------------------------------------------------
# Logger setup
# ---------------------------------------------------------------------------
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def process_order(order: dict[str, Any]) -> dict[str, Any]:
    """
    Simulate business logic on a single order.

    In a real-world scenario this could:
      - Write to DynamoDB / RDS
      - Call a payment gateway
      - Trigger a Step Functions workflow
      - Send a confirmation email via SES

    For this demo, we simply enrich the order with a processing flag.
    """
    LOGGER.info("─" * 60)
    LOGGER.info("Processing Order ID : %s", order["order_id"])
    LOGGER.info("Customer            : %s (%s)", order["customer_name"], order["customer_city"])
    LOGGER.info("Order Status        : %s", order["order_status"])
    LOGGER.info("Total Amount        : $%.2f", order["total_amount"])

    # Log each line item
    for item in order.get("items", []):
        LOGGER.info(
            "  • %s  x%d  @ $%.2f  = $%.2f",
            item["product_name"],
            item["quantity"],
            item["unit_price"],
            item["line_total"],
        )

    # Simulate processing result
    processed_order = {
        **order,
        "processing_status": "PROCESSED",
        "processed_by": "sqs-event-consumer-lambda",
    }

    LOGGER.info("Order %s processed successfully ✓", order["order_id"])
    return processed_order


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Entry point — invoked automatically by the SQS Event Source Mapping.

    Key points about the 'event' payload:
      - event["Records"] contains a LIST of SQS messages (batch).
      - Each record has:
          • record["body"]              → the actual message (our JSON order)
          • record["messageId"]         → SQS-assigned message ID
          • record["receiptHandle"]     → used internally by AWS to delete
          • record["messageAttributes"] → metadata we set in the producer
          • record["attributes"]        → SQS system attributes
              - ApproximateReceiveCount → how many times this msg was delivered
              - SentTimestamp           → epoch ms when the msg was sent

    IMPORTANT: If you raise an exception, ALL messages in the batch will
    be retried. For partial failure handling, enable
    "ReportBatchItemFailures" in the Event Source Mapping and return
    a batchItemFailures response (shown below).
    """
    LOGGER.info("=" * 60)
    LOGGER.info("SQS Event Consumer Lambda invoked")
    LOGGER.info("Number of records in this batch: %d", len(event["Records"]))
    LOGGER.info("=" * 60)

    # Track failures for partial batch failure reporting
    batch_item_failures = []
    successful_count = 0

    for record in event["Records"]:
        message_id = record["messageId"]

        try:
            # ----- Parse the SQS message body -----
            # The body is a JSON string that we serialized in the producer.
            order = json.loads(record["body"])

            # ----- Log useful SQS metadata -----
            attributes = record.get("attributes", {})
            LOGGER.info(
                "Message ID: %s | Receive Count: %s | Sent At: %s",
                message_id,
                attributes.get("ApproximateReceiveCount", "N/A"),
                attributes.get("SentTimestamp", "N/A"),
            )

            # ----- Log message attributes (set by the producer) -----
            msg_attrs = record.get("messageAttributes", {})
            if msg_attrs:
                LOGGER.info(
                    "Message Attributes → order_status=%s, customer_city=%s",
                    msg_attrs.get("order_status", {}).get("stringValue", "N/A"),
                    msg_attrs.get("customer_city", {}).get("stringValue", "N/A"),
                )

            # ----- Process the order -----
            process_order(order)
            successful_count += 1

        except Exception as exc:
            LOGGER.exception(
                "Failed to process message %s: %s", message_id, exc
            )
            # Report this message as failed so only THIS message is retried,
            # not the entire batch.
            batch_item_failures.append({"itemIdentifier": message_id})

    LOGGER.info("=" * 60)
    LOGGER.info(
        "Batch complete — %d succeeded, %d failed",
        successful_count, len(batch_item_failures),
    )
    LOGGER.info("=" * 60)

    # -----------------------------------------------------------------------
    # Partial Batch Failure Response
    # -----------------------------------------------------------------------
    # To use this, you MUST enable "ReportBatchItemFailures" in your
    # Event Source Mapping configuration. Without it, AWS ignores this
    # response and treats the entire batch as success or failure.
    #
    # If batchItemFailures is empty → all messages are deleted from the queue.
    # If batchItemFailures has entries → only those messages are retried.
    # -----------------------------------------------------------------------
    return {
        "batchItemFailures": batch_item_failures,
    }