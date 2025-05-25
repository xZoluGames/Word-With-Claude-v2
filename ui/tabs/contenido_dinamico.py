
from utils.logger import get_logger

logger = get_logger("contenido_dinamico")

"""
Tab de Contenido Dinámico - Gestión de secciones y contenido
"""

import customtkinter as ctk
from tkinter import messagebox
from ..dialogs import SeccionDialog

class ContenidoDinamicoTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de contenido dinámico"""
        # Frame principal
        paned_window = ctk.CTkFrame(self.parent, fg_color="transparent")
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de control izquierdo
        self.create_control_panel(paned_window)
        
        # Panel de contenido derecho
        self.create_content_panel(paned_window)
        
        # Actualizar lista y crear pestañas
        self.app.actualizar_lista_secciones()
        self.app.crear_pestanas_contenido()
    
    def create_control_panel(self, parent):
        """Crea el panel de control de secciones"""
        self.app.control_frame = ctk.CTkFrame(parent, width=320, corner_radius=10)
        self.app.control_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Header del panel
        header_frame = ctk.CTkFrame(self.app.control_frame, fg_color="gray25", height=45)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Botón colapsar
        self.app.sidebar_collapsed = False
        collapse_btn = ctk.CTkButton(
            header_frame, text="◀", width=30, height=30,
            command=self.app.toggle_sidebar,
            font=ctk.CTkFont(size=14)
        )
        collapse_btn.pack(side="left", padx=5, pady=7)
        
        title_label = ctk.CTkLabel(
            header_frame, text="🛠️ Gestión de Secciones",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=(5, 0))
        
        # Frame de búsqueda
        self.create_search_frame()
        
        # Botones de gestión
        self.create_management_buttons()
        
        # Lista de secciones
        self.create_sections_list()
    
    def create_search_frame(self):
        """Crea el frame de búsqueda"""
        search_frame = ctk.CTkFrame(self.app.control_frame, height=45)
        search_frame.pack(fill="x", padx=8, pady=(8, 4))
        
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=12))
        search_icon.pack(side="left", padx=(8, 4))
        
        self.app.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar sección...",
            height=30, font=ctk.CTkFont(size=11)
        )
        self.app.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.app.search_entry.bind("<KeyRelease>", self.app.filtrar_secciones)
    
    def create_management_buttons(self):
        """Crea los botones de gestión de secciones"""
        btn_frame = ctk.CTkFrame(self.app.control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=(4, 8))
        
        # Primera fila de botones
        btn_row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=2)
        
        add_btn = ctk.CTkButton(
            btn_row1, text="➕ Agregar", command=self.app.agregar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        add_btn.pack(side="left", padx=(0, 4))
        
        remove_btn = ctk.CTkButton(
            btn_row1, text="➖ Quitar", command=self.app.quitar_seccion,
            width=90, height=30, fg_color="red", hover_color="darkred",
            font=ctk.CTkFont(size=11)
        )
        remove_btn.pack(side="left", padx=(0, 4))
        
        edit_btn = ctk.CTkButton(
            btn_row1, text="✏️ Editar", command=self.app.editar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        edit_btn.pack(side="left")
        
        # Segunda fila
        btn_row2 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row2.pack(fill="x", pady=2)
        
        up_btn = ctk.CTkButton(
            btn_row2, text="⬆️ Subir", command=self.app.subir_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        up_btn.pack(side="left", padx=(0, 4))
        
        down_btn = ctk.CTkButton(
            btn_row2, text="⬇️ Bajar", command=self.app.bajar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        down_btn.pack(side="left", padx=(0, 4))
        
        preview_btn = ctk.CTkButton(
            btn_row2, text="👁️ Preview", command=self.app.mostrar_preview,
            width=90, height=30, fg_color="purple", hover_color="darkviolet",
            font=ctk.CTkFont(size=11)
        )
        preview_btn.pack(side="left")
    
    def create_sections_list(self):
        """Crea la lista de secciones"""
        list_label = ctk.CTkLabel(
            self.app.control_frame, text="📋 Secciones Activas:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        list_label.pack(anchor="w", padx=8, pady=(8, 4))
        
        self.app.secciones_listbox = ctk.CTkScrollableFrame(
            self.app.control_frame, label_text="",
            fg_color="gray15", corner_radius=8
        )
        self.app.secciones_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    
    def create_content_panel(self, parent):
        """Crea el panel de contenido"""
        self.app.content_container = ctk.CTkFrame(parent, corner_radius=10)
        self.app.content_container.pack(side="right", fill="both", expand=True)
        
        # Breadcrumb navigation
        breadcrumb_frame = ctk.CTkFrame(self.app.content_container, height=35, fg_color="gray25")
        breadcrumb_frame.pack(fill="x", padx=8, pady=(8, 4))
        breadcrumb_frame.pack_propagate(False)
        
        self.app.breadcrumb_label = ctk.CTkLabel(
            breadcrumb_frame, text="📍 Navegación: ",
            font=ctk.CTkFont(size=11), anchor="w"
        )
        self.app.breadcrumb_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Sub-tabview
        self.app.content_tabview = ctk.CTkTabview(
            self.app.content_container,
            segmented_button_selected_color="darkblue",
            segmented_button_selected_hover_color="blue"
        )
        self.app.content_tabview.pack(expand=True, fill="both", padx=8, pady=(4, 8))
