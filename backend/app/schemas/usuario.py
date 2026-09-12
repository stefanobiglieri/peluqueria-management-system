# uuid: lo usamos para tipar el campo "id" en el esquema de respuesta,
# igual que en el modelo de SQLAlchemy.
import uuid

# datetime: para tipar los campos de fecha en el esquema de respuesta.
from datetime import datetime

# BaseModel: la clase base de la que heredan todos los esquemas de Pydantic.
# ConfigDict: permite configurar el comportamiento de un esquema (lo vamos a usar
# para que UsuarioResponse pueda leer datos directamente desde un objeto de
# SQLAlchemy, no solo desde un diccionario).
# EmailStr: tipo especial que valida que el texto tenga formato de email real.
# model_validator: decorador para escribir una validación que compara
# VARIOS campos entre sí (no alcanza con validar cada campo por separado).
from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

# Reutilizamos el mismo Enum que ya definimos en el modelo de SQLAlchemy,
# en vez de escribirlo de nuevo acá. Así, si en el futuro se agrega un tercer
# tipo de login, se cambia en un solo lugar y ambas capas quedan sincronizadas.
from backend.app.models.usuario import TipoLogin


# UsuarioBase: contiene los campos que SIEMPRE están presentes al hablar
# de un Usuario, sin importar si estamos creando, actualizando o devolviendo uno.
# Create y Response van a heredar de acá para no repetir estos campos dos veces.
class UsuarioBase(BaseModel):
    # rol_id: qué rol se le asigna. Lo pedimos como UUID; FastAPI/Pydantic
    # van a rechazar automáticamente cualquier valor que no tenga forma de UUID válido.
    rol_id: uuid.UUID

    # email: opcional (puede no venir, si el login es por teléfono).
    # "| None" + "= None" es la forma de Pydantic v2 de decir "este campo
    # puede omitirse por completo o venir como None".
    # EmailStr valida el formato real, gracias a la librería que instalamos recién.
    email: EmailStr | None = None

    # telefono: mismo criterio que email, pero como texto simple
    # (no existe un tipo "PhoneStr" estándar en Pydantic).
    telefono: str | None = None

    # tipo_login: obligatorio siempre. Al tipar con el Enum, Pydantic solo
    # va a aceptar exactamente "EMAIL" o "TELEFONO", rechazando cualquier otro texto.
    tipo_login: TipoLogin


# UsuarioCreate: lo que se necesita para crear un usuario nuevo.
# Hereda todos los campos de UsuarioBase, y agrega "password".
class UsuarioCreate(UsuarioBase):
    # password: la contraseña en TEXTO PLANO que escribe la persona al registrarse.
    # Ojo: esto nunca se guarda así en la base de datos — este campo existe
    # solo para transportar el dato desde el cliente hasta el backend.
    # La conversión a password_hash (con hashing real) va a pasar en la capa
    # de servicio, que todavía no escribimos. Es opcional acá porque, si el
    # login es por TELEFONO, no hace falta que la persona envíe ninguna.
    password: str | None = None

    # model_validator(mode="after"): se ejecuta DESPUÉS de que Pydantic ya
    # validó cada campo por separado (que rol_id sea un UUID válido, que
    # tipo_login sea EMAIL o TELEFONO, etc.). Acá comparamos varios campos
    # entre sí, replicando en la aplicación las mismas dos reglas que ya
    # están garantizadas por los CheckConstraint en la base de datos —
    # así el error se detecta acá, con un mensaje claro, antes de siquiera
    # intentar guardar nada.
    @model_validator(mode="after")
    def validar_reglas_de_login(self) -> "UsuarioCreate":
        # Regla 1: si el login es por email, la contraseña es obligatoria.
        if self.tipo_login == TipoLogin.EMAIL and not self.password:
            raise ValueError(
                "La contraseña es obligatoria cuando el tipo de login es EMAIL."
            )

        # Regla 2: tiene que haber al menos un dato de contacto para loguearse.
        if not self.email and not self.telefono:
            raise ValueError(
                "Debe informarse al menos un email o un teléfono."
            )

        # Si pasó ambas validaciones, devolvemos el propio objeto sin cambios.
        # model_validator siempre debe devolver la instancia (self) al final.
        return self


# UsuarioUpdate: pensado para una actualización PARCIAL (por ejemplo,
# cambiar solo el teléfono de un usuario existente, sin tener que reenviar
# todos los demás datos). Por eso TODOS los campos son opcionales acá,
# a diferencia de UsuarioBase.
# Nota: a propósito NO repetimos la validación cruzada de UsuarioCreate.
# Validar una actualización parcial es más complejo (habría que comparar
# contra los datos que la persona YA tiene guardados, no solo contra lo que
# envía en este pedido puntual). Lo vamos a resolver cuando escribamos la
# lógica del servicio de actualización, no acá en el esquema.
class UsuarioUpdate(BaseModel):
    rol_id: uuid.UUID | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    tipo_login: TipoLogin | None = None
    password: str | None = None
    activo: bool | None = None
    bloqueado: bool | None = None


# UsuarioResponse: lo que la API devuelve al consultar un usuario.
# Hereda de UsuarioBase (rol_id, email, telefono, tipo_login) y agrega
# los campos que genera el propio sistema. A propósito, NO incluye
# "password" ni "password_hash" — nunca deben salir de la base de datos
# hacia afuera, ni siquiera hacia el dueño de la cuenta.
class UsuarioResponse(UsuarioBase):
    id: uuid.UUID
    activo: bool
    bloqueado: bool
    ultimo_acceso: datetime | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    # model_config con from_attributes=True: le dice a Pydantic que este
    # esquema puede construirse directamente a partir de un objeto de
    # SQLAlchemy (ej. una instancia de la clase Usuario), leyendo sus
    # atributos (usuario.id, usuario.email, etc.), en vez de exigir
    # que le pasemos un diccionario armado a mano. Es imprescindible
    # para que, más adelante, un endpoint pueda simplemente devolver
    # el objeto que le llega de la base de datos y que FastAPI lo
    # convierta solo a este esquema.
    model_config = ConfigDict(from_attributes=True)