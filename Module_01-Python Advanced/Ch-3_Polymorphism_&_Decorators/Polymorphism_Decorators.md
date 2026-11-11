# Module 3 — Polymorphism and Decorators

**Source folder:** `Ch-3_Polymorphism&Decorators/`  
**Source files reviewed:** `1_polymorphism.py`, `2_decorators.py`, `3_decorator_pandas.py`, `orders.csv`; the generated Parquet file is a binary output artifact.

## 1. Polymorphism

Polymorphism means “many forms”: different objects can respond to the same method call in their own way.

The source defines `api_fetch`, `database_fetch`, and `s3_fetch`, each with a `fetch()` method. The same call works with any of them:

```python
class ApiFetcher:
    def fetch(self):
        return "Fetching from API"

class DatabaseFetcher:
    def fetch(self):
        return "Fetching from database"

class S3Fetcher:
    def fetch(self):
        return "Fetching from object storage"

def run_ingestion(source):
    return source.fetch()
```

Python commonly uses **duck typing**: if an object supports the required operation, code can use it without requiring a specific declared parent class.

### Why it matters

A pipeline can accept multiple source implementations behind a common interface. This makes source integrations easier to extend.

## 2. Function decorators

A decorator takes a function, wraps or modifies its behaviour, and returns a callable.

The source `2_decorators.py` defines `my_decorator(fx)`, an inner `mainfunc(*args)`, and applies it using `@my_decorator`.

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Starting function")
        result = func(*args, **kwargs)
        print("Finished function")
        return result
    return wrapper

@log_call
def fetch_data(url, path):
    return f"Fetched {url} to {path}"
```

`@log_call` is equivalent to `fetch_data = log_call(fetch_data)`.

- `*args` collects positional arguments.
- `**kwargs` collects keyword arguments.
- `@wraps(func)` preserves useful metadata such as the original function name and docstring.
- Returning `result` preserves the wrapped function's output.

The repository's wrapper accepts `*args` but not `**kwargs`; adding both makes it more general.

## 3. Decorator for a pandas transformation

`3_decorator_pandas.py` defines a decorator that runs a function, writes the returned DataFrame to Parquet, then returns the DataFrame. The decorated function reads a CSV with pandas.

Flow:

1. Call `csv_to_parquet(file_path)`.
2. Read CSV into a DataFrame.
3. Wrapper receives the DataFrame.
4. Save it with `to_parquet(...)`.
5. Return the DataFrame to the caller.

This demonstrates separating cross-cutting behaviour (saving output) from the core transformation function.

**Production improvements:**
- Use `pathlib.Path` or `os.path.join` instead of hard-coded Windows-style paths.
- Make the output path configurable.
- Add logging and exception handling.
- Avoid silently overwriting output unless intended.
- Add tests for both the transformation and file-writing behaviour.

## 4. Decorator use cases in data engineering

- Logging pipeline start/end and execution duration.
- Retrying transient API failures.
- Validating input arguments.
- Measuring performance.
- Recording audit metadata.
- Saving or checkpointing outputs.

Be careful with retries: retry only safe operations and use bounded attempts/backoff. A retry around a non-idempotent write can duplicate data.

## 5. Common interview questions

1. **What is polymorphism?** Different implementations respond to the same interface or method call.
2. **What is duck typing?** Suitability is based on supported behaviour rather than explicit type inheritance.
3. **What is a decorator?** A callable that wraps or transforms another callable.
4. **What does `@decorator` mean?** It is syntactic sugar for assigning the decorated function to the decorator's returned callable.
5. **Why use `*args` and `**kwargs`?** To forward arbitrary positional and keyword arguments.
6. **Why use `functools.wraps`?** To preserve metadata from the original function.
7. **Give a pipeline use case.** A decorator can log runtime or retry transient API calls.

## 6. Revision checklist

- [ ] Explain duck typing using the three fetcher classes.
- [ ] Write a decorator from memory.
- [ ] Explain `*args`, `**kwargs`, and `functools.wraps`.
- [ ] Trace the CSV-to-Parquet decorator flow.
- [ ] Describe safe retry and logging use cases.
