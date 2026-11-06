import json
from contextlib import closing

import boto3
import pandas as pd


def process_sales_csv(event, context):
    """Accept a manual test event containing the S3 bucket and object key."""
    # 1. Download the CSV from S3.
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=event["bucket"], Key=event["key"])

    # 2. Load the CSV into a pandas DataFrame and close the S3 stream.
    with closing(response["Body"]) as csv_file:
        df = pd.read_csv(csv_file)

    # 3. Calculate each order's sales amount (all prices are in INR).
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)

    # 4. Group orders by category and sum their sales amounts.
    category_sales = df.groupby("category")["total_amount"].sum().round(2)

    # 5. Return summary statistics and the first five processed records.
    result = {
        "row_count": len(df),
        "columns": df.columns.tolist(),
        "currency": "INR",
        "total_quantity": int(df["quantity"].sum()),
        "total_sales": round(float(df["total_amount"].sum()), 2),
        "sales_by_category": category_sales.to_dict(),
        "preview": json.loads(df.head(5).to_json(orient="records")),
    }

    return {"statusCode": 200, "body": json.dumps(result)}
