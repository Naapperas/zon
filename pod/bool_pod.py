"""Class and methods related to the PodBool validator."""

from .base_pod import Pod
from .error import ValidationError


class PodBoolean(Pod):
    """A Pod that validates that the data is a boolean."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, bool):
            self._add_error(ValidationError(f"Expected boolean, got {type(data)}"))
            return False
        return True
