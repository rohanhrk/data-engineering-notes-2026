import json
from utils import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    km_to_miles,
    kg_to_pounds,
)

def lambda_handler(event, context):
    """
    Lambda function that uses a LAYER for unit conversions.
    The 'utils' module comes from the attached Lambda Layer, not from this zip.
    """
    print("Event received:", json.dumps(event))

    value = event.get("value", 0)
    conversion = event.get("conversion", "celsius_to_fahrenheit")

    conversions = {
        "celsius_to_fahrenheit": ("Celsius", "Fahrenheit", celsius_to_fahrenheit),
        "fahrenheit_to_celsius": ("Fahrenheit", "Celsius", fahrenheit_to_celsius),
        "km_to_miles": ("Kilometers", "Miles", km_to_miles),
        "kg_to_pounds": ("Kilograms", "Pounds", kg_to_pounds),
    }

    if conversion not in conversions:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": f"Unknown conversion: {conversion}",
                "available": list(conversions.keys()),
            }),
        }

    from_unit, to_unit, func = conversions[conversion]
    result = func(value)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "input": f"{value} {from_unit}",
            "output": f"{result} {to_unit}",
            "conversion_type": conversion,
        }),
    }
