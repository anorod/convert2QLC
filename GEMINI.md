# Project: Picolo to QLC+ Converter

## Project Overview

This project is a web application that automates the conversion of lighting show files from a Picolo lighting control desk to the QLC+ software format (`.qxc`).

The application is composed of two main decoupled components:

*   **Backend:** A conversion engine that handles the transformation logic. It's built with Python and FastAPI, and exposes a RESTful API.
*   **Frontend:** A web interface that allows users to interact with the service. It's a single-page application built with a modern JavaScript framework (Vue.js or React).

The entire application is containerized using Docker and orchestrated with Docker Compose.

## Version control workflow

The project uses gitflow as a version control workflow.

### Basic rules

*   **Lowercase and Hyphen-separated**: Stick to lowercase for branch names and use hyphens to separate words. For instance, feature/new-login or bugfix/header-styling.
*   **Alphanumeric Characters**: Use only alphanumeric characters (a-z, A-Z, 0–9) and hyphens. Avoid punctuation, spaces, underscores, or any non-alphanumeric character.
*   **No Continuous Hyphens**: Do not use continuous hyphens. feature--new-login can be confusing and hard to read.
*   **No Trailing Hyphens**: Do not end your branch name with a hyphen. For example, feature-new-login- is not a good practice.
*   **Descriptive**: The name should be descriptive and concise, ideally reflecting the work done on the branch.

### Branch prefixes

Using prefixes in branch names helps to quickly identify the purpose of the branches. Here are some common types of branches with their corresponding prefixes:

*   **Feature Branches**: These branches are used for developing new features. Use the prefix `feature/`. For instance, `feature/login-system`.
*   **Bugfix Branches**: These branches are used to fix bugs in the code. Use the prefix `bugfix/`. For example, `bugfix/header-styling`.
*   **Hotfix Branches**: These branches are made directly from the production branch to fix critical bugs in the production environment. Use the prefix `hotfix/`. For instance, `hotfix/critical-security-issue`.
*   **Release Branches**: These branches are used to prepare for a new production release. They allow for last-minute dotting of i’s and crossing t’s. Use the prefix `release/`. For example, `release/v1.0.1`.
*   **Documentation Branches**: These branches are used to write, update, or fix documentation eg. the README.md file. Use the prefix `docs/`. For instance, `docs/api-endpoints`.

### Include ticket or issue numbers

 If you are working on a ticket or issue numbered “T-123” for adding a new login system, the branch name could be `feature/T-123-new-login-system`.

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
