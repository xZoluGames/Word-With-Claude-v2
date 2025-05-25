
from utils.logger import get_logger

logger = get_logger("font_manager")

"""
Font Manager - Gestión de fuentes para accesibilidad y diseño responsivo
"""

import customtkinter as ctk

class FontManager:
    """Gestor de fuentes para accesibilidad y diseño responsivo"""
    def __init__(self):
        self.base_size = 12
        self.scale = 1.0
        self.font_cache = {}
        
    def get_size(self, tipo="normal"):
        """Obtiene el tamaño de fuente según el tipo y escala actual"""
        sizes = {
            "tiny": int(8 * self.scale),
            "small": int(10 * self.scale),
            "normal": int(12 * self.scale),
            "medium": int(14 * self.scale),
            "large": int(16 * self.scale),
            "xlarge": int(20 * self.scale),
            "title": int(24 * self.scale)
        }
        return sizes.get(tipo, self.base_size)
    
    def get_font(self, tipo="normal", weight="normal", family=None):
        """Obtiene una fuente CTk con el tamaño y peso especificados"""
        size = self.get_size(tipo)
        cache_key = f"{tipo}_{weight}_{family}_{size}"
        
        if cache_key not in self.font_cache:
            if family is None:
                family = "Segoe UI" if ctk.get_appearance_mode() == "Light" else "Helvetica"
            
            self.font_cache[cache_key] = ctk.CTkFont(
                family=family,
                size=size,
                weight=weight
            )
        
        return self.font_cache[cache_key]
    
    def increase_scale(self):
        """Aumenta la escala de fuentes"""
        if self.scale < 1.5:
            self.scale += 0.1
            self.font_cache.clear()
            return True
        return False
            
    def decrease_scale(self):
        """Disminuye la escala de fuentes"""
        if self.scale > 0.7:
            self.scale -= 0.1
            self.font_cache.clear()
            return True
        return False
    
    def reset_scale(self):
        """Restablece la escala por defecto"""
        self.scale = 1.0
        self.font_cache.clear()
    
    def get_current_scale(self):
        """Obtiene la escala actual"""
        return self.scale
