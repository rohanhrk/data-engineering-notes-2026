# SNS Learning

This example shows a single Lambda function that is triggered by an S3 object creation event and sends a status notification to an SNS topic.

## What This Lambda Does

1. Receives an S3 `ObjectCreated` event
2. Parses the event to extract:
   - bucket name
   - object key
   - event name
   - event time
   - AWS region
3. Sends an SNS notification with subject `Success` if parsing works
4. Sends an SNS notification with subject `Failed` if an exception happens

## Files

- `lambda_function.py` -> Lambda code
- `test_event.json` -> sample S3 event for Lambda testing

## Required Lambda Environment Variable

Add this environment variable in the Lambda configuration:

```text
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:your-topic-name
```

## Required IAM Permissions

The Lambda execution role needs permission to publish to SNS:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789012:your-topic-name"
    }
  ]
}
```

## How to Test

1. Create an SNS topic
2. Subscribe an email endpoint to the topic
3. Create the Lambda function
4. Add the `SNS_TOPIC_ARN` environment variable
5. Attach the `sns:Publish` IAM permission to the Lambda role
6. Add an S3 trigger to the Lambda
7. Use `test_event.json` in the Lambda test console, or upload a file to S3

## Example Behavior

Success notification subject:

```text
Success
```

Failure notification subject:

```text
Failed
```
