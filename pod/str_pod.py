"""Class and methods related to the PodString validator."""

from .base import Pod, ValidationError


class PodString(Pod):
    """A Pod that validates that the data is a string."""

    def validate(self, data):
        if not isinstance(data, str):
            self._add_error(ValidationError(f"Expected string, got {type(data)}"))
            return False
        return True
