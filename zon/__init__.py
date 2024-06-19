"""Validator package.

Flexible validation powered by Python with the expressiveness of a Zod-like API.
"""

# Why is this needed even?
from __future__ import annotations

__version__ = "2.0.0"
__author__ = "Nuno Pereira"
__email__ = "nunoafonso2002@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2023, Nuno Pereira"

# TODO: better typing.
# Things to consider:
# - Container and other collections.abc types
# - Typing with Self

import copy
from abc import ABC, abstractmethod
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
    # "ZonArray",
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
    # "ZonUnion",
]


@dataclass
class ValidationContext:
    """Context used throughout an entire validation run"""

    _error: ZonError = None
    path: list[str] = field(default_factory=list)

    def _ensure_error(self):
        if self._error is None:
            self._error = ZonError()

    def add_issue(self, issue: ZonIssue):
        """Adds the given `ZodIssue` to this context's `ZonError`"""
        self._ensure_error()
        self._error.add_issue(issue)

    def add_issues(self, issues: list[ZonIssue]):
        """Adds the given `ZodIssue`s to this context's `ZonError`"""
        self._ensure_error()
        self._error.add_issues(issues)

    def raise_error(self):
        """
        Raises the current validation error in this context if it exists.
        """

        raise self._error

    @property
    def dirty(self):
        return self._error is not None and len(self._error.issues) >= 0


T = TypeVar("T")


class ValidationRule:
    """
    Custom validation rul used to add more complex validation rules to an existing `Zon`
    """

    def __init__(
        self,
        name: str,
        fn: Callable[[T], bool],
        *,
        additional_data: Mapping[str, Any] = None,
    ):
        self.fn = fn
        self.name = name
        self.additional_data = additional_data if additional_data is not None else {}

    def check(self, data: Any, ctx: ValidationContext) -> bool:
        """
        Check this validation rule against the supplied data.

        Args:
            data (Any): the piece of data to be validated.
            ctx (ValidationContext): the context in which the validation is being run.

        Returns:
            bool: True if the data is valid, False otherwise.
        """

        valid = False
        try:
            valid = self.fn(data)

            if not valid:
                ctx.add_issue(
                    ZonIssue(
                        value=data,
                        message=f"Validation failed for type {self.name}",
                        path=[],
                    )
                )
        except validators.ValidationError as e:
            ctx.add_issue(
                ZonIssue(
                    value=data,
                    message=f"Validation failed for type {self.name}: {e}",
                    path=[],
                )
            )
            valid = False

        return valid


class Zon(ABC):
    """
    Base class for all Zons.

    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self, **kwargs):
        self.validators: list[ValidationRule] = []
        """validators that will run when 'validate' is invoked."""

        self._terminate_early = kwargs.get("terminate_early", False)

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    @abstractmethod
    def _default_validate(self, data: T, ctx: ValidationContext):
        """Default validation for any Zon validator

        The contract for this method is the same for any other `ValidationRule`:
        - If the validation succeeds, return True
        - If the validation false, raise a ZonError containing the relevant data.

        The default implementation raises a NotImplementedError.

        Args:
            data (Any): the piece of data to be validated.
            ctx (ValidationContext): the context of the validation.
        """

        raise NotImplementedError(
            "This method is not implemented for the base Zon class. You need to provide your "
        )

    @final
    def _validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            bool: True if the data is valid. This method will never return false as that case raises an error, as documented.

        Raises:
            ZonError: if validation against the supplied data fails.
            NotImplementedError: if the default validation rule was not overriden for this Zon object.
        """

        ctx = ValidationContext()

        def check_early_termination():
            if self._terminate_early and ctx.dirty:
                ctx.raise_error()

        try:
            self._default_validate(data, ctx)
        except NotImplementedError as ni:
            raise ni

        check_early_termination()

        for validator in self.validators:
            validator.check(data, ctx)

            check_early_termination()

        if ctx.dirty:
            ctx.raise_error()

        return True

    @final
    def validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
            ZonError: if validation fails.
        """
        if type(self) is Zon:  # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Zon class"
            )

        return self._validate(data)

    @final
    def safe_validate(
        self, data: T
    ) -> tuple[Literal[True], T] | tuple[Literal[False], ZonError]:
        """Validates the supplied data. This method is different from `validate` in the sense that
        it does not raise an error when validation fails. Instead, it returns an object encapsulating
        either a successful validation result or a validation error.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
            Exception: if any unexpected exception is encountered
        """

        try:
            self.validate(data)

            return (True, data)
        except ZonError as ze:
            return (False, ze)
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

    def optional(self) -> ZonOptional:
        """Returns a validator that validates that the data is valid for this validator if it exists.

        Returns:
            ZonOptional: The optional data validator.
        """

        return optional(self)


def intersection(zon1: Zon, zon2: Zon, *, fast_termination=False) -> ZonIntersection:
    """Returns a validator that validates that the data is valid for both validators supplied.

    Args:
        zon1 (Zon): the first validator
        zon2 (Zon): the second validator
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonIntersection: The intersection data validator.
    """
    return ZonIntersection(zon1, zon2, terminate_early=fast_termination)


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
            return

        (zon_2_parsed, data2_or_error) = self.zon2.safe_validate(data)

        if not zon_2_parsed:
            ctx.add_issues(data2_or_error.issues)
            return


def optional(zon: Zon, fast_termination=False) -> ZonIntersection:
    """Returns a validator that validates that the data is valid for this validator if it exists.

    Args:
        zon (Zon): the supplied validator
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonIntersection: The intersection data validator.
    """
    return ZonOptional(zon, terminate_early=fast_termination)


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
                lambda data: hasattr(data, "__len__") and len(data) <= max_value,
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
                lambda data: hasattr(data, "__len__") and len(data) >= min_value,
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
                lambda data: hasattr(data, "__len__") and len(data) == length,
            )
        )

        return _clone


def string(*, fast_termination=False) -> ZonString:
    """Returns a validator for string data.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonString: The string data validator.
    """

    return ZonString(terminate_early=fast_termination)


class ZonString(ZonContainer):
    """A Zon that validates that the data is a string.

    For all purposes, a string is a container of characters.
    """

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, str):
            ctx.add_issue(ZonIssue(value=data, message="Not a string", path=[]))

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
                validators.email,
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
                validators.url,
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
                validators.uuid,
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
                lambda data: re.match(regex, data) is not None,
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
                lambda data: needle in data,
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
                lambda data: data.startswith(prefix),
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
                lambda data: data.endswith(suffix),
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
                lambda data: _datetime_regex(opts).match(data) is not None,
            )
        )

        return _clone

    def ip(self, opts: Mapping[str, Any] | None = None) -> Self:
        """Assert that the value under validation is a valid IP address.

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
                lambda data: _validator(data, opts),
            )
        )

        return _clone


