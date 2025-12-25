import pytest

import zon


@pytest.fixture
def element_validator():
    return zon.string()


def test_list_get_element(element_validator):
    assert element_validator.list().element == element_validator


class TestElementListOuterFunction:
    @pytest.fixture
    def validator(self, element_validator):
        return zon.element_list(element_validator)

    def test_list_validate(self, validator):
        assert validator.validate([""])

        with pytest.raises(zon.error.ZonError):
            validator.validate(1)
        with pytest.raises(zon.error.ZonError):
            validator.validate("")
        with pytest.raises(zon.error.ZonError):
            validator.validate({"a": 2})
        with pytest.raises(zon.error.ZonError):
            validator.validate([1])

    def test_list_safe_validate(self, validator):
        assert validator.safe_validate([""]) == (True, [""])

        assert validator.safe_validate(1)[0] is False
        assert validator.safe_validate("")[0] is False
        assert validator.safe_validate({"a": 2})[0] is False
        assert validator.safe_validate([1])[0] is False

    def test_list_nonempty(self, validator):
        assert validator.nonempty().validate([""])

        with pytest.raises(zon.error.ZonError):
            validator.nonempty().validate([])

    def test_list_length(self, validator):
        _validator = validator.length(2)

        assert _validator.validate(["1", "2"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1", "2", "3"])

    def test_list_min(self, validator):
        _validator = validator.min(2)

        assert _validator.validate(["1", "2"])
        assert _validator.validate(["1", "2", "3"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1"])

    def test_list_max(self, validator):
        _validator = validator.max(2)

        assert _validator.validate(["1"])
        assert _validator.validate(["1", "2"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1", "2", "3"])


class TestElementListMethod:
    @pytest.fixture
    def validator(self, element_validator):
        return element_validator.list()

    def test_list_validate(self, validator):
        assert validator.validate([""])

        with pytest.raises(zon.error.ZonError):
            validator.validate(1)
        with pytest.raises(zon.error.ZonError):
            validator.validate("")
        with pytest.raises(zon.error.ZonError):
            validator.validate({"a": 2})
        with pytest.raises(zon.error.ZonError):
            validator.validate([1])

    def test_list_safe_validate(self, validator):
        assert validator.safe_validate([""]) == (True, [""])

        assert validator.safe_validate(1)[0] is False
        assert validator.safe_validate("")[0] is False
        assert validator.safe_validate({"a": 2})[0] is False
        assert validator.safe_validate([1])[0] is False

    def test_list_nonempty(self, validator):
        assert validator.nonempty().validate([""])

        with pytest.raises(zon.error.ZonError):
            validator.nonempty().validate([])

    def test_list_length(self, validator):
        _validator = validator.length(2)

        assert _validator.validate(["1", "2"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1", "2", "3"])

    def test_list_min(self, validator):
        _validator = validator.min(2)

        assert _validator.validate(["1", "2"])
        assert _validator.validate(["1", "2", "3"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1"])

    def test_list_max(self, validator):
        _validator = validator.max(2)

        assert _validator.validate(["1"])
        assert _validator.validate(["1", "2"])

        with pytest.raises(zon.error.ZonError):
            _validator.validate(["1", "2", "3"])


def test_list_error_paths(element_validator):
    """Test that validation errors for list elements have correct paths"""
    validator = zon.element_list(
        element_validator.min(2)
    )  # Require strings with min length 2

    # Test single element validation error
    result = validator.safe_validate(["valid", "x"])  # Second string too short
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["1"]

    # Test multiple element validation errors
    result = validator.safe_validate(["x", "y", "valid"])  # First two strings too short
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 2
    paths = [issue.path for issue in issues]
    assert ["0"] in paths
    assert ["1"] in paths

    # Test with wrong type element
    result = validator.safe_validate(["valid", 123])  # Second element not a string
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["1"]

    # Test empty list - should be valid (no elements to validate)
    result = validator.safe_validate([])
    assert result[0] is True
