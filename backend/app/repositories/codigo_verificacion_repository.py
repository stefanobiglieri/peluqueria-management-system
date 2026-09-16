# uuid: para tipar los identificadores que reciben las funciones.
import uuid

# datetime, timezone: para comparar la fecha de expiración contra el
# momento actual, siempre en UTC (mismo criterio que en los modelos).
from datetime import datetime, timezone

# Session: mismo tipo que en los otros repositorios.
from sqlalchemy.orm import Session

# El modelo de SQLAlchemy sobre el que vamos a operar.
from backend.app.models.codigo_verificacion import CodigoVerificacion


def crear(db: Session, codigo: CodigoVerificacion) -> CodigoVerificacion:
    """Inserta un nuevo CodigoVerificacion en la base de datos."""
    db.add(codigo)
    db.commit()
    db.refresh(codigo)
    return codigo


def obtener_no_utilizados_por_usuario(
    db: Session, usuario_id: uuid.UUID
) -> list[CodigoVerificacion]:
    """
    Busca todos los códigos de un usuario que todavía no fueron usados,
    sin importar si ya expiraron o no. Se usa para invalidarlos todos
    de una vez cuando se genera un código nuevo (regla de negocio ya
    validada: solo puede haber un código "vivo" por usuario a la vez).
    """
    return (
        db.query(CodigoVerificacion)
        .filter(
            CodigoVerificacion.usuario_id == usuario_id,
            CodigoVerificacion.utilizado.is_(False),
        )
        .all()
    )


def obtener_vigente(
    db: Session, usuario_id: uuid.UUID, codigo_ingresado: str
) -> CodigoVerificacion | None:
    """
    Busca un código específico para un usuario, que además esté
    vigente en este momento: no utilizado Y todavía no expirado.
    Si no cumple las tres condiciones a la vez, devuelve None —
    la capa de servicio decide qué hacer con ese None.
    """
    ahora = datetime.now(timezone.utc)
    return (
        db.query(CodigoVerificacion)
        .filter(
            CodigoVerificacion.usuario_id == usuario_id,
            CodigoVerificacion.codigo == codigo_ingresado,
            CodigoVerificacion.utilizado.is_(False),
            CodigoVerificacion.expiracion > ahora,
        )
        .first()
    )


def marcar_utilizado(db: Session, codigo: CodigoVerificacion) -> CodigoVerificacion:
    """
    Marca un código como utilizado. Se usa en dos situaciones distintas
    (invalidar códigos viejos al generar uno nuevo, y consumir el código
    correcto al validarlo) porque, a nivel de datos, la operación es
    exactamente la misma: activo pasa a False.
    """
    codigo.utilizado = True
    db.commit()
    db.refresh(codigo)
    return codigo
