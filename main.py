# main.py

from fastapi import FastAPI
from api.routes import router as api_router
from core.config import settings

# Creación de la instancia principal de la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API para el procesamiento seguro de transacciones financieras."
)

# Mensaje de bienvenida en la ruta raíz
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Bienvenido a {settings.APP_NAME}"}

# Incluimos las rutas definidas en api/routes.py
# Esto mantiene nuestro código organizado.
app.include_router(api_router, tags=["API V1"])