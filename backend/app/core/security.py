# bcrypt: para hashear y verificar contraseñas.
import bcrypt

# jwt: la librería PyJWT, para crear y decodificar tokens de sesión.
import jwt

# datetime, timedelta, timezone: para calcular el momento de expiración
# de cada token, siempre en UTC.
from datetime import datetime, timedelta, timezone

# Las tres variables de configuración que agregamos al .env y a config.py.
from backend.app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hashear_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano en su hash con bcrypt.
    Es la misma función que antes vivía duplicada dentro de
    usuario_service.py — la centralizamos acá porque ahora también
    la va a necesitar el módulo de autenticación.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Compara una contraseña en texto plano (la que alguien escribe al
    intentar loguearse) contra el hash guardado en la base de datos.
    bcrypt.checkpw hace esta comparación de forma segura: nunca
    "deshashea" el valor guardado (eso es imposible por diseño), sino
    que vuelve a hashear el texto plano recibido y compara los
    resultados entre sí.
    """
    return bcrypt.checkpw(password_plano.encode("utf-8"), password_hash.encode("utf-8"))


def crear_access_token(usuario_id: str) -> str:
    """
    Genera un token JWT que representa una sesión iniciada para un
    usuario puntual.
    """
    ahora = datetime.now(timezone.utc)

    # "payload": la información que va DENTRO del token, visible para
    # cualquiera que lo decodifique (un JWT no está encriptado, solo
    # firmado — cualquiera puede leer su contenido, pero no puede
    # modificarlo sin invalidar la firma).
    # "sub" (subject): convención estándar de JWT para identificar
    # a quién representa el token — en nuestro caso, el id del usuario.
    # "exp" (expiration): campo estándar de JWT que la propia librería
    # entiende automáticamente para rechazar el token una vez vencido.
    payload = {
        "sub": usuario_id,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": ahora,  # "issued at": cuándo se generó el token.
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT recibido. Si la firma no coincide
    (alguien lo alteró, o fue firmado con otra clave) o si ya expiró,
    jwt.decode lanza una excepción propia de PyJWT — dejamos que esa
    excepción se propague; quien llame a esta función decide cómo
    convertirla en una respuesta HTTP.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])