
from utils.logger import get_logger

logger = get_logger("help_dialog")

"""
Help Dialog - Diálogo de ayuda y guías
"""

import customtkinter as ctk

class HelpDialog:
    def __init__(self, parent_app):
        self.app = parent_app
    
    def show(self):
        """Muestra el diálogo de ayuda completa"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("📖 Guía Profesional Completa")
        self.window.geometry("1000x800")
        
        main_frame = ctk.CTkFrame(self.window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, text="📖 GUÍA PROFESIONAL COMPLETA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        self.text_widget = ctk.CTkTextbox(main_frame, wrap="word", font=ctk.CTkFont(size=12))
        self.text_widget.pack(expand=True, fill="both", padx=20, pady=(10, 20))
        
        self.load_help_content()
        self.text_widget.configure(state="disabled")
    
    def load_help_content(self):
        """Carga el contenido de ayuda"""
        content = """
🎓 GENERADOR PROFESIONAL DE PROYECTOS ACADÉMICOS - VERSIÓN 2.0

═══════════════════════════════════════════════════════════════════

🚀 CARACTERÍSTICAS PROFESIONALES AVANZADAS:
- Formato Word con niveles de esquema para índices automáticos
- Saltos de página inteligentes entre secciones principales
- Control profesional de líneas viudas y huérfanas
- Sistema completo de guardado/carga de proyectos
- Auto-guardado automático cada 5 minutos
- Estadísticas en tiempo real (palabras, secciones, referencias)
- Exportación/importación de configuraciones
- Gestión avanzada de imágenes personalizadas
- Atajos de teclado para flujo de trabajo eficiente

═══════════════════════════════════════════════════════════════════

⌨️ ATAJOS DE TECLADO PROFESIONALES:
- Ctrl+S: Guardar proyecto completo
- Ctrl+O: Cargar proyecto existente
- Ctrl+N: Crear nuevo proyecto
- F5: Validar proyecto rápidamente
- F9: Generar documento final
- Ctrl+Q: Salir de la aplicación

[... resto del contenido de ayuda ...]
"""
        self.text_widget.insert("1.0", content)
    
    def show_contextual_help(self, section):
        """Muestra ayuda contextual específica"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title(f"💡 Ayuda - {section}")
        self.window.geometry("600x400")
        
        # Contenido específico según sección
        # ... implementar contenido contextual ...
