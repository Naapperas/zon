import pytest

import zon


@pytest.fixture
def validator():
    return zon.integer()


def test_int(validator):
    assert validator.validate(1)


def test_not_float(validator):
    assert not validator.validate(1.5)


def test_not_str(validator):
    assert not validator.validate("1")


def test_not_list(validator):
    assert not validator.validate([1])


def test_not_record(validator):
    assert not validator.validate({"a": 1})


def test_gt_func(validator):
    assert not validator.gt(1).validate(0)


def test_gt_func_op(validator):
    new_validator = validator > 1

    assert not new_validator.validate(0)


def test_gte_func(validator):
    assert not validator.gte(1).validate(0)


def test_gte_func_op(validator):
    new_validator = validator >= 1

    assert not new_validator.validate(0)


def test_lt_func(validator):
    assert not validator.lt(1).validate(2)


def test_lt_func_op(validator):
    new_validator = validator < 1

    assert not new_validator.validate(2)


def test_lte_func(validator):
    assert not validator.lte(1).validate(2)


def test_lte_func_op(validator):
    new_validator = validator <= 1

    assert not new_validator.validate(2)


def test_eq_func(validator):
    assert not validator.eq(1).validate(2)


def test_eq_func_op(validator):
    new_validator = validator == 1

    assert not new_validator.validate(2)


def test_between_func(validator):
    assert not validator.between(1, 2).validate(0)
