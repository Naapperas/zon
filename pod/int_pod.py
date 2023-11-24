"""Class and methods related to PodInt validator."""

from .base_pod import Pod
from .error import ValidationError


class PodInteger(Pod):
    """A Pod that validates that the data is an integer."""

    def _validate(self, data):
        if not isinstance(data, int):
            self._add_error(ValidationError(f"Expected integer, got {type(data)}"))
            return False
        return True
