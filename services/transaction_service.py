# services/transaction_service.py

from uuid import UUID
from decimal import Decimal

from db.database import DatabaseSession
from db.models import Account, Transaction, TransactionStatus
from core.exceptions import AccountNotFoundError, InsufficientFundsError, SelfTransferError

class TransactionService:
    """
    Encapsula toda la lógica de negocio relacionada con cuentas y transacciones.
    Opera sobre una sesión de base de datos que se le inyecta al ser instanciada.
    """

    def __init__(self, db_session: DatabaseSession):
        self.db = db_session

    def create_account(self, owner_name: str, balance: Decimal) -> Account:
        """
        Crea una nueva cuenta en el sistema.
        
        Args:
            owner_name: El nombre del titular de la cuenta.
            balance: El saldo inicial de la cuenta.
        
        Returns:
            El objeto Account recién creado.
        """
        if balance < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")

        new_account = Account(owner_name=owner_name, balance=balance)
        self.db.save_account(new_account)
        print(f"Cuenta creada exitosamente: {new_account.id}")
        return new_account

    def get_account(self, account_id: UUID) -> Account:
        """
        Obtiene una cuenta por su ID.
        
        Args:
            account_id: El UUID de la cuenta a buscar.
        
        Returns:
            El objeto Account si se encuentra.
        
        Raises:
            AccountNotFoundError: Si la cuenta no existe.
        """
        account = self.db.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"La cuenta con ID {account_id} no fue encontrada.")
        return account

    def get_all_accounts(self) -> list[Account]:
        """Devuelve una lista de todas las cuentas en el sistema."""
        return self.db.get_all_accounts()

    def get_transactions_for_account(self, account_id: UUID) -> list[Transaction]:
        """
        Obtiene el historial de transacciones para una cuenta específica.
        
        Args:
            account_id: El UUID de la cuenta.
        
        Returns:
            Una lista de objetos Transaction.
            
        Raises:
            AccountNotFoundError: Si la cuenta no existe.
        """
        # Primero, validamos que la cuenta exista.
        self.get_account(account_id)
        return self.db.get_transactions_for_account(account_id)

    def create_transaction(
        self,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Decimal
    ) -> Transaction:
        """
        Procesa una nueva transacción, aplicando todas las reglas de negocio.
        Esta operación simula una transacción atómica.
        
        Args:
            source_account_id: ID de la cuenta de origen.
            destination_account_id: ID de la cuenta de destino.
            amount: El monto a transferir.
            
        Returns:
            La transacción completada.
            
        Raises:
            Varias excepciones de negocio si las validaciones fallan.
        """
        # 1. Validación: No se puede transferir a la misma cuenta.
        if source_account_id == destination_account_id:
            raise SelfTransferError("La cuenta de origen y destino no pueden ser la misma.")

        # 2. Validación: El monto debe ser positivo (ya cubierto por Pydantic, pero es buena práctica validar).
        if amount <= 0:
            raise ValueError("El monto de la transacción debe ser positivo.")
            
        # 3. Obtener cuentas y validar existencia.
        source_account = self.get_account(source_account_id)
        destination_account = self.get_account(destination_account_id)

        # 4. Validación: Fondos suficientes.
        if source_account.balance < amount:
            raise InsufficientFundsError(f"Saldo insuficiente en la cuenta {source_account_id}.")

        # --- Inicio de la Operación Atómica (Simulada) ---
        transaction = Transaction(
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount
        )
        self.db.save_transaction(transaction) # Guardar en estado PENDING

        try:
            # 5. Actualizar saldos.
            source_account.balance -= amount
            destination_account.balance += amount

            # 6. Persistir los cambios en las cuentas.
            self.db.save_account(source_account)
            self.db.save_account(destination_account)

            # 7. Marcar la transacción como completada.
            transaction.status = TransactionStatus.COMPLETED
            self.db.save_transaction(transaction)
            
            print(f"Transacción completada: {transaction.id}")
            return transaction

        except Exception as e:
            # Si algo falla durante la operación, marcamos la transacción como fallida.
            transaction.status = TransactionStatus.FAILED
            self.db.save_transaction(transaction)
            print(f"Error durante la transacción {transaction.id}: {e}")
            # Re-lanzamos la excepción para que la capa superior la maneje.
            raise