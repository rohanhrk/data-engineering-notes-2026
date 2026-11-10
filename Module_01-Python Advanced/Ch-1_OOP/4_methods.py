class MyClass:
    my_var = 100

    # dunder method or magic method
    def __init__(self):
        print("This is the constructor method")

    # Dunder method for str
    def __str__(self):
        return "This is the string representation of the object"
    
    @classmethod
    def _change_value(cls, new_value):
        cls.my_var = new_value
    
    @staticmethod
    def dummy():
        print("This is a static method")
    
obj = MyClass()
print(obj)
print(obj.my_var)

obj._change_value(200)
print(obj.my_var)

obj2 = MyClass()
print(obj2.my_var)

obj3 = MyClass()
obj3.dummy()


