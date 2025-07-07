# api/routes.py

from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Body

from db.database import DatabaseSession, get_db_session
from db.models import Account, Transaction
from services.transaction_service import TransactionService
from core.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    SelfTransferError,
)
from .security import get_api_key
from pydantic import BaseModel

# Creamos un router para agrupar todos los endpoints de la v1 de la API.
router = APIRouter(prefix="/api/v1")


# --- Modelo para el cuerpo de la petición de creación de transacciones ---
class TransactionCreateRequest(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal


# --- Endpoints ---

@router.get("/accounts", response_model=list[Account])
async def get_all_accounts(db: DatabaseSession = Depends(get_db_session)):
    """Obtiene una lista de todas las cuentas existentes."""
    service = TransactionService(db)
    return service.get_all_accounts()


@router.get("/accounts/{account_id}", response_model=Account)
async def get_account_details(account_id: UUID, db: DatabaseSession = Depends(get_db_session)):
    """Obtiene los detalles de una cuenta específica por su ID."""
    service = TransactionService(db)
    try:
        return service.get_account(account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/accounts/{account_id}/transactions", response_model=list[Transaction])
async def get_account_transactions(account_id: UUID, db: DatabaseSession = Depends(get_db_session)):
    """Obtiene el historial de transacciones para una cuenta específica."""
    service = TransactionService(db)
    try:
        return service.get_transactions_for_account(account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/transactions",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_api_key)], # Endpoint protegido
)
async def create_new_transaction(
    transaction_request: TransactionCreateRequest,
    db: DatabaseSession = Depends(get_db_session),
):
    """
    Crea una nueva transacción financiera.
    Este endpoint está protegido y requiere una X-API-Key válida en las cabeceras.
    """
    service = TransactionService(db)
    try:
        # Pasamos los datos del cuerpo de la petición al servicio
        completed_transaction = service.create_transaction(
            source_account_id=transaction_request.source_account_id,
            destination_account_id=transaction_request.destination_account_id,
            amount=transaction_request.amount,
        )
        return completed_transaction
    except (AccountNotFoundError, InsufficientFundsError, SelfTransferError) as e:
        # Capturamos errores de negocio y los devolvemos como un error 400 Bad Request.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Capturamos cualquier otro error inesperado como un error 500 del servidor.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado al procesar la transacción.")