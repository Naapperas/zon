"""Validator package.

Flexible validation powered by Python with the expressiveness of a Zod-like API.
"""

# Why is this needed even?
from __future__ import annotations

__version__ = "3.0.1"
__author__ = "Nuno Pereira"
__email__ = "nunoafonso2002@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2023, Nuno Pereira"

# TODO: better typing.
# Things to consider:
# - Container and other collections.abc types
# - Typing with Self

import copy
from abc import ABC, abstractmethod, update_abstractmethods
from typing import Any, Self, TypeVar, final, Literal
from collections.abc import Callable, Mapping, Sequence  # TODO: explore Container type
from dataclasses import dataclass, field
import re
import math
from enum import Enum, auto

import validators

from .error import ZonError, ZonIssue
from .traits import HasMax, HasMin

__all__ = [
    "Zon",
    "element_list",
    "ZonList",
    "ZonBoolean",
    "boolean",
    # "ZonDate",
    # "ZonDateTime",
    # "ZonNone",
    "ZonNumber",
    "number",
    "ZonRecord",
    "record",
    "ZonString",
    "string",
    "ZonOptional",
    "optional",
    "ZonIntersection",
    "intersection",
    "ZonEnum",
    "enum",
    "ZonLiteral",
    "literal",
    "ZonUnion",
    "union",
    "ZonTuple",
    "element_tuple",
]


@dataclass
class ValidationContext:
    """Context used throughout an entire validation run"""

    error: ZonError = None
    path: list[str] = field(default_factory=list)

    def _ensure_error(self):
        if self.error is None:
            self.error = ZonError()

    def add_issue(self, issue: ZonIssue):
        """Adds the given `ZodIssue` to this context's `ZonError`"""
        self._ensure_error()
        self.error.add_issue(issue)

    def add_issues(self, issues: list[ZonIssue]):
        """Adds the given `ZodIssue`s to this context's `ZonError`"""
        self._ensure_error()
        self.error.add_issues(issues)

    @property
    def dirty(self):
        return self.error is not None and len(self.error.issues) >= 0


T = TypeVar("T")


class ValidationRule:
    """
    Custom validation rul used to add more complex validation rules to an existing `Zon`
    """

    def __init__(
        self,
        name: str,
        fn: Callable[[T], tuple[T, bool]],
        *,
        additional_data: Mapping[str, Any] = None,
    ):
        self.fn = fn
        self.name = name
        self.additional_data = additional_data if additional_data is not None else {}

    def check(self, data: T, ctx: ValidationContext) -> T:
        """
        Check this validation rule against the supplied data.

        Args:
            data (T): the piece of data to be validated.
            ctx (ValidationContext): the context in which the validation is being run.

        Returns:
            T: The original data
        """

        try:
            new_data, valid = self.fn(data)

            if not valid:
                ctx.add_issue(
                    ZonIssue(
                        value=data,
                        message=f"Validation failed for type {self.name}",
                        path=[],
                    )
                )

            return new_data
        except Exception as e:
            ctx.add_issue(
                ZonIssue(
                    value=data,
                    message=f"Validation failed for type {self.name}: {e}",
                    path=[],
                )
            )

            return data


