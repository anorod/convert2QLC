
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pathlib import Path
from src.converter.parser import PicoloParser
from src.converter.transformer import convert_cue_times
from src.converter.xml_generator import XMLGenerator

# In a real scenario, these would be in a dedicated directory like docs/test_snapshots/
# For this task, we will assume they are present or can be derived.
# Since I cannot create new files in 'docs/', I will define them here for the purpose of the regression test logic.

SNAPSHOTS = {
    "20260220-TestSimplePicolo.txt": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Workspace>
<Workspace xmlns="http://www.qlcplus.org/Workspace" CurrentWindow="FunctionManager">
  <Creator>
    <Name>Q Light Controller Plus</Name>
    <Version>4.12.0</Version>
    <Author>anorod</Author>
  </Creator>
  <Engine>
    <InputOutputMap>
      <BeatGenerator BeatType="Disabled" BPM="0"/>
      <Universe Name="Universe 1" ID="0"/>
      <Universe Name="Universe 2" ID="1"/>
      <Universe Name="Universe 3" ID="2"/>
      <Universe Name="Universe 4" ID="3"/>
    </InputOutputMap>
    <Fixture>
      <Manufacturer>Generic</Manufacturer>
      <Model>Generic</Model>
      <Mode>255 Channel</Mode>
      <ID>0</ID>
      <Name>Dimmers</Name>
      <Universe>0</Universe>
      <Address>0</Address>
      <Channels>255</Channels>
    </Fixture>
    <Function ID="0" Type="Scene" Name="01. Cue inicial">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
      <FixtureVal ID="0">2,76,4,255,10,255,70,153</FixtureVal>
    </Function>
    <Function ID="1" Type="Scene" Name="02. Cue 2 segunda auto">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
      <FixtureVal ID="0">0,255,2,76,4,255,70,153</FixtureVal>
    </Function>
    <Function ID="2" Type="Scene" Name="03. Cue">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
    </Function>
    <Function ID="3" Type="Scene" Name="04. Cue 1 canal">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
      <FixtureVal ID="0">4,128</FixtureVal>
    </Function>
    <Function ID="4" Type="Scene" Name="04.5. Un decimal en la Cue">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
      <FixtureVal ID="0">1,255,4,128</FixtureVal>
    </Function>
    <Function ID="5" Type="Scene" Name="05. Otra Cue">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
    </Function>
    <Function ID="6" Type="Chaser" Name="Cuelist">
      <Speed FadeIn="0" FadeOut="0" Duration="0"/>
      <Direction>Forward</Direction>
      <RunOrder>Loop</RunOrder>
      <SpeedModes FadeIn="PerStep" FadeOut="PerStep" Duration="PerStep"/>
      <Step Number="0" FadeIn="3000" Hold="4294967294" FadeOut="3000">0</Step>
      <Step Number="1" FadeIn="3000" Hold="5000" FadeOut="3000">1</Step>
      <Step Number="2" FadeIn="3000" Hold="4294967294" FadeOut="5000">2</Step>
      <Step Number="3" FadeIn="1000" Hold="4294967294" FadeOut="3000">3</Step>
      <Step Number="4" FadeIn="3000" Hold="4294967294" FadeOut="3000">4</Step>
      <Step Number="5" FadeIn="3000" Hold="4294967294" FadeOut="3000">5</Step>
    </Function>
    <Monitor DisplayMode="0" ShowLabels="0">
      <Font>Arial,12,-1,5,400,0,0,0,0,0,0,0,0,0,0,1</Font>
      <ChannelStyle text="0"/>
      <ValueStyle text="0"/>
      <Grid Width="5" Height="3" Depth="5" Units="0"/>
    </Monitor>
  </Engine>
  <VirtualConsole>
    <Frame Caption="">
      <Appearance FrameStyle="None" ForegroundColor="Default" BackgroundColor="Default" BackgroundImage="None" Font="Default"/>
    </Frame>
    <Properties>
      <Size Width="1920" Height="1080"/>
      <GrandMaster Visible="1" ChannelMode="Intensity" ValueMode="Reduce" SliderMode="Normal"/>
    </Properties>
  </VirtualConsole>
  <SimpleDesk>
    <Engine/>
  </SimpleDesk>
</Workspace>
""",
}

def run_conversion_pipeline(input_content: str, file_name: str) -> str:
    """Helper to run the full pipeline."""
    parser = PicoloParser(input_content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channels = parsed_data["max_channel_number"]
    channel_value_pairs = parsed_data.get("_channel_value_pairs", {})
    
    # Transform times
    transformed_cues = convert_cue_times(cue_list, channel_data)
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        file_name=file_name,
        cue_list=transformed_cues,
        channel_data=channel_data,
        max_channel_number=max_channels,
        channel_value_pairs=channel_value_pairs
    )
    return xml_output

@pytest.mark.parametrize("test_file", (Path(__file__).parent.parent.parent.parent / "docs" / "test_files").glob("*.txt"))
def test_regression_pipeline(test_file: Path):
    """Regression test for the full conversion pipeline."""
    print(f"Testing file: {test_file.name}")
    
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Run pipeline
    actual_xml = run_conversion_pipeline(content, test_file.name)
    
    # Check if we have a snapshot for this file
    if test_file.name not in SNAPSHOTS:
        pytest.skip(f"No snapshot found for {test_file.name}. Please create one.")
    
    expected_xml = SNAPSHOTS[test_file.name]
    
    # Use a simple comparison (ignoring whitespace/formatting differences might be needed in reality)
    # For now, we do a direct string comparison of the cleaned versions.
    def clean_xml(xml_str: str) -> str:
        import xml.dom.minidom as minidom
        return minidom.parseString(xml_str).toxml()

    assert clean_xml(actual_xml) == clean_xml(expected_xml), \
        f"Mismatch in XML for {test_file.name}. Check the output."

if __name__ == "__main__":
    # Run manually if script is executed directly
    pytest([__file__])
