# Project: Picolo to QLC+ Converter

## Project Overview

This project is a web application that automates the conversion of lighting show files from a Picolo lighting control desk to the QLC+ software format (`.qxc`).

The application is composed of two main decoupled components:

*   **Backend:** A conversion engine that handles the transformation logic. It's built with Python and FastAPI, and exposes a RESTful API.
*   **Frontend:** A web interface that allows users to interact with the service. It's a single-page application built with a modern JavaScript framework (Vue.js or React).

The entire application is containerized using Docker and orchestrated with Docker Compose.
The project uses gitflow as a version control workflow

## Building and Running

The project is still in the planning phase, and the directory does not yet contain the backend or frontend source code. The following commands are based on the project's documentation and will be valid once the code is implemented.

**TODO:** Add the specific commands for building and running the project once the `docker-compose.yml` file is created.

A `docker-compose.yml` file will be used to build and run the entire application. The following command will start the application:

```bash
docker-compose up -d
```

The frontend will be accessible at `http://localhost:8080`.

## Development Conventions

The project follows a modular and decoupled architecture. The backend and frontend are developed and deployed as separate services.

*   **Backend:**
    *   **Language:** Python
    *   **Framework:** FastAPI
    *   **Testing:** Unit tests for business logic and integration tests for the API endpoint.
*   **Frontend:**
    *   **Framework:** Vue.js or React
    *   **Server:** Nginx
*   **Deployment:**
    *   The application is deployed using Docker.
    *   Each service (backend and frontend) has its own `Dockerfile`.
    *   `docker-compose.yml` is used to orchestrate the services.
*   **Logging:** Both services should generate logs for success and error events.
