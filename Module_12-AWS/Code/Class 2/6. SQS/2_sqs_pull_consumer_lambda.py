"""
Lambda 3 — SQS Pull-Based Consumer (Manual Trigger)
======================================================
Trigger : Manual invocation (console "Test" button, CLI, or API call)
Purpose : Demonstrates how to MANUALLY poll messages from SQS using the
          boto3 SDK — as opposed to Lambda 2 where AWS polls for you.

Architecture:
    Manual Trigger  ──▶  This Lambda  ──(receive_message)──▶  SQS Queue

Environment variables required:
    SQS_QUEUE_URL : The URL of the SQS queue to pull from.

IAM permissions required:
    sqs:ReceiveMessage — to read messages
    sqs:DeleteMessage  — to remove processed messages
"""

import json
import logging
import os
from typing import Any

import boto3

# ---------------------------------------------------------------------------
# Logger setup
# ---------------------------------------------------------------------------
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# SQS client and queue URL
# ---------------------------------------------------------------------------
sqs_client = boto3.client("sqs")
QUEUE_URL = os.environ["SQS_QUEUE_URL"]


def receive_messages(max_messages: int = 5, wait_time: int = 5) -> list[dict]:
    """
    Pull messages from the SQS queue using long polling.

    Parameters:
        max_messages : Number of messages to fetch (1–10).
        wait_time    : Long polling wait time in seconds (0–20).
                       - 0  = short polling (returns immediately, may miss msgs)
                       - >0 = long polling  (waits up to N seconds for msgs)
                       Long polling REDUCES cost and INCREASES efficiency.

    Key concepts:
        - VisibilityTimeout: After a message is received, it becomes
          INVISIBLE to other consumers for this duration (default 30s).
          If you don't delete it within this window, it reappears in
          the queue and can be picked up again.
        - ReceiptHandle: A temporary token needed to DELETE the message.
          It changes every time the message is received.
    """
    response = sqs_client.receive_message(
        QueueUrl=QUEUE_URL,
        # Maximum number of messages to return in one call
        MaxNumberOfMessages=max_messages,
        # Long polling — wait up to N seconds for messages to arrive
        WaitTimeSeconds=wait_time,
        # Request ALL available attribute types for demo purposes
        AttributeNames=["All"],
        # Also fetch custom message attributes set by the producer
        MessageAttributeNames=["All"],
    )

    # If the queue is empty, "Messages" key may not exist in the response
    messages = response.get("Messages", [])
    LOGGER.info("Received %d messages from SQS", len(messages))
    return messages


def process_order(order: dict[str, Any]) -> None:
    """
    Process a single order record.

    Same business logic as Lambda 2 — in production you'd likely
    share this via a common layer or package.
    """
    LOGGER.info("─" * 60)
    LOGGER.info("Processing Order ID : %s", order["order_id"])
    LOGGER.info("Customer            : %s (%s)", order["customer_name"], order["customer_city"])
    LOGGER.info("Order Status        : %s", order["order_status"])
    LOGGER.info("Total Amount        : $%.2f", order["total_amount"])

    for item in order.get("items", []):
        LOGGER.info(
            "  • %s  x%d  @ $%.2f  = $%.2f",
            item["product_name"],
            item["quantity"],
            item["unit_price"],
            item["line_total"],
        )

    LOGGER.info("Order %s processed successfully ✓", order["order_id"])


def delete_message(receipt_handle: str) -> None:
    """
    Delete a message from the queue after successful processing.

    THIS IS CRITICAL — if you don't delete the message, it will reappear
    in the queue after the VisibilityTimeout expires and get processed
    again (duplicate processing).

    The receipt_handle is a temporary token that uniquely identifies
    THIS particular receive of the message.
    """
    sqs_client.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle,
    )
    LOGGER.info("Message deleted from queue (ReceiptHandle: %s...)", receipt_handle[:20])
    

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Entry point — invoked manually via console Test button, CLI, or API.

    Workflow:
        1. Pull messages from SQS   (receive_message)
        2. Process each message      (business logic)
        3. Delete processed messages (acknowledge completion)

    You can pass optional parameters in the test event:
        {
            "max_messages": 10,
            "wait_time": 5
        }
    """
    LOGGER.info("=" * 60)
    LOGGER.info("SQS Pull Consumer Lambda invoked (manual trigger)")
    LOGGER.info("=" * 60)

    # Allow overriding defaults via the test event payload
    max_messages = event.get("max_messages", 5)
    wait_time = event.get("wait_time", 5)

    LOGGER.info(
        "Polling SQS — max_messages=%d, wait_time=%ds",
        max_messages, wait_time,
    )

    # ----- Step 1: Receive messages from SQS -----
    messages = receive_messages(max_messages=max_messages, wait_time=wait_time)

    if not messages:
        LOGGER.info("No messages available in the queue. Exiting.")
        return {
            "statusCode": 200,
            "body": {"message": "No messages in queue.", "processed": 0},
        }

    # ----- Step 2 & 3: Process each message and delete on success -----
    processed_count = 0
    failed_count = 0

    for message in messages:
        message_id = message["MessageId"]
        receipt_handle = message["ReceiptHandle"]

        try:
            # Log SQS system attributes
            sys_attrs = message.get("Attributes", {})
            LOGGER.info(
                "Message ID: %s | Receive Count: %s | Sent At: %s",
                message_id,
                sys_attrs.get("ApproximateReceiveCount", "N/A"),
                sys_attrs.get("SentTimestamp", "N/A"),
            )

            # Log custom message attributes
            msg_attrs = message.get("MessageAttributes", {})
            if msg_attrs:
                LOGGER.info(
                    "Message Attributes → order_status=%s, customer_city=%s",
                    msg_attrs.get("order_status", {}).get("StringValue", "N/A"),
                    msg_attrs.get("customer_city", {}).get("StringValue", "N/A"),
                )

            # Parse the message body (JSON string → dict)
            order = json.loads(message["Body"])

            # Process the order
            process_order(order)

            # Delete the message ONLY after successful processing
            # If we crash before this line, the message stays in the queue
            # and will be retried — this gives us at-least-once delivery.
            delete_message(receipt_handle)
            processed_count += 1

        except Exception as exc:
            LOGGER.exception(
                "Failed to process message %s: %s", message_id, exc
            )
            # Do NOT delete — the message will become visible again after
            # VisibilityTimeout and can be retried or sent to DLQ.
            failed_count += 1

    # ----- Summary -----
    summary = {
        "statusCode": 200,
        "body": {
            "message": "Pull-based processing complete.",
            "total_received": len(messages),
            "processed": processed_count,
            "failed": failed_count,
        },
    }

    LOGGER.info("=" * 60)
    LOGGER.info("Summary: %s", json.dumps(summary))
    LOGGER.info("=" * 60)

    return summary