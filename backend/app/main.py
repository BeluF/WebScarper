"""
Servidor principal de FastAPI para el Sistema de Recetario Personal.

Este módulo configura y arranca la aplicación FastAPI con todos los
endpoints necesarios para el scraping y gestión de recetas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, API_HOST, API_PORT, API_DEBUG
from app.database import crear_tablas
from app.api.routes import router

# Crear la aplicación FastAPI
app = FastAPI(
    title="WebScarper - Recetario Personal",
    description="API para scraping y gestión de recetas de cocina",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de la API
app.include_router(router)


@app.on_event("startup")
def startup_event():
    """
    Evento de inicio de la aplicación.
    
    Crea las tablas de la base de datos si no existen.
    """
    crear_tablas()


@app.get("/")
def root():
    """
    Endpoint raíz que muestra información básica de la API.
    
    Returns:
        Mensaje de bienvenida con links a la documentación.
    """
    return {
        "mensaje": "Bienvenido al API de WebScarper - Recetario Personal",
        "documentacion": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG
    )
