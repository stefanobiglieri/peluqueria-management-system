# backend/app/services/auth_service.py

# Session: mismo tipo que usan usuario_repository y
# codigo_verificacion_service — este archivo sigue el mismo patrón de
# funciones sueltas que reciben la sesión, no una clase con estado propio.
from sqlalchemy.orm import Session

from backend.app.core.security import verificar_password, crear_access_token
from backend.app.core.exceptions import BusinessException

# Importamos los MÓDULOS completos (no clases), igual que hace
# codigo_verificacion_service.py con usuario_repository.
from backend.app.repositories import usuario_repository
from backend.app.services import codigo_verificacion_service

# Canal: el Enum real que espera generar_codigo (no un string suelto).
from backend.app.models.codigo_verificacion import Canal

from backend.app.schemas.auth import TokenResponse, MensajeResponse

# Mismo mensaje textual que ya usa validar_codigo() en
# codigo_verificacion_service.py, para que un usuario inexistente y un
# código realmente inválido devuelvan EXACTAMENTE la misma respuesta.
MENSAJE_CODIGO_INVALIDO = "El código ingresado es inválido o ha expirado."
MENSAJE_CREDENCIALES_INVALIDAS = "Credenciales inválidas."
MENSAJE_CODIGO_GENERICO = "Si el número está registrado, recibirá un código."


def login_por_email(db: Session, email: str, password: str) -> TokenResponse:
    usuario = usuario_repository.obtener_por_email(db, email)

    # Un solo chequeo agrupa tres motivos distintos (no existe / está
    # desactivado / no tiene password_hash porque su tipo_login es
    # TELEFONO) para que el mensaje de error sea idéntico en los tres casos.
    if not usuario or not usuario.activo or not usuario.password_hash:
        raise BusinessException(MENSAJE_CREDENCIALES_INVALIDAS)

    if not verificar_password(password, usuario.password_hash):
        raise BusinessException(MENSAJE_CREDENCIALES_INVALIDAS)

    # "sub" es el campo estándar de JWT para identificar al dueño del
    # token. Usamos el id (nunca cambia), no el email.
    token = crear_access_token({"sub": str(usuario.id)})
    return TokenResponse(access_token=token)


def solicitar_codigo(db: Session, telefono: str) -> MensajeResponse:
    usuario = usuario_repository.obtener_por_telefono(db, telefono)

    # Solo generamos el código si el usuario existe y está activo, pero
    # la respuesta de abajo es SIEMPRE la misma exista o no el usuario:
    # así este endpoint no sirve para averiguar qué teléfonos están
    # registrados (misma decisión de seguridad que ya tomaste en
    # validar_codigo).
    if usuario and usuario.activo:
        codigo_verificacion_service.generar_codigo(db, usuario.id, Canal.WHATSAPP)

    return MensajeResponse(mensaje=MENSAJE_CODIGO_GENERICO)


def login_por_telefono(db: Session, telefono: str, codigo: str) -> TokenResponse:
    usuario = usuario_repository.obtener_por_telefono(db, telefono)

    # Mismo mensaje que un código inválido: no revelamos si el teléfono
    # existe o no en el sistema.
    if not usuario or not usuario.activo:
        raise BusinessException(MENSAJE_CODIGO_INVALIDO)

    # validar_codigo ya lanza BusinessException con este mismo mensaje
    # si el código no existe, ya se usó, o expiró — no hace falta
    # atraparla acá, se propaga tal cual hasta el endpoint.
    codigo_verificacion_service.validar_codigo(db, usuario.id, codigo)

    token = crear_access_token({"sub": str(usuario.id)})
    return TokenResponse(access_token=token)