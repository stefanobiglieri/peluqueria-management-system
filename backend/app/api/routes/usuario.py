# APIRouter: para agrupar los endpoints de Usuario bajo su propio prefijo,
# igual que ya hace health.py con los suyos.
# Depends: mecanismo de FastAPI para "inyectar" dependencias en una función
# de endpoint (en nuestro caso, la sesión de base de datos).
from fastapi import APIRouter, Depends

# Session: tipo de la sesión de base de datos.
from sqlalchemy.orm import Session

# get_db: la dependencia ya definida en database.py, que abre una sesión
# al empezar el pedido HTTP y la cierra automáticamente al terminar.
from backend.app.database.database import get_db

# Los esquemas de entrada y salida que ya construimos.
from backend.app.schemas.usuario import UsuarioCreate, UsuarioResponse

# El módulo de servicio completo (mismo criterio que usamos en el
# servicio con el repositorio: queda explícito en el código de dónde
# viene cada función, ej. "usuario_service.crear_usuario(...)").
from backend.app.services import usuario_service

# Nuestra excepción propia, para diferenciar errores de negocio de
# errores técnicos inesperados.
from backend.app.core.exceptions import BusinessException

# Los helpers de respuesta estandarizada que ya existían en el proyecto.
from backend.app.utils.responses import success_response, error_response


# Mismo patrón que health.py, pero con prefijo propio para este dominio
# y su propio tag (así, en la documentación automática de Swagger,
# los endpoints de Usuario van a aparecer agrupados bajo "Usuarios").
router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"]
)


@router.post("")
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo Usuario.

    FastAPI hace dos cosas automáticamente antes de que esta función
    se ejecute:
    1. Lee el cuerpo (body) de la petición HTTP y lo valida contra
       UsuarioCreate. Si algo no cumple (falta la contraseña siendo
       EMAIL, no hay email ni teléfono, etc.), FastAPI responde solo
       con un 422 y esta función ni siquiera llega a ejecutarse.
    2. Resuelve Depends(get_db): abre una sesión de base de datos
       y se la entrega a este parámetro.
    """
    try:
        # Delegamos toda la lógica de negocio al servicio. Este endpoint
        # no sabe nada de contraseñas, hashes, ni reglas de duplicados —
        # solo sabe recibir el pedido HTTP y devolver una respuesta.
        usuario = usuario_service.crear_usuario(db, datos)
    except BusinessException as error:
        # Si el servicio detectó una regla de negocio violada (email
        # duplicado, por ejemplo), la convertimos en una respuesta
        # HTTP clara con el formato estándar del proyecto.
        return error_response(message=str(error), status_code=400)

    # UsuarioResponse.model_validate(usuario): construye el esquema de
    # salida a partir del objeto de SQLAlchemy (posible gracias a
    # from_attributes=True que configuramos en UsuarioResponse).
    # .model_dump(mode="json"): convierte el esquema a un diccionario
    # con tipos ya compatibles con JSON (por ejemplo, UUID y datetime
    # se convierten a texto), porque JSONResponse no sabe serializar
    # esos tipos de Python directamente.
    usuario_serializado = UsuarioResponse.model_validate(usuario).model_dump(mode="json")

    return success_response(
        message="Usuario creado correctamente.",
        data=usuario_serializado,
        status_code=201,
    )