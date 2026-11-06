"""Small helper functions called by the Lambda handler."""


def greet(name):
    return f"Hello, {name}!"


def add_numbers(a, b):
    return a + b


def square(number):
    return number * number