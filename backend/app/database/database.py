"""
==========================================================
Archivo: database.py
Proyecto: Peluquería Management System

Ubicación:
backend/app/database/

Función:
Centraliza toda la configuración de acceso a la base de datos.

Responsabilidades:

- Crear el motor de SQLAlchemy.
- Crear las sesiones de trabajo.
- Definir la clase Base para los modelos.
- Proporcionar la dependencia get_db() utilizada
  por FastAPI.

Todos los modelos del sistema heredarán de Base.

Todos los endpoints utilizarán get_db() para acceder
a PostgreSQL.
==========================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import DATABASE_URL


# ==========================================================
# Clase Base
# ==========================================================

class Base(DeclarativeBase):
    """
    Clase base para todos los modelos de la base de datos.
    """
    pass


# ==========================================================
# Motor de conexión
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    echo=True
)


# ==========================================================
# Fábrica de sesiones
# ==========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================================
# Dependencia para FastAPI
# ==========================================================

def get_db():
    """
    Crea una sesión de base de datos.

    La sesión se abre al comenzar una petición y se
    cierra automáticamente cuando ésta finaliza.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()