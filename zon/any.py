"""Class and methods related to the ZonAny validator."""

from .base import Zon


class ZonNone(Zon):
    """A Zon that validates that the data is any data type."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, _data):
        return True
