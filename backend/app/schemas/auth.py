# backend/app/schemas/auth.py

# BaseModel: clase base de Pydantic para definir la forma de los datos
# que entran y salen de estos endpoints.
# EmailStr: valida formato real de email (ya usamos email-validator
# para UsuarioCreate, así que no hace falta instalar nada nuevo).
# Field: nos permite agregar restricciones extra a un campo puntual.
from pydantic import BaseModel, EmailStr, Field


# LoginEmailRequest: lo que recibe el endpoint de login por email.
# El servicio (no este schema) valida que ese usuario tenga
# tipo_login=EMAIL; acá solo garantizamos la FORMA de los datos.
class LoginEmailRequest(BaseModel):
    email: EmailStr
    # Llega en texto plano por HTTPS; nunca se guarda así, se compara
    # contra el hash existente con verificar_password() en el servicio.
    password: str


# SolicitarCodigoRequest: primer paso del login por teléfono.
# El cliente pide que se le genere un código nuevo para ese número.
class SolicitarCodigoRequest(BaseModel):
    telefono: str


# VerificarCodigoRequest: segundo paso del login por teléfono.
class VerificarCodigoRequest(BaseModel):
    telefono: str
    # pattern: exige exactamente 6 dígitos numéricos, igual que la
    # columna codigo VARCHAR(6) del modelo CodigoVerificacion.
    codigo: str = Field(pattern=r"^\d{6}$")


# MensajeResponse: respuesta del paso "solicitar código".
# Deliberadamente NO confirma si el teléfono existe o no como usuario
# (mismo principio de seguridad ya aplicado en validar_codigo): el
# servicio siempre arma el mismo mensaje, exista o no el usuario detrás.
class MensajeResponse(BaseModel):
    mensaje: str


# TokenResponse: lo que devuelven AMBOS caminos de login si tienen
# éxito. Formato estándar que espera OAuth2/Swagger.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"