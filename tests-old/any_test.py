import pytest

import zon


@pytest.fixture
def validator():
    return zon.anything()


def test_int(validator):
    assert validator.validate(1)


def test_float(validator):
    assert validator.validate(1.5)


def test_str(validator):
    assert validator.validate("1")


def test_list(validator):
    assert validator.validate([1])


def test_record(validator):
    assert validator.validate({"a": 1})
