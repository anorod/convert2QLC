"""
Unit tests for the Picolo parser module.

Tests cover parsing of Cue List, channel data extraction,
and maximum channel number identification.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from src.converter.parser import PicoloParser, InvalidFileFormatError

# Sample Picolo file content for testing
SAMPLE_PICOLO_FILE = """
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
0.1    3    3    Manua          T1           CUE                                         -
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
0.2    5    5    Manua          T1           CUE 0.1                                  c  -
Channels
 13   14   61   66   70   71   197
 75   75   40   75   40   47   FF
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
0.3    10   10   Manua          T1           CUE 0.3                                     -
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
1      15   15   Manua4         T1           CUE 1                                    c  -
Channels
 70
 41
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
2      8    8    Manua          T1           CUE 2                                    c  -
Channels
 61   70
 FF   44
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
2.5    6    12   0.1            T1           CUE 2.5                                  c  -
Channels
 2    5    11   21   41   42   61
 52   79   50   65   70   70   78
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
3      8    8    Manua          T1           CUE 3                                    c  -
Channels
 2    5    11   21   28   41   42
 19   64   50   65   07   70   70
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
4      8    12   Manua          T1           CUE 4                                    c  -
Channels
 2    5    11   21   37   41   42   53   54   90
 18   58   50   65   30   70   70   37   37   51
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
5      20   20   Manua          T1           CUE 5                                    c  -
Channels
 11   13   14   15   16   17   41   42   53   54   66
 87   50   50   FF   FF   FF   44   44   FF   FF   50
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
6      10   12   Manua          T1           CUE 6                                    c  -
Channels
 11   13   14   15   16   17   20   42   43   47   50   53   54   66
 75   50   50   FF   FF   FF   FF   45   50   70   80   FF   83   50
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
7      6    10   Manua          T1           CUE 7                                    c  -
Channels
 5    13   14   57   66
 80   80   50   70   50
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
8      8    10   Manua          T1           CUE 8                     c  -
Channels
 13   14   23   26   41   43   44   57   66   72
 65   35   FF   FF   90   90   91   70   35   FF
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
9      6    6    Manua          T1           CUE 9                                    c  -
Channels
 13   14   23   26   41   43   48   50   52   57   66   72
 65   37   FF   FF   90   90   93   FF   FF   70   37   FF
"""


def test_parse_cue_list():
    """Test parsing of the Cue List section."""
    parser = PicoloParser(SAMPLE_PICOLO_FILE)
    result = parser.parse_cue_list()
    # Should return a list with cue information
    assert isinstance(result, list)
    assert len(result) > 0
    # Check that we have the expected cues from the sample file
    assert any(cue["cue_number"] == "0.1" for cue in result)
    assert any(cue["cue_number"] == "0.2" for cue in result)


def test_parse_channel_data():
    """Test parsing of channel data."""
    parser = PicoloParser(SAMPLE_PICOLO_FILE)
    result = parser.parse_channel_data()
    # Should return a dict mapping cue numbers to channel lists
    assert isinstance(result, dict)
    assert len(result) > 0
    # Check that we have channels for some cues
    assert 1 in result or 2 in result


def test_find_max_channel_number():
    """Test finding the maximum channel number."""
    parser = PicoloParser(SAMPLE_PICOLO_FILE)
    # First parse the channel data
    parser.parse_channel_data()
    result = parser.find_max_channel_number()
    # Should return a positive integer (max channel from sample file)
    assert isinstance(result, int)
    assert result > 0


def test_parse_invalid_file():
    """Test parsing of invalid file format."""
    invalid_content = "This is not a valid Picolo file"
    parser = PicoloParser(invalid_content)

    with pytest.raises(InvalidFileFormatError):
        parser.parse_cue_list()
