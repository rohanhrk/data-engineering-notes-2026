# ==========================================================
# Standard Python Libraries
# ==========================================================

import logging     # Print structured logs instead of using print().
import json        # Pretty-print consumed Kafka messages in JSON format.
import time        # Add delay between processing messages.

# ==========================================================
# Schema Registry Components
# ==========================================================

# Connects to Confluent Schema Registry.
# Used to fetch the latest Avro schemas (data contracts).
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    topic_subject_name_strategy
)

# Converts Avro binary received from Kafka
# back into Python dictionaries.
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Kafka Consumer used to consume messages.
# KafkaException is raised for broker/message errors.
from confluent_kafka import Consumer, KafkaException

# SerializationContext tells the deserializer:
# - Which topic the message belongs to.
# - Whether it is deserializing KEY or VALUE.
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext
)


# ==========================================================
# Logger
# ==========================================================
# Configure application logging.
#
# Example:
#
# 2026-07-29 14:20:55 INFO Consumer Started

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Create one logger for this Python module.
LOGGER = logging.getLogger(__name__)

# ==========================================================
# Kafka Cluster Credentials
#
# Used by the consumer to authenticate
# with the Kafka Cluster.
# ==========================================================
BOOTSTRAP_SERVERS = 'pkc-oxqxx9.us-east-1.aws.confluent.cloud:9092'
KAFKA_API_KEY = 'S6IZH5UKUIH3L7IR'
KAFKA_API_SECRET = 'cfltAAeNJY1Wd/s3q1WZS++aJy/i/hKNP7eAJMIQU+dFAOd4RlTkHn7DKUbGXXQg'

# ==========================================================
# Schema Registry Credentials
#
# Used to download Avro schemas
# before deserializing Kafka messages.
# ==========================================================
SCHEMA_REGISTRY_URL = 'https://psrc-zj7q8pp.us-east1.gcp.confluent.cloud'
SCHEMA_REGISTRY_SCHEMA_KEY = '3SBMJEZJ7VIOFD65'
SCHEMA_REGISTRY_SCHEMA_SECRET = 'cfltO7LZIcPpFNumYlCWWpsOKSthQZxjeOEpvJIvSRA1QAEBNRE9/QP5n5Pgovbw'

# ==========================================================
# Kafka Topic Information
#
# Topic:
# ecomm_orders_topic
#
# Schema Registry Subjects:
#
# ecomm_orders_topic-key
# ecomm_orders_topic-value
# ==========================================================
TOPIC_NAME = 'ecomm_orders_topic'
KEY_SCHEMA_SUBJECT = f'{TOPIC_NAME}-key'
VALUE_SCHEMA_SUBJECT = f'{TOPIC_NAME}-value'

