# uuid: para tipar los parámetros que reciben un identificador de rol.
import uuid

# Session: el tipo de sesión de base de datos, misma lógica que en
# usuario_repository.py — este archivo recibe la sesión, nunca la crea.
from sqlalchemy.orm import Session

# El modelo de SQLAlchemy sobre el que vamos a operar.
from backend.app.models.rol import Rol


def crear(db: Session, rol: Rol) -> Rol:
    """Inserta un nuevo Rol en la base de datos."""
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


def obtener_por_id(db: Session, rol_id: uuid.UUID) -> Rol | None:
    """Busca un Rol por su id. Devuelve None si no existe."""
    return db.get(Rol, rol_id)


def obtener_por_nombre(db: Session, nombre: str) -> Rol | None:
    """Busca un Rol por nombre exacto. Devuelve None si no existe."""
    return db.query(Rol).filter(Rol.nombre == nombre).first()


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Rol]:
    """Lista roles con paginación básica."""
    return db.query(Rol).offset(skip).limit(limit).all()


def actualizar(db: Session, rol: Rol) -> Rol:
    """Guarda cambios sobre un Rol ya modificado en memoria."""
    db.commit()
    db.refresh(rol)
    return rol


def desactivar(db: Session, rol: Rol) -> Rol:
    """
    Desactiva un rol en vez de eliminarlo físicamente — mismo criterio
    que con Usuario: Rol va a estar referenciado por la clave foránea
    rol_id en la tabla usuarios, así que borrarlo de verdad rompería
    esa referencia para cualquier usuario que ya lo tenga asignado.
    """
    rol.activo = False
    db.commit()
    db.refresh(rol)
    return rol