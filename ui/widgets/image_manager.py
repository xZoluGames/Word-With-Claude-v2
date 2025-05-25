
from utils.logger import get_logger

logger = get_logger("image_manager")

"""
Image Manager - Diálogo de gestión de imágenes
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os

class ImageManagerDialog:
    def __init__(self, parent_app):
        self.app = parent_app
        
    def show(self):
        """Muestra el diálogo de gestión de imágenes"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("🖼️ Gestión de Imágenes")
        self.window.geometry("600x500")
        self.window.transient(self.app.root)
        self.window.grab_set()
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main_frame = ctk.CTkFrame(self.window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="🖼️ Gestión de Imágenes del Documento",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Estado de imágenes base
        self.create_status_section(main_frame)
        
        # Sección de carga personalizada
        self.create_custom_section(main_frame)
        
        # Configuración de marca de agua
        self.create_watermark_section(main_frame)
        
        # Información adicional
        self.create_info_section(main_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_status_section(self, parent):
        """Crea la sección de estado"""
        status_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_title = ctk.CTkLabel(
            status_frame, text="📁 Estado de Imágenes Base",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(pady=(10, 5))
        
        # Estado del encabezado
        enc_status = "✅ Encontrado" if self.app.ruta_encabezado else "❌ No encontrado"
        enc_label = ctk.CTkLabel(
            status_frame, text=f"Encabezado.png: {enc_status}",
            font=ctk.CTkFont(size=12)
        )
        enc_label.pack(pady=2)
        
        # Estado de la insignia
        ins_status = "✅ Encontrado" if self.app.ruta_insignia else "❌ No encontrado"
        ins_label = ctk.CTkLabel(
            status_frame, text=f"Insignia.png: {ins_status}",
            font=ctk.CTkFont(size=12)
        )
        ins_label.pack(pady=(2, 10))
    
    def create_custom_section(self, parent):
        """Crea la sección de carga personalizada"""
        custom_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=10)
        custom_frame.pack(fill="x", pady=(0, 20))
        
        custom_title = ctk.CTkLabel(
            custom_frame, text="📤 Cargar Imágenes Personalizadas",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        custom_title.pack(pady=(15, 10))
        
        # Botones de carga
        btn_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        enc_btn = ctk.CTkButton(
            btn_frame, text="📋 Cargar Encabezado", 
            command=lambda: self.app.cargar_imagen_personalizada("encabezado", self.window),
            width=200, height=35
        )
        enc_btn.pack(side="left", padx=(0, 10))
        
        ins_btn = ctk.CTkButton(
            btn_frame, text="🏛️ Cargar Insignia", 
            command=lambda: self.app.cargar_imagen_personalizada("insignia", self.window),
            width=200, height=35
        )
        ins_btn.pack(side="right", padx=(10, 0))
        
        # Estado de imágenes personalizadas
        self.create_custom_status(parent)
    
    def create_custom_status(self, parent):
        """Crea el estado de imágenes personalizadas"""
        custom_status_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        custom_status_frame.pack(fill="x", pady=(0, 20))
        
        custom_status_title = ctk.CTkLabel(
            custom_status_frame, text="🎨 Imágenes Personalizadas Cargadas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        custom_status_title.pack(pady=(10, 5))
        
        self.app.enc_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Encabezado: {'✅ Cargado' if self.app.encabezado_personalizado else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.app.enc_custom_label.pack(pady=2)
        
        self.app.ins_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Insignia: {'✅ Cargado' if self.app.insignia_personalizada else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.app.ins_custom_label.pack(pady=(2, 10))
    
    def create_watermark_section(self, parent):
        """Crea la sección de configuración de marca de agua"""
        watermark_frame = ctk.CTkFrame(parent, fg_color="purple", corner_radius=10)
        watermark_frame.pack(fill="x", pady=(0, 20))
        
        watermark_title = ctk.CTkLabel(
            watermark_frame, text="⚙️ Configuración de Marca de Agua",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        watermark_title.pack(pady=(15, 10))
        
        # Control de opacidad
        opacity_frame = ctk.CTkFrame(watermark_frame, fg_color="transparent")
        opacity_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            opacity_frame, text="Transparencia:",
            font=ctk.CTkFont(size=12), text_color="white"
        ).pack(side="left", padx=(0, 10))
        
        self.app.opacity_slider = ctk.CTkSlider(
            opacity_frame, from_=0.1, to=1.0,
            command=self.app.actualizar_opacidad_preview
        )
        self.app.opacity_slider.set(self.app.watermark_opacity)
        self.app.opacity_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.app.opacity_label = ctk.CTkLabel(
            opacity_frame, text=f"{int(self.app.watermark_opacity * 100)}%",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.app.opacity_label.pack(side="left")
        
        # Modo de encabezado
        mode_frame = ctk.CTkFrame(watermark_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            mode_frame, text="Modo:",
            font=ctk.CTkFont(size=12), text_color="white"
        ).pack(side="left", padx=(0, 10))
        
        self.app.mode_var = ctk.StringVar(value=self.app.watermark_mode)
        
        watermark_radio = ctk.CTkRadioButton(
            mode_frame, text="Marca de Agua",
            variable=self.app.mode_var, value="watermark",
            text_color="white"
        )
        watermark_radio.pack(side="left", padx=(0, 20))
        
        normal_radio = ctk.CTkRadioButton(
            mode_frame, text="Normal",
            variable=self.app.mode_var, value="normal",
            text_color="white"
        )
        normal_radio.pack(side="left")
        
        # Estirar al ancho
        self.app.stretch_var = ctk.CTkCheckBox(
            watermark_frame, text="Estirar al ancho de página",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.app.stretch_var.select() if self.app.watermark_stretch else self.app.stretch_var.deselect()
        self.app.stretch_var.pack(pady=(0, 15))
    
    def create_info_section(self, parent):
        """Crea la sección de información"""
        info_frame = ctk.CTkFrame(parent, fg_color="green", corner_radius=10)
        info_frame.pack(fill="x")
        
        info_text = """💡 INFORMACIÓN IMPORTANTE:
- Las imágenes base se buscan en: /resources/images/
- Las imágenes personalizadas tienen prioridad sobre las base
- Formatos soportados: PNG, JPG, JPEG
- Tamaño recomendado: Encabezado 600x100px, Insignia 100x100px"""
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=10),
            justify="left", wraplength=550, text_color="white"
        )
        info_label.pack(padx=15, pady=10)
    
    def create_action_buttons(self, parent):
        """Crea los botones de acción"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", pady=(10, 0))
        
        reset_btn = ctk.CTkButton(
            action_frame, text="🔄 Restablecer", 
            command=lambda: self.app.restablecer_imagenes(self.window),
            width=120, height=35, fg_color="red", hover_color="darkred"
        )
        reset_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            action_frame, text="✅ Cerrar", 
            command=self.window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
