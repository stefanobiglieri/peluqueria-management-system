# backend/app/schemas/rol_permiso.py

# uuid: para tipar el permiso_id que recibe el endpoint de asignación.
import uuid

from pydantic import BaseModel


# AsignarPermisoRequest: lo único que hace falta en el body para asignar
# un permiso — el rol_id ya viene en la URL (/roles/{rol_id}/permisos),
# no tiene sentido repetirlo también en el body.
class AsignarPermisoRequest(BaseModel):
    permiso_id: uuid.UUID