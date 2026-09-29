"""
Módulo de configuración de la base de datos.

Este módulo maneja la conexión a PostgreSQL utilizando un pool de conexiones
para optimizar el rendimiento y evitar problemas de concurrencia.
"""

import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()


class GestorBaseDatos:
    """
    Clase que gestiona la configuración y conexiones a la base de datos PostgreSQL.
    
    Esta clase implementa un patrón de pool de conexiones para reutilizar
    las conexiones y mejorar el rendimiento de la aplicación.
    """
    
    def __init__(self):
        """
        Inicializa la configuración de la base de datos.
        """
        self.parametros_db = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', ''),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': os.getenv('DB_PORT', '5432'),
        }
        self.pool_conexiones = None
    
    def obtener_conexion(self):
        """
        Obtiene una conexión del pool de conexiones.
        """
        if self.pool_conexiones is None:
            self.pool_conexiones = psycopg2.pool.SimpleConnectionPool(
                1, 10, **self.parametros_db
            )
        return self.pool_conexiones.getconn()
    
    def devolver_conexion(self, conexion):
        """
        Devuelve una conexión al pool para su reutilización.
        """
        if self.pool_conexiones:
            self.pool_conexiones.putconn(conexion)
    
    def cerrar_todo(self):
        """
        Cierra todas las conexiones del pool.
        """
        if self.pool_conexiones:
            self.pool_conexiones.closeall()


# ⚠️ ESTA LÍNEA ES LA QUE FALTA - Debe estar al final del archivo
gestor_bd = GestorBaseDatos()