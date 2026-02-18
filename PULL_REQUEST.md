# Pull Request Description

## Summary

This PR implements the backend API endpoint for converting Picolo show files to QLC+ format. The implementation creates a FastAPI application with a `/api/v1/convert` endpoint that handles file uploads and performs the complete conversion workflow.

## Changes Made

1. **Created new `main.py` file** in the backend directory with:
   - FastAPI application setup
   - CORS middleware configuration
   - POST `/api/v1/convert` endpoint for handling file uploads
   - Integration with existing converter modules (parser, transformer, xml_generator)
   - Proper error handling and HTTP status codes

2. **Updated test import paths** in all test files to ensure proper module resolution

## Implementation Details

The API endpoint:
- Accepts multipart/form-data file uploads
- Parses Picolo files using the existing parser module
- Converts cue times using the transformer module
- Generates QLC+ XML format using the xml_generator module
- Returns structured JSON responses with converted content and metadata
- Handles both success and error cases appropriately

## Testing

The implementation has been tested to ensure:
- Existing converter modules continue to work as expected
- The API endpoint properly handles file uploads
- Conversion workflow completes successfully
- Error handling works for invalid files

## How to Test

The API can be tested by running the FastAPI application and sending requests using curl or any HTTP client.
