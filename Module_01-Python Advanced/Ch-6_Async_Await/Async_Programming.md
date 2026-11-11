# Module 6 — Asynchronous Programming

**Source folder:** `Ch-6_Async/`  
**Source files reviewed:** `1_basics.py`, `2_await_api.py`, `3_multiple_apis.py`, `4_multiple_tasks.py`.

## 1. Async fundamentals

`async def` defines a coroutine function. Calling it creates a coroutine object; it does not execute the body to completion immediately. `await` suspends the current coroutine until the awaited operation completes, allowing the event loop to run other ready tasks.

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(3)
    print("World")

asyncio.run(main())
```

`asyncio.run()` creates and manages an event loop for the top-level coroutine.

`asyncio.sleep()` is non-blocking. During the wait, the event loop can schedule other coroutines.

## 2. Awaiting a single asynchronous operation

`2_await_api.py` contrasts a blocking `time.sleep()` example (commented out) with an asynchronous API-like function using `await asyncio.sleep(3)`.

```python
async def api_call():
    await asyncio.sleep(3)
    return {"orders": []}

async def execute():
    result = await api_call()
    print(result)

asyncio.run(execute())
```

An async function must be awaited or scheduled as a task for its work to run. Forgetting `await` can leave a coroutine unexecuted and produce a runtime warning.

## 3. Running multiple APIs concurrently

`3_multiple_apis.py` uses `asyncio.gather()` to run three API-like coroutines with delays of 2, 3, and 1 seconds.

```python
results = await asyncio.gather(
    api_call("https://api1.example", 2),
    api_call("https://api2.example", 3),
    api_call("https://api3.example", 1),
)
```

The coroutines overlap while waiting. For independent I/O-bound calls, total elapsed time can be close to the longest individual delay rather than the sum, excluding overhead.

`gather()` returns results in the order of the awaitables supplied, not the order in which they finish. The source assigns the returned list to `tasks`; `results` would be a clearer variable name.

## 4. Important bug in `4_multiple_tasks.py`

This file demonstrates mixing an API coroutine with other tasks, but contains two important mistakes:

- `execution()` calls `time.sleep(5)`, which blocks the event-loop thread and prevents other coroutines from progressing during that period.
- `transformation()` calls `asyncio.sleep(4)` without `await`, so the sleep coroutine is not actually awaited; the intended delay does not happen.

Corrected version:

```python
import asyncio

async def api_call(url, delay=3):
    print("Fetching", url)
    await asyncio.sleep(delay)
    print("Fetched", url)

async def execution():
    await asyncio.sleep(5)
    print("Execution completed")

async def transformation():
    await asyncio.sleep(4)
    print("Transformation completed")

async def main():
    await asyncio.gather(
        api_call("https://api1.example"),
        execution(),
        transformation(),
    )

asyncio.run(main())
```

If a genuinely blocking function must be called from async code, use `asyncio.to_thread(blocking_function, args...)` where appropriate.

## 5. Coroutines, tasks, and event loop

- **Coroutine:** object representing an async computation.
- **Task:** wraps a coroutine and schedules it on the event loop.
- **Event loop:** coordinates ready coroutines and I/O events.
- **`await`:** yields control while waiting for an awaitable.
- **`asyncio.gather`:** runs multiple awaitables concurrently and collects results.

`asyncio.create_task(coro())` is useful when you want to schedule a coroutine and keep a task handle.

## 6. Async vs threading

| Asyncio | Threading |
|---|---|
| Cooperative scheduling | OS thread scheduling |
| Tasks yield at `await` points | Threads can be pre-empted |
| Excellent for async-compatible I/O | Useful with blocking I/O libraries |
| Usually one event-loop thread | Multiple threads share process memory |

Async is not automatically faster for CPU-heavy work. CPU-bound functions can block the event loop unless moved to an executor/process.

## 7. Data Engineering use cases

- Fetch many independent HTTP endpoints using an async HTTP client.
- Coordinate concurrent object-storage or service requests.
- Build high-concurrency I/O ingestion services.
- Use bounded concurrency and rate limiting to protect upstream APIs.

The repository simulates delays with `asyncio.sleep`; it does not implement real HTTP requests. A production example would use an async HTTP library such as `httpx.AsyncClient` or `aiohttp`.

## 8. Common interview questions

1. **What is a coroutine?** An awaitable computation defined with `async def`.
2. **Why use `await`?** It suspends the current coroutine and lets the event loop schedule other work.
3. **What does `asyncio.run()` do?** Runs a top-level coroutine using an event loop.
4. **What does `gather()` do?** Runs multiple awaitables concurrently and collects results.
5. **Does async mean parallel CPU execution?** No; it primarily provides concurrency through cooperative scheduling.
6. **Why is `time.sleep()` problematic in async code?** It blocks the event-loop thread.
7. **What happens if `asyncio.sleep()` is not awaited?** It creates a coroutine object but does not perform the intended wait.

## 9. Revision checklist

- [ ] Write and run a coroutine with `asyncio.run`.
- [ ] Explain why an async function needs `await` or task scheduling.
- [ ] Use `asyncio.gather` for multiple I/O operations.
- [ ] Explain the two bugs in source file 4.
- [ ] Compare asyncio, threading, and multiprocessing.
