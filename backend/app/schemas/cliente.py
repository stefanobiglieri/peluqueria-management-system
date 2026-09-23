# backend/app/schemas/cliente.py

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# ClienteCreate: recibe TANTO los datos propios de Cliente como los
# datos de Usuario necesarios para crearlo junto (Opción B ya
# confirmada). email/password y telefono son todos opcionales acá
# porque cuál se usa depende del método de registro elegido — el
# model_validator de abajo exige la combinación correcta.
class ClienteCreate(BaseModel):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    fecha_nacimiento: date | None = None
    observaciones: str | None = None
    acepta_notificaciones: bool = True

    # Datos del Usuario a crear junto con el Cliente.
    email: EmailStr | None = None
    password: str | None = None
    telefono: str | None = None

    @model_validator(mode="after")
    def validar_metodo_de_registro(self):
        """
        Replica, a nivel aplicación, las mismas reglas que ya exige el
        CheckConstraint de Usuario — mismo criterio que UsuarioCreate:
        - Tiene que venir email+password, O telefono (al menos uno).
        - Si viene email, tiene que venir password también.
        """
        if not self.email and not self.telefono:
            raise ValueError("Debe indicarse email o teléfono para registrar al cliente.")
        if self.email and not self.password:
            raise ValueError("Si se registra por email, la contraseña es obligatoria.")
        return self


# ClienteResponse: lo que devuelve la API. Incluye usuario_id para que,
# desde el frontend, se pueda vincular este Cliente con su Usuario si
# hiciera falta (ej. mostrar el email/teléfono de login).
class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    usuario_id: uuid.UUID
    nombre: str
    apellido: str
    fecha_nacimiento: date | None
    observaciones: str | None
    acepta_notificaciones: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# ClienteListItem: igual que ClienteResponse, pero con email/telefono
# agregados — se usa SOLO en el listado, donde ayudan a diferenciar
# clientes con nombre y apellido iguales.
class ClienteListItem(ClienteResponse):
    email: str | None
    telefono: str | None