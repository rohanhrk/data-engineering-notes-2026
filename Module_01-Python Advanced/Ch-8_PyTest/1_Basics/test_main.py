from main import weather_check

# Test cases for weather_check function
def test_weather_check():
    # assert means that the function should return this value for these inputs
    assert weather_check(35, 40) == "It's hot and dry." 
    assert weather_check(35, 60) == "It's hot and humid."
    assert weather_check(25, 40) == "It's cool and dry."
    assert weather_check(25, 60) == "It's cool and humid."

if __name__ == "__main__":
    test_weather_check()
