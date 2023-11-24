"""Class and methods related to the PodFloat validator."""

from pod.error import ValidationError

from . import PodNumber


class PodFloat(PodNumber):
    """A Pod that validates that the data is a floating point number."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, float):
            self._add_error(ValidationError(f"Expected float, got {type(data)}"))
            return False
        return True
