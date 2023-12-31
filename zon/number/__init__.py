"""Class and methods related to the ZonNumber validator"""

from __future__ import annotations

from zon.base import Zon
from zon.error import ValidationError


class ZonNumber(Zon):
    """A Zon that validates that the data is a number, i.e., an int or a float."""

    def __gt__(self, other: (int | float)) -> "ZonNumber":
        return self.gt(other)

    def gt(self, value: int | float) -> "ZonNumber":
        """Assert that the value under validation is greater than a given value.

        Args:
            value (int | float): the minimum value

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def gt_validate(data):
            if data <= value:
                other._add_error(
                    ValidationError(f"Expected number > {value}, got {data}")
                )
                return False
            return True

        other.validators["gt"] = gt_validate
        return other

    def __ge__(self, other: int | float) -> "ZonNumber":
        return self.gte(other)

    def gte(self, value: int | float) -> "ZonNumber":
        """Assert that the value under validation is greater than or equal to a minimum value.

        Args:
            value (int | float): the minimum value

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def gte_validate(data):
            if data < value:
                other._add_error(
                    ValidationError(f"Expected number >= {value}, got {data}")
                )
                return False
            return True

        other.validators["gte"] = gte_validate
        return other

    def __lt__(self, other: int | float) -> "ZonNumber":
        return self.lt(other)

    def lt(self, value: int | float) -> "ZonNumber":
        """Assert that the value under validation is less than a given value.

        Args:
            value (int | float): the maximum value

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def lt_validate(data):
            if data >= value:
                other._add_error(
                    ValidationError(f"Expected number < {value}, got {data}")
                )
                return False
            return True

        other.validators["lt"] = lt_validate
        return other

    def __le__(self, other: int | float) -> "ZonNumber":
        return self.lte(other)

    def lte(self, value: int | float) -> "ZonNumber":
        """Assert that the value under validation is less than or equal to a maximum value.

        Args:
            value (int | float): the maximum value

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def lte_validate(data):
            if data > value:
                other._add_error(
                    ValidationError(f"Expected number <= {value}, got {data}")
                )
                return False
            return True

        other.validators["lte"] = lte_validate
        return other

    def __eq__(self, other: int | float) -> "ZonNumber":
        return self.eq(other)

    def eq(self, value: int | float) -> "ZonNumber":
        """Assert that the value under validation is equal to a given value.

        Args:
            value (int | float): the value to compare to

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def eq_validate(data):
            if data != value:
                other._add_error(
                    ValidationError(f"Expected number == {value}, got {data}")
                )
                return False
            return True

        other.validators["eq"] = eq_validate
        return other

    def between(
        self,
        min_value: int | float,
        max_value: int | float,
        *,
        min_exclusive=True,
        max_exclusive=True,
    ) -> "ZonNumber":
        """Assert that the value under validation is between two values.
        The comparison is exclusive on both ends by default.

        Args:
            min_value (int | float): the minimum value
            max_value (int | float): the maximum value
            min_exclusive (bool, optional): whether `min_value` should be considered valid.
            Defaults to True.
            max_exclusive (bool, optional): whether `max_value` should be considered valid.
            Defaults to True.

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def between_validate(data):
            min_cond = data < min_value if min_exclusive else data <= min_value
            max_cond = data > max_value if max_exclusive else data >= max_value

            if min_cond or max_cond:
                other._add_error(
                    ValidationError(
                        f"Expected {min_value} <= number <= {max_value}, got {data}"
                    )
                )
                return False
            return True

        other.validators["between"] = between_validate
        return other
