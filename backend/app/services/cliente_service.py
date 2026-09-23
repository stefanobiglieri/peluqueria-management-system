# backend/app/services/cliente_service.py

import uuid

from sqlalchemy.orm import Session

from backend.app.repositories import usuario_repository, cliente_repository as repository
from backend.app.services import usuario_service
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import TipoLogin
from backend.app.schemas.cliente import ClienteCreate
from backend.app.schemas.usuario import UsuarioCreate
from backend.app.core.exceptions import BusinessException, NotFoundException

# ID fijo del rol "Cliente". No lo buscamos por nombre en cada request
# para evitar una consulta extra en la operación más usada del sistema
# (el auto-registro). Si en algún momento se recrea la base de datos,
# este valor deberá actualizarse — está aislado en una sola constante
# a propósito, para que ese ajuste sea de una sola línea.
ROL_CLIENTE_ID = uuid.UUID("5e96e75f-df9a-4822-ba92-9e8666b61d8b")


def crear_cliente(db: Session, datos: ClienteCreate) -> Cliente:
    """
    Crea un Usuario y su Cliente asociado en una única transacción
    (Opción B ya confirmada): si cualquiera de los dos pasos falla,
    ninguno de los dos queda guardado.
    """
    # Determinamos el tipo_login según qué haya mandado el cliente,
    # validado ya por ClienteCreate.validar_metodo_de_registro().
    tipo_login = TipoLogin.EMAIL if datos.email else TipoLogin.TELEFONO

    datos_usuario = UsuarioCreate(
        rol_id=ROL_CLIENTE_ID,
        email=datos.email,
        telefono=datos.telefono,
        tipo_login=tipo_login,
        password=datos.password,
    )

    # _construir_usuario(): valida duplicados y arma el objeto, SIN
    # guardar todavía (ver usuario_service.py).
    nuevo_usuario = usuario_service._construir_usuario(db, datos_usuario)

    # usuario_repository.crear(): hace flush(), no commit() (ver
    # usuario_repository.py) — el Usuario ya existe dentro de la
    # transacción, pero todavía se podría revertir todo.
    usuario = usuario_repository.crear(db, nuevo_usuario)

    nuevo_cliente = Cliente(
        usuario_id=usuario.id,
        nombre=datos.nombre,
        apellido=datos.apellido,
        fecha_nacimiento=datos.fecha_nacimiento,
        observaciones=datos.observaciones,
        acepta_notificaciones=datos.acepta_notificaciones,
    )

    # cliente_repository.crear(): mismo criterio, flush() sin commit().
    cliente = repository.crear(db, nuevo_cliente)

    # Recién ACÁ, con ambas filas ya insertadas dentro de la misma
    # transacción sin errores, confirmamos todo junto.
    db.commit()
    db.refresh(cliente)

    return cliente


def obtener_cliente(db: Session, cliente_id: uuid.UUID) -> Cliente:
    cliente = repository.obtener_por_id(db, cliente_id)
    if cliente is None:
        raise NotFoundException(f"No existe un cliente con id {cliente_id}.")
    return cliente


def listar_clientes(
    db: Session, skip: int = 0, limit: int = 100, busqueda: str | None = None
) -> list[tuple[Cliente, str | None, str | None]]:
    return repository.listar_con_contacto(db, skip=skip, limit=limit, busqueda=busqueda)