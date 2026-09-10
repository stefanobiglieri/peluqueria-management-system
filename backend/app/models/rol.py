# Módulo estándar de Python para generar identificadores únicos universales (UUID).
# Lo usamos para el campo "id" de cada fila, en lugar de un número autoincremental.
import uuid

# datetime: para manejar fechas y horas.
# timezone: para asegurarnos de que toda fecha que guardemos esté en UTC,
# evitando ambigüedades si el servidor o los usuarios están en husos horarios distintos.
from datetime import datetime, timezone

# Tipos de columna de SQLAlchemy que vamos a usar en esta tabla:
# String para texto de largo limitado, Boolean para verdadero/falso,
# DateTime para fechas con hora.
from sqlalchemy import String, Boolean, DateTime

# Mapped y mapped_column son la sintaxis moderna de SQLAlchemy 2.0.
# "Mapped[tipo]" declara en Python qué tipo de dato va a tener la columna,
# lo que habilita autocompletado y chequeo de tipos en el editor.
# "mapped_column(...)" es donde definimos las restricciones reales de la columna en la base de datos.
from sqlalchemy.orm import Mapped, mapped_column

# Importamos la misma Base que ya configuramos y conectamos con Alembic.
# Heredar de ella es lo que hace que esta clase quede "anotada" en Base.metadata,
# y por lo tanto visible para Alembic al generar migraciones.
from backend.app.database.database import Base


# Definimos la clase Rol, que hereda de Base.
# Cada clase que herede de Base se traduce en una tabla real de PostgreSQL.
class Rol(Base):

    # Nombre real de la tabla en la base de datos: en plural y en minúsculas,
    # siguiendo la convención estándar de SQL (independientemente de que la
    # clase Python se llame "Rol", en singular).
    __tablename__ = "roles"

    # id: clave primaria (primary_key=True), de tipo UUID.
    # default=uuid.uuid4 significa que Python genera el valor automáticamente
    # antes de insertar la fila (Opción A que elegiste: generación en la aplicación,
    # no en la base de datos).
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    # nombre: texto de hasta 50 caracteres.
    # unique=True → traduce la restricción UNIQUE del diccionario de datos
    # (no puede haber dos roles con el mismo nombre).
    # nullable=False → traduce NOT NULL (el campo es obligatorio).
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # descripcion: texto de hasta 255 caracteres.
    # El "| None" en el tipo indica que la columna admite NULL,
    # coherente con la restricción "NULL" (opcional) del diccionario de datos.
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # activo: verdadero/falso, obligatorio (NOT NULL), con valor por defecto TRUE.
    # Indica si el rol puede seguir usándose para asignarse a nuevos usuarios.
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # fecha_creacion: fecha y hora con zona horaria (timezone=True).
    # nullable=False → siempre debe tener un valor.
    # default=lambda: ... → se calcula automáticamente en el momento de crear la fila,
    # usando la hora actual en UTC. Usamos "lambda" para que la hora se calcule
    # recién cuando se crea cada fila, y no una sola vez cuando arranca el programa.
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # fecha_actualizacion: igual que fecha_creacion, pero además tiene "onupdate".
    # onupdate le dice a SQLAlchemy: "cada vez que esta fila se modifique,
    # recalculá este valor automáticamente", así nunca hay que actualizarla a mano
    # en cada lugar del código que edite un Rol.
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )