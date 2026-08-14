# ==========================================================
# Standard Python libraries
# ==========================================================

import logging  # Used to print structured logs instead of print() statements.
import random   # Used to generate random customers, products, and quantities.
import time     # Used to generate event timestamps and simulate delay.
import uuid     # Used to generate globally unique IDs for orders and events.

# ==========================================================
# Kafka Producer
# ==========================================================
from confluent_kafka import Producer

# ==========================================================
# Schema Registry
# ==========================================================

# SchemaRegistryClient connects to Confluent Schema Registry.
# topic_subject_name_strategy tells AvroSerializer to use:
#   <topic>-key
#   <topic>-value
# as subject names.

from confluent_kafka.schema_registry import (
    SchemaRegistryClient, 
    topic_subject_name_strategy
)

# ==========================================================
# Avro Serializer
# ==========================================================
# AvroSerializer converts Python dictionaries into Avro binary
# using schemas stored in Schema Registry.
from confluent_kafka.schema_registry.avro import AvroSerializer

# ==========================================================
# Serialization Context
# ==========================================================
# SerializationContext tells the serializer:
# - Which topic this message belongs to
# - Whether it is serializing the KEY or VALUE
from confluent_kafka.serialization import MessageField, SerializationContext

# ==========================================================
# Logger
# ==========================================================
# Configure application logging.
# Every log will contain:
# Time -> Log Level -> Message
#
# Example:
# 2026-07-29 18:30:15 INFO Producer Started
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Create a logger for this Python module.
LOGGER = logging.getLogger(__name__)



# ==========================================================
# Kafka Cluster Connection Details
# ==========================================================
# These credentials allow this producer to authenticate
# with the Confluent Kafka Cluster.
BOOTSTRAP_SERVERS = 'pkc-oxqxx9.us-east-1.aws.confluent.cloud:9092'
KAFKA_API_KEY = 'S6IZH5UKUIH3L7IR'
KAFKA_API_SECRET = 'cfltAAeNJY1Wd/s3q1WZS++aJy/i/hKNP7eAJMIQU+dFAOd4RlTkHn7DKUbGXXQg'

# ==========================================================
# Kafka Schema Registry Connection Details
# ==========================================================
# These credentials allow this producer to authenticate
# with the Confluent Kafka Schema Registry.
SCHEMA_REGISTRY_URL = 'https://psrc-zj7q8pp.us-east1.gcp.confluent.cloud'
SCHEMA_REGISTRY_SCHEMA_KEY = '3SBMJEZJ7VIOFD65'
SCHEMA_REGISTRY_SCHEMA_SECRET = 'cfltO7LZIcPpFNumYlCWWpsOKSthQZxjeOEpvJIvSRA1QAEBNRE9/QP5n5Pgovbw'

# ==========================================================
# Kafka Topic
# ==========================================================
# Kafka topic where all order events will be published.
TOPIC_NAME = 'ecomm_orders_topic'

# By default, Schema Registry stores schemas under:
#
# ecomm_orders_topic-key
# ecomm_orders_topic-value
#
# These are called Subjects.
KEY_SCHEMA_SUBJECT = f'{TOPIC_NAME}-key'
VALUE_SCHEMA_SUBJECT = f'{TOPIC_NAME}-value'

# ==========================================================
# Counters
# ==========================================================
# Number of dummy events to publish.
NUMBER_OF_EVENT = 20

# Runtime counters used for validation
DELIVERED_MESSAGE_COUNT = 0
FAILED_MESSAGE_COUNT = 0

# ==========================================================
# Dummy Date
# ==========================================================
# Fake customer master data.
# Used only for generating sample events.
CUSTOMERS = [
    {"customer_id": "customer-1001", "shipping_country": "IN"},
    {"customer_id": "customer-1002", "shipping_country": "IN"},
    {"customer_id": "customer-1003", "shipping_country": "SG"},
    {"customer_id": "customer-1004", "shipping_country": "AE"},
]

# Product master.
#
# Prices are stored in minor currency units (paise)
# instead of decimal rupees.
#
# Example:
#
# 249900 = ₹2499.00
#

