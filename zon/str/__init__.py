"""Class and methods related to the ZonString validator."""

from __future__ import annotations

import re
import uuid
import ipaddress

from validate_email import validate_email

from zon.error import ValidationError

from zon.traits.collection import ZonCollection


class ZonString(ZonCollection):
    """A Zon that validates that the data is a string.

    For all purposes, a string is a collection of characters.
    """

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, str):
            self._add_error(ValidationError(f"Expected string, got {type(data)}"))
            return False
        return True

    def regex(self, regex: str | re.Pattern[str]) -> "ZonString":
        """Assert that the value under validation matches a given regular expression.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def regex_validate(data):
            if not re.match(regex, data):
                other._add_error(
                    ValidationError(
                        f"Expected string matching regex /{regex}/, got {data}"
                    )
                )
                return False
            return True

        other.validators["regex"] = regex_validate
        return other

    def uuid(self) -> "ZonString":
        """Assert that the value under validation is a valid UUID.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def uuid_validate(data):
            try:
                uuid.UUID(data)
            except ValueError:
                other._add_error(ValidationError(f"Expected UUID, got {data}"))
                return False
            return True

        other.validators["uuid"] = uuid_validate
        return other

    def email(self):
        """Assert that the value under validation is a valid email address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def email_validate(data):
            if not validate_email(data):
                other._add_error(ValidationError(f"Expected email, got {data}"))
                return False

            return True

        other.validators["email"] = email_validate
        return other

    def ip(self):
        """Assert that the value under validation is a valid IP address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def ip_validate(data):
            try:
                ipaddress.ip_address(data)
            except ValueError:
                other._add_error(ValidationError(f"Expected IPv4, got {data}"))
                return False
            return True

        other.validators["ip"] = ip_validate
        return other
