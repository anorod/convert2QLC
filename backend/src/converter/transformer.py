"""
Transformer module for converting Picolo data to QLC+ format.

This module provides functionality to convert channel levels from Picolo's
hexadecimal/percentage format to QLC+'s decimal format (0-255).
This module also includes functions for converting time values (TI, TO, TW)
from Picolo to QLC+ FadeIn, FadeOut and Hold attributes.
"""

import re


def convert_level(picolo_level: str) -> int:
    """Convert a Picolo level string to QLC+ decimal value.

    Args:
        picolo_level: A string representing the level in Picolo format.
                      Can be "FF" or a numeric string from "0" to "99".

    Returns:
        An integer between 0 and 255 representing the QLC+ level.

    Raises:
        ValueError: If the input is not a valid Picolo level format.

    Examples:
        >>> convert_level("FF")
        255
        >>> convert_level("99")
        253
        >>> convert_level("50")
        127
        >>> convert_level("0")
        0
    """
    # Handle the special case for "FF" (100%)
    if picolo_level.upper() == "FF":
        return 255

    try:
        # Convert numeric string to integer
        percentage = int(picolo_level)

        # Validate range
        if percentage < 0 or percentage > 99:
            raise ValueError(
                f"Invalid level value: {percentage}. Must be between 0 and 99"
            )

        # Convert percentage to 0-255 range
        qlc_value = round((percentage / 100.0) * 255)
        return int(qlc_value)

    except ValueError as e:
        raise ValueError(
            f"Invalid Picolo level format: '{picolo_level}'. "
            "Expected 'FF' or numeric string 0-99"
        ) from e


def convert_time_value(picolo_time: str, for_hold: bool = False) -> int:
    """Convert a Picolo time value to QLC+ milliseconds.
    
    Args:
        picolo_time: A string representing the time in Picolo format (seconds).
                     Can be "Manua", "ManuaX" (alphanumeric), or numeric string.
        for_hold: If True, apply Hold-specific logic (Manua -> 4294967294, ManuaX -> extract digits)
    
    Returns:
        An integer representing milliseconds.
        - For FadeIn/FadeOut: "Manua" returns 0, numeric strings return seconds * 1000
        - For Hold: "Manua" returns 4294967294, "ManuaX" extracts X and returns X * 1000
    
    Examples:
        >>> convert_time_value("3")
        3000
        >>> convert_time_value("Manua")
        0
        >>> convert_time_value("Manua", for_hold=True)
        4294967294
        >>> convert_time_value("Manua4", for_hold=True)
        4000
    """
    # Handle Hold-specific logic
    if for_hold:
        # Case 1: Pure "Manua" -> special large value
        if picolo_time == "Manua":
            return 4294967294
        
        # Case 2: Alphanumeric like "Manua4", "Manua10" -> extract numeric part
        match = re.search(r'\d+', picolo_time)
        if match:
            seconds = int(match.group())
            return seconds * 1000
    
    # Standard logic for FadeIn/FadeOut or non-Hold cases
    if picolo_time == "Manua":
        return 0
    
    try:
        # Convert seconds to milliseconds
        seconds = int(picolo_time)
        if seconds < 0:
            raise ValueError(
                f"Invalid Picolo time format: '{picolo_time}'. "
                "Expected 'Manua' or positive numeric string representing seconds"
            )
        return seconds * 1000
    except ValueError:
        raise ValueError(
            f"Invalid Picolo time format: '{picolo_time}'. "
            "Expected 'Manua', alphanumeric (e.g., 'Manua4'), or numeric string representing seconds"
        ) from None


def convert_cue_times(cue_list: list, channel_data: dict) -> list:
    """Convert cue times (TI, TO, TW) to QLC+ FadeIn, FadeOut and Hold attributes.
    
    Args:
        cue_list: List of cue dictionaries containing time information
        channel_data: Dictionary mapping cue numbers to channel data
    
    Returns:
        List of cues with converted time attributes for QLC+
    """
    # Create a copy of the cue list to avoid modifying original data
    result_cues = []
    
    # Process each cue in order
    for i, cue in enumerate(cue_list):
        new_cue = cue.copy()
        
        # Get TI (FadeIn) from cue - it's stored as "TI" key in the cue dict
        # For simplicity, we'll assume that the cues have TI, TO, TW values
        # which are stored as part of the cue data structure
        ti_value = cue.get("TI", "0")  # Default to 0 if not found
        to_value = cue.get("TO", "0")  # Default to 0 if not found
        tw_value = cue.get("TW", "0")  # Default to 0 if not found
        
        # Convert TI (FadeIn) from seconds to milliseconds
        try:
            fade_in = convert_time_value(ti_value)
        except ValueError:
            fade_in = 0
        
        # Calculate FadeOut based on next step's FadeIn value (crossfade logic)
        fade_out = 0  # Default value
        if i < len(cue_list) - 1:  # If not the last cue
            # Get the next cue and its TI value (FadeIn of next step)
            next_cue = cue_list[i + 1]
            next_ti_value = next_cue.get("TI", "0")
            try:
                fade_out = convert_time_value(next_ti_value)
            except ValueError:
                fade_out = 0
        else:
            # For the last step, use TO for FadeOut calculation
            # If TO is missing or invalid, fall back to TI (per user confirmation)
            if to_value and to_value != "0":
                try:
                    fade_out = convert_time_value(to_value)
                except ValueError:
                    # TO invalid, fallback to TI
                    try:
                        fade_out = convert_time_value(ti_value)
                    except ValueError:
                        fade_out = 0
            else:
                # TO missing or "0", use TI as fallback
                try:
                    fade_out = convert_time_value(ti_value)
                except ValueError:
                    fade_out = 0
        
        # Hold time is TW value - converted to milliseconds with special handling
        try:
            hold = convert_time_value(tw_value, for_hold=True)
        except ValueError:
            hold = 0

        # Add the converted time attributes to the cue
        new_cue["FadeIn"] = fade_in
        new_cue["FadeOut"] = fade_out
        new_cue["Hold"] = hold

        result_cues.append(new_cue)
    
    return result_cues
