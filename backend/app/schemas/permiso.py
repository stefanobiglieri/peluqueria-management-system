# backend/app/schemas/permiso.py

# uuid: para tipar el id en el schema de salida.
import uuid

# datetime: para tipar fecha_creacion/fecha_actualizacion en la salida.
from datetime import datetime

# BaseModel: clase base de Pydantic. ConfigDict: para activar
# from_attributes (permite construir el schema leyendo atributos de un
# objeto SQLAlchemy, no solo de un dict). Field: para poner restricciones
# de longitud consistentes con las columnas VARCHAR del modelo.
from pydantic import BaseModel, ConfigDict, Field


# PermisoBase: los campos que SIEMPRE hacen falta para describir un
# permiso, sin importar si es para crear o para mostrar. Evita repetir
# estos tres campos en PermisoCreate y PermisoResponse por separado.
class PermisoBase(BaseModel):
    # max_length=100: coincide con VARCHAR(100) en el modelo. Si alguien
    # manda un nombre más largo, Pydantic lo rechaza con 422 antes de
    # que llegue a intentar insertarse en la base.
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)
    modulo: str = Field(max_length=100)


# PermisoCreate: lo que recibe el endpoint de creación. Por ahora es
# idéntico a PermisoBase (no hace falta pedir "activo": todo permiso
# nuevo nace activo por defecto, según el modelo), pero lo dejamos como
# clase propia por si en el futuro se agrega algún campo exclusivo de
# la creación.
class PermisoCreate(PermisoBase):
    pass


# PermisoUpdate: TODOS los campos opcionales, porque una actualización
# parcial (PATCH) puede mandar solo el campo que se quiere cambiar —
# mismo criterio que UsuarioUpdate.
class PermisoUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)
    modulo: str | None = Field(default=None, max_length=100)
    # activo SÍ se puede actualizar acá: es la forma de desactivar un
    # permiso sin eliminarlo, la regla de negocio ya definida.
    activo: bool | None = None


# PermisoResponse: lo que devuelve la API. Incluye todos los campos
# generados por el sistema (id, fechas, activo) que no tiene sentido
# pedirle al cliente al crear un permiso.
class PermisoResponse(PermisoBase):
    # from_attributes=True: permite hacer
    # PermisoResponse.model_validate(objeto_sqlalchemy) directamente,
    # igual que en UsuarioResponse.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    