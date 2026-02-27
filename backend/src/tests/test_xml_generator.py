"""
Tests for the XML Generator module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from converter.xml_generator import XMLGenerator
import pytest


def test_generate_base_xml():
    """Test that the base XML structure is generated correctly."""
    generator = XMLGenerator()
    root = generator.generate_base_xml("Test Show")
    
    assert root.tag == "Workspace"
    assert "xmlns" in root.attrib
    assert root.attrib["xmlns"] == "http://www.qlcplus.org/Workspace"


def test_generate_fixture():
    """Test that a fixture is generated with the correct number of channels."""
    generator = XMLGenerator()
    fixture = generator.generate_fixture(5)
    
    assert fixture.tag == "Fixture"
    assert fixture.get("Name") == "Dimmers"
    assert fixture.get("Channels") == "5"
    
    # Check that there are no Channel subelements (use FixtureVal instead)
    channels = fixture.findall("Channel")
    assert len(channels) == 0


def test_generate_scene():
    """Test that a scene is generated with correct channel levels and timing."""
    generator = XMLGenerator()
    
    # Test Scene type (default behavior - should have 0 values)
    scene = generator.generate_scene(1, ["255", "128", "0"], 1000, 2000, 3000)
    
    assert scene.tag == "Function"
    assert scene.get("Type") == "Scene"
    assert scene.get("Name") == "1. Cue 1"
    
    # Check Speed element - Scene types should have 0 values
    speed = scene.find("Speed")
    assert speed is not None
    assert speed.get("FadeIn") == "0"
    assert speed.get("FadeOut") == "0"
    assert speed.get("Duration") == "0"
    
    # Check FixtureVal element with comma-separated values
    fixture_val = scene.find("FixtureVal")
    assert fixture_val is not None
    assert fixture_val.get("ID") == "0"
    assert fixture_val.text == "255,128,0"
    
    # Test non-Scene type (should use provided timing values)
    scene2 = generator.generate_scene(2, ["128", "64"], 1000, 2000, 3000, is_scene_type=False)
    speed2 = scene2.find("Speed")
    assert speed2.get("FadeIn") == "1000"
    assert speed2.get("FadeOut") == "2000"
    assert speed2.get("Duration") == "3000"


def test_generate_chaser():
    """Test that a chaser is generated with correct scenes."""
    generator = XMLGenerator()
    
    # Create two sample scenes
    scene1 = generator.generate_scene(1, ["255"], 0, 0, 0)
    scene2 = generator.generate_scene(2, ["128"], 0, 0, 0)
    
    chaser = generator.generate_chaser([scene1, scene2])
    
    assert chaser.tag == "Function"
    assert chaser.get("Type") == "Chaser"
    assert chaser.get("Name") == "Cuelist"
    
    # Check that we have two steps
    steps = chaser.findall("Step")
    assert len(steps) == 2


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
    
    # Check that the XML contains key elements in QXW format
    assert "Workspace" in xml_output
    assert "Fixture" in xml_output
    assert "Function" in xml_output
    assert "Type=\"Scene\"" in xml_output
    assert "Type=\"Chaser\"" in xml_output