PRODUCT_CATALOG = [
    {"sku": "LAPTOP-STAND-001", "unit_price_minor": 249900},
    {"sku": "WIRELESS-MOUSE-002", "unit_price_minor": 129900},
    {"sku": "USB-C-HUB-003", "unit_price_minor": 349900},
    {"sku": "MECHANICAL-KEYBOARD-004", "unit_price_minor": 599900},
    {"sku": "NOISE-CANCELLING-HEADSET-005", "unit_price_minor": 799900},
]

# ==========================================================
# generate_order_event() 
# ==========================================================
# Generate Order Event -> Follows this syntax in the industry
def generate_order_event():
    # Randomly pick one customer to simulate
    # a real checkout request.
    customer = random.choice(CUSTOMERS)
    
    # Select between 1 and 3 different products
    # for this order.
    selected_products = random.sample(PRODUCT_CATALOG, k=random.randint(1,3))
    
    # This list will contain all products
    # purchased in the current order.
    order_items = []
    
    for product in selected_products:
        # Customer buys between 1 and 3 units
        # of the selected product.
        quantity = random.randint(1, 3)
        
        # Add one line item into the order.
        order_items.append(
            {
                "sku": product["sku"],
                "quantity": quantity,
                "unit_price_minor": product["unit_price_minor"]
            }
        )
    
    # Calculate total order amount by summing:
    #
    # quantity × unit price
    #
    # for every purchased item.
    total_amount_minor = sum(item["quantity"] * item["unit_price_minor"] for item in order_items)
    
    # Build the final business event.
    #
    # This dictionary must exactly match
    # the Avro Value Schema stored in
    # Schema Registry.
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "ORDER_CREATED",
        "event_version": 1,
        "occurred_at": int(time.time() * 1000),
        "order_id": f"order-{uuid.uuid4()}",
        "customer_id": customer["customer_id"],
        "order_status": "CREATED",
        "currency": "INR",
        "total_amount_minor": total_amount_minor,
        "items": order_items,
        "shipping_country": customer["shipping_country"],
        "metadata": {
            "source": "checkout-service",
            "sales_channel": random.choice(["web", "mobile_app"]),
            "trace_id": uuid.uuid4().hex
        }
    }

# ==========================================================
# delivery_report()
# ==========================================================
# Callback executed automatically by Kafka
# after each message is acknowledged
# or fails permanently.
def delivery_report(error, message):
    global FAILED_MESSAGE_COUNT, DELIVERED_MESSAGE_COUNT
    
    if error is not None:
        # Increase failed message count
        # so main() can stop the application.
        FAILED_MESSAGE_COUNT += 1
        LOGGER.error("Message delivery failed: %s", error)
        return

    # Increase successful delivery count.
    DELIVERED_MESSAGE_COUNT += 1
    
    LOGGER.info(
        "Message delivered to topic=%s partition=%s offset=%s",
        message.topic(),
        message.partition(),
        message.offset()
    )
    
