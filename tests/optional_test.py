import pytest

import zon


@pytest.fixture
def base_validator():
    return zon.string()


def test_optional_get_value(base_validator):
    assert base_validator.optional().unwrap() is base_validator


class TestOptionalMethod:
    @pytest.fixture
    def validator(self, base_validator):
        return base_validator.optional()

    def test_optional_validate(self, validator):
        assert validator.validate(None)
        assert validator.validate("abc")

        with pytest.raises(zon.error.ZonError):
            validator.validate(1.5)

    def test_optional_safe_validate(self, validator):
        assert validator.safe_validate(None) == (True, None)
        assert validator.safe_validate("abc") == (True, "abc")

        # TODO: check for the specific error?
        assert validator.safe_validate(1.5)[0] is False


class TestOptionalOuterFunction:
    @pytest.fixture
    def validator(self, base_validator):
        return zon.optional(base_validator)

    def test_optional_validate(self, validator):
        assert validator.validate(None)
        assert validator.validate("abc")

        with pytest.raises(zon.error.ZonError):
            validator.validate(1.5)

    def test_optional_safe_validate(self, validator):
        assert validator.safe_validate(None) == (True, None)
        assert validator.safe_validate("abc") == (True, "abc")

        # TODO: check for the specific error?
        assert validator.safe_validate(1.5)[0] is False
