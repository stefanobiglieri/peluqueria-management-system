"""
==========================================================
Archivo: health.py
Ubicación: backend/app/schemas/

Función:
Define el Schema utilizado por el endpoint Health.

Un Schema describe la estructura que tendrán los datos
intercambiados por la API.

En este caso representa la respuesta enviada cuando se
verifica el estado del servidor.
==========================================================
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Respuesta estándar del endpoint Health.
    """

    success: bool
    message: str
    data: dict | None = None