
from utils.logger import get_logger

logger = get_logger("tooltip")

"""
ToolTip Widget - Tooltips para widgets de CustomTkinter
"""

import customtkinter as ctk

class ToolTip:
    """Clase para crear tooltips en widgets de CustomTkinter"""
    def __init__(self, widget, text='tooltip'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.tooltip = None
    
    def on_enter(self, event=None):
        """Muestra el tooltip cuando el mouse entra al widget"""
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        # Crear ventana del tooltip
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        
        # Posicionar tooltip
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Frame del tooltip con estilo
        tooltip_frame = ctk.CTkFrame(
            self.tooltip, 
            fg_color="gray20", 
            corner_radius=6,
            border_width=1,
            border_color="gray40"
        )
        tooltip_frame.pack()
        
        # Texto del tooltip
        label = ctk.CTkLabel(
            tooltip_frame, 
            text=self.text,
            font=ctk.CTkFont(size=11),
            text_color="white",
            justify="left",
            wraplength=300
        )
        label.pack(padx=8, pady=5)
        
        # Asegurar que el tooltip esté sobre otros widgets
        self.tooltip.lift()
    
    def on_leave(self, event=None):
        """Oculta el tooltip cuando el mouse sale del widget"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
