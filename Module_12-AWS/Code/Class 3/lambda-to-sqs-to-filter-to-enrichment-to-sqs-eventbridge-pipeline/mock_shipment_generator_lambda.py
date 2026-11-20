"""
Lambda 1: Mock Shipment Tracking Event Generator
-------------------------------------------------
Generates realistic logistics shipment tracking events and publishes them to SQS.
Simulates a fleet management system pushing delivery status updates.

Environment Variables:
    SQS_QUEUE_URL: URL of the target SQS queue
"""

import json
import boto3
import random
import uuid
import os
from datetime import datetime, timezone, timedelta

sqs = boto3.client("sqs")

# --------------- Realistic Mock Data Pools ---------------

WAREHOUSES = [
    {"warehouse_id": "WH-BLR-01", "warehouse_city": "Bangalore"},
    {"warehouse_id": "WH-MUM-01", "warehouse_city": "Mumbai"},
    {"warehouse_id": "WH-DEL-01", "warehouse_city": "Delhi"},
    {"warehouse_id": "WH-HYD-01", "warehouse_city": "Hyderabad"},
    {"warehouse_id": "WH-CHN-01", "warehouse_city": "Chennai"},
]

DESTINATIONS = [
    "Pune", "Jaipur", "Kolkata", "Lucknow", "Ahmedabad",
    "Nagpur", "Indore", "Bhopal", "Coimbatore", "Kochi",
]

DRIVERS = [
    {"driver_id": "DRV-101", "driver_name": "Raju Yadav"},
    {"driver_id": "DRV-102", "driver_name": "Suresh Patil"},
    {"driver_id": "DRV-103", "driver_name": "Manoj Kumar"},
    {"driver_id": "DRV-104", "driver_name": "Deepak Joshi"},
    {"driver_id": "DRV-105", "driver_name": "Anil Mehra"},
]

VEHICLE_TYPES = ["Truck-14ft", "Truck-20ft", "Mini-Van", "Container-40ft"]

SHIPMENT_STATUSES = [
    "PICKED_UP",
    "IN_TRANSIT",
    "OUT_FOR_DELIVERY",
    "DELIVERED",
    "FAILED",
    "RETURNED",
]

SHIPMENT_PRIORITIES = ["STANDARD", "EXPRESS", "SAME_DAY"]

PACKAGE_TYPES = [
    {"type": "Electronics", "avg_weight_kg": 5.0},
    {"type": "Furniture", "avg_weight_kg": 45.0},
    {"type": "Pharmaceuticals", "avg_weight_kg": 2.0},
    {"type": "FMCG", "avg_weight_kg": 12.0},
    {"type": "Auto Parts", "avg_weight_kg": 25.0},
    {"type": "Textiles", "avg_weight_kg": 8.0},
]

FAILURE_REASONS = [
    "Customer unavailable",
    "Incorrect address",
    "Refused by customer",
    "Damaged in transit",
    "Vehicle breakdown",
]

# --------------------------------------------------------



def generate_shipment_event():
    """Generate a single realistic shipment tracking event."""
    warehouse = random.choice(WAREHOUSES)
    driver = random.choice(DRIVERS)
    package = random.choice(PACKAGE_TYPES)
    status = random.choices(
        SHIPMENT_STATUSES,
        weights=[15, 25, 15, 25, 15, 5],
        k=1,
    )[0]
    priority = random.choices(
        SHIPMENT_PRIORITIES,
        weights=[50, 35, 15],
        k=1,
    )[0]

    # Simulate dispatch and expected delivery times
    dispatched_at = datetime.now(timezone.utc) - timedelta(
        hours=random.randint(6, 72)
    )
    sla_hours = {"STANDARD": 48, "EXPRESS": 24, "SAME_DAY": 12}[priority]
    expected_delivery = dispatched_at + timedelta(hours=sla_hours)

    weight_kg = round(
        package["avg_weight_kg"] * random.uniform(0.5, 2.0), 2
    )

    event = {
        "shipment_id": f"SHP-{uuid.uuid4().hex[:8].upper()}",
        "tracking_number": f"TRK{random.randint(1000000000, 9999999999)}",
        "origin_warehouse": warehouse["warehouse_id"],
        "origin_city": warehouse["warehouse_city"],
        "destination_city": random.choice(DESTINATIONS),
        "driver": {
            "driver_id": driver["driver_id"],
            "driver_name": driver["driver_name"],
        },
        "vehicle_type": random.choice(VEHICLE_TYPES),
        "package": {
            "type": package["type"],
            "weight_kg": weight_kg,
            "quantity": random.randint(1, 20),
        },
        "shipment_status": status,
        "shipment_priority": priority,
        "dispatched_at": dispatched_at.isoformat(),
        "expected_delivery_at": expected_delivery.isoformat(),
        "status_updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Add failure reason only for FAILED shipments
    if status == "FAILED":
        event["failure_reason"] = random.choice(FAILURE_REASONS)

    return event


def lambda_handler(event, context):
    """
    Generate mock shipment events and publish each to SQS.

    Invoke with: {"shipment_count": 10}   (default: 10 events)
    """
    queue_url = os.environ["SQS_QUEUE_URL"]
    shipment_count = event.get("shipment_count", 10)

    published = []

    for _ in range(shipment_count):
        shipment = generate_shipment_event()

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(shipment),
        )
        published.append(shipment)
        print(
            f"Published: {shipment['shipment_id']} | "
            f"{shipment['shipment_status']} | "
            f"{shipment['shipment_priority']} | "
            f"{shipment['origin_city']} -> {shipment['destination_city']} | "
            f"{shipment['package']['type']} ({shipment['package']['weight_kg']}kg)"
        )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Successfully published {shipment_count} shipment events to SQS",
                "shipments": published,
            },
            default=str,
        ),
    }