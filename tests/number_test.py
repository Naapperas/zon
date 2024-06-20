import math

import pytest

import zon


@pytest.fixture
def validator():
    return zon.number()


def test_number_validate(validator):
    assert validator.validate(1)
    assert validator.validate(1.5)

    with pytest.raises(zon.error.ZonError):
        validator.validate("1")
    with pytest.raises(zon.error.ZonError):
        validator.validate([1])
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 1})


def test_number_safe_validate(validator):
    assert validator.safe_validate(1) == (True, 1)
    assert validator.safe_validate(1.5) == (True, 1.5)

    # TODO: check for the specific error?
    assert validator.safe_validate("1")[0] is False
    assert validator.safe_validate([1])[0] is False
    assert validator.safe_validate({"a": 1})[0] is False


def test_number_gt(validator):
    _validator = validator.gt(2)

    assert _validator.validate(3)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(2)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)


def test_number_gte(validator):
    _validator = validator.gte(2)

    assert _validator.validate(2)
    assert _validator.validate(3)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)


def test_number_lt(validator):
    _validator = validator.lt(2)

    assert _validator.validate(1)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(2)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(3)


def test_number_lte(validator):
    _validator = validator.lte(2)

    assert _validator.validate(2)
    assert _validator.validate(1)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(3)


def test_number_int(validator):
    _validator = validator.int()

    assert _validator.validate(1)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1.5)


def test_number_float(validator):
    _validator = validator.float()

    assert _validator.validate(1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)


def test_number_positive(validator):
    _validator = validator.positive()

    assert _validator.validate(1)
    assert _validator.validate(1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(0)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(-1)


def test_number_non_negative(validator):
    _validator = validator.non_negative()

    assert _validator.validate(0) == 0
    assert _validator.validate(1)
    assert _validator.validate(1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(-1)


def test_number_negative(validator):
    _validator = validator.negative()

    assert _validator.validate(-1)
    assert _validator.validate(-1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(0)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)


def test_number_non_positive(validator):
    _validator = validator.non_positive()

    assert _validator.validate(0) == 0
    assert _validator.validate(-1)
    assert _validator.validate(-1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)


def test_number_multiple_of(validator):
    _validator = validator.multiple_of(2)

    assert _validator.validate(2)
    assert _validator.validate(4)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(1)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(3)


def test_number_finite(validator):
    _validator = validator.finite()

    assert _validator.validate(1)
    assert _validator.validate(1.5)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(math.inf)

    with pytest.raises(zon.error.ZonError):
        _validator.validate(-math.inf)
