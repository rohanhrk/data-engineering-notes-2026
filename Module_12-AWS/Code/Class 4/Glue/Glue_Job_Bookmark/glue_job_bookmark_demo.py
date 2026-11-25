import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import input_file_name


# --------------------------------------------------
# Logger setup
# --------------------------------------------------

logger = logging.getLogger("glue_job_bookmark_demo")
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
    ],
)

job_name = args["JOB_NAME"]
source_database = args["SOURCE_DATABASE"]
source_table = args["SOURCE_TABLE"]


# --------------------------------------------------
# Glue initialization
# --------------------------------------------------

sc = SparkContext()
glue_context = GlueContext(sc)

job = Job(glue_context)

# job.init loads the bookmark state saved for this Glue job.
job.init(job_name, args)

logger.info("Glue job-bookmark demo started")
logger.info("Source table: %s.%s", source_database, source_table)


# --------------------------------------------------
# Read new files from the Glue Catalog table
# --------------------------------------------------

# IMPORTANT:
# Keep this transformation_ctx value unchanged. Glue uses it as the key for
# this source inside the job bookmark state.
source_dynamic_frame = glue_context.create_dynamic_frame.from_catalog(
    database=source_database,
    table_name=source_table,
    transformation_ctx="bank_transactions_bookmark_source",
)

source_df = source_dynamic_frame.toDF()


# --------------------------------------------------
# Log each file read during this run
# --------------------------------------------------

# input_file_name() returns the S3 object path that produced each record.
# Grouping by it lets us print one record count per newly processed file.
file_counts = (
    source_df
    .withColumn("source_file", input_file_name())
    .groupBy("source_file")
    .count()
    .orderBy("source_file")
    .collect()
)

if file_counts:
    total_records = 0

    for file_record in file_counts:
        s3_path = file_record["source_file"]
        file_name = s3_path.rsplit("/", 1)[-1]
        record_count = file_record["count"]
        total_records += record_count

        logger.info(
            "File read: %s | Records: %s | S3 path: %s",
            file_name,
            record_count,
            s3_path,
        )

    logger.info("Total records read in this run: %s", total_records)
else:
    logger.info("No new files were read; the bookmark is up to date")


# --------------------------------------------------
# Commit the bookmark
# --------------------------------------------------

# job.commit saves the successfully processed S3 files in the bookmark state.
job.commit()

logger.info("Glue job-bookmark demo completed successfully")