def main() :
    # ==========================================================
    # STEP 1
    #
    # Create Schema Registry Client
    #
    # Purpose:
    # Connect to Schema Registry so the consumer
    # can fetch Avro schemas before deserialization.
    # ==========================================================
    schema_registry_client = SchemaRegistryClient(
        {
            "url": SCHEMA_REGISTRY_URL,
            "basic.auth.user.info": f"{SCHEMA_REGISTRY_SCHEMA_KEY}:{SCHEMA_REGISTRY_SCHEMA_SECRET}"
        }
    )
    
    # ==========================================================
    # STEP 2
    #
    # Fetch the latest approved Key and Value schemas.
    #
    # These schemas are required by AvroDeserializer
    # to convert binary Kafka messages back into
    # Python dictionaries.
    # ==========================================================
    latest_key_schema = schema_registry_client.get_latest_version(KEY_SCHEMA_SUBJECT)
    latest_value_schema = schema_registry_client.get_latest_version(VALUE_SCHEMA_SUBJECT)
    
    # Log the schema version and schema ID being used.
    #
    # Useful for debugging schema evolution.
    LOGGER.info(
        "Using key subject=%s version=%s schema_id=%s",
        KEY_SCHEMA_SUBJECT,
        latest_key_schema.version,
        latest_key_schema.schema_id
    )
    LOGGER.info(
        "Using value subject=%s version=%s schema_id=%s",
        VALUE_SCHEMA_SUBJECT,
        latest_value_schema.version,
        latest_value_schema.schema_id
    )
    
    # ==========================================================
    # STEP 3
    #
    # Create Key Avro Deserializer.
    #
    # Responsibilities:
    #
    # Binary Kafka Key
    #       ↓
    # Latest Key Schema
    #       ↓
    # Python Dictionary
    # ==========================================================
    key_avro_deserializer = AvroDeserializer(
        schema_registry_client = schema_registry_client,
        schema_str = None, #  means the key schema is obtained only from Schema Registry
        conf = {
            "use.latest.version": True,
            "subject.name.strategy": topic_subject_name_strategy
        }
    )
    
    # ==========================================================
    # STEP 4
    #
    # Create Value Avro Deserializer.
    #
    # Responsibilities:
    #
    # Binary Kafka Value
    #       ↓
    # Latest Value Schema
    #       ↓
    # Python Dictionary
    # ==========================================================
    value_avro_deserializer = AvroDeserializer(
        schema_registry_client = schema_registry_client,
        schema_str = None, #  means the key schema is obtained only from Schema Registry
        conf = {
            "use.latest.version": True,
            "subject.name.strategy": topic_subject_name_strategy
        }
    )
    
    # ==========================================================
    # STEP 5
    #
    # Create Kafka Consumer.
    #
    # Responsibilities:
    #
    # Connect to Kafka
    # Join Consumer Group
    # Read Messages
    # Track Offsets
    # Commit Offsets
    # ==========================================================
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS, # Kafka broker addresses
        "group.id": "G1", # Consumer group identifier
        "security.protocol": "SASL_SSL", # Connection protocol (SASL_SSL)
        "sasl.mechanism": "PLAIN", # Authentication mechanism (PLAIN)
        "sasl.username": KAFKA_API_KEY, # Kafka API Key
        "sasl.password": KAFKA_API_SECRET, # Kafka API Secret
        "auto.offset.reset": "earliest", # Where to start reading if no offset exists (earliest or latest)
        "enable.auto.commit": False, # Automatically commit offsets (True/False)
    })
    
    # Register this consumer
    # with the specified Kafka topic.
    #
    # Kafka automatically assigns
    # partitions belonging to this
    # consumer group.
    consumer.subscribe([TOPIC_NAME])
    
    LOGGER.info("Consumer started. Waiting for messages from topic=%s", TOPIC_NAME)
    
    # ==========================================================
    # STEP 6
    #
    # Infinite Poll Loop
    #
    # Repeat:
    #
    # Poll Message
    # ↓
    # Deserialize Key
    # ↓
    # Deserialize Value
    # ↓
    # Process Business Logic
    # ↓
    # Commit Offset
    # ==========================================================
    try:
        
        # ==========================================================
        # Kafka Consumer Flow
        #
        # Kafka Broker
        #       │
        #       ▼
        # Poll Message
        #       │
        #       ▼
        # Deserialize Key
        #       │
        #       ▼
        # Deserialize Value
        #       │
        #       ▼
        # Business Processing
        #       │
        #       ▼
        # Commit Offset
        #       │
        #       ▼
        # Poll Next Message
        # ==========================================================
        while True:
            # Poll Kafka for one message.
            #
            # Returns:
            #
            # None
            # → No message available.
            #
            # Kafka Message
            # → Message received.
            message = consumer.poll(timeout=1.0)
            
            # No message arrived during
            # this poll interval.
            #
            # Continue polling.
            if message is None:
                continue

            # Kafka returned an error.
            #
            # Raise exception so the application
            # can stop or retry appropriately.
            if message.error():
                raise KafkaException(message.error)
            
            # Build serialization context
            # required by AvroDeserializer.
            #
            # Context tells the deserializer:
            #
            # Topic Name
            # +
            # Message Field (KEY)
            key_context = SerializationContext(message.topic(), MessageField.KEY)
            
            # Convert binary Kafka Key
            # into a Python dictionary
            # using the latest Key Schema.
            order_key = key_avro_deserializer(message.key(), key_context)
            
            # Build serialization context
            # for the Kafka Value.
            value_context = SerializationContext(message.topic(), MessageField.VALUE)
            
            # Convert binary Kafka Value
            # into a Python dictionary
            # using the latest Value Schema.
            order_event = value_avro_deserializer(message.value(), value_context)
            
            order_id = order_key["order_id"]
            
            # Pretty-print the consumed event.
            #
            # Useful during development
            # to verify message contents.
            print(
                json.dumps(
                    {"key": order_key, "value": order_event},
                    indent=2,
                    default=str
                )
            )
            
            # Log processing information.
            #
            # Offset and partition help
            # identify exactly where
            # this message was read.
            LOGGER.info(
                "Processed order_id=%s partition=%s offset=%s",
                order_id,
                message.partition(),
                message.offset()
            )
            
            # ==========================================================
            # Commit Offset
            #
            # Tell Kafka:
            #
            # "This message has been processed successfully."
            #
            # Kafka stores the committed offset
            # so the consumer can resume
            # from the next message
            # after restart.
            # ==========================================================
            consumer.commit(message=message, asynchronous=False)
            
            LOGGER.info("Offset Committed synchronously")
            
            # Artificial delay.
            #
            # Used only for demonstration.
            #
            # Remove in production.
            time.sleep(3)
            
            print("------------------------------------------------------")
    
    except KeyboardInterrupt:
        LOGGER.info("Consumer stopped by user")
    
    except Exception:
        LOGGER.exception("consumer stopped because of an error")
        raise
    
    # Always close the consumer.
    #
    # Closing the consumer:
    #
    # ✔ Leaves the consumer group.
    # ✔ Commits pending state.
    # ✔ Releases network resources.
    finally:
        consumer.close()
        LOGGER.info("Consumer connection closed")
if __name__ == "__main__":
    try:
        main()
    except Exception:
        LOGGER.exception("Consumer stopper because of an error")