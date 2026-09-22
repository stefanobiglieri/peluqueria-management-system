# backend/app/repositories/rol_permiso_repository.py

# uuid: para tipar rol_id y permiso_id en cada función.
import uuid

# Session: mismo tipo que en los demás repositorios.
from sqlalchemy.orm import Session

# El modelo de la tabla intermedia.
from backend.app.models.rol_permiso import RolPermiso

# Permiso: lo necesitamos para el JOIN de listar_permisos_de_rol, que
# devuelve permisos reales, no filas de la tabla intermedia.
from backend.app.models.permiso import Permiso


def existe(db: Session, rol_id: uuid.UUID, permiso_id: uuid.UUID) -> bool:
    """
    Indica si ya existe esa asignación puntual. db.get() con una tupla
    busca por clave primaria compuesta — (rol_id, permiso_id), en el
    mismo orden en que se declararon en el modelo RolPermiso.
    """
    return db.get(RolPermiso, (rol_id, permiso_id)) is not None


def crear(db: Session, rol_id: uuid.UUID, permiso_id: uuid.UUID) -> RolPermiso:
    """Crea la fila de asignación en la tabla intermedia."""
    asignacion = RolPermiso(rol_id=rol_id, permiso_id=permiso_id)
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def eliminar(db: Session, rol_id: uuid.UUID, permiso_id: uuid.UUID) -> bool:
    """
    Elimina FÍSICAMENTE la fila de asignación — a diferencia de Usuario
    y Permiso, acá no hay 'desactivar': la asignación en sí no tiene
    historia de negocio que valga la pena preservar, es simplemente
    "este rol tiene o no tiene este permiso ahora".
    Devuelve True si existía y se borró, False si no existía.
    """
    asignacion = db.get(RolPermiso, (rol_id, permiso_id))
    if asignacion is None:
        return False
    db.delete(asignacion)
    db.commit()
    return True


def listar_permisos_de_rol(db: Session, rol_id: uuid.UUID) -> list[Permiso]:
    """
    Devuelve los objetos Permiso (no las filas de RolPermiso) asignados
    a un rol puntual, mediante un JOIN a través de la tabla intermedia.
    """
    return (
        db.query(Permiso)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .filter(RolPermiso.rol_id == rol_id)
        .all()
    )