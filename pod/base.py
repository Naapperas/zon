"""File containing base Pod class and helper utilities."""
from abc import ABC, abstractmethod
from typing import Any, final

from .error import ValidationError


class Pod(ABC):
    """Base class for all Pods.
    A Pod is the basic unit of validation in Pod.
    It is used to validate data, and can be composed with other Pods
    to create more complex validations.
    """

    def __init__(self):
        self.errors: list[ValidationError] = []

    def _add_error(self, error: ValidationError):
        self.errors.append(error)

    @abstractmethod
    def _validate(self, data: Any) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
    
    @final
    def validate(self, data):
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Pod class.
        """
        if isinstance(self, Pod):
            raise NotImplementedError("validate() method not implemented on base Pod class")

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

    def _validate(self, data):
        if data is None:
            return True
        return self.pod.validate(data)


class PodAnd(Pod):
    """A Pod that validates that the data is valid for both this Pod and the supplied Pod."""

    def __init__(self, pod1, pod2):
        super().__init__()
        self.pod1 = pod1
        self.pod2 = pod2

    def _validate(self, data):
        if not (self.pod1.validate(data) and self.pod2.validate(data)):
            for error in self.pod1.errors:
                self._add_error(error)

            for error in self.pod2.errors:
                self._add_error(error)

            return False

        return True
