import pytest

import zon


@pytest.fixture
def validator():
    return zon.element_list(zon.anything())


def test_list(validator):
    assert validator.validate([1])


def test_not_list(validator):
    assert not validator.validate(1)
    assert not validator.validate({"a": 1})
    assert not validator.validate("1")
    assert not validator.validate(1.5)
    assert not validator.validate(True)
