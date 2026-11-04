"""
S3 Access Using Python (boto3)

This script demonstrates how to interact with AWS S3 using the boto3 library.
It covers common S3 operations such as listing buckets, uploading, downloading,
reading, and deleting objects.

Prerequisites:
    - Install boto3: pip install boto3
    - Configure AWS credentials using one of the following methods:
        1. AWS CLI: run `aws configure` and provide Access Key, Secret Key, and Region
        2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
        3. IAM role (when running on an EC2 instance or Lambda function)
"""

import boto3
from botocore.exceptions import ClientError
import json


def get_s3_client():
    """Create and return an S3 client using default credentials."""
    return boto3.client("s3")


def list_buckets():
    """List all S3 buckets in the AWS account."""
    s3 = get_s3_client()
    response = s3.list_buckets()
    print("S3 Buckets:")
    # print(json.dumps(response, indent=4, default=str))
    for bucket in response["Buckets"]:
        print(f"  - {bucket['Name']} (created: {bucket['CreationDate']})")


def list_objects(bucket_name, prefix=""):
    """
    List all objects in a given S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket to list objects from.
        prefix: Filter results to objects whose keys start with this prefix.
                For example, prefix="images/" lists only objects inside the images folder.
    """
    s3 = get_s3_client()
    print(f"\nObjects in '{bucket_name}' (prefix='{prefix}'):")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if "Contents" not in response:
        print("  (no objects found)")
        return
    for obj in response["Contents"]:
        print(f"  - {obj['Key']}  (size: {obj['Size']} bytes)")


def upload_file(bucket_name, file_path, object_key):
    """
    Upload a local file to an S3 bucket.

    Args:
        bucket_name: Target S3 bucket name.
        file_path: Path to the local file to upload.
        object_key: The S3 key (path) where the file will be stored.
                    For example, "uploads/data.txt" stores it inside an uploads folder.
    """
    s3 = get_s3_client()
    s3.upload_file(file_path, bucket_name, object_key)
    print(f"Uploaded '{file_path}' to s3://{bucket_name}/{object_key}")


def download_file(bucket_name, object_key, file_path):
    """
    Download a file from S3 to the local filesystem.

    Args:
        bucket_name: Source S3 bucket name.
        object_key: The S3 key (path) of the object to download.
        file_path: Local file path where the downloaded file will be saved.
    """
    s3 = get_s3_client()
    s3.download_file(bucket_name, object_key, file_path)
    print(f"Downloaded s3://{bucket_name}/{object_key} to '{file_path}'")


def read_file_content(bucket_name, object_key):
    """
    Read and print the content of a text file directly from S3 without downloading it.

    This uses get_object() to stream the file content into memory.
    Best suited for small text files. For large files, use download_file() instead.

    Args:
        bucket_name: S3 bucket name.
        object_key: The S3 key (path) of the object to read.

    Returns:
        The file content as a string.
    """
    s3 = get_s3_client()
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    # Read the streaming body and decode bytes to a UTF-8 string
    content = response["Body"].read().decode("utf-8")
    print(f"\nContent of s3://{bucket_name}/{object_key}:")
    print(content)
    return content


def delete_object(bucket_name, object_key):
    """
    Delete an object from an S3 bucket.

    Args:
        bucket_name: S3 bucket name.
        object_key: The S3 key (path) of the object to delete.
    """
    s3 = get_s3_client()
    s3.delete_object(Bucket=bucket_name, Key=object_key)
    print(f"Deleted s3://{bucket_name}/{object_key}")


def main():
    bucket_name = "learning-bucket-2-nov-26"

    try:
        # 1. List all S3 buckets in the account
        list_buckets()

        # 2. List all objects inside the specified bucket
        list_objects(bucket_name, prefix = "raw_data/input/")

        # 3. Upload a local file to S3 under the "uploads/" prefix
        upload_file(bucket_name, "C:/Users/rohan/OneDrive/Desktop/Data Engineering - Shashank Mishra/data-engineering-notes/Module_12-AWS/Class 1 - AWS S3_Lamda/S3-Python-Code/Data/store_data.csv", "uploads/store_data.csv")

        # # 4. Download the uploaded file back from S3 to a local path
        download_file(bucket_name, "uploads/store_data.csv", "store_data.csv")

        # # 5. Read the file content directly from S3 (without saving to disk)
        # read_file_content(bucket_name, "uploads/store_data.csv")

        # # # 6. Clean up — delete the uploaded object from S3
        # # delete_object(bucket_name, "uploads/store_data.csv")

    except ClientError as e:
        # Handle AWS-specific errors (e.g., bucket not found, access denied)
        print(f"AWS Error: {e.response['Error']['Message']}")


if __name__ == "__main__":
    main()
