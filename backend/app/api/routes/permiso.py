# backend/app/api/routes/permiso.py

# uuid: para tipar el parámetro {permiso_id} que viene en la URL.
import uuid

# APIRouter, Depends, Query: mismo mecanismo que usuario.py.
from fastapi import APIRouter, Depends, Query

# Session: tipo de la sesión de base de datos.
from sqlalchemy.orm import Session

# get_db: la dependencia que abre y cierra la sesión sola.
from backend.app.database.database import get_db

# Los tres esquemas de Permiso que necesitamos acá.
from backend.app.schemas.permiso import PermisoCreate, PermisoUpdate, PermisoResponse

# El módulo completo del servicio.
from backend.app.services import permiso_service

# Nuestras dos excepciones propias.
from backend.app.core.exceptions import BusinessException, NotFoundException

# Los helpers de respuesta estandarizada, mismo criterio que usuario.py.
from backend.app.utils.responses import success_response, error_response


router = APIRouter(
    prefix="/api/v1/permisos",
    tags=["Permisos"]
)


def _serializar(permiso) -> dict:
    """
    Helper interno, mismo criterio que _serializar() en usuario.py:
    convierte el objeto Permiso de SQLAlchemy en un diccionario
    serializable a JSON, usando el esquema de salida.
    """
    return PermisoResponse.model_validate(permiso).model_dump(mode="json")


@router.post("")
def crear_permiso(datos: PermisoCreate, db: Session = Depends(get_db)):
    # FastAPI ya validó "datos" contra PermisoCreate (longitudes máximas,
    # campos obligatorios) antes de llegar acá.
    try:
        permiso = permiso_service.crear_permiso(db, datos)
    except BusinessException as error:
        # Nombre duplicado: regla de negocio violada → 400.
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Permiso creado correctamente.",
        data=_serializar(permiso),
        status_code=201,
    )


@router.get("/{permiso_id}")
def obtener_permiso(permiso_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        permiso = permiso_service.obtener_permiso(db, permiso_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Permiso encontrado.",
        data=_serializar(permiso),
    )


@router.get("")
def listar_permisos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    permisos = permiso_service.listar_permisos(db, skip=skip, limit=limit)

    return success_response(
        message="Permisos obtenidos correctamente.",
        data=[_serializar(permiso) for permiso in permisos],
    )


@router.patch("/{permiso_id}")
def actualizar_permiso(permiso_id: uuid.UUID, datos: PermisoUpdate, db: Session = Depends(get_db)):
    try:
        permiso = permiso_service.actualizar_permiso(db, permiso_id, datos)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)
    except BusinessException as error:
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Permiso actualizado correctamente.",
        data=_serializar(permiso),
    )


@router.delete("/{permiso_id}")
def desactivar_permiso(permiso_id: uuid.UUID, db: Session = Depends(get_db)):
    # Igual que en Usuario: usa el verbo DELETE por convención REST,
    # pero por dentro desactiva, no borra físicamente.
    try:
        permiso = permiso_service.desactivar_permiso(db, permiso_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Permiso desactivado correctamente.",
        data=_serializar(permiso),
    )