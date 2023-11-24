"""Class and methods related to the ZonRecord validator."""

from .base import Zon
from .error import ValidationError

# TODO: better error messages


class ZonRecord(Zon):
    """A Zon that validates that the data is an object with the specified properties."""

    def __init__(self, properties: dict[str, Zon]):
        super().__init__()
        self.properties = properties

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, dict):
            self._add_error(ValidationError(f"Expected object, got {type(data)}"))
            return False

        error = False
        for key, zon in self.properties.items():
            if not zon.validate(data.get(key)):
                self._add_error(
                    ValidationError(
                        f"Property {key} failed validation: {data.get(key)}"
                    )
                )
                error = True

        if error:
            for zon in self.properties.values():
                for error in zon.errors:
                    self._add_error(
                        ValidationError(f"Error validating properties: {error}")
                    )

        return not error
