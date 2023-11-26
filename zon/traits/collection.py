"""Class and methods related to Zon that act has collections of objects."""

from typing import Self

from zon import Zon
from zon.error import ValidationError


class ZonCollection(Zon):
    def length(self, length) -> "Self":
        """Assert that the value under validation has at least as many el.

        Returns:
            Self: a new zon with the validation rule added
        """

        other = self._clone()

        def len_validate(data):
            if len(data) != length:
                other._add_error(
                    ValidationError(f"Expected length to be {length}, got {len(data)}")
                )
                return False
            return True

        other.validators["len"] = len_validate
        return other

    def min(self, min_length) -> "Self":
        """Assert that the value under validation has at least as many elements as specified.

        Args:
            min_length (_type_): the minimum length of the collection.

        Returns:
            Self: a new zon with the validation rule added
        """

        other = self._clone()

        def min_len_validate(data):
            if len(data) < min_length:
                other._add_error(
                    ValidationError(
                        f"Expected minimum length to be {min_length}, got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["min_len"] = min_len_validate
        return other

    def max(self, max_length) -> "Self":
        """Assert that the value under validation has at most as many elements as specified.

        Args:
            max_length (_type_): the maximum length of the collection.

        Returns:
            Self: a new zon with the validation rule added
        """

        other = self._clone()

        def max_len_validate(data):
            if len(data) > max_length:
                other._add_error(
                    ValidationError(
                        f"Expected maximum length to be {max_length}, got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["max_len"] = max_len_validate
        return other
