"""NYC FHVHV trip analytics - intentionally unoptimized Spark job.

Business questions
------------------
1. How do FHVHV trips perform by pickup borough/platform per day?
2. How do FHVHV trips perform by pickup zone per month?

This version keeps the original job's *unoptimized* behavior intentionally.
The comments explain where wide transformations, late filtering, disabled
optimizations, and recomputation occur so the file can be used for Spark
performance learning.
"""

import argparse
import logging
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# ---------------------------------------------------------------------------
# Taxi-zone lookup schema
# ---------------------------------------------------------------------------
# Defining the schema explicitly avoids schema inference for the CSV lookup.
ZONE_SCHEMA = StructType(
    [
        StructField("LocationID", IntegerType(), nullable=False),
        StructField("Borough", StringType(), nullable=True),
        StructField("Zone", StringType(), nullable=True),
        StructField("service_zone", StringType(), nullable=True),
    ]
)


def configure_logging():
    """Configure simple stdout logging for Spark job progress."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("fhvhv-zone-analytics-unoptimized")

def build_spark():
    """Create a Spark session with optimizations intentionally disabled.

    These settings make the job useful for studying an unoptimized Spark
    execution plan:
      * AQE is disabled.
      * Automatic broadcast joins are disabled, forcing a shuffle-based join.
      * Parquet filter pushdown is disabled, making the scan less efficient.
    """
    return (
        SparkSession.builder
        .appName("fhvhv-zone-analytics-unoptimized")
        .config("spark.sql.adaptive.enabled", "false")
        # Prevent Spark from automatically broadcasting the small zone table.
        # The join therefore becomes a shuffle-based join for demonstration.
        .config("spark.sql.autoBroadcastJoinThreshold", "-1")
        # Disable Parquet filter pushdown so filters are not pushed into the
        # file scan. This intentionally increases scan work.
        .config("spark.sql.parquet.filterPushdown", "false")
        .getOrCreate()
    )

def parse_args():
    """Parse input and output locations supplied from the command line"""
    parser = argparse.ArgumentParser(
        description="Run unoptimized FHVHV spark analytics job."
    )
    
    parser.add_argument(
        "--trip-input",
        default="data/fhvhv_tripdata_2024-*.parquet",
        help="input parquet path, e.g. s3a://bucket/fhvhv_tripdata_2024-*.parquet"
    )
    
    parser.add_argument(
        "--zone-input",
        default="data/taxi_zone_lookup.csv",
        help="Taxi-zone CSV path, e.g. s3a://bucket/taxi_zone_lookup.csv"
    )
    
    parser.add_argument(
        "--output-base",
        default="output/unoptimized_fhvhv_zone_analytics",
        help="Base output path for this job."
    )
    
    return parser.parse_args()

def read_inputs(spark, args, logger):
    """Read the FHVHV trip data and taxi-zone lookup table."""
    logger.info(
        "Reading trip parquet data from %s", 
        args.trip_input    
    )
    trips_raw_df = spark.read.parquet(args.trip_input)
    
    logger.info(
        "Reading taxi zone lookup CSV from %s",
        args.zone_input
    )
    zones_raw_df = (
        spark.read
        .option("header", "true")
        .schema(ZONE_SCHEMA)
        .csv(args.zone_input)
    )
    
    return trips_raw_df, zones_raw_df

def build_unoptimized_analytics(trips_raw_df, zones_raw_df):
    """Build daily and monthly metrics while intentionally preserving inefficiency.

    The order of operations is important for the learning exercise:
      1. Create derived columns from the raw trip DataFrame.
      2. Join before filtering and before aggressively reducing columns.
      3. Apply filters only after the expensive join.
      4. Perform two separate aggregations.
    """
    
    # -----------------------------------------------------------------------
    # STEP 1: Derived columns
    # -----------------------------------------------------------------------
    # raw_payload_size deliberately references every source column. The later
    # no-op filter keeps this expression alive in the physical plan, making
    # unnecessary column processing visible for performance analysis.
    raw_payload_text = F.concat_ws(
        "||",
        *[
            F.coalesce(F.col(column_name).cast("string"),F.lit(""))
            for column_name in trips_raw_df.columns
        ]
    )
    trips_with_derived_columns = (
        trips_raw_df.withColumn("raw_payload_size", F.length(raw_payload_text))
        .withColumn("trip_date", F.to_date("pickup_datetime"))
        .withColumn("trip_month", F.date_format("pickup_datetime", "yyyy-MM"))
        .withColumn("trip_hour", F.hour("pickup_datetime"))
        .withColumn("trip_duration_minutes", F.col("trip_time") / F.lit(60.0))
        .withColumn(
            "gross_trip_value",
            F.col("base_passenger_fare") +
            F.col("tolls") +
            F.col("bcf") +
            F.col("sales_tax") +
            F.col("congestion_surcharge") +
            F.col("airport_fee") +
            F.col("tips")
        ) 
        .withColumn(
            "is_shared_trip",
            F.when(
                F.col("shared_request_flag") == F.lit("Y"), 
                F.lit(1)
            ).otherwise(
                F.lit(0)
            )
        )
        .withColumn(
            "is_airport_trip",
            F.when(
                F.col("airport_fee") > F.lit(0), 
                F.lit(1)
            ).otherwise(F.lit(0))
        )
    )
    
    # -----------------------------------------------------------------------
    # STEP 2: Prepare the taxi-zone lookup
    # -----------------------------------------------------------------------
    # Rename lookup columns so the join output has business-friendly names.
    # No broadcast hint is used. Combined with the disabled broadcast threshold,
    # this makes the join shuffle-based.
    pickup_zones = zones_raw_df.select(
        F.col("LocationID").alias("PULocationID"),
        F.col("Borough").alias("pickup_borough"),
        F.col("Zone").alias("pickup_zone"),
        F.col("service_zone")
    )
    
     # -----------------------------------------------------------------------
    # STEP 3: Wide transformation - shuffle join
    # -----------------------------------------------------------------------
    # This is intentionally placed BEFORE filtering. Therefore more rows and
    # columns flow through the expensive wide transformation than necessary.
    enriched_trips = trips_with_derived_columns.join(
        pickup_zones, 
        on="PULocationID", 
        how="left"
    )
    
    # -----------------------------------------------------------------------
    # STEP 4: Filters are intentionally applied late
    # -----------------------------------------------------------------------
    # In an optimized job, these filters would be pushed as early as possible
    # so fewer records reach the shuffle join and aggregations.
    filtered_enriched_trips = (
        enriched_trips
        .filter(F.col("raw_payload_size") >= F.lit(0))
        .filter(F.col("pickup_datetime").isNotNull())
        .filter(F.col("dropoff_datetime").isNotNull())
        .filter(F.col("trip_miles") > F.lit(0))
        .filter(F.col("trip_time") > F.lit(0))
        .filter(F.col("base_passenger_fare") >= F.lit(0))
    )
    
    # Reuse these expressions in the daily aggregation below.
    total_miles = F.sum("trip_miles")
    total_passenger_fare = F.sum("base_passenger_fare")
    
    # Avoid division by zero when calculating fare per mile.
    fare_per_mile = F.when(
        total_miles != F.lit(0.0), 
        total_passenger_fare / total_miles
    )
    
    # -----------------------------------------------------------------------
    # STEP 5: Wide transformation - daily aggregation
    # -----------------------------------------------------------------------
    # groupBy causes a shuffle because records with the same grouping keys
    # must be brought together.
    daily_borough_platform_metrics = filtered_enriched_trips.groupBy(
        "trip_date", "pickup_borough", "hvfhs_license_num"
    ).agg(
        F.count(F.lit(1)).alias("trip_count"),
        F.round(
            total_miles, 2
        ).alias("total_miles"),
        F.round(
            F.sum("trip_duration_minutes"), 2
        ).alias("total_trip_minutes"),
        F.round(
            total_passenger_fare, 2
        ).alias("total_passenger_fare"),
        F.round(
            F.sum("driver_pay"), 2
        ).alias("total_driver_pay"),
        F.round(
            fare_per_mile, 2
        ).alias("avg_fare_per_mile"),
        F.round(
            F.avg("driver_pay"), 2
        ).alias("avg_driver_pay_per_trip"),
        F.sum("is_shared_trip").alias("shared_trip_count"),
    )

    # -----------------------------------------------------------------------
    # STEP 6: Wide transformation - monthly zone aggregation
    # -----------------------------------------------------------------------
    # This is a second aggregation over the same logical upstream lineage.
    monthly_zone_metrics = (
        filtered_enriched_trips
        .groupBy(
            "trip_month", 
            "pickup_borough", 
            "pickup_zone", 
            "service_zone"
        ).agg(
            F.count(F.lit(1)).alias("trip_count"),
            F.round(
                F.sum("gross_trip_value"), 2
            ).alias("total_gross_trip_value"),
            F.round(
                F.sum("tips"), 2
            ).alias("total_tips"),
            F.round(
                F.sum("driver_pay"), 2
            ).alias("total_driver_pay"),
            F.round(
                F.avg("trip_miles"), 2
            ).alias("avg_trip_miles"),
            F.round(
                F.avg("trip_duration_minutes"), 2
            ).alias("avg_trip_minutes"),
            F.sum("is_airport_trip").alias("airport_trip_count"),
            F.round(
                F.sum("congestion_surcharge"), 2
            ).alias("total_congestion_surcharge"),
        )
    )

    return daily_borough_platform_metrics, monthly_zone_metrics

def write_outputs(
    daily_metrics_df, 
    monthly_matrics_df, 
    output_base, 
    logger
):
    
    """Write both result DataFrames.

    IMPORTANT: Neither shared upstream DataFrame is cached/persisted.
    Therefore the two actions can recompute the common scan + join lineage.
    This is intentional because this file represents the unoptimized job.
    """
    
    daily_output = f"{output_base.rstrip('/')}/daily_borough_platform_metrics"
    monthly_output = f"{output_base.rstrip('/')}/monthly_pickup_zone_metrics"
    
    # ACTION 1
    logger.info("Writing daily borough/platform metrics to %s", daily_output)
    (
        daily_metrics_df
        .write
        .mode("overwrite")
        .parquet(daily_output)
    )
    
    # ACTION 2
    # Because the common lineage was not persisted, Spark may execute the
    # upstream scan, join, and aggregation lineage again for this action.
    logger.info("Writing monthly pickup zone metrics to %s", monthly_output)
    (
        monthly_matrics_df
        .write
        .mode("overwrite")
        .parquet(monthly_output)
    )
    
def main():
    """Application entry point."""
    logger = configure_logging()
    spark = build_spark()
    args = parse_args()
    
    # Keep Spark's own logs quieter while retaining application-level INFO logs.
    spark.sparkContext.setLogLevel("WARN")
    
    
    logger.info("Starting unoptimized FHVHV analytics job")
    logger.info(
        "AQE enabled? %s",
        spark.conf.get("spark.sql.adaptive.enabled")
    )
    logger.info(
        "Shuffle partitiones: %s",
        spark.conf.get("spark.sql.shuffle.partitions")
    )
    logger.info(
        "Auto broadcast join threshold: %s",
        spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
    )
    
    try:
        trips_raw_df, zones_raw_df = read_inputs(spark, args, logger)
        
        daily_metrics_df, monthly_matrics_df = build_unoptimized_analytics(
            trips_raw_df, 
            zones_raw_df
        )
        
        write_outputs(
            daily_metrics_df, 
            monthly_matrics_df, 
            args.output_base, 
            logger
        )
        
        logger.info("Finished unoptimized FHVHV analytics job")
    finally:
        # Always stop the SparkSession, even when the job fails
        spark.stop()
        

if __name__ == "__main__":
    main()