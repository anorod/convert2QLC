# convert2QLC
Convert shows from different Light Consoles to software QLC+ 4.x

## Features
- Convert Picolo show files (.txt) to QLC+ XML format (.qxc)
- Extract detailed cue information with channel data
- Generate complete QLC+ projects with fixtures, scenes, and chasers

## Usage
1. Upload a Picolo show file via the API endpoint `/api/v1/convert`
2. Receive converted QLC+ XML file ready for import into QLC+

## Implementation Details
The converter extracts only the detailed cue section from Picolo files, which contains actual channel data. This ensures accurate conversion of lighting cues and their associated channel levels.

## Development
- Backend: Python/FastAPI
- Frontend: Vue.js/React (in development)
- Tests: pytest for backend testing
