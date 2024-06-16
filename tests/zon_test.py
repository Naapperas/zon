"""
Tests related to core Zon functionality that is not necessarily bound to any specific Zon implementation.
"""

import pytest

import zon

@pytest.fixture
def normal_validator():
    # This is just for demonstration purposes
    return zon.string(fast_termination=False).length(3).max(2)

@pytest.fixture
def fail_fast_validator():
    # This is just for demonstration purposes
    return zon.string(fast_termination=True).length(3).max(2)


def test_fail_fast(normal_validator, fail_fast_validator):

    test_input = "12345"

    with pytest.raises(zon.error.ZonError) as fail_fast_result:
        fail_fast_validator.validate(test_input)
    
    assert len(fail_fast_result.value.issues) == 1

    with pytest.raises(zon.error.ZonError) as normal_result:
        normal_validator.validate(test_input)
    
    assert len(normal_result.value.issues) == 2