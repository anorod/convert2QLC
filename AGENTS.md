# AGENTS.md

This document provides guidelines for agentic coding assistants working on this repository.

## Build/Lint/Test Commands

### Backend (Python/FastAPI)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run backend locally:**
```bash
uvicorn main:app --reload --port 5000
```

**Run tests:**
```bash
pytest
```

**Run a single test:**
```bash
pytest path/to/test_file.py::test_function_name -v
```

**Type checking (mypy):**
```bash
mypy src/
```

**Linting (flake8):**
```bash
flake8 src/ --max-line-length=100 --extend-ignore=E203,W503
```

**Format code (black):**
```bash
black src/
```

### Frontend (Vue.js/React)

**Install dependencies:**
```bash
npm install
```

**Run frontend locally:**
```bash
npm run dev
```

**Build for production:**
```bash
npm run build
```

**Linting:**
```bash
npm run lint
```

**Format code:**
```bash
npm run format
```

### Docker

**Build and run containers:**
```bash
docker-compose up -d --build
```

**Stop containers:**
```bash
docker-compose down
```

## Code Style Guidelines

### Python (Backend)

#### Imports
- Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Add a blank line between groups
- Within each group, sort alphabetically
- No relative imports (use absolute imports)

Example:
```python
import json
import os
from pathlib import Path

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from src.converter.parser import parse_picolo_file
from src.converter.transformer import transform_to_qlc
```

#### Formatting
- Line length: 100 characters (not 88)
- Use 4 spaces for indentation
- No trailing whitespace
- No tabs
- Blank lines:
  - Two blank lines around top-level function and class definitions
  - One blank line around method definitions inside a class

#### Type Hints
- Always use type hints for function parameters and return values
- Use `typing` module for complex types (List, Dict, Optional, etc.)
- For variables with complex types, add type comments

Example:
```python
def convert_file(file: UploadFile) -> dict[str, str]:
    """Convert Picolo file to QLC+ format."""
    content = await file.read()
    result: dict[str, str] = {"status": "success"}
    return result
```

#### Naming Conventions
- **Variables**: snake_case (lowercase with underscores)
  - Example: `cue_list`, `max_channel_number`
- **Functions**: snake_case (lowercase with underscores)
  - Example: `parse_picolo_file()`, `transform_to_qlc()`
- **Classes**: PascalCase (capitalized without underscores)
  - Example: `PicoloParser`, `QLCGenerator`
- **Constants**: UPPER_SNAKE_CASE (all uppercase with underscores)
  - Example: `MAX_FILE_SIZE`, `DEFAULT_PORT`
- **Private members**: Prefix with underscore (single leading underscore)
  - Example: `_internal_method()`

#### Error Handling
- Use specific exception types instead of bare `except:`
- Log errors before raising them
- Include context in error messages
- Use custom exceptions for business logic errors

