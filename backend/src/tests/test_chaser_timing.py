"""
Comprehensive unit tests for chaser timing logic.

Tests cover all edge cases for Picolo to QLC+ time conversion:
- FadeIn calculation (TI * 1000)
- Crossfade logic (FadeOut of step N = FadeIn of step N+1)
- Last step TO fallback (use TI when TO is missing/invalid)
- Hold special cases (Manua, ManuaX patterns)

References: project-specs.md sections 4.2.2
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converter.transformer import convert_time_value, convert_cue_times
import pytest


class TestConvertTimeValueBasic:
    """Test basic time value conversions."""
    
    def test_numeric_seconds_to_milliseconds(self):
        """Test that numeric seconds are converted to milliseconds correctly."""
        assert convert_time_value("3") == 3000
        assert convert_time_value("5") == 5000
        assert convert_time_value("10") == 10000
        assert convert_time_value("0") == 0
    
    def test_manua_returns_zero_for_fade(self):
        """Test that 'Manua' returns 0 for FadeIn/FadeOut calculations."""
        assert convert_time_value("Manua") == 0


class TestConvertTimeValueHold:
    """Test Hold-specific time value conversions."""
    
    def test_manua_hold_special_value(self):
        """Test Case A: TW='Manua' -> Hold=4294967294 (special QLC+ manual hold value)."""
        assert convert_time_value("Manua", for_hold=True) == 4294967294
    
    def test_manua_with_number_extract_digits(self):
        """Test Case C: TW='Manua4' -> Hold=4000 (extract numeric part and convert)."""
        assert convert_time_value("Manua4", for_hold=True) == 4000
        assert convert_time_value("Manua10", for_hold=True) == 10000
        assert convert_time_value("Manua99", for_hold=True) == 99000
    
    def test_numeric_hold_normal_conversion(self):
        """Test that numeric TW values are converted normally."""
        assert convert_time_value("5", for_hold=True) == 5000
        assert convert_time_value("3", for_hold=True) == 3000


class TestCrossfadeLogic:
    """Test crossfade logic where FadeOut(Step N) = FadeIn(Step N+1)."""
    
    def test_crossfade_basic(self):
        """Test Case B: Crossfade - Step 1 (TI=3) + Step 2 (TI=5) -> Step 1 FadeOut=5000."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "5", "TO": "5", "TW": "2"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Step 1: FadeIn from TI=3, FadeOut from next step's TI=5
        assert result[0]["FadeIn"] == 3000
        assert result[0]["FadeOut"] == 5000  # Crossfade: next step's TI
        
        # Step 2: FadeIn from TI=5, FadeOut from TO=5 (last step)
        assert result[1]["FadeIn"] == 5000
        assert result[1]["FadeOut"] == 5000  # Last step uses its own TO
    
    def test_crossfade_multiple_steps(self):
        """Test crossfade across multiple chaser steps."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "2", "TO": "2", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "4", "TO": "4", "TW": "Manua"},
            {"cue_number": "0.3", "TI": "6", "TO": "6", "TW": "Manua"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Step 1: FadeIn=2000, FadeOut=4000 (from step 2's TI)
        assert result[0]["FadeIn"] == 2000
        assert result[0]["FadeOut"] == 4000
        
        # Step 2: FadeIn=4000, FadeOut=6000 (from step 3's TI)
        assert result[1]["FadeIn"] == 4000
        assert result[1]["FadeOut"] == 6000
        
        # Step 3 (last): FadeIn=6000, FadeOut=6000 (uses its own TO)
        assert result[2]["FadeIn"] == 6000
        assert result[2]["FadeOut"] == 6000


class TestLastStepTOFallback:
    """Test last step TO fallback logic (use TI when TO is missing/invalid)."""
    
    def test_last_step_no_to_uses_ti(self):
        """Test that last step with no TO uses TI for FadeOut."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "5", "TW": "2"}  # No TO field
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Last step has no TO, should fallback to TI=5 -> FadeOut=5000
        assert result[1]["FadeIn"] == 5000
        assert result[1]["FadeOut"] == 5000  # Fallback to TI
    
    def test_last_step_to_zero_uses_ti(self):
        """Test that last step with TO='0' uses TI for FadeOut."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "5", "TO": "0", "TW": "2"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Last step has TO='0', should fallback to TI=5 -> FadeOut=5000
        assert result[1]["FadeIn"] == 5000
        assert result[1]["FadeOut"] == 5000  # Fallback to TI
    
    def test_last_step_invalid_to_uses_ti(self):
        """Test that last step with invalid TO uses TI for FadeOut."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "5", "TO": "invalid", "TW": "2"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Last step has invalid TO, should fallback to TI=5 -> FadeOut=5000
        assert result[1]["FadeIn"] == 5000
        assert result[1]["FadeOut"] == 5000  # Fallback to TI


class TestCompleteChaserScenario:
    """Test complete chaser scenario with all timing aspects."""
    
    def test_full_chaser_timing(self):
        """Test Case A complete: TI=3, TO=3, TW=Manua -> FI=3000, FO=3000, Hold=4294967294."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Single step chaser: FadeIn from TI, FadeOut from TO (or TI if TO missing), Hold from TW
        assert result[0]["FadeIn"] == 3000
        assert result[0]["FadeOut"] == 3000  # Uses TO=3
        assert result[0]["Hold"] == 4294967294  # TW="Manua" -> special value
    
    def test_mixed_timing_values(self):
        """Test chaser with mixed timing values including ManuaX patterns."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "3", "TO": "3", "TW": "Manua"},
            {"cue_number": "0.2", "TI": "5", "TO": "5", "TW": "Manua4"},
            {"cue_number": "0.3", "TI": "10", "TO": "", "TW": "8"}  # Empty TO, should use TI
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Step 1
        assert result[0]["FadeIn"] == 3000
        assert result[0]["FadeOut"] == 5000  # Crossfade to step 2
        assert result[0]["Hold"] == 4294967294  # Manua
        
        # Step 2
        assert result[1]["FadeIn"] == 5000
        assert result[1]["FadeOut"] == 10000  # Crossfade to step 3
        assert result[1]["Hold"] == 4000  # Manua4 -> extract 4
        
        # Step 3 (last, empty TO)
        assert result[2]["FadeIn"] == 10000
        assert result[2]["FadeOut"] == 10000  # Fallback to TI since TO is empty
        assert result[2]["Hold"] == 8000  # TW=8 seconds


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_cue_list(self):
        """Test that empty cue list returns empty result."""
        result = convert_cue_times([], {})
        assert result == []
    
    def test_single_cue_no_to(self):
        """Test single cue with no TO field."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "5", "TW": "Manua"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # Single cue with no TO should use TI for both FadeIn and FadeOut
        assert result[0]["FadeIn"] == 5000
        assert result[0]["FadeOut"] == 5000  # Fallback to TI
        assert result[0]["Hold"] == 4294967294
    
    def test_manua_ti_value(self):
        """Test cue with Manua as TI value."""
        sample_cues = [
            {"cue_number": "0.1", "TI": "Manua", "TO": "3", "TW": "5"},
            {"cue_number": "0.2", "TI": "2", "TO": "2", "TW": "Manua"}
        ]
        sample_channel_data = {1: ["FF"]}
        
        result = convert_cue_times(sample_cues, sample_channel_data)
        
        # First cue with Manua TI -> FadeIn=0
        assert result[0]["FadeIn"] == 0
        assert result[0]["FadeOut"] == 2000  # Crossfade to step 2's TI
        assert result[0]["Hold"] == 5000
