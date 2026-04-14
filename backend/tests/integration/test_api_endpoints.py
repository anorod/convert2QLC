import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_picolo_file_path() -> Path:
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')
    )
    return Path(project_root, "docs", "test_files", "Ejemplo-Fichero-Picolo.txt")


class TestConvertEndpoint:
    def test_valid_picolo_file_returns_200(
        self, client: TestClient, valid_picolo_file_path: Path
    ) -> None:
        with open(valid_picolo_file_path, "rb") as f:
            response = client.post("/api/v1/convert", files={"file": ("test.txt", f)})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "converted_file" in data
        assert "<?xml" in data["converted_file"]

    def test_invalid_file_type_returns_error(
        self, client: TestClient
    ) -> None:
        fake_pdf_content = b"%PDF-1.4 fake pdf content"
        response = client.post(
            "/api/v1/convert", files={"file": ("test.pdf", fake_pdf_content)}
        )

        assert response.status_code in (400, 500)
        data = response.json()
        assert "detail" in data

    def test_empty_file_returns_error(self, client: TestClient) -> None:
        empty_content = b""
        response = client.post(
            "/api/v1/convert", files={"file": ("empty.txt", empty_content)}
        )

        assert response.status_code in (400, 500)
        data = response.json()
        assert "detail" in data


if __name__ == "__main__":
    pytest([__file__, "-v"])
