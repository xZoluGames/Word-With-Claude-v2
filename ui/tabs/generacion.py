
from utils.logger import get_logger

logger = get_logger("generacion")

"""
Tab de Generación - Opciones y validación del documento final
"""

import customtkinter as ctk
from tkinter import messagebox

class GeneracionTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de generación"""
        # Contenedor principal para toda la pestaña
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Panel superior - Opciones
        self.create_options_panel(main_container)
        
        # Panel inferior - Validación
        self.create_validation_panel(main_container)
        
        # Inicializar con mensaje de bienvenida
        self.app.mostrar_bienvenida_validacion()
    
    def create_options_panel(self, parent):
        """Crea el panel de opciones de generación"""
        # Frame contenedor para opciones
        options_container = ctk.CTkFrame(parent, fg_color="transparent")
        options_container.pack(fill="x", padx=20, pady=(20, 10))
        
        top_frame = ctk.CTkFrame(options_container, corner_radius=15, height=200)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        
        options_title = ctk.CTkLabel(
            top_frame, text="⚙️ Opciones de Generación",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15))
        
        # Grid de opciones
        options_grid = ctk.CTkFrame(top_frame, fg_color="transparent")
        options_grid.pack(padx=30, pady=(0, 20))
        
        # Columnas
        col1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=20)
        
        col2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=20)
        
        # Opciones columna 1
        self.app.incluir_portada = ctk.CTkCheckBox(
            col1, text="📄 Incluir Portada",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_portada.select()
        self.app.incluir_portada.pack(anchor="w", pady=5)
        
        self.app.incluir_indice = ctk.CTkCheckBox(
            col1, text="📑 Incluir Índice",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_indice.select()
        self.app.incluir_indice.pack(anchor="w", pady=5)
        
        # Opciones columna 2
        self.app.incluir_agradecimientos = ctk.CTkCheckBox(
            col2, text="🙏 Incluir Agradecimientos",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_agradecimientos.pack(anchor="w", pady=5)
        
        self.app.numeracion_paginas = ctk.CTkCheckBox(
            col2, text="📊 Numeración de páginas",
            font=ctk.CTkFont(size=14)
        )
        self.app.numeracion_paginas.select()
        self.app.numeracion_paginas.pack(anchor="w", pady=5)
    
    def create_validation_panel(self, parent):
        """Crea el panel de validación"""
        # Frame contenedor para el panel de validación
        validation_container = ctk.CTkFrame(parent, fg_color="transparent")
        validation_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        bottom_frame = ctk.CTkFrame(validation_container, corner_radius=15)
        bottom_frame.pack(fill="both", expand=True)
        
        # Header con tabs
        header_frame = ctk.CTkFrame(bottom_frame, height=50, fg_color="gray25")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Tabs de validación
        self.app.validation_tabs = ctk.CTkSegmentedButton(
            header_frame,
            values=["🔍 Validación", "📋 Logs", "📊 Estadísticas", "💡 Sugerencias"],
            command=self.app.cambiar_tab_validacion
        )
        self.app.validation_tabs.pack(side="left", padx=15, pady=10)
        self.app.validation_tabs.set("🔍 Validación")
        
        # Botón de limpiar
        clear_btn = ctk.CTkButton(
            header_frame, text="🗑️", width=35, height=35,
            command=self.app.limpiar_validacion,
            fg_color="transparent", hover_color="gray30"
        )
        clear_btn.pack(side="right", padx=15)
        
        # Contenedor de contenido
        self.app.validation_container = ctk.CTkFrame(bottom_frame)
        self.app.validation_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Área de texto
        self.app.validation_text = ctk.CTkTextbox(
            self.app.validation_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="gray10"
        )
        self.app.validation_text.pack(fill="both", expand=True)
        
        # Panel de progreso
        self.create_progress_panel(bottom_frame)
    
    def create_progress_panel(self, parent):
        """Crea el panel de progreso"""
        progress_frame = ctk.CTkFrame(parent, height=80)
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))
        progress_frame.pack_propagate(False)
        
        # Etiqueta de estado
        self.app.status_label = ctk.CTkLabel(
            progress_frame, text="🟢 Listo para validar",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.app.status_label.pack(pady=(10, 5))
        
        # Barra de progreso
        self.app.progress = ctk.CTkProgressBar(
            progress_frame, height=20,
            progress_color="green"
        )
        self.app.progress.pack(fill="x", padx=20, pady=(0, 5))
        self.app.progress.set(0)
        
        # Subtareas
        self.app.subtask_label = ctk.CTkLabel(
            progress_frame, text="",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        self.app.subtask_label.pack()