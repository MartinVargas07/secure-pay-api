# api/security.py

import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from core.config import settings

# Definimos el esquema de la API Key. Le decimos a FastAPI que busque
# una cabecera llamada "X-API-Key".
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependencia que valida la API Key proporcionada en la cabecera X-API-Key.

    Compara de forma segura la clave proporcionada con la clave de administrador
    almacenada en la configuración.

    Raises:
        HTTPException(401): Si la clave es inválida.
    """
    # Usamos .get_secret_value() para obtener el string real de SecretStr
    admin_key = settings.ADMIN_API_KEY.get_secret_value()

    if secrets.compare_digest(api_key, admin_key):
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o ausente.",
        )
