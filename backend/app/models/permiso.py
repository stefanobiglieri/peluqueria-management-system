# backend/app/models/permiso.py

# uuid: para generar el identificador único de cada permiso (misma
# lógica que en Rol y Usuario).
import uuid

# datetime, timezone: para calcular fecha_creacion/fecha_actualizacion
# siempre en UTC, igual que en los demás modelos.
from datetime import datetime, timezone

# Boolean, String, DateTime: los tipos de columna que vamos a usar.
from sqlalchemy import Boolean, String, DateTime

# Mapped, mapped_column: la sintaxis moderna de SQLAlchemy 2.0 para
# declarar columnas con su tipo de Python asociado.
from sqlalchemy.orm import Mapped, mapped_column

# Base: la clase declarativa de la que heredan todos los modelos.
from backend.app.database.database import Base


class Permiso(Base):
    __tablename__ = "permisos"

    # id: clave primaria UUID generada por Python, misma decisión que
    # en Rol y Usuario (no delegamos la generación a PostgreSQL).
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # nombre: el "nombre técnico" del permiso (ej. "crear_usuario"),
    # el que va a usar el código para verificar autorización — por eso
    # es UNIQUE: no pueden existir dos permisos con el mismo código.
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # descripcion: texto libre para uso humano (ej. en una futura
    # pantalla de administración de permisos), no lo usa el código.
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # modulo: agrupa permisos por área funcional del sistema (ej.
    # "Usuarios", "Turnos", "Pagos"). Sirve para poder mostrar los
    # permisos organizados por módulo en una futura UI de asignación
    # de roles, en vez de una lista plana de decenas de permisos.
    modulo: Mapped[str] = mapped_column(String(100), nullable=False)

    # activo: permite desactivar un permiso sin eliminarlo físicamente
    # (coherente con la regla de negocio: "los permisos desactivados
    # dejarán de otorgar acceso sin necesidad de eliminarlos").
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # fecha_creacion: se calcula sola al crear la fila.
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # fecha_actualizacion: se recalcula sola cada vez que se modifica
    # la fila.
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )