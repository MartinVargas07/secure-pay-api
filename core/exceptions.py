# core/exceptions.py


class TransactionError(Exception):
    """Clase base para excepciones relacionadas con transacciones en la aplicación."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccountNotFoundError(TransactionError):
    """Se lanza cuando no se encuentra una cuenta en la base de datos."""

    pass


class InsufficientFundsError(TransactionError):
    """Se lanza cuando una cuenta no tiene fondos suficientes para una transacción."""

    pass


class SelfTransferError(TransactionError):
    """Se lanza cuando se intenta hacer una transferencia a la misma cuenta."""

    pass


class InvalidAPIKeyError(Exception):
    """Se lanza cuando una API Key es inválida o no se proporciona."""

    pass
