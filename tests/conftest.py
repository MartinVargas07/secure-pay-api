# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from typing import Generator

# Importamos la app principal de FastAPI para que el TestClient pueda interactuar con ella.
from main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    """
    Crea un cliente de prueba para la API.

    El scope="module" lo crea una vez por archivo, haciéndolo eficiente.
    """
    with TestClient(app) as c:
        yield c