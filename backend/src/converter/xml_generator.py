"""
XML Generator module for converting Picolo data to QLC+ XML format (.qxc).

This module provides functionality to generate QLC+ XML files from parsed Picolo show data.
It creates the base XML structure, a generic fixture, scenes for each cue, and a chaser
to sequence the scenes in the correct order.
"""

from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .transformer import convert_level, convert_time_value


class XMLGenerator:
    """Generator class for creating QLC+ XML files."""

    def __init__(self):
        """Initialize the XML generator with default namespace and version."""
        self.namespace = "http://www.qlcplus.org/QLCPlus"
        self.version = "4.12.0"  # QLC+ version

    def generate_base_xml(self, file_name: str) -> ET.Element:
        """Create the base XML structure for a QLC+ project.

        Args:
            file_name: The name of the file (used for project name)

        Returns:
            Root element of the XML document
        """
        # Create root element with proper namespace and version
        root = ET.Element("QLCPlus")
        root.set("version", self.version)
        root.set("name", file_name)
        
        return root

    def generate_fixture(self, max_channel_number: int) -> ET.Element:
        """Generate a generic fixture for the QLC+ project based on channel count.

        Args:
            max_channel_number: The highest channel number found in the parsed data

        Returns:
            Fixture element with appropriate configuration
        """
        # Create fixture element
        fixture = ET.Element("Fixture")
        fixture.set("Name", "Generic Fixture")
        fixture.set("Manufacturer", "Picolo Converter")
        fixture.set("Model", "Generic")
        fixture.set("Type", "Generic")
        fixture.set("Channels", str(max_channel_number))
        
        # Add channels to the fixture (for each channel, we just add a basic channel element)
        for i in range(1, max_channel_number + 1):
            channel = ET.SubElement(fixture, "Channel")
            channel.set("Name", f"Channel {i}")
            channel.set("Group", "Generic")
            channel.set("Type", "Intensity")
            channel.set("Min", "0")
            channel.set("Max", "255")
            channel.set("Default", "0")
            channel.set("Description", f"Channel {i} of the generic fixture")
        
        return fixture

    def generate_scene(self, cue_number: int, channel_levels: List[str], 
                      fade_in: int, fade_out: int, hold: int) -> ET.Element:
        """Generate a scene element for a specific cue with channel levels and timing.

        Args:
            cue_number: The cue number (used for scene name)
            channel_levels: List of channel level values in QLC+ decimal format (0-255)
            fade_in: FadeIn time in milliseconds
            fade_out: FadeOut time in milliseconds
            hold: Hold time in milliseconds

        Returns:
            Scene element with channel data and timing attributes
        """
        # Create scene element with a descriptive name
        scene = ET.Element("Scene")
        scene.set("Name", f"Cue {cue_number} Scene")
        scene.set("FadeIn", str(fade_in))
        scene.set("FadeOut", str(fade_out))
        scene.set("Hold", str(hold))
        
        # Add channel data to the scene
        for i, level in enumerate(channel_levels):
            # Skip if level is empty or None
            if not level:
                continue
                
            channel = ET.SubElement(scene, "Channel")
            channel.set("Number", str(i + 1))  # Channel numbers are 1-based
            channel.set("Level", str(level))
        
        return scene

    def generate_chaser(self, scenes: List[ET.Element]) -> ET.Element:
        """Generate a chaser that sequences all scenes in order.

        Args:
            scenes: List of scene elements to include in the chaser

        Returns:
            Chaser element with all scenes included in sequence
        """
        # Create chaser element
        chaser = ET.Element("Chaser")
        chaser.set("Name", "Picolo Cue Sequence")
        chaser.set("Mode", "Forward")
        chaser.set("Direction", "Forward")
        chaser.set("Loop", "false")
        chaser.set("FadeIn", "0")
        chaser.set("FadeOut", "0")
        chaser.set("Hold", "0")
        
        # Add all scenes to the chaser in order
        for i, scene in enumerate(scenes):
            # Get the scene name and create a step for it
            scene_name = scene.get("Name", f"Scene {i + 1}")
            step = ET.SubElement(chaser, "Step")
            step.set("Scene", scene_name)
            step.set("Duration", "0")  # Use default duration or calculate based on cue times
            
        return chaser

    def generate_xml(self, file_name: str, cue_list: List[Dict], 
                    channel_data: Dict[int, List[str]], max_channel_number: int) -> str:
        """Generate complete QLC+ XML document from parsed Picolo data.

        Args:
            file_name: Name of the original Picolo file (used for project name)
            cue_list: List of parsed cues with time information
            channel_data: Dictionary mapping cue numbers to channel data
            max_channel_number: Highest channel number found in the file

        Returns:
            Formatted XML string representing the QLC+ project
        """
        # Create base XML structure
        root = self.generate_base_xml(file_name)
        
        # Create fixture element with appropriate channel count
        fixture = self.generate_fixture(max_channel_number)
        root.append(fixture)
        
        # Generate scenes for each cue (convert cue times first)
        scenes = []
        for i, cue in enumerate(cue_list):
            # Get the channel levels for this cue
            try:
                cue_number = int(float(cue.get("cue_number", 0)))
            except ValueError:
                continue
            levels = channel_data.get(cue_number, [])
            
            # Get time values from cue (these are already converted by transformer)
            fade_in = int(cue.get("FadeIn", 0))
            fade_out = int(cue.get("FadeOut", 0)) 
            hold = int(cue.get("Hold", 0))
            
            # Create scene with channel levels and timing
            scene = self.generate_scene(cue_number, levels, fade_in, fade_out, hold)
            scenes.append(scene)
            root.append(scene)
        
        # Create chaser to sequence all scenes
        chaser = self.generate_chaser(scenes)
        root.append(chaser)
        
        # Convert the XML tree to a formatted string
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")