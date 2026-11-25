# AWS Glue job-bookmark demonstration

This example demonstrates how an AWS Glue job bookmark prevents previously
processed S3 CSV files from being read again. The job does not transform or
write the records. It only logs each file read during the current run and the
number of records found in that file.

## Included batches

| Upload order | File | Records |
| --- | --- | ---: |
| 1 | `transactions_2026_10_01.csv` | 75 |
| 2 | `transactions_2026_10_02.csv` | 120 |
| 3 | `transactions_2026_10_03.csv` | 55 |

The folders named `batch_1`, `batch_2`, and `batch_3` represent separate upload
steps. Upload the files themselves into the same S3 source prefix.

## 1. Create the S3 source

Create an initially empty prefix such as:

```text
s3://YOUR-BUCKET/glue-bookmark-demo/transactions/
```

Upload only the first file:

```text
data/batch_1/transactions_2026_10_01.csv
```

The resulting object should be:

```text
s3://YOUR-BUCKET/glue-bookmark-demo/transactions/transactions_2026_10_01.csv
```

Do not upload all three files before the first run. If you do, Glue correctly
treats all three as new files and processes all of them together.

## 2. Create the crawler

Create and run a Glue crawler with:

- S3 source: `s3://YOUR-BUCKET/glue-bookmark-demo/transactions/`
- Target database: for example, `banking_raw`
- Resulting table: for example, `transactions`

Confirm that the Catalog table location is the parent `transactions/` prefix,
not the individual CSV object. Because subsequent files use the same schema and
are placed under that table location, rerunning the crawler is not required for
this demonstration.

## 3. Create the Glue job

Upload `glue_job_bookmark_demo.py` and create a Glue Spark job. Add these job
parameters:

| Key | Example value |
| --- | --- |
| `--SOURCE_DATABASE` | `banking_raw` |
| `--SOURCE_TABLE` | `transactions` |
| `--job-bookmark-option` | `job-bookmark-enable` |

`--JOB_NAME` is supplied automatically by Glue.

The following three pieces must remain in the script:

- `job.init(job_name, args)` loads the existing bookmark state.
- `transformation_ctx="bank_transactions_bookmark_source"` identifies the
  source inside that state. Do not rename it between runs.
- `job.commit()` saves bookmark progress after a successful run.

## 4. Demonstrate bookmark behavior

### Run 1

With only the first CSV uploaded, run the job. The logs should contain:

```text
File read: transactions_2026_10_01.csv | Records: 75
Total records read in this run: 75
```

### Run 2 without uploading anything

Run the same Glue job again. The logs should contain:

```text
No new files were read; the bookmark is up to date
```

### Run 3 after uploading batch 2

Upload `data/batch_2/transactions_2026_10_02.csv` into the same S3 prefix and
run the job again. The job should report only:

```text
File read: transactions_2026_10_02.csv | Records: 120
Total records read in this run: 120
```

### Run 4 after uploading batch 3

Upload `data/batch_3/transactions_2026_10_03.csv` and run the job again. The
job should report only that file and its 55 records.

## Important behavior

- S3 bookmarks track files by object last-modified time, not by transaction ID.
- Uploading or modifying an old filename after a successful run changes its
  last-modified time, so Glue can process that object again.
- Bookmark state belongs to the Glue job name. Creating a different Glue job
  starts with different bookmark state.
- Disabling bookmarks makes every run read every file.
- Resetting the bookmark in the Glue console makes the job eligible to process
  the existing source files again.

The official behavior is documented in [Tracking processed data using job
bookmarks](https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html).
