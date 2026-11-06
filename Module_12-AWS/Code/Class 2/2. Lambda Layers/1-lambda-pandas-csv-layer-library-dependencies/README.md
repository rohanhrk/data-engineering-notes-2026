# Process a sales CSV with AWS Lambda and pandas

Read a CSV from Amazon S3, calculate order amounts with pandas, and return a sales summary. This example uses a manual Lambda console test event.

## 1. Explore the sample data

`sample.csv` contains 15 fictional orders across 10 customers and three categories: Electronics, Home, and Stationery. Each row represents one order for one product. All prices are in INR, before any taxes or discounts.

| Column | Meaning | Example |
| --- | --- | --- |
| `order_id` | Unique order identifier | `ORD-1001` |
| `order_date` | Order date in YYYY-MM-DD format | `2026-09-01` |
| `customer_name` | Fictional customer name | `Asha Sharma` |
| `city` | Customer's city | `Bengaluru` |
| `category` | Product category | `Electronics` |
| `product` | Product name | `Wireless Mouse` |
| `quantity` | Units ordered | `2` |
| `unit_price` | Price per unit in INR | `799.00` |

## 2. Understand the code

Open `sales_processor.py`. Its handler function, `process_sales_csv(event, context)`, performs five steps:

1. Fetch the object identified by `bucket` and `key` in the test event.
2. Read the CSV into a pandas DataFrame.
3. Add `total_amount = quantity * unit_price` to each row.
4. Group rows by `category` and sum their sales amounts.
5. Return the row count, columns, units sold, total sales, category totals, and the first five processed records.

The AWS Lambda **Handler** setting must be:

```text
sales_processor.process_sales_csv
```

The part before the dot is the Python filename without `.py`; the part after the dot is the function name. See the [AWS handler naming documentation](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html#python-handler-naming).

## 3. Build the deployment ZIP

From the class working directory:

```bash
cd Lambda-Pandas-CSV-Example
python3 -m zipfile -c lambda-pandas-deployment.zip sales_processor.py
```

This recreates the ZIP with `sales_processor.py` at its root. A ready-to-upload ZIP is also included. Rebuild it after editing the code. The sample CSV belongs in S3; pandas is supplied by the Lambda layer.

## 4. Configure S3 and Lambda

1. Upload `sample.csv` to the root of an S3 bucket in your chosen AWS Region.
2. Create a Lambda function with **Python 3.13**, **x86_64** architecture, **512 MB** memory, and a **30-second** timeout.
3. Under **Layers → Add a layer → AWS layers**, select **AWSSDKPandas-Python313** and a version matching the runtime and architecture. If it is not listed, use a matching layer ARN for your Region from the [AWS SDK for pandas layer list](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html).
4. Upload `lambda-pandas-deployment.zip` using **Code → Upload from → .zip file**.
5. Under **Code → Runtime settings → Edit**, set **Handler** to `sales_processor.process_sales_csv` and save.
6. Keep the execution role's basic Lambda logging permissions and add the following policy, replacing `your-bucket-name`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/sample.csv"
    }
  ]
}
```

## 5. Run the example

Create a Lambda console test event using `test_event.json`:

```json
{
  "bucket": "your-bucket-name",
  "key": "sample.csv"
}
```

Replace the bucket name and click **Test**. If you uploaded the CSV into a folder, update both the event's `key` and the policy's object path. An S3 notification trigger uses a different event structure and is not configured for this example.

The response has `statusCode: 200` and a JSON string in `body`. After decoding `body`, these summary values should match:

```json
{
  "row_count": 15,
  "currency": "INR",
  "total_quantity": 34,
  "total_sales": 16817.0,
  "sales_by_category": {
    "Electronics": 8393.0,
    "Home": 5493.0,
    "Stationery": 2931.0
  }
}
```

The body also includes `columns` (the eight CSV columns plus `total_amount`) and `preview` (the first five rows). The first order's `total_amount` is `1598.0`.

## Troubleshooting

| Error | Check |
| --- | --- |
| Cannot import module / handler not found | Confirm the ZIP contains `sales_processor.py` at its root and the handler is `sales_processor.process_sales_csv`. |
| No module named `pandas` | Attach the pandas layer matching your Python runtime, architecture, and Region. |
| S3 `AccessDenied` | Confirm the execution role can read the exact object. Customer-managed KMS encryption also requires the appropriate key permissions. |
| S3 `NoSuchKey` | Match the event's `key` to the object's full, case-sensitive S3 key. |
| Missing column / numeric calculation error | Use the supplied CSV schema with numeric `quantity` and `unit_price` values. |