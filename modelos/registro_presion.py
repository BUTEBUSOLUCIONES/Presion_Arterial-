"""
Módulo del modelo de datos para registros de presión arterial.

Define la clase que representa cada medición de presión arterial
con todos sus atributos correspondientes a la tabla 'presion'.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RegistroPresion:
    """
    Clase que representa un registro de presión arterial.
    
    Corresponde exactamente a la estructura de la tabla 'presion'
    en la base de datos PostgreSQL.
    
    Atributos:
        presion_secuencial: Identificador único del registro (autoincremental)
        presion_fechahora: Fecha y hora de la medición
        presion_sistolica: Valor de la presión sistólica (mmHg)
        presion_diastolica: Valor de la presión diastólica (mmHg)
        presion_pulso: Valor del pulso cardíaco (latidos por minuto)
        presion_anio: Año de la medición (ej: 2024)
        presion_aniomes: Año y mes combinados (ej: 202401 para enero 2024)
        presion_aniomessemana: Año, mes y semana del mes (ej: 2024011)
        presion_anio_semana: Año y semana del año (ej: 202401)
        presion_archivoorigen: Origen del registro (ej: 'desktop-app')
        presion_fechacreacion: Fecha de creación del registro
        presion_estado: Estado del registro ('Activo' o 'Inactivo')
    """
    
    presion_secuencial: Optional[int] = None
    presion_fechahora: Optional[datetime] = None
    presion_sistolica: float = 0.0
    presion_diastolica: float = 0.0
    presion_pulso: float = 0.0
    presion_anio: int = 0
    presion_aniomes: int = 0
    presion_aniomessemana: int = 0
    presion_anio_semana: int = 0
    presion_archivoorigen: str = 'desktop-app'
    presion_fechacreacion: Optional[datetime] = None
    presion_estado: str = 'Activo'
    
    def a_diccionario(self):
        """
        Convierte el objeto RegistroPresion a un diccionario.
        
        Returns:
            dict: Diccionario con todos los atributos del registro.
        """
        return {
            'presion_secuencial': self.presion_secuencial,
            'presion_fechahora': self.presion_fechahora,
            'presion_sistolica': self.presion_sistolica,
            'presion_diastolica': self.presion_diastolica,
            'presion_pulso': self.presion_pulso,
            'presion_anio': self.presion_anio,
            'presion_aniomes': self.presion_aniomes,
            'presion_aniomessemana': self.presion_aniomessemana,
            'presion_anio_semana': self.presion_anio_semana,
            'presion_archivoorigen': self.presion_archivoorigen,
            'presion_fechacreacion': self.presion_fechacreacion,
            'presion_estado': self.presion_estado,
        }
    
    def __str__(self):
        """
        Representación en texto del registro.
        
        Returns:
            str: Cadena con la información principal del registro.
        """
        return (f"Presión: {self.presion_sistolica}/{self.presion_diastolica} "
                f"mmHg, Pulso: {self.presion_pulso} lpm, "
                f"Fecha: {self.presion_fechahora}")