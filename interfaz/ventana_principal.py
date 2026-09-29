"""
Módulo de la ventana principal de la aplicación.

Este módulo define la ventana principal de la interfaz gráfica
que permite navegar entre las diferentes secciones de la aplicación:
formulario de ingreso, consulta de datos y gráficos.
"""

import customtkinter as ctk
from tkinter import messagebox

from interfaz.formulario_ingreso import FormularioIngreso
from interfaz.grilla_consulta import GrillaConsulta
from interfaz.grafico_lineas import GraficoLineas
from interfaz.graficos import VentanaGraficos


class VentanaPrincipal(ctk.CTk):
    """
    Clase que representa la ventana principal de la aplicación.
    
    Contiene el menú de navegación lateral y el área de contenido
    donde se muestran las diferentes vistas de la aplicación.
    """
    
    def __init__(self):
        """
        Inicializa la ventana principal configurando su apariencia
        y creando los componentes de la interfaz.
        """
        super().__init__()
        
        # Configuración de la ventana
        self.title("Control de Presión Arterial")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear la interfaz
        self._crear_barra_lateral()
        self._crear_area_contenido()
        
        # Variable para el frame activo
        self.frame_activo = None
        
        # Mostrar el formulario por defecto
        self.mostrar_vista("formulario")
    
    def _crear_barra_lateral(self):
        """
        Crea la barra lateral de navegación con los botones
        para acceder a las diferentes vistas de la aplicación.
        """
        self.barra_lateral = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.barra_lateral.pack(side="left", fill="y", padx=0, pady=0)
        self.barra_lateral.pack_propagate(False)
        
        # Título/Logo
        titulo = ctk.CTkLabel(
            self.barra_lateral,
            text="❤️ Presión\nArterial",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        titulo.pack(pady=30, padx=20)
        
        # Línea separadora
        ctk.CTkFrame(self.barra_lateral, height=2, fg_color="gray").pack(
            pady=10, padx=20, fill="x"
        )
        
        # Botón: Ingresar Datos
        self.btn_formulario = ctk.CTkButton(
            self.barra_lateral,
            text="📝 Ingresar Datos",
            font=ctk.CTkFont(size=14),
            height=45,
            corner_radius=8,
            command=lambda: self.mostrar_vista("formulario")
        )
        self.btn_formulario.pack(pady=8, padx=15, fill="x")
        
        # Botón: Consultar Datos
        self.btn_consulta = ctk.CTkButton(
            self.barra_lateral,
            text="📊 Consultar Datos",
            font=ctk.CTkFont(size=14),
            height=45,
            corner_radius=8,
            command=lambda: self.mostrar_vista("consulta")
        )
        self.btn_consulta.pack(pady=8, padx=15, fill="x")
        
        # Botón: Gráfico de Líneas
        self.btn_lineas = ctk.CTkButton(
            self.barra_lateral,
            text="📈 Gráfico de Líneas",
            font=ctk.CTkFont(size=14),
            height=45,
            corner_radius=8,
            command=lambda: self.mostrar_vista("lineas")
        )
        self.btn_lineas.pack(pady=8, padx=15, fill="x")
        
        # Botón: Gráfico de Frecuencia
        self.btn_frecuencia = ctk.CTkButton(
            self.barra_lateral,
            text="🔢 Gráfico de Frecuencia",
            font=ctk.CTkFont(size=14),
            height=45,
            corner_radius=8,
            command=lambda: self.mostrar_vista("frecuencia")
        )
        self.btn_frecuencia.pack(pady=8, padx=15, fill="x")
        
        # Línea separadora
        ctk.CTkFrame(self.barra_lateral, height=2, fg_color="gray").pack(
            pady=20, padx=20, fill="x"
        )
        
        # Botón: Salir
        self.btn_salir = ctk.CTkButton(
            self.barra_lateral,
            text="🚪 Salir",
            font=ctk.CTkFont(size=14),
            height=45,
            corner_radius=8,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self._cerrar_aplicacion
        )
        self.btn_salir.pack(pady=10, padx=15, fill="x")
    
    def _crear_area_contenido(self):
        """
        Crea el área principal donde se mostrarán las diferentes vistas.
        """
        self.area_contenido = ctk.CTkFrame(self, corner_radius=0)
        self.area_contenido.pack(side="right", fill="both", expand=True)
    
    def mostrar_vista(self, tipo_vista: str):
        """
        Muestra la vista correspondiente según el tipo solicitado.
        """
        if self.frame_activo:
            self.frame_activo.destroy()
        
        if tipo_vista == "formulario":
            self.frame_activo = FormularioIngreso(self.area_contenido)
        elif tipo_vista == "consulta":
            self.frame_activo = GrillaConsulta(self.area_contenido)
        elif tipo_vista == "lineas":
            self.frame_activo = GraficoLineas(self.area_contenido)
        elif tipo_vista == "frecuencia":
            self.frame_activo = VentanaGraficos(self.area_contenido, tipo="frecuencia")
        
        self.frame_activo.pack(fill="both", expand=True, padx=20, pady=20)
        self._actualizar_botones(tipo_vista)

    def _actualizar_botones(self, vista_activa: str):
        """
        Actualiza el color de los botones para resaltar el activo.
        
        Args:
            vista_activa: Nombre de la vista actualmente activa.
        """
        botones = {
            "formulario": self.btn_formulario,
            "consulta": self.btn_consulta,
            "lineas": self.btn_lineas,
            "frecuencia": self.btn_frecuencia,
        }
        
        for vista, boton in botones.items():
            if vista == vista_activa:
                boton.configure(fg_color="#2563eb")
            else:
                boton.configure(fg_color="#3b82f6")
    
    def _cerrar_aplicacion(self):
        """
        Cierra la aplicación liberando todos los recursos,
        incluyendo las conexiones a la base de datos.
        """
        from config.base_datos import gestor_bd
        gestor_bd.cerrar_todo()
        self.destroy()