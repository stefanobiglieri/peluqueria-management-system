# uuid: para generar el identificador único de cada usuario (misma lógica que en Rol).
import uuid

# enum: módulo estándar de Python para crear un conjunto cerrado de valores posibles.
# Lo usamos para representar tipo_login, que solo puede ser EMAIL o TELEFONO,
# nunca cualquier otro texto.
import enum

# datetime y timezone: igual que en Rol, para manejar fechas siempre en UTC.
from datetime import datetime, timezone

# Tipos de columna de SQLAlchemy:
# String → texto de largo limitado.
# Boolean → verdadero/falso.
# DateTime → fecha y hora.
# ForeignKey → declara que una columna apunta a la clave primaria de otra tabla.
# CheckConstraint → restricción a nivel de base de datos (nuestra Opción B).
# Enum → tipo de columna de SQLAlchemy que representa un enum de Python en la base real.
from sqlalchemy import String, Boolean, DateTime, ForeignKey, CheckConstraint, Enum as SQLEnum

# Mapped y mapped_column: misma sintaxis moderna que usamos en Rol.
from sqlalchemy.orm import Mapped, mapped_column

# La Base compartida, ya conectada con Alembic.
from backend.app.database.database import Base


# TipoLogin: un Enum de Python que define los únicos dos valores posibles.
# Heredar de "str" además de "enum.Enum" hace que estos valores se comporten
# como texto plano ("EMAIL", no "TipoLogin.EMAIL"), evitando problemas al
# serializar a JSON más adelante (en los endpoints).
class TipoLogin(str, enum.Enum):
    EMAIL = "EMAIL"
    TELEFONO = "TELEFONO"


class Usuario(Base):

    # Nombre real de la tabla en PostgreSQL.
    __tablename__ = "usuarios"

    # __table_args__: acá van las restricciones que involucran a MÁS DE UNA columna
    # a la vez (una restricción sobre una sola columna, como unique=True, va directamente
    # en esa columna; estas comparan dos columnas entre sí, por eso van acá).
    __table_args__ = (
        # Restricción 1 (punto 1 ya confirmado): si el login es por EMAIL,
        # exige password_hash cargado. Si es por TELEFONO, no lo exige.
        CheckConstraint(
            "(tipo_login = 'EMAIL' AND password_hash IS NOT NULL) "
            "OR (tipo_login = 'TELEFONO')",
            name="ck_usuario_password_requerido_si_email",
        ),
        # Restricción 2 (la que acabamos de sumar): al menos uno de los dos
        # datos de contacto para login (email o telefono) tiene que estar
        # informado. PostgreSQL rechaza cualquier fila donde ambos sean NULL,
        # sin importar qué parte del código intente insertarla.
        CheckConstraint(
            "email IS NOT NULL OR telefono IS NOT NULL",
            name="ck_usuario_email_o_telefono_obligatorio",
        ),
    )

    # id: clave primaria UUID, generada por Python (misma decisión que en Rol).
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # rol_id: clave foránea hacia la tabla "roles", columna "id".
    # nullable=False → todo usuario DEBE tener un rol asignado (NOT NULL del diccionario).
    rol_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id"), nullable=False
    )

    # email: único si está presente, pero puede ser NULL a nivel de columna
    # (la obligatoriedad de "al menos uno" la garantiza el CheckConstraint de arriba,
    # no esta columna por sí sola).
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # telefono: misma lógica que email.
    telefono: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    # tipo_login: usa el Enum que definimos arriba. SQLEnum crea en PostgreSQL
    # un tipo de dato real llamado "tipo_login_enum" que solo acepta 'EMAIL' o 'TELEFONO'.
    # nullable=False → todo usuario debe indicar explícitamente cómo inicia sesión.
    tipo_login: Mapped[TipoLogin] = mapped_column(
        SQLEnum(TipoLogin, name="tipo_login_enum"), nullable=False
    )

    # password_hash: NULLABLE, porque solo es obligatorio para quienes usan
    # tipo_login=EMAIL. Esa obligatoriedad la garantiza el CheckConstraint 1,
    # no esta columna.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # activo: si el usuario puede acceder al sistema. Por defecto, sí.
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # bloqueado: si tiene prohibido hacer nuevas reservas. Por defecto, no.
    bloqueado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ultimo_acceso: puede no existir todavía (un usuario recién creado nunca inició sesión).
    ultimo_acceso: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # fecha_creacion: se calcula sola al crear la fila (misma lógica que en Rol).
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # fecha_actualizacion: se recalcula sola cada vez que se modifica la fila.
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )