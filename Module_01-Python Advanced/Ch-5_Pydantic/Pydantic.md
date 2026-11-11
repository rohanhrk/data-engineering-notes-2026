# Module 5 — Pydantic

**Source folder:** `Ch-5_Pydantic/`  
**Source notebooks reviewed:** `1_basics.ipynb`, `2_Fields.ipynb`, `3_Serialization.ipynb`.

## 1. What is Pydantic?

Pydantic is a Python library for parsing and validating data using type hints. It is useful at system boundaries: API payloads, configuration, event messages, and records entering a pipeline.

The notebooks use Pydantic v2 style (`BaseModel`, `Field`, `model_dump`, `model_dump_json`).

## 2. BaseModel and type validation

The first notebook defines an `employee_schema` with `name: str`, `id: int`, and `department: str`.

```python
from pydantic import BaseModel

class Employee(BaseModel):
    name: str
    id: int
    department: str

employee = Employee(name="John Doe", id=123, department="HR")
```

Pydantic validates the incoming values and creates a model instance. It may coerce compatible values by default; the notebook demonstrates the string `"101"` being parsed as integer `101`.

`Employee(**payload)` unpacks dictionary keys as keyword arguments.

## 3. Coercion vs strict types

Coercion converts compatible input values to the declared type. Strict types reject values that are not already the required type.

```python
from pydantic import BaseModel, StrictInt

class StrictEmployee(BaseModel):
    id: StrictInt

StrictEmployee(id=101)       # valid
# StrictEmployee(id="101")   # validation error
```

Choose strictness based on the data contract. Coercion is convenient for inconsistent external payloads; strict validation can catch upstream schema drift.

## 4. Field constraints and optional fields

The second notebook defines fields using `Field`:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class Employee(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., gt=18, lt=65)
    email: EmailStr = Field(..., description="Employee email")
    department: Optional[str] = None
    gender: Literal["Male", "Female", "Other"]
```

- `...` means the field is required.
- `min_length` and `max_length` constrain strings.
- `gt` and `lt` mean strictly greater than and strictly less than.
- `EmailStr` validates email syntax (requires the optional email validation dependency).
- `Optional[str] = None` means the value may be a string or `None`, and the field has a default.
- `Literal` restricts values to a defined set.

The notebook's age rule is `gt=18, lt=65`, so 18 and 65 are excluded.

## 5. Serialization

The third notebook uses:

```python
employee.model_dump()       # Python dictionary
employee.model_dump_json()  # JSON string
```

Serialization converts a validated model into a format suitable for downstream systems. Pydantic v2 also supports options such as `exclude_none=True`, `exclude_unset=True`, and `by_alias=True`.

**Parsing vs serialization:**
- Validation/parsing: untrusted input → validated model.
- Serialization: model → dictionary or JSON representation.

## 6. Data Engineering applications

- Validate API response payloads before writing to Bronze.
- Validate configuration and environment settings.
- Define contracts for event messages.
- Validate required fields, types, ranges, and enumerated values.
- Serialize validated records for API calls or storage.

Pydantic validation does not replace business-level data quality checks such as referential integrity, duplicate detection, freshness, or reconciliation.

## 7. Common interview questions

1. **What is Pydantic?** A type-hint-based parsing and validation library.
2. **What is `BaseModel`?** The base class for defining validated data models.
3. **What does `Field` do?** Adds constraints, defaults, aliases, and schema metadata.
4. **What is coercion?** Converting compatible input values to declared types.
5. **How do strict types differ?** They reject values that would otherwise be coerced.
6. **`model_dump()` vs `model_dump_json()`?** Dictionary vs JSON string.
7. **Why validate ingestion data?** Catch malformed or contract-breaking records before they propagate.

## 8. Revision checklist

- [ ] Define a Pydantic model.
- [ ] Validate a dictionary using `Model(**payload)`.
- [ ] Demonstrate coercion and `StrictInt`.
- [ ] Add `Field` constraints and `Literal`.
- [ ] Explain required vs optional fields.
- [ ] Serialize using `model_dump()` and `model_dump_json()`.
