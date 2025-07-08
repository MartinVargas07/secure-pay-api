# tests/unit/test_transaction_service.py

import pytest
from uuid import uuid4
from decimal import Decimal

from services.transaction_service import TransactionService
from db.models import Account, TransactionStatus
from core.exceptions import InsufficientFundsError, SelfTransferError, AccountNotFoundError

# --- Mock de la Base de Datos para Pruebas Unitarias ---
class MockDatabaseSession:
    def __init__(self):
        self.accounts = {}
        self.transactions = {}

    def get_account_by_id(self, account_id):
        return self.accounts.get(account_id)

    def save_account(self, account):
        self.accounts[account.id] = account

    def save_transaction(self, transaction):
        self.transactions[transaction.id] = transaction

# --- Suite de Pruebas para TransactionService ---

def test_create_transaction_success():
    """Prueba el camino feliz: una transacción exitosa."""
    # Arrange
    mock_db = MockDatabaseSession()
    source_account = Account(owner_name="Sender", balance=Decimal("100.00"))
    dest_account = Account(owner_name="Receiver", balance=Decimal("50.00"))
    mock_db.save_account(source_account)
    mock_db.save_account(dest_account)
    
    service = TransactionService(db_session=mock_db)
    amount_to_transfer = Decimal("25.50")

    # Act
    transaction = service.create_transaction(
        source_account_id=source_account.id,
        destination_account_id=dest_account.id,
        amount=amount_to_transfer
    )

    # Assert
    assert transaction.status == TransactionStatus.COMPLETED
    assert transaction.amount == amount_to_transfer
    assert mock_db.accounts[source_account.id].balance == Decimal("74.50")
    assert mock_db.accounts[dest_account.id].balance == Decimal("75.50")
    assert len(mock_db.transactions) == 1

def test_create_transaction_insufficient_funds():
    """Prueba que se lanza una excepción si no hay fondos suficientes."""
    # Arrange
    mock_db = MockDatabaseSession()
    source_account = Account(owner_name="Sender", balance=Decimal("10.00"))
    dest_account = Account(owner_name="Receiver", balance=Decimal("50.00"))
    mock_db.save_account(source_account)
    mock_db.save_account(dest_account)
    
    service = TransactionService(db_session=mock_db)
    amount_to_transfer = Decimal("20.00")

    # Act & Assert
    with pytest.raises(InsufficientFundsError) as excinfo:
        service.create_transaction(
            source_account_id=source_account.id,
            destination_account_id=dest_account.id,
            amount=amount_to_transfer
        )
    
    assert "Saldo insuficiente" in str(excinfo.value)
    assert mock_db.accounts[source_account.id].balance == Decimal("10.00")

def test_create_transaction_self_transfer():
    """Prueba que se lanza una excepción al intentar transferir a la misma cuenta."""
    # Arrange
    mock_db = MockDatabaseSession()
    account = Account(owner_name="User", balance=Decimal("100.00"))
    mock_db.save_account(account)
    service = TransactionService(db_session=mock_db)

    # Act & Assert
    with pytest.raises(SelfTransferError):
        service.create_transaction(
            source_account_id=account.id,
            destination_account_id=account.id,
            amount=Decimal("10.00")
        )

def test_create_transaction_source_account_not_found():
    """Prueba que se lanza una excepción si la cuenta de origen no existe."""
    # Arrange
    mock_db = MockDatabaseSession()
    dest_account = Account(owner_name="Receiver", balance=Decimal("50.00"))
    mock_db.save_account(dest_account)
    service = TransactionService(db_session=mock_db)
    non_existent_id = uuid4()

    # Act & Assert
    with pytest.raises(AccountNotFoundError):
        service.create_transaction(
            source_account_id=non_existent_id,
            destination_account_id=dest_account.id,
            amount=Decimal("10.00")
        )

def test_create_transaction_with_negative_amount():
    """Prueba que se lanza un ValueError si el monto es negativo."""
    # Arrange
    mock_db = MockDatabaseSession()
    source_account = Account(owner_name="Sender", balance=Decimal("100.00"))
    dest_account = Account(owner_name="Receiver", balance=Decimal("50.00"))
    mock_db.save_account(source_account)
    mock_db.save_account(dest_account)
    
    service = TransactionService(db_session=mock_db)

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service.create_transaction(
            source_account_id=source_account.id,
            destination_account_id=dest_account.id,
            amount=Decimal("-10.00")
        )
    
    assert "El monto de la transacción debe ser positivo" in str(excinfo.value)

def test_create_account_success():
    """Prueba la creación exitosa de una nueva cuenta."""
    # Arrange
    mock_db = MockDatabaseSession()
    service = TransactionService(db_session=mock_db)
    owner_name = "Test User"
    initial_balance = Decimal("250.75")

    # Act
    new_account = service.create_account(owner_name, initial_balance)

    # Assert
    assert new_account is not None
    assert new_account.owner_name == owner_name
    assert new_account.balance == initial_balance.quantize(Decimal("0.01"))
    assert mock_db.get_account_by_id(new_account.id) is not None