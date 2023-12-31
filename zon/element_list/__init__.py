"""Class and methods related to the ZonList validator."""

from zon.base import Zon
from zon.error import ValidationError

from zon.traits.collection import ZonCollection


class ZonList(ZonCollection):
    """A Zon that validates that the data is a list of elements of the specified type."""

    def __init__(self, element_type: Zon):
        super().__init__()
        self.element_type = element_type

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, list):
            self._add_error(ValidationError(f"Expected list, got {type(data)}"))
            return False

        error = False
        for i, element in enumerate(data):
            if not self.element_type.validate(element):
                self._add_error(
                    ValidationError(f"Element {i} of list failed validation: {element}")
                )

                error = True

        if error:
            for error in self.element_type.errors:
                self._add_error(ValidationError(f"Error validating elements: {error}"))

        return not error
