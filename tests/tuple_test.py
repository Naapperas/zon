import pytest

import zon

@pytest.fixture
def items():
    return [
        zon.string(),
        zon.number(),
        zon.boolean(),
    ]

@pytest.fixture
def validator(items):
    return zon.element_tuple(items)

def test_tuple_get_items(validator, items):
    assert validator.items == items

def test_tuple_validate(validator):
    assert validator.validate(("1", 1.5, True))
    
    with pytest.raises(zon.error.ZonError):
        validator.validate(("1", 1.5))

    with pytest.raises(zon.error.ZonError):
        validator.validate(("1", 1.5, True, 1))

    with pytest.raises(zon.error.ZonError):
        validator.validate(("1", 1.5, "True"))

def test_tuple_safe_validate(validator):
    assert validator.safe_validate(("1", 1.5, True)) == (True, ("1", 1.5, True))

    assert validator.safe_validate(("1", 1.5))[0] is False
    assert validator.safe_validate(("1", 1.5, True, 1))[0] is False
    assert validator.safe_validate(("1", 1.5, "True"))[0] is False
