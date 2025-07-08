# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from typing import Generator

from main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    """Crea un cliente de prueba para la API."""
    with TestClient(app) as c:
        yield c
