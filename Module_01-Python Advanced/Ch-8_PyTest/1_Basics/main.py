def weather_check(temperature, humidity):
    if temperature > 30 and humidity < 50:
        return "It's hot and dry."
    elif temperature > 30 and humidity >= 50:
        return "It's hot and humid."
    elif temperature <= 30 and humidity < 50:
        return "It's cool and dry."
    else:
        return "It's cool and humid."