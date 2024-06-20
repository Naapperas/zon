import random
import pytest

import zon


@pytest.fixture
def value():
    return random.random()


@pytest.fixture
def validator(value):
    return zon.literal(value)


def test_literal_get_value(validator, value):
    assert validator.value == value


def test_literal_validate(validator, value):
    assert validator.validate(value)

    with pytest.raises(zon.error.ZonError):
        validator.validate(value + 1)


def test_literal_safe_validate(validator, value):
    assert validator.safe_validate(value) == (True, value)

    assert validator.safe_validate(value + 1)[0] is False