def number(*, fast_termination=False) -> ZonNumber:
    """Returns a validator for numeric data.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonNumber: The number data validator.
    """

    return ZonNumber(terminate_early=fast_termination)


class ZonNumber(Zon, HasMax, HasMin):
    """A Zon that validates that the data is a number."""

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, (int, float)):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid number", path=[]))

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
                lambda data: data is not None and data > min_ex,
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
                lambda data: data is not None and data >= min_in,
            )
        )

        return _clone

    def max(self, max_value: int | float) -> Self:
        return self.gte(max_value)

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
                lambda data: data is not None and data < max_ex,
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
                lambda data: data is not None and data <= max_in,
            )
        )

        return _clone

    def min(self, min_value: int | float) -> Self:
        return self.lte(min_value)

    def int(self) -> Self:
        """Assert that the value under validation is an integer.

        Returns:
            ZonNumber: a new `Zon` with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "int",
                lambda data: isinstance(data, int),
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
                lambda data: isinstance(data, float),
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
                lambda data: data is not None and data > 0,
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
                lambda data: data is not None and data < 0,
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
                lambda data: data is not None and data >= 0,
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
                lambda data: data is not None and data <= 0,
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
                lambda data: data is not None and data % base == 0,
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
                lambda data: data is not None and not math.isinf(data),
            )
        )

        return _clone


def boolean(*, fast_termination=False) -> ZonBoolean:
    """Returns a validator for boolean data.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonBoolean: The boolean data validator.
    """

    return ZonBoolean(terminate_early=fast_termination)


class ZonBoolean(Zon):
    """A Zon that validates that the data is a boolean."""

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, bool):
            ctx.add_issue(ZonIssue(value=data, message="Not a valid boolean", path=[]))


def literal(value: Any, /, *, fast_termination=False) -> ZonLiteral:
    """Returns a validator for a given literal value.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.
        value: the value that must be matched

    Returns:
        ZonBoolean: The literal data validator.
    """

    return ZonLiteral(value, terminate_early=fast_termination)


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


def enum(options: Sequence[str], /, *, fast_termination=False) -> ZonEnum:
    """Returns a validator for an enum.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.
        options: the values that must be matched

    Returns:
        ZodEnum: The enum data validator.
    """

    return ZonEnum(options, terminate_early=fast_termination)


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


def record(properties: dict[str, Zon], /, *, fast_termination=False) -> ZonRecord:
    """Returns a validator for a record.

    Args:
        properties (dict[str, Zon]): the shape of the record
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonRecord: The record data validator.
    """

    return ZonRecord(properties, terminate_early=fast_termination)


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

            if self._terminate_early:
                return

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
                ctx.add_issues(data_or_error.issues)

                if self._terminate_early:
                    return

        if self._catchall is None:
            match self.unknown_key_policy:
                case ZonRecord.UnknownKeyPolicy.STRIP:
                    # ignore extra keys
                    pass
                case ZonRecord.UnknownKeyPolicy.PASSTHROUGH:
                    # TODO: rework validation to return data

                    # data_to_return.extend({k: data[k] for k in extra_keys})

                    pass
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
                    ctx.add_issues(data_or_error.issues)

                    if self._terminate_early:
                        return

    @property
    def shape(self) -> Mapping[str, Zon]:
        return self._shape

    def keyof(self) -> ZonEnum:
        """Returns a validator for the keys of an object"""

        return enum(self._shape.keys())

    def extend(self, extra_properties: Mapping[str, Zon]) -> Self:
        """
        Extends the shape of the record with the given properties.

        Args:
            extra_properties (Mapping[str, Zon]): the properties to extend the shape with.

        Returns:
            ZonRecord: a new `ZonRecord` with the new shape
        """

        return ZonRecord(
            {**self.shape, **extra_properties}, terminate_early=self._terminate_early
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
                    terminate_early=v._terminate_early,
                ).optional()

            # if isinstance(v, ZonArray):
            #     return ZonArray(_partialify(v.item_type))

            return v.optional()

        return ZonRecord(
            {k: _partialify(v) for k, v in self.shape.items()},
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
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
            terminate_early=self._terminate_early,
        )
