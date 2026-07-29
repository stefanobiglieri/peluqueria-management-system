"""
==========================================================
Archivo: responses.py
Proyecto: Peluquería Management System

Función:
Centraliza la generación de respuestas del backend.

Objetivos:

- Mantener un formato uniforme en toda la API.
- Evitar repetir código.
- Facilitar el mantenimiento del proyecto.
- Permitir que el frontend siempre reciba respuestas
  con la misma estructura.

En el futuro todas las rutas utilizarán estas funciones.
==========================================================
"""

from fastapi.responses import JSONResponse


def success_response(message: str, data=None, status_code: int = 200):
    """
    Genera una respuesta exitosa.

    Parámetros
    ----------
    message : str
        Mensaje descriptivo.

    data : any
        Información adicional.

    status_code : int
        Código HTTP.

    Retorna
    -------
    JSONResponse
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )


def error_response(message: str, status_code: int = 400):
    """
    Genera una respuesta de error.

    Parámetros
    ----------
    message : str

    status_code : int

    Retorna
    -------
    JSONResponse
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message
        }
    )