# uuid: para tipar el identificador de rol en las funciones del servicio.
import uuid

# Session: mismo tipo que en el repositorio.
from sqlalchemy.orm import Session

# Módulo completo del repositorio, mismo criterio que con Usuario.
from backend.app.repositories import rol_repository as repository

# El modelo real, para armar la instancia que se va a guardar.
from backend.app.models.rol import Rol

# Los esquemas de entrada.
from backend.app.schemas.rol import RolCreate, RolUpdate

# Nuestras dos excepciones propias, ya usadas con Usuario.
from backend.app.core.exceptions import BusinessException, NotFoundException


def crear_rol(db: Session, datos: RolCreate) -> Rol:
    """Aplica las reglas de negocio para dar de alta un Rol nuevo."""
    # Única regla de negocio real de esta entidad: no permitir nombres
    # duplicados, con un mensaje claro antes de que la base lo rechace
    # con su propio UniqueConstraint.
    if repository.obtener_por_nombre(db, datos.nombre):
        raise BusinessException(f"Ya existe un rol con el nombre '{datos.nombre}'.")

    nuevo_rol = Rol(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
    )

    return repository.crear(db, nuevo_rol)


def obtener_rol(db: Session, rol_id: uuid.UUID) -> Rol:
    """Busca un rol por id, o lanza NotFoundException si no existe."""
    rol = repository.obtener_por_id(db, rol_id)
    if rol is None:
        raise NotFoundException(f"No existe un rol con id {rol_id}.")
    return rol


def listar_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Rol]:
    """Lista roles, delegando directamente al repositorio."""
    return repository.listar(db, skip=skip, limit=limit)


def actualizar_rol(db: Session, rol_id: uuid.UUID, datos: RolUpdate) -> Rol:
    """Aplica cambios parciales sobre un rol existente."""
    rol = obtener_rol(db, rol_id)

    # Mismo criterio que con el email de Usuario: solo verificamos
    # duplicado si el nombre realmente está cambiando, y excluimos
    # al propio rol de la comparación.
    if datos.nombre and datos.nombre != rol.nombre:
        existente = repository.obtener_por_nombre(db, datos.nombre)
        if existente and existente.id != rol.id:
            raise BusinessException(f"Ya existe un rol con el nombre '{datos.nombre}'.")
        rol.nombre = datos.nombre

    if datos.descripcion is not None:
        rol.descripcion = datos.descripcion

    if datos.activo is not None:
        rol.activo = datos.activo

    return repository.actualizar(db, rol)


def desactivar_rol(db: Session, rol_id: uuid.UUID) -> Rol:
    """Desactiva un rol existente (no lo elimina físicamente)."""
    rol = obtener_rol(db, rol_id)
    return repository.desactivar(db, rol)