class division:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def divide(self):
        if self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self.a / self.b
