"""Class and methods related to the PodFloat validator."""

from .base import Pod
from .error import ValidationError


class PodFloat(Pod):
    """A Pod that validates that the data is a floating point number."""

    def validate(self, data):
        if not isinstance(data, float):
            self._add_error(ValidationError(f"Expected float, got {type(data)}"))
            return False
        return True
