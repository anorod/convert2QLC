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
        self.channel_data: Dict[str, List[str]] = {}
        self.max_channel_number: Optional[int] = None
        self.channel_mapping: Dict[int, int] = {}
        self._channel_value_pairs: Dict[str, Dict[int, str]] = {}

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
        in_detailed_section = False  # Track if we're in the detailed section with channel data

        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a cue header line (starts with "Cue" and has the column headers)
            if line.startswith("Cue") and "TI" in line and "TO" in line:
                found_cue_header = True
                
                # Look ahead to determine if this is a summary or detailed section
                # A detailed section has ONE cue data line followed by Channels (or another Cue header)
                # A summary section has MULTIPLE cue data lines before the next Cue header
                lookahead_pos = i + 1
                is_summary_section = False
                
                # Count how many cue data lines are in this section
                cue_data_count = 0
                while lookahead_pos < len(lines):
                    lookahead_line = lines[lookahead_pos].strip()
                    
                    # If we find a "Channels" line, this is NOT a summary (it's detailed)
                    if lookahead_line == "Channels":
                        break
                    # If we hit another Cue header, check how many cues were in this section
                    elif lookahead_line.startswith("Cue") and "TI" in lookahead_line:
                        is_summary_section = (cue_data_count > 1)
                        break
                    # Count cue data lines (lines that start with a number)
                    elif (lookahead_line and not lookahead_line.startswith("-") and 
                         not lookahead_line.startswith("Cue")):
                        parts = lookahead_line.split()
                        if parts:
                            first_token = parts[0]
                            # Check if it's a number (with optional decimal point)
                            is_number = True
                            dot_count = 0
                            for c in first_token:
                                if not c.isdigit() and c != '.':
                                    is_number = False
                                    break
                                elif c == '.':
                                    dot_count += 1
                                    if dot_count > 1:
                                        is_number = False
                                        break
                            if is_number:
                                cue_data_count += 1
                    lookahead_pos += 1
                
                # Move past the cue header line before processing data
                i += 1
                
                # Only parse cue data if this is NOT a summary section
                # If it's a summary section, skip to the next Cue header
                if is_summary_section:
                    # Skip all lines until we hit the next Cue header
                    while i < len(lines):
                        line = lines[i].strip()
                        # Stop when we find another Cue header
                        if line.startswith("Cue") and "TI" in line:
                            break
                        i += 1
                    continue
                
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
                        # Skip lines that look like "Channels" or other non-cue data
                        if cue_number == "Channels":
                            i += 1
                            continue
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

    def parse_channel_data(self) -> Dict[str, List[str]]:
        """Parse channel data from the Cues content section.

        Returns:
            A dictionary mapping cue numbers to channel data.

        Raises:
            InvalidFileFormatError: If the channel data cannot be parsed.
        """
        # Parse channel data sections
        channel_data: Dict[str, List[str]] = {}
        lines = self.content.split("\n")

        i = 0
        current_cue_number = None
        max_iterations = len(lines) * 2  # Safety limit to prevent infinite loops
        iterations = 0
        increment_i = True  # Track whether we should increment i at the end of loop
        in_detailed_section = False  # Track if we're in a section with actual channel data

        while i < len(lines) and iterations < max_iterations:
            line = lines[i].strip()
            increment_i = True  # Reset for each iteration

            # Check if this is a "Channels" line (indicates channel data follows)
            if line == "Channels":
                in_detailed_section = True  # We've found actual channel data
                i += 1
                
                channel_numbers_line1 = []
                channel_numbers_line2 = []
                values_line1 = []
                values_line2 = []

                # Read the next two lines - first line contains channel numbers, second contains values
                # Skip any separator lines that might appear before actual channel data
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines) and lines[i].strip():
                    # First line after "Channels" contains channel numbers
                    channel_numbers_line1 = lines[i].strip().split()
                    i += 1

                # Skip any separator lines that might appear before second channel data line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines) and lines[i].strip():
                    # Second line contains values for those channels
                    values_line1 = lines[i].strip().split()
                    i += 1

                # Read potential third and fourth lines (for cues with many channels)
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines) and lines[i].strip():
                    next_line = lines[i].strip()
                    # Only read more channel numbers if this doesn't look like a section header
                    if (not next_line.startswith("Cue") and 
                        not next_line == "Channels" and
                        not next_line.startswith("*")):
                        channel_numbers_line2 = lines[i].strip().split()
                        i += 1

                # Skip any separator lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines) and lines[i].strip():
                    next_line = lines[i].strip()
                    # Only read more channel values if this doesn't look like a section header
                    if (not next_line.startswith("Cue") and 
                        not next_line == "Channels" and
                        not next_line.startswith("*")):
                        values_line2 = lines[i].strip().split()
                        i += 1

                # Combine channel numbers and values
                all_channel_numbers = channel_numbers_line1 + channel_numbers_line2
                all_values = values_line1 + values_line2

                # Filter out any non-numeric values (like separator lines)
                filtered_channels = [ch for ch in all_channel_numbers if ch and not re.match(r'^-+$', ch)]
                filtered_values = [val for val in all_values if val and not re.match(r'^-+$', val)]

                # Create channel-value pairs, converting values to QLC+ format
                channel_value_pairs = {}
                for idx, channel_num_str in enumerate(filtered_channels):
                    try:
                        channel_num = int(channel_num_str)
                        value_str = filtered_values[idx] if idx < len(filtered_values) else "0"
                        
                        # Convert Picolo level to QLC+ format
                        try:
                            qlc_value = convert_level(value_str)
                            channel_value_pairs[channel_num] = str(qlc_value)
                        except ValueError:
                            # Keep original value if conversion fails
                            channel_value_pairs[channel_num] = value_str
                    except ValueError:
                        # Skip invalid channel numbers
                        continue

                if current_cue_number is not None and channel_value_pairs:
                    # Use the same cue number format (string) for consistency with cue_list
                    # Convert to string without decimal point for integer cues
                    cue_key = str(current_cue_number).rstrip('.0')
                    
                    # Store as a list of values in order, but we'll need to reconstruct pairs later
                    # For now, keep the flat structure for backward compatibility
                    channel_data[cue_key] = [channel_value_pairs[ch] for ch in sorted(channel_value_pairs.keys())]
                    self._channel_value_pairs[cue_key] = channel_value_pairs
                
                # We've manually incremented i inside this block, so don't increment again
                increment_i = False
            elif line.startswith("Cue") and "TI" in line and "TO" in line:
                pass
            elif re.match(r"^\s*[0-9]+(\.[0-9]+)?\s+" + r"[0-9]+", line):
                # This line has a number followed by space and another digit.
                # It could be either:
                # 1. A cue header: "1      3    3    Manua..." (starts at beginning of line)
                # 2. Channel data: " 1    3    5    71" (has leading spaces)
                
                if re.match(r"^[0-9]+(\.[0-9]+)?\s+" + r"[0-9]+", line):
                    # This is a cue header line (starts at beginning of line, not indented)
                    match = re.search(r"^\s*([0-9]+(\.[0-9]+)?)", line)
                    if match:
                        try:
                            val = float(match.group(1))
                            # Additional check: cue numbers should be reasonable (< 1000)
                            # and the next tokens should look like time values (small integers)
                            parts = line.strip().split()
                            if len(parts) >= 3:
                                # Check if the first three tokens after cue number look like a cue line
                                # Cue number, TI, TO should all be numeric
                                try:
                                    cue_num = float(parts[0])
                                    ti = float(parts[1])
                                    to_val = float(parts[2])
                                    # If this looks like a cue line (cue num < 100, times are reasonable),
                                    # treat it as a cue number
                                    if cue_num < 100 and ti < 100 and to_val < 100:
                                        current_cue_number = val
                                        # Store this cue in our data structure with consistent key format
                                        cue_key = str(current_cue_number).rstrip('.0')
                                        if cue_key not in channel_data:
                                            channel_data[cue_key] = []
                                    else:
                                        # This is likely channel data, not a cue line
                                        current_cue_number = None
                                except ValueError:
                                    current_cue_number = None
                            else:
                                current_cue_number = None
                        except ValueError:
                            # Skip lines that can't be converted to float (e.g., separator lines)
                            current_cue_number = None
                else:
                    # This line starts with a number but has leading spaces - it's channel data, not a cue header
                    # Don't change current_cue_number - keep the existing cue context
                    pass
            # Increment i if we haven't already done so in this iteration
            if increment_i:
                i += 1
            iterations += 1

        # Assign the result to self.channel_data as expected by tests
        self.channel_data = channel_data
        return channel_data

    def parse_channel_mapping(self) -> Dict[int, int]:
        """Parse the Channel Dmx mapping section.

        Returns:
            A dictionary mapping Picolo channel numbers to DMX addresses.
        """
        channel_map: Dict[int, int] = {}
        lines = self.content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this is the "Channel Dmx" header line
            if line == "Channel Dmx   Li Cu":
                i += 1
                
                # Read mapping lines until we hit an empty line or another section
                while i < len(lines):
                    mapping_line = lines[i].strip()
                    
                    # Stop at empty lines or section headers
                    if not mapping_line:
                        break
                    
                    # Check for section headers that might appear after the mapping
                    if (mapping_line.startswith("Cue") or 
                        mapping_line == "Channels" or
                        mapping_line.startswith("*")):
                        break
                    
                    # Parse mapping line: "1       1     FF 1"
                    parts = mapping_line.split()
                    if len(parts) >= 2:
                        try:
                            picolo_channel = int(parts[0])
                            dmx_address = int(parts[1])
                            channel_map[picolo_channel] = dmx_address
                        except ValueError:
                            # Skip lines that can't be parsed as integers
                            pass
                    i += 1
            else:
                i += 1
        
        return channel_map

    def parse(self) -> Dict[str, object]:
        """Parse the entire Picolo file and return structured data.

        Returns:
            A dictionary containing parsed cue list, channel data,
            and maximum channel number.

        Raises:
            InvalidFileFormatError: If any section cannot be parsed.
        """
        self.cue_list = self.parse_cue_list()
        self.channel_mapping = self.parse_channel_mapping()
        # Don't initialize _channel_value_pairs here - let parse_channel_data set it
        self.channel_data = self.parse_channel_data()
        self.max_channel_number = self.find_max_channel_number()

        return {
            "cue_list": self.cue_list,
            "channel_data": self.channel_data,
            "max_channel_number": self.max_channel_number,
            "_channel_value_pairs": self._channel_value_pairs,
        }

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
