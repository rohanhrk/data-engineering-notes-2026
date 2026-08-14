# ==================================================================================================
# Imports
# ==================================================================================================

import json         # Used to convert Python dictionaries into JSON before sending to Kafka.
import random       # Used to generate random products, payment methods, customer tiers, etc.
import time         # Used to generate timestamps and introduce delays between events.


from confluent_kafka import Producer        # Kafka Producer used to publish events to Kafka topics.
from faker import Faker                     # Generates realistic fake customer information like names, emails, and UUIDs.

# ==================================================================================================
# Configuration
# ==================================================================================================
CHECKOUT_TOPIC = 'ecommerce_checkout_events'            # Kafka topic for checkout events.
PAYMENT_TOPIC = 'ecommerce_payment_events'              # Kafka topic for payment events.
NUMBER_OF_ORDERS = 10                                   # Total number of orders to simulate.
WAIT_BETWEEN_EVENTS_SECONDS = 3                         # Delay between publishing events to simulate real-time streaming.
KAFKA_CONFIG_FILE = 'client.properties'                 # Confluent Cloud connection properties file.

# ==================================================================================================
# PRODUCT CATELOG
# ==================================================================================================

# Sample product catalogue.
# Used to generate realistic e-commerce orders with
# different categories and prices.

PRODUCTS = [
    {"id": "prd_101", "name": "Classic Cotton Shirt", "category": "Apparel", "price": 899.0},
    {"id": "prd_102", "name": "Slim Fit Jeans", "category": "Apparel", "price": 1599.0},
    {"id": "prd_201", "name": "5G Smartphone", "category": "Electronics", "price": 24999.0},
    {"id": "prd_202", "name": "Wireless Headphones", "category": "Electronics", "price": 1999.0},
    {"id": "prd_203", "name": "Fitness Smartwatch", "category": "Electronics", "price": 6999.0},
    {"id": "prd_301", "name": "Running Shoes", "category": "Footwear", "price": 3499.0},
    {"id": "prd_401", "name": "Insulated Water Bottle", "category": "Home", "price": 499.0},
    {"id": "prd_402", "name": "Drip Coffee Maker", "category": "Home", "price": 4499.0},
    {"id": "prd_501", "name": "Premium Yoga Mat", "category": "Fitness", "price": 1499.0},
    {"id": "prd_601", "name": "SPF 50 Sunscreen", "category": "Beauty", "price": 599.0},
]

# ==================================================================================================
# CITIES
# ==================================================================================================

# Sample list of Indian cities used as shipping destinations.

INDIAN_CITIES = [
    "Bengaluru",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Jaipur",
    "Ahmedabad",
    "Kochi",
]

# ==================================================================================================
# FAKER
# ==================================================================================================

# Faker generates realistic Indian customer data
# such as names, emails, UUIDs, etc.

fake = Faker("en_IN")

# ==================================================================================================
# read_kafka_config()
# ==================================================================================================

# Reads Kafka configuration from client.properties.
# Returns a dictionary containing bootstrap server,
# security protocol, API key, API secret, etc.

