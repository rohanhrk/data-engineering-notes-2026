# Module 4 — Multi-Threading

**Source folder:** `Ch-4_Multi-Threading/`  
**Source file reviewed:** `1_multi-threading.py`.

## 1. What is a thread?

A thread is an execution path within a process. Threads in the same process share memory, which makes communication convenient but introduces synchronization concerns.

The repository uses `concurrent.futures.ThreadPoolExecutor` to fetch five example URLs. Each `fetch_data(url)` prints a start message, sleeps for five seconds to simulate I/O, prints completion, and returns a result.

## 2. ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_data(url):
    print("Fetching:", url)
    time.sleep(2)             # simulate waiting for I/O
    return f"Data from {url}"

urls = ["https://example.com/a", "https://example.com/b"]

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_data, urls))

print(results)
```

- `max_workers` controls the maximum number of worker threads.
- `executor.map(fn, iterable)` schedules work for each input and returns results in input order.
- `with` ensures the executor is shut down cleanly.
- In the repository, five workers are created for five URLs; tasks can wait concurrently rather than each sleeping sequentially.

## 3. Concurrency vs parallelism

- **Concurrency:** multiple tasks make progress during overlapping time periods.
- **Parallelism:** multiple tasks execute at the same instant, typically on multiple CPU cores.

Threads are particularly useful for I/O-bound work such as HTTP requests, file operations, and waiting on databases.

For CPU-bound Python work, threads may not provide speedup for pure Python code because of the Global Interpreter Lock (GIL) in standard CPython builds. Consider multiprocessing or native/vectorized libraries for CPU-heavy tasks.

## 4. Thread safety and synchronization

Because threads share memory, simultaneous updates can cause race conditions.

Tools include:
- `threading.Lock` to protect a critical section.
- `Event` for signalling.
- `Queue` for safe producer-consumer communication.

Avoid holding locks for long periods. Acquire/release safely with a context manager.

## 5. Error handling and practical improvements

`executor.map()` propagates task exceptions when the corresponding result is retrieved. For per-task control, use `submit()` and inspect each `Future`.

```python
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_data, url) for url in urls]
    for future in futures:
        try:
            result = future.result(timeout=15)
        except Exception as exc:
            print("Task failed:", exc)
```

For real HTTP ingestion, use a requests timeout, bounded worker count, retries with backoff, and rate-limit handling. Do not use `time.sleep()` as a substitute for a proper HTTP client timeout.

## 6. Threading vs asyncio vs multiprocessing

| Approach | Best fit | Key idea |
|---|---|---|
| Threading | Blocking I/O libraries | Multiple OS threads |
| asyncio | High-concurrency async I/O | Cooperative event-loop scheduling |
| Multiprocessing | CPU-bound work | Separate processes |

## 7. Data Engineering use cases

- Fetch multiple independent API endpoints.
- Download multiple files.
- Run independent blocking I/O tasks concurrently.
- Parallelize network-bound ingestion where the source permits it.

For large-scale pipelines, also consider service rate limits, connection pools, bounded concurrency, idempotency, and observability.

## 8. Common interview questions

1. **What is a thread?** An execution path within a process.
2. **When is threading useful?** Mostly I/O-bound tasks.
3. **What is the GIL?** A CPython mechanism that, in standard builds, limits simultaneous execution of Python bytecode by threads.
4. **What is a race condition?** Outcome depends on unpredictable timing of concurrent access.
5. **What does ThreadPoolExecutor do?** Manages a reusable pool of worker threads.
6. **Threading vs multiprocessing?** Threads share process memory; processes have separate address spaces and can execute CPU work in parallel.
7. **Threading vs asyncio?** Threads use OS scheduling; asyncio uses cooperative scheduling on an event loop.

## 9. Revision checklist

- [ ] Explain `ThreadPoolExecutor`, `max_workers`, and `executor.map`.
- [ ] Identify I/O-bound vs CPU-bound work.
- [ ] Explain GIL and race conditions.
- [ ] Describe a lock use case.
- [ ] Implement bounded concurrent API/file downloads.
