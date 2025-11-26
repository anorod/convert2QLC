# Project Plan: Picolo to QLC+ Show Converter

## Objective

This project aims to solve the manual and error-prone conversion of lighting show files from Picolo consoles to the QLC+ format. The solution is a web application that automates this process. It will be developed with a decoupled architecture, using a Python backend with FastAPI for the conversion logic and an interactive JavaScript frontend (Vue.js/React) for the user interface. The entire system will be orchestrated and deployed using Docker containers.

## Milestones and Tasks

### 1. Initial Phase: Environment Setup

- [ ] Initialize the Git repository.
- [ ] Create the directory structure (`backend/`, `frontend/`).
- [ ] Configure the initial `docker-compose.yml` file for the `backend` and `frontend` services.
- [ ] Create a base `Dockerfile` for the backend service (Python).
- [ ] Create a base `Dockerfile` for the frontend service (Node/Nginx).

### 2. Development Phase: Backend (Conversion Engine)

-   **2.1. Picolo File Parsing**
    -   [ ] Implement the reading and analysis of the `.txt` file.
    -   [ ] Create data models to store the Cue List and channel data.
    -   [ ] Implement the logic to identify the highest channel number.
    -   [ ] Implement input file validation (type, `.txt` extension, and maximum size configurable via an **environment variable**).
-   **2.2. Conversion Logic**
    -   [ ] Implement the channel level conversion function (Picolo to QLC+ 0-255).
    -   [ ] Implement the time mapping function (`TI`, `TO`, `TW` to `FadeIn`, `FadeOut`, `Hold`).
-   **2.3. XML Generation (QLC+)**
    -   [ ] Create the base structure of the `.qxc` XML document.
    -   [ ] Implement the generation of the generic Fixture.
    -   [ ] Implement the generation of Scenes from the parsed data.
    -   [ ] Implement the generation of the Chaser containing all the steps (cues).

### 3. Development Phase: Backend API

-   [ ] Set up the base FastAPI application.
-   [ ] Create the `POST /api/v1/convert` endpoint.
-   [ ] Implement file upload (`multipart/form-data`).
-   [ ] Integrate the conversion engine with the API endpoint.
-   [ ] Build the JSON response (`summary`, `fileName`, `fileContent`).
-   [ ] Implement error handling and corresponding JSON responses.

### 4. Development Phase: Frontend (User Interface)

-   [ ] Initialize the project (Vue.js or React).
-   [ ] Design and layout the main interface (upload area, buttons, results area).
-   [ ] Implement the file upload form.
-   [ ] Implement client-side file validation (`.txt` extension, size) for immediate feedback.
-   [ ] Implement **server-side validation in the Frontend container** (type, `.txt` extension, size) after user upload and before forwarding to the Backend.
-   [ ] Develop the service to communicate with the backend API.
-   [ ] Implement the loading state (animation/spinner) during conversion.
-   [ ] Implement the display of the conversion summary (`cueCount`, `channelCount`).
-   [ ] Implement the download button that generates the `.qxc` file from the `fileContent`.
-   [ ] Implement the display of error messages from the API.

### 5. Testing Phase

-   **5.1. Unit Tests (Backend):** Must be created and run concurrently with the development of each new function or component to ensure its correct operation from the start.
    -   [ ] Create tests for level conversion (cases `FF`, `99`, `0`, etc.).
    -   [ ] Create tests for time mapping (cases `Manua`, numeric, alphanumeric).
    -   [ ] Create tests for key parsing functions.
-   **5.2. Integration Tests (API)**
    -   [ ] Test the `/api/v1/convert` endpoint with valid `.txt` files (using available test resources).
    -   [ ] Test the endpoint with malformed or invalid files to verify errors.

### 6. Deployment Phase

-   [ ] Finalize the backend `Dockerfile` for production (with Gunicorn).
-   [ ] Finalize the frontend `Dockerfile` for production (static asset build and Nginx).
-   [ ] Configure `docker-compose.yml` for the production environment.
-   [ ] Configure Docker volumes to persist logs.

## Key Questions to Answer

1.  **Large File Handling:** This risk will be mitigated through backend validation. The maximum file size will be configurable via an environment variable to prevent excessively large files from being processed and affecting browser performance.
2.  **QLC+ Compatibility:** Is there a specific version of QLC+ with which the generated `.qxc` file must ensure compatibility?
