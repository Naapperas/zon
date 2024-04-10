"""Validator package.

The purpose of this package is to provide a set of functions to validate data, using a Zod-like syntax.
"""

from __future__ import annotations

__version__ = "2.0.0"
__author__ = "Nuno Pereira"
__email__ = "nunoafonso2002@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2023, Nuno Pereira"

from abc import ABC, abstractmethod
from typing import final, Callable, TypeVar, Self, Any
import copy
import re
from deprecation import deprecated

import validators
from dateutil.parser import parse


from .error import ZonError

T = TypeVar("T")
ValidationRule = Callable[[T], bool]


class Zon(ABC):
    """
    Base class for all Zons.
    
    A Zon is the basic unit of validation in Zon.
    It is used to validate data, and can be composed with other Zons
    to create more complex validations.
    """

    def __init__(self):
        self.errors: list[ZonError] = []
        """List of validation errors accumulated"""

        self.validators: dict[str, ValidationRule] = {}
        """validators that will run when 'validate' is invoked."""

        self._setup()

    def _clone(self) -> Self:
        """Creates a copy of this Zon."""
        return copy.deepcopy(self)

    def _add_error(self, error: ZonError):
        """Adds an error to this Zon's error output.

        Args:
            error (ZonError): the validation error to add.
        """
        self.errors.append(error)

    @abstractmethod
    def _setup(self) -> None:
        """Sets up the Zon with default validation rules.

        This implies that a '_default_' rule will be present, otherwise the validation fails.

        This method is called when the Zon is created.
        """

    @final
    @deprecated(deprecated_in="2.0.0", current_version=__version__)
    def _validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Returns:
            bool: True if the data is valid, False otherwise.
        """

        if "_default_" not in self.validators or not self.validators["_default_"]:
            self._add_error(
                ZonError(f"Zon of type {type(self)} must have a valid '_default_' rule")
            )
            return False

        # TODO: better error messages
        return all(validator(data) for (_, validator) in self.validators.items())

    @deprecated(
        deprecated_in="2.0.0",
        current_version=__version__,
        details="This method does not exist in the original 'zod' code. Please use 'parse' and 'safe_parse' to better reflect zod's API",
    )
    @final
    def validate(self, data: T) -> bool:
        """Validates the supplied data.

        Args:
            data (Any): the piece of data to be validated.

        Raises:
            NotImplementedError: the default implementation of this method
            is not implemented on base Zon class.
        """
        if type(self) is Zon:  # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Zon class"
            )

        return self._validate(data)

    def parse(self, data: T) -> T:
        """Parses the supplied data, validating it and returning it if it is valid. Raises an exception if the data is invalid

        Args:
            data (T): the data to be parsed.

        Raises:
            NotImplementedError: the default implementation of this method is not implemented, so an exception is raised
            ZonError: if a some member of the validation chains fails when validation some of the data.

        Returns:
            T: the data given as input if it is valid.
        """

        if type(self) is Zon:  # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Zon class"
            )

        if not all(validator(data) for validator in self.validators.values()):
            raise ZonError(f"Error parsing data: {self.errors}")

        return data

    def safe_parse(self, data: T) -> tuple[bool, T] | tuple[bool, ZonError]:
        """Parses the supplied data, but unlike `parse` this method does not throw. Instead it returns a tuple in the form ()

        Args:
            data (T): _description_

        Raises:
            NotImplementedError: _description_
            e: _description_

        Returns:
            dict[str, bool | T]: _description_
        """

        if type(self) is Zon:  # pylint: disable=unidiomatic-typecheck
            raise NotImplementedError(
                "validate() method not implemented on base Zon class"
            )

        try:
            result = self.parse(data)

            return {"success": True, "data": result}
        except ZonError as e:
            return {"success": False, "errors": str(e)}  # TODO: improve this
        except NotImplementedError as e:
            raise e  # we should never get here, just rethrow for good measure

    def and_also(self, zon: "Zon") -> "ZonAnd":
        """Creates a new Zon that validates that
        the data is valid for both this Zon and the supplied Zon.

        Args:
            zon (Zon): the Zon to be validated.

        Returns:
            ZonAnd: a new validator that validates that
            the data is valid for both this Zon and the supplied Zon.
        """
        return ZonAnd(self, zon)

    def __and__(self, zon: "Zon") -> "ZonAnd":
        return self.and_also(zon)

    def refine(self, refinement: Callable[[T], bool]) -> "Self":
        """Creates a new Zon that validates the data with the supplied refinement.

        A refinement is a function that takes a piece of data and returns True if the data is valid or throws otherwise.

        Args:
            refinement (Callable[[T], bool]): the refinement to be applied.

        Returns:
            ZonRefined: a new validator that validates the data with the supplied refinement.
        """
        _clone = self._clone()

        def _refinement_validate(data):
            try:
                return refinement(data)
            except ZonError as e:
                _clone._add_error(e)
                return False

        if "_refined_" not in _clone.validators:
            _clone.validators["_refined_"] = _refinement_validate
        else:
            current_refinement = _clone.validators["_refined_"]

            def _refined_validator(data):
                return current_refinement(data) and _refinement_validate(data)

            _clone.validators["_refined_"] = _refined_validator

        return _clone

    def optional(self) -> "ZonOptional":
        """Creates a new Zon that makes this validation chain optional.

        Returns:
            ZonOptional: a new validator that makes any validation optional.
        """
        return ZonOptional(self)


class ZonOptional(Zon):
    """A Zon that makes its data validation optional."""

    def __init__(self, zon):
        super().__init__()
        self.zon = zon

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if data is None or not data:
            return True
        return self.zon.validate(data)

    def unwrap(self) -> Zon:
        """Extracts the wrapped Zon from this ZonOptional.

        Returns:
            Zon: the wrapped Zon
        """

        return self.zon

class ZonAnd(Zon):
    """A Zon that validates that the data is valid for both this Zon and the supplied Zon."""

    def __init__(self, zon1: Zon, zon2: Zon):
        super().__init__()
        self.zon1 = zon1
        self.zon2 = zon2

    def _setup(self):
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not (self.zon1.validate(data) and self.zon2.validate(data)):
            for error in self.zon1.errors:
                self._add_error(error)

            for error in self.zon2.errors:
                self._add_error(error)

            return False

        return True


class ZonCollection(Zon):
    """
    A ZonCollection is a validator that abstracts any piece of data that might be a collection of something else.
    """

    def length(self, length: int) -> "Self":
        """Assert that the value under validation has exactly 'length' elements.

        Args:
            length (int): the exact length of the collection.

        Returns:
            Self: a new Zon with the validation rule added
        """

        other = self._clone()

        def len_validate(data):
            if len(data) != length:
                other._add_error(
                    ZonError(f"Expected length to be {length}, got {len(data)}")
                )
                return False
            return True

        other.validators["len"] = len_validate
        return other

    def min(self, min_length: int) -> "Self":
        """Assert that the value under validation has at least as many elements as specified.

        Args:
            min_length (int): the minimum length of the collection.

        Returns:
            Self: a new zon with the validation rule added
        """

        other = self._clone()

        def min_len_validate(data):
            if len(data) < min_length:
                other._add_error(
                    ZonError(
                        f"Expected minimum length to be {min_length}, got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["min_len"] = min_len_validate
        return other

    def max(self, max_length: int) -> "Self":
        """Assert that the value under validation has at most as many elements as specified.

        Args:
            max_length (int): the maximum length of the collection.

        Returns:
            Self: a new zon with the validation rule added
        """

        other = self._clone()

        def max_len_validate(data):
            if len(data) > max_length:
                other._add_error(
                    ZonError(
                        f"Expected maximum length to be {max_length}, got {len(data)}"
                    )
                )
                return False
            return True

        other.validators["max_len"] = max_len_validate
        return other


class ZonString(ZonCollection):
    """
    A Zon that validates that the data is a string.

    For all purposes, a string is a collection of characters.
    """

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, str):
            self._add_error(ZonError(f"Expected string, got {type(data)}"))
            return False
        return True

    def regex(
        self, regex: str | re.Pattern[str], opts: dict[str, Any] | None = None
    ) -> "ZonString":
        """Assert that the value under validation matches a given regular expression.

        Args:
            regex (str): the regex to use.
            opts (dict[str, Any]): additional options.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def regex_validate(data):
            if not re.match(regex, data):
                if opts and "message" in opts:
                    other._add_error(ZonError(opts["message"]))
                else:
                    other._add_error(
                        ZonError(
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
            if not validators.uuid(data):
                other._add_error(ZonError(f"Expected valid UUID, got {data}"))
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
            if not validators.email(data):
                other._add_error(ZonError(f"Expected valid email address, got {data}"))
                return False

            return True

        other.validators["email"] = email_validate
        return other

    def emoji(self):
        """Assert that the value under validation is a valid emoji.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def emoji_validate(data):
            if not re.match(
                "^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$", data
            ):
                other._add_error(ZonError(f"Expected valid email address, got {data}"))
                return False

            return True

        other.validators["emoji"] = emoji_validate
        return other

    def url(self):
        """Assert that the value under validation is a valid URL.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def url_validate(data):
            if not validators.url(data):
                other._add_error(ZonError(f"Expected valid url, got {data}"))
                return False

            return True

        other.validators["url"] = url_validate
        return other

    def ip(self, opts: dict[str, Any] | None = None):
        """Assert that the value under validation is a valid IP address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def ip_validate(data):

            valid = False
            ipv4 = validators.ipv4(data)
            ipv6 = validators.ipv6(data)

            match opts.get("version", None):
                case None:
                    valid = ipv4 or ipv6
                case 6 | "6":
                    valid = ipv6
                case 4 | "4":
                    valid = ipv4

            if not valid:
                if opts and "message" in opts:
                    other._add_error(ZonError(opts["message"]))
                else:
                    other._add_error(ZonError(f"Expected valid IP address, got {data}"))
                return False

            return True

        other.validators["ip"] = ip_validate
        return other

    def date(self):
        """Assert that the value under validation is a valid IP address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        raise NotImplementedError("Not implemented yet")
        # return self.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}")

    def time(self):
        """Assert that the value under validation is a valid IP address.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        raise NotImplementedError("Not implemented yet")
        # return self.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}")

    def includes(self, substr: str):
        """Assert that the value under validation includes the given string as a substring.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def includes_validate(data: str):
            try:
                data.index(substr)
                return True
            except ValueError:
                other._add_error(ZonError(f"Expected '{data}' to include '{substr}'"))
                return False

        other.validators["includes"] = includes_validate
        return other

    def startswith(self, prefix: str):
        """Assert that the value under validation is a string that starts with the given prefix.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def startswith_validate(data: str):
            if not data.startswith(prefix):
                other._add_error(
                    ZonError(f"Expected '{data}' to start with '{prefix}'")
                )
                return False

            return True

        other.validators["startswith"] = startswith_validate
        return other

    def endswith(self, suffix: str):
        """Assert that the value under validation is a string that ends with the given suffix.

        Returns:
            ZonString: a new zon with the validation rule added
        """

        other = self._clone()

        def endswith_validate(data: str):
            if not data.endswith(suffix):
                other._add_error(ZonError(f"Expected '{data}' to end with '{suffix}'"))
                return False

            return True

        other.validators["endswith"] = endswith_validate
        return other

    def nanoid(self, data: str):

        raise NotImplementedError("Not yet implemented")

    def cuid(self, data: str):

        raise NotImplementedError("Not yet implemented")

    def cuid2(self, data: str):

        raise NotImplementedError("Not yet implemented")

    def ulid(self, data: str):

        raise NotImplementedError("Not yet implemented")


class ZonNumber(Zon):
    """A Zon that validates that the data is a number, i.e., an int or a float."""

    def __gt__(self, other: int | float) -> "ZonNumber":
        return self.gt(other)

    def gt(self, value: int | float ) -> "ZonNumber":
        """Assert that the value under validation is greater than a given value.

        Args:
            value (int | float): the minimum value

        Returns:
            ZonNumber: a new zon with the validation rule added
        """

        other = self._clone()

        def gt_validate(data: int | float):
            if data <= value:
                other._add_error(ZonError(f"Expected number > {value}, got {data}"))
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

        def gte_validate(data: int | float):
            if data < value:
                other._add_error(ZonError(f"Expected number >= {value}, got {data}"))
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

        def lt_validate(data: int | float):
            if data >= value:
                other._add_error(ZonError(f"Expected number < {value}, got {data}"))
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

        def lte_validate(data: int | float):
            if data > value:
                other._add_error(ZonError(f"Expected number <= {value}, got {data}"))
                return False
            return True

        other.validators["lte"] = lte_validate
        return other
