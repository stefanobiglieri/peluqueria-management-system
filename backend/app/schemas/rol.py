# uuid: para tipar el "id" en el esquema de respuesta.
import uuid

# datetime: para tipar los campos de fecha en el esquema de respuesta.
from datetime import datetime

# BaseModel: clase base de todo esquema de Pydantic.
# ConfigDict: para habilitar from_attributes en RolResponse, igual que
# hicimos en UsuarioResponse (leer directo desde un objeto de SQLAlchemy).
from pydantic import BaseModel, ConfigDict


# RolBase: campos que comparten Create y Response. A diferencia de
# Usuario, acá no necesitamos ningún model_validator cruzado, porque
# Rol no tiene ninguna regla que compare dos campos entre sí.
class RolBase(BaseModel):
    # nombre: obligatorio. La restricción UNIQUE la garantiza la base
    # de datos; acá solo garantizamos que sea un texto no vacío.
    nombre: str

    # descripcion: opcional, igual que en el modelo de SQLAlchemy.
    descripcion: str | None = None


# RolCreate: no agrega nada sobre RolBase por ahora (a diferencia de
# UsuarioCreate, que sí necesitaba el campo extra "password"). Igual
# la definimos como clase propia, en vez de usar RolBase directamente
# en el endpoint, para que en el futuro sea fácil agregarle algo
# específico de la creación sin tener que reordenar nada.
class RolCreate(RolBase):
    pass


# RolUpdate: actualización parcial, todos los campos opcionales.
class RolUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    activo: bool | None = None


# RolResponse: lo que la API devuelve. Rol no tiene ningún dato
# sensible como password_hash, así que acá no hay nada que excluir
# a propósito — simplemente se agregan los campos que genera el sistema.
class RolResponse(RolBase):
    id: uuid.UUID
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)