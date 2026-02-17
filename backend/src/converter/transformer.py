"""
Transformer module for converting Picolo data to QLC+ format.

This module provides functionality to convert channel levels from Picolo's
hexadecimal/percentage format to QLC+'s decimal format (0-255).
"""


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
