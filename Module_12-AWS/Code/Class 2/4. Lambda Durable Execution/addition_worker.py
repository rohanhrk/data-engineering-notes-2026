"""Lambda B: a regular Lambda. Handler: addition_worker.perform_addition."""

import time


def perform_addition(event, context):
    """Simulate a slow task, add two integers, and return the result to AWS."""
    # This is an ordinary Lambda handler: no durable decorator or SDK required.
    # event is the payload passed by Lambda A's context.invoke(...).
    # context is the standard Lambda context; this demo does not need to use it.
    job_id = event["job_id"]
    a = event["a"]
    b = event["b"]
    if type(a) is not int or type(b) is not int:
        raise ValueError("a and b must be integers")

    print(f"B: Work started for {job_id}", flush=True)
    print("B: Simulating a 20-second task", flush=True)

    # DEMO ONLY: make the pause visible during the presentation. This sleep
    # keeps B running and incurs B's compute charges. A is suspended separately
    # by context.invoke(). Real applications would do useful work here.
    time.sleep(120)

    result = a + b
    print(f"B: Work completed: {a} + {b} = {result}", flush=True)

    # A plain dictionary is sufficient. AWS delivers this result to the durable
    # invoke operation and resumes A; B does not invoke A or send a callback.
    return {"job_id": job_id, "result": result}
