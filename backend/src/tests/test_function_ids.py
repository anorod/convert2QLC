"""
Comprehensive tests to verify that function IDs start from 0 and are unique.
Tests use the provided test file (20260220-TestSimplePicolo.txt).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from converter.parser import PicoloParser
from converter.xml_generator import XMLGenerator
from converter.transformer import convert_cue_times
import pytest


def test_function_ids_start_from_zero():
    """Test that function IDs in generated XML start from 0."""
    # Read the test file
    with open("C:\\Users\\anorod\\source\\repos\\convert2QLC\\backend\\src\\tests\\20260220-TestSimplePicolo.txt", "r") as f:
        content = f.read()
    
    # Parse the Picolo file
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo",
        converted_cues,
        channel_data,
        max_channel_number,
        parser._channel_value_pairs
    )
    
    # Extract all function IDs from the XML
    import re
    function_id_pattern = r'ID="(\d+)"'
    matches = re.findall(function_id_pattern, xml_output)
    
    # Filter to only Function elements (not other elements with ID attributes)
    # We need a more precise approach - look for Function elements specifically
    function_ids = []
    lines = xml_output.split('\n')
    for line in lines:
        if '<Function' in line and 'ID=' in line:
            match = re.search(r'ID="(\d+)"', line)
            if match:
                function_ids.append(int(match.group(1)))
    
    # Verify that the first function ID is 0
    assert len(function_ids) > 0, "No Function elements found in XML"
    assert min(function_ids) == 0, f"First function ID should be 0, but found {min(function_ids)}"
    print(f"✓ First function ID is 0")


def test_function_ids_are_unique():
    """Test that all function IDs in generated XML are unique."""
    # Read the test file
    with open("C:\\Users\\anorod\\source\\repos\\convert2QLC\\backend\\src\\tests\\20260220-TestSimplePicolo.txt", "r") as f:
        content = f.read()
    
    # Parse the Picolo file
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo",
        converted_cues,
        channel_data,
        max_channel_number,
        parser._channel_value_pairs
    )
    
    # Extract all function IDs from the XML
    import re
    function_ids = []
    lines = xml_output.split('\n')
    for line in lines:
        if '<Function' in line and 'ID=' in line:
            match = re.search(r'ID="(\d+)"', line)
            if match:
                function_ids.append(int(match.group(1)))
    
    # Verify that all IDs are unique
    assert len(function_ids) > 0, "No Function elements found in XML"
    unique_ids = set(function_ids)
    assert len(unique_ids) == len(function_ids), \
        f"Duplicate function IDs found. Total IDs: {len(function_ids)}, Unique IDs: {len(unique_ids)}"
    print(f"✓ All {len(function_ids)} function IDs are unique")


def test_function_ids_sequential():
    """Test that function IDs form a sequential series starting from 0."""
    # Read the test file
    with open("C:\\Users\\anorod\\source\\repos\\convert2QLC\\backend\\src\\tests\\20260220-TestSimplePicolo.txt", "r") as f:
        content = f.read()
    
    # Parse the Picolo file
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo",
        converted_cues,
        channel_data,
        max_channel_number,
        parser._channel_value_pairs
    )
    
    # Extract all function IDs from the XML
    import re
    function_ids = []
    lines = xml_output.split('\n')
    for line in lines:
        if '<Function' in line and 'ID=' in line:
            match = re.search(r'ID="(\d+)"', line)
            if match:
                function_ids.append(int(match.group(1)))
    
    # Verify that IDs form a sequential series from 0
    assert len(function_ids) > 0, "No Function elements found in XML"
    sorted_ids = sorted(function_ids)
    expected_ids = list(range(len(sorted_ids)))
    assert sorted_ids == expected_ids, \
        f"Function IDs should be sequential from 0. Expected: {expected_ids}, Got: {sorted_ids}"
    print(f"✓ Function IDs form a complete sequential series from 0 to {len(function_ids)-1}")


def test_no_duplicate_function_ids():
    """Test that there are no duplicate function IDs in the generated XML."""
    # Read the test file
    with open("C:\\Users\\anorod\\source\\repos\\convert2QLC\\backend\\src\\tests\\20260220-TestSimplePicolo.txt", "r") as f:
        content = f.read()
    
    # Parse the Picolo file
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo",
        converted_cues,
        channel_data,
        max_channel_number,
        parser._channel_value_pairs
    )
    
    # Extract all function IDs from the XML
    import re
    function_id_pattern = r'ID="(\d+)"'
    matches = re.findall(function_id_pattern, xml_output)
    
    # Filter to only Function elements
    function_ids = []
    lines = xml_output.split('\n')
    for line in lines:
        if '<Function' in line and 'ID=' in line:
            match = re.search(r'ID="(\d+)"', line)
            if match:
                function_ids.append(int(match.group(1)))
    
    # Check for duplicates
    seen_ids = set()
    duplicates = []
    for func_id in function_ids:
        if func_id in seen_ids:
            duplicates.append(func_id)
        seen_ids.add(func_id)
    
    assert len(duplicates) == 0, \
        f"Found duplicate function IDs: {duplicates}. Each ID should appear only once."
    print(f"✓ No duplicate function IDs found in XML with {len(function_ids)} functions")


def test_function_id_count_matches_cue_count():
    """Test that the number of scene function IDs matches the number of cues."""
    # Read the test file
    with open("C:\\Users\\anorod\\source\\repos\\convert2QLC\\backend\\src\\tests\\20260220-TestSimplePicolo.txt", "r") as f:
        content = f.read()
    
    # Parse the Picolo file
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    
    # Count the number of cues
    num_cues = len(cue_list)
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo",
        converted_cues,
        channel_data,
        max_channel_number,
        parser._channel_value_pairs
    )
    
    # Extract all function IDs from the XML
    import re
    scene_ids = []
    chaser_ids = []
    lines = xml_output.split('\n')
    for line in lines:
        if '<Function' in line and 'ID=' in line and 'Type=' in line:
            match = re.search(r'ID="(\d+)"', line)
            type_match = re.search(r'Type="([^"]+)"', line)
            if match and type_match:
                func_id = int(match.group(1))
                func_type = type_match.group(1)
                if func_type == "Scene":
                    scene_ids.append(func_id)
                elif func_type == "Chaser":
                    chaser_ids.append(func_id)
    
    # Verify that the number of scene IDs matches the number of cues
    assert len(scene_ids) > 0, "No Scene elements found in XML"
    assert len(scene_ids) == num_cues, \
        f"Number of scene function IDs ({len(scene_ids)}) should match number of cues ({num_cues})"
    print(f"✓ Number of scene functions ({len(scene_ids)}) matches number of cues ({num_cues})")


if __name__ == "__main__":
    test_function_ids_start_from_zero()
    test_function_ids_are_unique()
    test_function_ids_sequential()
    test_no_duplicate_function_ids()
    test_function_id_count_matches_cue_count()
    print("\n✓ All tests passed!")
