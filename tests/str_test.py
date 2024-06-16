import uuid
import pytest

import zon


@pytest.fixture
def validator():
    return zon.string()


def test_str_validate(validator):
    assert validator.validate("1")

    with pytest.raises(zon.error.ZonError):
        validator.validate(1.5)
    with pytest.raises(zon.error.ZonError):
        validator.validate(1)
    with pytest.raises(zon.error.ZonError):
        validator.validate([1])
    with pytest.raises(zon.error.ZonError):
        validator.validate({"a": 1})


def test_str_safe_validate(validator):
    assert validator.safe_validate("1") == (True, "1")

    # TODO: check for the specific error?
    assert validator.safe_validate(1.5)[0] is False
    assert validator.safe_validate(1)[0] is False
    assert validator.safe_validate([1])[0] is False
    assert validator.safe_validate({"a": 1})[0] is False


def test_str_length_equal(validator):
    _validator = validator.length(2)

    assert _validator.validate("12")

    with pytest.raises(zon.error.ZonError):
        _validator.validate("1")


def test_str_length_less_than(validator):
    _validator = validator.max(2)

    assert _validator.validate("1")
    assert _validator.validate("12")

    with pytest.raises(zon.error.ZonError):
        _validator.validate("123")


def test_str_length_greater_than(validator):
    _validator = validator.min(2)

    assert _validator.validate("123")
    assert _validator.validate("12")

    with pytest.raises(zon.error.ZonError):
        _validator.validate("1")


def test_str_email(validator):
    _validator = validator.email()

    assert _validator.validate("test@host.com")
    
    with pytest.raises(zon.error.ZonError):
        assert _validator.validate("test@host")

    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("@host.com")
    
    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("host.com")

def test_str_url(validator):
    _validator = validator.url()

    assert _validator.validate("https://www.google.com")
    assert _validator.validate("http://www.google.com")

    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("www.google.com")
    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("google.com")
    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("google.com/")
    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("google.com")

def test_uuid(validator):
    _validator = validator.uuid()

    assert _validator.validate(uuid.uuid4().hex)

    with pytest.raises(zon.error.ZonError):
        _validator.validate("not_a_UUID")

"""
def test_str_emoji(validator):
    _validator = validator.emoji()

    assert _validator.validate("😀")
    assert _validator.validate("🤩")
    assert _validator.validate("🤨")
    assert _validator.validate("😐")
    assert _validator.validate("😑")

    with pytest.raises(zon.error.ZonError):
        assert not _validator.validate("1")
"""

"""
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

def test_regex(validator):
    _validator = validator.regex(r"^[a-z ]+$")

    assert _validator.validate("abc")
    assert _validator.validate("def")
    assert _validator.validate("abc def")

    assert not _validator.validate("abc1")
    assert not _validator.validate("abc def1")
"""
