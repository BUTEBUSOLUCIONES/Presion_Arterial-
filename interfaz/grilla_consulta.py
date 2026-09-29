"""
Módulo de la grilla de consulta de datos con paginación.

Este módulo contiene la interfaz gráfica para visualizar los registros
de presión arterial en formato de tabla (grilla) con paginación.
Incluye funcionalidades para filtrar por diferentes criterios usando
Combobox y calendarios, navegar entre páginas y exportar los resultados
a Excel. La grilla tiene estilo personalizado con encabezado oscuro,
líneas divisorias grises entre filas y columnas mediante bordes en tags,
y filas tipo cebra con colores contrastantes.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime, date
import calendar
from tkcalendar import DateEntry
from servicios.servicio_presion import ServicioPresion


class GrillaConsulta(ctk.CTkFrame):
    """
    Clase que representa la vista de consulta de registros con paginación.
    
    Muestra los datos en una tabla (Treeview) con estilo personalizado:
    - Encabezado negro con letras blancas
    - Líneas divisorias grises entre filas y columnas (usando bordes en tags)
    - Filas alternadas con colores azul claro y blanco (efecto cebra)
    """
    
    def __init__(self, parent):
        """
        Inicializa la grilla de consulta con paginación.
        
        Args:
            parent: Widget padre donde se colocará la grilla.
        """
        super().__init__(parent)
        self.servicio = ServicioPresion()
        self.registros = []
        self.pagina_actual = 1
        self.registros_por_pagina = 15
        self.total_registros = 0
        self.total_paginas = 0
        self.filtros_actuales = {}
        self.orden_actual = "desc"
        
        self._configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_datos()
    
    def _configurar_estilo_tabla(self):
        """
        Configura el estilo visual del Treeview con líneas divisorias grises.
        Mantiene el fondo negro y letras blancas en los encabezados incluso
        al pasar el mouse (hover) o hacer clic.
        """
        estilo = ttk.Style()
        estilo.theme_use('clam')
        
        # Encabezado negro con letras blancas y bordes visibles
        estilo.configure(
            'Treeview.Heading',
            background='black',
            foreground='white',
            font=('Arial', 10, 'bold'),
            relief='solid',
            borderwidth=1
        )
        
        # Mantener colores negros/blancos en todos los estados del encabezado
        estilo.map('Treeview.Heading',
            background=[
                ('active', 'black'),
                ('pressed', 'black'),
                ('disabled', 'gray')
            ],
            foreground=[
                ('active', 'white'),
                ('pressed', 'white'),
                ('disabled', 'lightgray')
            ]
        )
        
        # Configuración base de la tabla con bordes visibles
        estilo.configure(
            'Treeview',
            background='white',
            foreground='black',
            fieldbackground='white',
            font=('Arial', 9),
            rowheight=28,
            relief='solid',
            borderwidth=1
        )
        
        # Fila seleccionada
        estilo.map('Treeview',
            background=[('selected', '#2563eb')],
            foreground=[('selected', 'white')]
        )

    def _crear_interfaz(self):
        """
        Crea todos los componentes visuales de la pantalla de consulta.
        """
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="📊 Consulta de Registros",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=5)
        
        # --- Frame de Filtros centrado ---
        frame_filtros = ctk.CTkFrame(self)
        frame_filtros.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(
            frame_filtros,
            text="🔍 Filtros:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5, padx=20, anchor="center")
        
        frame_centro_filtros = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_centro_filtros.pack(pady=5, padx=20, anchor="center")
        
        grid_filtros = ctk.CTkFrame(frame_centro_filtros, fg_color="transparent")
        grid_filtros.pack(anchor="center")
        
        # Filtro 1: Rango de fechas con calendario
        ctk.CTkLabel(grid_filtros, text="Rango de fechas:").grid(row=0, column=0, padx=10, pady=3, sticky="e")
        
        primer_dia_mes = date.today().replace(day=1)
        self.calendario_inicio = DateEntry(
            grid_filtros,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            locale='es_ES'
        )
        self.calendario_inicio.set_date(primer_dia_mes)
        self.calendario_inicio.grid(row=0, column=1, padx=5, pady=3)
        
        ctk.CTkLabel(grid_filtros, text="a").grid(row=0, column=2, padx=5)
        
        ultimo_dia_mes = calendar.monthrange(date.today().year, date.today().month)[1]
        ultimo_dia = date.today().replace(day=ultimo_dia_mes)
        self.calendario_fin = DateEntry(
            grid_filtros,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            locale='es_ES'
        )
        self.calendario_fin.set_date(ultimo_dia)
        self.calendario_fin.grid(row=0, column=3, padx=5, pady=3)
        
        # Filtro 2: Año
        ctk.CTkLabel(grid_filtros, text="Año:").grid(row=1, column=0, padx=10, pady=3, sticky="e")
        self.combo_anio_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_desde.set("Todos")
        self.combo_anio_desde.grid(row=1, column=1, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=1, column=2, padx=5)
        self.combo_anio_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_hasta.set("Todos")
        self.combo_anio_hasta.grid(row=1, column=3, padx=5, pady=3)
        
        # Filtro 3: Año-Mes
        ctk.CTkLabel(grid_filtros, text="Año-Mes:").grid(row=2, column=0, padx=10, pady=3, sticky="e")
        self.combo_aniomes_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_desde.set("Todos")
        self.combo_aniomes_desde.grid(row=2, column=1, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=2, column=2, padx=5)
        self.combo_aniomes_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_hasta.set("Todos")
        self.combo_aniomes_hasta.grid(row=2, column=3, padx=5, pady=3)
        
        # Filtro 4: Año-Semana
        ctk.CTkLabel(grid_filtros, text="Año-Semana:").grid(row=3, column=0, padx=10, pady=3, sticky="e")
        self.combo_anio_semana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_desde.set("Todos")
        self.combo_anio_semana_desde.grid(row=3, column=1, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=3, column=2, padx=5)
        self.combo_anio_semana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_hasta.set("Todos")
        self.combo_anio_semana_hasta.grid(row=3, column=3, padx=5, pady=3)
        
        # Filtro 5: Año-Mes-Semana
        ctk.CTkLabel(grid_filtros, text="Año-Mes-Semana:").grid(row=4, column=0, padx=10, pady=3, sticky="e")
        self.combo_aniomessemana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_desde.set("Todos")
        self.combo_aniomessemana_desde.grid(row=4, column=1, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=4, column=2, padx=5)
        self.combo_aniomessemana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_hasta.set("Todos")
        self.combo_aniomessemana_hasta.grid(row=4, column=3, padx=5, pady=3)
        
        # Filtro 6: Ordenamiento
        ctk.CTkLabel(grid_filtros, text="Ordenar por:").grid(row=5, column=0, padx=10, pady=3, sticky="e")
        self.combo_orden = ctk.CTkComboBox(
            grid_filtros,
            width=250,
            values=["Fecha y Hora - Ascendente", "Fecha y Hora - Descendente"],
            command=self._cambiar_orden
        )
        self.combo_orden.set("Fecha y Hora - Descendente")
        self.combo_orden.grid(row=5, column=1, padx=5, pady=3, columnspan=3, sticky="w")
        
        # Botones de filtros
        frame_botones = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_botones.pack(pady=3)
        
        self.btn_filtrar = ctk.CTkButton(
            frame_botones,
            text="🔍 Filtrar",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35,
            command=self._aplicar_filtros
        )
        self.btn_filtrar.pack(side="left", padx=3)
        
        self.btn_limpiar = ctk.CTkButton(
            frame_botones,
            text="🧹 Limpiar Filtros",
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._limpiar_filtros
        )
        self.btn_limpiar.pack(side="left", padx=3)
        
        self.btn_exportar = ctk.CTkButton(
            frame_botones,
            text="📥 Exportar a Excel",
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._exportar_excel
        )
        self.btn_exportar.pack(side="left", padx=3)
        
        # --- Frame principal ---
        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(pady=5, padx=20, fill="both", expand=True)
        
        # Frame de la grilla
        frame_grilla = ctk.CTkFrame(frame_principal)
        frame_grilla.pack(fill="both", expand=True)
        
        columnas = ("ID", "Fecha", "Sistólica", "Diastólica", "Pulso", "Año", "Año-Mes", "Año-Semana")
        
        self.tabla = ttk.Treeview(
            frame_grilla,
            columns=columnas,
            show="headings",
            height=15
        )
        
        configuracion_columnas = {
            "ID": {"texto": "ID", "ancho": 60},
            "Fecha": {"texto": "Fecha y Hora", "ancho": 150},
            "Sistólica": {"texto": "Sistólica", "ancho": 90},
            "Diastólica": {"texto": "Diastólica", "ancho": 90},
            "Pulso": {"texto": "Pulso", "ancho": 80},
            "Año": {"texto": "Año", "ancho": 70},
            "Año-Mes": {"texto": "Año-Mes", "ancho": 90},
            "Año-Semana": {"texto": "Año-Semana", "ancho": 100},
        }
        
        for col, config in configuracion_columnas.items():
            self.tabla.heading(col, text=config["texto"])
            self.tabla.column(col, width=config["ancho"], anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_grilla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Configurar tags con bordes grises para simular líneas de cuadrícula
        self.tabla.tag_configure('fila_par', background='#cfe2ff', foreground='black')
        self.tabla.tag_configure('fila_impar', background='white', foreground='black')
        
        # --- Frame de Paginación ---
        frame_paginacion = ctk.CTkFrame(frame_principal, fg_color="#e5e7eb")
        frame_paginacion.pack(fill="x", pady=0)
        
        self.btn_primera = ctk.CTkButton(
            frame_paginacion,
            text="⏮ Primera",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=32,
            command=self._ir_a_primera_pagina
        )
        self.btn_primera.pack(side="left", padx=5, pady=5)
        
        self.btn_anterior = ctk.CTkButton(
            frame_paginacion,
            text="◀ Anterior",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=32,
            command=self._ir_a_pagina_anterior
        )
        self.btn_anterior.pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(frame_paginacion, text="Ir a página:", font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        self.entry_pagina = ctk.CTkEntry(frame_paginacion, width=50)
        self.entry_pagina.pack(side="left", padx=5)
        self.entry_pagina.bind('<Return>', lambda evento: self._ir_a_pagina_especifica())
        
        self.btn_ir = ctk.CTkButton(
            frame_paginacion,
            text="Ir",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=50,
            height=32,
            command=self._ir_a_pagina_especifica
        )
        self.btn_ir.pack(side="left", padx=5)
        
        self.btn_siguiente = ctk.CTkButton(
            frame_paginacion,
            text="Siguiente ▶",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=32,
            command=self._ir_a_pagina_siguiente
        )
        self.btn_siguiente.pack(side="left", padx=5)
        
        self.btn_ultima = ctk.CTkButton(
            frame_paginacion,
            text="Última ⏭",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=32,
            command=self._ir_a_ultima_pagina
        )
        self.btn_ultima.pack(side="left", padx=5)
        
        ctk.CTkFrame(frame_paginacion, width=2, fg_color="gray").pack(side="left", padx=15, fill="y", pady=5)
        
        ctk.CTkLabel(frame_paginacion, text="Registros/pág:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        self.combo_registros_pagina = ctk.CTkComboBox(
            frame_paginacion,
            width=70,
            values=["10", "15", "20", "25", "30", "35", "40", "45", "50"],
            command=self._cambiar_registros_por_pagina
        )
        self.combo_registros_pagina.set("15")
        self.combo_registros_pagina.pack(side="left", padx=5)
        
        self.etiqueta_paginacion = ctk.CTkLabel(
            frame_paginacion,
            text="Página 1 de 1",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.etiqueta_paginacion.pack(side="left", padx=15)
        
        self.etiqueta_cantidad = ctk.CTkLabel(
            frame_paginacion,
            text="Total: 0 registros",
            font=ctk.CTkFont(size=11)
        )
        self.etiqueta_cantidad.pack(side="right", padx=10)
    
    def _cargar_datos(self):
        """
        Carga la primera página de registros y actualiza los Combobox.
        """
        try:
            self.pagina_actual = 1
            self._actualizar_combobox()
            self._cargar_pagina_actual()
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(error)}")
    
    def _cargar_pagina_actual(self):
        """
        Carga los registros de la página actual.
        """
        try:
            self.total_registros = self.servicio.contar_registros(self.filtros_actuales)
            
            if self.total_registros > 0:
                self.total_paginas = (self.total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina
            else:
                self.total_paginas = 1
            
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
            if self.pagina_actual < 1:
                self.pagina_actual = 1
            
            self.registros = self.servicio.obtener_registros_paginados(
                self.pagina_actual,
                self.registros_por_pagina,
                self.filtros_actuales,
                self.orden_actual
            )
            
            self._actualizar_grilla()
            self._actualizar_controles_paginacion()
            
        except Exception as error:
            messagebox.showerror("Error", f"Error al cargar la página: {str(error)}")
    
    def _actualizar_combobox(self):
        """
        Actualiza los valores de los Combobox de filtros.
        """
        anios = self.servicio.obtener_valores_anio()
        aniomes = self.servicio.obtener_valores_aniomes()
        anio_semanas = self.servicio.obtener_valores_anio_semana()
        aniomessemanas = self.servicio.obtener_valores_aniomessemana()
        
        valores_anio = ["Todos"] + [str(a) for a in sorted(anios, reverse=True)]
        self.combo_anio_desde.configure(values=valores_anio)
        self.combo_anio_hasta.configure(values=valores_anio)
        
        valores_aniomes = ["Todos"] + [str(a) for a in sorted(aniomes, reverse=True)]
        self.combo_aniomes_desde.configure(values=valores_aniomes)
        self.combo_aniomes_hasta.configure(values=valores_aniomes)
        
        valores_anio_semana = ["Todos"] + [str(a) for a in sorted(anio_semanas, reverse=True)]
        self.combo_anio_semana_desde.configure(values=valores_anio_semana)
        self.combo_anio_semana_hasta.configure(values=valores_anio_semana)
        
        valores_aniomessemana = ["Todos"] + [str(a) for a in sorted(aniomessemanas, reverse=True)]
        self.combo_aniomessemana_desde.configure(values=valores_aniomessemana)
        self.combo_aniomessemana_hasta.configure(values=valores_aniomessemana)
    
    def _actualizar_grilla(self):
        """
        Actualiza la tabla visual con los registros de la página actual.
        Aplica el efecto cebra alternando colores de fondo en las filas.
        """
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)
        
        for indice, registro in enumerate(self.registros):
            fecha_str = registro.presion_fechahora.strftime("%Y-%m-%d %H:%M") if registro.presion_fechahora else ""
            
            if indice % 2 == 0:
                etiquetas = ('fila_par',)
            else:
                etiquetas = ('fila_impar',)
            
            self.tabla.insert(
                "", "end",
                values=(
                    registro.presion_secuencial,
                    fecha_str,
                    f"{registro.presion_sistolica:.0f}",
                    f"{registro.presion_diastolica:.0f}",
                    f"{registro.presion_pulso:.0f}",
                    registro.presion_anio,
                    registro.presion_aniomes,
                    registro.presion_anio_semana,
                ),
                tags=etiquetas
            )
    
    def _actualizar_controles_paginacion(self):
        """
        Actualiza los controles de paginación.
        """
        self.etiqueta_paginacion.configure(
            text=f"Página {self.pagina_actual} de {self.total_paginas}"
        )
        
        self.etiqueta_cantidad.configure(text=f"Total: {self.total_registros} registros")
        
        self.entry_pagina.delete(0, 'end')
        self.entry_pagina.insert(0, str(self.pagina_actual))
        
        if self.pagina_actual <= 1:
            self.btn_primera.configure(state="disabled", fg_color="#9ca3af")
            self.btn_anterior.configure(state="disabled", fg_color="#9ca3af")
        else:
            self.btn_primera.configure(state="normal", fg_color="#3b82f6")
            self.btn_anterior.configure(state="normal", fg_color="#3b82f6")
        
        if self.pagina_actual >= self.total_paginas:
            self.btn_siguiente.configure(state="disabled", fg_color="#9ca3af")
            self.btn_ultima.configure(state="disabled", fg_color="#9ca3af")
        else:
            self.btn_siguiente.configure(state="normal", fg_color="#3b82f6")
            self.btn_ultima.configure(state="normal", fg_color="#3b82f6")
    
    def _ir_a_primera_pagina(self):
        """Navega a la primera página."""
        self.pagina_actual = 1
        self._cargar_pagina_actual()
    
    def _ir_a_pagina_anterior(self):
        """Navega a la página anterior."""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pagina_actual()
    
    def _ir_a_pagina_siguiente(self):
        """Navega a la página siguiente."""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._cargar_pagina_actual()
    
    def _ir_a_ultima_pagina(self):
        """Navega a la última página."""
        self.pagina_actual = self.total_paginas
        self._cargar_pagina_actual()
    
    def _ir_a_pagina_especifica(self):
        """Navega a la página específica indicada."""
        try:
            pagina = int(self.entry_pagina.get())
            
            if pagina < 1 or pagina > self.total_paginas:
                messagebox.showwarning(
                    "Advertencia",
                    f"La página debe estar entre 1 y {self.total_paginas}"
                )
                return
            
            self.pagina_actual = pagina
            self._cargar_pagina_actual()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número de página válido")
    
    def _cambiar_registros_por_pagina(self, valor):
        """
        Cambia la cantidad de registros por página.
        
        Args:
            valor: Nuevo valor seleccionado en el Combobox.
        """
        try:
            self.registros_por_pagina = int(valor)
            self.pagina_actual = 1
            self._cargar_pagina_actual()
        except ValueError:
            messagebox.showerror("Error", "Valor inválido")
    
    def _cambiar_orden(self, valor):
        """
        Cambia el orden de los registros.
        
        Args:
            valor: Texto seleccionado en el Combobox de ordenamiento.
        """
        if "Ascendente" in valor:
            self.orden_actual = "asc"
        else:
            self.orden_actual = "desc"
        self._cargar_pagina_actual()
    
    def _aplicar_filtros(self):
        """
        Aplica los filtros seleccionados y recarga la primera página.
        """
        try:
            filtros = {}
            
            fecha_inicio = self.calendario_inicio.get_date()
            fecha_fin = self.calendario_fin.get_date()
            
            if fecha_inicio and fecha_fin:
                filtros['fecha_inicio'] = datetime.combine(fecha_inicio, datetime.min.time())
                filtros['fecha_fin'] = datetime.combine(fecha_fin, datetime.max.time())
            
            if self.combo_anio_desde.get() and self.combo_anio_desde.get() != "Todos":
                filtros['anio_desde'] = int(self.combo_anio_desde.get())
            if self.combo_anio_hasta.get() and self.combo_anio_hasta.get() != "Todos":
                filtros['anio_hasta'] = int(self.combo_anio_hasta.get())
            
            if self.combo_aniomes_desde.get() and self.combo_aniomes_desde.get() != "Todos":
                filtros['aniomes_desde'] = int(self.combo_aniomes_desde.get())
            if self.combo_aniomes_hasta.get() and self.combo_aniomes_hasta.get() != "Todos":
                filtros['aniomes_hasta'] = int(self.combo_aniomes_hasta.get())
            
            if self.combo_anio_semana_desde.get() and self.combo_anio_semana_desde.get() != "Todos":
                filtros['anio_semana_desde'] = int(self.combo_anio_semana_desde.get())
            if self.combo_anio_semana_hasta.get() and self.combo_anio_semana_hasta.get() != "Todos":
                filtros['anio_semana_hasta'] = int(self.combo_anio_semana_hasta.get())
            
            if self.combo_aniomessemana_desde.get() and self.combo_aniomessemana_desde.get() != "Todos":
                filtros['aniomessemana_desde'] = int(self.combo_aniomessemana_desde.get())
            if self.combo_aniomessemana_hasta.get() and self.combo_aniomessemana_hasta.get() != "Todos":
                filtros['aniomessemana_hasta'] = int(self.combo_aniomessemana_hasta.get())
            
            self.filtros_actuales = filtros
            self.pagina_actual = 1
            self._cargar_pagina_actual()
            
        except ValueError as error:
            messagebox.showerror("Error", f"Formato inválido: {str(error)}")
        except Exception as error:
            messagebox.showerror("Error", f"Error al filtrar: {str(error)}")
    
    def _limpiar_filtros(self):
        """
        Restablece todos los filtros y recarga los datos.
        """
        primer_dia_mes = date.today().replace(day=1)
        ultimo_dia_mes = calendar.monthrange(date.today().year, date.today().month)[1]
        ultimo_dia = date.today().replace(day=ultimo_dia_mes)
        
        self.calendario_inicio.set_date(primer_dia_mes)
        self.calendario_fin.set_date(ultimo_dia)
        
        self.combo_anio_desde.set("Todos")
        self.combo_anio_hasta.set("Todos")
        self.combo_aniomes_desde.set("Todos")
        self.combo_aniomes_hasta.set("Todos")
        self.combo_anio_semana_desde.set("Todos")
        self.combo_anio_semana_hasta.set("Todos")
        self.combo_aniomessemana_desde.set("Todos")
        self.combo_aniomessemana_hasta.set("Todos")
        self.combo_orden.set("Fecha y Hora - Descendente")
        self.orden_actual = "desc"
        self.filtros_actuales = {}
        self.pagina_actual = 1
        self._cargar_pagina_actual()
    
    def _exportar_excel(self):
        """
        Exporta todos los registros filtrados a Excel.
        """
        try:
            total = self.servicio.contar_registros(self.filtros_actuales)
            
            if total == 0:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            respuesta = messagebox.askyesno(
                "Confirmar",
                f"Se exportarán {total} registros.\n\n¿Continuar?"
            )
            
            if not respuesta:
                return
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                title="Guardar Excel"
            )
            
            if archivo:
                todos = self.servicio.obtener_registros_paginados(
                    1, total, self.filtros_actuales, self.orden_actual
                )
                df = self.servicio.convertir_a_dataframe(todos)
                df.to_excel(archivo, index=False, engine='openpyxl')
                messagebox.showinfo("Éxito", f"Exportado a:\n{archivo}")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo exportar: {str(error)}")