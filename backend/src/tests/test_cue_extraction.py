"""
Test suite for the cue details extraction functionality.

This module tests the extract_cue_details_section method in XMLGenerator
to ensure it correctly extracts the detailed cue information from Picolo files.
"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from converter.xml_generator import XMLGenerator


def test_extract_cue_details_from_test_file():
    """Test extraction of cue details from the test file (lines 315-338)."""
    # Read the test file (local copy in tests directory)
    test_file_path = Path(__file__).parent / "20260220-TestSimplePicolo.txt"
    with open(test_file_path, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # Create generator instance
    generator = XMLGenerator()
    
    # Extract cue details section
    result = generator.extract_cue_details_section(content)
    
    # Verify the extraction worked correctly - should get DETAILED section only
    assert "Cue    TI   TO   TW" in result, "Header should be present"
    assert "Channels Patch" not in result, "Should not include Channels Patch line"
    assert "Cue inicial" in result, "First cue description should be present"
    assert "Cue 2 segunda auto" in result, "Second cue description should be present"
    assert "Otra Cue BK" in result, "Last cue description should be present"
    
    # Verify we're NOT getting the summary section (which has different patterns)
    for line in result.split('\n'):
        assert not line.startswith("Shp Text"), "Should not include summary section patterns"
        assert not line.startswith("CmyFlash"), "Should not include summary section patterns"
    
    # Verify we DO have detailed cue data with channel values
    lines = result.split('\n')
    assert 20 <= len(lines) <= 30, f"Should extract around 25 lines, got {len(lines)}"
    assert "Channels" in result and "Patch" not in result, "Should have Channels marker"
    assert any(val in result for val in ["FF", "30", "50"]), "Should contain channel values"


def test_extract_cue_details_empty_content():
    """Test behavior with empty content."""
    generator = XMLGenerator()
    
    with pytest.raises(ValueError, match="Cue details section header not found"):
        generator.extract_cue_details_section("")


def test_extract_cue_details_no_header():
    """Test behavior when cue header is not present."""
    generator = XMLGenerator()
    
    with pytest.raises(ValueError, match="Cue details section header not found"):
        generator.extract_cue_details_section("Some random content\nLine 2\nLine 3")


def test_extract_cue_details_minimal_valid_content():
    """Test with minimal valid content containing just the cue section."""
    generator = XMLGenerator()
    
    # Create minimal content with cue section
    content = """Some header content
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      3    3    Manua          T1           Cue inicial                              c  -
Channels Patch
More content"""
    
    result = generator.extract_cue_details_section(content)
    
    # Should extract from header to Channels Patch (excluding it)
    assert "Cue    TI   TO   TW" in result
    assert "Cue inicial" in result
    assert "Channels Patch" not in result
    assert "More content" not in result


def test_extract_cue_details_with_empty_lines():
    """Test extraction when section ends with empty lines."""
    generator = XMLGenerator()
    
    # Create content ending with empty line
    content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      3    3    Manua          T1           Cue inicial                              c  -
Channels

More content"""
    
    result = generator.extract_cue_details_section(content)
    
    # Should extract from header to first empty line after Channels
    assert "Cue    TI   TO   TW" in result
    assert "Cue inicial" in result
    assert "More content" not in result


def test_extract_cue_details_multiple_sections():
    """Test that we extract the SECOND cue section (detailed one)."""
    generator = XMLGenerator()
    
    # Create content with multiple cue sections
    # First is a summary-like section, second is detailed with channels
    content = """First header
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      3    3    Manua          T1           Cue inicial                              c  -
Channels Patch
Some other section
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
2      3    3    Manua          T1           Second cue                              c  -
Channels
FF FF FF"""
    
    result = generator.extract_cue_details_section(content)
    
    # Should extract the SECOND section (the detailed one with channels)
    assert "Cue inicial" not in result, "Should not include first section"
    assert "Second cue" in result, "Should include second section"
    assert "FF FF FF" in result, "Should include channel data from second section"


def test_extract_cue_details_with_group_sections():
    """Test extraction when Group sections appear after Channels Patch."""
    generator = XMLGenerator()
    
    # Create content with cue section followed by Group sections
    content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      3    3    Manua          T1           Cue inicial                              c  -
Channels Patch

Group TI   TO   TW   Tm Text         cfs
500   3    3    ManuaT1              c  -"""
    
    result = generator.extract_cue_details_section(content)
    
    # Should extract cue section but NOT the Group sections
    assert "Cue    TI   TO   TW" in result
    assert "Cue inicial" in result
    assert "Channels Patch" not in result
    assert "Group TI" not in result, "Should exclude Group sections after Channels Patch"
    assert "500   3    3" not in result
