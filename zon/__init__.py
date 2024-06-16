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
from typing import Callable, Self, TypeVar, final
from dataclasses import dataclass, field

from .error import ZonError, ZonIssue
from .traits import HasMax, HasMin

@dataclass
class ValidationContext:
    """Context used throughout an entire validation run
    """

    _error: ZonError = None
    path: list[str] = field(default_factory=list)

    def _ensure_error(self):
        if self._error is None:
            self._error = ZonError()

    def add_issue(self, issue: ZonIssue):
        """Adds the given `ZodIssue` to this context's `ZonError`
        """
        self._ensure_error()
        self._error.add_issue(issue)

    def add_issues(self, issues: list[ZonIssue]):
        """Adds the given `ZodIssue`s to this context's `ZonError`
        """
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
ValidationRule = Callable[[T, ValidationContext], bool]

class Zon(ABC):
    """
    Base class for all Zons.

    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self, **kwargs):
        self.validators: dict[str, ValidationRule] = {}
        """validators that will run when 'validate' is invoked."""

        self._terminate_early = kwargs.get("terminate_early", False)

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    @abstractmethod
    def _default_validate(self, data: T, ctx: ValidationContext) -> bool:
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

        try:
            _passed = self._default_validate(data, ctx)
        except ZonError as ze:
            if self._terminate_early:
                # since we want to terminate early, we can just directly raise the error
                raise ze

            ctx.add_issues(ze.issues)
        except NotImplementedError as ni:
            raise ni

        for validator_type, validator in self.validators.items():
            try:
                _passed = validator(data, ctx)

                return True
            except ZonError as ze:
                ctx.add_issues(ze.issues)

                if self._terminate_early:
                    # Since we want to terminate early, we can just directly raise the error
                    # Following the sequence of the code, we are guaranteed to have errors at this point.
                    ctx.raise_error()

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
    def safe_validate(self, data: T) -> tuple[bool, T] | tuple[bool, ZonError]:
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

    def max(self, max_value: int | float):
        """Validates that this container as at most `max_value` elements (exclusive).

        Args:
            max_value (int | float): the maximum number of elements that this container can have
        """

        # TODO: add check

    def min(self, min_value: int | float):
        """Validates that this container as at least `max_value` elements (exclusive).

        Args:
            min_value (int | float): the minimum number of elements that this container can have
        """

        # TODO: add check

    def length(self, length: int):
        """Validates that this container as exactly `length` elements.

        Args:
            length (int): the exact number of elements that this container can have
        """

        # TODO: add check


def string(*, fast_termination=False) -> ZonString:
    """Returns a validator for string data.

    Args:
        fast_termination (bool, optional): whether this validator's validation should stop as soon as an error occurs. Defaults to False.

    Returns:
        ZonString: The string data validator.
    """
    return ZonString(fast_termination=fast_termination)


class ZonString(ZonContainer):
    """A Zon that validates that the data is a string.

    For all purposes, a string is a collection of characters.
    """

    def _default_validate(self, data: T, ctx: ValidationContext) -> bool:

        if not isinstance(data, str):
            ctx.add_issue(ZonIssue(value=data, message="Not a string", path=[]))

        return True
