"""Lambda A: prepare a task, suspend while Lambda B works, then finish.

Handler: workflow_coordinator.run_workflow
Enable durable execution on this Lambda and set WORKER_FUNCTION_ARN.
"""

import os

from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)

# A decorator (the @ line) wraps a function to give it extra behavior.
# @durable_step makes this helper usable by context.step(). Calling
# prepare_task(event) builds a step callable; context.step(...) executes it.
# A successfully checkpointed result is reused during replay.
@durable_step
def prepare_task(step_context, event):
    """Do the work that should complete before we call Lambda B."""
    # The SDK supplies step_context automatically. It offers a step logger
    job_id = event["job_id"]
    a = event["a"]
    b = event["b"]
    if type(a) is not int or type(b) is not int:
        raise ValueError("a and b must be integer")
    
    print(f"A: workflow started for {job_id}", flush=True)
    print(f"A: Prepared task: add {a} and {b}", flush=True)
    print("A: Calling Lambda B next; I will suspend until its result is ready", flush=True)

    # Return data needed later: return values are checkpointed, local mutations
    # are not. Reading configuration here also saves it with this step's result.
    return {
        "worker_arn": os.environ["WORKER_FUNCTION_ARN"],
        "payload": {"job_id": job_id, "a": a, "b": b},
    }

@durable_step
def finish_task(step_context, worker_result):
    """Run only after the durable invoke has supplied Lambda B's result."""
    print(f"A: Resumed; Lambda B returned {worker_result['result']}", flush=True)
    print(f"A: Workflow completed for {worker_result['job_id']}", flush=True)
    return {
        "job_id": worker_result["job_id"],
        "status": "COMPLETED",
        "result": worker_result["result"],
    }

# @durable_execution wraps the Lambda entry point. It handles the durable
# execution protocol and gives our code a DurableContext for checkpoints/replay.
# The decorator alone is not enough: enable durable execution in AWS as well.
@durable_execution
def run_workflow(event, context: DurableContext):
    """Coordinate two durable steps and one durable Lambda invocation."""
    # `context: DurableContext` is a type hint, not a constructor call.
    # It describes the object the decorator supplies. Python needs no `await`
    # here: the SDK exposes synchronous-looking durable operations.

    # 1. The decorator binds event to the helper's event parameter; the SDK
    # supplies step_context. The name labels the operation in execution history.
    prepared = context.step(prepare_task(event), name="prepare_task")

    # 2. This is the suspension point. AWS records the invoke operation and
    # invokes the separate Lambda B. Lambda A's current invocation ends while
    # B works; A consumes no compute during this wait.

    # When B returns, AWS saves its result and starts another invocation of A.
    # A replays from the top: the completed prepare step returns its saved data,
    # and this invoke returns B's saved result. B is not called again merely
    # because A replays. This needs no sleep, polling loop, or callback code in A.
    worker_result = context.invoke(
        prepared["worker_arn"],     # Which deployed lambda shoud run
        prepared["payload"],        # JSON-serializable input for lambda B
        name="call-worker"          # Label shown in durable execution history
    )


    # 3. Continue here with B's result. Keeping prints inside steps prevents
    # ordinary replay from reprinting already-completed business steps.
    # A failure before a checkpoint is saved can still cause a step to retry;
    # durable execution is not a promise of exactly-once external side effects.
    return context.step(finish_task(worker_result), name="finish-task")
