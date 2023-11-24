"""Class and methods related to the PodString validator."""

from .base_pod import Pod


class PodString(Pod):
    """A Pod that validates that the data is a string."""

    def _setup(self) -> None:
        self.validators["_default_"] = (
            _default_validate,
            lambda data, _: f"Expected string, got {type(data)}",
        )


def _default_validate(data):
    if not isinstance(data, str):
        return False
    return True
