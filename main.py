"""
Módulo principal de ejecución de la aplicación.

Este archivo es el punto de entrada para iniciar la aplicación
de Control de Presión Arterial. Se encarga de cargar las variables
de entorno y lanzar la ventana principal.
"""

import sys
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Asegurar que la ruta del proyecto esté en el path del sistema
# para que las importaciones de los módulos locales funcionen correctamente
ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# Importar la ventana principal de la interfaz gráfica
from interfaz.ventana_principal import VentanaPrincipal


def ejecutar_aplicacion():
    """
    Función principal que inicializa y ejecuta la aplicación.
    
    Crea una instancia de la ventana principal y la muestra en pantalla.
    Captura cualquier error inesperado durante la ejecución para evitar
    que la aplicación se cierre de forma abrupta sin mostrar un mensaje.
    """
    try:
        print("Iniciando la aplicación de Control de Presión Arterial...")
        
        # Crear la instancia de la ventana principal
        aplicacion = VentanaPrincipal()
        
        # Iniciar el bucle principal de la interfaz gráfica
        aplicacion.mainloop()
        
    except Exception as error:
        print(f"Ocurrió un error inesperado al ejecutar la aplicación: {error}")
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_aplicacion()