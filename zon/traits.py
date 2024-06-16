"""
Traits useful for various its and bits of Zon code.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Self


class HasMax:
    """
    Validation helper that indicates that the validation value has some attribute that must be upper-bound by some value
    """

    @abstractmethod
    def max(self, max_value: int | float) -> Self:
        """
        Defines that a given attribute of the value being validated must be upper-bound by the given parameter.

        Args:
            max_value (int | float): the maximum value (inclusive) that the attribute being validated can have.
        """

        raise NotImplementedError("'max' must be implemented by subclasses")


class HasMin:
    """
    Validation helper that indicates that the validation value has some attribute that must be lower-bound by some value
    """

    @abstractmethod
    def min(self, min_value: int | float) -> Self:
        """
        Defines that a given attribute of the value being validated must be lower-bound by the given parameter.

        Args:
            min_value (int | float): the minimum value (inclusive) that the attribute being validated can have.
        """

        raise NotImplementedError("'min' must be implemented by subclasses")
