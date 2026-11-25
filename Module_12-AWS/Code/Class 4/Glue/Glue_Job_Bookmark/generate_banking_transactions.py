"""Generate deterministic CSV batches for the AWS Glue bookmark demonstration."""

import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path


OUTPUT_DIRECTORY = Path(__file__).parent / "data"
RANDOM_SEED = 20261004

BATCHES = [
    ("batch_1", "transactions_2026_10_01.csv", "2026-10-01", 75),
    ("batch_2", "transactions_2026_10_02.csv", "2026-10-02", 120),
    ("batch_3", "transactions_2026_10_03.csv", "2026-10-03", 55),
]

CUSTOMERS = [
    "Aarav Sharma",
    "Aadhya Patel",
    "Arjun Verma",
    "Ananya Reddy",
    "Kabir Singh",
    "Ira Mehta",
    "Myra Khan",
    "Vihaan Mishra",
    "Sara Agarwal",
    "Reyansh Nair",
]

LOCATIONS = [
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Bengaluru", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"),
    ("Delhi", "Delhi"),
    ("Kolkata", "West Bengal"),
    ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"),
]

TRANSACTION_DETAILS = [
    ("DEBIT", "Grocery", "Fresh Basket"),
    ("DEBIT", "Fuel", "City Fuel Station"),
    ("DEBIT", "Dining", "Spice Kitchen"),
    ("DEBIT", "Shopping", "Metro Retail"),
    ("DEBIT", "Utilities", "Power Utility"),
    ("CREDIT", "Salary", "Employer Payroll"),
    ("CREDIT", "Refund", "Merchant Refund"),
    ("TRANSFER", "Bank Transfer", "Account Transfer"),
]

CHANNELS = ["UPI", "Mobile Banking", "Internet Banking", "ATM", "POS"]
STATUSES = ["SUCCESS", "SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "PENDING"]

FIELDNAMES = [
    "transaction_id",
    "account_id",
    "customer_name",
    "transaction_timestamp",
    "transaction_type",
    "merchant_category",
    "merchant_name",
    "amount",
    "currency",
    "channel",
    "city",
    "state",
    "country",
    "transaction_status",
    "risk_score",
    "reference_number",
]


def create_batch(random_generator, batch_number, transaction_date, record_count):
    rows = []
    start_time = datetime.strptime(transaction_date, "%Y-%m-%d")

    for row_number in range(1, record_count + 1):
        global_number = (batch_number * 1000) + row_number
        customer_number = random_generator.randint(1, 200)
        transaction_type, category, merchant = random_generator.choice(
            TRANSACTION_DETAILS
        )
        city, state = random_generator.choice(LOCATIONS)
        amount = Decimal(random_generator.randint(1000, 250000)) / Decimal("100")

        rows.append(
            {
                "transaction_id": f"TXN{global_number:08d}",
                "account_id": f"ACC{customer_number:06d}",
                "customer_name": random_generator.choice(CUSTOMERS),
                "transaction_timestamp": (
                    start_time
                    + timedelta(seconds=random_generator.randint(0, 86399))
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "transaction_type": transaction_type,
                "merchant_category": category,
                "merchant_name": merchant,
                "amount": f"{amount:.2f}",
                "currency": "INR",
                "channel": random_generator.choice(CHANNELS),
                "city": city,
                "state": state,
                "country": "India",
                "transaction_status": random_generator.choice(STATUSES),
                "risk_score": random_generator.randint(1, 100),
                "reference_number": f"REF{global_number:010d}",
            }
        )

    return rows


def main():
    random_generator = random.Random(RANDOM_SEED)

    for batch_number, (folder, filename, transaction_date, record_count) in enumerate(
        BATCHES,
        start=1,
    ):
        output_file = OUTPUT_DIRECTORY / folder / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(
                create_batch(
                    random_generator,
                    batch_number,
                    transaction_date,
                    record_count,
                )
            )

        print(f"Wrote {record_count} records to {output_file}")


if __name__ == "__main__":
    main()
