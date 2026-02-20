"""
Parser module for Picolo show files.

This module provides functionality to parse Picolo .txt files and extract
structured data including cue lists, channel levels, and maximum channel numbers.
"""

from typing import Dict, List, Optional
import re

from .transformer import convert_level


class InvalidFileFormatError(Exception):
    """Custom exception for invalid Picolo file formats."""

    pass


class PicoloParser:
    """Parser class for Picolo show files."""

    def __init__(self, content: str):
        """Initialize the parser with file content.

        Args:
            content: The raw text content of the Picolo file.
        """
        self.content = content
        self.cue_list: List[Dict[str, str]] = []
        self.channel_data: Dict[int, List[str]] = {}
        self.max_channel_number: Optional[int] = None

    def parse_cue_list(self) -> List[Dict[str, str]]:
        """Parse the Cue List section of the Picolo file.

        Returns:
            A list of dictionaries containing cue information.

        Raises:
            InvalidFileFormatError: If the Cue List section cannot be parsed.
        """
        # Find all cue lines in the format:
        # "Cue TI TO TW Ti To Tm Jump Lp Text Command TC cfs"
        # followed by lines with cue data
        cues: List[Dict[str, str]] = []
        lines = self.content.split("\n")

        i = 0
        found_cue_header = False

        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a cue header line (starts with "Cue" and has the column headers)
            if line.startswith("Cue") and "TI" in line and "TO" in line:
                found_cue_header = True
                # Skip the header line
                i += 1

                # Now look for actual cue data lines - these are lines that start with a number
                while i < len(lines):
                    cue_line = lines[i].strip()

                    # Stop processing when we hit a new Cue header, Channels line, or empty line
                    if (
                        not cue_line
                        or cue_line.startswith("Cue")
                        or cue_line == "Channels"
                    ):
                        break

                    # Parse cue line: "0.1 3 3 Manua T1 CUE -"
                    # (CueNum TI TO TW Ti To Tm Jump Lp Text Command TC cfs)
                    parts = cue_line.split()
                    if len(parts) >= 1:
                        cue_number = parts[0]
                        # Extract time values TI, TO, TW from the cue line
                        cue_data = {
                            "cue_number": cue_number,
                            "TI": parts[1] if len(parts) > 1 else "0",
                            "TO": parts[2] if len(parts) > 2 else "0", 
                            "TW": parts[3] if len(parts) > 3 else "0"
                        }
                        cues.append(cue_data)
                    i += 1
            else:
                i += 1

        # If no cue header was found, this is not a valid Picolo file
        if not found_cue_header and cues:
            raise InvalidFileFormatError("Invalid Cue List format")
        elif not found_cue_header:
            raise InvalidFileFormatError("Cue List section not found or invalid format")

        return cues

    def parse_channel_data(self) -> Dict[int, List[str]]:
        """Parse channel data from the Cues content section.

        Returns:
            A dictionary mapping cue numbers to channel data.

        Raises:
            InvalidFileFormatError: If the channel data cannot be parsed.
        """
        # Parse channel data sections
        channel_data: Dict[int, List[str]] = {}
        lines = self.content.split("\n")

        i = 0
        current_cue_number = None
        max_iterations = len(lines) * 2  # Safety limit to prevent infinite loops
        iterations = 0

        while i < len(lines) and iterations < max_iterations:
            line = lines[i].strip()

            # Check if this is a "Channels" line (indicates channel data follows)
            if line == "Channels":
                i += 1

                channels_line1 = []
                channels_line2 = []

                # Read the next two lines for channel values
                # Skip any separator lines that might appear before actual channel data
                while i < len(lines) and not lines[i].strip():
                    i += 1
                    
                if i < len(lines) and lines[i].strip():
                    channels_line1 = lines[i].strip().split()
                    i += 1

                # Skip any separator lines that might appear before second channel data line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                    
                if i < len(lines) and lines[i].strip():
                    channels_line2 = lines[i].strip().split()
                    i += 1

                # Combine both lines of channel data
                all_channels = channels_line1 + channels_line2

                # Filter out any non-numeric values (like separator lines)
                filtered_channels = [ch for ch in all_channels if ch and not re.match(r'^-+$', ch)]

                if current_cue_number is not None and filtered_channels:
                    # Convert cue number to int for consistency
                    cue_int = int(round(current_cue_number))

                    # Convert Picolo levels to QLC+ format
                    converted_channels = []
                    for channel_str in filtered_channels:
                        try:
                            qlc_value = convert_level(channel_str)
                            converted_channels.append(str(qlc_value))
                        except ValueError:
                            # Keep original value if conversion fails
                            converted_channels.append(channel_str)

                    channel_data[cue_int] = converted_channels
            elif line.startswith("Cue") and "TI" in line and "TO" in line:
                # Skip cue header - i will be incremented at the end of loop
                pass
            elif re.match(r"^\s*\d+(\.\d+)?\s+\d", line):
                # Cue data line: starts with number, followed by space, then another digit
                match = re.search(r"(\d+(\.\d+)?)", line)
                if match:
                    try:
                        val = float(match.group(1))
                        current_cue_number = val
                    except ValueError:
                        # Skip lines that can't be converted to float (e.g., separator lines)
                        current_cue_number = None
            # Always increment i to move to next line
            i += 1
            iterations += 1

        # Assign the result to self.channel_data as expected by tests
        self.channel_data = channel_data
        return channel_data

    def find_max_channel_number(self) -> Optional[int]:
        """Find and store the highest channel number in the file.

        Returns:
            The maximum channel number found, or None if not found.
        """
        # Find max channel from all channel data
        max_channel = 0

        for cue_channels in self.channel_data.values():
            for channel_str in cue_channels:
                try:
                    # Convert hex string to integer
                    if channel_str.startswith("0x"):
                        channel_num = int(channel_str, 16)
                    else:
                        channel_num = int(channel_str)

                    if channel_num > max_channel:
                        max_channel = channel_num
                except ValueError:
                    # Skip non-numeric values
                    continue

        return max_channel if max_channel > 0 else None

    def parse(self) -> Dict[str, object]:
        """Parse the entire Picolo file and return structured data.

        Returns:
            A dictionary containing parsed cue list, channel data,
            and maximum channel number.

        Raises:
            InvalidFileFormatError: If any section cannot be parsed.
        """
        self.cue_list = self.parse_cue_list()
        self.channel_data = self.parse_channel_data()
        self.max_channel_number = self.find_max_channel_number()

        return {
            "cue_list": self.cue_list,
            "channel_data": self.channel_data,
            "max_channel_number": self.max_channel_number,
        }