"""
==========================================================
Archivo: db_check.py
Proyecto: Peluquería Management System

Función:
Verifica que SQLAlchemy pueda conectarse correctamente
a PostgreSQL utilizando la configuración del proyecto.

Ejecución recomendada:

python -m backend.app.utils.db_check

No ejecutar directamente el archivo, ya que los imports
absolutos del proyecto requieren ejecutarlo como módulo.

Este archivo se utilizará únicamente para diagnóstico
durante el desarrollo.

No forma parte de la API.
==========================================================
"""

from sqlalchemy import text

from backend.app.database.database import engine


def check_database_connection():
    """
    Verifica la conexión con PostgreSQL.
    """

    try:

        with engine.connect() as connection:

            version = connection.execute(
                text("SELECT version();")
            ).scalar()

            print("\n=====================================")
            print("Conexión exitosa con PostgreSQL")
            print("=====================================")
            print(version)
            print("=====================================\n")

    except Exception as error:

        print("\n=====================================")
        print("ERROR DE CONEXIÓN")
        print("=====================================")
        print(error)
        print("=====================================\n")


if __name__ == "__main__":
    check_database_connection()