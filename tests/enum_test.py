import pytest

import zon


@pytest.fixture
def values():
    return {"1", "2", "3", "4", "5"}


@pytest.fixture
def validator(values):
    return zon.enum(values)


def test_enum_get_options(validator, values):
    assert validator.enum == values


def test_enum_validate(validator):
    assert validator.validate("1")
    assert validator.validate("2")
    assert validator.validate("3")
    assert validator.validate("4")
    assert validator.validate("5")

    with pytest.raises(zon.error.ZonError):
        validator.validate("6")


def test_enum_safe_validate(validator):
    assert validator.safe_validate("1") == (True, "1")
    assert validator.safe_validate("2") == (True, "2")
    assert validator.safe_validate("3") == (True, "3")
    assert validator.safe_validate("4") == (True, "4")
    assert validator.safe_validate("5") == (True, "5")

    # TODO: check for the specific error?
    assert validator.safe_validate("6")[0] is False


def test_enum_exclude(validator):
    assert validator.exclude(["1"]).enum == {"2", "3", "4", "5"}
    assert validator.exclude(["2"]).enum == {"1", "3", "4", "5"}
    assert validator.exclude(["3"]).enum == {"1", "2", "4", "5"}
    assert validator.exclude(["4"]).enum == {"1", "2", "3", "5"}
    assert validator.exclude(["5"]).enum == {"1", "2", "3", "4"}


def test_enum_extract(validator):
    assert validator.extract(["1"]).enum == {
        "1",
    }
    assert validator.extract(["2"]).enum == {
        "2",
    }
    assert validator.extract(["3"]).enum == {
        "3",
    }
    assert validator.extract(["4"]).enum == {
        "4",
    }
    assert validator.extract(["5"]).enum == {
        "5",
    }
