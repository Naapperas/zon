"""Class and methods related to the ZonNone validator."""

from .base import Zon
from .error import ValidationError


class ZonNone(Zon):
    """A Zon that validates that the data is None."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if data is not None:
            self._add_error(ValidationError(f"Expected None, got {type(data)}"))
            return False
        return True