Example:
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    data = parse_file(file_content)
except InvalidFileFormatError as e:
    logger.error(f"Invalid file format: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

#### Documentation
- Add docstrings to all public functions and classes
- Use Google style docstrings
- Include type information in docstrings
- Document parameters, return values, and exceptions

Example:
```python
def parse_picolo_file(content: str) -> dict:
    """Parse Picolo show file content.
    
    Args:
        content: The raw text content of the Picolo file.
    
    Returns:
        A dictionary containing parsed cue list and channel data.
    
    Raises:
        InvalidFileFormatError: If the file format is invalid.
    """
    pass
```

### JavaScript/TypeScript (Frontend)

#### Imports
- Group imports in this order:
  1. React/Vue imports
  2. Third-party imports
  3. Local component imports
- Sort alphabetically within groups
- Use absolute paths for local imports

Example:
```javascript
import { useState } from 'react';
import { Button, Upload } from 'antd';
import FileUpload from './components/FileUpload';
```

#### Formatting
- Line length: 100 characters
- Use 2 spaces for indentation
- No trailing whitespace
- Semicolons at end of statements
- Single quotes for strings

#### TypeScript
- Always use TypeScript (not plain JavaScript)
- Add type annotations to all function parameters and return values
- Define interfaces for complex data structures

Example:
```typescript
interface ConversionResult {
  summary: {
    cueCount: number;
    channelCount: number;
    scenes: Array<{ id: number; name: string }>;
  };
  fileName: string;
  fileContent: string;
}

async function convertFile(file: File): Promise<ConversionResult> {
  // implementation
}
```

#### Naming Conventions
- **Variables**: camelCase (lowercase first word, uppercase subsequent)
  - Example: `cueList`, `maxChannelNumber`
- **Functions**: camelCase
  - Example: `handleFileUpload()`, `downloadQxcFile()`
- **Classes/Components**: PascalCase
  - Example: `FileUpload`, `ConversionSummary`
- **Constants**: UPPER_SNAKE_CASE
  - Example: `MAX_FILE_SIZE`, `API_ENDPOINT`
- **React state**: Use descriptive names (not `state`, `data`)
  - Example: `isLoading`, `conversionResult`

#### Error Handling
- Use try/catch blocks for API calls and file operations
- Display user-friendly error messages
- Log errors to console for debugging
- Don't expose raw error details to users

Example:
```javascript
async function uploadFile(file) {
  try {
    const response = await fetch('/api/v1/convert', {
      method: 'POST',
      body: file,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Upload failed:', error);
    showErrorMessage('Failed to convert file. Please try again.');
    throw error;
  }
}
```

## Git Workflow

### Branch Naming
- Use lowercase with hyphens: `feature/new-login`
- Include ticket/issue numbers when applicable: `bugfix/T-123-header-styling`
- No continuous hyphens, no trailing hyphens
- Be descriptive and concise

### Commit Messages
- First line: Summary (50 chars max)
- Second line: Blank line
- Body: Detailed explanation if needed (wrap at 72 chars)
- Footer: Reference issues/PRs if applicable

Example:
```
Add file upload validation

Ensure files are validated on both client and server side.
Fixes #42
```

### Branch Prefixes
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `release/` - Release preparation
- `docs/` - Documentation updates

## Testing Guidelines

### Backend Tests
- Test all business logic functions
- Test edge cases (empty files, max values, etc.)
- Mock external dependencies
- Use pytest fixtures for test data

Example:
```python
import pytest
from src.converter.transformer import convert_level

@pytest.mark.parametrize("input_val,expected", [
    ("FF", 255),
    ("99", 253),
    ("0", 0),
])
def test_convert_level(input_val, expected):
    assert convert_level(input_val) == expected
```

### Frontend Tests
- Test component rendering and behavior
- Test API integration
- Test user interactions
- Use Jest for unit tests
- Use Cypress for E2E tests

Example:
```javascript
import { render, screen } from '@testing-library/react';
import FileUpload from './FileUpload';

test('renders file upload button', () => {
  render(<FileUpload />);
  expect(screen.getByText('Upload File')).toBeInTheDocument();
});
```

## Architecture Guidelines

### Backend
- Keep business logic separate from API routes
- Use FastAPI's dependency injection for shared dependencies
- Validate input at the API level and business logic level
- Return consistent error responses

### Frontend
- Separate components by concern (presentational vs. container)
- Use state management (Redux, Zustand) for complex state
- Keep components small and focused
- Use props to customize component behavior

## Logging

### Backend
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR
- Include context in log messages
- Don't log sensitive information
- Use structured logging when possible

Example:
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting file conversion", extra={
    "file_size": len(content),
    "filename": filename
})
```

### Frontend
- Log errors and warnings to console
- Include component names in logs for debugging
- Don't log sensitive user data

Example:
```javascript
console.error('[FileUpload] Conversion failed:', error);
```

## Security Guidelines

- Never commit secrets or credentials
- Validate all user input on both client and server
- Use parameterized queries to prevent SQL injection (if using databases)
- Sanitize file uploads to prevent malicious content
- Set appropriate CORS headers
- Use HTTPS in production
