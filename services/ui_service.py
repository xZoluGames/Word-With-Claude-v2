# services/ui_service.py
"""
Servicio de UI - Maneja operaciones complejas de interfaz
"""

import os
import customtkinter as ctk
from tkinter import messagebox
from config.settings import BUTTON_COLORS
from utils.logger import get_logger

logger = get_logger('UIService')

class UIService:
    """Servicio para operaciones de UI"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def create_header(self, parent):
        """Crea el header completo de la aplicación"""
        header_frame = ctk.CTkFrame(parent, height=120, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 Generador de Proyectos Académicos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Crear botones
        self._create_header_buttons(header_frame)
    
    def _create_header_buttons(self, parent):
        """Crea los botones del header"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # Primera fila de botones
        btn_row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=(0, 5))
        
        buttons_config = [
            ("📖 Guía", self.app.mostrar_instrucciones, None),
            ("📋 Plantilla", self.app.cargar_documento_base, BUTTON_COLORS['purple']),
            ("💾 Guardar", self.app.guardar_proyecto, BUTTON_COLORS['green']),
            ("📂 Cargar", self.app.cargar_proyecto, BUTTON_COLORS['blue'])
        ]
        
        for text, command, color in buttons_config:
            btn = ctk.CTkButton(
                btn_row1, text=text, command=command,
                width=80, height=30,
                fg_color=color
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Estadísticas
        self.app.stats_label = ctk.CTkLabel(
            btn_row1, text="📊 Palabras: 0 | Secciones: 0/0 | Referencias: 0",
            font=ctk.CTkFont(size=11), text_color="gray70"
        )
        self.app.stats_label.pack(side="right", padx=(5, 0))
        
        # Segunda fila
        btn_row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row2.pack(fill="x")
        
        # Botón generar
        self.app.generate_btn = ctk.CTkButton(
            btn_row2, text="📄 Generar Documento", 
            command=self.app.generar_documento_async,
            width=140, height=30,
            fg_color=BUTTON_COLORS['green']
        )
        self.app.generate_btn.pack(side="right", padx=(5, 0))
    
    def configurar_ventana_responsiva(self):
        """Configura la ventana según el tamaño de pantalla"""
        screen_width = self.app.root.winfo_screenwidth()
        screen_height = self.app.root.winfo_screenheight()
        
        # Calcular tamaño óptimo
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Limitar tamaños
        window_width = max(1000, min(window_width, 1600))
        window_height = max(600, min(window_height, 900))
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.app.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        logger.info(f"Ventana configurada: {window_width}x{window_height}")
    
    def mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida"""
        self.app.root.after(1000, lambda: messagebox.showinfo(
            "🎓 ¡Bienvenido!",
            "Generador de Proyectos Académicos v2.0\n\n"
            "✨ Sistema completamente refactorizado\n"
            "🚀 Mejor rendimiento y organización\n"
            "📚 Todas las funciones disponibles\n\n"
            "Presiona F1 para ver la guía completa"
        ))
    
    def buscar_imagenes_base(self):
        """Busca imágenes base en resources"""
        try:
            recursos_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      "resources", "images")
            
            if not os.path.exists(recursos_dir):
                os.makedirs(recursos_dir)
                logger.info(f"Directorio creado: {recursos_dir}")
            
            # Buscar encabezado
            for filename in ['Encabezado.png', 'encabezado.png']:
                path = os.path.join(recursos_dir, filename)
                if os.path.exists(path):
                    self.app.ruta_encabezado = path
                    logger.info(f"Encabezado encontrado: {filename}")
                    break
            
            # Buscar insignia
            for filename in ['Insignia.png', 'insignia.png']:
                path = os.path.join(recursos_dir, filename)
                if os.path.exists(path):
                    self.app.ruta_insignia = path
                    logger.info(f"Insignia encontrada: {filename}")
                    break
                    
        except Exception as e:
            logger.error(f"Error buscando imágenes: {e}")
    
    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un mensaje al usuario"""
        messagebox.showinfo(titulo, mensaje)
    
    def agregar_tooltips(self):
        """Agrega tooltips a elementos importantes"""
        # Por implementar
        pass