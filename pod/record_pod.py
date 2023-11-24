"""Class and methods related to the PodRecord validator."""

from .base_pod import Pod
from .error import ValidationError

# TODO: better error messages


class PodRecord(Pod):
    """A Pod that validates that the data is an object with the specified properties."""

    def __init__(self, properties: dict[str, Pod]):
        super().__init__()
        self.properties = properties

    def _validate(self, data):
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
