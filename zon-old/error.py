"""Validation errors for Zons"""

from deprecation import deprecated

from . import __version__


@deprecated(
    deprecated_in="2.0.0",
    current_version=__version__,
    details="Use the new ZonError class instead.",
)
class ValidationError(Exception):
    """
    Validation error thrown when a validation fails.

    Deprecated:
        This class was deprecated in 2.0.0 and will be removed soon. Use ZonError instead.
    """

    def __init__(self, message: str):
        """Builds a new ValidationError with the supplied message.

        Args:
            message (str): The message to be displayed when the exception is thrown.
        """
        super()
        self.message = message

    def __str__(self):
        """Used to covert this exception into a string."""

        return repr(self.message)

    def __repr__(self) -> str:
        """Used to covert this exception into a string."""

        return f"ValidationError({self.message})"


class ZonError(Exception):
    """Validation error thrown when a validation fails."""

    def __init__(self, message: str):
        """Builds a new ValidationError with the supplied message.

        Args:
            message (str): The message to be displayed when the exception is thrown.
        """
        super()
        self.message = message

    def __str__(self):
        """Used to covert this exception into a string."""

        return repr(self.message)

    def __repr__(self) -> str:
        """Used to covert this exception into a string."""

        return f"ValidationError({self.message})"
