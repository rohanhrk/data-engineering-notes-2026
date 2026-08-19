"""
Optimized Spark Data Processing Job: NYC FHVHV Trip Analytics

Business Objectives:
    1. Analyze daily High-Volume For-Hire Vehicle (FHVHV) trip performance metrics by 
       pickup borough and licensing platform.
    2. Analyze monthly performance metrics aggregated by pickup zone and service zone.

Key Performance Optimizations:
    - Column Pruning: Reads only necessary schema fields from raw Parquet files to reduce I/O.
    - Explicit Schema Enforcement: Avoids schema inference overhead on CSV lookups.
    - Early Data Cleaning & Transformation: Applies filters and row-level transformations prior to joins/shuffles.
    - Broadcast Hash Join: Broadcasts the small taxi zone lookup table to prevent full shuffles of trip data.
    - Caching/Persisting Intermediate State: Persists enriched trip DataFrame (`MEMORY_AND_DISK`) to reuse 
      the dataset across multiple output actions without rescanning/recomputing source data.
"""

import argparse
import logging
import sys

from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Explicit Schema Definition for Taxi Zone Reference Data
ZONE_SCHEMA = StructType(
    [
        StructField("LocationID", IntegerType(), nullable=False),
        StructField("Borough", StringType(), nullable=True),
        StructField("Zone", StringType(), nullable=True),
        StructField("service_zone", StringType(), nullable=True),
    ]
)

# Column Pruning Selection: Restrict reading to required fields only
REQUIRED_TRIP_COLUMNS = [
    "hvfhs_license_num",
    "pickup_datetime",
    "dropoff_datetime",
    "PULocationID",
    "trip_miles",
    "trip_time",
    "base_passenger_fare",
    "tolls",
    "bcf",
    "sales_tax",
    "congestion_surcharge",
    "airport_fee",
    "tips",
    "driver_pay",
    "shared_request_flag",
]


def parse_args():
    """Parse runtime command line arguments for input/output paths."""
    parser = argparse.ArgumentParser(
        description="Run the optimized FHVHV Spark analytics job."
    )
    parser.add_argument(
        "--trip-input",
        default="data/fhvhv_tripdata_2024-*.parquet",
        help="Input parquet path. Example: s3a://bucket/fhvhv_tripdata_2024-*.parquet",
    )
    parser.add_argument(
        "--zone-input",
        default="data/taxi_zone_lookup.csv",
        help="Taxi zone lookup CSV path. Example: s3a://bucket/taxi_zone_lookup.csv",
    )
    parser.add_argument(
        "--output-base",
        default="output/optimized_fhvhv_zone_analytics",
        help="Base output directory path for saving result datasets.",
    )
    return parser.parse_args()


