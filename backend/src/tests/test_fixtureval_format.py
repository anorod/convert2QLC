"""
Tests para verificar el formato correcto de FixtureVal en la generación XML.

Estos tests validan que:
1. El formato de FixtureVal sea fixture_index,valor (no canal:valor)
2. Todas las Scenes con canales tengan elemento FixtureVal
3. Las Cues sin canales no tengan FixtureVal
4. El fixture_index sea channel_number - 1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.converter.parser import PicoloParser
from src.converter.xml_generator import XMLGenerator
from src.converter.transformer import convert_cue_times
import pytest
import re


def get_test_file_content():
    """Load the test file content."""
    test_file = os.path.join(os.path.dirname(__file__), "20260224-TestSimplePicolo2.txt")
    with open(test_file, "r") as f:
        return f.read()


def parse_and_generate_xml(content):
    """Parse content and generate XML."""
    parser = PicoloParser(content)
    parsed_data = parser.parse()
    
    cue_list = parsed_data["cue_list"]
    channel_data = parsed_data["channel_data"]
    max_channel_number = parsed_data["max_channel_number"]
    channel_value_pairs = parsed_data.get("_channel_value_pairs", {})
    
    # Convert cue times
    converted_cues = convert_cue_times(cue_list, {})
    
    # Generate XML
    generator = XMLGenerator()
    xml_output = generator.generate_xml(
        "TestSimplePicolo2",
        converted_cues,
        channel_data,
        max_channel_number,
        channel_value_pairs
    )
    
    return {
        "xml": xml_output,
        "parser": parser,
        "parsed_data": parsed_data,
        "converted_cues": converted_cues
    }


def extract_scenes_from_xml(xml):
    """Extract all Scene functions from XML."""
    scenes = []
    lines = xml.split('\n')
    
    for line in lines:
        if '<Function' in line and 'Type="Scene"' in line:
            match = re.search(r'ID="(\d+)"', line)
            name_match = re.search(r'Name="([^"]+)"', line)
            if match:
                scenes.append({
                    "id": int(match.group(1)),
                    "name": name_match.group(1) if name_match else None
                })
    
    return scenes


def extract_fixtureval_from_xml(xml, scene_id):
    """Extract FixtureVal text for a specific scene ID."""
    # Find the Function element with the given ID and Type="Scene"
    pattern = rf'<Function\s+ID="{scene_id}"[^>]*Type="Scene"[^>]*>(.*?)</Function>'
    match = re.search(pattern, xml, re.DOTALL)
    
    if not match:
        # Try alternative order of attributes
        pattern = rf'<Function\s+Type="Scene"[^>]*ID="{scene_id}"[^>]*>(.*?)</Function>'
        match = re.search(pattern, xml, re.DOTALL)
    
    if not match:
        return None
    
    function_content = match.group(1)
    fixtureval_match = re.search(r'<FixtureVal\s+ID="0">([^<]*)</FixtureVal>', function_content)
    
    if fixtureval_match:
        return fixtureval_match.group(1)
    
    return None


def test_fixtureval_format_for_cue_with_channels():
    """Verifica que el FixtureVal use formato fixture_index,valor (no canal:valor)."""
    content = get_test_file_content()
    result = parse_and_generate_xml(content)
    xml = result["xml"]
    
    # Cue 1 tiene canales: 3, 5, 11, 71 con valores: 48(30 hex), 255(FF), 255(FF), 96(60 hex)
    # El FixtureVal debería ser: 2,48,4,255,10,255,70,96 (fixture_index = channel - 1)
    fixtureval_text = extract_fixtureval_from_xml(xml, "0")
    
    assert fixtureval_text is not None, "FixtureVal no encontrado para Scene ID 0"
    
    # Verificar que NO usa formato canal:valor
    assert ":" not in fixtureval_text, f"FixtureVal usa formato incorrecto 'canal:valor': {fixtureval_text}"
    
    # Verificar que usa formato fixture_index,valor
    values = [int(v) for v in fixtureval_text.split(",")]
    assert len(values) % 2 == 0, f"FixtureVal debe tener pares de valores (index, valor): {fixtureval_text}"
    
    # Verificar los valores específicos para Cue 1
    # Canales: 3->48, 5->255, 11->255, 71->96
    # Fixture indices: 2, 4, 10, 70
    expected_pairs = [(2, 48), (4, 255), (10, 255), (70, 96)]
    actual_pairs = list(zip(values[::2], values[1::2]))
    
    assert actual_pairs == expected_pairs, f"FixtureVal incorrecto. Esperado: {expected_pairs}, Obtenido: {actual_pairs}"


def test_all_scenes_with_channels_have_fixtureval():
    """Verifica que cada Scene que tiene datos de canales incluya elemento FixtureVal."""
    content = get_test_file_content()
    result = parse_and_generate_xml(content)
    xml = result["xml"]
    channel_value_pairs = result["parsed_data"].get("_channel_value_pairs", {})
    
    # Cues con canales: 1, 2, 4, 4.5
    cues_with_channels = [cue for cue in result["converted_cues"] if str(int(float(cue.get("cue_number", 0)))) in channel_value_pairs]
    
    assert len(cues_with_channels) > 0, "No se encontraron Cues con canales"
    
    # Verificar que cada Cue con canales tiene FixtureVal en su Scene
    for i, cue in enumerate(cues_with_channels):
        cue_number = int(float(cue.get("cue_number", 0)))
        fixtureval_text = extract_fixtureval_from_xml(xml, str(i))
        
        assert fixtureval_text is not None, f"Scene ID {i} (Cue {cue_number}) no tiene FixtureVal aunque la Cue tiene canales"


def test_scenes_without_channels_have_no_fixtureval():
    """Verifica que Scenes de Cues vacías (BK) no tengan elemento FixtureVal."""
    content = get_test_file_content()
    result = parse_and_generate_xml(content)
    xml = result["xml"]
    channel_value_pairs = result["parsed_data"].get("_channel_value_pairs", {})
    
    # Cues sin canales: 3 (Cue BK), 5 (Otra Cue BK)
    cues_without_channels = []
    for i, cue in enumerate(result["converted_cues"]):
        cue_number = int(float(cue.get("cue_number", 0)))
        if str(cue_number) not in channel_value_pairs:
            cues_without_channels.append((i, cue_number))
    
    # Verificar que estas Cues no tengan FixtureVal
    for scene_id, cue_number in cues_without_channels:
        fixtureval_text = extract_fixtureval_from_xml(xml, str(scene_id))
        
        assert fixtureval_text is None, f"Scene ID {scene_id} (Cue {cue_number}) no debería tener FixtureVal"


def test_fixture_index_is_channel_minus_one():
    """Verifica que el índice de fixture sea canal menos uno."""
    content = get_test_file_content()
    result = parse_and_generate_xml(content)
    xml = result["xml"]
    
    # Para Cue 2: canales 1, 3, 5, 71 con valores FF(255), 30(48), FF(255), 60(96)
    # FixtureVal debería ser: 0,255,2,48,4,255,70,96
    fixtureval_text = extract_fixtureval_from_xml(xml, "1")
    
    assert fixtureval_text is not None, "FixtureVal no encontrado para Scene ID 1"
    
    values = [int(v) for v in fixtureval_text.split(",")]
    actual_pairs = list(zip(values[::2], values[1::2]))
    
    # Canales: 1->255, 3->48, 5->255, 71->96
    # Fixture indices (channel - 1): 0, 2, 4, 70
    expected_pairs = [(0, 255), (2, 48), (4, 255), (70, 96)]
    
    assert actual_pairs == expected_pairs, f"FixtureVal incorrecto para Cue 2. Esperado: {expected_pairs}, Obtenido: {actual_pairs}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
