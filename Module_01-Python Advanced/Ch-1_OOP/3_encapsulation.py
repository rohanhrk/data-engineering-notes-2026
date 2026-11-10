# Define Class
class MyFirstClass:
    # Class Variables
    var1 = "Rohan"
    var2 = "Hazarika"

    # Instance Variables
    def __init__(self, dyn1, dyn2, dyn3):
        self.dyn1 = dyn1
        self._dyn2 = dyn2
        self.__dyn3 = dyn3

    def func1(self):
        print(f"Hello World, {self.dyn1}")
    
    def func2(self):
        print(f"Hello Globe, {self._dyn2}")
         
    def func3(self):
        print(f"Hello Globe, {self.__dyn3}")

# Create Object
obj = MyFirstClass("abc", "xyz", "pqr")
obj.dyn1 = "def"
print(obj.dyn1)
obj.func1()


"""
    It will print "xyz" because _dyn3 is a protected variable and 
    it can be accessed outside the class but it is not recommended to do so. 
    It is just a convention to use _ before the variable name to indicate that 
    it is a protected variable and it should not be accessed outside the class.
"""
print(obj._dyn2)

"""
    This will not give error but it will create a new variable __dyn3 in the object and 
    assign the value "roh" to it. It will not change the value of __dyn3 which is a private variable.
"""
 
obj.__dyn3 = "roh"
print(obj.__dyn3)

# It will print "Hello Globe, pqr" because the value of __dyn3 is still "pqr" and it is not changed by obj.__dyn3 = "stu" statement.
obj.func3()