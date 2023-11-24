"""File containing base Zon class and helper utilities."""
from abc import ABC, abstractmethod
from typing import final, Callable, TypeVar, Self
import copy

from .error import ValidationError

T = TypeVar("T")
ValidationRule = Callable[[T], bool]


class Zon(ABC):
    """Base class for all Zons.
    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self):
        self.errors: list[ValidationError] = []
        """List of validation errors accumulated"""

        self.validators: dict[str, ValidationRule] = {}
        """validators that will run when 'validate' is invoked."""

        self._setup()

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    def _add_error(self, error: ValidationError):
        self.errors.append(error)

    @abstractmethod
    def _setup(self) -> None:
        """Sets up the Zon with default validation rules.

        This implies that a '_default_' rule will be present, otherwise the validation fails.

        This method is called when the Zon is created.
        """

    @final
    def _validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            bool: True if the data is valid, False otherwise.
        """

        if "_default_" not in self.validators or not self.validators["_default_"]:
            self._add_error(
                ValidationError(
                    f"Zon of type {type(self)} must have a valid '_default_' rule"
                )
            )
            return False

        # TODO: better error messages
        return all(validator(data) for (_, validator) in self.validators.items())

    @final
    def validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
        """
        if type(self) is Zon:  # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Zon class"
            )

        return self._validate(data)

    def and_also(self, zon: "Zon") -> "ZonAnd":
        """Creates a new Zon that validates that
        the data is valid for both this Zon and the supplied Zon.

        Args:
            zon (Zon): the Zon to be validated.

        Returns:
            ZonAnd: a new validator that validates that
            the data is valid for both this Zon and the supplied Zon.
        """
        return ZonAnd(self, zon)

    def __and__(self, zon: "Zon") -> "ZonAnd":
        return self.and_also(zon)


def optional(zon: Zon) -> "ZonOptional":
    """Marks this validation chain as optional, making it so the data supplied need not be defined.

    Args:
        zon (Zon): the validator to be marked as optional.

    Returns:
        ZonOptional: a new validator that makes any validation optional.
    """
    return ZonOptional(zon)


class ZonOptional(Zon):
    """A Zon that makes its data validation optional."""

    def __init__(self, zon):
        super().__init__()
        self.zon = zon

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if data is None:
            return True
        return self.zon.validate(data)


class ZonAnd(Zon):
    """A Zon that validates that the data is valid for both this Zon and the supplied Zon."""

    def __init__(self, zon1, zon2):
        super().__init__()
        self.zon1 = zon1
        self.zon2 = zon2

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not (self.zon1.validate(data) and self.zon2.validate(data)):
            for error in self.zon1.errors:
                self._add_error(error)

            for error in self.zon2.errors:
                self._add_error(error)

            return False

        return True
