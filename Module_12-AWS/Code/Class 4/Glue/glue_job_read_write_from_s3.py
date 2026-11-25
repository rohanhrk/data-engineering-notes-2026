import sys
import logging
from datetime import datetime

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

from pyspark.context import SparkContext
from pyspark.sql.functions import (
    col,
    lit,
    current_timestamp,
    when,
    upper,
    trim,
    to_date,
    to_timestamp
)
from pyspark.sql.types import DoubleType, IntegerType


# --------------------------------------------------
# Logger setup
# --------------------------------------------------

logger = logging.getLogger("glue_csv_transformation_job")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s - %(message)s"
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)


# --------------------------------------------------
# Job arguments
# --------------------------------------------------

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_DATABASE",
        "SOURCE_TABLE",
        "TARGET_S3_PATH"
    ]
)

job_name = args["JOB_NAME"]
source_database = args["SOURCE_DATABASE"]
source_table = args["SOURCE_TABLE"]
target_s3_path = args["TARGET_S3_PATH"]


# --------------------------------------------------
# Glue context initialization
# --------------------------------------------------

# It initialize the Spark engine and connect it to AWS Glue’s job-management features.
# Creates the main Apache Spark context.
# - Connects your Python driver to the Spark execution engine.
# - Manages executors, distributed tasks, memory, and cluster resources.
sc = SparkContext()

# Wraps the Spark context with AWS Glue functionality.
# It adds Glue-specific capabilities such as:
# - Reading from the Glue Data Catalog.
# - Creating and processing DynamicFrame objects.
# - Reading and writing AWS data sources.
# - Glue transformation helpers.
glue_context = GlueContext(sc)

# Retrieves the standard Spark SQL SparkSession associated with the Glue context.
# You use spark when working with:
# - Spark DataFrames.
# - Spark SQL.
# - Iceberg operations.
# - Temporary views.
# - DataFrame readers and writers.
spark = glue_context.spark_session

# Creates an AWS Glue Job helper object.
job = Job(glue_context)

# Initializes that helper for the current job run.
# - job_name is usually obtained from args["JOB_NAME"].
# - args contains the resolved runtime parameters.
# - Initializes Glue features such as job-bookmark tracking.
job.init(job_name, args)

logger.info("Glue job started")
logger.info(f"Job name: {job_name}")
logger.info(f"Source database: {source_database}")
logger.info(f"Source table: {source_table}")
logger.info(f"Target S3 path: {target_s3_path}")


