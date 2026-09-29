"""
Módulo del gráfico de líneas de presión arterial.

Este módulo contiene la interfaz gráfica para visualizar la evolución
temporal de la presión sistólica, diastólica y pulso en un gráfico
de líneas interactivo. Incluye los mismos filtros que la grilla de
consulta (sin ordenamiento) y permite exportar el gráfico a imagen.
Al pasar el mouse sobre los puntos del gráfico se muestra el valor
y la fecha correspondiente mediante tooltips personalizados.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import calendar
from tkcalendar import DateEntry
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
from servicios.servicio_presion import ServicioPresion


class GraficoLineas(ctk.CTkFrame):
    """
    Clase que representa la vista de gráfico de líneas de presión arterial.
    
    Muestra la evolución temporal de los valores de presión sistólica,
    diastólica y pulso en un gráfico de líneas interactivo con tooltips.
    Incluye los mismos filtros que la grilla de consulta (sin ordenamiento)
    para permitir analizar períodos específicos.
    """
    
    def __init__(self, parent):
        """
        Inicializa el gráfico de líneas.
        
        Args:
            parent: Widget padre donde se colocará el gráfico.
        """
        super().__init__(parent)
        self.servicio = ServicioPresion()
        self.registros = []
        self.filtros_actuales = {}
        self.figura = None
        self.canvas = None
        self.frame_grafico = None
        
        self._crear_interfaz()
        self._cargar_datos()
    
    def _crear_interfaz(self):
        """
        Crea todos los componentes visuales de la pantalla de gráfico.
        """
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="📈 Gráfico de Líneas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=5)
        
        # Frame de Filtros
        frame_filtros = ctk.CTkFrame(self)
        frame_filtros.pack(pady=5, padx=20, fill="x")
        
        # Contenedor centrado para los filtros
        frame_centro_filtros = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_centro_filtros.pack(pady=10, padx=20, anchor="center")
        
        grid_filtros = ctk.CTkFrame(frame_centro_filtros, fg_color="transparent")
        grid_filtros.pack(anchor="center")
        
        # Fila 0: Filtros: y Rango de fechas en la misma línea
        ctk.CTkLabel(
            grid_filtros,
            text="🔍 Filtros:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=3, sticky="e")
        
        ctk.CTkLabel(grid_filtros, text="Rango de fechas:").grid(row=0, column=1, padx=10, pady=3, sticky="e")
        
        primer_dia_mes = date.today().replace(day=1)
        self.calendario_inicio = DateEntry(
            grid_filtros, width=15, background='darkblue',
            foreground='white', borderwidth=2,
            date_pattern='dd/mm/yyyy', locale='es_ES'
        )
        self.calendario_inicio.set_date(primer_dia_mes)
        self.calendario_inicio.grid(row=0, column=2, padx=5, pady=3)
        
        ctk.CTkLabel(grid_filtros, text="a").grid(row=0, column=3, padx=5)
        
        ultimo_dia_mes = calendar.monthrange(date.today().year, date.today().month)[1]
        ultimo_dia = date.today().replace(day=ultimo_dia_mes)
        self.calendario_fin = DateEntry(
            grid_filtros, width=15, background='darkblue',
            foreground='white', borderwidth=2,
            date_pattern='dd/mm/yyyy', locale='es_ES'
        )
        self.calendario_fin.set_date(ultimo_dia)
        self.calendario_fin.grid(row=0, column=4, padx=5, pady=3)
        
        # Filtro 2: Año
        ctk.CTkLabel(grid_filtros, text="Año:").grid(row=1, column=1, padx=10, pady=3, sticky="e")
        self.combo_anio_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_desde.set("Todos")
        self.combo_anio_desde.grid(row=1, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=1, column=3, padx=5)
        self.combo_anio_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_hasta.set("Todos")
        self.combo_anio_hasta.grid(row=1, column=4, padx=5, pady=3)
        
        # Filtro 3: Año-Mes
        ctk.CTkLabel(grid_filtros, text="Año-Mes:").grid(row=2, column=1, padx=10, pady=3, sticky="e")
        self.combo_aniomes_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_desde.set("Todos")
        self.combo_aniomes_desde.grid(row=2, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=2, column=3, padx=5)
        self.combo_aniomes_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_hasta.set("Todos")
        self.combo_aniomes_hasta.grid(row=2, column=4, padx=5, pady=3)
        
        # Filtro 4: Año-Semana
        ctk.CTkLabel(grid_filtros, text="Año-Semana:").grid(row=3, column=1, padx=10, pady=3, sticky="e")
        self.combo_anio_semana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_desde.set("Todos")
        self.combo_anio_semana_desde.grid(row=3, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=3, column=3, padx=5)
        self.combo_anio_semana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_hasta.set("Todos")
        self.combo_anio_semana_hasta.grid(row=3, column=4, padx=5, pady=3)
        
        # Filtro 5: Año-Mes-Semana
        ctk.CTkLabel(grid_filtros, text="Año-Mes-Semana:").grid(row=4, column=1, padx=10, pady=3, sticky="e")
        self.combo_aniomessemana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_desde.set("Todos")
        self.combo_aniomessemana_desde.grid(row=4, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=4, column=3, padx=5)
        self.combo_aniomessemana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_hasta.set("Todos")
        self.combo_aniomessemana_hasta.grid(row=4, column=4, padx=5, pady=3)
        
        # Botones
        frame_botones = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_botones.pack(pady=3)
        
        self.btn_filtrar = ctk.CTkButton(
            frame_botones, text="🔍 Filtrar",
            font=ctk.CTkFont(size=14, weight="bold"), height=35,
            command=self._aplicar_filtros
        )
        self.btn_filtrar.pack(side="left", padx=3)
        
        self.btn_limpiar = ctk.CTkButton(
            frame_botones, text="🧹 Limpiar Filtros",
            font=ctk.CTkFont(size=14), height=35,
            fg_color="#6b7280", hover_color="#4b5563",
            command=self._limpiar_filtros
        )
        self.btn_limpiar.pack(side="left", padx=3)
        
        self.btn_exportar = ctk.CTkButton(
            frame_botones, text="💾 Exportar Gráfico",
            font=ctk.CTkFont(size=14), height=35,
            fg_color="#10b981", hover_color="#059669",
            command=self._exportar_grafico
        )
        self.btn_exportar.pack(side="left", padx=3)
        
        # Frame del gráfico
        self.frame_grafico = ctk.CTkFrame(self)
        self.frame_grafico.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.etiqueta_cantidad = ctk.CTkLabel(
            self.frame_grafico, text="Total: 0 registros",
            font=ctk.CTkFont(size=12)
        )
        self.etiqueta_cantidad.pack(pady=5)
    
    def _cargar_datos(self):
        """
        Carga los registros iniciales y actualiza los Combobox.
        """
        try:
            self._actualizar_combobox()
            self._generar_grafico()
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(error)}")
    
    def _generar_grafico(self):
        """
        Genera el gráfico de líneas interactivo con tooltips.
        Los datos se ordenan siempre por fecha ascendente para mostrar
        la evolución temporal correctamente.
        """
        try:
            self.registros = self.servicio.filtrar_registros(self.filtros_actuales)
            self.registros.sort(key=lambda r: r.presion_fechahora)
            
            if not self.registros:
                messagebox.showinfo("Información", "No hay registros para graficar")
                return
            
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            
            self.figura = Figure(figsize=(12, 6), dpi=100)
            eje = self.figura.add_subplot(111)
            
            fechas = []
            sistolicas = []
            diastolicas = []
            pulsos = []
            
            for registro in self.registros:
                fechas.append(registro.presion_fechahora)
                sistolicas.append(registro.presion_sistolica)
                diastolicas.append(registro.presion_diastolica)
                pulsos.append(registro.presion_pulso)
            
            # Graficar las tres series con pickradius para facilitar selección
            eje.plot(
                fechas, sistolicas, marker='o', linewidth=2, markersize=8,
                label='Sistólica', color='#2563eb', pickradius=10
            )
            eje.plot(
                fechas, diastolicas, marker='s', linewidth=2, markersize=8,
                label='Diastólica', color='#10b981', pickradius=10
            )
            eje.plot(
                fechas, pulsos, marker='^', linewidth=2, markersize=8,
                label='Pulso', color='#ef4444', pickradius=10
            )
            
            eje.set_xlabel('Fecha', fontsize=11, fontweight='bold')
            eje.set_ylabel('Valor', fontsize=11, fontweight='bold')
            eje.set_title(
                'Evolución de la Presión Arterial',
                fontsize=13, fontweight='bold', pad=15
            )
            eje.legend(fontsize=10, loc='best')
            eje.grid(True, alpha=0.3)
            
            self.figura.autofmt_xdate()
            self.figura.tight_layout()
            
            self.canvas = FigureCanvasTkAgg(self.figura, master=self.frame_grafico)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            # Configurar mplcursors con hover=True
            cursor = mplcursors.cursor(self.figura, hover=True)
            
            @cursor.connect("add")
            def on_add(sel):
                """
                Muestra el tooltip personalizado con la fecha y el valor
                al pasar el mouse sobre un punto del gráfico.
                """
                try:
                    indice = sel.index
                    
                    if 0 <= indice < len(fechas):
                        fecha_formateada = fechas[indice].strftime("%d-%m-%Y %H:%M")
                        valor = sel.target[1]
                        serie = sel.artist.get_label()
                        
                        # Establecer el texto personalizado del tooltip
                        sel.annotation.set_text(
                            f"{serie}\nFecha: {fecha_formateada}\nValor: {valor:.1f}"
                        )
                        sel.annotation.set_visible(True)
                except Exception:
                    pass
            
            self.etiqueta_cantidad.configure(text=f"Total: {len(self.registros)} registros")
            
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo generar el gráfico: {str(error)}")
    
    def _actualizar_combobox(self):
        """
        Actualiza los valores de los Combobox de filtros con los datos
        únicos disponibles en la base de datos.
        """
        try:
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
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron actualizar los filtros: {str(error)}")
    
    def _aplicar_filtros(self):
        """
        Aplica los filtros seleccionados y regenera el gráfico.
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
            self._generar_grafico()
            
        except ValueError as error:
            messagebox.showerror("Error", f"Formato inválido: {str(error)}")
        except Exception as error:
            messagebox.showerror("Error", f"Error al filtrar: {str(error)}")
    
    def _limpiar_filtros(self):
        """
        Restablece todos los filtros al estado inicial y regenera el gráfico.
        """
        try:
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
            
            self.filtros_actuales = {}
            self._generar_grafico()
        except Exception as error:
            messagebox.showerror("Error", f"Error al limpiar filtros: {str(error)}")
    
    def _exportar_grafico(self):
        """
        Exporta el gráfico actual a un archivo de imagen en alta resolución.
        """
        try:
            if not self.figura:
                messagebox.showwarning("Advertencia", "No hay gráfico para exportar")
                return
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("Imagen PNG", "*.png"),
                    ("Imagen JPG", "*.jpg"),
                    ("Documento PDF", "*.pdf"),
                    ("Imagen SVG", "*.svg"),
                ],
                title="Guardar gráfico"
            )
            
            if archivo:
                self.figura.savefig(archivo, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico exportado a:\n{archivo}")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo exportar: {str(error)}")