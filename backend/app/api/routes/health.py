# ==========================================================
# Archivo: health.py
# Proyecto: Peluquería Management System
#
# Función:
# Contiene los endpoints utilizados para verificar el estado
# de funcionamiento del backend.
#
# En futuras versiones podrán agregarse verificaciones de
# conexión con PostgreSQL, Redis, Mercado Pago y otros
# servicios externos.
# ==========================================================

from fastapi import APIRouter
from backend.app.utils.responses import success_response

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"]
)

@router.get("/")
def health():
    """
    Endpoint utilizado para verificar que la API se encuentra operativa.

    Returns
    -------
    JSONResponse
        Respuesta estandarizada indicando que el backend funciona correctamente.
    """

    return success_response(
        message="Backend funcionando correctamente."
    )