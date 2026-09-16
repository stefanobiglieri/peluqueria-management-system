# secrets: a diferencia del módulo "random" (pensado para simulaciones,
# juegos, etc.), "secrets" está diseñado específicamente para generar
# valores impredecibles con fines de seguridad. Para un código que
# protege el acceso a una cuenta, es el módulo correcto a usar.
import secrets

# uuid: para tipar el identificador de usuario.
import uuid

# datetime, timedelta, timezone: para calcular el momento exacto de
# expiración (ahora + 2 minutos), siempre en UTC.
from datetime import datetime, timedelta, timezone

# Session: mismo tipo que en los otros servicios.
from sqlalchemy.orm import Session

# Agregar este import junto a los demás, arriba del archivo:
from backend.app.repositories import usuario_repository

# Módulo completo del repositorio.
from backend.app.repositories import codigo_verificacion_repository as repository

# El modelo real y su Enum de canal.
from backend.app.models.codigo_verificacion import CodigoVerificacion, Canal

# Nuestra excepción de reglas de negocio (un código inválido o vencido
# es una violación de regla de negocio, no un recurso "no encontrado"
# en el sentido de NotFoundException).
from backend.app.core.exceptions import BusinessException


# Duración de validez del código, en minutos. Se definió explícitamente
# como una constante acá (y no como columna configurable en la base),
# porque el propio usuario del proyecto confirmó que no hace falta que
# sea configurable por ahora.
MINUTOS_DE_VALIDEZ = 2


def _generar_codigo_numerico() -> str:
    """
    Genera un código de 6 dígitos como texto (con posibles ceros a la
    izquierda, ej. "042190"). secrets.randbelow(1_000_000) da un número
    entre 0 y 999999; zfill(6) rellena con ceros a la izquierda si el
    número tiene menos de 6 dígitos, para que el código SIEMPRE tenga
    exactamente 6 caracteres.
    """
    numero = secrets.randbelow(1_000_000)
    return str(numero).zfill(6)


def generar_codigo(db: Session, usuario_id: uuid.UUID, canal: Canal) -> CodigoVerificacion:
    """
    Genera un nuevo código de verificación para un usuario, invalidando
    cualquier código anterior que siguiera sin usarse.
    """
    # Verificamos que el usuario exista y esté en condiciones de
    # iniciar sesión ANTES de generar nada. Esto evita un error técnico
    # de clave foránea, y aplica una regla de negocio real: un usuario
    # inactivo o bloqueado no debería poder recibir un código de login.
    usuario = usuario_repository.obtener_por_id(db, usuario_id)
    if usuario is None:
        raise BusinessException("El usuario indicado no existe.")
    if not usuario.activo:
        raise BusinessException("El usuario está inactivo y no puede iniciar sesión.")
    if usuario.bloqueado:
        raise BusinessException("El usuario está bloqueado y no puede iniciar sesión.")

    # Regla de negocio ya validada: cualquier código previo sin usar
    # queda invalidado al pedirse uno nuevo, exista o no haya expirado.
    codigos_previos = repository.obtener_no_utilizados_por_usuario(db, usuario_id)
    for codigo_previo in codigos_previos:
        repository.marcar_utilizado(db, codigo_previo)

    ahora = datetime.now(timezone.utc)

    nuevo_codigo = CodigoVerificacion(
        usuario_id=usuario_id,
        codigo=_generar_codigo_numerico(),
        canal=canal,
        expiracion=ahora + timedelta(minutes=MINUTOS_DE_VALIDEZ),
    )

    return repository.crear(db, nuevo_codigo)

def validar_codigo(db: Session, usuario_id: uuid.UUID, codigo_ingresado: str) -> None:
    """
    Valida un código ingresado por el usuario. Si es válido, lo marca
    como utilizado (no puede volver a usarse). Si no es válido o ya
    expiró, lanza BusinessException con un mensaje genérico.

    Nota de seguridad: el mensaje de error es intencionalmente el mismo
    tanto si el código no existe, como si ya se usó, como si expiró.
    Dar mensajes distintos para cada caso ("el código ya expiró" vs
    "el código es incorrecto") le daría pistas a alguien intentando
    adivinar códigos ajenos sobre cuál de esas situaciones ocurrió.
    """
    codigo = repository.obtener_vigente(db, usuario_id, codigo_ingresado)

    if codigo is None:
        raise BusinessException("El código ingresado es inválido o ha expirado.")

    repository.marcar_utilizado(db, codigo)