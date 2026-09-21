# backend/app/repositories/permiso_repository.py

# uuid: para tipar los parámetros que reciben un identificador de permiso.
import uuid

# Session: mismo tipo que en usuario_repository.py — cada función RECIBE
# una sesión ya abierta, nunca crea ni cierra sesiones por su cuenta.
from sqlalchemy.orm import Session

# El modelo de SQLAlchemy sobre el que vamos a operar.
from backend.app.models.permiso import Permiso


def crear(db: Session, permiso: Permiso) -> Permiso:
    """Inserta un Permiso ya armado en la base de datos."""
    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    return permiso


def obtener_por_id(db: Session, permiso_id: uuid.UUID) -> Permiso | None:
    """Busca un Permiso por id. Devuelve None si no existe."""
    return db.get(Permiso, permiso_id)


def obtener_por_nombre(db: Session, nombre: str) -> Permiso | None:
    """
    Busca un Permiso por su nombre técnico exacto. Se usa para validar
    la restricción UNIQUE antes de insertar o actualizar, dando un
    mensaje de error claro en vez de dejar que PostgreSQL rechace el
    INSERT con un IntegrityError críptico.
    """
    return db.query(Permiso).filter(Permiso.nombre == nombre).first()


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Permiso]:
    """Lista permisos con paginación básica, mismo criterio que Usuario."""
    return db.query(Permiso).offset(skip).limit(limit).all()


def actualizar(db: Session, permiso: Permiso) -> Permiso:
    """
    Guarda cambios sobre un Permiso ya modificado en memoria. No hace
    falta 'add' de nuevo: SQLAlchemy ya rastrea los cambios porque el
    objeto vino de esta sesión.
    """
    db.commit()
    db.refresh(permiso)
    return permiso


def desactivar(db: Session, permiso: Permiso) -> Permiso:
    """
    Desactiva un permiso en vez de borrarlo físicamente — mismo criterio
    que Usuario: un Permiso probablemente esté referenciado por
    RolPermiso, y borrarlo de verdad rompería esas asignaciones.
    """
    permiso.activo = False
    db.commit()
    db.refresh(permiso)
    return permiso