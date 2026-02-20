"""
Test for the new API endpoint functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test that we can import our main application
try:
    from main import app
    print("API application imported successfully")
except Exception as e:
    print(f"Error importing API: {e}")

# Test the conversion functionality directly
from converter.parser import PicoloParser
from converter.transformer import convert_cue_times
from converter.xml_generator import XMLGenerator

# Test with sample data from existing tests
sample_picolo_content = """
Cue    TI   TO   TW   Ti   To   Tm Jump   Lp Text                 Command         TC  cfs
0.1    3    3    Manua          T1           CUE                                         -
Channels
 13   14   61   66   70   71   197
 75   75   40   75   40   47   FF
"""

try:
    parser = PicoloParser(sample_picolo_content)
    parsed_data = parser.parse()
    
    print("Parser test successful")
    print(f"Cue count: {len(parsed_data['cue_list'])}")
    print(f"Channel data keys: {list(parsed_data['channel_data'].keys())}")
    
    # Test time conversion
    converted_cue_list = convert_cue_times(parsed_data["cue_list"], parsed_data["channel_data"])
    print("Time conversion test successful")
    
    # Test XML generation
    xml_generator = XMLGenerator()
    xml_content = xml_generator.generate_xml(
        "test_file.txt",
        converted_cue_list,
        parsed_data["channel_data"],
        parsed_data["max_channel_number"]
    )
    
    print("XML generation test successful")
    print(f"Generated XML length: {len(xml_content)} characters")
    
except Exception as e:
    print(f"Error in conversion tests: {e}")