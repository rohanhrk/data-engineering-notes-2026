# Durable Lambda calls a worker, suspends, and resumes

Lambda A prepares an addition task, invokes Lambda B, and suspends. B simulates 20 seconds of work and returns `10 + 20 = 30`. A resumes with that result and completes. The Python files include comments explaining every decorator and durable operation.

```text
Lambda A: prepare-task
        |
        v
context.invoke(B) -----> Lambda B: sleep 20 seconds, add numbers
        |                           |
   A suspended                      |
        |                           v
        +<------------------- return result: 30
        |
        v
Lambda A: finish-task --> COMPLETED
```

## Files and handlers

| Lambda | Source | Handler | ZIP |
| --- | --- | --- | --- |
| A: durable coordinator | `workflow_coordinator.py` | `workflow_coordinator.run_workflow` | `coordinator-deployment.zip` |
| B: regular worker | `addition_worker.py` | `addition_worker.perform_addition` | `worker-deployment.zip` |

`test_event.json` starts A. There is one README for the entire example.

## 1. Deploy worker B first

Use one AWS account and Region for both functions.

1. Create a regular Lambda named **durable-demo-worker**, using **Python 3.13** and **x86_64**. Leave durable execution disabled for B.
2. Upload `worker-deployment.zip` under **Code → Upload from → .zip file**.
3. Set its handler to `addition_worker.perform_addition` under **Runtime settings**.
4. Set memory to **128 MB** and timeout to **60 seconds**. The default three-second timeout is too short for the simulated task.
5. Keep the execution role's **AWSLambdaBasicExecutionRole** logging permissions.
6. Publish a version and copy its qualified ARN, including the version number. For example: `arn:aws:lambda:ap-south-1:123456789012:function:durable-demo-worker:1`.

Publishing B makes the demo use a fixed worker implementation. B needs no permission to invoke A.

## 2. Deploy durable coordinator A

1. Create a Lambda named **durable-demo-coordinator**, using **Python 3.13** and **x86_64**, with **Enable durable execution** selected at creation.
2. Upload `coordinator-deployment.zip` and set its handler to `workflow_coordinator.run_workflow`.
3. Use **128 MB** memory and a **30-second** function timeout. Set the **durable execution timeout** to **5 minutes (300 seconds)** so the whole workflow has time to complete. These are separate settings: the function timeout applies to an individual invocation.
4. Under **Configuration → Environment variables**, set `WORKER_FUNCTION_ARN` to B's qualified ARN from step 1.

The managed Python runtime supplies the Durable Execution SDK for this console demo; the ZIP contains only the application code. See the [supported runtimes and SDK packaging guidance](https://docs.aws.amazon.com/lambda/latest/dg/durable-supported-runtimes.html). For a production deployment, package a pinned SDK version with your application.

### Coordinator permissions

A's execution role needs **AWSLambdaBasicDurableExecutionRolePolicy**, which supplies checkpoint/state and CloudWatch logging permissions. The console can create this role when durable execution is enabled. Verify it under **Configuration → Permissions**. See [AWS durable security guidance](https://docs.aws.amazon.com/lambda/latest/dg/durable-security.html).

Also add this inline policy to **A's execution role**, replacing the example ARN with the exact qualified ARN in `WORKER_FUNCTION_ARN`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:ap-south-1:123456789012:function:durable-demo-worker:1"
    }
  ]
}
```

After saving the code, environment variable, and settings, **publish a version of A**. Run the published version for the demonstration. Publish a new version after subsequent changes and select it for the next run. AWS's [console getting-started guide](https://docs.aws.amazon.com/lambda/latest/dg/durable-getting-started.html) covers durable creation, version publishing, and the execution view.

## 3. Run the presentation

1. Open the published version of **durable-demo-coordinator**.
2. Create a console test event using `test_event.json`:

   ```json
   {"job_id": "demo-001", "a": 10, "b": 20}
   ```

3. Run the test once, then open **Durable executions** and select that execution.
4. Point out `prepare-task`, the pending `call-worker` operation, and then `finish-task` after B returns. The overall execution remains in progress while A is suspended; suspension is not a terminal **Stopped** status. Do not click **Stop execution**.
5. Open the CloudWatch log groups for A and B to show their print statements. Each function has its own log group; A's resumed invocation may use another log stream. Search across streams for `demo-001` and allow for log-delivery delay.

Expected business messages, shown below in logical order across both functions:

```text
A: Workflow started for demo-001
A: Prepared task: add 10 and 20
A: Calling Lambda B next; I will suspend until its result is ready

B: Work started for demo-001
B: Simulating a 20-second task
... about 20 seconds of simulated work ...
B: Work completed: 10 + 20 = 30

A: Resumed; Lambda B returned 30
A: Workflow completed for demo-001
```

The final workflow output is:

```json
{"job_id": "demo-001", "status": "COMPLETED", "result": 30}
```

## Explain the four key pieces of code

| Code | Purpose in this demo |
| --- | --- |
| `@durable_execution` | Wraps A's entry point so the SDK handles durable execution and supplies `DurableContext`. |
| `@durable_step` | Wraps a helper so it can be passed to `context.step()`. The SDK supplies the helper's first argument, `step_context`. |
| `context.step(prepare_task(event), name="prepare-task")` | Executes preparation and checkpoints its returned data. The decorated `prepare_task(event)` builds the callable; `context.step` manages execution. |
| `context.invoke(worker_arn, payload, name="call-worker")` | Requests B's invocation, suspends A, and supplies B's saved result when A resumes. |

The step helper signatures and their calls look different because the SDK supplies `step_context`; callers pass only business arguments. See the [step operation reference](https://docs.aws.amazon.com/durable-execution/sdk-reference/operations/step/).

Resuming starts another invocation of A and replays its handler from the beginning. Completed operations return their saved results. Consequently, A's successfully checkpointed preparation prints do not run again during normal replay, and B is not invoked again just because A resumes. Code outside durable operations does execute again. See the [durable invoke lifecycle](https://docs.aws.amazon.com/durable-execution/sdk-reference/operations/invoke/).

B's `time.sleep(20)` is only a visible stand-in for slow work and consumes B's compute time. A's durable suspension consumes no compute while it waits. B simply returns a dictionary; AWS handles resuming A without custom callback code. Failures before checkpointing may cause retries, so real external writes still need idempotency.

## Rebuild the two ZIP files

From the class working directory:

```bash
cd Lambda-Durable-Invoke-Example
python3 -m zipfile -c coordinator-deployment.zip workflow_coordinator.py
python3 -m zipfile -c worker-deployment.zip addition_worker.py
```

Each ZIP has its own Python file at the root. Neither ZIP requires pandas or a layer.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Worker times out | B must have a timeout longer than its 20-second simulated task; use 60 seconds. |
| `AccessDenied` calling B | A's role must allow `lambda:InvokeFunction` on the exact ARN, including version, used in its environment variable. |
| Missing `WORKER_FUNCTION_ARN` | Add the variable to A and publish/select a new version. |
| Checkpoint/state permission error | Check A's durable execution role policy. |
| Cannot import SDK / durable execution error | Confirm A was created with durable execution enabled and uses a supported managed Python runtime. |
| Handler not found | Match the handler to the file and function names in the table above. |
| No resumed message | Check `call-worker` and B's logs for failure. A cannot execute the finishing step if B fails. |

This folder prepares the demo; creating and running the AWS functions is a separate deployment step.
