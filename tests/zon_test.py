import pytest

import zon


@pytest.fixture
def validator():
    return zon.string()


def test_refinement(validator):
    _validator = validator.refine(lambda data: data[0] == data[-1])

    assert _validator.validate("1")
    assert _validator.validate("212")

    with pytest.raises(zon.error.ZonError):
        _validator.validate("21")


def test_top_level_error_path(validator):
    """Test that top-level validation errors have an empty path"""
    _validator = validator.min(3)

    result = _validator.safe_validate("ab")
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == []  # Empty path for top-level errors

    # Test with number validator
    number_validator = zon.number().int().positive()
    result = number_validator.safe_validate(-5)
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == []  # Empty path for top-level errors

    # Test with boolean validator
    bool_validator = zon.boolean()
    result = bool_validator.safe_validate("not_a_boolean")
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) >= 1
    for issue in issues:
        assert issue.path == []  # All top-level errors should have empty paths
