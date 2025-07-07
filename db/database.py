# db/database.py

from typing import Dict, List
from uuid import UUID
from decimal import Decimal

from .models import Account, Transaction

# --- SIMULACIÓN DE ALMACENAMIENTO EN BASE DE DATOS ---
# En un sistema real, esto sería una base de datos SQL o NoSQL.
# Usamos diccionarios en memoria para simular las tablas.
# Las claves serán los UUIDs para un acceso rápido.
_accounts_db: Dict[UUID, Account] = {}
_transactions_db: Dict[UUID, Transaction] = {}


def _initialize_mock_data():
    """Función para poblar la BD con datos de ejemplo al iniciar."""
    if not _accounts_db:  # Solo inicializar si está vacío
        account1 = Account(owner_name="Martin Vargas", balance=Decimal("1000.00"))
        account2 = Account(owner_name="Kevin Rosero", balance=Decimal("500.50"))
        _accounts_db[account1.id] = account1
        _accounts_db[account2.id] = account2


class DatabaseSession:
    """
    Esta clase simula una sesión de base de datos. En un sistema con SQLAlchemy,
    esto manejaría el Engine, la Session y las transacciones (commit, rollback).
    Aquí, simplemente opera sobre nuestros diccionarios en memoria.
    """

    def get_account_by_id(self, account_id: UUID) -> Account | None:
        """Busca una cuenta por su UUID."""
        return _accounts_db.get(account_id)

    def save_account(self, account: Account):
        """Guarda o actualiza una cuenta en la 'base de datos'."""
        _accounts_db[account.id] = account

    def get_all_accounts(self) -> List[Account]:
        """Devuelve todas las cuentas."""
        return list(_accounts_db.values())

    def save_transaction(self, transaction: Transaction):
        """Guarda una nueva transacción."""
        _transactions_db[transaction.id] = transaction

    def get_transactions_for_account(self, account_id: UUID) -> List[Transaction]:
        """Busca todas las transacciones de una cuenta (como origen o destino)."""
        return [
            tx
            for tx in _transactions_db.values()
            if tx.source_account_id == account_id
            or tx.destination_account_id == account_id
        ]


def get_db_session():
    """
    Esta es una función generadora que actúa como un Inyector de Dependencias en FastAPI.
    """
    _initialize_mock_data()  # Aseguramos que haya datos de prueba
    session = DatabaseSession()
    try:
        yield session
    finally:
        # En una BD real, aquí iría 'session.close()'
        pass