@update_abstractmethods
class Zon(ABC):
    """
    Base class for all Zons.

    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self):
        self.validators: list[ValidationRule] = []
        """validators that will run when 'validate' is invoked."""

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    @abstractmethod
    def _default_validate(self, data: T, ctx: ValidationContext) -> T:
        """Default validation for any Zon validator

        The contract for this method is the same for any other `ValidationRule`: If the validation fails, mark the context as dirty.

        In any case, this method should return the original data

        The default implementation raises a NotImplementedError.

        Args:
            data (Any): the piece of data to be validated.
            ctx (ValidationContext): the context of the validation.
        """

        raise NotImplementedError(
            "This method is not implemented for the base Zon class. You need to provide your "
        )

    @final
    def _validate(
        self, data: T
    ) -> tuple[Literal[True], T] | tuple[Literal[False], ZonError]:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            (bool, T) | (bool, ZonError): A tuple containing a boolean indicating whether the data is valid,
            and either the validated data or a ZonError object.

        Raises:
            ZonError: if validation against the supplied data fails.
            NotImplementedError: if the default validation rule was not overriden for this Zon object.
        """

        ctx = ValidationContext()

        cloned_data = copy.deepcopy(data)

        try:
            cloned_data = self._default_validate(cloned_data, ctx)
        except NotImplementedError as ni:
            raise ni

        if ctx.dirty:
            return (False, ctx.error)

        for validator in self.validators:
            cloned_data = validator.check(cloned_data, ctx)

        return (not ctx.dirty, cloned_data if not ctx.dirty else ctx.error)

    @final
    def validate(self, data: T) -> T:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            T: the validated data.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
            ZonError: if validation fails.
        """

        valid, data_or_error = self.safe_validate(data)

        if valid:
            return data_or_error

        raise data_or_error

    @final
    def safe_validate(
        self, data: T
    ) -> tuple[Literal[True], T] | tuple[Literal[False], ZonError]:
        """Validates the supplied data. This method is different from `validate` in the sense that
        it does not raise an error when validation fails. Instead, it returns an object encapsulating
        either a successful validation result or a validation error.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            (bool, T) | (bool, ZonError): A tuple containing a boolean indicating whether the data is valid,
            and either the validated data or a ZonError object.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
            Exception: if any unexpected exception is encountered
        """

        try:
            return self._validate(data)
        except Exception as e:
            raise e

    def and_also(self, other: Zon) -> ZonIntersection:
        """Returns a validator that validates that the data is valid for both this and the supplied validators.

        Args:
            other (Zon): the second validator

        Returns:
            ZonIntersection: The intersection data validator.
        """

        return intersection(self, other)

    def or_else(self, other: Sequence[Zon]) -> ZonUnion:
        """Returns a validator that validates that the data is valid for at least one of the supplied validators.

        Args:
            other (Sequence(Zon))
        """

        return union([self, *other])

    def optional(self) -> ZonOptional:
        """Returns a validator that validates that the data is valid for this validator if it exists.

        Returns:
            ZonOptional: The optional data validator.
        """

        return optional(self)

    def list(self) -> ZonList:
        """Returns a validator that validates a list whose elements are valid under this validator.

        Returns:
            ZonArray: The list data validator.
        """

        return element_list(self)

    def refine(
        self, refinement: Callable[[T], bool], /, message: str | None = None
    ) -> Self:
        """Returns a validator that validates that the data is valid under this validator and that it is valid under the provided refinement function.

        Args:
            refinement (Callable[[T], tuple[T, bool]]): the refinement function
            message (str | None): custom message to be used in the error.

        Returns:
            Zon: The refined data validator.
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                message if message is not None else "custom",
                lambda data: (data, refinement(data)),
            )
        )

        return _clone


def intersection(zon1: Zon, zon2: Zon) -> ZonIntersection:
    """Returns a validator that validates that the data is valid for both validators supplied.

    Args:
        zon1 (Zon): the first validator
        zon2 (Zon): the second validator

    Returns:
        ZonIntersection: The intersection data validator.
    """

    return ZonIntersection(zon1, zon2)


class ZonIntersection(Zon):
    """A Zon that validates that the data is valid for both this Zon and the supplied Zon."""

    def __init__(self, zon1: Zon, zon2: Zon, /, **kwargs):
        super().__init__(**kwargs)
        self.zon1 = zon1
        self.zon2 = zon2

    def _default_validate(self, data: T, ctx: ValidationContext):
        (zon_1_parsed, data1_or_error) = self.zon1.safe_validate(data)

        if not zon_1_parsed:
            ctx.add_issues(data1_or_error.issues)
            return data

        (zon_2_parsed, data2_or_error) = self.zon2.safe_validate(data)

        if not zon_2_parsed:
            ctx.add_issues(data2_or_error.issues)
            return data

        return data


def optional(zon: Zon) -> ZonIntersection:
    """Returns a validator that validates that the data is valid for this validator if it exists.

    Args:
        zon (Zon): the supplied validator

    Returns:
        ZonIntersection: The intersection data validator.
    """
    return ZonOptional(zon)


