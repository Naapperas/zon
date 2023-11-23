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
    def __init__(self):
        self.errors: list[ValidationError] = []

    def _add_error(self, error: ValidationError):
        self.errors.append(error)

    @abstractmethod
    def validate(self, data):
        raise NotImplementedError("validate() method not implemented on base Pod class")


def optional(pod: Pod) -> "PodOptional":
    return PodOptional(pod)


def number() -> "PodNumber":
    return PodNumber()


def integer() -> "PodInteger":
    return PodInteger()


def floating_point() -> "PodFloat":
    return PodFloat()


def boolean() -> "PodBoolean":
    return PodBoolean()


def string() -> "PodString":
    return PodString()


def element_list(element_type: "Pod") -> "PodList":
    return PodList(element_type)


def union(types: list["Pod"]) -> "PodUnion":
    return PodUnion(types)


def record(properties: dict[str, "Pod"]) -> "PodObject":
    return PodObject(properties)


class PodOptional(Pod):
    """Marks a Pod as optional."""

    def __init__(self, pod):
        super().__init__()
        self.pod = pod

    def validate(self, data):
        if data is None:
            return True
        return self.pod.validate(data)


class PodNumber(Pod):
    def validate(self, data):
        if not isinstance(data, int) and not isinstance(data, float):
            self._add_error(
                ValidationError("Expected number, got {}".format(type(data)))
            )
            return False
        return True


class PodInteger(Pod):
    def validate(self, data):
        if not isinstance(data, int):
            self._add_error(
                ValidationError("Expected integer, got {}".format(type(data)))
            )
            return False
        return True


class PodFloat(Pod):
    def validate(self, data):
        if not isinstance(data, float):
            self._add_error(
                ValidationError("Expected float, got {}".format(type(data)))
            )
            return False
        return True


class PodBoolean(Pod):
    def validate(self, data):
        if not isinstance(data, bool):
            self._add_error(
                ValidationError("Expected boolean, got {}".format(type(data)))
            )
            return False
        return True


class PodString(Pod):
    def validate(self, data):
        if not isinstance(data, str):
            self._add_error(
                ValidationError("Expected string, got {}".format(type(data)))
            )
            return False
        return True


class PodList(Pod):
    def __init__(self, element_type: Pod):
        super().__init__()
        self.element_type = element_type

    def validate(self, data):
        if not isinstance(data, list):
            self._add_error(ValidationError("Expected list, got {}".format(type(data))))
            return False

        error = False
        for i, element in enumerate(data):
            if not self.element_type.validate(element):
                self._add_error(
                    ValidationError(
                        "Element {} of list failed validation: {}".format(i, element)
                    )
                )

                error = True

        if error:
            for error in self.element_type.errors:
                self._add_error(ValidationError(f"Error validating elements: {error}"))

        return not error


class PodUnion(Pod):
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
    def __init__(self, properties: dict[str, Pod]):
        super().__init__()
        self.properties = properties

    def validate(self, data):
        if not isinstance(data, dict):
            self._add_error(
                ValidationError("Expected object, got {}".format(type(data)))
            )
            return False

        error = False
        for key, pod in self.properties.items():
            if not pod.validate(data.get(key)):
                self._add_error(
                    ValidationError(
                        "Property {} failed validation: {}".format(key, data.get(key))
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
