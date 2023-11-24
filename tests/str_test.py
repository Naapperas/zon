import pytest

import zon


@pytest.fixture
def validator():
    return zon.string()


def test_str(validator):
    assert validator.validate("1")


def test_not_float(validator):
    assert not validator.validate(1.5)


def test_not_int(validator):
    assert not validator.validate(1)


def test_not_list(validator):
    assert not validator.validate([1])


def test_not_record(validator):
    assert not validator.validate({"a": 1})
