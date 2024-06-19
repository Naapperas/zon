import pytest 

import zon

@pytest.fixture
def element_validator():
    return zon.string()

@pytest.fixture
def validator(element_validator):
    return zon.element_list(element_validator)

def test_list_get_element(validator, element_validator):
    assert validator.element == element_validator

def test_list_validate(validator):
    assert validator.validate([""])

    with pytest.raises(zon.error.ZonError):
        validator.validate(1)
    with pytest.raises(zon.error.ZonError):
        validator.validate("")
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 2})
    with pytest.raises(zon.error.ZonError):
        validator.validate([1])

def test_list_safe_validate(validator):
    assert validator.safe_validate([""]) == (True, [""])

    assert validator.safe_validate(1)[0] is False
    assert validator.safe_validate("")[0] is False
    assert validator.safe_validate({"a": 2})[0] is False
    assert validator.safe_validate([1])[0] is False

def test_list_nonempty(validator):
    assert validator.nonempty().validate([""])

    with pytest.raises(zon.error.ZonError):
        validator.nonempty().validate([])

def test_list_length(validator):
    _validator = validator.length(2)

    assert _validator.validate(["1", "2"])

    with pytest.raises(zon.error.ZonError):
        _validator.validate(["1"])

    with pytest.raises(zon.error.ZonError):
        _validator.validate(["1", "2", "3"])

def test_list_min(validator):
    _validator = validator.min(2)

    assert _validator.validate(["1", "2"])
    assert _validator.validate(["1", "2", "3"])

    with pytest.raises(zon.error.ZonError):
        _validator.validate(["1"])

def test_list_max(validator):
    _validator = validator.max(2)

    assert _validator.validate(["1"])
    assert _validator.validate(["1", "2"])

    with pytest.raises(zon.error.ZonError):
        _validator.validate(["1", "2", "3"])