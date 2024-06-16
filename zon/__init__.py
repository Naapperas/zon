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

from .error import ZonError, ZonIssue
from .traits import HasMax, HasMin

T = TypeVar("T")
ValidationRule = Callable[[T], bool]


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
    def _default_validate(self, data: T) -> bool:
        """Default validation for any Zon validator

        The contract for this method is the same for any other `ValidationRule`:
        - If the validation succeeds, return True
        - If the validation false, raise a ZonError containing the relevant data
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

        _error: ZonError = None

        def _update_error(ze: ZonError):
            nonlocal _error
            if not _error:
                _error = ze
            else:
                _error.add_issues(ze.issues)

        try:
            _passed = self._default_validate(data)
        except ZonError as ze:
            if self._terminate_early:
                raise ze

            _update_error(ze)
        except NotImplementedError as ni:
            raise ni

        for validator_type, validator in self.validators.items():
            try:
                _passed = validator(data)

                return True
            except ZonError as ze:
                _update_error(ze)

                if self._terminate_early:
                    raise _error from ze

        if _error is not None:
            raise _error from None

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


def string(*, fast_termination = False) -> ZonString:
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

    def _default_validate(self, data: T) -> bool:

        if not isinstance(data, str):

            err = ZonError()
            err.add_issue(ZonIssue(value=data, message="Not a string", path=[]))

            raise err
        
        return True
