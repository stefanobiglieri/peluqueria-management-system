# backend/app/services/permiso_service.py

# uuid: para tipar el identificador que reciben las funciones.
import uuid

# Session: mismo tipo que en el repositorio.
from sqlalchemy.orm import Session

# Importamos el MÓDULO completo del repositorio, mismo criterio que
# usuario_service.py.
from backend.app.repositories import permiso_repository as repository

# El modelo real.
from backend.app.models.permiso import Permiso

# Los esquemas de entrada: creación y actualización parcial.
from backend.app.schemas.permiso import PermisoCreate, PermisoUpdate

# Nuestras dos excepciones propias.
from backend.app.core.exceptions import BusinessException, NotFoundException


def crear_permiso(db: Session, datos: PermisoCreate) -> Permiso:
    """Aplica las reglas de negocio para dar de alta un Permiso nuevo."""
    # Validamos la unicidad de 'nombre' ACÁ, antes de intentar insertar,
    # para poder devolver un mensaje de negocio claro (400) en vez de
    # dejar que la restricción UNIQUE de la base rechace el INSERT con
    # un error técnico (500) — mismo criterio que Usuario con email.
    if repository.obtener_por_nombre(db, datos.nombre):
        raise BusinessException(f"Ya existe un permiso con el nombre '{datos.nombre}'.")

    nuevo_permiso = Permiso(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        modulo=datos.modulo,
    )

    return repository.crear(db, nuevo_permiso)


def obtener_permiso(db: Session, permiso_id: uuid.UUID) -> Permiso:
    """
    Busca un permiso por id. Convierte el None del repositorio en una
    excepción de negocio explícita — mismo criterio que
    obtener_usuario().
    """
    permiso = repository.obtener_por_id(db, permiso_id)
    if permiso is None:
        raise NotFoundException(f"No existe un permiso con id {permiso_id}.")
    return permiso


def listar_permisos(db: Session, skip: int = 0, limit: int = 100) -> list[Permiso]:
    """Simple 'paso a través' del repositorio, sin reglas propias."""
    return repository.listar(db, skip=skip, limit=limit)


def actualizar_permiso(db: Session, permiso_id: uuid.UUID, datos: PermisoUpdate) -> Permiso:
    """Aplica cambios parciales sobre un permiso existente."""
    # Si no existe, obtener_permiso ya lanza NotFoundException acá mismo.
    permiso = obtener_permiso(db, permiso_id)

    # Si mandaron un nombre nuevo Y es distinto al que ya tenía,
    # verificamos que no choque con el de otro permiso (excluyendo al
    # propio permiso que estamos editando).
    if datos.nombre and datos.nombre != permiso.nombre:
        existente = repository.obtener_por_nombre(db, datos.nombre)
        if existente and existente.id != permiso.id:
            raise BusinessException(f"Ya existe un permiso con el nombre '{datos.nombre}'.")
        permiso.nombre = datos.nombre

    if datos.descripcion is not None:
        permiso.descripcion = datos.descripcion

    if datos.modulo is not None:
        permiso.modulo = datos.modulo

    if datos.activo is not None:
        permiso.activo = datos.activo

    return repository.actualizar(db, permiso)


def desactivar_permiso(db: Session, permiso_id: uuid.UUID) -> Permiso:
    """Desactiva un permiso existente (no lo elimina físicamente)."""
    permiso = obtener_permiso(db, permiso_id)
    return repository.desactivar(db, permiso)