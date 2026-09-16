from dotenv import load_dotenv
import os
from pathlib import Path

# Ruta al archivo .env ubicado en backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
DEBUG = os.getenv("DEBUG") == "True"
DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
# ==========================================================
# Archivo: config.py
# Proyecto: Peluquería Management System
# Autor: Stefano Biglieri
# Lenguaje: Python 3.13
#
# ----------------------------------------------------------
# DESCRIPCIÓN
# ----------------------------------------------------------
# Este archivo centraliza toda la configuración del sistema.
#
# Su función consiste en leer el contenido del archivo .env
# y dejar disponibles sus variables para el resto del
# proyecto.
#
# Gracias a esta arquitectura, el código nunca accederá
# directamente al archivo .env, sino que utilizará este
# módulo como intermediario.
#
# ----------------------------------------------------------
# FUNCIONAMIENTO
# ----------------------------------------------------------
# 1. Localiza automáticamente el archivo .env.
#
# 2. Carga todas las variables de configuración mediante la
#    biblioteca python-dotenv.
#
# 3. Convierte dichas variables en información accesible para
#    cualquier módulo del proyecto utilizando os.getenv().
#
# 4. Permite modificar configuraciones sin necesidad de
#    alterar el código fuente.
#
# ----------------------------------------------------------
# BIBLIOTECAS UTILIZADAS
# ----------------------------------------------------------
# python-dotenv
#   Permite cargar automáticamente el archivo .env.
#
# pathlib
#   Facilita el manejo de rutas de forma compatible entre
#   Windows, Linux y macOS.
#
# os
#   Permite acceder a las variables de entorno del sistema.
#
# ----------------------------------------------------------
# IMPORTANTE
# ----------------------------------------------------------
# Toda configuración general del proyecto deberá agregarse
# primero al archivo .env y luego exponerse mediante este
# módulo.
#
# Ningún otro archivo deberá acceder directamente al .env.
# ==========================================================