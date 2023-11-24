"""Class and methods related to the ZonString validator."""

from __future__ import annotations

import re
import uuid
import email.utils
import ipaddress

from zon.base import Zon
from zon.error import ValidationError


class ZonString(Zon):
    """A Zon that validates that the data is a string."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, str):
            self._add_error(ValidationError(f"Expected string, got {type(data)}"))
            return False
        return True

    def len(
        self, min_length, max_length, *, min_exclusive=True, max_exclusive=True
    ) -> "ZonString":
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
                        f"Expected string length between \
                        {'(' if min_exclusive else '['}{min_length},\
                        {max_length}{')' if max_exclusive else ']'}\
                        , got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["len"] = len_validate
        return other

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
            if email.utils.parseaddr(data) == ("", ""):
                other._add_error(ValidationError(f"Expected email, got {data}"))
                return False

            return True

        other.validators["email"] = email_validate
        return other

    def ip(self):
        """Assert that the value under validation is a valid IPv4 address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def ipv4_validate(data):
            try:
                ipaddress.ip_address(data)
            except ValueError:
                other._add_error(ValidationError(f"Expected IPv4, got {data}"))
                return False
            return True

        other.validators["ip"] = ipv4_validate
        return other
