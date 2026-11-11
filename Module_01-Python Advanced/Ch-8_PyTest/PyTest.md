# Module 8 — Testing with Pytest

**Source folder:** `Ch-8_PyTest/`  
**Source files reviewed:** `main.py` and `test_main.py` in `1_Basics`, `2_Classes`, `3_CheckErrors`, `4_Parametrized_Testing`, and `Mocks`.

## 1. What is pytest?

Pytest is a Python testing framework. It discovers test files/functions by naming conventions, runs assertions, and reports failures.

Install and run:

```bash
pip install pytest pytest-mock
pytest Ch-8_PyTest/ -v
```

Typical conventions:
- Test files named `test_*.py` or `*_test.py`.
- Test functions named `test_*`.
- Use plain `assert` statements.

## 2. Basic function tests

`1_Basics/main.py` defines `weather_check(temp)` and returns a message for four temperature ranges. `test_main.py` imports it and checks representative values using assertions.

```python
def test_weather_check():
    assert weather_check(-5) == "It's freezing outside!"
    assert weather_check(10) == "It's a bit chilly."
```

A test passes if the expression is true; otherwise pytest reports the expected and actual values.

## 3. Testing class methods

`2_Classes/main.py` defines a `weather` class with `weather_check()` and `rain_check()` methods. The test creates an instance and checks both methods.

```python
def test_rain_check():
    instance = weather()
    assert instance.rain_check(0.8) == (
        "It's likely to rain. Don't forget your umbrella!"
    )
```

Each test should arrange its inputs, execute the behaviour, and assert the outcome. This is often called Arrange–Act–Assert.

## 4. Testing exceptions

`3_CheckErrors/main.py` adds `divide(a, b)` and raises `ValueError` when `b == 0`.

```python
import pytest

def test_divide_by_zero():
    instance = weather()
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        instance.divide(10, 0)
```

`pytest.raises()` verifies both that the expected exception is raised and, optionally, that its message matches.

## 5. Parametrized testing

`4_Parametrized_Testing/test_main.py` uses `@pytest.mark.parametrize` to run the same test with several input/expected-output pairs.

```python
import pytest

@pytest.mark.parametrize(
    "temp, expected",
    [
        (-5, "It's freezing outside!"),
        (10, "It's a bit chilly."),
        (20, "The weather is pleasant."),
        (30, "It's hot outside!"),
    ],
)
def test_weather_check(temp, expected):
    assert weather_check(temp) == expected
```

This reduces repetitive test code and makes it easy to add boundary cases.

For the temperature logic, add tests at exact boundaries: `0`, `15`, and `25`, because the implementation uses `<` comparisons.

## 6. Mocking external dependencies

`Mocks/main.py` defines `api_call(url)` that calls `requests.get(url)` and returns `{"data": response.json()}`.

The test uses the `mocker` fixture from `pytest-mock`:

```python
def test_api_call(mocker):
    mock_get = mocker.patch("main.requests.get")
    mock_get.return_value.json.return_value = {
        "main": {"key": "value"}
    }

    result = api_call("https://example.com/weather")
    assert result == {"data": {"main": {"key": "value"}}}
```

A mock replaces a real dependency so the test does not call the external service. This makes tests faster, deterministic, and independent of network availability.

The test can be strengthened by asserting `requests.get` was called with the expected URL and by testing error responses/timeouts.

## 7. Test quality and best practices

- Test normal, boundary, invalid, and exceptional inputs.
- Keep unit tests isolated from network and real external services.
- Use fixtures for shared setup.
- Use mocks for external dependencies, but do not mock the function's own core logic.
- Test observable behaviour rather than private implementation details.
- Keep tests deterministic and fast.
- Avoid unnecessary print statements in production modules; importing a module should not unexpectedly execute application work.

## 8. Data Engineering testing examples

Test:
- Transformation functions with small input DataFrames.
- Schema and null constraints.
- Duplicate handling and deduplication.
- Date parsing and timezone conversion.
- API client error handling using mocks.
- Incremental watermark logic.
- Aggregation totals and reconciliation rules.

For Spark pipelines, use small deterministic fixtures and compare expected DataFrames, including schema and row content.

## 9. Common interview questions

1. **What is pytest?** A framework for discovering and running Python tests.
2. **How does pytest discover tests?** Through file/function naming conventions and configured patterns.
3. **What is an assertion?** A condition that must be true for the test to pass.
4. **How do you test exceptions?** `pytest.raises()`.
5. **What is parametrization?** Running one test function with multiple input sets.
6. **What is mocking?** Replacing a dependency with a controlled test double.
7. **Why mock API calls?** Avoid network dependency, latency, cost, and nondeterministic responses.
8. **What is a unit test?** A focused test of a small unit of behaviour in isolation.

## 10. Revision checklist

- [ ] Run pytest on a test folder.
- [ ] Write tests for a function and a class.
- [ ] Test a raised exception with `pytest.raises`.
- [ ] Parametrize boundary-value tests.
- [ ] Mock `requests.get`.
- [ ] Explain unit tests vs integration tests.
