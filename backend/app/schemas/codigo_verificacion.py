# uuid: para tipar "id" y "usuario_id".
import uuid

# datetime: para tipar los campos de fecha.
from datetime import datetime

# BaseModel y ConfigDict: igual que en los esquemas anteriores.
from pydantic import BaseModel, ConfigDict

# Reutilizamos el Enum ya definido en el modelo, mismo criterio que
# aplicamos con TipoLogin en el esquema de Usuario.
from backend.app.models.codigo_verificacion import Canal


# CodigoVerificacionResponse: no hereda de ninguna "Base" propia,
# porque no existe ningún esquema de entrada del cual compartir campos
# (a diferencia de Usuario y Rol). Se define directo con todos los
# campos que tiene sentido leer.
class CodigoVerificacionResponse(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    canal: Canal
    utilizado: bool
    expiracion: datetime
    fecha_creacion: datetime

    # Notá que, a propósito, NO incluimos el campo "codigo" acá.
    # Aunque hoy esta entidad no se expone por HTTP, si en el futuro
    # se arma una pantalla interna de administración que liste estos
    # registros, tampoco debería mostrar el código en sí — ver el
    # código no debería servirle a nadie que no sea el propio usuario
    # que lo recibió por SMS/WhatsApp.

    model_config = ConfigDict(from_attributes=True)