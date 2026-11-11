def weather_check(temperature):
    if temperature < 0:
        return "Freezing"
    elif 0 <= temperature < 10:
        return "Cold"
    elif 10 <= temperature < 20:
        return "Cool"
    elif 20 <= temperature < 30:
        return "Warm"
    else:
        return "Hot"