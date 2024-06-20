import pytest

import zon


@pytest.fixture
def validator_options():
    return [zon.string(), zon.number().int()]


@pytest.fixture
def validator(validator_options):
    return zon.union(validator_options)


def test_get_validator_options(validator, validator_options):
    assert validator.options == validator_options


def test_union_validate(validator):
    assert validator.validate("1")
    assert validator.validate(1)

    with pytest.raises(zon.error.ZonError):
        validator.validate(1.5)
    with pytest.raises(zon.error.ZonError):
        validator.validate([""])
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 2})


def test_union_safe_validate(validator):
    assert validator.safe_validate("1") == (True, "1")
    assert validator.safe_validate(1) == (True, 1)

    assert validator.safe_validate(1.5)[0] is False
    assert validator.safe_validate([""])[0] is False
    assert validator.safe_validate({"a": 2})[0] is False