class ZonOptional(Zon):
    """A Zon that makes its data validation optional."""

    def __init__(self, zon: Zon, **kwargs):
        super().__init__(**kwargs)
        self._zon = zon

    def _default_validate(self, data, ctx):
        if data:
            (passed, data_or_error) = self._zon.safe_validate(data)

            if not passed:
                ctx.add_issues(data_or_error.issues)

        return data

    def unwrap(self) -> Zon:
        """Extracts the wrapped Zon from this ZonOptional.

        Returns:
            Zon: the wrapped Zon
        """

        return self._zon


class ZonContainer(Zon, HasMax, HasMin):
    """A Zon that acts as a container for other types of data.

    Contains container specific validator rules.
    """

    def max(self, max_value: int | float) -> Self:
        """Validates that this container as at most `max_value` elements (inclusive).

        Args:
            max_value (int | float): the maximum number of elements that this container can have
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "max_length",
                lambda data: (
                    data,
                    hasattr(data, "__len__") and len(data) <= max_value,
                ),
            )
        )

        return _clone

    def min(self, min_value: int | float) -> Self:
        """Validates that this container as at least `max_value` elements (inclusive).

        Args:
            min_value (int | float): the minimum number of elements that this container can have
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "min_length",
                lambda data: (
                    data,
                    hasattr(data, "__len__") and len(data) >= min_value,
                ),
            )
        )

        return _clone

    def length(self, length: int) -> Self:
        """Validates that this container as exactly `length` elements.

        Args:
            length (int): the exact number of elements that this container can have
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "equal_length",
                lambda data: (data, hasattr(data, "__len__") and len(data) == length),
            )
        )

        return _clone


def string() -> ZonString:
    """Returns a validator for string data.

    Returns:
        ZonString: The string data validator.
    """

    return ZonString()


class ZonString(ZonContainer):
    """A Zon that validates that the data is a string.

    For all purposes, a string is a container of characters.
    """

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, str):
            ctx.add_issue(ZonIssue(value=data, message="Not a string", path=[]))

        return data

    def email(self) -> Self:
        """
        Assert that the value under validation is a valid email.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "email",
                lambda data: (data, validators.email(data)),
            )
        )

        return _clone

    def url(self) -> Self:
        """
        Assert that the value under validation is a valid URL.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "url",
                lambda data: (data, validators.url(data)),
            )
        )

        return _clone

    def emoji(self) -> Self:
        """Assert that the value under validation is a valid emoji.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        raise NotImplementedError

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "emoji",
                lambda data: re.compile(
                    r"^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$"
                ).match(data)
                is not None,
            )
        )

        return _clone

    def uuid(self) -> Self:
        """Assert that the value under validation is a valid UUID.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "uuid",
                lambda data: (data, validators.uuid(data)),
            )
        )

        return _clone

    # TODO: cuid, cuid2, nanoid, ulid

    def regex(self, regex: str | re.Pattern[str]) -> Self:
        """Assert that the value under validation matches the given regular expression.

        Args:
            regex (str): the regex to use.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "regex",
                lambda data: (data, re.match(regex, data) is not None),
            )
        )

        return _clone

    def includes(self, needle: str) -> Self:
        """Assert that the value under validation includes the given string.

        Args:
            needle (str): the string to look for.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "includes",
                lambda data: (data, needle in data),
            )
        )

        return _clone

    def starts_with(self, prefix: str) -> Self:
        """Assert that the value under validation starts with the given string.

        Args:
            prefix (str): the string to look for.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "starts_with",
                lambda data: (data, data.startswith(prefix)),
            )
        )

        return _clone

    def ends_with(self, suffix: str) -> Self:
        """Assert that the value under validation ends with the given string.

        Args:
            suffix (str): the string to look for.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "ends_with",
                lambda data: (data, data.endswith(suffix)),
            )
        )

        return _clone

    def datetime(self, opts: Mapping[str, Any] | None = None) -> Self:
        """Assert that the value under validation is a valid datetime.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        if opts is None:
            opts = {}

        # code ported from https://github.com/colinhacks/zod. All credit goes to the original author.
        def _time_regex_source(opts: Mapping[str, Any]):
            regex = r"([01]\d|2[0-3]):[0-5]\d:[0-5]\d"

            if "precision" in opts:
                precision = opts["precision"]

                regex = rf"{regex}\.\d{{{precision}}}"
            else:
                regex = rf"{regex}(\.\d+)?"

            return regex

        def _datetime_regex(opts: Mapping[str, Any]):
            dateRegexSource = r"((\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-((0[13578]|1[02])-(0[1-9]|[12]\d|3[01])|(0[469]|11)-(0[1-9]|[12]\d|30)|(02)-(0[1-9]|1\d|2[0-8])))"

            regex = f"{dateRegexSource}T{_time_regex_source(opts)}"

            branches: list[str] = []
            branches.append("Z?" if opts.get("local", False) else "Z")
            if opts.get("offset", False):
                branches.append(
                    r"([+-]\d{2}(:?\d{2})?)"
                )  # slight deviation from zod's regex, allowing for hour-only offsets

            regex = f"{regex}({'|'.join(branches)})"

            print(regex)

            return re.compile(f"^{regex}$")

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "datetime",
                lambda data: (data, _datetime_regex(opts).match(data) is not None),
            )
        )

        return _clone

    def ip(self, opts: Mapping[str, Any] | None = None) -> Self:
        """Assert that the value under validation is a valid IP address.

        By default this checks if the IP is either a valid IPv4 or IPv6 address.
        Clients can constrain this behavior by specifying the version in the `opts` parameter, like so:
        ```py
        zon.string().ip({"version": "v4"})
        ```

        Args:
            opts (Mapping[str, Any]): the options to use. Defaults to None

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        if opts is None:
            opts = {}

        _clone = self._clone()

        def _validator(data, opts: Mapping[str, Any]):

            doesnt_specify_version = "version" not in opts

            if doesnt_specify_version or opts["version"] == "v4":
                try:
                    if validators.ipv4(data):
                        return True
                except validators.ValidationError:
                    pass

            if doesnt_specify_version or opts["version"] == "v6":
                try:
                    if validators.ipv6(data):
                        return True
                except validators.ValidationError:
                    pass

            return False

        _clone.validators.append(
            ValidationRule(
                "ip",
                lambda data: (data, _validator(data, opts)),
            )
        )

        return _clone

    def trim(self) -> Self:
        """Trim whitespace from both sides of the value.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "trim",
                lambda data: (data.strip(), True),
            )
        )

        return _clone

    def to_lower_case(self) -> Self:
        """Convert the value to lowercase.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "to_lower_case",
                lambda data: (data.lower(), True),
            )
        )

        return _clone

    def to_upper_case(self) -> Self:
        """Convert the value to uppercase.

        Returns:
            ZonString: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "to_upper_case",
                lambda data: (data.upper(), True),
            )
        )

        return _clone


