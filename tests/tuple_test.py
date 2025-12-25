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


def test_tuple_rest(validator):
    _validator = validator.rest(zon.number())

    assert _validator.validate(("1", 1.5, True))
    assert _validator.validate(("1", 1.5, True, 1))
    assert _validator.validate(("1", 1.5, True, 1, 2, 3, 4))

    with pytest.raises(zon.error.ZonError):
        _validator.validate(("1", 1.5, True, "1"))


def test_tuple_error_paths(items):
    """Test that validation errors for tuple elements have correct paths"""
    validator = zon.element_tuple(items)

    # Test tuple element validation error
    result = validator.safe_validate(
        ("valid", "not_a_number", True)
    )  # Second element wrong type
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["1"]

    # Test another tuple element validation error
    result = validator.safe_validate(
        ("valid", 1.5, "not_a_boolean")
    )  # Third element wrong type
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["2"]

    # Test multiple tuple element validation errors
    result = validator.safe_validate(
        ("valid", "not_a_number", "not_a_boolean")
    )  # Second and third wrong
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 2
    paths = [issue.path for issue in issues]
    assert ["1"] in paths
    assert ["2"] in paths

    # Test tuple with rest elements
    validator_with_rest = validator.rest(zon.string())
    result = validator_with_rest.safe_validate(
        ("valid", 1.5, True, "good", 123, "also_good")
    )  # 5th element wrong type
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == [
        "1"
    ]  # Rest elements have their own indexing starting from 0

    # Test wrong number of elements (no element-specific paths)
    result = validator.safe_validate(("valid", 1.5))  # Missing third element
    assert result[0] is False
    issues = result[1].issues
    # Wrong number of elements should be at the top level, not element paths
    assert all(len(issue.path) == 0 for issue in issues)
