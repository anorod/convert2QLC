# Implement Time Mapping Logic

**Description**
Develop the logic for converting Picolo's time values (`TI`, `TO`, `TW`) into QLC+'s `FadeIn`, `FadeOut`, and `Hold` attributes in milliseconds. This includes handling the crossfade logic for `FadeOut` and special string values like "Manua".

**Checklist of acceptance criteria**

*   [ ] A function correctly converts Picolo's `TI` (seconds) to `FadeIn` (milliseconds).
*   [ ] The logic correctly calculates `FadeOut` for a step based on the `FadeIn` of the next step.
*   [ ] The `FadeOut` for the very last step is correctly calculated from its own `TO` value.
*   [ ] The logic correctly converts `TW` values to `Hold` (milliseconds), handling `"Manua"`, numeric, and alphanumeric cases.
*   [ ] Unit tests are written to validate the time mapping for all cases.

> Tags: backend, business-logic, transformation

---