def number() -> ZonNumber:
    """Returns a validator for numeric data.

    Returns:
        ZonNumber: The number data validator.
    """

    return ZonNumber()


class ZonNumber(Zon, HasMax, HasMin):
    """A Zon that validates that the data is a number."""

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, (int, float)):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid number", path=[]))

        return data

    def gt(self, min_ex: float | int) -> Self:
        """Assert that the value under validation is greater than the given number.

        Args:
            min_ex (float | int): the number to compare against.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "gt",
                lambda data: (data, data is not None and data > min_ex),
            )
        )

        return _clone

    def gte(self, min_in: float | int) -> Self:
        """Assert that the value under validation is greater than or equal to the given number.

        Args:
            min_in (float | int): the number to compare against.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "gte",
                lambda data: (data, data is not None and data >= min_in),
            )
        )

        return _clone

    def min(self, min_value: int | float) -> Self:
        return self.gte(min_value)

    def lt(self, max_ex: float | int) -> Self:
        """Assert that the value under validation is less than the given number.

        Args:
            max_ex (float | int): the number to compare against.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "lt",
                lambda data: (data, data is not None and data < max_ex),
            )
        )

        return _clone

    def lte(self, max_in: float | int) -> Self:
        """Assert that the value under validation is less than or equal to the given number.

        Args:
            max_in (float | int): the number to compare against.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "lte",
                lambda data: (data, data is not None and data <= max_in),
            )
        )

        return _clone

    def max(self, max_value: int | float) -> Self:
        return self.lte(max_value)

    def int(self) -> Self:
        """Assert that the value under validation is an integer.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "int",
                lambda data: (data, isinstance(data, int)),
            )
        )

        return _clone

    def float(self) -> Self:
        """Assert that the value under validation is a float.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "float",
                lambda data: (data, isinstance(data, float)),
            )
        )

        return _clone

    def positive(self) -> Self:
        """Assert that the value under validation is a positive number.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "positive",
                lambda data: (data, data is not None and data > 0),
            )
        )

        return _clone

    def negative(self) -> Self:
        """Assert that the value under validation is a negative number.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "negative",
                lambda data: (data, data is not None and data < 0),
            )
        )

        return _clone

    def non_negative(self) -> Self:
        """Assert that the value under validation is a non-negative number.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "non_negative",
                lambda data: (data, data is not None and data >= 0),
            )
        )

        return _clone

    def non_positive(self) -> Self:
        """Assert that the value under validation is a non-positive number.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "non_positive",
                lambda data: (data, data is not None and data <= 0),
            )
        )

        return _clone

    def multiple_of(self, base: int | float) -> Self:
        """Assert that the value under validation is a multiple of the given number.

        Args:
            base (int): the number to compare against.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "multiple_of",
                lambda data: (data, data is not None and data % base == 0),
            )
        )

        return _clone

    def step(self, base: int | float) -> Self:
        return self.multiple_of(base)

    def finite(self) -> Self:
        """Assert that the value under validation is a finite number.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "finite",
                lambda data: (data, data is not None and not math.isinf(data)),
            )
        )

        return _clone


