# Module 9 — OS and File Operations

**Source folder:** `Ch-9_OS/`  
**Source file reviewed:** `1_basics.py`; sample files are in `Data/`.

## 1. Python `os` module

The `os` module provides operating-system interfaces for working with directories, paths, environment variables, and file metadata.

The source contains examples (commented out) of:
- `os.getcwd()` — current working directory.
- `os.path.abspath(__file__)` — absolute path to the current Python file.
- `os.path.dirname(...)` — parent directory of a path.
- `os.listdir()` — entries in a directory.
- `os.path.isfile(path)` — checks whether a path is a file.
- `os.path.isdir(path)` — checks whether a path is a directory.

## 2. Building paths safely

The source uses:

```python
os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Data"
)
```

This builds a path to the `Data` folder relative to the script, rather than depending on the shell's current working directory.

For new Python code, `pathlib` is often clearer:

```python
from pathlib import Path

script_dir = Path(__file__).resolve().parent
data_dir = script_dir / "Data"

for path in data_dir.iterdir():
    if path.is_file():
        print(path.name)
```

## 3. Incremental file processing example

The source sets `last_load = "2026-01-14"` and iterates over files in `Data/`. It compares the filename stem with the watermark and prints a message for newer files.

```python
last_load = "2026-01-14"

for file_name in os.listdir(data_dir):
    file_date = file_name.split(".")[0]
    if file_date > last_load:
        print(f"Processing {file_name} new file")
```

This works as a simple demonstration because ISO date strings (`YYYY-MM-DD`) sort lexicographically in chronological order, provided they are consistently formatted.

**Important limitations:**
- It assumes every directory entry is a date-named file.
- It does not check the extension or parse the date.
- It does not actually process or persist the data.
- It does not update the watermark after successful processing.
- A production pipeline needs idempotency and failure recovery.

Safer date parsing:

```python
from datetime import date
from pathlib import Path

last_load = date.fromisoformat("2026-01-14")

for path in data_dir.glob("*.csv"):
    file_date = date.fromisoformat(path.stem)
    if file_date > last_load:
        print(f"Process {path.name}")
```

## 4. A robust incremental file-processing pattern

1. Identify candidate files using a controlled naming pattern.
2. Parse and validate the date/partition from the filename.
3. Compare with the persisted watermark or processed-file manifest.
4. Process the file.
5. Validate row counts/schema and write output.
6. Record successful processing.
7. Advance the watermark only after the write succeeds.

Do not update the watermark before processing completes; otherwise a failed file can be skipped on the next run.

## 5. Useful file operations

```python
from pathlib import Path

path = Path("data/orders.csv")

path.exists()
path.is_file()
path.suffix
path.name
path.parent
path.stat().st_size
```

Use context managers for file handles:

```python
with open("sample.txt", "r", encoding="utf-8") as file:
    content = file.read()
```

For tabular formats, use pandas readers (`read_csv`, `read_json`, `read_parquet`) where appropriate.

## 6. Data Engineering applications

- Discover new files in landing directories.
- Process date-partitioned files incrementally.
- Validate file extensions, sizes, and naming conventions.
- Archive or move processed files.
- Build repeatable ingestion jobs that survive restarts.

## 7. Common interview questions

1. **`os.getcwd()` vs `__file__`?** Current process working directory vs the path of the current script.
2. **Why use `os.path.join` or `pathlib`?** To construct paths portably.
3. **How do you list directory entries?** `os.listdir()` or `Path.iterdir()`.
4. **How do you check whether a path is a file?** `os.path.isfile()` or `Path.is_file()`.
5. **Why are ISO date strings sortable?** Fixed-width year-month-day components sort in chronological order lexicographically.
6. **What is a watermark?** A persisted position/date indicating how far incremental processing has successfully progressed.
7. **When should a watermark advance?** Only after the corresponding data has been processed and committed successfully.

## 8. Revision checklist

- [ ] Explain working directory vs script directory.
- [ ] Build paths using `pathlib`.
- [ ] List and filter files in a directory.
- [ ] Parse date-based filenames.
- [ ] Explain watermark and idempotency.
- [ ] Describe how to recover from a failed file load.
