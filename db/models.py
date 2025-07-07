# db/models.py

from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class Account(BaseModel):
    """
    Representa una cuenta de usuario en el sistema.
    """

    # Usamos UUID como identificador único para evitar IDs predecibles.
    id: UUID = Field(default_factory=uuid4)
    owner_name: str

    # CRÍTICO: Usamos Decimal para valores monetarios para evitar problemas
    # de precisión de punto flotante que ocurren con float.
    balance: Decimal = Field(ge=0)  # El saldo nunca puede ser negativo.

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("balance")
    def balance_must_have_two_decimal_places(cls, v):
        """Asegura que el balance siempre tenga 2 decimales."""
        return v.quantize(Decimal("0.01"))


class TransactionStatus(str, Enum):
    """
    Define los estados posibles de una transacción.
    Usar un Enum hace el código más legible y menos propenso a errores que usar strings.
    """

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Transaction(BaseModel):
    """
    Representa una transacción financiera entre dos cuentas.
    """

    id: UUID = Field(default_factory=uuid4)
    source_account_id: UUID
    destination_account_id: UUID

    # El monto de la transacción debe ser positivo.
    amount: Decimal = Field(gt=0)

    status: TransactionStatus = TransactionStatus.PENDING
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("amount")
    def amount_must_have_two_decimal_places(cls, v):
        """Asegura que el monto siempre tenga 2 decimales."""
        return v.quantize(Decimal("0.01"))
