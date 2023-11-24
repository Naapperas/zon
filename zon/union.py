"""Class and methods related to the ZonUnion validator."""

from .base import Zon


class ZonUnion(Zon):
    """A Zon that validates that the data is one of the specified types."""

    def __init__(self, types: list[Zon]):
        super().__init__()
        self.types = types

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if any(zon.validate(data) for zon in self.types):
            return True

        for zon in self.types:
            for error in zon.errors:
                self._add_error(error)

        return False
