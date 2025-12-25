import pytest

import zon


def test_nested_record_in_record_paths():
    """Test path population for nested records within records"""
    # Create nested record structure: user -> address -> street
    address_validator = zon.record(
        {
            "street": zon.string().min(5),
            "city": zon.string(),
        }
    )

    user_validator = zon.record(
        {
            "name": zon.string(),
            "address": address_validator,
        }
    )

    # Test nested error path
    result = user_validator.safe_validate(
        {
            "name": "John",
            "address": {
                "street": "x",  # Too short (violates min(5))
                "city": "NYC",
            },
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["address", "street"]


def test_nested_list_in_record_paths():
    """Test path population for lists within records"""
    # Record containing a list of strings
    user_validator = zon.record(
        {
            "name": zon.string(),
            "hobbies": zon.string().list().min(1),  # Non-empty list of strings
        }
    )

    # Test list element error within record
    result = user_validator.safe_validate(
        {
            "name": "John",
            "hobbies": ["reading", 123, "coding"],  # Second element wrong type
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["hobbies", "1"]

    # Test multiple list element errors within record
    result = user_validator.safe_validate(
        {
            "name": "John",
            "hobbies": [123, 456, "coding"],  # First two elements wrong type
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 2
    paths = [issue.path for issue in issues]
    assert ["hobbies", "0"] in paths
    assert ["hobbies", "1"] in paths


def test_nested_record_in_list_paths():
    """Test path population for records within lists"""
    # List of user records
    user_record = zon.record(
        {
            "name": zon.string().min(1),  # Require at least 1 character
            "age": zon.number().int().positive(),
        }
    )
    users_validator = user_record.list()

    # Test record field error within list
    result = users_validator.safe_validate(
        [
            {"name": "John", "age": 25},
            {"name": "Jane", "age": -5},  # Negative age
        ]
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["1", "age"]

    # Test multiple record errors within list
    result = users_validator.safe_validate(
        [
            {"name": "", "age": 25},  # Empty name
            {"name": "Jane", "age": -5},  # Negative age
        ]
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 2
    paths = [issue.path for issue in issues]
    assert ["0", "name"] in paths
    assert ["1", "age"] in paths


def test_deeply_nested_structure_paths():
    """Test path population for deeply nested structures"""
    # Create a deeply nested structure: company -> departments -> employees -> address
    address_validator = zon.record(
        {
            "street": zon.string(),
            "zip": zon.string().regex(r"^\d{5}$"),
        }
    )

    employee_validator = zon.record(
        {
            "name": zon.string(),
            "address": address_validator,
        }
    )

    department_validator = zon.record(
        {
            "name": zon.string(),
            "employees": employee_validator.list(),
        }
    )

    company_validator = zon.record(
        {
            "name": zon.string(),
            "departments": department_validator.list(),
        }
    )

    # Test very deeply nested error
    result = company_validator.safe_validate(
        {
            "name": "TechCorp",
            "departments": [
                {
                    "name": "Engineering",
                    "employees": [
                        {
                            "name": "Alice",
                            "address": {
                                "street": "123 Main St",
                                "zip": "123",  # Invalid zip code (not 5 digits)
                            },
                        }
                    ],
                }
            ],
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["departments", "0", "employees", "0", "address", "zip"]


def test_tuple_in_record_paths():
    """Test path population for tuples within records"""
    # Record containing a tuple
    person_validator = zon.record(
        {
            "name": zon.string(),
            "coordinates": zon.element_tuple(
                [zon.number(), zon.number()]
            ),  # (x, y) coordinates
        }
    )

    # Test tuple element error within record
    result = person_validator.safe_validate(
        {
            "name": "John",
            "coordinates": (10.5, "not_a_number"),  # Second element wrong type
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["coordinates", "1"]


def test_list_in_tuple_paths():
    """Test path population for lists within tuples"""
    # Tuple containing a list
    order_validator = zon.element_tuple(
        [
            zon.string(),  # order_id
            zon.string().list(),  # items
        ]
    )

    # Test list element error within tuple
    result = order_validator.safe_validate(("order123", ["item1", 123, "item3"]))
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["1", "1"]  # Tuple index 1, list index 1


def test_optional_nested_structure_paths():
    """Test path population for optional nested structures"""
    # Optional nested record
    optional_address_validator = zon.record(
        {
            "street": zon.string(),
            "city": zon.string(),
        }
    ).optional()

    user_validator = zon.record(
        {
            "name": zon.string(),
            "address": optional_address_validator,
        }
    )

    # Test error in optional nested structure
    result = user_validator.safe_validate(
        {
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": 123,  # Wrong type
            },
        }
    )
    assert result[0] is False
    issues = result[1].issues
    assert len(issues) == 1
    assert issues[0].path == ["address", "city"]

    # Test with None (should be valid for optional)
    result = user_validator.safe_validate(
        {
            "name": "John",
            "address": None,
        }
    )
    assert result[0] is True
