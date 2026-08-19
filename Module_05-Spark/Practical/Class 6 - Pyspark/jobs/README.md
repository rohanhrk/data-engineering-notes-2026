## Spark Submit To Run Optimized Spark Job

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --conf spark.dynamicAllocation.enabled=false \
  --driver-memory 5g \
  --driver-cores 1 \
  --executor-memory 4g \
  --executor-cores 2 \
  --num-executors 3 \
  --conf spark.sql.shuffle.partitions=50 \
  fhvhv_zone_analytics_optimized.py \
  --trip-input   s3://spark-file-storage/spark-learning/rides/tripdata/*.parquet \
  --zone-input   s3://spark-file-storage/spark-learning/rides/tripzone/taxi_zone_lookup.csv \
  --output-base  s3://spark-file-storage/spark-learning/rides/optimized
```