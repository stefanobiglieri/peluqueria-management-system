# backend/app/services/rol_permiso_service.py

# uuid: para tipar rol_id y permiso_id.
import uuid

from sqlalchemy.orm import Session

# Importamos el MÓDULO completo del repositorio de la tabla intermedia.
from backend.app.repositories import rol_permiso_repository as repository

# Reutilizamos los servicios ya existentes de Rol y Permiso para validar
# que ambos existan — en vez de consultar sus repositorios directo acá,
# lo que evitaría duplicar la traducción de "no existe" a NotFoundException.
from backend.app.services import rol_service, permiso_service

# El modelo de salida: estas funciones devuelven Permiso, no RolPermiso,
# porque a quien llama le interesa "qué permiso es", no el detalle de
# la fila intermedia.
from backend.app.models.permiso import Permiso

from backend.app.core.exceptions import BusinessException, NotFoundException


def asignar_permiso(db: Session, rol_id: uuid.UUID, permiso_id: uuid.UUID) -> Permiso:
    """
    Asigna un permiso a un rol. Ambas líneas de abajo ya lanzan
    NotFoundException solas si el rol o el permiso no existen — no hace
    falta duplicar ese chequeo acá.
    """
    rol_service.obtener_rol(db, rol_id)
    permiso = permiso_service.obtener_permiso(db, permiso_id)

    # Evita una asignación duplicada con un mensaje de negocio claro,
    # en vez de dejar que la clave primaria compuesta de la base
    # rechace el INSERT con un IntegrityError técnico.
    if repository.existe(db, rol_id, permiso_id):
        raise BusinessException("Ese permiso ya está asignado a este rol.")

    repository.crear(db, rol_id, permiso_id)
    return permiso


def quitar_permiso(db: Session, rol_id: uuid.UUID, permiso_id: uuid.UUID) -> None:
    """Quita un permiso de un rol. Valida que ambos existan primero."""
    rol_service.obtener_rol(db, rol_id)
    permiso_service.obtener_permiso(db, permiso_id)

    eliminado = repository.eliminar(db, rol_id, permiso_id)
    if not eliminado:
        # El rol y el permiso existen, pero nunca estuvieron asociados
        # entre sí — es un recurso (la asignación) que no existe → 404,
        # no una regla de negocio violada.
        raise NotFoundException("Ese rol no tiene asignado ese permiso.")


def listar_permisos_de_rol(db: Session, rol_id: uuid.UUID) -> list[Permiso]:
    """Lista los permisos asignados a un rol. Valida que el rol exista."""
    rol_service.obtener_rol(db, rol_id)
    return repository.listar_permisos_de_rol(db, rol_id)