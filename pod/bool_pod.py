"""Class and methods related to the PodBool validator."""

from .base_pod import Pod
from .error import ValidationError


class PodBoolean(Pod):
    """A Pod that validates that the data is a boolean."""

    def _setup(self) -> None:
        self.validators["_default_"] = self._default_validate

    def _default_validate(self, data):
        if not isinstance(data, bool):
            self._add_error(ValidationError(f"Expected boolean, got {type(data)}"))
            return False
        return True

    def true(self):
        """Assert that the value under validation is True.

        Returns:
            PodBoolean: a new pod with the validation rule added
        """

        other = self._clone()

        def true_validate(data):
            if not data:
                other._add_error(ValidationError(f"Expected True, got {data}"))
                return False
            return True

        other.validators["true"] = true_validate
        return other
    
    def false(self):
        """Assert that the value under validation is False.

        Returns:
            PodBoolean: a new pod with the validation rule added
        """

        other = self._clone()

        def false_validate(data):
            if data:
                other._add_error(ValidationError(f"Expected False, got {data}"))
                return False
            return True

        other.validators["false"] = false_validate
        return other