"""Class and methods related to ZonInteger validator."""

from zon.error import ZonError

import zon.number as zon_number


class ZonInteger(zon_number.ZonNumber):
    """A Zon that validates that the data is an integer."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, int):
            self._add_error(ZonError(f"Expected integer, got {type(data)}"))
            return False
        return True
