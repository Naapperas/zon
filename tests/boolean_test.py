import pytest

import zon


@pytest.fixture
def validator():
    return zon.boolean()


def test_boolean_validate(validator):
    assert validator.validate(True)
    assert validator.validate(False)

    with pytest.raises(zon.error.ZonError):
        validator.validate("1")
    with pytest.raises(zon.error.ZonError):
        validator.validate([1])
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 1})
    with pytest.raises(zon.error.ZonError):
        validator.validate(1)
    with pytest.raises(zon.error.ZonError):
        validator.validate(1.5)


def test_boolean_safe_validate(validator):
    assert validator.safe_validate(True) == (True, True)
    assert validator.safe_validate(False) == (True, False)

    # TODO: check for the specific error?
    assert validator.safe_validate("1")[0] is False
    assert validator.safe_validate([1])[0] is False
    assert validator.safe_validate({"a": 1})[0] is False
    assert validator.safe_validate(1)[0] is False
    assert validator.safe_validate(1.5)[0] is False
