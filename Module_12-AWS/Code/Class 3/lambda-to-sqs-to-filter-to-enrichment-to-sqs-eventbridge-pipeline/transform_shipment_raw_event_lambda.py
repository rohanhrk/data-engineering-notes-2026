"""
Lambda 2: Shipment Event Transformer (EventBridge Pipe Enrichment Stage)
------------------------------------------------------------------------
Receives filtered shipment events from EventBridge Pipe and enriches them
with SLA compliance metrics before they land in the S3 destination.

This Lambda is configured as the "Enrichment" step in EventBridge Pipe.
It receives a LIST of events (batch) and must return a LIST of transformed events.
"""

import json
from datetime import datetime


def calculate_sla_metrics(shipment):
    """Calculate delivery SLA compliance metrics."""
    dispatched_at = datetime.fromisoformat(shipment["dispatched_at"])
    status_updated_at = datetime.fromisoformat(shipment["status_updated_at"])
    expected_delivery_at = datetime.fromisoformat(shipment["expected_delivery_at"])

    # Actual delivery duration in hours
    actual_duration_hours = round(
        (status_updated_at - dispatched_at).total_seconds() / 3600, 2
    )

    # SLA window in hours
    sla_window_hours = round(
        (expected_delivery_at - dispatched_at).total_seconds() / 3600, 2
    )

    # SLA compliance check
    sla_breached = status_updated_at > expected_delivery_at
    breach_hours = (
        round(
            (status_updated_at - expected_delivery_at).total_seconds() / 3600, 2
        )
        if sla_breached
        else 0.0
    )

    return {
        "actual_duration_hours": actual_duration_hours,
        "sla_window_hours": sla_window_hours,
        "sla_breached": sla_breached,
        "breach_hours": breach_hours,
    }


def lambda_handler(event, context):
    """
    Transform and enrich shipment events with SLA metrics.

    EventBridge Pipe sends a batch (list) of events.
    Each element has the SQS message structure with 'body' as a JSON string.
    Must return a list of the same length.
    """
    transformed_events = []

    for record in event:
        # Parse the SQS message body
        shipment = json.loads(record["body"]) if isinstance(record.get("body"), str) else record.get("body", record)

        # Calculate SLA metrics
        sla_metrics = calculate_sla_metrics(shipment)

        # Build enriched event for S3 destination
        enriched = {
            "shipment_id": shipment["shipment_id"],
            "tracking_number": shipment["tracking_number"],
            "route": {
                "origin_warehouse": shipment["origin_warehouse"],
                "origin_city": shipment["origin_city"],
                "destination_city": shipment["destination_city"],
            },
            "driver_id": shipment["driver"]["driver_id"],
            "driver_name": shipment["driver"]["driver_name"],
            "vehicle_type": shipment["vehicle_type"],
            "package_type": shipment["package"]["type"],
            "package_weight_kg": shipment["package"]["weight_kg"],
            "package_quantity": shipment["package"]["quantity"],
            "shipment_status": shipment["shipment_status"],
            "shipment_priority": shipment["shipment_priority"],
            "dispatched_at": shipment["dispatched_at"],
            "expected_delivery_at": shipment["expected_delivery_at"],
            "status_updated_at": shipment["status_updated_at"],
            "sla_metrics": sla_metrics,
        }

        # Add failure reason if shipment failed
        if shipment.get("failure_reason"):
            enriched["failure_reason"] = shipment["failure_reason"]

        transformed_events.append(enriched)

        status_label = "SLA BREACHED" if sla_metrics["sla_breached"] else "WITHIN SLA"
        print(
            f"Enriched: {shipment['shipment_id']} | "
            f"{shipment['shipment_status']} | "
            f"{shipment['shipment_priority']} | "
            f"Duration: {sla_metrics['actual_duration_hours']}h | "
            f"{status_label}"
        )

    return transformed_events