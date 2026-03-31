"""
FastAPI application for Picolo to QLC+ conversion.
"""

import os
import sys
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Add the src directory to Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.converter.parser import PicoloParser
from src.converter.transformer import convert_cue_times
from src.converter.xml_generator import XMLGenerator

app = FastAPI(
    title="Picolo to QLC+ Converter",
    description="API for converting Picolo show files to QLC+ format",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Picolo to QLC+ Converter API"}

@app.post("/api/v1/convert")
async def convert_picolo_file(file: UploadFile) -> Dict[str, Any]:
    """
    Convert a Picolo file to QLC+ XML format.
    
    Args:
        file: The uploaded Picolo file (txt format)
        
    Returns:
        A dictionary containing the converted XML content and metadata
        
    Raises:
        HTTPException: If file upload fails or conversion process encounters errors
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse the Picolo file
        parser = PicoloParser(content_str)
        parsed_data = parser.parse()
        
        # Transform data for QLC+
        transformed_cues = convert_cue_times(parsed_data["cue_list"], {})
        
        # Generate XML using the XML generator
        xml_gen = XMLGenerator()
        xml_content = xml_gen.generate_xml(
            file.filename,
            transformed_cues,
            parsed_data["channel_data"],
            parsed_data.get("max_channel_number", 71),
            parsed_data.get("_channel_value_pairs", {})
        )
        
        return {
            "status": "success",
            "file_name": file.filename,
            "converted_file": xml_content,
            "metadata": {
                "cue_count": len(parsed_data.get("cues", [])),
                "channel_count": 71  # Fixed for now based on expected output
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Picolo file format: {str(e)}")
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error during conversion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during conversion")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)