# backend/app/repositories/cliente_repository.py

import uuid

from sqlalchemy.orm import Session

from backend.app.models.cliente import Cliente

# Usuario: lo necesitamos para el JOIN, ya que email y teléfono viven
# ahí, no en Cliente.
from backend.app.models.usuario import Usuario

# func: para poder llamar a unaccent(), una función de PostgreSQL, no
# de Python — SQLAlchemy la traduce a SQL real en la consulta.
from sqlalchemy import func

def crear(db: Session, cliente: Cliente) -> Cliente:
    """
    Inserta un Cliente ya armado. Igual que ahora usuario_repository.crear(),
    NO hace commit: solo add() + flush() + refresh(). Quien llame a esta
    función (cliente_service.crear_cliente) es quien decide cuándo
    confirmar la transacción completa (Usuario + Cliente juntos).
    """
    db.add(cliente)
    db.flush()
    db.refresh(cliente)
    return cliente


def obtener_por_id(db: Session, cliente_id: uuid.UUID) -> Cliente | None:
    return db.get(Cliente, cliente_id)


def obtener_por_usuario_id(db: Session, usuario_id: uuid.UUID) -> Cliente | None:
    """
    Busca el Cliente asociado a un Usuario puntual. Útil, por ejemplo,
    para cuando alguien ya logueado (tenemos su usuario_id desde el
    token JWT) quiere ver sus propios datos de Cliente.
    """
    return db.query(Cliente).filter(Cliente.usuario_id == usuario_id).first()


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Cliente]:
    return db.query(Cliente).offset(skip).limit(limit).all()


def listar_con_contacto(
    db: Session, skip: int = 0, limit: int = 100, busqueda: str | None = None
) -> list[tuple[Cliente, str | None, str | None]]:
    query = db.query(Cliente, Usuario.email, Usuario.telefono).join(
        Usuario, Usuario.id == Cliente.usuario_id
    )

    if busqueda:
        patron = f"%{busqueda}%"

        # nombre_completo: concatena nombre + espacio + apellido, para
        # poder comparar contra búsquedas de ambos juntos (ej. "ana
        # gomez"). func.concat(...) arma esa concatenación en SQL, no
        # en Python, para que se resuelva sobre TODAS las filas de la
        # base de una sola vez, no fila por fila desde afuera.
        nombre_completo = func.concat(Cliente.nombre, " ", Cliente.apellido)

        query = query.filter(
            func.unaccent(Cliente.nombre).ilike(func.unaccent(patron))
            | func.unaccent(Cliente.apellido).ilike(func.unaccent(patron))
            | func.unaccent(nombre_completo).ilike(func.unaccent(patron))
        )

    return query.offset(skip).limit(limit).all()


def actualizar(db: Session, cliente: Cliente) -> Cliente:
    """
    A diferencia de crear(), acá SÍ hacemos commit: una actualización de
    Cliente es una operación autónoma, no forma parte de una creación
    conjunta con Usuario.
    """
    db.commit()
    db.refresh(cliente)
    return cliente