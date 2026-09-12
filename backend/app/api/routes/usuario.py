# uuid: lo usamos para tipar el parámetro {usuario_id} que viene en la URL
# de varios endpoints (GET, PATCH, DELETE por id).
import uuid

# APIRouter: agrupa los endpoints de Usuario bajo su propio prefijo y tag.
# Depends: mecanismo de FastAPI para inyectar dependencias (la sesión de
# base de datos) en los parámetros de una función de endpoint.
from fastapi import APIRouter, Depends, Query

# Session: tipo de la sesión de base de datos que vamos a recibir vía Depends.
from sqlalchemy.orm import Session

# get_db: la dependencia de database.py que abre una sesión al iniciar
# el pedido HTTP y la cierra sola al terminar.
from backend.app.database.database import get_db

# Los tres esquemas de Usuario que necesitamos acá: entrada para crear,
# entrada para actualizar (parcial), y salida (sin datos sensibles).
from backend.app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse

# El módulo completo del servicio, para que quede explícito en cada línea
# que esa operación es lógica de negocio (ej. "usuario_service.algo(...)").
from backend.app.services import usuario_service

# Nuestras dos excepciones propias: una para reglas de negocio violadas
# (400) y otra para recursos que no existen (404).
from backend.app.core.exceptions import BusinessException, NotFoundException

# Los helpers de respuesta estandarizada que ya existían en el proyecto,
# usados también por health.py.
from backend.app.utils.responses import success_response, error_response


# Mismo patrón que health.py: prefijo propio y tag propio, para que
# Swagger agrupe estos endpoints bajo "Usuarios" en la documentación.
router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"]
)


def _serializar(usuario) -> dict:
    """
    Helper interno (el guion bajo al principio del nombre es una
    convención de Python para decir "esto es de uso interno de este
    archivo, no se pensó para importarse desde otro lado").
    Evita repetir esta misma conversión en cada endpoint que devuelve
    un usuario: transforma el objeto Usuario de SQLAlchemy en un
    diccionario ya serializable a JSON, usando el esquema de salida.
    """
    # model_validate(usuario): arma un UsuarioResponse leyendo los
    # atributos del objeto de SQLAlchemy (posible por from_attributes=True).
    # .model_dump(mode="json"): lo convierte a diccionario, transformando
    # tipos como UUID y datetime a texto, compatible con JSONResponse.
    return UsuarioResponse.model_validate(usuario).model_dump(mode="json")


@router.post("")
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # FastAPI ya validó "datos" contra UsuarioCreate antes de llegar acá
    # (formato de email, reglas de tipo_login/password, etc.). Si algo
    # no cumplía, ya respondió 422 solo, sin ejecutar esta función.
    try:
        # Toda la lógica de negocio (duplicados, hasheo de contraseña,
        # armado del modelo) vive en el servicio, no acá.
        usuario = usuario_service.crear_usuario(db, datos)
    except BusinessException as error:
        # Convertimos la regla de negocio violada en una respuesta HTTP
        # clara, con el formato estándar del proyecto.
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Usuario creado correctamente.",
        data=_serializar(usuario),
        status_code=201,
    )


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    # {usuario_id} en la ruta y "usuario_id: uuid.UUID" acá coinciden por
    # nombre: FastAPI toma ese segmento de la URL y lo convierte
    # automáticamente a un uuid.UUID real. Si alguien manda algo que no
    # tiene forma de UUID, FastAPI responde 422 sin llegar a esta función.
    try:
        usuario = usuario_service.obtener_usuario(db, usuario_id)
    except NotFoundException as error:
        # Acá usamos 404, no 400: el pedido en sí estaba bien formado,
        # simplemente el recurso pedido no existe.
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Usuario encontrado.",
        data=_serializar(usuario),
    )


@router.get("")
def listar_usuarios(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # skip y limit NO aparecen entre llaves en la ruta ("" no tiene {}),
    # así que FastAPI los interpreta como parámetros de consulta (query
    # params) opcionales, con esos valores por defecto:
    # /api/v1/usuarios?skip=0&limit=50
    usuarios = usuario_service.listar_usuarios(db, skip=skip, limit=limit)

    return success_response(
        message="Usuarios obtenidos correctamente.",
        # Serializamos cada usuario de la lista, uno por uno, con el
        # mismo helper que usamos para un usuario individual.
        data=[_serializar(usuario) for usuario in usuarios],
    )


@router.patch("/{usuario_id}")
def actualizar_usuario(usuario_id: uuid.UUID, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    # UsuarioUpdate tiene todos los campos opcionales: quien llame a este
    # endpoint puede mandar solo el campo que quiere cambiar.
    try:
        usuario = usuario_service.actualizar_usuario(db, usuario_id, datos)
    except NotFoundException as error:
        # El usuario que se quiere actualizar no existe.
        return error_response(message=str(error), status_code=404)
    except BusinessException as error:
        # Existe, pero el cambio pedido viola una regla (ej. el nuevo
        # email ya lo tiene otro usuario).
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Usuario actualizado correctamente.",
        data=_serializar(usuario),
    )


@router.delete("/{usuario_id}")
def desactivar_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    # Se llama "delete" y usa el verbo HTTP DELETE por convención REST
    # (es el verbo esperado para "dar de baja" un recurso), pero por
    # dentro llama a desactivar_usuario, NO borra la fila físicamente —
    # coherente con la decisión de diseño ya tomada en el repositorio
    # (preservar integridad referencial e historial).
    try:
        usuario = usuario_service.desactivar_usuario(db, usuario_id)
    except NotFoundException as error:
        return error_response(message=str(error), status_code=404)

    return success_response(
        message="Usuario desactivado correctamente.",
        data=_serializar(usuario),
    )