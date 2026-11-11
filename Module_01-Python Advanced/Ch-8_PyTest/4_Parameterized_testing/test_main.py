from main import weather_check
import pytest

@pytest.mark.parametrize(
    "temperature, expected_output",
    [
        (-5, "Freezing"),
        (5, "Cold"),
        (15, "Cool"),
        (25, "Warm"),
        (35, "Hot")
    ]
)
def test_weather_check(temperature, expected_output):
    assert weather_check(temperature) == expected_output

if __name__ == "__main__":
    pytest.main([__file__])