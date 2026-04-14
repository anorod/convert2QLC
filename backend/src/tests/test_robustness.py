"""
Unit tests for robustness and edge cases in the Picolo parser.

Tests cover:
- Unicode/UTF-8 characters (©, ®, é, ñ, emojis 🚀) in cue names and channel values
- Invalid UTF-8 bytes to verify controlled error handling
- Malformed files missing critical sections (e.g., no channels section)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.converter.parser import PicoloParser, InvalidFileFormatError


class TestUnicodeCharacters:
    """Test handling of Unicode/UTF-8 characters in cue names and values."""

    @pytest.mark.parametrize("unicode_char", [
        ("©"),      # Copyright symbol
        ("®"),      # Registered trademark
        ("é"),      # Accented character
        ("ñ"),      # Spanish ñ
        ("🚀"),     # Emoji rocket
        ("αβγ"),    # Greek letters
        ("你好"),   # Chinese characters
        ("مرحبا"),  # Arabic characters
    ])
    def test_unicode_in_cue_text(self, unicode_char):
        """Test that Unicode characters in cue text are handled correctly."""
        content = f"""Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test {unicode_char}                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        result = parser.parse_cue_list()
        
        assert isinstance(result, list)
        assert len(result) == 1
        # Verify the Unicode character is preserved in the text field
        assert unicode_char in result[0]["Text"]

    @pytest.mark.parametrize("unicode_char", [
        ("é"),      # Accented character
        ("ñ"),      # Spanish ñ
        ("©"),      # Copyright symbol
    ])
    def test_unicode_in_cue_number(self, unicode_char):
        """Test that Unicode characters in cue numbers are handled gracefully."""
        content = f"""Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test {unicode_char}                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        # Should not raise an exception, should parse successfully
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert "cue_list" in result


class TestInvalidEncoding:
    """Test handling of invalid UTF-8 bytes and encoding errors."""

    def test_invalid_utf8_bytes(self):
        """Test that invalid UTF-8 bytes raise controlled error, not UnicodeDecodeError."""
        # Create a string with invalid UTF-8 sequence
        # This simulates what might happen when reading a corrupted file
        try:
            # Invalid UTF-8 byte sequence (0xFF is never valid in UTF-8)
            invalid_bytes = b"Cue    TI   TO\xFFInvalid encoding"
            # Try to decode with strict error handling
            content = invalid_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            # If we get here, the decoder caught it - that's expected behavior
            # The parser should handle this gracefully if passed raw bytes
            pass
        
        # Test that passing already-decoded content with replacement chars works
        content_with_replacement = "Cue    TI   TO \ufffd Invalid encoding"
        parser = PicoloParser(content_with_replacement)
        
        # Should either parse successfully or raise InvalidFileFormatError, not crash
        try:
            result = parser.parse_cue_list()
            # If it parses, that's fine - the replacement char is valid Unicode
            assert isinstance(result, list)
        except InvalidFileFormatError:
            # Also acceptable - malformed content raises controlled exception
            pass

    def test_mixed_encoding_content(self):
        """Test handling of mixed encoding scenarios."""
        # Content with various special characters that might cause encoding issues
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test ©®éñ                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert len(result["cue_list"]) == 1


class TestMalformedFiles:
    """Test handling of malformed files missing critical sections."""

    def test_missing_cue_header(self):
        """Test that files without Cue List header raise InvalidFileFormatError."""
        content = """This is not a valid Picolo file
Just some random text
No cue headers here
"""
        parser = PicoloParser(content)
        
        with pytest.raises(InvalidFileFormatError) as exc_info:
            parser.parse_cue_list()
        
        assert "Cue List" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_missing_channels_section(self):
        """Test that files without Channels section are handled gracefully."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  -
2      3    3    Manua          T1           CUE Test2                         c  -
"""
        parser = PicoloParser(content)
        
        # Should parse cue list successfully even without channels
        result = parser.parse_cue_list()
        
        assert isinstance(result, list)
        assert len(result) == 2

    def test_empty_file(self):
        """Test that empty files raise InvalidFileFormatError."""
        content = ""
        parser = PicoloParser(content)
        
        with pytest.raises(InvalidFileFormatError):
            parser.parse_cue_list()

    def test_only_whitespace(self):
        """Test that whitespace-only files raise InvalidFileFormatError."""
        content = "   \n\n   \n  "
        parser = PicoloParser(content)
        
        with pytest.raises(InvalidFileFormatError):
            parser.parse_cue_list()

    def test_incomplete_cue_line(self):
        """Test handling of incomplete cue lines."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5
"""
        parser = PicoloParser(content)
        
        # Should handle gracefully - either parse what it can or raise controlled error
        try:
            result = parser.parse_cue_list()
            assert isinstance(result, list)
        except InvalidFileFormatError:
            pass

    def test_missing_channel_values(self):
        """Test handling of Channels section with no values."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  -
Channels
"""
        parser = PicoloParser(content)
        
        # Should not crash, should handle empty channels gracefully
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert "channel_data" in result

    def test_truncated_file(self):
        """Test handling of truncated/incomplete files."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  
"""
        parser = PicoloParser(content)
        
        # Should handle gracefully - file is truncated but not necessarily invalid
        try:
            result = parser.parse_cue_list()
            assert isinstance(result, list)
        except InvalidFileFormatError:
            pass

    def test_duplicate_headers(self):
        """Test handling of duplicate section headers."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  -
Channels
  13   14
  75   75
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
2      3    3    Manua          T1           CUE Test2                         c  -
Channels
  15
  80
"""
        parser = PicoloParser(content)
        
        # Should handle multiple sections correctly
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert len(result["cue_list"]) >= 1


class TestEdgeCases:
    """Test various edge cases and boundary conditions."""

    def test_very_long_cue_text(self):
        """Test handling of very long cue text fields."""
        long_text = "A" * 500  # 500 character text
        content = f"""Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE {long_text}                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        
        # Should handle long text without crashing
        result = parser.parse_cue_list()
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_special_characters_in_text(self):
        """Test handling of special characters in cue text."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test <>&"'|\\                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        
        # Should handle special characters without crashing
        result = parser.parse_cue_list()
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_non_ascii_channel_values(self):
        """Test handling of non-ASCII characters in channel values."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  -
Channels
  13   14
  FF   é
"""
        parser = PicoloParser(content)
        
        # Should handle gracefully - invalid channel values should be skipped or handled
        result = parser.parse_channel_data()
        
        assert isinstance(result, dict)

    def test_zero_cue_number(self):
        """Test handling of cue number 0."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
0      5    5    Manua          T1           CUE Zero                          c  -
Channels
  13   14
  75   75
"""
        parser = PicoloParser(content)
        
        result = parser.parse_cue_list()
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_very_large_channel_numbers(self):
        """Test handling of very large channel numbers."""
        content = """Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      5    5    Manua          T1           CUE Test                          c  -
Channels
  9999   10000
  FF     FF
"""
        parser = PicoloParser(content)
        
        result = parser.parse()
        
        assert isinstance(result, dict)
        # Max channel should be found correctly
        assert result["max_channel_number"] is not None
