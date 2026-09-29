"""
Módulo de visualización de gráficos.

Este módulo contiene la interfaz gráfica para generar y visualizar
dos tipos de gráficos de los registros de presión arterial:
- Gráfico de líneas: muestra la evolución temporal de los valores
- Gráfico de frecuencia: muestra la cantidad de repeticiones de cada valor
También permite exportar los gráficos a formatos de imagen.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
from servicios.servicio_presion import ServicioPresion


class VentanaGraficos(ctk.CTkFrame):
    """
    Clase que representa la vista de gráficos de presión arterial.
    
    Soporta dos modos de visualización:
    - 'lineas': Gráfico de evolución temporal
    - 'frecuencia': Gráfico de distribución de valores
    
    Permite actualizar los datos y exportar el gráfico a imagen.
    """
    
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
        self.figura = None
        self.canvas = None
        self._crear_interfaz()
        self._cargar_grafico()
    
    def _crear_interfaz(self):
        """
        Crea todos los componentes visuales de la pantalla de gráficos.
        """
        # Determinar título según el tipo
        if self.tipo == "lineas":
            titulo_texto = "📈 Gráfico de Líneas - Evolución Temporal"
        else:
            titulo_texto = " Gráfico de Frecuencia - Distribución de Valores"
        
        # Título
        titulo = ctk.CTkLabel(
            self,
            text=titulo_texto,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=10)
        
        # Frame de controles
        frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        frame_controles.pack(pady=10)
        
        # Botón: Actualizar
        self.btn_actualizar = ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._cargar_grafico
        )
        self.btn_actualizar.pack(side="left", padx=5)
        
        # Botón: Exportar
        self.btn_exportar = ctk.CTkButton(
            frame_controles,
            text="💾 Exportar Gráfico",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._exportar_grafico
        )
        self.btn_exportar.pack(side="left", padx=5)
        
        # Frame donde se mostrará el gráfico
        self.frame_grafico = ctk.CTkFrame(self)
        self.frame_grafico.pack(pady=10, padx=20, fill="both", expand=True)
    
    def _cargar_grafico(self):
        """
        Obtiene los datos de la base de datos y genera el gráfico
        correspondiente al tipo configurado.
        """
        try:
            # Obtener todos los registros
            registros = self.servicio.obtener_todos()
            
            if not registros:
                messagebox.showinfo("Información", "No hay registros para graficar")
                return
            
            # Convertir a DataFrame
            dataframe = self.servicio.convertir_a_dataframe(registros)
            
            # Destruir el gráfico anterior si existe
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            
            # Crear nueva figura de matplotlib
            self.figura = Figure(figsize=(12, 7), dpi=100)
            
            # Generar el gráfico según el tipo
            if self.tipo == "lineas":
                self._generar_grafico_lineas(dataframe)
            else:
                self._generar_grafico_frecuencia(dataframe)
            
            # Renderizar el gráfico en el frame
            self.canvas = FigureCanvasTkAgg(self.figura, master=self.frame_grafico)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo generar el gráfico: {str(error)}")
    
    def _generar_grafico_lineas(self, dataframe):
        """
        Genera un gráfico de líneas que muestra la evolución temporal
        de la presión sistólica, diastólica y el pulso.
        
        Args:
            dataframe: DataFrame de Pandas con los registros ordenados por fecha.
        """
        eje = self.figura.add_subplot(111)
        
        # Ordenar por fecha
        dataframe = dataframe.sort_values('Fecha')
        
        # Graficar las tres series con colores diferenciados
        eje.plot(
            dataframe['Fecha'], dataframe['Sistólica'],
            marker='o', linewidth=2, markersize=6,
            label='Sistólica', color='#2563eb'
        )
        eje.plot(
            dataframe['Fecha'], dataframe['Diastólica'],
            marker='s', linewidth=2, markersize=6,
            label='Diastólica', color='#10b981'
        )
        eje.plot(
            dataframe['Fecha'], dataframe['Pulso'],
            marker='^', linewidth=2, markersize=6,
            label='Pulso', color='#ef4444'
        )
        
        # Configurar etiquetas y título
        eje.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        eje.set_ylabel('Valor', fontsize=12, fontweight='bold')
        eje.set_title(
            'Evolución de la Presión Arterial',
            fontsize=14, fontweight='bold', pad=20
        )
        eje.legend(fontsize=11, loc='best')
        eje.grid(True, alpha=0.3)
        
        # Rotar etiquetas de fecha para mejor legibilidad
        self.figura.autofmt_xdate()
        self.figura.tight_layout()
    
    def _generar_grafico_frecuencia(self, dataframe):
        """
        Genera tres gráficos de barras mostrando la frecuencia
        (cantidad de repeticiones) de cada valor para sistólica,
        diastólica y pulso.
        
        Args:
            dataframe: DataFrame de Pandas con los registros.
        """
        # Crear 3 subgráficos en una fila
        figura, ejes = self.figura.subplots(1, 3, figsize=(15, 5))
        
        # Configuración de cada subgráfico
        configuracion = [
            {
                'columna': 'Sistólica',
                'titulo': 'Frecuencia Sistólica',
                'color': '#2563eb',
                'eje': ejes[0]
            },
            {
                'columna': 'Diastólica',
                'titulo': 'Frecuencia Diastólica',
                'color': '#10b981',
                'eje': ejes[1]
            },
            {
                'columna': 'Pulso',
                'titulo': 'Frecuencia Pulso',
                'color': '#ef4444',
                'eje': ejes[2]
            }
        ]
        
        for config in configuracion:
            eje = config['eje']
            columna = config['columna']
            
            # Contar frecuencia de cada valor (redondeado a entero)
            valores = dataframe[columna].round(0).astype(int)
            frecuencia = Counter(valores)
            
            # Ordenar por valor para mejor visualización
            valores_ordenados = sorted(frecuencia.keys())
            frecuencias = [frecuencia[v] for v in valores_ordenados]
            
            # Crear gráfico de barras
            eje.bar(
                valores_ordenados, frecuencias,
                color=config['color'], alpha=0.7, edgecolor='black'
            )
            eje.set_xlabel('Valor', fontsize=10)
            eje.set_ylabel('Frecuencia', fontsize=10)
            eje.set_title(config['titulo'], fontsize=12, fontweight='bold')
            eje.grid(True, alpha=0.3, axis='y')
            
            # Rotar etiquetas si hay muchos valores
            if len(valores_ordenados) > 10:
                eje.tick_params(axis='x', rotation=45)
        
        # Título general
        figura.suptitle(
            'Distribución de Frecuencias',
            fontsize=14, fontweight='bold', y=1.02
        )
        figura.tight_layout()
    
    def _exportar_grafico(self):
        """
        Exporta el gráfico actual a un archivo de imagen.
        
        Permite guardar en formatos: PNG, JPG, PDF y SVG.
        """
        try:
            if not self.figura:
                messagebox.showwarning("Advertencia", "No hay gráfico para exportar")
                return
            
            # Abrir diálogo para guardar archivo
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
                # Guardar con alta resolución
                self.figura.savefig(archivo, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico exportado correctamente a:\n{archivo}")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo exportar el gráfico: {str(error)}")