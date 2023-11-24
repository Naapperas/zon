"""Class and methods related to the PodString validator."""

from .base_pod import Pod
from .error import ValidationError


class PodString(Pod):
    """A Pod that validates that the data is a string."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, str):
            self._add_error(ValidationError(f"Expected string, got {type(data)}"))
            return False
        return True