try:
    # --------------------------------------------------
    # Read data from Glue Catalog as DynamicFrame
    # --------------------------------------------------

    logger.info("Reading data from Glue Data Catalog")

    source_dynamic_frame = glue_context.create_dynamic_frame.from_catalog(
        database=source_database,
        table_name=source_table,
        transformation_ctx="source_dynamic_frame"
    )

    source_count = source_dynamic_frame.count()
    logger.info(f"Source record count: {source_count}")

    if source_count == 0:
        logger.warning("Source table has zero records. Job will complete without writing output.")
        job.commit()
        sys.exit(0)

    logger.info("Source schema:")
    source_dynamic_frame.printSchema()


    # --------------------------------------------------
    # Convert DynamicFrame to Spark DataFrame
    # --------------------------------------------------

    logger.info("Converting DynamicFrame to DataFrame")

    df = source_dynamic_frame.toDF()

    logger.info(f"Source columns: {df.columns}")


    # --------------------------------------------------
    # Basic schema-safe transformations
    # --------------------------------------------------

    logger.info("Applying transformations")

    required_columns = [
        "order_id",
        "customer_id",
        "customer_name",
        "email",
        "city",
        "state",
        "order_date",
        "product_id",
        "product_category",
        "quantity",
        "unit_price",
        "discount_amount",
        "payment_method",
        "order_status"
    ]

    missing_columns = [column_name for column_name in required_columns if column_name not in df.columns]

    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise Exception(f"Input data is missing required columns: {missing_columns}")

    transformed_df = (
        df
        # Clean string columns
        .withColumn("order_id", trim(col("order_id")))
        .withColumn("customer_id", trim(col("customer_id")))
        .withColumn("customer_name", trim(col("customer_name")))
        .withColumn("email", trim(col("email")))
        .withColumn("city", trim(col("city")))
        .withColumn("state", trim(col("state")))

        # Standardize categorical columns
        .withColumn("product_category", upper(trim(col("product_category"))))
        .withColumn("payment_method", upper(trim(col("payment_method"))))
        .withColumn("order_status", upper(trim(col("order_status"))))

        # Type casting
        .withColumn("quantity", col("quantity").cast(IntegerType()))
        .withColumn("unit_price", col("unit_price").cast(DoubleType()))
        .withColumn("discount_amount", col("discount_amount").cast(DoubleType()))

        # The crawler reads order_date as a string, while the CSV contains a
        # timestamp such as "2026-10-02 07:08:00". Parse the complete timestamp
        # first, and then derive a DateType value for output partitioning.
        .withColumn(
            "order_date",
            to_date(
                to_timestamp(
                    trim(col("order_date")),
                    "yyyy-MM-dd HH:mm:ss"
                )
            )
        )

        # Derived columns
        .withColumn("gross_amount", col("quantity") * col("unit_price"))
        .withColumn(
            "net_amount",
            (col("quantity") * col("unit_price")) - col("discount_amount")
        )

        # Business flag
        .withColumn(
            "is_successful_order",
            when(col("order_status").isin("PAID", "SHIPPED", "DELIVERED"), lit(True))
            .otherwise(lit(False))
        )

        # Audit columns
        .withColumn("processed_at", current_timestamp())
        .withColumn("source_table", lit(f"{source_database}.{source_table}"))
    )


    # --------------------------------------------------
    # Data quality filters
    # --------------------------------------------------

    logger.info("Applying data quality filters")

    clean_df = transformed_df.filter(
        col("order_id").isNotNull()
        & col("customer_id").isNotNull()
        & col("order_date").isNotNull()
        & col("quantity").isNotNull()
        & col("unit_price").isNotNull()
        & (col("quantity") > 0)
        & (col("unit_price") > 0)
    )

    clean_count = clean_df.count()
    rejected_count = source_count - clean_count

    logger.info(f"Clean record count: {clean_count}")
    logger.info(f"Rejected record count: {rejected_count}")


    # --------------------------------------------------
    # Select final output columns
    # --------------------------------------------------

    final_df = clean_df.select(
        "order_id",
        "customer_id",
        "customer_name",
        "email",
        "city",
        "state",
        "order_date",
        "product_id",
        "product_category",
        "quantity",
        "unit_price",
        "discount_amount",
        "gross_amount",
        "net_amount",
        "payment_method",
        "order_status",
        "is_successful_order",
        "processed_at",
        "source_table"
    )


    # --------------------------------------------------
    # Convert DataFrame back to DynamicFrame
    # --------------------------------------------------

    logger.info("Converting transformed DataFrame back to DynamicFrame")

    final_dynamic_frame = DynamicFrame.fromDF(
        final_df,
        glue_context,
        "final_dynamic_frame"
    )


    # --------------------------------------------------
    # Write directly to S3
    # --------------------------------------------------

    logger.info("Writing transformed data to S3")

    glue_context.write_dynamic_frame.from_options(
        frame=final_dynamic_frame,
        connection_type="s3",
        connection_options={
            "path": target_s3_path,
            "partitionKeys": ["order_date"]
        },
        format="parquet",
        transformation_ctx="s3_output"
    )

    logger.info(f"Data successfully written to: {target_s3_path}")


except Exception:
    logger.exception("Glue job failed")
    raise


else:
    logger.info("Committing Glue job")
    # Commit bookmark progress only after all processing and writes succeed.
    job.commit()
    logger.info("Glue job completed successfully")
