"""The main file containing all the validators and types used throughout Pod"""
from abc import ABC, abstractmethod


class ValidationError(Exception):
    """Validation error thrown when a validation fails."""

    def __init__(self, message: str):
        """Builds a new ValidationError with the supplied message.

        Args:
            message (str): The message to be displayed when the exception is thrown.
        """
        super()
        self.message = message

    def __str__(self):
        """Used to covert this exception into a string."""

        return repr(self.message)

    def __repr__(self) -> str:
        """Used to covert this exception into a string."""

        return f"ValidationError({self.message})"


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
    def validate(self, data):
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Pod class.
        """
        raise NotImplementedError("validate() method not implemented on base Pod class")


def optional(pod: Pod) -> "PodOptional":
    """Marks this validation chain as optional, making it so the data supplied need not be defined.

    Args:
        pod (Pod): the validator to be marked as optional.

    Returns:
        PodOptional: a new validator that makes any validation optional.
    """
    return PodOptional(pod)


def number() -> "PodNumber":
    """Creates a new Pod that validates that the data is a number, i.e., an int or a float.

    Returns:
        PodNumber: a new validator that validates that the data is a number.
    """
    return PodNumber()


def integer() -> "PodInteger":
    """Creates a new Pod that validates that the data is an integer.

    Returns:
        PodInteger: a new validator that validates that the data is an integer
    """
    return PodInteger()


def floating_point() -> "PodFloat":
    """Creates a new Pod that validates that the data is a floating point number.

    Returns:
        PodFloat: a new validator that validates that the data is a floating point number.
    """
    return PodFloat()


def boolean() -> "PodBoolean":
    """Creates a new Pod that validates that the data is a boolean.

    Returns:
        PodBoolean: a new validator that validates that the data is a boolean.
    """
    return PodBoolean()


def string() -> "PodString":
    """Creates a new Pod that validates that the data is a string.

    Returns:
        PodString: a new validator that validates that the data is a string.
    """
    return PodString()


def element_list(element_type: "Pod") -> "PodList":
    """Creates a new Pod that validates that the data is a list of elements of the specified type.

    Args:
        element_type (Pod): the type of the elements of the list.

    Returns:
        PodList: a new validator that validates that the data is
        a list of elements of the specified type.
    """
    return PodList(element_type)


def union(types: list["Pod"]) -> "PodUnion":
    """Creates a new Pod that validates that the data is one of the specified types.

    Args:
        types (list[Pod]): the types of the data to be validated.

    Returns:
        PodUnion: a new validator that validates that the data is one of the specified types.
    """
    return PodUnion(types)


def record(properties: dict[str, "Pod"]) -> "PodObject":
    """Creates a new Pod that validates that the data is an object with the specified properties.

    Args:
        properties (dict[str, Pod]): the properties of the object to be validated.

    Returns:
        PodObject: a new validator that validates that the data is
        an object with the specified properties.
    """
    return PodObject(properties)


class PodOptional(Pod):
    """A Pod that makes its data validation optional."""

    def __init__(self, pod):
        super().__init__()
        self.pod = pod

    def validate(self, data):
        if data is None:
            return True
        return self.pod.validate(data)


class PodNumber(Pod):
    """A Pod that validates that the data is a number, i.e., an int or a float."""

    def validate(self, data):
        if not isinstance(data, int) and not isinstance(data, float):
            self._add_error(ValidationError(f"Expected number, got {type(data)}"))
            return False
        return True


class PodInteger(Pod):
    """A Pod that validates that the data is an integer."""

    def validate(self, data):
        if not isinstance(data, int):
            self._add_error(ValidationError(f"Expected integer, got {type(data)}"))
            return False
        return True


class PodFloat(Pod):
    """A Pod that validates that the data is a floating point number."""

    def validate(self, data):
        if not isinstance(data, float):
            self._add_error(ValidationError(f"Expected float, got {type(data)}"))
            return False
        return True


class PodBoolean(Pod):
    """A Pod that validates that the data is a boolean."""

    def validate(self, data):
        if not isinstance(data, bool):
            self._add_error(ValidationError(f"Expected boolean, got {type(data)}"))
            return False
        return True


class PodString(Pod):
    """A Pod that validates that the data is a string."""

    def validate(self, data):
        if not isinstance(data, str):
            self._add_error(ValidationError(f"Expected string, got {type(data)}"))
            return False
        return True


class PodList(Pod):
    """A Pod that validates that the data is a list of elements of the specified type."""

    def __init__(self, element_type: Pod):
        super().__init__()
        self.element_type = element_type

    def validate(self, data):
        if not isinstance(data, list):
            self._add_error(ValidationError(f"Expected list, got {type(data)}"))
            return False

        error = False
        for i, element in enumerate(data):
            if not self.element_type.validate(element):
                self._add_error(
                    ValidationError(f"Element {i} of list failed validation: {element}")
                )

                error = True

        if error:
            for error in self.element_type.errors:
                self._add_error(ValidationError(f"Error validating elements: {error}"))

        return not error


class PodUnion(Pod):
    """A Pod that validates that the data is one of the specified types."""

    def __init__(self, types: list[Pod]):
        super().__init__()
        self.types = types

    def validate(self, data):
        if any(pod.validate(data) for pod in self.types):
            return True

        for pod in self.types:
            for error in pod.errors:
                self._add_error(error)

        return False


class PodObject(Pod):
    """A Pod that validates that the data is an object with the specified properties."""

    def __init__(self, properties: dict[str, Pod]):
        super().__init__()
        self.properties = properties

    def validate(self, data):
        if not isinstance(data, dict):
            self._add_error(ValidationError(f"Expected object, got {type(data)}"))
            return False

        error = False
        for key, pod in self.properties.items():
            if not pod.validate(data.get(key)):
                self._add_error(
                    ValidationError(
                        f"Property {key} failed validation: {data.get(key)}"
                    )
                )
                error = True

        if error:
            for pod in self.properties.values():
                for error in pod.errors:
                    self._add_error(
                        ValidationError(f"Error validating properties: {error}")
                    )

        return not error
