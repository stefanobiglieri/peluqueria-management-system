# uuid: para tipar los parámetros que reciben un identificador de usuario.
import uuid

# Session: el tipo de objeto que SQLAlchemy usa para ejecutar operaciones
# dentro de una transacción. Cada función de este archivo RECIBE una
# sesión ya abierta — el repositorio nunca crea ni cierra sesiones por
# su cuenta, eso es responsabilidad de get_db() (ya definido en database.py).
from sqlalchemy.orm import Session

# El modelo de SQLAlchemy sobre el que vamos a operar.
from backend.app.models.usuario import Usuario


def crear(db: Session, usuario: Usuario) -> Usuario:
    """Inserta un Usuario ya armado en la base de datos."""
    # add(): le avisa a SQLAlchemy que esta fila es nueva.
    db.add(usuario)

    # flush() (NUEVO, reemplaza a commit()): ejecuta el INSERT real
    # DENTRO de la transacción actual, sin confirmarla todavía. Esto
    # permite que, si algo viola un CheckConstraint o UniqueConstraint,
    # el error salte acá mismo (igual que antes con commit), pero SIN
    # cerrar la transacción — quien llame a esta función decide cuándo
    # confirmar todo con un commit() propio, lo cual permite que esta
    # inserción forme parte de una operación más grande (ej. crear un
    # Cliente junto con su Usuario, todo o nada).
    db.flush()

    # refresh(): sigue funcionando igual después de flush() (no hace
    # falta que la transacción esté confirmada para releer la fila).
    db.refresh(usuario)

    return usuario


def obtener_por_id(db: Session, usuario_id: uuid.UUID) -> Usuario | None:
    """Busca un Usuario por id. Devuelve None si no existe."""
    return db.get(Usuario, usuario_id)


def obtener_por_email(db: Session, email: str) -> Usuario | None:
    """Busca un Usuario por email exacto. Devuelve None si no existe."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def obtener_por_telefono(db: Session, telefono: str) -> Usuario | None:
    """Busca un Usuario por teléfono exacto. Devuelve None si no existe."""
    return db.query(Usuario).filter(Usuario.telefono == telefono).first()


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    """
    Lista usuarios con paginación básica: 'skip' registros que se saltan
    y 'limit' como máximo a devolver, para no traer toda la tabla de golpe.
    """
    return db.query(Usuario).offset(skip).limit(limit).all()


def actualizar(db: Session, usuario: Usuario) -> Usuario:
    """
    Guarda cambios sobre un Usuario que YA fue modificado en memoria
    (ej. usuario.telefono = "nuevo"). No hace falta 'add' de nuevo:
    SQLAlchemy ya rastrea los cambios porque el objeto vino de esta sesión.
    """
    db.commit()
    db.refresh(usuario)
    return usuario


def desactivar(db: Session, usuario: Usuario) -> Usuario:
    """
    Desactiva un usuario en vez de borrarlo físicamente.
    Decisión de diseño intencional: un Usuario probablemente vaya a estar
    referenciado por Turnos, Comisiones, etc. en el futuro. Eliminarlo de
    verdad rompería esas referencias o perdería historial real del negocio.
    """
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario