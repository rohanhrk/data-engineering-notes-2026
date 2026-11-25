import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import SelectFromCollection
from awsglue.utils import getResolvedOptions
from awsgluedq.transforms import EvaluateDataQuality
from pyspark.context import SparkContext
from pyspark.sql.functions import col, current_timestamp


# --------------------------------------------------
# Logger setup
# --------------------------------------------------

logger = logging.getLogger("glue_data_quality_to_iceberg_job")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
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
        "TARGET_DATABASE",
        "TARGET_TABLE",
        "ICEBERG_WAREHOUSE",
        "DQ_RESULTS_S3_PATH",
    ],
)

job_name = args["JOB_NAME"]
source_database = args["SOURCE_DATABASE"]
source_table = args["SOURCE_TABLE"]
target_database = args["TARGET_DATABASE"]
target_table = args["TARGET_TABLE"]
iceberg_warehouse = args["ICEBERG_WAREHOUSE"]
dq_results_s3_path = args["DQ_RESULTS_S3_PATH"]


# --------------------------------------------------
# Glue and Spark initialization
# --------------------------------------------------

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(job_name, args)

# The Glue job must also have --datalake-formats=iceberg and the Iceberg Spark
# extension configured. See README.md for the exact job parameters.
spark.conf.set(
    "spark.sql.catalog.glue_catalog",
    "org.apache.iceberg.spark.SparkCatalog",
)
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", iceberg_warehouse)
spark.conf.set(
    "spark.sql.catalog.glue_catalog.catalog-impl",
    "org.apache.iceberg.aws.glue.GlueCatalog",
)
spark.conf.set(
    "spark.sql.catalog.glue_catalog.io-impl",
    "org.apache.iceberg.aws.s3.S3FileIO",
)

logger.info("Glue job started")
logger.info("Source table: %s.%s", source_database, source_table)
logger.info("Target table: %s.%s", target_database, target_table)


# --------------------------------------------------
# Read the crawler-created table from Glue Catalog
# --------------------------------------------------

source_dynamic_frame = glue_context.create_dynamic_frame.from_catalog(
    database=source_database,
    table_name=source_table,
    transformation_ctx="source_dynamic_frame",
)

logger.info("Source schema:")
source_dynamic_frame.printSchema()


# --------------------------------------------------
# Evaluate and publish AWS Glue Data Quality results
# --------------------------------------------------

# These values match the raw CSV. The crawler already provides the numeric
# types needed by the quantity and amount rules, so extra casting is unnecessary.
data_quality_ruleset = """
Rules = [
    IsComplete "order_id",
    IsUnique "order_id",
    IsComplete "customer_id",
    IsComplete "customer_email",
    IsComplete "product_id",
    IsComplete "order_timestamp",
    ColumnValues "order_timestamp" matches "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$",
    ColumnValues "quantity" between 1 and 20,
    ColumnValues "unit_price" > 0,
    ColumnValues "discount_amount" >= 0,
    ColumnValues "tax_amount" >= 0,
    ColumnValues "shipping_amount" >= 0,
    ColumnValues "currency" in ["INR"],
    ColumnValues "country" in ["India"],
    ColumnValues "payment_method" in ["UPI", "Credit Card", "Debit Card", "Net Banking", "COD", "Wallet"],
    ColumnValues "order_status" in ["Placed", "Processing", "Paid", "Shipped", "Delivered", "Cancelled", "Returned"]
]
"""

dq_results = EvaluateDataQuality().process_rows(
    frame=source_dynamic_frame,
    ruleset=data_quality_ruleset,
    publishing_options={
        "dataQualityEvaluationContext": "orders_data_quality",
        "enableDataQualityCloudWatchMetrics": True,
        "enableDataQualityResultsPublishing": True,
        "resultsS3Prefix": dq_results_s3_path,
    },
    additional_options={"performanceTuning.caching": "CACHE_NOTHING"},
)

row_level_outcomes = SelectFromCollection.apply(
    dfc=dq_results,
    key="rowLevelOutcomes",
    transformation_ctx="row_level_outcomes",
).toDF()

# Show rejected rows in the Glue job logs for the demonstration.
row_level_outcomes.filter(
    col("DataQualityEvaluationResult") == "Failed"
).select(
    "order_id",
    "DataQualityRulesFail",
).show(20, truncate=False)


# --------------------------------------------------
# Transform only rows that passed Data Quality
# --------------------------------------------------

final_df = (
    row_level_outcomes
    .filter(col("DataQualityEvaluationResult") == "Passed")
    .drop(
        "DataQualityRulesPass",
        "DataQualityRulesFail",
        "DataQualityRulesSkip",
        "DataQualityEvaluationResult",
    )
    .withColumn("gross_amount", col("quantity") * col("unit_price"))
    .withColumn(
        "net_amount",
        (col("quantity") * col("unit_price"))
        - col("discount_amount")
        + col("tax_amount")
        + col("shipping_amount"),
    )
    .withColumn("processed_at", current_timestamp())
)


# --------------------------------------------------
# Write to an Iceberg table in the Glue Data Catalog
# --------------------------------------------------

# CREATE NAMESPACE creates the target Glue database when it does not exist.
# createOrReplace creates the table on the first run and replaces its contents
# on later runs. This keeps the classroom example intentionally simple.
spark.sql(
    f"CREATE NAMESPACE IF NOT EXISTS glue_catalog.`{target_database}`"
)

iceberg_table = f"glue_catalog.`{target_database}`.`{target_table}`"

(
    final_df.writeTo(iceberg_table)
    .using("iceberg")
    .tableProperty("format-version", "2")
    .createOrReplace()
)

logger.info("Data written successfully to %s", iceberg_table)


# --------------------------------------------------
# Commit the Glue job
# --------------------------------------------------

job.commit()
logger.info("Glue job completed successfully")
