"""
Módulo de visualización de gráficos.

Este módulo contiene la interfaz gráfica para generar y visualizar
dos tipos de gráficos de los registros de presión arterial:
- Gráfico de líneas: muestra la evolución temporal de los valores.
- Gráfico de frecuencia: muestra la cantidad de repeticiones de cada
  valor agrupado por rangos fijos.

El gráfico de frecuencia incluye los mismos filtros que el gráfico de
líneas (rango de fechas, año, año-mes, año-semana, año-mes-semana)
y permite exportar el gráfico a formatos de imagen.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import calendar
from tkcalendar import DateEntry
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from servicios.servicio_presion import ServicioPresion


class VentanaGraficos(ctk.CTkFrame):
    """
    Clase que representa la vista de gráficos de presión arterial.

    Soporta dos modos de visualización:
    - 'lineas': Gráfico de evolución temporal.
    - 'frecuencia': Gráfico de distribución por rangos fijos.

    Incluye filtros por rango de fechas y por año / año-mes / año-semana /
    año-mes-semana (los mismos que usa el gráfico de líneas).

    Permite actualizar los datos y exportar el gráfico a imagen.
    """

    # Rangos fijos usados para el gráfico de frecuencia.
    # Cada entrada es (etiqueta, límite_inferior, límite_superior_exclusivo).
    # Los mismos rangos se aplican a sistólica, diastólica y pulso.
    RANGOS = [
        ("000 a 060", 0, 61),
        ("061 a 080", 61, 81),
        ("081 a 100", 81, 101),
        ("101 a 110", 101, 111),
        ("111 a 120", 111, 121),
        ("121 a 130", 121, 131),
        ("131 a 140", 131, 141),
        ("141 a 150", 141, 151),
        ("151 a 160", 151, 161),
        ("161 a 170", 161, 171),
        ("171 a infinito", 171, float("inf")),
    ]

    def __init__(self, parent, tipo: str = "lineas"):
        """
        Inicializa la ventana de gráficos.

        Args:
            parent: Widget padre donde se colocará el gráfico.
            tipo: Tipo de gráfico a mostrar ('lineas' o 'frecuencia').
        """
        super().__init__(parent)
        self.servicio = ServicioPresion()
        self.tipo = tipo
        self.registros = []
        self.filtros_actuales = {}
        self.figura = None
        self.canvas = None
        self.frame_grafico = None

        self._crear_interfaz()
        self._cargar_datos()

    # -----------------------------------------------------------------
    # Construcción de la interfaz
    # -----------------------------------------------------------------

    def _crear_interfaz(self):
        """
        Crea todos los componentes visuales de la pantalla de gráficos.
        """
        # Determinar título según el tipo.
        if self.tipo == "lineas":
            titulo_texto = "📈 Gráfico de Líneas - Evolución Temporal"
        else:
            titulo_texto = "🔢 Gráfico de Frecuencia - Distribución por Rangos"

        # Título.
        titulo = ctk.CTkLabel(
            self,
            text=titulo_texto,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        titulo.pack(pady=5)

        # Frame de Filtros (mismo formato que GraficoLineas).
        self._crear_frame_filtros()

        # Frame del gráfico.
        self.frame_grafico = ctk.CTkFrame(self)
        self.frame_grafico.pack(pady=5, padx=20, fill="both", expand=True)

        # Etiqueta con la cantidad de registros.
        self.etiqueta_cantidad = ctk.CTkLabel(
            self.frame_grafico, text="Total: 0 registros",
            font=ctk.CTkFont(size=12),
        )
        self.etiqueta_cantidad.pack(pady=5)

    def _crear_frame_filtros(self):
        """
        Crea el bloque de filtros (idéntico al del gráfico de líneas):
        rango de fechas, año, año-mes, año-semana y año-mes-semana.
        """
        frame_filtros = ctk.CTkFrame(self)
        frame_filtros.pack(pady=5, padx=20, fill="x")

        frame_centro_filtros = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_centro_filtros.pack(pady=10, padx=20, anchor="center")

        grid_filtros = ctk.CTkFrame(frame_centro_filtros, fg_color="transparent")
        grid_filtros.pack(anchor="center")

        # --- Fila 0: rango de fechas ---
        ctk.CTkLabel(
            grid_filtros,
            text="🔍 Filtros:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=3, sticky="e")

        ctk.CTkLabel(grid_filtros, text="Rango de fechas:").grid(
            row=0, column=1, padx=10, pady=3, sticky="e"
        )

        primer_dia_mes = date.today().replace(day=1)
        self.calendario_inicio = DateEntry(
            grid_filtros, width=15, background="darkblue",
            foreground="white", borderwidth=2,
            date_pattern="dd/mm/yyyy", locale="es_ES",
        )
        self.calendario_inicio.set_date(primer_dia_mes)
        self.calendario_inicio.grid(row=0, column=2, padx=5, pady=3)

        ctk.CTkLabel(grid_filtros, text="a").grid(row=0, column=3, padx=5)

        ultimo_dia_mes = calendar.monthrange(date.today().year, date.today().month)[1]
        ultimo_dia = date.today().replace(day=ultimo_dia_mes)
        self.calendario_fin = DateEntry(
            grid_filtros, width=15, background="darkblue",
            foreground="white", borderwidth=2,
            date_pattern="dd/mm/yyyy", locale="es_ES",
        )
        self.calendario_fin.set_date(ultimo_dia)
        self.calendario_fin.grid(row=0, column=4, padx=5, pady=3)

        # --- Fila 1: Año ---
        ctk.CTkLabel(grid_filtros, text="Año:").grid(
            row=1, column=1, padx=10, pady=3, sticky="e"
        )
        self.combo_anio_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_desde.set("Todos")
        self.combo_anio_desde.grid(row=1, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=1, column=3, padx=5)
        self.combo_anio_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_hasta.set("Todos")
        self.combo_anio_hasta.grid(row=1, column=4, padx=5, pady=3)

        # --- Fila 2: Año-Mes ---
        ctk.CTkLabel(grid_filtros, text="Año-Mes:").grid(
            row=2, column=1, padx=10, pady=3, sticky="e"
        )
        self.combo_aniomes_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_desde.set("Todos")
        self.combo_aniomes_desde.grid(row=2, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=2, column=3, padx=5)
        self.combo_aniomes_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomes_hasta.set("Todos")
        self.combo_aniomes_hasta.grid(row=2, column=4, padx=5, pady=3)

        # --- Fila 3: Año-Semana ---
        ctk.CTkLabel(grid_filtros, text="Año-Semana:").grid(
            row=3, column=1, padx=10, pady=3, sticky="e"
        )
        self.combo_anio_semana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_desde.set("Todos")
        self.combo_anio_semana_desde.grid(row=3, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=3, column=3, padx=5)
        self.combo_anio_semana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_anio_semana_hasta.set("Todos")
        self.combo_anio_semana_hasta.grid(row=3, column=4, padx=5, pady=3)

        # --- Fila 4: Año-Mes-Semana ---
        ctk.CTkLabel(grid_filtros, text="Año-Mes-Semana:").grid(
            row=4, column=1, padx=10, pady=3, sticky="e"
        )
        self.combo_aniomessemana_desde = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_desde.set("Todos")
        self.combo_aniomessemana_desde.grid(row=4, column=2, padx=5, pady=3)
        ctk.CTkLabel(grid_filtros, text="a").grid(row=4, column=3, padx=5)
        self.combo_aniomessemana_hasta = ctk.CTkComboBox(grid_filtros, width=120, values=[])
        self.combo_aniomessemana_hasta.set("Todos")
        self.combo_aniomessemana_hasta.grid(row=4, column=4, padx=5, pady=3)

        # --- Botones ---
        frame_botones = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_botones.pack(pady=3)

        self.btn_filtrar = ctk.CTkButton(
            frame_botones, text="🔍 Filtrar",
            font=ctk.CTkFont(size=14, weight="bold"), height=35,
            command=self._aplicar_filtros,
        )
        self.btn_filtrar.pack(side="left", padx=3)

        self.btn_limpiar = ctk.CTkButton(
            frame_botones, text="🧹 Limpiar Filtros",
            font=ctk.CTkFont(size=14), height=35,
            fg_color="#6b7280", hover_color="#4b5563",
            command=self._limpiar_filtros,
        )
        self.btn_limpiar.pack(side="left", padx=3)

        self.btn_exportar = ctk.CTkButton(
            frame_botones, text="💾 Exportar Gráfico",
            font=ctk.CTkFont(size=14), height=35,
            fg_color="#10b981", hover_color="#059669",
            command=self._exportar_grafico,
        )
        self.btn_exportar.pack(side="left", padx=3)

    # -----------------------------------------------------------------
    # Carga y generación de datos
    # -----------------------------------------------------------------

    def _cargar_datos(self):
        """
        Carga los registros iniciales y actualiza los Combobox de filtros.
        """
        try:
            self._actualizar_combobox()
            self._generar_grafico()
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(error)}")

    def _actualizar_combobox(self):
        """
        Actualiza los valores de los Combobox con los datos únicos
        disponibles en la base de datos.
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

    def _generar_grafico(self):
        """
        Obtiene los registros filtrados y genera el gráfico correspondiente
        al tipo configurado ('lineas' o 'frecuencia').
        """
        try:
            self.registros = self.servicio.filtrar_registros(self.filtros_actuales)
            self.registros.sort(key=lambda r: r.presion_fechahora)

            if not self.registros:
                messagebox.showinfo("Información", "No hay registros para graficar")
                return

            # Destruir el gráfico anterior si existe.
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

            # Crear nueva figura de matplotlib.
            self.figura = Figure(figsize=(12, 7), dpi=100)

            # Generar el gráfico según el tipo.
            if self.tipo == "lineas":
                self._generar_grafico_lineas()
            else:
                self._generar_grafico_frecuencia()

            # Renderizar el gráfico en el frame.
            self.canvas = FigureCanvasTkAgg(self.figura, master=self.frame_grafico)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            # Actualizar la etiqueta de cantidad.
            self.etiqueta_cantidad.configure(
                text=f"Total: {len(self.registros)} registros"
            )

        except Exception as error:
            messagebox.showerror("Error", f"No se pudo generar el gráfico: {str(error)}")

    def _generar_grafico_lineas(self):
        """
        Genera un gráfico de líneas que muestra la evolución temporal
        de la presión sistólica, diastólica y el pulso.
        """
        eje = self.figura.add_subplot(111)

        fechas = [r.presion_fechahora for r in self.registros]
        sistolicas = [r.presion_sistolica for r in self.registros]
        diastolicas = [r.presion_diastolica for r in self.registros]
        pulsos = [r.presion_pulso for r in self.registros]

        eje.plot(
            fechas, sistolicas, marker="o", linewidth=2, markersize=6,
            label="Sistólica", color="#2563eb",
        )
        eje.plot(
            fechas, diastolicas, marker="s", linewidth=2, markersize=6,
            label="Diastólica", color="#10b981",
        )
        eje.plot(
            fechas, pulsos, marker="^", linewidth=2, markersize=6,
            label="Pulso", color="#ef4444",
        )

        eje.set_xlabel("Fecha", fontsize=12, fontweight="bold")
        eje.set_ylabel("Valor", fontsize=12, fontweight="bold")
        eje.set_title(
            "Evolución de la Presión Arterial",
            fontsize=14, fontweight="bold", pad=20,
        )
        eje.legend(fontsize=11, loc="best")
        eje.grid(True, alpha=0.3)

        self.figura.autofmt_xdate()
        self.figura.tight_layout()

    def _generar_grafico_frecuencia(self):
        """
        Genera tres gráficos de barras mostrando la frecuencia
        (cantidad de mediciones) que caen dentro de cada rango fijo,
        para sistólica, diastólica y pulso.

        Los rangos son fijos (self.RANGOS) y los mismos para las 3 series.
        """
        etiquetas = [r[0] for r in self.RANGOS]

        # Crear 3 subgráficos en una fila.
        ejes = self.figura.subplots(1, 3)

        # Configuración de cada subgráfico.
        configuracion = [
            {
                "columna": "Sistólica",
                "titulo": "Frecuencia Sistólica",
                "color": "#2563eb",
                "eje": ejes[0],
                "attr": "presion_sistolica",
            },
            {
                "columna": "Diastólica",
                "titulo": "Frecuencia Diastólica",
                "color": "#10b981",
                "eje": ejes[1],
                "attr": "presion_diastolica",
            },
            {
                "columna": "Pulso",
                "titulo": "Frecuencia Pulso",
                "color": "#ef4444",
                "eje": ejes[2],
                "attr": "presion_pulso",
            },
        ]

        for config in configuracion:
            eje = config["eje"]

            # Contar cuántas mediciones caen en cada rango.
            frecuencias = [0] * len(self.RANGOS)
            for registro in self.registros:
                valor = getattr(registro, config["attr"], None)
                if valor is None:
                    continue
                v = float(valor)
                for i, (_, lo, hi) in enumerate(self.RANGOS):
                    if lo <= v < hi:
                        frecuencias[i] += 1
                        break

            # Crear gráfico de barras.
            eje.bar(
                etiquetas, frecuencias,
                color=config["color"], alpha=0.7, edgecolor="black",
            )
            eje.set_xlabel("Rango", fontsize=10)
            eje.set_ylabel("Frecuencia", fontsize=10)
            eje.set_title(config["titulo"], fontsize=12, fontweight="bold")
            eje.grid(True, alpha=0.3, axis="y")

            # Rotar las etiquetas del eje X para que se lean.
            eje.tick_params(axis="x", rotation=45)
            for label in eje.get_xticklabels():
                label.set_ha("right")

        # Título general.
        self.figura.suptitle(
            "Distribución de Frecuencias por Rango",
            fontsize=14, fontweight="bold", y=1.02,
        )
        self.figura.tight_layout()

    # -----------------------------------------------------------------
    # Acciones de filtros
    # -----------------------------------------------------------------

    def _aplicar_filtros(self):
        """
        Aplica los filtros seleccionados y regenera el gráfico.
        """
        try:
            filtros = {}

            fecha_inicio = self.calendario_inicio.get_date()
            fecha_fin = self.calendario_fin.get_date()

            if fecha_inicio and fecha_fin:
                filtros["fecha_inicio"] = datetime.combine(fecha_inicio, datetime.min.time())
                filtros["fecha_fin"] = datetime.combine(fecha_fin, datetime.max.time())

            if self.combo_anio_desde.get() and self.combo_anio_desde.get() != "Todos":
                filtros["anio_desde"] = int(self.combo_anio_desde.get())
            if self.combo_anio_hasta.get() and self.combo_anio_hasta.get() != "Todos":
                filtros["anio_hasta"] = int(self.combo_anio_hasta.get())

            if self.combo_aniomes_desde.get() and self.combo_aniomes_desde.get() != "Todos":
                filtros["aniomes_desde"] = int(self.combo_aniomes_desde.get())
            if self.combo_aniomes_hasta.get() and self.combo_aniomes_hasta.get() != "Todos":
                filtros["aniomes_hasta"] = int(self.combo_aniomes_hasta.get())

            if self.combo_anio_semana_desde.get() and self.combo_anio_semana_desde.get() != "Todos":
                filtros["anio_semana_desde"] = int(self.combo_anio_semana_desde.get())
            if self.combo_anio_semana_hasta.get() and self.combo_anio_semana_hasta.get() != "Todos":
                filtros["anio_semana_hasta"] = int(self.combo_anio_semana_hasta.get())

            if self.combo_aniomessemana_desde.get() and self.combo_aniomessemana_desde.get() != "Todos":
                filtros["aniomessemana_desde"] = int(self.combo_aniomessemana_desde.get())
            if self.combo_aniomessemana_hasta.get() and self.combo_aniomessemana_hasta.get() != "Todos":
                filtros["aniomessemana_hasta"] = int(self.combo_aniomessemana_hasta.get())

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

    # -----------------------------------------------------------------
    # Exportación
    # -----------------------------------------------------------------

    def _exportar_grafico(self):
        """
        Exporta el gráfico actual a un archivo de imagen.

        Permite guardar en formatos: PNG, JPG, PDF y SVG.
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
                title="Guardar gráfico",
            )

            if archivo:
                self.figura.savefig(archivo, dpi=300, bbox_inches="tight")
                messagebox.showinfo("Éxito", f"Gráfico exportado correctamente a:\n{archivo}")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo exportar el gráfico: {str(error)}")