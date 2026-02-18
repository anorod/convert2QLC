---
description: Run backend tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.

The project structure shows tests are in backend/src/tests/ and uses pytest. 
Run all tests with proper PYTHONPATH configuration.

Use the following commands to execute:
!`cd backend && PYTHONPATH=src python -m pytest src/tests/ -v`