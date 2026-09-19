# backend/app/models/__init__.py

# Este archivo se ejecuta automáticamente cuando algo hace "import backend.app.models".
# Su único trabajo es importar cada modelo del proyecto, para que todos queden
# registrados en Base.metadata. Así, Alembic (y cualquier otra parte del sistema)
# puede simplemente hacer "import backend.app.models" una sola vez y automáticamente
# tener disponibles TODOS los modelos existentes, sin tener que acordarse de
# agregarlos uno por uno en cada lugar donde se necesiten.

from backend.app.models.rol import Rol
from backend.app.models.usuario import Usuario
from backend.app.models.codigo_verificacion import CodigoVerificacion
from backend.app.models.permiso import Permiso
from backend.app.models.rol_permiso import RolPermiso