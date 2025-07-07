# tests/integration/test_api_routes.py

from fastapi.testclient import TestClient
from decimal import Decimal

# La fixture 'client' viene de conftest.py
from core.config import settings

def test_get_all_accounts_success(client: TestClient):
    """Prueba que el endpoint para obtener todas las cuentas funciona."""
    # Arrange & Act
    response = client.get("/api/v1/accounts")
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data) >= 2 # Basado en los datos de prueba iniciales
    assert "owner_name" in response_data[0]
    assert "balance" in response_data[0]

def test_create_transaction_no_api_key(client: TestClient):
    """Prueba que el endpoint de transacciones está protegido y devuelve 401 sin API Key."""
    # Arrange
    payload = {
        "source_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "destination_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "amount": 10.0
    }

    # Act
    response = client.post("/api/v1/transactions", json=payload)

    # Assert
    assert response.status_code == 401 # FastAPI convierte la falta de cabecera a 401 por auto_error=True
    assert "API Key inválida o ausente" in response.json()["detail"]

def test_create_transaction_api_insufficient_funds(client: TestClient):
    """Prueba el flujo de error de la API cuando no hay fondos suficientes."""
    # Arrange: Primero, obtenemos las cuentas reales de la DB en memoria
    accounts_response = client.get("/api/v1/accounts")
    accounts = accounts_response.json()
    source_account_id = accounts[0]["id"]
    dest_account_id = accounts[1]["id"]
    
    # Un monto absurdamente alto para asegurar que falle
    high_amount = 9999999.99

    payload = {
        "source_account_id": source_account_id,
        "destination_account_id": dest_account_id,
        "amount": high_amount
    }
    headers = {"X-API-Key": settings.ADMIN_API_KEY.get_secret_value()}

    # Act
    response = client.post("/api/v1/transactions", json=payload, headers=headers)

    # Assert
    assert response.status_code == 400 # Bad Request por error de lógica de negocio
    assert "Saldo insuficiente" in response.json()["detail"]

def test_create_transaction_api_success(client: TestClient):
    """Prueba el camino feliz completo de una transacción a través de la API."""
    # Arrange
    accounts_response = client.get("/api/v1/accounts")
    accounts_before = accounts_response.json()
    source_account = accounts_before[0]
    dest_account = accounts_before[1]
    
    source_balance_before = Decimal(str(source_account["balance"]))
    
    amount_to_transfer = 100.00
    payload = {
        "source_account_id": source_account["id"],
        "destination_account_id": dest_account["id"],
        "amount": amount_to_transfer
    }
    headers = {"X-API-Key": settings.ADMIN_API_KEY.get_secret_value()}

    # Act
    response = client.post("/api/v1/transactions", json=payload, headers=headers)

    # Assert
    assert response.status_code == 201 # Created
    transaction_data = response.json()
    assert transaction_data["status"] == "COMPLETED"
    assert Decimal(str(transaction_data["amount"])) == Decimal(str(amount_to_transfer))

    # Verificamos que el saldo de la cuenta de origen realmente haya disminuido
    account_details_response = client.get(f"/api/v1/accounts/{source_account['id']}")
    source_account_after = account_details_response.json()
    source_balance_after = Decimal(str(source_account_after["balance"]))
    
    assert source_balance_after == source_balance_before - Decimal(str(amount_to_transfer))