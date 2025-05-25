
from utils.logger import get_logger

logger = get_logger("components")

"""
Componentes - Componentes reutilizables para la interfaz de usuario
"""

import customtkinter as ctk
from tkinter import messagebox

class StatsPanel(ctk.CTkFrame):
    """Panel de estadísticas en tiempo real"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de estadísticas"""
        self.stats_label = ctk.CTkLabel(
            self, text="📊 Palabras: 0 | Secciones: 0/0 | Referencias: 0",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.stats_label.pack(pady=10)
    
    def update_stats(self, words, sections_complete, sections_total, references):
        """Actualiza las estadísticas mostradas"""
        stats_text = f"📊 Palabras: {words} | Secciones: {sections_complete}/{sections_total} | Referencias: {references}"
        self.stats_label.configure(text=stats_text)

class FormatPanel(ctk.CTkFrame):
    """Panel de configuración de formato"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de formato"""
        title_label = ctk.CTkLabel(
            self, text="🎨 Configuración de Formato",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Fuente
        font_frame = ctk.CTkFrame(self, fg_color="transparent")
        font_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(font_frame, text="Fuente:").pack(side="left")
        self.font_combo = ctk.CTkComboBox(
            font_frame, values=["Times New Roman", "Arial", "Calibri"],
            width=150
        )
        self.font_combo.pack(side="right")
        
        # Tamaño
        size_frame = ctk.CTkFrame(self, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(size_frame, text="Tamaño:").pack(side="left")
        self.size_combo = ctk.CTkComboBox(
            size_frame, values=["10", "11", "12", "13", "14"],
            width=80
        )
        self.size_combo.pack(side="right")
    
    def get_format_config(self):
        """Retorna la configuración actual de formato"""
        return {
            'fuente': self.font_combo.get(),
            'tamaño': int(self.size_combo.get())
        }
    
    def set_format_config(self, config):
        """Aplica una configuración de formato"""
        if 'fuente' in config:
            self.font_combo.set(config['fuente'])
        if 'tamaño' in config:
            self.size_combo.set(str(config['tamaño']))

class ValidationPanel(ctk.CTkFrame):
    """Panel de validación de proyectos"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de validación"""
        title_label = ctk.CTkLabel(
            self, text="🔍 Validación del Proyecto",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 15))
        
        self.validation_text = ctk.CTkTextbox(
            self, height=200, font=ctk.CTkFont(size=11)
        )
        self.validation_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.progress_bar = ctk.CTkProgressBar(self, height=15)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))
    
    def show_validation_results(self, results):
        """Muestra los resultados de validación"""
        self.validation_text.delete("1.0", "end")
        self.validation_text.insert("1.0", results)
        
    def update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.set(value)