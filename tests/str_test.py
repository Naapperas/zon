import pytest

import zon

import uuid


@pytest.fixture
def validator():
    return zon.string()


def test_str(validator):
    assert validator.validate("1")


def test_not_float(validator):
    assert not validator.validate(1.5)


def test_not_int(validator):
    assert not validator.validate(1)


def test_not_list(validator):
    assert not validator.validate([1])


def test_not_record(validator):
    assert not validator.validate({"a": 1})


def test_email(validator):
    _validator = validator.email()

    assert _validator.validate("test@host.com")
    assert _validator.validate("test@host")

    assert not _validator.validate("@host.com")
    assert not _validator.validate("host.com")


def test_ipv4(validator):
    _validator = validator.ip()

    assert _validator.validate("255.255.255.255")
    assert _validator.validate("0.0.0.0")

    assert not _validator.validate("1.1.1")
    assert not _validator.validate("0.0.0.0.0")
    assert not _validator.validate("256.256.256.256")
    assert not _validator.validate("255.255.255.256")
    assert not _validator.validate("255.255.256.255")
    assert not _validator.validate("255.256.255.255")
    assert not _validator.validate("256.255.255.255")


def test_ipv6(validator):
    _validator = validator.ip()

    # Ipv6 addresses
    assert _validator.validate("::")
    assert _validator.validate("::1")
    assert _validator.validate("::ffff:127.0.0.1")
    assert _validator.validate("::ffff:7f00:1")
    assert _validator.validate("::ffff:127.0.0.1")

    assert not _validator.validate("::1.1.1")
    assert not _validator.validate("::ffff:127.0.0.1.1.1")
    assert not _validator.validate("::ffff:127.0.0.256")
    assert not _validator.validate("::ffff:127.0.0.256.256")

    # Example taken from https://zod.dev/?id=ip-addresses
    assert not _validator.validate("84d5:51a0:9114:gggg:4cfa:f2d7:1f12:7003")


def test_uuid(validator):
    _validator = validator.uuid()

    assert _validator.validate(uuid.uuid4().hex)

    assert not _validator.validate("not_a_UUID")


def test_regex(validator):
    _validator = validator.regex(r"^[a-z ]+$")

    assert _validator.validate("abc")
    assert _validator.validate("def")
    assert _validator.validate("abc def")

    assert not _validator.validate("abc1")
    assert not _validator.validate("abc def1")
