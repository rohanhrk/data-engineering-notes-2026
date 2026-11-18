"""Lambda example: listen to S3 create events and publish status to SNS.

Expected flow:
1. S3 uploads trigger this Lambda.
2. The Lambda extracts bucket, object key, event name, and event time.
3. On success, it publishes a "Success" notification to SNS.
4. On failure, it publishes a "Failed" notification to SNS.
"""

import json
import logging
import os
from typing import Any
from urllib.parse import unquote_plus

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Reuse clients across invocations to avoid recreating them for every request.
S3_CLIENT = boto3.client("s3")
TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def publish_sns_notification(subject: str, message: str) -> None:
    """Publish a notification to the configured SNS topic."""
    sns_client = boto3.client("sns")
    try:
        response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Subject=subject,
            Message=json.dumps(message, indent=2),
            MessageAttributes={
                "message_for": {
                    "DataType": "String",
                    "StringValue": "email",
                },
                "message_type": {
                    "DataType": "String",
                    "StringValue": "notification",
                },
                "env": {
                    "DataType": "String",
                    "StringValue": "dev",
                }
            }
        )
        LOGGER.info("SNS notification published: %s", response)
    except Exception as e:
        LOGGER.error("Failed to publish SNS notification: %s", str(e))
        raise   
    
def lambda_handler(event: dict[str, Any], context: Any) -> None:
    """Lambda function to process S3 create events and publish status to SNS."""
    LOGGER.info("Received event: %s", json.dumps(event))

    # Extract bucket name and object key from the event
    try:
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        object_key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
        event_name = event["Records"][0]["eventName"]
        event_time = event["Records"][0]["eventTime"]

        LOGGER.info(
            "Processing S3 event: bucket=%s, key=%s, event=%s, time=%s",
            bucket_name,
            object_key,
            event_name,
            event_time,
        )


        # Publish success notification to SNS
        publish_sns_notification(
            subject="S3 Event Processed Successfully",
            message=f"Successfully processed S3 event for bucket '{bucket_name}' and key '{object_key}'.",
        )
    except Exception as e:
        LOGGER.error("Error processing S3 event: %s", str(e))
        # Publish failure notification to SNS
        publish_sns_notification(
            subject="S3 Event Processing Failed",
            message=f"Failed to process S3 event. Error: {str(e)}",
        )
        raise  # Re-raise the exception to indicate failure
    