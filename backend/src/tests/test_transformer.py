"""
Unit tests for the transformer module.

Tests cover level conversion from Picolo format to QLC+ format.
"""

import sys
sys.path.insert(0, "../../..")

from converter.transformer import convert_level
import pytest


# Test cases: (input, expected_output)
TEST_CASES = [
    ("FF", 255),
    ("ff", 255),  # Test case insensitivity
    ("99", 252),
    ("50", 128),
    ("0", 0),
    ("25", 64),
    ("75", 191),
]


def test_convert_level_valid_inputs():
    """Test conversion with valid inputs."""
    for input_val, expected in TEST_CASES:
        result = convert_level(input_val)
        assert result == expected, f"convert_level('{input_val}') should return {expected}, got {result}"


def test_convert_level_invalid_inputs():
    """Test conversion with invalid inputs."""
    invalid_inputs = ["100", "-1", "ABC", "GG", "", "99.5"]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(ValueError):
            convert_level(invalid_input)


def test_convert_level_edge_cases():
    """Test edge cases."""
    # Test that 0% maps to 0 and 99% maps to 252 (not 254 or 255)
    assert convert_level("0") == 0
    assert convert_level("99") == 252
    
    # Test that "FF" is the only way to get 255
    assert convert_level("FF") == 255
