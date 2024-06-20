import pytest

import zon


@pytest.fixture
def validator():
    return zon.anything()


def test_anything_validate(validator):
    assert validator.validate(1)
    assert validator.validate(1.5)
    assert validator.validate("1")
    assert validator.validate([1])
    assert validator.validate({"a": 1})


def test_anything_safe_validate(validator):
    assert validator.safe_validate(1)[0] is True
    assert validator.safe_validate(1.5)[0] is True
    assert validator.safe_validate("1")[0] is True
    assert validator.safe_validate([1])[0] is True
    assert validator.safe_validate({"a": 1})[0] is True