def configure_logging():
    """Initialize standard output logger for execution tracking."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("fhvhv-zone-analytics-optimized")


def build_spark(args):
    """
    Initialize SparkSession with performance configurations.
    
    Config Settings:
      - autoBroadcastJoinThreshold: Set to 10MB to enable automatic broadcasting of small tables.
      - adaptive.enabled: Set to false explicitly for predictable, static query plan evaluation.
    """
    return (
        SparkSession.builder.appName("fhvhv-zone-analytics-optimized")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.autoBroadcastJoinThreshold", "10485760")  # 10 MB
        .getOrCreate()
    )

    # Optional cluster environment configuration template:
    # return (
    #     SparkSession.builder.appName("fhvhv-zone-analytics-optimized")
    #     .master("yarn")
    #     .config("spark.submit.deployMode", "cluster")
    #     .config("spark.driver.memory", "4g")
    #     .config("spark.driver.cores", 1)
    #     .config("spark.executor.memory", "10g")
    #     .config("spark.executor.cores", 2)
    #     .config("spark.executor.instances", 3)
    #     .config("spark.sql.adaptive.enabled", "false")
    #     .config("spark.sql.autoBroadcastJoinThreshold", "10485760")
    #     .getOrCreate()
    # )


def read_inputs(spark, args, logger):
    """
    Read source files and apply early column selection/renaming.
    
    Returns:
        tuple: (trips_pruned DataFrame, zones_pruned DataFrame)
    """
    logger.info("Reading trip parquet data from %s", args.trip_input)

    # Read Parquet using projection pushdown (pruned columns reduce disk I/O and memory usage)
    trips_pruned = spark.read.parquet(args.trip_input).select(*REQUIRED_TRIP_COLUMNS)

    logger.info("Reading taxi zone lookup from %s", args.zone_input)
    # Read CSV with explicit schema to avoid inferSchema performance penalties
    zones_pruned = (
        spark.read.option("header", "true")
        .schema(ZONE_SCHEMA)
        .csv(args.zone_input)
        .select(
            F.col("LocationID").alias("PULocationID"),
            F.col("Borough").alias("pickup_borough"),
            F.col("Zone").alias("pickup_zone"),
            F.col("service_zone"),
        )
    )

    return trips_pruned, zones_pruned


def build_optimized_analytics(trips_pruned, zones_pruned):
    """
    Apply data filtering, feature engineering, enrichment, and aggregations.
    
    Pipeline Steps:
        1. Clean and filter invalid records (narrow transformation).
        2. Derive calculated fields (date formats, duration, flags, total fare).
        3. Join trips with zones via Broadcast Join (wide transformation 1).
        4. Persist enriched data to disk/memory for multi-action reuse.
        5. Aggregate daily borough/platform metrics (wide transformation 2).
        6. Aggregate monthly pickup zone metrics (wide transformation 3).
        
    Returns:
        tuple: (enriched_trips, daily_borough_platform_metrics, monthly_zone_metrics)
    """

    # --- Step 1 & 2: Row-level filtering and column generation ---
    cleaned_trips = (
        trips_pruned.filter(F.col("pickup_datetime").isNotNull())
        .filter(F.col("dropoff_datetime").isNotNull())
        .filter(F.col("trip_miles") > F.lit(0))
        .filter(F.col("trip_time") > F.lit(0))
        .filter(F.col("base_passenger_fare") >= F.lit(0))
        .withColumn("trip_date", F.to_date("pickup_datetime"))
        .withColumn("trip_month", F.date_format("pickup_datetime", "yyyy-MM"))
        .withColumn("trip_duration_minutes", F.col("trip_time") / F.lit(60.0))
        .withColumn(
            "gross_trip_value",
            F.col("base_passenger_fare")
            + F.col("tolls")
            + F.col("bcf")
            + F.col("sales_tax")
            + F.col("congestion_surcharge")
            + F.col("airport_fee")
            + F.col("tips"),
        )
        .withColumn(
            "is_shared_trip",
            F.when(F.col("shared_request_flag") == F.lit("Y"), F.lit(1)).otherwise(
                F.lit(0)
            ),
        )
        .withColumn(
            "is_airport_trip",
            F.when(F.col("airport_fee") > F.lit(0), F.lit(1)).otherwise(F.lit(0)),
        )
    )

    # --- Step 3: Broadcast Hash Join ---
    # Broadcast small lookup table (`zones_pruned`) to avoid full network shuffle of `cleaned_trips`
    enriched_trips = cleaned_trips.join(
        F.broadcast(zones_pruned), on="PULocationID", how="left"
    ).persist(StorageLevel.MEMORY_AND_DISK)  # Cache result to support dual write actions efficiently

    # Common Expressions for Aggregations
    total_miles = F.sum("trip_miles")
    total_passenger_fare = F.sum("base_passenger_fare")
    fare_per_mile = F.when(
        total_miles != F.lit(0.0), total_passenger_fare / total_miles
    )

    # --- Step 4: Daily Borough/Platform Aggregations ---
    daily_borough_platform_metrics = enriched_trips.groupBy(
        "trip_date", "pickup_borough", "hvfhs_license_num"
    ).agg(
        F.count(F.lit(1)).alias("trip_count"),
        F.round(total_miles, 2).alias("total_miles"),
        F.round(F.sum("trip_duration_minutes"), 2).alias("total_trip_minutes"),
        F.round(total_passenger_fare, 2).alias("total_passenger_fare"),
        F.round(F.sum("driver_pay"), 2).alias("total_driver_pay"),
        F.round(fare_per_mile, 2).alias("avg_fare_per_mile"),
        F.round(F.avg("driver_pay"), 2).alias("avg_driver_pay_per_trip"),
        F.sum("is_shared_trip").alias("shared_trip_count"),
    )

    # --- Step 5: Monthly Pickup Zone Aggregations ---
    monthly_zone_metrics = enriched_trips.groupBy(
        "trip_month", "pickup_borough", "pickup_zone", "service_zone"
    ).agg(
        F.count(F.lit(1)).alias("trip_count"),
        F.round(F.sum("gross_trip_value"), 2).alias("total_gross_trip_value"),
        F.round(F.sum("tips"), 2).alias("total_tips"),
        F.round(F.sum("driver_pay"), 2).alias("total_driver_pay"),
        F.round(F.avg("trip_miles"), 2).alias("avg_trip_miles"),
        F.round(F.avg("trip_duration_minutes"), 2).alias("avg_trip_minutes"),
        F.sum("is_airport_trip").alias("airport_trip_count"),
        F.round(F.sum("congestion_surcharge"), 2).alias("total_congestion_surcharge"),
    )

    return enriched_trips, daily_borough_platform_metrics, monthly_zone_metrics


def write_outputs(enriched_trips, daily_metrics, monthly_metrics, output_base, logger):
    """
    Trigger Parquet writes for calculated metrics and release cached memory.
    """
    daily_output = f"{output_base.rstrip('/')}/daily_borough_platform_metrics"
    monthly_output = f"{output_base.rstrip('/')}/monthly_pickup_zone_metrics"

    # Action 1: Write daily metrics to Parquet (Triggers DAG computation & persists enriched_trips)
    logger.info("Writing daily borough/platform metrics to %s", daily_output)
    daily_metrics.write.mode("overwrite").parquet(daily_output)

    # Action 2: Write monthly metrics (Reuses persisted enriched_trips DataFrame, avoiding re-computation)
    logger.info("Writing monthly pickup zone metrics to %s", monthly_output)
    monthly_metrics.write.mode("overwrite").parquet(monthly_output)

    # Free persisted memory/disk resources after executing all downstream actions
    enriched_trips.unpersist()


def main():
    """Main execution entry point."""
    args = parse_args()
    logger = configure_logging()
    spark = build_spark(args)
    spark.sparkContext.setLogLevel("WARN")

    logger.info("Starting optimized FHVHV analytics job")
    logger.info("AQE enabled? %s", spark.conf.get("spark.sql.adaptive.enabled"))
    logger.info(
        "Shuffle partitions: %s", spark.conf.get("spark.sql.shuffle.partitions")
    )
    logger.info(
        "Auto broadcast join threshold: %s",
        spark.conf.get("spark.sql.autoBroadcastJoinThreshold"),
    )

    try:
        # Pipeline Execution
        trips_pruned, zones_pruned = read_inputs(spark, args, logger)
        enriched_trips, daily_metrics, monthly_metrics = build_optimized_analytics(
            trips_pruned, zones_pruned
        )
        write_outputs(
            enriched_trips, daily_metrics, monthly_metrics, args.output_base, logger
        )
        logger.info("Finished optimized FHVHV analytics job successfully")
    finally:
        # Gracefully terminate Spark session
        spark.stop()


if __name__ == "__main__":
    main()