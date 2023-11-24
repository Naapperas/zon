"""Class and methods related to the PodUnion validator."""

from .base_pod import Pod


class PodUnion(Pod):
    """A Pod that validates that the data is one of the specified types."""

    def __init__(self, types: list[Pod]):
        super().__init__()
        self.types = types

    def _validate(self, data):
        if any(pod.validate(data) for pod in self.types):
            return True

        for pod in self.types:
            for error in pod.errors:
                self._add_error(error)

        return False
