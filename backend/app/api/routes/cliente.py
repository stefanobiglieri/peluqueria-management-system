# backend/app/api/routes/cliente.py

import uuid

from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from backend.app.database.database import get_db

# NUEVO: agregamos ClienteListItem, el schema usado en el listado con
# email/telefono incluidos.
from backend.app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteListItem

from backend.app.services import cliente_service

from backend.app.core.exceptions import BusinessException, NotFoundException

from backend.app.utils.responses import success_response, error_response

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clientes"]
)


def _serializar(cliente) -> dict:
    """
    Helper para un Cliente individual (crear, obtener por id): NO tiene
    email/telefono, porque en esos casos no hace falta diferenciar
    entre varios — ya sabemos exactamente cuál es.
    """
    return ClienteResponse.model_validate(cliente).model_dump(mode="json")


def _serializar_con_contacto(item) -> dict:
    """
    Helper para el LISTADO: item es una tupla (Cliente, email, telefono),
    tal como la devuelve cliente_repository.listar_con_contacto() vía
    el JOIN con Usuario. Arma el dict combinando los campos propios de
    Cliente con los dos de contacto, que ayudan a diferenciar clientes
    con nombre y apellido iguales.
    """
    cliente, email, telefono = item
    data = ClienteResponse.model_validate(cliente).model_dump(mode="json")
    data["email"] = email
    data["telefono"] = telefono
    return data


@router.post("")
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    # ClienteCreate ya validó (vía su model_validator) que venga
    # email+password o telefono, antes de llegar acá.
    try:
        cliente = cliente_service.crear_cliente(db, datos)
    except BusinessException as error:
        # Email o teléfono ya registrado por otro Usuario.
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Cliente registrado correctamente.",
        data=_serializar(cliente),
        status_code=201,
    )


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        cliente = cliente_service.obtener_cliente(db, cliente_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Cliente encontrado.",
        data=_serializar(cliente),
    )


@router.get("")
def listar_clientes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    # Query param opcional: /api/v1/clientes?busqueda=Pérez
    # Si no se manda, listar_con_contacto() no aplica ningún filtro.
    busqueda: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    resultados = cliente_service.listar_clientes(db, skip=skip, limit=limit, busqueda=busqueda)

    return success_response(
        message="Clientes obtenidos correctamente.",
        data=[_serializar_con_contacto(item) for item in resultados],
    )