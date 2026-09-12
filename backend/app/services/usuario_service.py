# uuid: para tipar el identificador de usuario que reciben las funciones nuevas.
import uuid

# bcrypt: para hashear contraseñas.
import bcrypt

# Session: mismo tipo que en el repositorio.
from sqlalchemy.orm import Session

# Importamos el MÓDULO completo del repositorio.
from backend.app.repositories import usuario_repository as repository

# El modelo real y el Enum de tipo de login.
from backend.app.models.usuario import Usuario, TipoLogin

# Los esquemas de entrada: creación y actualización parcial.
from backend.app.schemas.usuario import UsuarioCreate, UsuarioUpdate

# Nuestras dos excepciones propias.
from backend.app.core.exceptions import BusinessException, NotFoundException


def _hashear_password(password: str) -> str:
    """Convierte una contraseña en texto plano en su hash con bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Aplica las reglas de negocio para dar de alta un Usuario nuevo."""
    if datos.email and repository.obtener_por_email(db, datos.email):
        raise BusinessException("Ya existe un usuario registrado con ese email.")

    if datos.telefono and repository.obtener_por_telefono(db, datos.telefono):
        raise BusinessException("Ya existe un usuario registrado con ese teléfono.")

    password_hash = None
    if datos.tipo_login == TipoLogin.EMAIL:
        password_hash = _hashear_password(datos.password)

    nuevo_usuario = Usuario(
        rol_id=datos.rol_id,
        email=datos.email,
        telefono=datos.telefono,
        tipo_login=datos.tipo_login,
        password_hash=password_hash,
    )

    return repository.crear(db, nuevo_usuario)


def obtener_usuario(db: Session, usuario_id: uuid.UUID) -> Usuario:
    """
    Busca un usuario por id. A diferencia del repositorio (que devuelve
    None si no existe), el servicio convierte ese None en una excepción
    de negocio explícita — quien llame a esta función no tiene que
    acordarse de chequear None por su cuenta cada vez.
    """
    usuario = repository.obtener_por_id(db, usuario_id)
    if usuario is None:
        raise NotFoundException(f"No existe un usuario con id {usuario_id}.")
    return usuario


def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    """
    Por ahora es un simple 'paso a través' del repositorio, sin reglas de
    negocio propias. La dejamos igual en el servicio (y no llamamos al
    repositorio directo desde el endpoint) para mantener siempre el mismo
    camino de entrada: endpoint -> servicio -> repositorio, sin excepciones
    a la regla que compliquen entender el flujo más adelante.
    """
    return repository.listar(db, skip=skip, limit=limit)


def actualizar_usuario(db: Session, usuario_id: uuid.UUID, datos: UsuarioUpdate) -> Usuario:
    """Aplica cambios parciales sobre un usuario existente."""
    # Reutilizamos obtener_usuario: si no existe, ya lanza NotFoundException,
    # y no seguimos ejecutando el resto de la función.
    usuario = obtener_usuario(db, usuario_id)

    # Si mandaron un email nuevo Y es distinto al que ya tenía, verificamos
    # que no choque con el de otro usuario (excluyendo al propio usuario
    # que estamos editando, o siempre se "chocaría consigo mismo").
    if datos.email and datos.email != usuario.email:
        existente = repository.obtener_por_email(db, datos.email)
        if existente and existente.id != usuario.id:
            raise BusinessException("Ya existe un usuario registrado con ese email.")
        usuario.email = datos.email

    if datos.telefono and datos.telefono != usuario.telefono:
        existente = repository.obtener_por_telefono(db, datos.telefono)
        if existente and existente.id != usuario.id:
            raise BusinessException("Ya existe un usuario registrado con ese teléfono.")
        usuario.telefono = datos.telefono

    if datos.rol_id is not None:
        usuario.rol_id = datos.rol_id

    if datos.tipo_login is not None:
        usuario.tipo_login = datos.tipo_login

    if datos.password is not None:
        usuario.password_hash = _hashear_password(datos.password)

    if datos.activo is not None:
        usuario.activo = datos.activo

    if datos.bloqueado is not None:
        usuario.bloqueado = datos.bloqueado

    return repository.actualizar(db, usuario)


def desactivar_usuario(db: Session, usuario_id: uuid.UUID) -> Usuario:
    """Desactiva un usuario existente (no lo elimina físicamente)."""
    usuario = obtener_usuario(db, usuario_id)
    return repository.desactivar(db, usuario)