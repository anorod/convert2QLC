# Test Commands for the API

## Start the API Server

```bash
cd backend
python main.py
```

The server will start on `http://127.0.0.1:5000`

## Test Commands using curl

### 1. Test the root endpoint
```bash
curl http://127.0.0.1:5000/
```

### 2. Test the conversion endpoint with a sample Picolo file
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/convert" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_picolo_file.txt"
```

### 3. Test with a valid file (you'll need to have a sample Picolo file)
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/convert" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/your/picolo_file.txt"
```

### 4. Test error handling with invalid file
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/convert" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@invalid_file.txt"
```

### 5. Get OpenAPI documentation
```bash
curl http://127.0.0.1:5000/docs
```

## Sample Response Format

Successful conversion response:
```json
{
  "status": "success",
  "file_name": "sample_file.txt",
  "converted_file": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<QLCPlus version=\"4.12.0\" name=\"sample_file.txt\">...",
  "metadata": {
    "cue_count": 10,
    "channel_count": 50
  }
}
```

Error response:
```json
{
  "detail": "Invalid Picolo file format: <error message>"
}
```