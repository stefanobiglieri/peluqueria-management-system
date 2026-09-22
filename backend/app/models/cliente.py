# backend/app/models/cliente.py

# uuid: para el id propio y para la FK hacia Usuario.
import uuid

# date: fecha_nacimiento es solo fecha, sin hora — a diferencia de
# fecha_creacion/fecha_actualizacion, que sí llevan hora y zona horaria.
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # usuario_id: FK única hacia Usuario — "única" (unique=True) porque
    # es una relación 1 a 1: cada Cliente corresponde a exactamente un
    # Usuario, y ese Usuario no puede ser a la vez el de otro Cliente.
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"), unique=True, nullable=False
    )

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)

    # fecha_nacimiento: opcional, según el diccionario de datos original
    # (no todos los clientes la informan al registrarse).
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)

    # observaciones: texto libre y potencialmente largo (ej. alergias,
    # preferencias), por eso Text y no String con un límite arbitrario.
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    # acepta_notificaciones: controla si el cliente recibe los mensajes
    # de WhatsApp (confirmación y recordatorio) que ya describiste.
    # Nace en True porque, según lo definido, cualquier cliente nuevo
    # empieza aceptando notificaciones salvo que decida desactivarlas.
    acepta_notificaciones: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )