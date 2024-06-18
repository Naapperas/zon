import pytest

import zon


@pytest.fixture
def string_validator():
    return zon.string().min(1)


@pytest.fixture
def integer_validator():
    return zon.number().int().positive()


@pytest.fixture
def validator_dict(string_validator, integer_validator):
    return {
        "name": string_validator,
        "age": integer_validator,
    }


@pytest.fixture
def validator(validator_dict):
    return zon.record(validator_dict)


def test_record_validate(validator):
    assert validator.validate(
        {
            "name": "John",
            "age": 1,
        }
    )

    with pytest.raises(zon.error.ZonError):
        validator.validate(
            {
                "age": 1,
            }
        )

    with pytest.raises(zon.error.ZonError):
        validator.validate(
            {
                "name": "",
            }
        )


def test_record_sage_validate(validator):
    assert validator.safe_validate(
        {
            "name": "John",
            "age": 1,
        }
    ) == (
        True,
        {
            "name": "John",
            "age": 1,
        },
    )

    assert (
        validator.safe_validate(
            {
                "age": 1,
            }
        )[0]
        is False
    )

    assert (
        validator.safe_validate(
            {
                "name": "",
            }
        )[0]
        is False
    )


def test_record_shape(validator, validator_dict):
    assert validator.shape is validator_dict


def test_record_keyof(validator, validator_dict):
    _validator = validator.keyof()

    for key in validator_dict.keys():
        assert _validator.validate(key)


def test_record_extend(validator):
    _validator = validator.extend({"male": zon.boolean()})

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
            "male": True,
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "name": "John",
                "age": 1,
            }
        )


def test_record_merge(validator):
    extra_validator = zon.record({"male": zon.boolean()})
    _validator = validator.merge(extra_validator)

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
            "male": True,
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "name": "John",
                "age": 1,
            }
        )


def test_record_pick(validator):
    # TODO: improve testing on this
    _validator = validator.pick({"name": True})

    assert _validator.validate(
        {
            "name": "John",
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "age": 1,
            }
        )


def test_record_omit(validator):
    # TODO: improve testing on this
    _validator = validator.omit({"name": True})

    assert _validator.validate(
        {
            "age": 1,
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "name": "John",
            }
        )


def test_record_partial_all(validator):
    _validator = validator.partial()

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
        }
    )

    assert _validator.validate(
        {
            "age": 1,
        }
    )

    assert _validator.validate(
        {
            "name": "",
        }
    )

    assert _validator.validate({})


def test_record_partial_some(validator):
    _validator = validator.partial({"name": True})

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
        }
    )

    assert _validator.validate(
        {
            "age": 1,
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "name": "",
            }
        )

    with pytest.raises(zon.error.ZonError):
        _validator.validate({})


def test_record_deep_partial(validator):
    _validator = validator.extend(
        {"sub": zon.record({"sub_number": zon.number()})}
    ).deep_partial()

    assert _validator.validate({"name": "John", "age": 1, "sub": {"sub_number": 1}})

    assert _validator.validate({"age": 1, "sub": {"sub_number": 1}})

    assert _validator.validate({"name": "", "sub": {"sub_number": 1}})
    assert _validator.validate({"sub": {"sub_number": 1}})
    assert _validator.validate({"sub": {}})

    assert _validator.validate({})
