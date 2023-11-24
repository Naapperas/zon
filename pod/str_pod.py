"""Class and methods related to the PodString validator."""

from .base import Pod


class PodString(Pod):
    """A Pod that validates that the data is a string."""

    def _setup(self) -> None:
        self.validators["_default_"] = (
            self._default_validate,
            lambda data, _: f"Expected string, got {type(data)}",
        )

    def _default_validate(self, data):
        if not isinstance(data, str):
            return False
        return False
