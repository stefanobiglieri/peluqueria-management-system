# backend/app/api/routes/auth.py

# APIRouter: agrupa un conjunto de endpoints relacionados (login) para
# después registrarlos todos juntos en main.py con una sola línea.
# Depends: le dice a FastAPI "antes de ejecutar esta función, resolvé
# esta otra cosa primero" — en nuestro caso, abrir una sesión de base
# de datos.
from fastapi import APIRouter, Depends

# Session: el tipo de objeto que representa una conexión abierta a la
# base de datos, usado para tipar el parámetro que vamos a recibir.
from sqlalchemy.orm import Session

# get_db: la función que ya usan usuario.py y rol.py. Abre una sesión,
# se la entrega al endpoint, y la cierra sola al terminar la request
# (sin importar si hubo error o no) — nunca abrimos ni cerramos
# sesiones a mano acá.
from backend.app.database.database import get_db

# Importamos el MÓDULO completo de servicios de auth (no funciones
# sueltas), mismo criterio que usa codigo_verificacion_service.py al
# importar usuario_repository.
from backend.app.services import auth_service

# Los esquemas de entrada (Request) que ya creaste y verificaste. Ya no
# importamos TokenResponse ni MensajeResponse acá: no los usamos como
# response_model, porque devolvemos success_response()/error_response()
# (ver más abajo), no el schema Pydantic directo.
from backend.app.schemas.auth import (
    LoginEmailRequest, SolicitarCodigoRequest, VerificarCodigoRequest,
)

# BusinessException: la misma excepción propia que ya usa usuario.py
# para representar una regla de negocio violada (acá, "credenciales
# inválidas" o "código inválido/expirado"). NO importamos
# NotFoundException porque ningún camino de auth la usa: nunca queremos
# decir "ese usuario no existe" de forma explícita en login, eso le daría
# pistas a un atacante sobre qué emails/teléfonos están registrados.
from backend.app.core.exceptions import BusinessException

# Los mismos helpers de respuesta estandarizada que ya usan health.py y
# usuario.py. Los usamos acá por consistencia con el resto del proyecto:
# success_response() arma el JSON de éxito con "message" y "data";
# error_response() arma el de error con "message" y el status_code que
# le pasemos. Antes este archivo devolvía el schema Pydantic (TokenResponse)
# directo, lo cual rompía esa consistencia y —más grave— dejaba que
# BusinessException se propagara sin atrapar, causando un 500 genérico
# en vez de un 400 claro (el bug que acabamos de encontrar y corregir).
from backend.app.utils.responses import success_response, error_response

# prefix: cada ruta definida abajo queda automáticamente bajo
# /api/v1/auth (ej. la primera queda en POST /api/v1/auth/email), sin
# tener que repetir ese texto en cada @router.post.
# tags: agrupa estos 3 endpoints bajo el título "auth" en la pantalla
# de Swagger (/docs), separados visualmente de "Usuarios" y "rol".
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/email")
def login_email(payload: LoginEmailRequest, db: Session = Depends(get_db)):
    # payload: FastAPI ya validó que el JSON recibido tiene la forma de
    # LoginEmailRequest (email con formato válido + password como texto)
    # ANTES de que esta función se ejecute. Si no cumple, el cliente
    # recibe un 422 automático sin que este código llegue a correr.
    try:
        # Toda la lógica real (buscar el usuario, verificar password,
        # generar el token) vive en el servicio, no acá — mismo patrón
        # que usuario_service.py.
        resultado = auth_service.login_por_email(db, payload.email, payload.password)
    except BusinessException as error:
        # Acá caen TODOS los motivos de rechazo que agrupamos a propósito
        # en auth_service.py (usuario inexistente, inactivo, sin
        # password_hash, o password incorrecta) bajo el mismo mensaje
        # genérico "Credenciales inválidas." — por eso alcanza con
        # atrapar un solo tipo de excepción acá.
        return error_response(message=str(error), status_code=400)

    # resultado es un TokenResponse (Pydantic). .model_dump(mode="json")
    # lo convierte a diccionario plano, transformando cualquier tipo no
    # serializable directamente a JSON — acá no hay UUID ni datetime,
    # pero mantenemos la misma conversión que usa _serializar() en
    # usuario.py por consistencia.
    return success_response(
        message="Inicio de sesión exitoso.",
        data=resultado.model_dump(mode="json"),
    )


@router.post("/telefono/solicitar-codigo")
def solicitar_codigo(payload: SolicitarCodigoRequest, db: Session = Depends(get_db)):
    # OJO: a propósito, NO hay try/except acá. Repasando auth_service.py,
    # solicitar_codigo() nunca lanza BusinessException — devuelve el
    # mismo MensajeResponse genérico exista o no el usuario detrás de
    # ese teléfono (esa es justamente la decisión de seguridad que
    # confirmaste: este endpoint no debe poder usarse para averiguar
    # qué teléfonos están registrados).
    resultado = auth_service.solicitar_codigo(db, payload.telefono)

    # resultado.mensaje: el texto fijo definido en auth_service.py
    # (MENSAJE_CODIGO_GENERICO). data=None porque no hay ningún dato real
    # que devolver en este paso — el código nunca viaja por HTTP.
    return success_response(message=resultado.mensaje, data=None)


@router.post("/telefono/verificar")
def verificar_codigo(payload: VerificarCodigoRequest, db: Session = Depends(get_db)):
    try:
        # login_por_telefono ya valida internamente, a través de
        # codigo_verificacion_service.validar_codigo(), que el código
        # exista, no esté usado, y no haya expirado — cualquiera de esos
        # tres motivos llega acá como la MISMA BusinessException con el
        # mismo mensaje genérico (ver MENSAJE_CODIGO_INVALIDO).
        resultado = auth_service.login_por_telefono(db, payload.telefono, payload.codigo)
    except BusinessException as error:
        return error_response(message=str(error), status_code=400)

    return success_response(
        message="Inicio de sesión exitoso.",
        data=resultado.model_dump(mode="json"),
    )