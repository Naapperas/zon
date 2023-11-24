"""Class and methods related to the PodFloat validator."""

from .base_pod import Pod
from .error import ValidationError


class PodFloat(Pod):
    """A Pod that validates that the data is a floating point number."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, float):
            self._add_error(ValidationError(f"Expected float, got {type(data)}"))
            return False
        return True
