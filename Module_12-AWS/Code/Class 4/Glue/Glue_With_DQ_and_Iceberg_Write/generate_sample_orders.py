"""Generate deterministic, crawler-ready order data for the Glue DQ demo."""

import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


OUTPUT_FILE = Path(__file__).parent / "data" / "customer_orders.csv"
RECORD_COUNT = 1200
RANDOM_SEED = 20261003


CUSTOMERS = [
    ("Aarav Sharma", "STANDARD"),
    ("Aadhya Patel", "PREMIUM"),
    ("Arjun Verma", "STANDARD"),
    ("Ananya Reddy", "PREMIUM"),
    ("Kabir Singh", "STANDARD"),
    ("Ira Mehta", "NEW"),
    ("Myra Khan", "PREMIUM"),
    ("Vihaan Mishra", "STANDARD"),
    ("Sara Agarwal", "NEW"),
    ("Reyansh Nair", "STANDARD"),
]

CITIES = [
    ("Mumbai", "Maharashtra", "400001"),
    ("Pune", "Maharashtra", "411001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Delhi", "Delhi", "110001"),
    ("Kolkata", "West Bengal", "700001"),
    ("Ahmedabad", "Gujarat", "380001"),
    ("Jaipur", "Rajasthan", "302001"),
    ("Lucknow", "Uttar Pradesh", "226001"),
]

PRODUCTS = [
    ("P1001", "Wireless Mouse", "Electronics", Decimal("799.00")),
    ("P1002", "Bluetooth Speaker", "Electronics", Decimal("2499.00")),
    ("P1003", "USB-C Hub", "Electronics", Decimal("1899.00")),
    ("P2001", "Data Engineering Handbook", "Books", Decimal("1299.00")),
    ("P2002", "SQL Patterns Guide", "Books", Decimal("899.00")),
    ("P3001", "Desk Lamp", "Home", Decimal("1499.00")),
    ("P3002", "Ergonomic Chair", "Home", Decimal("12499.00")),
    ("P4001", "Cotton Jacket", "Fashion", Decimal("2999.00")),
    ("P4002", "Running Shoes", "Fashion", Decimal("3499.00")),
    ("P5001", "Protein Shaker", "Fitness", Decimal("599.00")),
    ("P5002", "Resistance Bands", "Fitness", Decimal("999.00")),
    ("P6001", "Yoga Mat", "Sports", Decimal("799.00")),
]

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "COD",
    "Wallet",
]
ORDER_STATUSES = [
    "Placed",
    "Processing",
    "Paid",
    "Shipped",
    "Delivered",
    "Cancelled",
    "Returned",
]
SHIPPING_MODES = ["Standard", "Express", "Same Day"]

FIELDNAMES = [
    "order_id",
    "customer_id",
    "customer_name",
    "customer_email",
    "customer_segment",
    "city",
    "state",
    "country",
    "postal_code",
    "order_timestamp",
    "product_id",
    "product_name",
    "product_category",
    "quantity",
    "unit_price",
    "discount_amount",
    "tax_amount",
    "shipping_amount",
    "reported_total_amount",
    "currency",
    "payment_method",
    "order_status",
    "shipping_mode",
    "delivery_date",
    "source_system",
]


def money(value):
    """Return a two-decimal string using financial half-up rounding."""

    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def build_row(row_number, random_generator):
    customer_number = random_generator.randint(1, 250)
    customer_name, customer_segment = random_generator.choice(CUSTOMERS)
    email_name = customer_name.lower().replace(" ", ".")
    city, state, postal_code = random_generator.choice(CITIES)
    product_id, product_name, product_category, unit_price = random_generator.choice(
        PRODUCTS
    )
    quantity = random_generator.randint(1, 5)
    discount_amount = Decimal(
        random_generator.choice(["0.00", "50.00", "100.00", "150.00", "250.00"])
    )
    shipping_amount = Decimal(
        random_generator.choice(["0.00", "40.00", "75.00", "120.00"])
    )
    taxable_amount = (unit_price * quantity) - discount_amount
    tax_amount = (taxable_amount * Decimal("0.18")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total_amount = taxable_amount + tax_amount + shipping_amount
    order_status = random_generator.choice(ORDER_STATUSES)
    order_timestamp = datetime(2026, 9, 1) + timedelta(
        minutes=random_generator.randint(0, 60 * 24 * 45)
    )

    delivery_date = ""
    if order_status in {"Shipped", "Delivered", "Returned"}:
        delivery_date = (
            order_timestamp.date() + timedelta(days=random_generator.randint(1, 8))
        ).isoformat()

    row = {
        "order_id": f"ORD{row_number:07d}",
        "customer_id": f"CUST{customer_number:05d}",
        "customer_name": customer_name,
        "customer_email": f"{email_name}{customer_number}@example.com",
        "customer_segment": customer_segment,
        "city": city,
        "state": state,
        "country": "India",
        "postal_code": postal_code,
        "order_timestamp": order_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "product_id": product_id,
        "product_name": product_name,
        "product_category": product_category,
        "quantity": quantity,
        "unit_price": money(unit_price),
        "discount_amount": money(discount_amount),
        "tax_amount": money(tax_amount),
        "shipping_amount": money(shipping_amount),
        "reported_total_amount": money(total_amount),
        "currency": "INR",
        "payment_method": random_generator.choice(PAYMENT_METHODS),
        "order_status": order_status,
        "shipping_mode": random_generator.choice(SHIPPING_MODES),
        "delivery_date": delivery_date,
        "source_system": random_generator.choice(["WEB", "MOBILE", "STORE"]),
    }

    # Deliberate quality defects make the Data Quality report useful in a demo.
    defects = {
        37: ("customer_email", ""),
        91: ("quantity", 0),
        144: ("unit_price", "-10.00"),
        233: ("discount_amount", "-25.00"),
        318: ("currency", "USD"),
        407: ("payment_method", "Crypto"),
        512: ("order_status", "Unknown"),
        621: ("order_timestamp", "not-a-timestamp"),
        736: ("product_id", ""),
        844: ("country", "Nepal"),
        963: ("tax_amount", "-5.00"),
        1088: ("shipping_amount", "-1.00"),
    }

    if row_number in defects:
        field_name, bad_value = defects[row_number]
        row[field_name] = bad_value

    # Both occurrences of this order ID should fail the IsUnique rule.
    if row_number == 1150:
        row["order_id"] = "ORD0001149"

    return row


def main():
    random_generator = random.Random(RANDOM_SEED)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(
            build_row(row_number, random_generator)
            for row_number in range(1, RECORD_COUNT + 1)
        )

    print(f"Wrote {RECORD_COUNT} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
