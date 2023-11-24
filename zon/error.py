"""Validation errors for Zons"""


class ValidationError(Exception):
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
