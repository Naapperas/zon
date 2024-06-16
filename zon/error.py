"""Validation errors for Zons"""

from typing import Any
from dataclasses import dataclass

from typing_extensions import deprecated


@deprecated("Use the new ZonError class instead.")
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


@dataclass(kw_only=True, frozen=True)
class ZonIssue:
    """Some issue with validation"""

    value: Any
    message: str
    path: list[str]


class ZonError(Exception):
    """Validation error thrown when a validation fails."""

    issues: list[ZonIssue]

    def __init__(self):
        """Builds a new ValidationError with the supplied message.

        Args:
            message (str): The message to be displayed when the exception is thrown.
        """
        super()
        self.issues = []

    def add_issue(self, issue: ZonIssue):
        """Adds an existing issue to this validation error"""

        self.issues.append(issue)

    def add_issues(self, issues: list[ZonIssue]):
        """Adds a batch of existing issues to this validation error"""

        self.issues.extend(issues)

    def __str__(self):
        """Used to covert this exception into a string."""

        return repr(self)

    def __repr__(self) -> str:
        """Used to covert this exception into a string."""

        return f"""ZonError(
        issues: {self.issues})
        """
