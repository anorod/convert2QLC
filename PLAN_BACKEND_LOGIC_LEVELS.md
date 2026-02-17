# Plan de Implementación: Lógica de Conversión de Niveles (Issue #04)

## Objetivo
Implementar la lógica de conversión de niveles de canal desde el formato Picolo al formato QLC+.

## Requisitos (de docs/issues/04-backend-logic-levels.md)
- Crear una función que convierta niveles Picolo (string) a niveles QLC+ (integer)
- Convertir "FF" a 255
- Convertir strings numéricos (ej. "50") a su valor correspondiente en rango 0-255
- Manejar correctamente el caso "0"
- Escribir tests unitarios para todos los casos de conversión

## Requisitos Adicionales (de docs/project-specs-es.md)
- Fórmula de conversión: valor_qlc = round((porcentaje / 100.0) * 255)
- Para "FF": valor_qlc = 255

## Pasos a Seguir

### 1. Crear rama de trabajo
```bash
cd C:\Users\anorod\source\repos\convert2QLC
git checkout -b feature/04-backend-logic-levels
```

### 2. Implementar función de conversión
**Ubicación:** `backend/src/converter/transformer.py` (crear archivo)

**Contenido:**
```python
"""
Transformer module for converting Picolo data to QLC+ format.

This module provides functionality to convert channel levels from Picolo's
hexadecimal/percentage format to QLC+'s decimal format (0-255).
"""

from typing import Union


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
            raise ValueError(f"Invalid level value: {percentage}. Must be between 0 and 99")
        
        # Convert percentage to 0-255 range
        qlc_value = round((percentage / 100.0) * 255)
        return int(qlc_value)
    
    except ValueError as e:
        raise ValueError(f"Invalid Picolo level format: '{picolo_level}'. Expected 'FF' or numeric string 0-99") from e
```

### 3. Crear tests unitarios
**Ubicación:** `backend/src/tests/test_transformer.py` (crear archivo)

**Contenido:**
```python
"""
Unit tests for the transformer module.

Tests cover level conversion from Picolo format to QLC+ format.
"""

import sys
sys.path.insert(0, "../../..")

from src.converter.transformer import convert_level
import pytest


# Test cases: (input, expected_output)
TEST_CASES = [
    ("FF", 255),
    ("ff", 255),  # Test case insensitivity
    ("99", 253),
    ("50", 127),
    ("0", 0),
    ("25", 63),
    ("75", 191),
]


def test_convert_level_valid_inputs():
    """Test conversion with valid inputs."""
    for input_val, expected in TEST_CASES:
        result = convert_level(input_val)
        assert result == expected, f"convert_level('{input_val}') should return {expected}, got {result}"


def test_convert_level_invalid_inputs():
    """Test conversion with invalid inputs."""
    invalid_inputs = ["100", "-1", "ABC", "GG", "", "99.5"]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(ValueError):
            convert_level(invalid_input)


def test_convert_level_edge_cases():
    """Test edge cases."""
    # Test that 0% maps to 0 and 99% maps to 253 (not 254 or 255)
    assert convert_level("0") == 0
    assert convert_level("99") == 253
    
    # Test that "FF" is the only way to get 255
    assert convert_level("FF") == 255
```

### 4. Integrar con el parser existente
Modificar `backend/src/converter/parser.py` para usar la función de conversión:

En el método `parse_channel_data()`, después de extraer los niveles, convertir cada valor:
```python
from src.converter.transformer import convert_level

# En parse_channel_data(), cuando se procesan los canales:
for cue_int in channel_data:
    for i, channel_str in enumerate(channel_data[cue_int]):
        try:
            qlc_value = convert_level(channel_str)
            channel_data[cue_int][i] = str(qlc_value)  # Guardar como string para mantener formato
        except ValueError as e:
            # Manejar errores de conversión (opcional: registrar o saltar)
            pass
```

### 5. Ejecutar tests y validaciones
```bash
# Desde el directorio backend/
python -m pytest src/tests/test_transformer.py -v
python -m pytest src/tests/ -v

# Verificar estilo de código
flake8 src/ --max-line-length=100 --extend-ignore=E203,W503

# Verificar tipos
mypy src/
```

### 6. Crear commit
```bash
git add backend/src/converter/transformer.py backend/src/tests/test_transformer.py backend/src/converter/parser.py
git commit -m "feat(backend): implement channel level conversion logic\n\nImplement convert_level function to transform Picolo levels (0-99, FF) to QLC+ decimal values (0-255). Add comprehensive unit tests and integrate with parser module."
```

## Criterios de Aceptación
- [ ] Función `convert_level()` creada y funcional
- [ ] Convierte "FF" a 255 ✓
- [ ] Convierte strings numéricos (ej. "50") correctamente ✓
- [ ] Maneja el caso "0" correctamente ✓
- [ ] Tests unitarios escritos y pasan para todos los casos ✓

## Dependencias
- Ninguna - este es un módulo independiente de lógica de negocio

## Riesgos y Consideraciones
1. **Validación de entrada**: Asegurar que solo se acepten valores válidos (0-99, FF)
2. **Manejo de errores**: Proporcionar mensajes de error claros para valores inválidos
3. **Integración**: Verificar que la función se integra bien con el parser existente sin romper tests existentes
4. **Rango de salida**: Asegurar que los valores resultantes están siempre en 0-255
