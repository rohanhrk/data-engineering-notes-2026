"""Set the AWS Lambda handler to lambda_function.lambda_handler.

Example test event: {"name": "Alex", "a": 3, "b": 4}
An empty test event ({}) also works using the defaults below.
"""

import json
from helpers.functions import add_numbers, greet, square

def lambda_handler(event, context):
    name = event.get("name", "World")
    a = event.get("a", 2)
    b = event.get("b", 3)

    result = {
        "greeting": greet(name),
        "sum": add_numbers(a, b),
        "square_of_a": square(a)
    }

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }