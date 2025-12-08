# Implement Channel Level Conversion Logic

**Description**
Create the business logic to convert Picolo's channel level format (0-99 and "FF") to QLC+'s decimal format (0-255). This is a core transformation rule for the converter.

**Checklist of acceptance criteria**

*   [ ] A function is created that takes a Picolo level (string) as input and returns a QLC+ level (integer).
*   [ ] The function correctly converts `"FF"` to `255`.
*   [ ] The function correctly converts numeric strings (e.g., `"50"`) to their corresponding 0-255 value.
*   [ ] The function handles the `"0"` case correctly.
*   [ ] Unit tests are written to cover all conversion cases (FF, 0, 99, 50, etc.).

> Tags: backend, business-logic, transformation

---
