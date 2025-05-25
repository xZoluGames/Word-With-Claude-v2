
from utils.logger import get_logger

logger = get_logger("formato_avanzado")

"""
Tab de Formato Avanzado - Configuración de estilos del documento
"""

import customtkinter as ctk
from tkinter import messagebox

class FormatoAvanzadoTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de formato avanzado"""
        scroll_frame = ctk.CTkScrollableFrame(self.parent, label_text="Configuración de Formato", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Sección de tipografía
        self.create_typography_section(scroll_frame)
        
        # Sección de espaciado
        self.create_spacing_section(scroll_frame)
        
        # Opciones de alineación
        self.create_alignment_section(scroll_frame)
        
        # Botón para aplicar configuración
        apply_btn = ctk.CTkButton(
            scroll_frame, text="✅ Aplicar Configuración", command=self.app.aplicar_formato,
            height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(pady=15)
    
    def create_typography_section(self, parent):
        """Crea la sección de tipografía"""
        tipo_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=8)
        tipo_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            tipo_frame, text="🔤 Tipografía",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        tipo_grid = ctk.CTkFrame(tipo_frame, fg_color="transparent")
        tipo_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Primera fila
        row1_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row1_tipo.pack(fill="x", pady=3)
        
        # Fuente del texto
        fuente_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        fuente_texto_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_texto_frame, text="Fuente texto:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.fuente_texto = ctk.CTkComboBox(
            fuente_texto_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.app.fuente_texto.set("Times New Roman")
        self.app.fuente_texto.pack(fill="x")
        
        # Tamaño del texto
        tamaño_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        tamaño_texto_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_texto_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.tamaño_texto = ctk.CTkComboBox(tamaño_texto_frame, values=["10", "11", "12", "13", "14"], height=25)
        self.app.tamaño_texto.set("12")
        self.app.tamaño_texto.pack(fill="x")
        
        # Segunda fila
        row2_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row2_tipo.pack(fill="x", pady=3)
        
        # Fuente de títulos
        fuente_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        fuente_titulo_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_titulo_frame, text="Fuente títulos:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.fuente_titulo = ctk.CTkComboBox(
            fuente_titulo_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.app.fuente_titulo.set("Times New Roman")
        self.app.fuente_titulo.pack(fill="x")
        
        # Tamaño de títulos
        tamaño_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        tamaño_titulo_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_titulo_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.tamaño_titulo = ctk.CTkComboBox(tamaño_titulo_frame, values=["12", "13", "14", "15", "16"], height=25)
        self.app.tamaño_titulo.set("14")
        self.app.tamaño_titulo.pack(fill="x")
    
    def create_spacing_section(self, parent):
        """Crea la sección de espaciado"""
        espaciado_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=8)
        espaciado_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            espaciado_frame, text="📏 Espaciado",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        espaciado_grid = ctk.CTkFrame(espaciado_frame, fg_color="transparent")
        espaciado_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        espaciado_row = ctk.CTkFrame(espaciado_grid, fg_color="transparent")
        espaciado_row.pack(fill="x", pady=3)
        
        # Interlineado
        interlineado_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        interlineado_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(interlineado_frame, text="Interlineado:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.interlineado = ctk.CTkComboBox(interlineado_frame, values=["1.0", "1.5", "2.0"], height=25)
        self.app.interlineado.set("2.0")
        self.app.interlineado.pack(fill="x")
        
        # Márgenes
        margen_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        margen_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(margen_frame, text="Márgenes (cm):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.margen = ctk.CTkComboBox(margen_frame, values=["2.0", "2.54", "3.0"], height=25)
        self.app.margen.set("2.54")
        self.app.margen.pack(fill="x")
    
    def create_alignment_section(self, parent):
        """Crea la sección de alineación"""
        align_frame = ctk.CTkFrame(parent, fg_color="darkred", corner_radius=8)
        align_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            align_frame, text="📐 Alineación",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        align_grid = ctk.CTkFrame(align_frame, fg_color="transparent")
        align_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Primera fila
        align_row = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row.pack(fill="x", pady=3)
        
        self.app.salto_pagina_var = ctk.CTkCheckBox(
            align_row, text="Salto de página entre secciones", font=ctk.CTkFont(size=12)
        )
        self.app.salto_pagina_var.select()
        self.app.salto_pagina_var.pack(side="left", padx=(10, 10))
        
        self.app.conservar_siguiente_var = ctk.CTkCheckBox(
            align_row, text="Conservar con siguiente", font=ctk.CTkFont(size=12)
        )
        self.app.conservar_siguiente_var.select()
        self.app.conservar_siguiente_var.pack(side="right", padx=(10, 10))
        
        # Segunda fila
        align_row2 = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row2.pack(fill="x", pady=3)
        
        self.app.justificado_var = ctk.CTkCheckBox(
            align_row2, text="Justificado", font=ctk.CTkFont(size=12)
        )
        self.app.justificado_var.select()
        self.app.justificado_var.pack(side="left", padx=(10, 10))
        
        self.app.sangria_var = ctk.CTkCheckBox(
            align_row2, text="Sangría primera línea", font=ctk.CTkFont(size=12)
        )
        self.app.sangria_var.select()
        self.app.sangria_var.pack(side="right", padx=(10, 10))
