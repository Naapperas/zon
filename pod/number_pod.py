"""Class and methods related to the PodNumber validator"""

from .base_pod import Pod
from .error import ValidationError


class PodNumber(Pod):
    """A Pod that validates that the data is a number, i.e., an int or a float."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, int) and not isinstance(data, float):
            self._add_error(ValidationError(f"Expected number, got {type(data)}"))
            return False
        return True
