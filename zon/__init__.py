"""Validator package.

The purpose of this package is to provide a set of functions to validate data, using a Zod-like syntax.
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

from .error import ZonError

T = TypeVar("T")
ValidationRule = Callable[[T], bool]


class Zon(ABC):
    """
    Base class for all Zons.
    
    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self):
        self.errors: list[ZonError] = []
        """List of validation errors accumulated"""

        self.validators: dict[str, ValidationRule] = {}
        """validators that will run when 'validate' is invoked."""

        self._setup()

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    def _add_error(self, error: ZonError):
        """Adds an error to this Zon's error output.

        Args:
            error (ZonError): the validation error to add.
        """
        self.errors.append(error)

    @abstractmethod
    def _default_validate(self) -> bool:
        """Default validation for any Zon validator

        The contract for this method is the same for any other ValidationRule:
        - If the validation succeeds, return True
        - If the validation false, raise a ZonError containing the relevant data
        """

        raise NotImplementedError("This method is not implemented for the base Zon class. You need to provide your ")

    @final
    def _validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            bool: True if the data is valid. This method will never return false as that case raises an error, as documented.

        Raises:
            ZonError: if validation against the supplied data fails.
        """

        for validator_type, validator in self.validators.items():
            try:
                _passed = validator(data)

                return True
            except ZonError as ze:
                pass

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
            Exception: if validation fails
        """

        try:
            self.validate(data)

            return (True, data)
        except ZonError as ze:
            return (False, ze)
        except Exception as e:
            raise e