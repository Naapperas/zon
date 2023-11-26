import pytest

import zon


@pytest.fixture
def validator():
    # use strings as the default collection, should work for all other implementations
    return zon.string()


def test_length(validator):
    assert validator.length(1).validate("1")

    assert not validator.length(0).validate("1")


def test_min_length(validator):
    assert validator.min(1).validate("1")
    assert validator.min(1).validate("12")
    assert validator.min(1).validate("123")

    assert not validator.min(2).validate("1")


def test_max_length(validator):
    assert validator.max(1).validate("1")

    assert not validator.max(0).validate("1")
    assert not validator.max(0).validate("12")
    assert not validator.max(0).validate("123")