def read_kafka_config() :
    """Read Confluent Cloud connection properties from client.properties."""
    config = {}
    
    with open(KAFKA_CONFIG_FILE, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            
            # Ignore blank lines and comments.
            if line and not line.startswith("#"):
                
                # Split each property into key and value
                # and store them in a dictionary.
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
                
    return config

# ==================================================================================================
# create_checkout_event()
# ==================================================================================================

# Creates a checkout event that represents
# a customer placing an order.

def create_checkout_event(order_number, event_time):
    product = random.choice(PRODUCTS)                               # Randomly select a product from the catalogue.
    quantity = random.randint(1, 3)                                 # Randomly decide how many units the customer buys.
    
    # Randomly assign a customer loyalty tier.
    # STANDARD customers are most common.
    customer_tier = random.choices(
        ["STANDARD", "SILVER", "GOLD"],
        weights=[65, 25, 10],
        k = 1
    )[0]
    
    # Determine discount based on customer tier.
    discount_rate = {
        "STANDARD": 0.00,
        "SILVER": 0.05,
        "GOLD": 0.10
    }[customer_tier]
    
    subtotal = product["price"] * quantity                          # Calculate subtotal before discount.
    discount_amount = round(subtotal * discount_rate, 2)            # Calculate total discount amount.
    
    # Construct the checkout event payload.
    # This event will be published to the checkout Kafka topic.
    checkout_event = {
        "event_id": f"chk_evt_{fake.uuid4()}",
        "event_ts": event_time,
        "order_id": f"ord_{int(time.time())}_{order_number:04d}",
        "customer_id": f"cust_{fake.random_number(digits=8, fix_len=True)}",
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "customer_tier": customer_tier,
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "quantity": quantity,
        "unit_price": product["price"],
        "discount_amount": discount_amount,
        "currency": "INR",
        "shipping_city": random.choice(INDIAN_CITIES),
        "sales_channel": random.choices(
            ["MOBILE_APP", "WEB"],
            weights=[65, 35],
            k=1
        )[0]
    }
    
    expected_amount = round(subtotal - discount_amount, 2)          # Calculate final amount after discount.This amount will be used while generating the payment event.
    return checkout_event, expected_amount


# ==================================================================================================
# create_payment_event()
# ==================================================================================================

# Creates a payment event for the checkout order.

def create_payment_event(checkout_event, expected_amount):
    
    # Most payments succeed.
    # Around 10% are intentionally marked as failed.

    payment_status = random.choices(
        ["AUTHORIZED", "FAILED"],
        weights=[90, 10],
        k=1,
    )[0]

    
    fraud_score = round(random.uniform(0.02, 0.40), 3)                                  # Generate a random fraud score.
    failure_reason = None
    
    if payment_status == "FAILED":                                                      # Assign a failure reason only for failed payments.
        failure_reason = random.choice(
            ["BANK_DECLINED", "INSUFFICIENT_FUNDS", "OTP_TIMEOUT"]
        )

    
    payment_timestamp = checkout_event["event_ts"] + random.randint(30, 180) * 1000     # Payment happens between 30 seconds and 3 minutes after checkout.

    payment_event = {                                                                   # Construct payment event payload.
        "event_id": f"pay_evt_{fake.uuid4()}",
        "event_ts": payment_timestamp,
        "order_id": checkout_event["order_id"],
        "payment_id": f"pay_{fake.random_number(digits=10, fix_len=True)}",
        "payment_method": random.choices(
            ["UPI", "CARD", "WALLET", "NET_BANKING"],
            weights=[50, 30, 12, 8],
            k=1,
        )[0],
        "payment_status": payment_status,
        "amount": expected_amount,
        "currency": "INR",
        "gateway": random.choice(["Razorpay", "Stripe", "Paytm"]),
        "fraud_score": fraud_score,
        "failure_reason": failure_reason,
    }
    
    return payment_event

# ==================================================================================================
# delivery_report()
# ==================================================================================================

# Callback executed after Kafka attempts to deliver a message.

def delivery_report(error, message) :
    if error:                                                   # Print an error if message delivery fails.
        print(f"Kafka delivery failed: {error}")

# ==================================================================================================
# publish()
# ==================================================================================================

# Publish an event to the specified Kafka topic.

def publish(producer, kafka_topic, event): 
    """Publish a plain JSON value without supplying a Kafka key."""
    # Convert Python dictionary into JSON bytes
    # before sending to Kafka.
    producer.produce(
        kafka_topic,
        value=json.dumps(event).encode("utf-8"),
        callback=delivery_report                                # Trigger delivery callback immediately.
    )
    
    producer.poll(0)                                            # Process any pending events right now, but don't wait (non-blocking)                                
    
    print(                                                      # Display which order was published.
        f"Published to {kafka_topic:<28}"
        f"order_id={event['order_id']}"
    )
    
# ==================================================================================================
# main()
# ==================================================================================================

def main():
    producer = Producer(read_kafka_config())                                                                    # Create Kafka producer using configuration.
    event_time = int(time.time() * 1000)                                                                        # Initial event timestamp in Epoch milliseconds.
    
    print("Starting checkout and payment producer.....")
    print("Press ctrl+c to stop.\n")
    
    # Start producing checkout and payment events.
    try:
        for order_number in range(1, NUMBER_OF_ORDERS + 1):
            checkout_event, expected_amount = create_checkout_event(order_number, event_time)                   # Generate checkout event.
            publish(producer, CHECKOUT_TOPIC, checkout_event)                                                   # Publish checkout event.
            
            time.sleep(WAIT_BETWEEN_EVENTS_SECONDS)                                                             # Wait before payment happens.
            
            payment_event = create_payment_event(checkout_event, expected_amount)                               # Generate corresponding payment event.
            publish(producer, PAYMENT_TOPIC, payment_event)                                                     # Publish payment event.
            
            event_time = payment_event["event_ts"] + 30_000                                                     # Advance event time so the next order occurs after this payment.
            
            print()
            time.sleep(WAIT_BETWEEN_EVENTS_SECONDS)                                                             # Simulate streaming by waiting before producing the next order.
    except KeyboardInterrupt:
        print("\nProducer stopped by user.")
    finally:
        producer.flush()                                                                                        # Ensure all pending Kafka messages are delivered before exiting.
        print("Producer finished.")

# ==================================================================================================
# Entry Point
# ==================================================================================================
if __name__ == "__main__":
    main()                                                                                                      # Start the producer program.