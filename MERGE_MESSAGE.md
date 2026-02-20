# Merge Message

This merge implements the backend API endpoint for Picolo to QLC+ conversion. The implementation includes:

- FastAPI application with CORS middleware
- POST `/api/v1/convert` endpoint that handles file uploads
- Integration with existing converter modules (parser, transformer, xml_generator)
- Proper error handling and HTTP responses
- Complete conversion workflow from Picolo to QLC+ XML format

The API is ready for testing and will be used by the frontend application.