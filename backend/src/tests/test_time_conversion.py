"""
Unit tests for the time conversion functionality in transformer module.

Tests cover conversion of Picolo time values (TI, TO, TW) to QLC+ FadeIn, FadeOut and Hold attributes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converter.transformer import convert_time_value, convert_cue_times
import pytest

def test_convert_time_value():
    """Test conversion of Picolo time values to milliseconds."""
    # Test normal numeric values
    assert convert_time_value("3") == 3000
    assert convert_time_value("5") == 5000
    assert convert_time_value("0") == 0
    
    # Test "Manua" value
    assert convert_time_value("Manua") == 0
    
    # Test invalid values
    with pytest.raises(ValueError):
        convert_time_value("invalid")
    
    with pytest.raises(ValueError):
        convert_time_value("-5")


def test_convert_cue_times():
    """Test conversion of cue times to QLC+ attributes."""
    # Sample cue list with time values
    sample_cues = [
        {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
        {"cue_number": "0.2", "TI": "5", "TO": "5", "TW": "2"},
        {"cue_number": "0.3", "TI": "10", "TO": "10", "TW": "Manua"}
    ]
    
    # Sample channel data (not used in time conversion but needed for function call)
    sample_channel_data = {1: ["FF"], 2: ["99"]}
    
    result = convert_cue_times(sample_cues, sample_channel_data)
    
    # Check the first cue - FadeIn should be 3000ms, FadeOut should be 5000ms (from next cue)
    assert result[0]["FadeIn"] == 3000
    assert result[0]["FadeOut"] == 5000  # From next cue's TI value
    assert result[0]["Hold"] == 4294967294  # TW is "Manua" -> special QLC+ value
    
    # Check the second cue - FadeIn should be 5000ms, FadeOut should be 10000ms (from last cue)
    assert result[1]["FadeIn"] == 5000
    assert result[1]["FadeOut"] == 10000  # From last cue's TI value (since it's the last)
    assert result[1]["Hold"] == 2000  # TW = 2 seconds -> 2000ms
    
    # Check the third cue - FadeIn should be 10000ms, FadeOut should be 10000ms (TO value since it's last)
    assert result[2]["FadeIn"] == 10000
    assert result[2]["FadeOut"] == 10000  # From TO since it's the last cue
    assert result[2]["Hold"] == 4294967294  # TW is "Manua" -> special QLC+ value


def test_convert_cue_times_with_manua_values():
    """Test conversion with various "Manua" values."""
    sample_cues = [
        {"cue_number": "1", "TI": "Manua", "TO": "3", "TW": "5"},
        {"cue_number": "2", "TI": "2", "TO": "Manua", "TW": "Manua"}
    ]
    
    sample_channel_data = {1: ["FF"]}
    
    result = convert_cue_times(sample_cues, sample_channel_data)
    
    # First cue - TI is "Manua" so FadeIn should be 0
    assert result[0]["FadeIn"] == 0
    assert result[0]["FadeOut"] == 2000  # From next cue's TI value
    assert result[0]["Hold"] == 5000  # TW = 5 seconds -> 5000ms
    
    # Second cue - TI is 2, TO is "Manua", so FadeOut should be TO value (which is "Manua" -> 0)
    # Since it's the last cue, we use TO directly for FadeOut calculation
    assert result[1]["FadeIn"] == 2000  # TI = 2 seconds -> 2000ms
    assert result[1]["FadeOut"] == 0  # TO is "Manua" -> 0 (but it's the last cue, so TO value is used)
    assert result[1]["Hold"] == 4294967294  # TW is "Manua" -> special QLC+ value