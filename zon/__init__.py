"""Validator package.

Flexible validation powered by Python with the expressiveness of a Zod-like API.
"""

from __future__ import annotations

__version__ = "2.0.0"
__author__ = "Nuno Pereira"
__email__ = "nunoafonso2002@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2023, Nuno Pereira"

import copy
from abc import ABC, abstractmethod
from typing import Any, Self, TypeVar, final, Literal
from collections.abc import Callable
from dataclasses import dataclass, field
import re

import validators

from .error import ZonError, ZonIssue
from .traits import HasMax, HasMin


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
    def __init__(self, name: str, fn: Callable[[T], bool], *, additional_data: dict[str, Any] = {}):
        self.fn = fn
        self.name = name
        self.additional_data = additional_data

    def check(self, data: Any, ctx: ValidationContext) -> bool:
        valid = self.fn(data)

        if not valid:
            ctx.add_issue(
                ZonIssue(
                    value=data,
                    message=f"Validation failed for type {self.name}",
                    path=[],
                )
            )

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
    def safe_validate(self, data: T) -> tuple[Literal[True], T] | tuple[Literal[False], ZonError]:
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
                lambda data: hasattr(data, '__len__') and len(data) <= max_value,
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
                lambda data: hasattr(data, '__len__') and len(data) >= min_value,
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
                lambda data: hasattr(data, '__len__') and len(data) == length,
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

    For all purposes, a string is a collection of characters.
    """

    def _default_validate(self, data: T, ctx: ValidationContext):
        if not isinstance(data, str):
            ctx.add_issue(ZonIssue(value=data, message="Not a string", path=[]))

    def email(self) -> Self:
        """
        Assert that the value under validation is a valid email.
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
        Assert that the value under validation is a valid url.
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
            ZonString: a new zon with the validation rule added
        """

        raise NotImplementedError

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "emoji",
                lambda data: re.compile(r"^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$").match(data) is not None,
            )
        )

        return _clone
    
    def uuid(self) -> Self:
        """Assert that the value under validation is a valid uuid.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        _clone = self._clone()

        _clone.validators.append(
            ValidationRule(
                "uuid",
                validators.uuid,
            )
        )

        return _clone