"""
This file is part of the Lambda LAYER.
It gets deployed separately and can be reused across multiple Lambda functions.
Lambda automatically makes this available under /opt/python/ at runtime.
"""


def celsius_to_fahrenheit(c):
    return round((c * 9 / 5) + 32, 2)


def fahrenheit_to_celsius(f):
    return round((f - 32) * 5 / 9, 2)


def km_to_miles(km):
    return round(km * 0.621371, 2)


def kg_to_pounds(kg):
    return round(kg * 2.20462, 2)