# Module 1 — Object-Oriented Programming (OOP)

**Source folder:** `Ch-1_OOP/`  
**Source files reviewed:** `1_basics.py`, `2_constructors.py`, `3_encapsulation.py`, `4_DataExt_Class.py`, `5_methods.py`, and the CSV/JSON/TSV sample order files.

## 1. What is OOP?

Object-oriented programming organizes code around **classes** and **objects**.

- **Class:** a blueprint defining attributes (data) and methods (behaviour).
- **Object:** a particular instance created from a class.
- **Attribute:** a value associated with a class or object.
- **Method:** a function defined inside a class.

OOP helps structure reusable code for pipeline components such as API clients, file readers, validators, and transformation utilities.

## 2. Classes, objects, class variables, and instance methods

The first source file defines `MyClass` with class variables `var1` and `var2`, plus instance methods `func1()` and `func2()`.

```python
class Greeter:
    language = "Python"       # class variable

    def greet(self, name):    # instance method
        return f"Hello, {name}"

obj = Greeter()
print(obj.greet("Rohan"))
print(Greeter.language)
```

- Class variables are shared through the class and normally shared by its instances.
- Instance methods receive the current object as their first argument, conventionally named `self`.
- `obj.method()` is bound-method syntax: Python supplies `obj` as `self`.

## 3. Constructors and instance attributes

`2_constructors.py` demonstrates `__init__`. Python calls this initializer after creating an instance.

```python
class Order:
    category = "retail"

    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount

    def summary(self):
        return f"{self.order_id}: {self.amount}"

order = Order(1001, 1200.0)
print(order.summary())
```

`self.order_id` and `self.amount` are instance attributes. Different objects can hold different values.

The source also demonstrates `MyClass.func2(obj)`. This is the unbound/class-level way of calling the function while explicitly passing the instance; normally prefer `obj.func2()`.

**Interview point:** `__init__` initializes an already-created object; it is not technically the method that creates the object. `__new__` is responsible for object creation.

## 4. Encapsulation and attribute naming conventions

`3_encapsulation.py` demonstrates three naming styles:

| Style | Example | Meaning |
|---|---|---|
| Public | `self.name` | Normal public attribute |
| Protected convention | `self._name` | Internal-use convention; still accessible |
| Name-mangled | `self.__name` | Python rewrites the attribute name to reduce accidental access |

Important source-code observation: assigning `obj.dyn2 = "stu"` does **not** change `obj.__dyn2`. It creates a separate public attribute called `dyn2`; the original double-underscore attribute is name-mangled (roughly `_MyClass__dyn2`).

```python
class Customer:
    def __init__(self, name):
        self.name = name
        self._segment = "standard"
        self.__credit_limit = 5000

    def get_credit_limit(self):
        return self.__credit_limit
```

Python does not provide strict private access modifiers like some languages. Use properties when controlled read/write access is needed.

## 5. Working with data files through a class

`4_DataExt_Class.py` defines a `DataExt` class that stores a file path and uses pandas to read:
- delimited text using `pd.read_csv(path, sep=separator)`;
- JSON using `pd.read_json(path)`;
- Parquet using `pd.read_parquet(path)`.

```python
import pandas as pd

class DataExtractor:
    def __init__(self, path):
        self.path = path

    def read_csv(self, separator=","):
        return pd.read_csv(self.path, sep=separator)

    def read_json(self):
        return pd.read_json(self.path)

    def read_parquet(self):
        return pd.read_parquet(self.path)
```

For reusable pipeline code, return the DataFrame instead of only printing `head()`. Add file-existence checks, clear exceptions, logging, and configuration rather than hard-coding paths.

**Important correction:** despite the README wording referring to a dataclass, `4_DataExt_Class.py` does not use `@dataclass`; it is a regular class wrapping pandas readers.

## 6. Method types and special methods

`5_methods.py` demonstrates:

- `__init__`: initializer.
- `__str__`: human-readable string representation used by `print(obj)`.
- `@classmethod`: receives the class as `cls`; useful for changing class-level state or alternative constructors.
- `@staticmethod`: receives neither `self` nor `cls`; useful for a utility logically grouped with the class.

```python
class PipelineConfig:
    batch_size = 1000

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"PipelineConfig({self.name})"

    @classmethod
    def set_batch_size(cls, value):
        cls.batch_size = value

    @staticmethod
    def is_valid_batch_size(value):
        return isinstance(value, int) and value > 0
```

The source names its class method `_change_value`; the leading underscore is a convention indicating internal use, not an access restriction.

## 7. Sample order datasets

The `Files/` directory includes the same sample orders in CSV, JSON, and TSV formats. Fields are `OrderID`, `CustomerName`, `Product`, `Quantity`, `Price`, and `OrderDate`.

This illustrates that the same logical records can arrive in different file formats. TSV is tab-separated; CSV is comma-separated; JSON is structured key/value data. The repository also contains a Parquet sample, a columnar binary format commonly used in analytics.

## 8. Data Engineering applications

- Create reusable extractors for CSV, JSON, and Parquet.
- Encapsulate source connection settings in client classes.
- Represent pipeline configuration as objects.
- Use `__str__` or `__repr__` for useful diagnostics.
- Avoid mutable shared class variables for per-pipeline state.

## 9. Common interview questions

1. **Class vs object?** A class defines structure and behaviour; an object is an instance.
2. **Class variable vs instance variable?** Class variables belong to the class and are shared by default; instance variables belong to individual objects.
3. **What is `self`?** The conventional reference to the current instance.
4. **What does `__init__` do?** Initializes instance state after object creation.
5. **Does Python have private variables?** Not strict private fields; double underscores trigger name mangling.
6. **Instance method vs class method vs static method?** They receive `self`, `cls`, or neither, respectively.
7. **What is a dataclass?** A class decorated with `@dataclass` to generate common methods such as `__init__`; the repository's `DataExt` is not a dataclass.

## 10. Revision checklist

- [ ] Explain class, object, attribute, and method.
- [ ] Write a class with an initializer and two instances.
- [ ] Explain public, `_protected` convention, and `__name` mangling.
- [ ] Demonstrate all three method types.
- [ ] Read CSV, JSON, and Parquet using pandas.
- [ ] Explain why returning a DataFrame is more reusable than printing it.
