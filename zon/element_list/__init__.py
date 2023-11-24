"""Class and methods related to the ZonList validator."""

from zon.base import Zon
from zon.error import ValidationError


class ZonList(Zon):
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

    def len(
        self, min_length, max_length, *, min_exclusive=True, max_exclusive=True
    ) -> "ZonList":
        """Assert that the value under validation has a given length.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def len_validate(data):
            max_cond = (
                len(data) > max_length if max_exclusive else len(data) >= max_length
            )
            min_cond = (
                len(data) < min_length if min_exclusive else len(data) <= min_length
            )

            if max_cond or min_cond:
                other._add_error(
                    ValidationError(
                        f"Expected list length between \
                        {'(' if min_exclusive else '['}{min_length},\
                        {max_length}{')' if max_exclusive else ']'}\
                        , got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["len"] = len_validate
        return other
