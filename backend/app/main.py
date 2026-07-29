from fastapi import FastAPI

from backend.app.core.config import APP_NAME, APP_VERSION
from backend.app.api.routes.health import router as health_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend del Sistema de Gestión para Peluquerías."
)

app.include_router(health_router)
# ==========================================================
# Archivo: main.py
# Proyecto: Peluquería Management System
# Autor: Stefano Biglieri
# Lenguaje: Python 3.13
#
# ----------------------------------------------------------
# DESCRIPCIÓN
# ----------------------------------------------------------
# Este archivo constituye el punto de entrada (Entry Point)
# del backend del sistema.
#
# Su función es crear la aplicación FastAPI e iniciar el
# servidor que responderá todas las solicitudes provenientes
# del frontend.
#
# A medida que el proyecto evolucione, desde este archivo se
# cargarán automáticamente los distintos módulos del sistema,
# como autenticación, usuarios, turnos, servicios, pagos,
# estadísticas y demás funcionalidades.
#
# ----------------------------------------------------------
# FUNCIONAMIENTO
# ----------------------------------------------------------
# 1. Importa la clase FastAPI desde la biblioteca FastAPI.
#
# 2. Importa la configuración general del sistema desde el
#    archivo config.py.
#
# 3. Crea una instancia de la aplicación FastAPI utilizando
#    los datos obtenidos desde el archivo .env.
#
# 4. Registra el primer endpoint del sistema (/), cuya única
#    finalidad es verificar que el servidor funciona
#    correctamente.
#
# 5. Devuelve un mensaje en formato JSON indicando que el
#    backend se encuentra operativo.
#
# ----------------------------------------------------------
# BIBLIOTECAS UTILIZADAS
# ----------------------------------------------------------
# FastAPI
#   Framework moderno para el desarrollo de APIs REST.
#
# app.core.config
#   Módulo propio encargado de cargar la configuración del
#   proyecto desde el archivo .env.
#
# ----------------------------------------------------------
# IMPORTANTE
# ----------------------------------------------------------
# Este archivo siempre será el punto de inicio del backend.
# Su responsabilidad será únicamente iniciar la aplicación y
# registrar los distintos módulos del sistema, evitando
# contener lógica de negocio.
# ==========================================================