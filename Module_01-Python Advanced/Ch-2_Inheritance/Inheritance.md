# Module 2 — Inheritance

**Source folder:** `Ch-2_Inheritance/`  
**Source files reviewed:** `1_single_level.py`, `2.1_multiple.py`, `2.2_multiple.py`, `3_multi_level.py`.

## 1. What is inheritance?

Inheritance allows a child class to reuse or specialize attributes and methods from a parent class.

```python
class Company:
    def info(self):
        return "Company information"

class Employee(Company):
    def employee_info(self):
        return self.info()
```

`Employee` inherits from `Company`. This can reduce duplication and express an “is-a” relationship.

## 2. Single inheritance

`1_single_level.py` defines `company` and `employee(company)`. The employee class carries employee and company names and calls `company.info(self)`.

A more idiomatic version uses `super()`:

```python
class Company:
    def __init__(self, company_name):
        self.company_name = company_name

    def info(self):
        return f"Company: {self.company_name}"

class Employee(Company):
    def __init__(self, employee_name, company_name):
        super().__init__(company_name)
        self.employee_name = employee_name

    def employee_info(self):
        return f"{self.employee_name} works at {self.info()}"
```

`super()` delegates to the next class in the Method Resolution Order (MRO), rather than hard-coding a parent class name.

## 3. Hierarchical inheritance (source file 2.1)

The file `2.1_multiple.py` has two sibling child classes, `employee(company)` and `contractor(company)`. Both inherit from the same parent.

This is **hierarchical inheritance**, not multiple inheritance: one parent has multiple child classes.

Use it when different entity types share common behaviour but have their own specialized behaviour.

## 4. Multiple inheritance (source file 2.2)

`2.2_multiple.py` defines `employee(company, client_company)`, so the child inherits from two parent classes.

The example explicitly calls `company.info(self)` and `client_company.info(self)`. This works for the demonstration, but bypasses cooperative MRO-based delegation.

```python
class Company:
    def info(self):
        return "Employer"

class ClientCompany:
    def client_info(self):
        return "Client"

class Employee(Company, ClientCompany):
    pass

employee = Employee()
print(employee.info())
print(employee.client_info())
print(Employee.mro())
```

### Method Resolution Order (MRO)

MRO defines the order Python searches for a method or attribute in an inheritance hierarchy.

- Inspect it with `ClassName.mro()` or `ClassName.__mro__`.
- `super()` follows the MRO.
- The order of parent classes can affect which implementation is selected.

The “diamond problem” occurs when a class inherits through multiple paths from a common ancestor. Python uses C3 linearization to produce a consistent MRO.

## 5. Multilevel inheritance

`3_multi_level.py` creates a chain:

`company → manager → employee`

The `employee` class calls `manager.info(self)`, which calls `company.info(self)`. This demonstrates a multilevel hierarchy.

A cleaner cooperative version:

```python
class Company:
    def __init__(self, company_name):
        self.company_name = company_name

    def info(self):
        return f"Company: {self.company_name}"

class Manager(Company):
    def __init__(self, manager_name, company_name):
        super().__init__(company_name)
        self.manager_name = manager_name

    def info(self):
        return f"Manager {self.manager_name}; {super().info()}"

class Employee(Manager):
    def __init__(self, employee_name, manager_name, company_name):
        super().__init__(manager_name, company_name)
        self.employee_name = employee_name

    def info(self):
        return f"Employee {self.employee_name}; {super().info()}"
```

## 6. Key inheritance patterns

| Pattern | Shape | Repository example |
|---|---|---|
| Single | one parent → one child | `1_single_level.py` |
| Hierarchical | one parent → multiple children | `2.1_multiple.py` |
| Multiple | multiple parents → one child | `2.2_multiple.py` |
| Multilevel | parent → child → grandchild | `3_multi_level.py` |

## 7. Inheritance vs composition

Inheritance models an “is-a” relationship. Composition models a “has-a” relationship.

For example, a `DataPipeline` may **have a** `DataReader`, `Transformer`, and `DataWriter`; it does not necessarily need to inherit from all three. Composition often keeps pipeline components more flexible and easier to test.

## 8. Data Engineering applications

- Shared base classes for file readers or source connectors.
- Specialized API clients for different vendors.
- Common logging/configuration behaviour.
- Prefer composition for assembling ingestion, transformation, and loading components.

## 9. Common interview questions

1. **What is inheritance?** Reusing and extending behaviour from a parent class.
2. **What is hierarchical inheritance?** Multiple child classes inherit from one parent.
3. **What is multiple inheritance?** One class inherits from more than one parent.
4. **What is MRO?** Python's method lookup order.
5. **What does `super()` do?** Calls the next implementation in the MRO.
6. **What is the diamond problem?** Ambiguous-looking inheritance paths to a common ancestor; Python resolves it through MRO.
7. **Inheritance vs composition?** Inheritance expresses “is-a”; composition expresses “has-a”.

## 10. Revision checklist

- [ ] Draw the four inheritance structures.
- [ ] Explain why `2.1_multiple.py` is hierarchical, not multiple inheritance.
- [ ] Print and explain an MRO.
- [ ] Rewrite a parent-child example using `super()`.
- [ ] Explain when composition is preferable.
