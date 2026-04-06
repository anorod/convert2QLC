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
        self.workspace_namespace = "http://www.qlcplus.org/Workspace"
        self.version = "4.12.0"  # QLC+ version

    def generate_base_xml(self, file_name: str) -> ET.Element:
        """Create the base XML structure for a QLC+ project.

        Args:
            file_name: The name of the file (used for project name)

        Returns:
            Root element of the XML document
        """
        # Create root element with proper namespace and version
        root = ET.Element("Workspace")
        root.set("xmlns", self.workspace_namespace)

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
        fixture.set("Manufacturer", "Generic")
        fixture.set("Model", "Generic")
        fixture.set("Mode", "71 Channel")
        fixture.set("ID", "0")
        fixture.set("Name", "Dimmers")
        fixture.set("Universe", "0")
        fixture.set("Address", "0")
        fixture.set("Channels", str(max_channel_number))

        return fixture


    def generate_scene(self, cue_number: int, channel_data: Dict[int, str],
                      fade_in: int, fade_out: int, hold: int, is_scene_type: bool = True,
                      function_id: Optional[str] = None, cue_info: Optional[Dict] = None) -> ET.Element:
        """Generate a scene element for a specific cue with channel levels and timing.

        Args:
            cue_number: The cue number as string (used for scene name, preserves decimals like "4.5")
            channel_data: Dictionary mapping channel numbers to their QLC+ level values,
                          or list of values in order (for backward compatibility)
            fade_in: FadeIn time in milliseconds
            fade_out: FadeOut time in milliseconds
            hold: Hold time in milliseconds
            is_scene_type: Whether this function should be treated as a Scene type.
                           If True, sets Speed attributes to 0. Defaults to True for backward compatibility.
            function_id: Optional custom ID for the Function element. If not provided,
                         defaults to cue_number for backward compatibility.

        Returns:
            Scene element with channel data and timing attributes
        """
        # Create Function element with a descriptive name (QXW format)
        function = ET.Element("Function")
        function_id_to_use = str(function_id) if function_id is not None else str(cue_number)
        function.set("ID", function_id_to_use)
        function.set("Type", "Scene")
        
        # Use Text from cue_info if available, otherwise use default format
        cue_text = cue_info.get("Text", "") if cue_info else ""
        if cue_text.strip():
            function.set("Name", f"{cue_number}. {cue_text.strip()}")
        else:
            function.set("Name", f"{cue_number}. Cue {cue_number}")

        # Add Speed element with timing information
        speed = ET.SubElement(function, "Speed")
        if is_scene_type:
            speed.set("FadeIn", "0")
            speed.set("FadeOut", "0")
            speed.set("Duration", "0")
        else:
            speed.set("FadeIn", str(fade_in))
            speed.set("FadeOut", str(fade_out))
            speed.set("Duration", str(hold))

        # Add FixtureVal elements with channel-value pairs
        if isinstance(channel_data, dict) and channel_data:
            fixture_val = ET.SubElement(function, "FixtureVal")
            fixture_val.set("ID", "0")

            # Check if this is a new format (channel_num -> value)
            first_key = list(channel_data.keys())[0] if channel_data else None
            if isinstance(first_key, int) and isinstance(channel_data[first_key], str):
                # New format: {channel_number: value}
                channel_pairs = []
                for channel_num in sorted(channel_data.keys()):
                    value = channel_data[channel_num]
                    fixture_index = int(channel_num) - 1
                    channel_pairs.append(f"{fixture_index},{value}")
                fixture_val.text = ",".join(channel_pairs)
            else:
                # Handle old format properly
                if len(channel_data) > 0 and isinstance(list(channel_data.values())[0], list):
                    # Old format: {cue_number: [values]}
                    first_key = list(channel_data.keys())[0]
                    if isinstance(channel_data[first_key], list):
                        fixture_val.text = ",".join(str(v) for v in channel_data[first_key])
                else:
                    # Fallback to simple handling
                    if isinstance(list(channel_data.values())[0], str):
                        channel_pairs = []
                        for channel_num in sorted(channel_data.keys()):
                            value = channel_data[channel_num]
                            fixture_index = int(channel_num) - 1
                            channel_pairs.append(f"{fixture_index},{value}")
                        fixture_val.text = ",".join(channel_pairs)
        elif isinstance(channel_data, list) and channel_data:
            fixture_val = ET.SubElement(function, "FixtureVal")
            fixture_val.set("ID", "0")
            # Backward compatibility: use comma-separated values (old format)
            fixture_val.text = ",".join(str(v) for v in channel_data)

        return function

    def generate_chaser(self, scenes: List[ET.Element]) -> ET.Element:
        """Generate a chaser that sequences all scenes in order.

        Args:
            scenes: List of scene elements to include in the chaser

        Returns:
            Chaser element with all scenes included in sequence
        """
        # Create chaser element (QXW format)
        chaser = ET.Element("Function")
        total_scenes = len(scenes)
        chaser.set("ID", str(total_scenes))
        chaser.set("Type", "Chaser")
        chaser.set("Name", "Cuelist")

        # Add Speed element
        speed = ET.SubElement(chaser, "Speed")
        speed.set("FadeIn", "0")
        speed.set("FadeOut", "0")
        speed.set("Duration", "0")

        # Add Direction and RunOrder
        ET.SubElement(chaser, "Direction").text = "Forward"
        ET.SubElement(chaser, "RunOrder").text = "Loop"

        # Add SpeedModes
        speed_modes = ET.SubElement(chaser, "SpeedModes")
        speed_modes.set("FadeIn", "PerStep")
        speed_modes.set("FadeOut", "PerStep")
        speed_modes.set("Duration", "PerStep")

        # Add steps for each scene
        for i, scene in enumerate(scenes):
            step = ET.SubElement(chaser, "Step")
            step.set("Number", str(i))
            # Get timing from the scene's Speed element
            speed_elem = scene.find("Speed")
            if speed_elem is not None:
                fade_in = int(speed_elem.get("FadeIn", 0))
                hold = int(speed_elem.get("Duration", 4294967294))
                fade_out = int(speed_elem.get("FadeOut", 0))
            else:
                fade_in = 0
                hold = 4294967294
                fade_out = 0

            step.set("FadeIn", str(fade_in * 1000 if fade_in > 0 else fade_in))
            step.set("Hold", str(hold if hold != 4294967294 else 4294967294))
            step.set("FadeOut", str(fade_out * 1000 if fade_out > 0 else fade_out))
            step.text = str(i)

        return chaser

    def generate_engine_section(self, file_name: str, max_channel_number: int) -> ET.Element:
        """Generate the Engine section for QXW format.

        Args:
            file_name: Name of the original Picolo file
            max_channel_number: Highest channel number found in the file

        Returns:
            Engine element with all subsections
        """
        engine = ET.Element("Engine")

        # Add InputOutputMap
        io_map = ET.SubElement(engine, "InputOutputMap")
        beat_gen = ET.SubElement(io_map, "BeatGenerator")
        beat_gen.set("BeatType", "Disabled")
        beat_gen.set("BPM", "0")

        # Add Universes
        for i in range(1, 5):
            universe = ET.SubElement(io_map, "Universe")
            universe.set("Name", f"Universe {i}")
            universe.set("ID", str(i-1))

         # Add Fixture
        fixture = self.generate_fixture(max_channel_number)
        engine.append(fixture)

        return engine

    def generate_virtual_console_section(self) -> ET.Element:
        """Generate the VirtualConsole section for QXW format."""
        vc = ET.Element("VirtualConsole")

        # Add Frame
        frame = ET.SubElement(vc, "Frame")
        frame.set("Caption", "")
        appearance = ET.SubElement(frame, "Appearance")
        appearance.set("FrameStyle", "None")
        appearance.set("ForegroundColor", "Default")
        appearance.set("BackgroundColor", "Default")
        appearance.set("BackgroundImage", "None")
        appearance.set("Font", "Default")

        # Add Properties
        properties = ET.SubElement(vc, "Properties")
        size = ET.SubElement(properties, "Size")
        size.set("Width", "1920")
        size.set("Height", "1080")
        grand_master = ET.SubElement(properties, "GrandMaster")
        grand_master.set("Visible", "1")
        grand_master.set("ChannelMode", "Intensity")
        grand_master.set("ValueMode", "Reduce")
        grand_master.set("SliderMode", "Normal")

        return vc

    def generate_simple_desk_section(self) -> ET.Element:
        """Generate the SimpleDesk section for QXW format."""
        sd = ET.Element("SimpleDesk")
        engine = ET.SubElement(sd, "Engine")
        return sd

    def extract_cue_details_section(self, content: str) -> str:
        """Extract the detailed cue section from Picolo file content.

        Args:
            content: The raw text content of the Picolo file

        Returns:
            String containing only the cue details section (lines 315-338 in test file)

        Raises:
            ValueError: If the cue details section cannot be found
        """
        lines = content.split('\n')
        start_line = None
        end_line = None

        # Find the start of cue details section (line with "Cue    TI   TO   TW")
        # We need to find the SECOND occurrence if it exists, as the first is typically a summary section
        header_count = 0
        first_header_line = None
        second_header_line = None
        for i, line in enumerate(lines):
            if line.startswith("Cue    TI   TO   TW"):
                header_count += 1
                if header_count == 1:
                    first_header_line = i
                elif header_count == 2:
                    second_header_line = i
                    break

        # Use the second header if found, otherwise use the first one
        start_line = second_header_line if second_header_line is not None else first_header_line

        if start_line is None:
            raise ValueError("Cue details section header not found")

        # Find the end of cue details section
        # The pattern is: Cue header -> cue number line -> Channels -> channel numbers -> values
        # We need to find where this pattern stops and Group sections start

        in_cue_section = True  # We're starting at a cue header, so we're in the cue section
        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Mark that we're in the cue data section when we see a cue line
            if line.startswith("Cue    "):
                in_cue_section = True
            elif line.startswith("Group TI"):
                # Found Group sections - these should not be included in cue details
                end_line = i
                break
            elif line.strip() == "Channels Patch":
                # Found Channels Patch marker - this should not be included in cue details
                end_line = i
                break
            elif in_cue_section and line.strip() == "":
                # Empty line after cue data indicates potential end
                # But check if there are more cues coming
                next_non_empty = i + 1
                while next_non_empty < len(lines) and lines[next_non_empty].strip() == "":
                    next_non_empty += 1

                if next_non_empty < len(lines):
                    # Check if the next non-empty line starts a new Cue section, Group, or Channels Patch
                    if not lines[next_non_empty].startswith("Cue    ") and not lines[next_non_empty].startswith("Group TI") and not lines[next_non_empty].strip() == "Channels Patch":
                        end_line = i
                        break
                else:
                    # End of file reached
                    end_line = len(lines)

            # If we've gone past a reasonable number of lines, stop
            if i > start_line + 500:  # Safety limit
                end_line = i
                break
            elif in_cue_section and line.strip() == "":
                # Empty line after cue data indicates potential end
                # But check if there are more cues coming
                next_non_empty = i + 1
                while next_non_empty < len(lines) and lines[next_non_empty].strip() == "":
                    next_non_empty += 1

                if next_non_empty < len(lines):
                    # Check if the next non-empty line starts a new Cue section, Group, or Channels Patch
                    if not lines[next_non_empty].startswith("Cue    ") and not lines[next_non_empty].strip() == "Channels Patch":
                        end_line = i
                        break
                else:
                    # End of file reached
                    end_line = len(lines)
                    break

        if end_line is None:
            # If no clear end marker found, use a reasonable default
            end_line = start_line + 25  # Typically around 25 lines of cue data

        # Extract and return the section
        cue_section = '\n'.join(lines[start_line:end_line])
        return cue_section

    def generate_xml(self, file_name: str, cue_list: List[Dict],
                    channel_data: Dict[str, List[str]], max_channel_number: int,
                    channel_value_pairs: Dict[str, Dict[int, str]] = {}) -> str:
        """Generate complete QLC+ XML document from parsed Picolo data.

        Args:
            file_name: Name of the original Picolo file (used for project name)
            cue_list: List of parsed cues with time information
            channel_data: Dictionary mapping cue numbers to channel data
            max_channel_number: Highest channel number found in the file
            channel_value_pairs: Optional dictionary mapping cue numbers to channel-value pairs

        Returns:
            Formatted XML string representing the QLC+ project
        """
        # Create base XML structure (Workspace)
        root = self.generate_base_xml(file_name)

        # Add CurrentWindow attribute
        root.set("CurrentWindow", "FunctionManager")

        # Add Creator section
        creator = ET.SubElement(root, "Creator")
        ET.SubElement(creator, "Name").text = "Q Light Controller Plus"
        ET.SubElement(creator, "Version").text = self.version
        ET.SubElement(creator, "Author").text = "anorod"

        # Generate Engine section with InputOutputMap, Fixture, and Functions
        engine = self.generate_engine_section(file_name, max_channel_number)
        root.append(engine)

        # Generate scenes for each cue (convert cue times first)
        scenes = []
        for i, cue in enumerate(cue_list):
            # Get the channel levels for this cue - preserve original string format (including decimals like "4.5")
            cue_number_str = cue.get("cue_number", "0")
            
            # Validate cue number is numeric (skip non-numeric cues like "Group" or "Channels")
            try:
                float(cue_number_str)  # Just validate, don't convert
            except ValueError:
                continue

            # Get time values from cue (these are already converted by transformer)
            fade_in = int(cue.get("FadeIn", 0))
            fade_out = int(cue.get("FadeOut", 0))
            hold = int(cue.get("Hold", 0))

            # Get the appropriate channel data for this cue - use original string key
            if cue_number_str in channel_value_pairs:
                # Use the detailed channel-value pairs
                cue_channels = channel_value_pairs[cue_number_str]
            else:
                # Fallback to flat list (for backward compatibility)
                cue_channels = {}
                levels = channel_data.get(cue_number_str, [])
                for j, level in enumerate(levels):
                    cue_channels[j+1] = level

            # Create scene with channel levels and timing - use original string to preserve decimals
            # Pass the scene index (i) as function_id to ensure unique sequential IDs starting from 0
            scene = self.generate_scene(cue_number_str, cue_channels, fade_in, fade_out, hold, is_scene_type=True, function_id=str(i), cue_info=cue)
            scenes.append(scene)
            engine.append(scene)

        # Create chaser to sequence all scenes
        chaser = self.generate_chaser(scenes)
        engine.append(chaser)

        # Add Monitor section
        monitor = ET.SubElement(engine, "Monitor")
        monitor.set("DisplayMode", "0")
        monitor.set("ShowLabels", "0")
        font = ET.SubElement(monitor, "Font")
        font.text = "Arial,12,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        monitor.append(ET.Element("ChannelStyle", {"text": "0"}))
        monitor.append(ET.Element("ValueStyle", {"text": "0"}))
        grid = ET.SubElement(monitor, "Grid")
        grid.set("Width", "5")
        grid.set("Height", "3")
        grid.set("Depth", "5")
        grid.set("Units", "0")

        # Add VirtualConsole section
        vc = self.generate_virtual_console_section()
        root.append(vc)

        # Add SimpleDesk section
        sd = self.generate_simple_desk_section()
        root.append(sd)

        # Convert the XML tree to a formatted string
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
