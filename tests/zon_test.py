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
