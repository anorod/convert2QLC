"""
Tests for the XML Generator module.
"""

import pytest
from converter.xml_generator import XMLGenerator


def test_generate_base_xml():
    """Test that the base XML structure is generated correctly."""
    generator = XMLGenerator()
    root = generator.generate_base_xml("Test Show")
    
    assert root.tag == "QLCPlus"
    assert root.get("version") == "4.12.0"
    assert root.get("name") == "Test Show"


def test_generate_fixture():
    """Test that a fixture is generated with the correct number of channels."""
    generator = XMLGenerator()
    fixture = generator.generate_fixture(5)
    
    assert fixture.tag == "Fixture"
    assert fixture.get("Name") == "Generic Fixture"
    assert fixture.get("Channels") == "5"
    
    # Check that we have 5 channel elements
    channels = fixture.findall("Channel")
    assert len(channels) == 5
    
    # Check first channel
    first_channel = channels[0]
    assert first_channel.get("Name") == "Channel 1"
    assert first_channel.get("Group") == "Generic"
    assert first_channel.get("Type") == "Intensity"


def test_generate_scene():
    """Test that a scene is generated with correct channel levels and timing."""
    generator = XMLGenerator()
    scene = generator.generate_scene(1, ["255", "128", "0"], 1000, 2000, 3000)
    
    assert scene.tag == "Scene"
    assert scene.get("Name") == "Cue 1 Scene"
    assert scene.get("FadeIn") == "1000"
    assert scene.get("FadeOut") == "2000"
    assert scene.get("Hold") == "3000"
    
    # Check that channels are correctly added
    channels = scene.findall("Channel")
    assert len(channels) == 3
    
    # Check first channel
    assert channels[0].get("Number") == "1"
    assert channels[0].get("Level") == "255"
    
    # Check second channel
    assert channels[1].get("Number") == "2"
    assert channels[1].get("Level") == "128"


def test_generate_chaser():
    """Test that a chaser is generated with correct scenes."""
    generator = XMLGenerator()
    
    # Create two sample scenes
    scene1 = generator.generate_scene(1, ["255"], 0, 0, 0)
    scene2 = generator.generate_scene(2, ["128"], 0, 0, 0)
    
    chaser = generator.generate_chaser([scene1, scene2])
    
    assert chaser.tag == "Chaser"
    assert chaser.get("Name") == "Picolo Cue Sequence"
    
    # Check that we have two steps
    steps = chaser.findall("Step")
    assert len(steps) == 2
    
    # Check first step
    assert steps[0].get("Scene") == "Cue 1 Scene"
    
    # Check second step
    assert steps[1].get("Scene") == "Cue 2 Scene"


def test_generate_xml():
    """Test that complete XML is generated correctly."""
    generator = XMLGenerator()
    
    # Sample data
    cue_list = [
        {"cue_number": "1.0", "TI": "3", "TO": "2", "TW": "5"},
        {"cue_number": "2.0", "TI": "2", "TO": "1", "TW": "3"}
    ]
    channel_data = {
        1: ["255", "128"],
        2: ["128", "64"]
    }
    max_channel_number = 2
    
    xml_output = generator.generate_xml("Test Show", cue_list, channel_data, max_channel_number)
    
    # Check that the XML contains key elements
    assert "QLCPlus" in xml_output
    assert "Fixture" in xml_output
    assert "Scene" in xml_output
    assert "Chaser" in xml_output
    assert "Test Show" in xml_output