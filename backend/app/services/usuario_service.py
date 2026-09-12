# bcrypt: la librería que reemplaza a passlib para hashear contraseñas.
import bcrypt

# Session: mismo tipo que en el repositorio.
from sqlalchemy.orm import Session

# Importamos el MÓDULO completo del repositorio (no funciones sueltas).
# Así, en cada línea donde se usa (ej. "repository.crear(...)"), queda
# explícito a simple vista que esa operación es un acceso a datos.
from backend.app.repositories import usuario_repository as repository

# El modelo real, para construir la instancia que se va a guardar,
# y el Enum de tipo de login, para comparar contra él.
from backend.app.models.usuario import Usuario, TipoLogin

# El esquema de entrada: datos ya validados por Pydantic (formato de
# email, reglas de tipo_login/password ya verificadas).
from backend.app.schemas.usuario import UsuarioCreate

# Nuestra excepción propia para errores de regla de negocio.
from backend.app.core.exceptions import BusinessException


def _hashear_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano en su hash con bcrypt.
    bcrypt trabaja con bytes, no con str, por eso codificamos antes
    de hashear y decodificamos el resultado para guardarlo como texto
    normal en password_hash.
    gensalt() genera una 'sal' aleatoria distinta cada vez, para que
    dos usuarios con la misma contraseña nunca tengan el mismo hash.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Aplica las reglas de negocio para dar de alta un Usuario nuevo."""

    # Regla de negocio: rechazar un email ya registrado con un mensaje
    # claro, ANTES de que la base lo rechace con un UniqueConstraint
    # (mismo criterio ya aplicado con el CheckConstraint de tipo_login).
    if datos.email and repository.obtener_por_email(db, datos.email):
        raise BusinessException("Ya existe un usuario registrado con ese email.")

    if datos.telefono and repository.obtener_por_telefono(db, datos.telefono):
        raise BusinessException("Ya existe un usuario registrado con ese teléfono.")

    # Solo hasheamos contraseña si el login es por EMAIL. Si es por
    # TELEFONO, datos.password ya viene en None (lo garantiza el
    # model_validator de UsuarioCreate).
    password_hash = None
    if datos.tipo_login == TipoLogin.EMAIL:
        password_hash = _hashear_password(datos.password)

    # Armamos la instancia real del modelo, combinando los datos ya
    # validados del esquema con el password_hash calculado acá
    # (que nunca viaja en el esquema de entrada).
    nuevo_usuario = Usuario(
        rol_id=datos.rol_id,
        email=datos.email,
        telefono=datos.telefono,
        tipo_login=datos.tipo_login,
        password_hash=password_hash,
    )

    return repository.crear(db, nuevo_usuario)