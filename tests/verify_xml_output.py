import xml.etree.ElementTree as ET
from backend.src.converter.xml_generator import XMLGenerator

def verify_padding():
    generator = XMLGenerator()
    
    test_cases = [
        {"cue_number": "1", "text": "First"},
        {"cue_number": "9", "text": "Ninth"},
        {"cue_number": "10", "text": "Tenth"},
        {"cue_number": "4.5", "text": "Decimal"},
        {"cue_number": "abc", "text": "Invalid"},
    ]
    
    channel_map = {case["cue_number"]: {"1": "255"} for case in test_cases}
    
    print(f"{'Input Cue':<10} | {'Actual Name Attr':<15} | {'Attributes Check'}")
    print("-" * 60)
    
    for i, case in enumerate(test_cases):
        cue_num = case["cue_number"]
        text = case["text"]
        channels = channel_map.get(cue_num, {})
        
        scene = generator.generate_scene(
            cue_number=cue_num,
            channel_data=channels,
            fade_in=0,
            fade_out=0,
            hold=0,
            is_scene_type=True,
            function_id=str(i),
            cue_info=case
        )
        
        actual_name = scene.get("Name", "N/A")
        func_id = scene.get("ID", "N/A")
        func_type = scene.get("Type", "N/A")
        
        attr_check = f"ID={func_id}, Type={func_type}"
        print(f"{cue_num:<10} | {actual_name:<15} | {attr_check}")

if __name__ == "__main__":
    try:
        verify_padding()
    except Exception as e:
        print(f"Verification failed with error: {e}")


