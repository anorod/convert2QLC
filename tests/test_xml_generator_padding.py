import pytest
from backend.src.converter.xml_generator import XMLGenerator

@pytest.fixture
def generator():
    return XMLGenerator()

@pytest.mark.parametrize("input_str, expected", [
    ("1", "01"),
    ("9", "09"),
    ("10", "10"),
])
def test_pad_integer_part(generator, input_str, expected):
    assert generator._pad_scene_pattern(input_str) == expected


@pytest.mark.parametrize("input_str, expected", [
    ("4.5", "04.5"),
    ("0", "00"),
    ("12.34", "12.34"),
])
def test_pad_decimal_preserves_decimal(generator, input_str, expected):
    assert generator._pad_scene_pattern(input_str) == expected


@pytest.mark.parametrize("bad_input", ["", "abc", "1a", "12.3.4"])
def test_pad_invalid_inputs_return_as_is(generator, bad_input):
    assert generator._pad_scene_pattern(bad_input) == bad_input
