# uuid: para tipar el parámetro {rol_id} que viene en la URL de varios endpoints.
import uuid

# APIRouter: agrupa los endpoints de Rol bajo su propio prefijo y tag.
# Depends: para inyectar la sesión de base de datos.
# Query: para poder restringir skip/limit, igual que hicimos en Usuario.
from fastapi import APIRouter, Depends, Query

# Session: tipo de la sesión de base de datos.
from sqlalchemy.orm import Session

# get_db: la dependencia que abre y cierra la sesión por pedido HTTP.
from backend.app.database.database import get_db

# Los esquemas de Rol que necesitamos acá.
from backend.app.schemas.rol import RolCreate, RolUpdate, RolResponse

# NUEVO: el schema de entrada para asignar un permiso, y el de salida
# de Permiso (reutilizado, para devolver la lista de permisos de un rol
# con el mismo formato que ya usa el router de Permiso).
from backend.app.schemas.rol_permiso import AsignarPermisoRequest
from backend.app.schemas.permiso import PermisoResponse

# El módulo completo del servicio.
from backend.app.services import rol_service

# NUEVO: el servicio que resuelve la relación Rol-Permiso.
from backend.app.services import rol_permiso_service

# Nuestras dos excepciones propias.
from backend.app.core.exceptions import BusinessException, NotFoundException

# Los helpers de respuesta estandarizada del proyecto.
from backend.app.utils.responses import success_response, error_response


# Mismo patrón que usuario.py: prefijo y tag propios para este dominio.
router = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"]
)


def _serializar(rol) -> dict:
    """
    Mismo helper que usamos en usuario.py: convierte un objeto Rol de
    SQLAlchemy en un diccionario serializable a JSON, vía RolResponse.
    """
    return RolResponse.model_validate(rol).model_dump(mode="json")


# NUEVO: helper equivalente, pero para serializar un Permiso — se usa
# en los endpoints de asignación de más abajo, que devuelven permisos,
# no roles.
def _serializar_permiso(permiso) -> dict:
    return PermisoResponse.model_validate(permiso).model_dump(mode="json")


@router.post("")
def crear_rol(datos: RolCreate, db: Session = Depends(get_db)):
    # FastAPI ya validó "datos" contra RolCreate (que nombre sea texto,
    # etc.) antes de llegar acá.
    try:
        rol = rol_service.crear_rol(db, datos)
    except BusinessException as error:
        # Nombre duplicado, la única regla de negocio de esta entidad.
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Rol creado correctamente.",
        data=_serializar(rol),
        status_code=201,
    )


@router.get("/{rol_id}")
def obtener_rol(rol_id: uuid.UUID, db: Session = Depends(get_db)):
    # FastAPI convierte automáticamente {rol_id} de la URL a un UUID real.
    try:
        rol = rol_service.obtener_rol(db, rol_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Rol encontrado.",
        data=_serializar(rol),
    )


@router.get("")
def listar_roles(
    # Mismo blindaje que ya aplicamos en Usuario: limit nunca puede
    # superar 100, FastAPI lo rechaza solo con un 422 si se excede.
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    roles = rol_service.listar_roles(db, skip=skip, limit=limit)

    return success_response(
        message="Roles obtenidos correctamente.",
        data=[_serializar(rol) for rol in roles],
    )


@router.patch("/{rol_id}")
def actualizar_rol(rol_id: uuid.UUID, datos: RolUpdate, db: Session = Depends(get_db)):
    try:
        rol = rol_service.actualizar_rol(db, rol_id, datos)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)
    except BusinessException as error:
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Rol actualizado correctamente.",
        data=_serializar(rol),
    )


@router.delete("/{rol_id}")
def desactivar_rol(rol_id: uuid.UUID, db: Session = Depends(get_db)):
    # Mismo criterio que en Usuario: usa el verbo DELETE por convención
    # REST, pero por dentro desactiva en vez de borrar físicamente.
    try:
        rol = rol_service.desactivar_rol(db, rol_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Rol desactivado correctamente.",
        data=_serializar(rol),
    )


# ==========================================================
# NUEVO — Endpoints de asignación de permisos (relación RolPermiso)
# ==========================================================
# Estos tres endpoints resuelven la tabla intermedia RolPermiso sin
# exponerla como una entidad propia (Opción A ya confirmada): desde
# afuera, la relación se ve y se maneja como "los permisos de este rol",
# no como filas sueltas de una tabla de asignación.

@router.post("/{rol_id}/permisos")
def asignar_permiso(rol_id: uuid.UUID, datos: AsignarPermisoRequest, db: Session = Depends(get_db)):
    try:
        permiso = rol_permiso_service.asignar_permiso(db, rol_id, datos.permiso_id)
    except NotFoundException as error:
        # El rol o el permiso indicado no existen.
        return error_response(message=str(error), status_code=404)
    except BusinessException as error:
        # Ese permiso ya estaba asignado a ese rol.
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Permiso asignado correctamente al rol.",
        data=_serializar_permiso(permiso),
        status_code=201,
    )


@router.get("/{rol_id}/permisos")
def listar_permisos_de_rol(rol_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        permisos = rol_permiso_service.listar_permisos_de_rol(db, rol_id)
    except NotFoundException as error:
        # El rol indicado no existe.
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Permisos del rol obtenidos correctamente.",
        data=[_serializar_permiso(permiso) for permiso in permisos],
    )


@router.delete("/{rol_id}/permisos/{permiso_id}")
def quitar_permiso(rol_id: uuid.UUID, permiso_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        rol_permiso_service.quitar_permiso(db, rol_id, permiso_id)
    except NotFoundException as error:
        # El rol no existe, el permiso no existe, o esa asignación
        # puntual nunca existió — los tres casos son "recurso no
        # encontrado" → 404.
        return error_response(message=str(error), status_code=404)

    return success_response(message="Permiso quitado correctamente del rol.", data=None)