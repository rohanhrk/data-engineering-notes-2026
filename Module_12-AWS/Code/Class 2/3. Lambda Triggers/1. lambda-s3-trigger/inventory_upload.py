"""Read inventory CSV uploads. Handler: inventory_upload.handle_inventory_upload."""

import json
import logging
from contextlib import closing
from urllib.parse import unquote_plus

import boto3
import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handle_inventory_upload(event, context):
    """Process S3 ObjectCreated notifications for incoming/*.csv objects."""
    # S3 can send this special message when notifications are configured.
    if event.get("Event") == "s3:TestEvent":
        logger.info("S3 notification configuration test received")
        return {"processed_files": 0, "results": []}