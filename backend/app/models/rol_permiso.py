# backend/app/models/rol_permiso.py

# uuid: para tipar las dos claves foráneas (ambas apuntan a columnas
# UUID de Rol y Permiso).
import uuid

# datetime, timezone: para fecha_creacion, la única fecha que tiene
# esta tabla (no hay fecha_actualizacion: una asignación de permiso no
# se "edita", se crea o se borra).
from datetime import datetime, timezone

# DateTime: el único tipo de columna propio que necesitamos acá además
# de las FK (rol_id y permiso_id son UUID, mismo tipo que su columna
# origen, así que no hace falta importar un tipo nuevo para ellas).
from sqlalchemy import DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    # rol_id y permiso_id: ambas marcadas primary_key=True. En
    # SQLAlchemy, cuando más de una columna tiene primary_key=True,
    # la clave primaria de la tabla queda compuesta por todas ellas
    # juntas — exactamente el (rol_id, permiso_id) que definiste en el
    # diccionario de datos. Esto es lo que impide, a nivel de base de
    # datos, que un mismo permiso se asigne dos veces al mismo rol: la
    # base rechazaría la segunda fila por violar la clave primaria.
    rol_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id"), primary_key=True
    )
    permiso_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permisos.id"), primary_key=True
    )

    # fecha_creacion: cuándo se asignó ese permiso a ese rol.
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )