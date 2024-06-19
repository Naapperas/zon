# zon - Zod-like validator library for Python

[![Coverage Status](https://coveralls.io/repos/github/Naapperas/zon/badge.svg?branch=refactor/refactor-api)](https://coveralls.io/github/Naapperas/zon?branch=refactor/refactor-api)

Want to have the validation power of [zod](https://zod.dev/) but with the ease-of-use of Python?

Enter `zon`.

`zon` is a Python library that aims to provide a simple, easy-to-use API for validating data, similiar to `zod`'s own API'. In fact, the whole library and its name were inspired by `zod`: **Z**od + Pyth**on** = **Zon** !!!.

## Why

While doing a project for college, we were using both Python and JS/TS in the code-base. We were also using a JSON-Schema document to define a data schema for the data that we would be consuming.

There exists tooling that allows for one schema to generate TS types and from that Zod validator code, but there was nothing of the sort for Python. What's more, none of the validation libraries I found for Python had an API that was as easy to use as Zod's. So, I set out to build it.

## Installation

### Pip

This package is available on PyPI, so you can install it with `pip`:

```bash
pip install zon
```

### Source

Alternatively, you can clone this repository and install it from source:

```bash
git clone https://github.com/Naapperas/zon
cd zon
pip install .
```

## Usage

In its essence, `zon` behaves much like `zod`. If you have used `zod`, you will feel right at home with `zon`.

> [!NOTE]  
> There are some differences in the public API between `zon` and `zod`. Those mostly stem from the fact that Python does not have type inference like Typescript has.

### Basic types

`zon` features most of `zod`'s basic types:

```python
zon.string()
zon.integer()
zon.floating_point()
zon.boolean()
zon.none()
zon.anything()
```

Besides this, there's also a `zon.optional()` type, which allows for a value to be either of the type passed as an argument or `None`.

```python
zon.optional(zon.string())
```

### Integers and Floats

`zon`'z integer and floating point types derive from a common `ZonNumber` class that defines some methods that can be applied to all numbers:

```python
validator = zon.integer() # (for floats, use zon.floating_point())

validator.gt(5)
validator.gte(5)
validator.lt(5)
validator.lte(5)
```

### Strings

For strings, there are also some extra methods:

```python
zon.string().min(5)
zon.string().max(10)
zon.string().length(5)
zon.string().email()
zon.string().regex(r"^\d{3}-\d{3}-\d{4}$")
zon.string().uuid()
zon.string().ip()
zon.string().datetime()
```

#### Datetime

`zod` uses regex-based validation for datetimes, which must be valid [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) strings. However, due to an issue with most JavaScript engines' datetime validation, offsets cannot specify only hours, and `zod` reflects this in their API.

While `zon` could reflect `zod`'s API in this matter, it is best to not constrain users to the problems of another platform, making this one of the aspects where `zon` deviates from `zod`.

### List

Lists are defined by calling the `zon.list()` method, passing as an argument a `Zon` instance. All elements in this list must be of the same type.

```python
zon.element_list(zon.string())
```

Like strings, lists also have some extra methods that check the length of the list:

```python
validator = zon.list(...)

validator.min(5)
validator.max(10)
validator.length(5)
```

### Union

`zon` supports unions of types, which are defined by calling the `zon.union()` method, passing as arguments the `Zon` instances that are part of the union.

```python
zod.union([zon.string(), zon.integer()])
```

### Record

`zon` supports validating objects according to a specified schema, using the `zon.schema()` method. This method takes as an argument a dictionary, where the keys are the keys of the object to be validated and the values are the `Zon` instances that define the type of each key.

This method is probably the most useful in the library since it can be used to, for example, validate JSON data from a HTTP response, like such:

```python
import zon

schema = zon.record({
    "name": zon.string(),
    "age": zon.number(),
    "isAwesome": zon.boolean(),
    "friends": zon.array(zon.string()),
    "address": zon.record({
        "street": zon.string(),
        "city": zon.string(),
        "country": zon.string(),
    }),
})
```

## Examples

Example usage of `zon` can be found in the `examples` directory.

## Documentation

Documentation is still not available, but it will be soon.

## Tests

Tests can be found in the [tests](tests) folder. `zon` uses `pytest` for unit testing.

To run the tests, simply run:

```bash 
pytest test
```

Coverage can be found on [Coveralls](https://coveralls.io/github/Naapperas/zon).

## Contributing

Contribution guidelines can be found in [CONTRIBUTING](CONTRIBUTING.md)

Past and current contributors can be found in [CONTRIBUTORS](CONTRIBUTORS.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
