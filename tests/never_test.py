import pytest

import zon


@pytest.fixture
def validator():
    return zon.never()


def test_never_validate(validator):
    with pytest.raises(zon.error.ZonError):
        validator.validate(1)
    with pytest.raises(zon.error.ZonError):
        validator.validate(1.5)
    with pytest.raises(zon.error.ZonError):
        validator.validate("1")
    with pytest.raises(zon.error.ZonError):
        validator.validate([1])
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 1})


def test_never_safe_validate(validator):
    assert validator.safe_validate(1)[0] is False
    assert validator.safe_validate(1.5)[0] is False
    assert validator.safe_validate("1")[0] is False
    assert validator.safe_validate([1])[0] is False
    assert validator.safe_validate({"a": 1})[0] is False
