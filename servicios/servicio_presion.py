"""
Módulo del servicio de operaciones para registros de presión arterial.

Este módulo contiene la clase ServicioPresion que maneja todas las
operaciones de lectura, escritura, filtrado y paginación de datos
en la tabla 'presion' de la base de datos PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List
import pandas as pd
import sys
import os

# Agregar la ruta raíz del proyecto al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.base_datos import gestor_bd
from modelos.registro_presion import RegistroPresion


class ServicioPresion:
    """
    Clase que gestiona todas las operaciones con la tabla 'presion'.
    """

    def insertar_registro(self, registro: RegistroPresion) -> RegistroPresion:
        """
        Inserta un nuevo registro de presión arterial en la base de datos.

        Args:
            registro: Objeto RegistroPresion con los datos a insertar.

        Returns:
            RegistroPresion: El mismo objeto con el ID asignado por la base de datos.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO presion
                (presion_fechahora, presion_sistolica, presion_diastolica,
                 presion_pulso, presion_anio, presion_aniomes,
                 presion_aniomessemana, presion_anio_semana,
                 presion_archivoorigen, presion_fechacreacion, presion_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING presion_secuencial
            """, (
                registro.presion_fechahora,
                registro.presion_sistolica,
                registro.presion_diastolica,
                registro.presion_pulso,
                registro.presion_anio,
                registro.presion_aniomes,
                registro.presion_aniomessemana,
                registro.presion_anio_semana,
                registro.presion_archivoorigen,
                registro.presion_fechacreacion,
                registro.presion_estado
            ))

            registro.presion_secuencial = cursor.fetchone()[0]
            conexion.commit()
            return registro

        except Exception as error:
            if conexion:
                conexion.rollback()
            raise error
        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_todos(self) -> List[RegistroPresion]:
        """
        Obtiene todos los registros activos de la tabla 'presion'.

        Returns:
            List[RegistroPresion]: Lista de todos los registros ordenados
            por fecha de manera descendente.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM presion
                WHERE presion_estado = 'Activo'
                ORDER BY presion_fechahora DESC
            """)

            registros_db = cursor.fetchall()
            return [self._convertir_fila_a_registro(fila) for fila in registros_db]

        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def filtrar_registros(self, filtros: dict) -> List[RegistroPresion]:
        """
        Obtiene registros aplicando los filtros especificados.

        Args:
            filtros: Diccionario con los criterios de filtrado.

        Returns:
            List[RegistroPresion]: Lista de registros que cumplen los filtros.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            consulta_sql = "SELECT * FROM presion WHERE presion_estado = 'Activo'"
            parametros = []

            if filtros.get('fecha_inicio') and filtros.get('fecha_fin'):
                consulta_sql += " AND presion_fechahora BETWEEN %s AND %s"
                parametros.extend([filtros['fecha_inicio'], filtros['fecha_fin']])
            if filtros.get('anio_desde'):
                consulta_sql += " AND presion_anio >= %s"
                parametros.append(filtros['anio_desde'])
            if filtros.get('anio_hasta'):
                consulta_sql += " AND presion_anio <= %s"
                parametros.append(filtros['anio_hasta'])
            if filtros.get('aniomes_desde'):
                consulta_sql += " AND presion_aniomes >= %s"
                parametros.append(filtros['aniomes_desde'])
            if filtros.get('aniomes_hasta'):
                consulta_sql += " AND presion_aniomes <= %s"
                parametros.append(filtros['aniomes_hasta'])
            if filtros.get('anio_semana_desde'):
                consulta_sql += " AND presion_anio_semana >= %s"
                parametros.append(filtros['anio_semana_desde'])
            if filtros.get('anio_semana_hasta'):
                consulta_sql += " AND presion_anio_semana <= %s"
                parametros.append(filtros['anio_semana_hasta'])
            if filtros.get('aniomessemana_desde'):
                consulta_sql += " AND presion_aniomessemana >= %s"
                parametros.append(filtros['aniomessemana_desde'])
            if filtros.get('aniomessemana_hasta'):
                consulta_sql += " AND presion_aniomessemana <= %s"
                parametros.append(filtros['aniomessemana_hasta'])

            consulta_sql += " ORDER BY presion_fechahora DESC"

            cursor = conexion.cursor(cursor_factory=RealDictCursor)
            cursor.execute(consulta_sql, parametros)
            registros_db = cursor.fetchall()

            return [self._convertir_fila_a_registro(fila) for fila in registros_db]

        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_valores_anio(self) -> List[int]:
        """
        Obtiene la lista de años únicos disponibles en los registros.

        Returns:
            List[int]: Lista de años ordenados de forma descendente.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT DISTINCT presion_anio FROM presion "
                "WHERE presion_estado = 'Activo' ORDER BY presion_anio DESC"
            )
            return [fila[0] for fila in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_valores_aniomes(self) -> List[int]:
        """
        Obtiene la lista de valores únicos de año-mes disponibles.

        Returns:
            List[int]: Lista de valores año-mes ordenados.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT DISTINCT presion_aniomes FROM presion "
                "WHERE presion_estado = 'Activo' ORDER BY presion_aniomes DESC"
            )
            return [fila[0] for fila in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_valores_anio_semana(self) -> List[int]:
        """
        Obtiene la lista de valores únicos de año-semana disponibles.

        Returns:
            List[int]: Lista de valores año-semana ordenados.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT DISTINCT presion_anio_semana FROM presion "
                "WHERE presion_estado = 'Activo' ORDER BY presion_anio_semana DESC"
            )
            return [fila[0] for fila in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_valores_aniomessemana(self) -> List[int]:
        """
        Obtiene la lista de valores únicos de año-mes-semana disponibles.

        Returns:
            List[int]: Lista de valores año-mes-semana ordenados.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT DISTINCT presion_aniomessemana FROM presion "
                "WHERE presion_estado = 'Activo' ORDER BY presion_aniomessemana DESC"
            )
            return [fila[0] for fila in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def contar_registros(self, filtros: dict = None) -> int:
        """
        Cuenta el total de registros que cumplen con los filtros especificados.

        Args:
            filtros: Diccionario opcional con criterios de filtrado.

        Returns:
            int: Número total de registros que cumplen los criterios.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            consulta_sql = "SELECT COUNT(*) FROM presion WHERE presion_estado = 'Activo'"
            parametros = []

            if filtros:
                if filtros.get('fecha_inicio') and filtros.get('fecha_fin'):
                    consulta_sql += " AND presion_fechahora BETWEEN %s AND %s"
                    parametros.extend([filtros['fecha_inicio'], filtros['fecha_fin']])
                if filtros.get('anio_desde'):
                    consulta_sql += " AND presion_anio >= %s"
                    parametros.append(filtros['anio_desde'])
                if filtros.get('anio_hasta'):
                    consulta_sql += " AND presion_anio <= %s"
                    parametros.append(filtros['anio_hasta'])
                if filtros.get('aniomes_desde'):
                    consulta_sql += " AND presion_aniomes >= %s"
                    parametros.append(filtros['aniomes_desde'])
                if filtros.get('aniomes_hasta'):
                    consulta_sql += " AND presion_aniomes <= %s"
                    parametros.append(filtros['aniomes_hasta'])
                if filtros.get('anio_semana_desde'):
                    consulta_sql += " AND presion_anio_semana >= %s"
                    parametros.append(filtros['anio_semana_desde'])
                if filtros.get('anio_semana_hasta'):
                    consulta_sql += " AND presion_anio_semana <= %s"
                    parametros.append(filtros['anio_semana_hasta'])
                if filtros.get('aniomessemana_desde'):
                    consulta_sql += " AND presion_aniomessemana >= %s"
                    parametros.append(filtros['aniomessemana_desde'])
                if filtros.get('aniomessemana_hasta'):
                    consulta_sql += " AND presion_aniomessemana <= %s"
                    parametros.append(filtros['aniomessemana_hasta'])

            cursor = conexion.cursor()
            cursor.execute(consulta_sql, parametros)
            return cursor.fetchone()[0]

        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def obtener_registros_paginados(
        self,
        pagina: int,
        registros_por_pagina: int,
        filtros: dict = None,
        orden: str = "desc"
    ) -> List[RegistroPresion]:
        """
        Obtiene una página específica de registros con paginación y ordenamiento.

        Args:
            pagina: Número de página a obtener (comienza en 1).
            registros_por_pagina: Cantidad de registros por página.
            filtros: Diccionario opcional con criterios de filtrado.
            orden: Orden de los registros ('asc' o 'desc').

        Returns:
            List[RegistroPresion]: Lista de registros de la página solicitada.
        """
        conexion = None
        cursor = None
        try:
            conexion = gestor_bd.obtener_conexion()
            consulta_sql = "SELECT * FROM presion WHERE presion_estado = 'Activo'"
            parametros = []

            if filtros:
                if filtros.get('fecha_inicio') and filtros.get('fecha_fin'):
                    consulta_sql += " AND presion_fechahora BETWEEN %s AND %s"
                    parametros.extend([filtros['fecha_inicio'], filtros['fecha_fin']])
                if filtros.get('anio_desde'):
                    consulta_sql += " AND presion_anio >= %s"
                    parametros.append(filtros['anio_desde'])
                if filtros.get('anio_hasta'):
                    consulta_sql += " AND presion_anio <= %s"
                    parametros.append(filtros['anio_hasta'])
                if filtros.get('aniomes_desde'):
                    consulta_sql += " AND presion_aniomes >= %s"
                    parametros.append(filtros['aniomes_desde'])
                if filtros.get('aniomes_hasta'):
                    consulta_sql += " AND presion_aniomes <= %s"
                    parametros.append(filtros['aniomes_hasta'])
                if filtros.get('anio_semana_desde'):
                    consulta_sql += " AND presion_anio_semana >= %s"
                    parametros.append(filtros['anio_semana_desde'])
                if filtros.get('anio_semana_hasta'):
                    consulta_sql += " AND presion_anio_semana <= %s"
                    parametros.append(filtros['anio_semana_hasta'])
                if filtros.get('aniomessemana_desde'):
                    consulta_sql += " AND presion_aniomessemana >= %s"
                    parametros.append(filtros['aniomessemana_desde'])
                if filtros.get('aniomessemana_hasta'):
                    consulta_sql += " AND presion_aniomessemana <= %s"
                    parametros.append(filtros['aniomessemana_hasta'])

            # Aplicar ordenamiento
            if orden == "asc":
                consulta_sql += " ORDER BY presion_fechahora ASC"
            else:
                consulta_sql += " ORDER BY presion_fechahora DESC"

            # Agregar LIMIT y OFFSET para paginación
            offset = (pagina - 1) * registros_por_pagina
            consulta_sql += " LIMIT %s OFFSET %s"
            parametros.extend([registros_por_pagina, offset])

            cursor = conexion.cursor(cursor_factory=RealDictCursor)
            cursor.execute(consulta_sql, parametros)
            registros_db = cursor.fetchall()

            return [self._convertir_fila_a_registro(fila) for fila in registros_db]

        finally:
            if cursor:
                cursor.close()
            if conexion:
                gestor_bd.devolver_conexion(conexion)

    def convertir_a_dataframe(self, registros: List[RegistroPresion]) -> pd.DataFrame:
        """
        Convierte una lista de registros de presión a un DataFrame de Pandas.

        Args:
            registros: Lista de objetos RegistroPresion a convertir.

        Returns:
            pd.DataFrame: DataFrame con los datos organizados en columnas.
        """
        datos = []
        for registro in registros:
            datos.append({
                'ID': registro.presion_secuencial,
                'Fecha': registro.presion_fechahora,
                'Sistólica': registro.presion_sistolica,
                'Diastólica': registro.presion_diastolica,
                'Pulso': registro.presion_pulso,
                'Año': registro.presion_anio,
                'Año-Mes': registro.presion_aniomes,
                'Año-Mes-Semana': registro.presion_aniomessemana,
                'Año-Semana': registro.presion_anio_semana,
            })
        return pd.DataFrame(datos)

    def _convertir_fila_a_registro(self, fila) -> RegistroPresion:
        """
        Convierte una fila de la base de datos en un objeto RegistroPresion.

        Args:
            fila: Diccionario con los datos de una fila de la base de datos.

        Returns:
            RegistroPresion: Objeto con los datos convertidos.
        """
        return RegistroPresion(
            presion_secuencial=fila['presion_secuencial'],
            presion_fechahora=fila['presion_fechahora'],
            presion_sistolica=float(fila['presion_sistolica']),
            presion_diastolica=float(fila['presion_diastolica']),
            presion_pulso=float(fila['presion_pulso']),
            presion_anio=fila['presion_anio'],
            presion_aniomes=fila['presion_aniomes'],
            presion_aniomessemana=fila['presion_aniomessemana'],
            presion_anio_semana=fila['presion_anio_semana'],
            presion_archivoorigen=fila['presion_archivoorigen'],
            presion_fechacreacion=fila['presion_fechacreacion'],
            presion_estado=fila['presion_estado'],
        )