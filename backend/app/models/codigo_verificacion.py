# uuid: para generar el identificador único de cada código (misma lógica que en Rol y Usuario).
import uuid

# enum: para representar "canal", que solo puede ser SMS o WHATSAPP.
import enum

# datetime, timezone: para manejar fechas siempre en UTC.
from datetime import datetime, timezone

# Tipos de columna de SQLAlchemy:
# String → el código numérico en sí (lo guardamos como texto, no como número,
# porque nunca vamos a hacer cuentas matemáticas con él, y así evitamos
# perder un cero a la izquierda, ej. "042190").
# Boolean → para "utilizado".
# DateTime → para "expiracion" y "fecha_creacion".
# ForeignKey → declara que "usuario_id" apunta a la tabla "usuarios".
# Enum → tipo de columna que representa el Enum de Python en la base real.
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum

# Mapped y mapped_column: misma sintaxis moderna que venimos usando.
from sqlalchemy.orm import Mapped, mapped_column

# La Base compartida, ya conectada con Alembic.
from backend.app.database.database import Base


# Canal: Enum de Python con los dos únicos medios de envío posibles.
# Hereda de "str" por el mismo motivo que TipoLogin en Usuario:
# que se comporte como texto plano al serializar a JSON.
class Canal(str, enum.Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"


class CodigoVerificacion(Base):

    # Nombre real de la tabla en PostgreSQL.
    __tablename__ = "codigos_verificacion"

    # id: clave primaria UUID, generada por Python (misma decisión que en Rol y Usuario).
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # usuario_id: clave foránea hacia la tabla "usuarios", columna "id".
    # nullable=False → todo código pertenece obligatoriamente a un usuario.
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False
    )

    # codigo: el código de 6 dígitos enviado al usuario. String(6) porque,
    # como se explicó arriba, lo tratamos como texto, no como número.
    codigo: Mapped[str] = mapped_column(String(6), nullable=False)

    # canal: usa el Enum definido arriba. SQLEnum crea en PostgreSQL un tipo
    # de dato real llamado "canal_enum" que solo acepta 'SMS' o 'WHATSAPP'.
    canal: Mapped[Canal] = mapped_column(
        SQLEnum(Canal, name="canal_enum"), nullable=False
    )

    # utilizado: si el código ya fue canjeado. Por defecto, no.
    utilizado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # expiracion: NOT NULL, sin valor por defecto automático a nivel de columna,
    # porque el valor exacto (hora de creación + 2 minutos) lo vamos a calcular
    # explícitamente en la capa de servicio cuando generemos cada código,
    # no acá en el modelo. Lo dejamos así para que sea 100% explícito en el
    # lugar donde se genera el código, en vez de escondido en el modelo.
    expiracion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # fecha_creacion: se calcula sola al crear la fila (misma lógica que en Rol y Usuario).
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )