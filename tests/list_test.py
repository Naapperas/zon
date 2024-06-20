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
