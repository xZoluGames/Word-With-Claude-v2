
from utils.logger import get_logger

logger = get_logger("preview_window")

"""
Preview Window - Ventana de vista previa del documento
"""

import customtkinter as ctk

class PreviewWindow:
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        
    def show(self):
        """Muestra la ventana de preview"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.app.actualizar_preview()
    
    def create_window(self):
        """Crea la ventana de vista previa"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("👁️ Vista Previa del Documento")
        
        # Posicionar a la derecha
        main_x = self.app.root.winfo_x()
        main_y = self.app.root.winfo_y()
        main_width = self.app.root.winfo_width()
        
        self.window.geometry(f"400x800+{main_x + main_width + 10}+{main_y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Opciones
        self.create_options(main_frame)
        
        # Área de preview
        self.create_preview_area(main_frame)
        
        # Configurar cierre
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
    
    def create_header(self, parent):
        """Crea el header de la ventana"""
        header_frame = ctk.CTkFrame(parent, height=50, fg_color="gray25")
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame, text="📄 Vista Previa del Documento",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15, pady=10)
        
        refresh_btn = ctk.CTkButton(
            header_frame, text="🔄", width=35, height=35,
            command=self.app.actualizar_preview,
            font=ctk.CTkFont(size=16)
        )
        refresh_btn.pack(side="right", padx=15)
    
    def create_options(self, parent):
        """Crea las opciones de vista"""
        options_frame = ctk.CTkFrame(parent, height=40)
        options_frame.pack(fill="x", pady=(0, 10))
        options_frame.pack_propagate(False)
        
        self.app.preview_mode = ctk.CTkSegmentedButton(
            options_frame,
            values=["📝 Texto", "🎨 Formato", "📊 Estructura"],
            command=self.app.cambiar_modo_preview
        )
        self.app.preview_mode.pack(padx=10, pady=5)
        self.app.preview_mode.set("📝 Texto")
    
    def create_preview_area(self, parent):
        """Crea el área de preview"""
        self.app.preview_text = ctk.CTkTextbox(
            parent, wrap="word",
            font=ctk.CTkFont(family="Georgia", size=12),
            state="disabled"
        )
        self.app.preview_text.pack(fill="both", expand=True)
    
    def hide(self):
        """Oculta la ventana"""
        if self.window:
            self.window.withdraw()
