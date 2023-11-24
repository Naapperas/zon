# zon - Zod-like validator library for Python

Want to have the validation power of [zod](https://zod.dev/) but with the ease-of-use of Python?

Enter `zon`.

`zon` is a Python library that aims to provide a simple, easy-to-use API for validating data, similiar to `zod`'s own API'. In fact, the whole library and its name were inspired by `zod`: **Z**od + Pyth**on** = **Zon** !!!.

## Why

While doing a project for college, we were using both Python and JS/TS in the code-base. We were also using a JSON-Schema document to define a data schema for the data that we would be consuming.

There exists tooling that allows for one schema to generate TS types and from that Zod validator code, but there was nothing of the sort for Python. What's more, none of the validation libraries I found for Python had an API that was as easy to use as Zod's. So, I set out to build it.