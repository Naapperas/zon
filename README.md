# zon - Zod-like validator library for Python

[![Coverage Status](https://coveralls.io/repos/github/Naapperas/zon/badge.svg?branch=refactor/refactor-api)](https://coveralls.io/github/Naapperas/zon?branch=refactor/refactor-api)

Want to have the validation power of [zod](https://zod.dev/) but with the ease-of-use of Python?

Enter `zon`.

`zon` is a Python library that aims to provide a simple, easy-to-use API for validating data, similar to `zod`'s own API'. In fact, the whole library and its name were inspired by `zod`: **Z**od + Pyth**on** = **Zon** !!!.

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
> There are some differences in the public API between `zon` and `zod`. Those mostly stem from the fact that Python does not have type inference like Typescript has. There are other slight deviations between `zon` and `zod`. 

### General

#### Validate

To validate against a schema, use `validator.validate()`

```python
validator = zon.string()
message = validator.validate("Hello World!") # returns 'Hello World!'
```

Alternatively, you may use `validator.safe_validate()`.
`safe_validate` will tell you whether the validation was successful, without throwing an error. Depending on the needs of your project, you can do this to handle exceptions more elegantly.

```python
validator = zon.string()
success, message = validator.safe_validate("Hello World!") # returns (True, 'Hello World!')
```

#### Chaining

Most validators can be chained together, just like `zod`:

```python
validator = zon.string().min(5).max(10).email()
```

This is equivalent to:

```python
validator = zon.string()
validator = validator.min(5)
validator = validator.max(10)
validator = validator.email()
```

### Basic types

`zon` features most of `zod`'s basic types:

```python
zon.string()
zon.number()
zon.boolean()
zon.literal()
zon.enum()

zon.record()
zon.element_list()
zon.element_tuple()

zon.union()
zon.intersection()
zon.optional()

zon.never()
zon.anything()
```

### Numbers

```python
validator = zon.number()

validator.gt(5)
validator.gte(5) # alias for .min(5)
validator.lt(5)
validator.lte(5) # alias for .max(5)

validator.int()
validator.float()

validator.positive()
validator.negative()
validator.non_negative()
validator.non_positive()

validator.multiple_of(5) # alias for .step(5)

validator.finite()
```

### Strings

For strings, there are also some extra methods:

```python
validator = zon.string()

validator.min(5)
validator.max(10)
validator.length(5)

validator.email()
validator.url()
validator.uuid()
validator.regex(r"^\d{3}-\d{3}-\d{4}$")
validator.includes("needle")
validator.starts_with("prefix")
validator.ends_with("suffix")
validator.datetime()
validator.ip()

# transformers
validator.trim()
validator.to_lower_case()
validator.to_upper_case()
```

#### Datetime

`zon` accepts the same options as `zod` for datetime string validation:
```python
validator.datetime({"precision": 3})
validator.datetime({"local": True})
validator.datetime({"offset": True})
```

> [!NOTE]
> `zod` uses regex-based validation for datetimes, which must be valid [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) strings. However, due to an issue with most JavaScript engines' datetime validation, offsets cannot specify only hours, and `zod` reflects this in their API.
> While `zon` could reflect `zod`'s API in this matter, it is best to not constrain users to the problems of another platform, making this one of the aspects where `zon` deviates from `zod`.

#### IP addresses

`zon` accepts the same options as `zod` for ip address string validation:
```python
validator.ip({"version": "v4"})
validator.ip({"version": "v6"})
```


### List

Lists are defined by calling the `zon.element_list()` method, passing as an argument a `Zon` instance. All elements in this list must be of the same type.

```python
zon.element_list(zon.string())
```

Like strings, lists also have some extra methods that check the length of the list:

```python
validator = zon.element_list(...)

validator.min(5)
validator.max(10)
validator.length(5)
```

There is also a method for validating that the list has at least one element, `nonempty`:
```py
validator.nonempty()
```

You can get the type of the list's elements by accessing the `element` property:
```py
zon.element_list(zon.string()).element is ZonString
```

### Union

`zon` supports unions of types, which are defined by calling the `zon.union()` method, passing as arguments the `Zon` instances that are part of the union.

```python
zod.union([zon.string(), zon.number()])
```

To access the various options, access the `options` property:

```python
zod.union([zon.string(), zon.number()]).options = [ZonString, ZonNumber]
```

### Record

`zon` supports validating objects according to a specified schema, using the `zon.schema()` method. This method takes as an argument a dictionary, where the keys are the keys of the object to be validated and the values are the `Zon` instances that define the type of each key.

```python
validator = zon.record({
    "name": zon.string(),
    "age": zon.number(),
    "isAwesome": zon.boolean(),
    "friends": zon.element_list(zon.string()),
    "address": zon.record({
        "street": zon.string(),
        "city": zon.string(),
        "country": zon.string(),
    }),
})
```

Useful methods for `ZonRecord` instances:
```py
validator.extend({...})
validator.merge(otherZon) == validator.extend(otherZon.shape)
validator.pick({"name": True}) == ZonRecord({"name": ...})
validator.omit({"name": True}) == ZonRecord({"<key that is different from name>": ..., ...})
validator.partial() # makes all attributes optional, shallowly
validator.partial({"name": True}) # makes only "name" optional (in this example)
validator.deepPartial() # makes all attributes optional, recursively
validator.required() # makes all attributes required, shallowly
```

You can access the shape of objects validated by any `ZonRecord` instance by accessing the `shape` property:
```py
shape = validator.shape
```

If you want to validate only the keys of the shape, use the `keyof` method:
```py
validator.keyof() == ZonEnum(["name", "age", "isAwesome", "friends", "address"])
```

#### Unknown Keys

As `zod`, `zon` normally strips unknown keys from records. This, however, can be configured:
```py
validator.strict() # presence of unknown keys makes validation fail
validator.passthrough() # add unknown keys to the resulting record
validator.strip() # the default behavior, strip unknown keys from the resulting record
```

#### Catchall

In case you want to validate unknown keys, you can use the `catchall` method to specify the validator that is used:
```py
validator.catchall(zon.string()) # unknown keys *must* be associated with string values
```

### Tuple

`zon` supports tuples out-of-the-box, which are fixed-size containers whose elements might not have the same type:
```py
validator = zon.tuple([...])
```

If you want to access the items of the tuples, use the `items` property:
```py
validator.items = [...]
```

Variadic items can be validated using the `rest` method:
```py
validator.rest(zon.string()) # after the defined items, everything must be a string
```

### Enums

`zon` supports enumerations, which allow validating that any given data is one of many values:

```py
validator = zon.enum([...])
```

If you want to access the possible valid values, use the `enum` property:
```py
validator.enum = [...]
```

## Examples

Example usage of `zon` can be found in the [`examples`](./examples/) directory.

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