# ==========================================================
# main()
# ==========================================================
def main() :
    # ==========================================================
    # STEP 1
    # Create Schema Registry Client
    #
    # Purpose:
    # Connect this application to Schema Registry
    # so schemas can be fetched before serialization.
    # ==========================================================
    schema_registry_client = SchemaRegistryClient(
        {
            "url": SCHEMA_REGISTRY_URL,
            "basic.auth.user.info": f"{SCHEMA_REGISTRY_SCHEMA_KEY}:{SCHEMA_REGISTRY_SCHEMA_SECRET}"
        }
    )
    
    # ==========================================================
    # STEP 2
    # Fetch Latest Key and Value Schemas
    #
    # Producer always serializes using the latest
    # approved schema stored in Schema Registry.
    # ==========================================================
    latest_key_schema = schema_registry_client.get_latest_version(KEY_SCHEMA_SUBJECT)
    latest_value_schema = schema_registry_client.get_latest_version(VALUE_SCHEMA_SUBJECT)
    
    # log the info of key schema version and global schema ID found in schema Registry
    LOGGER.info(
        "Using key subject=%s version=%s schema_id=%s",
        KEY_SCHEMA_SUBJECT,
        latest_key_schema.version,
        latest_key_schema.schema_id
    )
    
    # log the info of value schema version and global schema ID found in schema Registry
    LOGGER.info(
        "Using value subject=%s version=%s schema_id=%s",
        VALUE_SCHEMA_SUBJECT,
        latest_value_schema.version,
        latest_value_schema.schema_id
    )
    
    # ==========================================================
    # STEP 3
    # Create Avro Serializers
    #
    # Serializer converts Python dictionaries
    # into compact Avro binary using the
    # latest schema from Schema Registry.
    # ==========================================================
    key_avro_serializer = AvroSerializer(
        schema_registry_client = schema_registry_client,
        schema_str = None, #  means the key schema is obtained only from Schema Registry
        conf = {
            "auto.register.schemas": False,
            "use.latest.version": True,
            "subject.name.strategy": topic_subject_name_strategy 
        }
    )
    value_avro_serializer = AvroSerializer(
        schema_registry_client = schema_registry_client,
        schema_str = None, #  means the key schema is obtained only from Schema Registry
        conf = {
            "auto.register.schemas": False,
            "use.latest.version": True,
            "subject.name.strategy": topic_subject_name_strategy 
        }
    )
    
    # ==========================================================
    # STEP 4
    # Create Kafka Producer
    #
    # Responsible for:
    #
    # - Connecting to Kafka
    # - Sending records
    # - Retrying transient failures
    # - Waiting for acknowledgements
    # ==========================================================
    producer = Producer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "acks": "all",
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": KAFKA_API_KEY,
        "sasl.password": KAFKA_API_SECRET,
        "enable.idempotence": True
    })
    
    
    # ==========================================================
    # STEP 5
    #
    # Repeat for every order:
    #
    # Generate Event
    # ↓
    # Build Kafka Key
    # ↓
    # Serialize Key
    # ↓
    # Serialize Value
    # ↓
    # Produce Message
    # ↓
    # Wait for Ack
    # ==========================================================        
    for event_number in range(1, NUMBER_OF_EVENT + 1):
        # 6.1 Generate Event
        order_event = generate_order_event()
       
        order_id = order_event["order_id"]
        customer_id = order_event["customer_id"]
        LOGGER.info(
            "Publishing event=%s/%s order_id=%s customer_id=%s total_amount_minor=%s",
            event_number,
            NUMBER_OF_EVENT,
            order_id,
            customer_id,
            order_event["total_amount_minor"]
        )
        
        # 6.2 Build kafka key 
        order_key = {"order_id": order_id}
        
        # ==========================================================
        # Serialization
        # ==========================================================
        # Convert Python dictionary into
        # Avro binary using the latest
        # Key Schema.
        serialized_key = key_avro_serializer(
            order_key,
            SerializationContext(TOPIC_NAME, MessageField.KEY)
        )
        serialized_value = value_avro_serializer(
            order_event, 
            SerializationContext(TOPIC_NAME, MessageField.VALUE)
        )
        
        # ==========================================================
        # Produce
        # ==========================================================
        # Add the serialized message
        # to Kafka Producer's internal buffer.
        #
        # Message is not guaranteed to be
        # in Kafka until flush() completes.
        producer.produce(
            # Destination kafka topic
            topic = TOPIC_NAME,
            key=serialized_key,
            value=serialized_value,
            
            # Call back function => Kafka will call this function after delivery succeeds or fails
            on_delivery=delivery_report
        )
        
        # ==========================================================
        # Flush
        # ==========================================================
        # Force the producer to send
        # all buffered messages immediately
        # and wait for Kafka acknowledgement.
        messages_still_queued = producer.flush(timeout=10)

        # ==========================================================
        # Validation
        # ==========================================================
        # Final safety check.
        #
        # Verify every generated event
        # was acknowledged by Kafka.
        if messages_still_queued > 0:
            raise RuntimeError(f"{messages_still_queued} messages were not delivered")
        
        # stop immediately if the delivery callback reported a permanent kafka error
        if FAILED_MESSAGE_COUNT > 0:
            raise RuntimeError("Kafka Failed to deliver a message")
        
        time.sleep(3)
    
    if DELIVERED_MESSAGE_COUNT != NUMBER_OF_EVENT:
        raise RuntimeError(
            f"Expected {NUMBER_OF_EVENT} acknowledgements by recieved "
            f"{DELIVERED_MESSAGE_COUNT}"
        )
        
    LOGGER.info("Producer finished successfully delivered=%s", DELIVERED_MESSAGE_COUNT)
    
    
# Run main() only when this file is executed directly
if __name__ == "__main__":
    try:
        main()
    except Exception:
        LOGGER.exception("Producer stopper because of an error")