def boolean() -> ZonBoolean:
    """Returns a validator for boolean data.

    Returns:
        ZonBoolean: The boolean data validator.
    """

    return ZonBoolean()


class ZonBoolean(Zon):
    """A Zon that validates that the data is a boolean."""

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, bool):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid boolean", path=[]))

        return data


def literal(value: Any, /) -> ZonLiteral:
    """Returns a validator for a given literal value.

    Args:
        value: the value that must be matched

    Returns:
        ZonBoolean: The literal data validator.
    """

    return ZonLiteral(value)


class ZonLiteral(Zon):
    """A Zon that validates that the data is one of the given literals."""

    def __init__(self, value: Any, /, **kwargs):
        super().__init__(**kwargs)
        self._value = value

    @property
    def value(self):
        return self._value

    def _default_validate(self, data: T, ctx: ValidationContext):
        if data != self._value:
            ctx.add_issue(
                ZonIssue(value=data, message=f"Expected {self._value}", path=[])
            )

        return data


def enum(options: Sequence[str], /) -> ZonEnum:
    """Returns a validator for an enum.

    Args:
        options: the values that must be matched

    Returns:
        ZodEnum: The enum data validator.
    """

    return ZonEnum(options)


class ZonEnum(Zon):
    """A Zon that validates that the data is one of the given values

    This class mimics the behavior of `zod`'s own enums, not TypeScript enums.
    """

    def __init__(self, options: Sequence[str], **kwargs):
        super().__init__(**kwargs)
        self._options: set[str] = options

    @property
    def enum(self) -> set[str]:
        """
        The enum variants that this validator allows.
        """
        return set(self._options)

    def _default_validate(self, data, ctx):
        if data not in self._options:
            ctx.add_issue(
                ZonIssue(
                    value=data, message=f"Expected one of {self._options}", path=[]
                )
            )

        return data

    def exclude(self, options: Sequence[str]) -> Self:
        """
        Excludes the given options from the enum.

        Args:
            options (Sequence[str]): the options to exclude.

        Returns:
            ZonEnum: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone._options = self._options - set(options)

        return _clone

    def extract(self, options: Sequence[str]) -> Self:
        """
        Extracts the given options from the enum.

        Args:
            options (Sequence[str]): the options to extract.

        Returns:
            ZonEnum: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone._options = self._options & set(options)

        return _clone


