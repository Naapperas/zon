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


def test_record_safe_validate(validator):
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

    assert _validator.validate({}) == {}


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

    assert _validator.validate({}) == {}


def test_record_required_all(validator):
    _validator = validator.partial().required()

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
        }
    )

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
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


def test_record_required_some(validator):
    _validator = validator.partial().required({"age": True})

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


def test_record_unknown_key_policy_strict(validator):
    _validator = validator.strict()

    with pytest.raises(zon.error.ZonError):
        _validator.validate(
            {
                "name": "John",
                "age": 1,
                "unknown": 1,
            }
        )


def test_record_unknown_key_policy_strip(validator):
    _validator = validator.strip()

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
            "unknown": 1,
        }
    ) == {
        "name": "John",
        "age": 1,
    }


def test_record_unknown_key_policy_passthrough(validator):
    _validator = validator.passthrough()

    assert _validator.validate(
        {
            "name": "John",
            "age": 1,
            "unknown": 1,
        }
    ) == {
        "name": "John",
        "age": 1,
        "unknown": 1,
    }


def test_record_error_paths(validator):
    """Test that validation errors for record fields have correct paths"""
    # Test field validation error path
    result = validator.safe_validate(
        {
            "name": "",  # Too short (violates min(1))
            "age": 1,
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["name"]

    # Test another field validation error path
    result = validator.safe_validate(
        {
            "name": "John",
            "age": -5,  # Not positive
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["age"]

    # Test multiple field validation errors
    result = validator.safe_validate(
        {
            "name": "",  # Too short
            "age": -5,  # Not positive
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 2
    paths = [issue.path for issue in issues]
    assert ["name"] in paths
    assert ["age"] in paths

    # Test with missing required field
    result = validator.safe_validate(
        {
            "name": "John",
            # age missing
        }
    )
    assert result[0] is False
    issues = result[1].issues
    # Missing field should also have the field name in the path
    assert any(issue.path == ["age"] for issue in issues)
