#!/usr/bin/env python
"""
Verification script to test the cue extraction functionality.
This script verifies that we can extract lines 315-338 from the test file.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))
from converter.xml_generator import XMLGenerator

def main():
    # Read the test file
    test_file_path = Path("docs/test_files/Ejemplo-Fichero-Picolo.txt")
    with open(test_file_path, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # Create generator instance
    generator = XMLGenerator()
    
    # Extract cue details section
    result = generator.extract_cue_details_section(content)
    
    print("Extracted Cue Details Section:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    print(f"\nTotal lines extracted: {len(result.split(chr(10)))}")
    
    # Verify key content is present
    checks = [
        ("Cue header", "Cue    TI   TO   TW" in result),
        ("First cue description", "INICIO SECUENCIA" in result),
        ("Second cue description", "PASADA" in result),
        ("Third cue description", "AVISOS" in result),
        ("Fourth cue description", "INICIO TAMBORES" in result),
        ("Fifth cue description", "ENTRA PABLO BUTACAS" in result),
        ("Sixth cue description", "SUBE A ESCENARIO CON" in result),
        ("Channels Patch not included", "Channels Patch" not in result),
    ]
    
    print("\nVerification Checks:")
    all_passed = True
    for check_name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nAll verification checks passed!")
        return 0
    else:
        print("\nSome verification checks failed!")
        return 1

if __name__ == "__main__":
    exit(main())