def record(properties: dict[str, Zon], /) -> ZonRecord:
    """Returns a validator for a record.

    Args:
        properties (dict[str, Zon]): the shape of the record

    Returns:
        ZonRecord: The record data validator.
    """

    return ZonRecord(properties)


class ZonRecord(Zon):
    """A Zon that validates that the data is a record with the provided shape."""

    class UnknownKeyPolicy(Enum):
        STRIP = auto()
        PASSTHROUGH = auto()
        STRICT = auto()

    def __init__(
        self,
        shape: Mapping[str, Zon],
        /,
        unknown_key_policy: UnknownKeyPolicy = UnknownKeyPolicy.STRIP,
        catchall: Zon | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._shape = shape
        self.unknown_key_policy = unknown_key_policy
        self._catchall = catchall

    def _default_validate(self, data, ctx: ValidationContext):

        if not isinstance(data, dict):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid object", path=[]))

            return data

        data_to_return = {}

        extra_keys: set[str] = {}
        if (
            self._catchall is not None
            or self.unknown_key_policy is not ZonRecord.UnknownKeyPolicy.STRIP
        ):
            extra_keys = set(data.keys()) - set(self._shape.keys())

        for key, zon in self._shape.items():
            # TODO: need to verify path
            # maybe instantiate new context here and compute path from there?

            # default to None since this way we also validate the attribute if it is optional
            validation_value = data.get(key, None)

            (validated, data_or_error) = zon.safe_validate(validation_value)

            if not validated:
                updated_issues = [
                    ZonIssue(
                        value=issue.value,
                        message=issue.message,
                        path=[key] + issue.path,
                    )
                    for issue in data_or_error.issues
                ]

                ctx.add_issues(updated_issues)
            elif data_or_error is not None:  # in case of optional data
                data_to_return[key] = data_or_error

        if self._catchall is None:
            match self.unknown_key_policy:
                case ZonRecord.UnknownKeyPolicy.STRIP:
                    # ignore extra keys
                    pass
                case ZonRecord.UnknownKeyPolicy.PASSTHROUGH:
                    data_to_return.update({k: data[k] for k in extra_keys})
                case ZonRecord.UnknownKeyPolicy.STRICT:
                    if len(extra_keys) > 0:
                        ctx.add_issue(
                            ZonIssue(
                                value=extra_keys,
                                message=f"Unexpected keys: {extra_keys}",
                                path=[],
                            )
                        )

        else:
            for key in extra_keys:
                value = data.get(key)

                (valid, data_or_error) = self._catchall.safe_validate(value)

                if not valid:
                    updated_issues = [
                        ZonIssue(
                            value=issue.value,
                            message=issue.message,
                            path=[key] + issue.path,
                        )
                        for issue in data_or_error.issues
                    ]

                    ctx.add_issues(updated_issues)
                elif data_or_error is not None:  # in case of optional data
                    data_to_return[key] = data_or_error

        return data_to_return

    @property
    def shape(self) -> Mapping[str, Zon]:
        return self._shape

    def keyof(self) -> ZonEnum:
        """Returns a validator for the keys of an object"""

        return enum(self.shape.keys())

    def extend(self, extra_properties: Mapping[str, Zon]) -> Self:
        """
        Extends the shape of the record with the given properties.

        Args:
            extra_properties (Mapping[str, Zon]): the properties to extend the shape with.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return ZonRecord(
            {**self.shape, **extra_properties},
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def merge(self, other: ZonRecord) -> Self:
        """
        Merges the shape of the record with the given properties.

        Args:
            other (ZonRecord): the properties to extend the shape with.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return self.extend(other.shape)

    def pick(self, attributes: Mapping[str, Literal[True]]) -> ZonRecord:
        """
        Picks the given attributes from the record.

        Args:
            attributes (Mapping[str, Literal[True]]): the attributes to pick.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return ZonRecord(
            {k: v for k, v in self.shape.items() if attributes.get(k, False)},
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def omit(self, attributes: Mapping[str, Literal[True]]) -> ZonRecord:
        """
        Omits the given attributes from the record.

        Args:
            attributes (Mapping[str, Literal[True]]): the attributes to omit.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return ZonRecord(
            {k: v for k, v in self.shape.items() if not attributes.get(k, False)},
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def partial(
        self, /, optional_properties: Mapping[str, Literal[True]] | None = None
    ) -> ZonRecord:
        """
        Marks the given attributes as optional.

        Args:
            optional_properties (Mapping[str, Literal[True]]): the attributes to mark as optional.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        if not optional_properties:
            optional_properties = {k: True for k in self.shape.keys()}

        return ZonRecord(
            {
                k: (v.optional() if optional_properties.get(k, False) else v)
                for k, v in self.shape.items()
            },
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def deep_partial(self) -> ZonRecord:
        """
        Marks all attributes as optional.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        def _partialify(v: Zon) -> ZonOptional:
            if isinstance(v, ZonRecord):
                return ZonRecord(
                    {k: _partialify(_v) for k, _v in v.shape.items()},
                ).optional()

            # if isinstance(v, ZonArray):
            #     return ZonArray(_partialify(v.item_type).unwrap()).optional()

            return v.optional()

        return ZonRecord(
            {k: _partialify(v) for k, v in self.shape.items()},
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def required(
        self, /, required_properties: Mapping[str, Literal[True]] | None = None
    ) -> ZonRecord:

        if not required_properties:
            required_properties = {k: True for k in self.shape.keys()}

        return ZonRecord(
            {
                k: (
                    (v.unwrap() if isinstance(v, ZonOptional) else v)
                    if required_properties.get(k, False)
                    else v
                )
                for k, v in self.shape.items()
            },
            unknown_key_policy=self.unknown_key_policy,
            catchall=self._catchall,
        )

    def passthrough(self) -> ZonRecord:
        """
        Returns a validator for the same record shape that adds unknown keys to the returned.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        # TODO: tests

        return ZonRecord(
            self.shape,
            unknown_key_policy=ZonRecord.UnknownKeyPolicy.PASSTHROUGH,
            catchall=self._catchall,
        )

    def strict(self) -> ZonRecord:
        """
        Returns a validator for the same record shape but that fails validation if the data under validation does not match this validator's shape exactly.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return ZonRecord(
            self.shape,
            unknown_key_policy=ZonRecord.UnknownKeyPolicy.STRICT,
            catchall=self._catchall,
        )

    def strip(self) -> ZonRecord:
        """
        Returns a validator for the same record shape that unknown keys from the returned data.

        Returns:
            ZonRecord: a new `ZonRecord` with the new policy
        """

        # TODO: tests

        return ZonRecord(
            self.shape,
            unknown_key_policy=ZonRecord.UnknownKeyPolicy.STRIP,
            catchall=self._catchall,
        )

    def catchall(self, catchall_validator: Zon) -> ZonRecord:
        """
        Returns a validator for the same record shape that pipes unknown keys and their values through a general, "catch-all" validator.

        Returns:
            ZonRecord: a new `ZonRecord` with the new catchall validator
        """

        return ZonRecord(
            self.shape,
            unknown_key_policy=self.unknown_key_policy,
            catchall=catchall_validator,
        )


def element_list(element: Zon, /) -> ZonList:
    """
    Returns a validator for an array with the given element type.

    Args:
        element (Zon): the element type of the array.

    Returns:
        ZonArray: a new `ZonArray` validator
    """

    return ZonList(element)


class ZonList(ZonContainer):
    """A Zon that validates that the input is a list with the given element type"""

    def __init__(self, element, **kwargs):
        super().__init__(**kwargs)

        self._element = element

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, list):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid list", path=[]))
            return data

        for i, element in enumerate(data):
            (valid, data_or_error) = self._element.safe_validate(element)

            if not valid:

                updated_issues = [
                    ZonIssue(
                        value=issue.value,
                        message=issue.message,
                        path=[str(i)] + issue.path,
                    )
                    for issue in data_or_error.issues
                ]

                ctx.add_issues(updated_issues)

        return data

    @property
    def element(self):
        return self._element

    def nonempty(self):
        """
        Returns a validator for a list with at least one element.

        Returns:
            ZonList: a new `ZonList` validator
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "nonempty",
                lambda data: (data, hasattr(data, "__len__") and len(data) > 0),
            )
        )

        return _clone


def union(options: Sequence[Zon], /) -> ZonUnion:
    """
    Returns a validator for a union of the given types.

    Args:
        options (Sequence[Zon]): the types to validate against.

    Returns:
        ZonUnion: a new `ZonUnion` validator
    """

    return ZonUnion(options)


class ZonUnion(Zon):
    """A Zon that validates that the input is one of the given types"""

    def __init__(self, options: Sequence[Zon], /, **kwargs):
        super().__init__(**kwargs)
        self._options = options

    @property
    def options(self) -> Sequence[Zon]:
        return self._options

    def _default_validate(self, data: T, ctx: ValidationContext):

        issues = []
        for option in self._options:
            (valid, data_or_error) = option.safe_validate(data)

            if valid:
                return data

            issues.extend(data_or_error.issues)

        if len(issues) > 0:
            ctx.add_issues(issues)
            ctx.add_issue(ZonIssue(value=data, message="Not a valid union", path=[]))

        return data


def element_tuple(items: Sequence[Zon], /) -> ZonTuple:
    """
    Returns a validator for a tuple with the given element types.

    Args:
        items (Sequence[Zon]): the element types of the tuple.

    Returns:
        ZonTuple: a new `ZonTuple` validator
    """

    return ZonTuple(items)


class ZonTuple(Zon):
    """A Zon that validates that the input is a tuple whose elements might have different types"""

    def __init__(self, items: Sequence[Zon], rest: Zon | None = None, /, **kwargs):
        super().__init__(**kwargs)
        self._items = items
        self._rest = rest

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, tuple):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid list", path=[]))
            return data

        if len(data) < len(self._items):
            ctx.add_issue(ZonIssue(value=data, message="Not enough elements", path=[]))
            return data

        if self._rest is None and len(data) > len(self._items):
            ctx.add_issue(ZonIssue(value=data, message="Too many elements", path=[]))
            return data

        for i, _validator in enumerate(self._items):
            if _validator is None:
                continue

            (valid, data_or_error) = _validator.safe_validate(data[i])

            if not valid:
                updated_issues = [
                    ZonIssue(
                        value=issue.value,
                        message=issue.message,
                        path=[str(i)] + issue.path,
                    )
                    for issue in data_or_error.issues
                ]

                ctx.add_issues(updated_issues)

        if self._rest is not None:
            for i, extra_value in enumerate(data[len(self.items) :]):
                (valid, data_or_error) = self._rest.safe_validate(extra_value)

                if not valid:
                    updated_issues = [
                        ZonIssue(
                            value=issue.value,
                            message=issue.message,
                            path=[str(i)] + issue.path,
                        )
                        for issue in data_or_error.issues
                    ]

                    ctx.add_issues(updated_issues)

        return data

    @property
    def items(self):
        return self._items

    def rest(self, rest: Zon) -> ZonTuple:
        """
        Returns a validator for a tuple that might accept more elements of a given type

        Args:
            rest (Zon): the element type of the rest of the tuple's elements.

        Returns:
            ZonTuple: a new `ZonTuple` validator
        """

        return ZonTuple(self._items, rest)


def anything() -> ZonAnything:
    """
    Returns a validator for anything.

    Returns:
        ZonAnything: a new `ZonAnything` validator
    """

    return ZonAnything()


class ZonAnything(Zon):
    """A Zon that validates that the input is anything"""

    def _default_validate(self, data: T, ctx: ValidationContext):
        return data


def never() -> ZonNever:
    """
    Returns a validator for nothing.

    Returns:
        ZonNever: a new `ZonNever` validator
    """

    return ZonNever()


class ZonNever(Zon):
    """A Zon that validates no input."""

    def _default_validate(self, data: T, ctx: ValidationContext):
        ctx.add_issue(ZonIssue(value=data, message="No data allowed", path=[]))
        return data
