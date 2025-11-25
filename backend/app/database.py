"""
Configuración de la base de datos SQLite con SQLAlchemy.

Este módulo configura la conexión a la base de datos y proporciona
la sesión para las operaciones de ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Crear el engine de SQLAlchemy
# check_same_thread=False es necesario para SQLite con FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Crear la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def obtener_db():
    """
    Generador que proporciona una sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy para operaciones de base de datos.
    
    Note:
        La sesión se cierra automáticamente al finalizar el uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def crear_tablas():
    """
    Crea todas las tablas definidas en los modelos.
    
    Esta función debe llamarse al iniciar la aplicación para
    asegurar que todas las tablas existan en la base de datos.
    """
    from app.models import Receta  # noqa: F401
    Base.metadata.create_all(bind=engine)
