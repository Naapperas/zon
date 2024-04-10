"""Class and methods related to the ZonFloat validator."""

from zon.error import ZonError

from . import ZonNumber


class ZonFloat(ZonNumber):
    """A Zon that validates that the data is a floating point number."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, float):
            self._add_error(ZonError(f"Expected float, got {type(data)}"))
            return False
        return True
