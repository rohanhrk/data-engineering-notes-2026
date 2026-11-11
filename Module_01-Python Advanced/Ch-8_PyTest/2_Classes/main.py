class Weather:
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def check_weather(self):
        if self.temperature > 30 and self.humidity < 50:
            return "It's hot and dry."
        elif self.temperature > 30 and self.humidity >= 50:
            return "It's hot and humid."
        elif self.temperature <= 30 and self.humidity < 50:
            return "It's cool and dry."
        else:
            return "It's cool and humid."