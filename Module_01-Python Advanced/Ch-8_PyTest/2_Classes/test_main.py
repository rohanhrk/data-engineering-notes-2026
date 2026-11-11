from main import Weather

def test_weather_check():
    # Test cases for Weather class
    weather1 = Weather(35, 40)
    assert weather1.check_weather() == "It's hot and dry."

    weather2 = Weather(35, 60)
    assert weather2.check_weather() == "It's hot and humid."

    weather3 = Weather(25, 40)
    assert weather3.check_weather() == "It's cool and dry."

    weather4 = Weather(25, 60)
    assert weather4.check_weather() == "It's cool and humid."

if __name__ == "__main__":
    test_weather_check()