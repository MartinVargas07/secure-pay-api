# core/config.py

import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
# Es importante llamar a esta función antes de crear la instancia de Settings.
load_dotenv()


class Settings(BaseSettings):
    """
    Clase que gestiona la configuración de la aplicación.
    Hereda de BaseSettings de Pydantic, lo que le permite leer automáticamente
    las variables de entorno o desde un archivo .env.
    """

    APP_NAME: str = "SecurePay API"
    LOG_LEVEL: str = "INFO"

    # SecretStr es un tipo de Pydantic que oculta el valor en logs
    # y representaciones de string, añadiendo una capa de seguridad.
    SECRET_KEY: SecretStr
    ADMIN_API_KEY: SecretStr

    class Config:
        # Define el archivo del cual se pueden leer las variables de entorno.
        # En Pydantic V2, se recomienda usar @classmethod y settings_customise_sources
        # pero para mantenerlo simple y compatible, .env_file funciona bien.
        env_file = ".env"
        env_file_encoding = "utf-8"


# Creamos una única instancia de la configuración que será usada en toda la app.
# Esto sigue el patrón Singleton y asegura que la configuración se carga una sola vez.
settings = Settings()
