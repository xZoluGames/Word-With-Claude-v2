
from utils.logger import get_logger

logger = get_logger("info_general")

"""
Tab de Información General - Datos básicos del proyecto
"""

import customtkinter as ctk
from tkinter import messagebox

class InfoGeneralTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la pestaña de información general"""
        # Scroll frame con altura reducida
        scroll_frame = ctk.CTkScrollableFrame(self.parent, label_text="Datos del Proyecto", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Toggle para usar formato base
        base_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=8)
        base_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            base_frame, text="📋 Formato Base",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 5))
        
        self.app.usar_base_var = ctk.CTkCheckBox(
            base_frame, text="Usar plantilla base (3º AÑO)",
            font=ctk.CTkFont(size=12), command=self.app.toggle_formato_base
        )
        self.app.usar_base_var.pack(pady=(0, 10))
        
        # Campos organizados
        self.crear_campos(scroll_frame)
    
    def crear_campos(self, parent):
        """Crea los campos de entrada"""
        campos = [
            ("Institución Educativa", "institucion", "Colegio Privado Divina Esperanza"),
            ("Título del Proyecto", "titulo", "Ingrese el título de su investigación"),
            ("Categoría", "categoria", "Ciencia o Tecnología"),
            ("Ciclo", "ciclo", "Tercer año"),
            ("Curso", "curso", "3 BTI"),
            ("Énfasis", "enfasis", "Tecnología")
        ]
        
        # Crear campos en pares
        for i in range(0, len(campos), 2):
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # Primera columna
            if i < len(campos):
                self.crear_campo(row_frame, campos[i], side="left")
            
            # Segunda columna
            if i + 1 < len(campos):
                self.crear_campo(row_frame, campos[i + 1], side="right")
        
        # Campos largos
        campos_largos = [
            ("Área de Desarrollo", "area", "Especifique el área de desarrollo"),
            ("Estudiantes (separar con comas)", "estudiantes", "Nombre1 Apellido1, Nombre2 Apellido2"),
            ("Tutores (separar con comas)", "tutores", "Prof. Nombre Apellido, Dr. Nombre Apellido"),
            ("Director", "director", "Cristina Raichakowski"),
            ("Responsable", "responsable", "Nombre del responsable")
        ]
        
        for label, key, placeholder in campos_largos:
            field_frame = ctk.CTkFrame(parent, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(field_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=30)
            entry.pack(fill="x", pady=(3, 0))
            self.app.proyecto_data[key] = entry
    
    def crear_campo(self, parent, campo_data, side="left"):
        """Crea un campo individual"""
        label, key, placeholder = campo_data
        
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        if side == "left":
            field_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        else:
            field_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(field_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=30)
        entry.pack(fill="x", pady=(3, 0))
        self.app.proyecto_data[key] = entry
