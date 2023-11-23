import pod

import pytest


@pytest.fixture
def validator():
    return pod.number()


def test_int(validator):
    assert validator.validate(1)


def test_float(validator):
    assert validator.validate(1.5)


def test_not_str(validator):
    assert not validator.validate("1")


def test_not_list(validator):
    assert not validator.validate([1])


def test_not_record(validator):
    assert not validator.validate({"a": 1})
