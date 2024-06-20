import pytest

import zon


@pytest.fixture
def validator_prefix():
    return zon.string().starts_with("abc")


@pytest.fixture
def validator_suffix():
    return zon.string().ends_with("def")


class TestIntersection:
    @pytest.fixture
    def validator(self, validator_prefix, validator_suffix):
        return zon.intersection(validator_prefix, validator_suffix)

    def test_intersection_validate(self, validator):
        assert validator.validate("abcdef")

        with pytest.raises(zon.error.ZonError):
            validator.validate("abc")

    def test_intersection_safe_validate(self, validator):
        assert validator.safe_validate("abcdef") == (True, "abcdef")

        assert validator.safe_validate("abc")[0] is False


class TestAndAlso:
    @pytest.fixture
    def validator(self, validator_prefix, validator_suffix):
        return validator_prefix.and_also(validator_suffix)

    def test_intersection_validate(self, validator):
        assert validator.validate("abcdef")

        with pytest.raises(zon.error.ZonError):
            validator.validate("abc")

    def test_intersection_safe_validate(self, validator):
        assert validator.safe_validate("abcdef") == (True, "abcdef")

        assert validator.safe_validate("abc")[0] is False
