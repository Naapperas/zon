"""File containing base Pod class and helper utilities."""
from abc import ABC, abstractmethod
from typing import final, Callable, TypeVar

from .error import ValidationError

T = TypeVar("T")
ValidationRule = tuple[Callable[[T], bool], Callable[[T, str], str]]


class Pod(ABC):
    """Base class for all Pods.
    A Pod is the basic unit of validation in Pod.
    It is used to validate data, and can be composed with other Pods
    to create more complex validations.
    """

    def __init__(self):
        self.errors: list[ValidationError] = []
        """List of validation errors accumulated"""

        self.validators: dict[str, ValidationRule] = {}
        """validators that will run when 'validate' is invoked."""

    def _add_error(self, error: ValidationError):
        self.errors.append(error)

    @abstractmethod
    def _setup(self) -> None:
        """Sets up the Pod with default validation rules.

        This implies that a '_default_' rule will be present, otherwise the validation fails

        This method is called when the Pod is created.
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
            raise ValidationError(
                f"Pod of type {type(self)} must have a valid '_default_' rule"
            )

        passes = True

        for name, (validator, error_generator) in self.validators.items():
            if not validator(data):
                passes = False
                self._add_error(ValidationError(error_generator(data, name)))

        return passes

    @final
    def validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Pod class.
        """
        if type(self) is Pod: # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Pod class"
            )

        return self._validate(data)

    def and_also(self, pod: "Pod") -> "PodAnd":
        """Creates a new Pod that validates that
        the data is valid for both this Pod and the supplied Pod.

        Args:
            pod (Pod): the Pod to be validated.

        Returns:
            PodAnd: a new validator that validates that
            the data is valid for both this Pod and the supplied Pod.
        """
        return PodAnd(self, pod)


def optional(pod: Pod) -> "PodOptional":
    """Marks this validation chain as optional, making it so the data supplied need not be defined.

    Args:
        pod (Pod): the validator to be marked as optional.

    Returns:
        PodOptional: a new validator that makes any validation optional.
    """
    return PodOptional(pod)


class PodOptional(Pod):
    """A Pod that makes its data validation optional."""

    def __init__(self, pod):
        super().__init__()
        self.pod = pod

    def _setup(self):
        self.validators["_default_"] = (self._default_validate, lambda _: "")

    def _default_validate(self, data):
        if data is None:
            return True
        return self.pod.validate(data)


class PodAnd(Pod):
    """A Pod that validates that the data is valid for both this Pod and the supplied Pod."""

    def __init__(self, pod1, pod2):
        super().__init__()
        self.pod1 = pod1
        self.pod2 = pod2

    def _setup(self):
        self.validators["_default_"] = (self._default_validate, lambda _: "")

    def _default_validate(self, data):
        if not (self.pod1.validate(data) and self.pod2.validate(data)):
            for error in self.pod1.errors:
                self._add_error(error)

            for error in self.pod2.errors:
                self._add_error(error)

            return False

        return True
