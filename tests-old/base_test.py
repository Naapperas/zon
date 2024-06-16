import pytest

import zon


@pytest.fixture
def validator():
    return zon.anything()


def test_refine(validator):

    assert validator.validate(1)

    refined_validator = validator.refine(lambda x: x == 1)

    assert refined_validator.validate(1)
    assert not refined_validator.validate(2)
