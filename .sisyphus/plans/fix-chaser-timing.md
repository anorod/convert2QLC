# 🛠️ PLAN FINAL: Fix Chaser Timing Logic & Crossfade Precision

## TL;DR
> **Summary**: Ajustar la lógica del backend para que los atributos `FadeIn`, `FadeOut` y `Hold` de los Chasers en QLC+ reflejen exactamente las especificaciones de Picolo, implementando la lógica de crossfade entre pasos y el manejo de tiempos manuales.
> **Deliverables**: 
> - Lógica de transformación actualizada (Python).
> - Suite de tests unitarios (`pytest`) con casos de borde (Manua, Crossfade, Last Step).
> - Verificación de no-regresión en `Scenes`.
> **Effort**: Short
> **Critical Path**: Implementación $\rightarrow$ Tests de Regresión $\rightarrow$ Verificación XML.

## Context
### Research Findings
- **Source of Truth**: `project-specs.md` (Secciones 4.2.2).
- **Input Reference**: `docs/test_files/20260220-TestSimplePicolo.txt`.
- **Expected Output Reference**: `docs/test_files/20260220-TestSimplePicolo.qxw`.

## Work Objectives
### Core Objective
Garantizar que la duración de cada paso en el Chaser sea idéntica a la intención del show original, respetando la transición suave entre cues y manejando correctamente los casos donde no hay un `TO` definido.

### Definition of Done (verifiable)
- [ ] `pytest` pasa con 100% de cobertura en los nuevos casos de tiempo.
- [ ] El XML generado para el archivo de prueba contiene:
    - `FadeIn` = $TI \times 1000$ ms.
    - `FadeOut(Step N)` = `FadeIn(Step N+1)`.
    - `FadeOut(Last Step)` = $TO_{last} \times 1000$ (o si no hay $TO$, usar $TI_{last} \times 1000$).
    - `Hold` = $TW \times 1000$ (con soporte para `"Manua"` y `"ManuaX"`).

### Must NOT Have (guardrails)
- DO NOT break existing `FadeIn`/`FadeOut` logic for `Scenes`.
- DO NOT use hardcoded values; all must derive from the parsed input.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: tests-after (using `pytest`).
- QA policy: Every task has agent-executed scenarios.
- Evidence: `.sisyphus/evidence/task-timing-verification.log`.

## Execution Strategy
### Parallel Execution Waves
**Wave 1: [Foundation]**
- [ ] Create git branch `feature/fix-chaser-timing`.
- [ ] Implement core timing calculation logic in the transformer.

**Wave 2: [Validation]**
- [ ] Implement unit tests with the provided test data.
- [ ] Run full test suite to verify no regressions.

## TODOs
- [x] **1. Preparación de Entorno**
  - **Task**: Crear rama `feature/fix-chaser-timing`.
  - **Acceptance Criteria**: `git branch --show-current` == `feature/fix-chaser-timing`. ✓ VERIFIED

- [x] **2. Implementación de Lógica de Tiempo (Backend)**
  - **What to do**: 
    1. Modificar el transformador para calcular `FadeIn` ($TI \times 1000$). ✓
    2. Implementar buffer/lookahead para calcular `FadeOut` del paso actual basándose en el $TI$ del siguiente. ✓
    3. Implementar lógica de "Last Step" para `FadeOut` usando su propio $TO$ (o $TI$ si $TO$ es nulo). ✓
    4. Implementar regex para `Hold`: extraer dígitos de strings como `"Manua4"` o usar `4294967294` si es solo `"Manua"`. ✓
  - **References**: `project-specs.md:93-103`.
  - **Files Modified**: `backend/src/converter/transformer.py`

- [x] **3. Suite de Tests de Precisión**
  - **What to do**: Crear `tests/test_chaser_timing.py` con casos:
    - Caso A: `TI=3, TO=3, TW=Manua` $\rightarrow$ `FI=3000, FO=3000, Hold=4294967294`. ✓
    - Caso B (Crossfade): Paso 1 ($TI=3$) y Paso 2 ($TI=5$) $\rightarrow$ Paso 1 `FadeOut` debe ser $5000$. ✓
    - Caso C: `TW="Manua4"` $\rightarrow$ `Hold=4000`. ✓
  - **Acceptance Criteria**: Ejecución de `pytest` sin fallos. ✓ (15 tests passed)
  - **File Created**: `backend/src/tests/test_chaser_timing.py`

- [x] **4. Verificación de No-Regresión (Scenes)**
  - **What to do**: Ejecutar tests existentes de `Scenes` para asegurar que la nueva lógica de crossfade no ha alterando el cálculo de `FadeIn/Out` simple de las escenas.
  - **Result**: All 21 time-related tests pass (3 existing + 15 new + 3 transformer). ✓

## Final Verification Wave (MANDATORY)
- [x] F1. Plan Compliance Audit — oracle ✓ APPROVED
  - All TODOs completed: Tasks 1-4 verified ✓
  - Branch created: `feature/fix-chaser-timing` ✓
  - Files modified per spec: `backend/src/converter/transformer.py` ✓
  
- [x] F2. Code Quality Review — unspecified-high ✓ APPROVED
  - Follows AGENTS.md Python style guidelines ✓
  - Type hints present on all functions ✓
  - Docstrings with examples (doctests) ✓
  - Error handling with specific exceptions ✓
  - No hardcoded values, all derived from input ✓

- [x] F3. Scope Fidelity Check — deep ✓ APPROVED
  - Test coverage: 18 tests pass (15 new + 3 existing) ✓
  - All spec requirements implemented per project-specs.md 4.2.2:
    - FadeIn = TI * 1000 ✓
    - FadeOut(Step N) = FadeIn(Step N+1) crossfade ✓
    - FadeOut(Last Step) = TO * 1000 (or TI fallback) ✓
    - Hold = TW * 1000 with Manua/ManuaX handling ✓
  - No scope creep: Only timing logic modified ✓

## Commit Strategy
Atomic commits per task. Message format: `fix(timing): description`.
