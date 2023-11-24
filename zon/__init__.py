"""Validator package.

The purpose of this package is to provide a set of functions to validate data, using a Zod-like syntax.
"""


__version__ = "1.0.0"
__author__ = "Nuno Pereira"
__email__ = "nunoafonso2002@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2023, Nuno Pereira"

from zon.number.float import ZonFloat
from zon.number.int import ZonInteger
from zon.base import Zon
from zon.bool import ZonBoolean
from zon.list import ZonList
from zon.str import ZonString
from zon.union import ZonUnion
from zon.record import ZonRecord


def string() -> "ZonString":
    """Creates a new Zon that validates that the data is a string.

    Returns:
        ZonString: a new validator that validates that the data is a string.
    """
    return ZonString()


def integer() -> "ZonInteger":
    """Creates a new Zon that validates that the data is an integer.

    Returns:
        ZonInteger: a new validator that validates that the data is an integer
    """
    return ZonInteger()


def floating_point() -> "ZonFloat":
    """Creates a new Zon that validates that the data is a floating point number.

    Returns:
        ZonFloat: a new validator that validates that the data is a floating point number.
    """
    return ZonFloat()


def boolean() -> "ZonBoolean":
    """Creates a new Zon that validates that the data is a boolean.

    Returns:
        ZonBoolean: a new validator that validates that the data is a boolean.
    """
    return ZonBoolean()


def element_list(element_type: "Zon") -> "ZonList":
    """Creates a new Zon that validates that the data is a list of elements of the specified type.

    Args:
        element_type (Zon): the type of the elements of the list.

    Returns:
        ZonList: a new validator that validates that the data is
        a list of elements of the specified type.
    """
    return ZonList(element_type)


def union(types: list["Zon"]) -> "ZonUnion":
    """Creates a new Zon that validates that the data is one of the specified types.

    Args:
        types (list[Zon]): the types of the data to be validated.

    Returns:
        ZonUnion: a new validator that validates that the data is one of the specified types.
    """
    return ZonUnion(types)


def record(properties: dict[str, "Zon"]) -> "ZonRecord":
    """Creates a new Zon that validates that the data is an object with the specified properties.

    Args:
        properties (dict[str, Zon]): the properties of the object to be validated.

    Returns:
        ZonRecord: a new validator that validates that the data is
        an object with the specified properties.
    """
    return ZonRecord(properties)
