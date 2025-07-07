# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from typing import Generator

# Importamos la app principal de FastAPI para que el TestClient pueda interactuar con ella.
from main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    """
    Fixture que crea un cliente de prueba para la API.
    scope="module" crea el cliente una vez por archivo de prueba.
    por cada archivo de pruebas que lo use, haciéndolo eficiente.
    """
    with TestClient(app) as c:
        yield c
