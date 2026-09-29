"""
Módulo del formulario de ingreso de datos de presión arterial.

Este módulo contiene la interfaz gráfica para ingresar nuevos registros
de presión arterial, incluyendo validaciones y cálculo automático
de campos derivados como año, mes y semana.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from modelos.registro_presion import RegistroPresion
from servicios.servicio_presion import ServicioPresion


class FormularioIngreso(ctk.CTkFrame):
    """
    Clase que representa el formulario de ingreso de datos.
    
    Permite al usuario ingresar los valores de presión sistólica,
    diastólica y pulso, calculando automáticamente los campos
    derivados y guardando el registro en la base de datos.
    """
    
    def __init__(self, parent):
        """
        Inicializa el formulario de ingreso.
        
        Args:
            parent: Widget padre donde se colocará el formulario.
        """
        super().__init__(parent)
        self.servicio = ServicioPresion()
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """
        Crea todos los componentes visuales del formulario.
        """
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="📝 Ingreso de Datos de Presión Arterial",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=20)
        
        # Frame del formulario
        frame_formulario = ctk.CTkFrame(self)
        frame_formulario.pack(pady=20, padx=40, fill="x")
        
        # Campo: Fecha y Hora
        self._crear_campo(frame_formulario, "Fecha y Hora:", 0)
        self.entry_fecha = ctk.CTkEntry(frame_formulario, width=300)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.entry_fecha.grid(row=0, column=1, padx=20, pady=15)
        
        # Campo: Presión Sistólica
        self._crear_campo(frame_formulario, "Presión Sistólica (mmHg):", 1)
        self.entry_sistolica = ctk.CTkEntry(
            frame_formulario, 
            width=300, 
            placeholder_text="Ej: 120"
        )
        self.entry_sistolica.grid(row=1, column=1, padx=20, pady=15)
        
        # Campo: Presión Diastólica
        self._crear_campo(frame_formulario, "Presión Diastólica (mmHg):", 2)
        self.entry_diastolica = ctk.CTkEntry(
            frame_formulario, 
            width=300, 
            placeholder_text="Ej: 80"
        )
        self.entry_diastolica.grid(row=2, column=1, padx=20, pady=15)
        
        # Campo: Pulso
        self._crear_campo(frame_formulario, "Pulso (lpm):", 3)
        self.entry_pulso = ctk.CTkEntry(
            frame_formulario, 
            width=300, 
            placeholder_text="Ej: 72"
        )
        self.entry_pulso.grid(row=3, column=1, padx=20, pady=15)
        
        # Campo: Archivo Origen
        self._crear_campo(frame_formulario, "Archivo Origen:", 4)
        self.entry_origen = ctk.CTkEntry(frame_formulario, width=300)
        self.entry_origen.insert(0, "desktop-app")
        self.entry_origen.grid(row=4, column=1, padx=20, pady=15)
        
        # Frame de botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=20)
        
        # Botón: Guardar
        self.btn_guardar = ctk.CTkButton(
            frame_botones,
            text="💾 Guardar Registro",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            command=self._guardar_registro
        )
        self.btn_guardar.pack(side="left", padx=10)
        
        # Botón: Limpiar
        self.btn_limpiar = ctk.CTkButton(
            frame_botones,
            text="🧹 Limpiar",
            font=ctk.CTkFont(size=16),
            height=50,
            width=150,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._limpiar_formulario
        )
        self.btn_limpiar.pack(side="left", padx=10)
    
    def _crear_campo(self, parent, texto: str, fila: int):
        """
        Crea una etiqueta para un campo del formulario.
        
        Args:
            parent: Widget padre donde se colocará la etiqueta.
            texto: Texto a mostrar en la etiqueta.
            fila: Número de fila en el grid.
        """
        etiqueta = ctk.CTkLabel(
            parent,
            text=texto,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        etiqueta.grid(row=fila, column=0, padx=20, pady=15, sticky="w")
    
    def _guardar_registro(self):
        """
        Valida los datos ingresados y guarda el registro en la base de datos.
        
        Realiza las siguientes validaciones:
        - Todos los campos obligatorios están completos
        - Los valores numéricos están dentro de rangos aceptables
        - La presión sistólica es mayor que la diastólica
        
        Si todo es válido, calcula los campos derivados y guarda el registro.
        """
        try:
            # Obtener valores de los campos
            fecha_str = self.entry_fecha.get()
            sistolica_str = self.entry_sistolica.get()
            diastolica_str = self.entry_diastolica.get()
            pulso_str = self.entry_pulso.get()
            origen = self.entry_origen.get()
            
            # Validar que los campos no estén vacíos
            if not all([fecha_str, sistolica_str, diastolica_str, pulso_str]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Convertir a números
            sistolica = float(sistolica_str)
            diastolica = float(diastolica_str)
            pulso = float(pulso_str)
            
            # Validar rangos
            if not (70 <= sistolica <= 250):
                messagebox.showerror("Error", "La sistólica debe estar entre 70 y 250 mmHg")
                return
            
            if not (40 <= diastolica <= 150):
                messagebox.showerror("Error", "La diastólica debe estar entre 40 y 150 mmHg")
                return
            
            if not (40 <= pulso <= 200):
                messagebox.showerror("Error", "El pulso debe estar entre 40 y 200 lpm")
                return
            
            if sistolica <= diastolica:
                messagebox.showerror("Error", "La sistólica debe ser mayor que la diastólica")
                return
            
            # Parsear fecha
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            
            # Calcular campos derivados
            anio = fecha.year
            mes = fecha.month
            semana_anio = fecha.isocalendar()[1]  # Semana del año (1-53)
            semana_mes = (fecha.day - 1) // 7 + 1  # Semana del mes (1-5)
            
            aniomes = anio * 100 + mes
            aniomessemana = anio * 1000 + mes * 10 + semana_mes
            anio_semana = anio * 100 + semana_anio
            
            # Crear objeto RegistroPresion
            registro = RegistroPresion(
                presion_fechahora=fecha,
                presion_sistolica=sistolica,
                presion_diastolica=diastolica,
                presion_pulso=pulso,
                presion_anio=anio,
                presion_aniomes=aniomes,
                presion_aniomessemana=aniomessemana,
                presion_anio_semana=anio_semana,
                presion_archivoorigen=origen,
                presion_fechacreacion=datetime.now(),
                presion_estado='Activo'
            )
            
            # Guardar en la base de datos
            self.servicio.insertar_registro(registro)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Éxito",
                f"Registro guardado correctamente!\n\n"
                f"Sistólica: {sistolica:.0f} mmHg\n"
                f"Diastólica: {diastolica:.0f} mmHg\n"
                f"Pulso: {pulso:.0f} lpm"
            )
            
            # Limpiar formulario
            self._limpiar_formulario()
            
        except ValueError as error:
            messagebox.showerror("Error", f"Datos inválidos: {str(error)}")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo guardar el registro: {str(error)}")
    
    def _limpiar_formulario(self):
        """
        Limpia todos los campos del formulario y establece valores por defecto.
        """
        self.entry_sistolica.delete(0, 'end')
        self.entry_diastolica.delete(0, 'end')
        self.entry_pulso.delete(0, 'end')
        self.entry_fecha.delete(0, 'end')
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.entry_sistolica.focus()