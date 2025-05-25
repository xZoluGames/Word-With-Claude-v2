"""
Ventana principal - Coordinador principal de la aplicación
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
from datetime import datetime
from PIL import Image
from core.state_manager import state_manager
# Imports de módulos internos
from core.project_manager import ProjectManager
from core.document_generator import DocumentGenerator
from core.validator import ProjectValidator
from modules.citations import CitationProcessor
from modules.references import ReferenceManager
from modules.sections import SectionManager

# Imports de UI
from .widgets import FontManager, ToolTip, PreviewWindow, ImageManagerDialog
from .tabs import (
    InfoGeneralTab, ContenidoDinamicoTab, CitasReferenciasTab,
    FormatoAvanzadoTab, GeneracionTab
)
from .dialogs import SeccionDialog, HelpDialog
from utils.logger import get_logger
logger = get_logger('MainWindow')
class ProyectoAcademicoGenerator:
    """Clase principal del generador de proyectos académicos"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎓 Generador de Proyectos Académicos - Versión Avanzada")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # MOVER _init_variables() ANTES de _init_state_manager()
        self._init_variables()  # Mover esta línea aquí
        self._init_managers()
        self._init_state_manager()  # Ahora puede acceder a formato_config
        self._init_ui_components()
        
        # Configurar ventana y UI
        self.configurar_ventana_responsiva()
        self.configurar_atajos_accesibilidad()
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
        # Iniciar servicios
        self.mostrar_bienvenida()
        self.actualizar_estadisticas()
        self.project_manager.auto_save_project(self)
    def _init_state_manager(self):
        """Inicializa y configura el gestor de estado centralizado."""
        from utils.logger import get_logger
        logger = get_logger('MainWindow')
        
        # Cargar estado inicial
        initial_state = {
            'formato_config': self.formato_config,
            'secciones_disponibles': self.secciones_disponibles,
            'secciones_activas': self.secciones_activas
        }
        
        state_manager.update_state(**initial_state)
        
        # Suscribir a cambios de estado
        state_manager.subscribe(self._on_state_change)
        
        logger.info("StateManager integrado")

    def _on_state_change(self, new_state):
        """Callback cuando cambia el estado global."""
        # Actualizar UI según los cambios
        # Por ejemplo, actualizar estadísticas
        self.actualizar_estadisticas()
    def _init_managers(self):
        """Inicializa los gestores y procesadores"""
        from template_manager import obtener_template_manager
        
        self.template_manager = obtener_template_manager()
        self.project_manager = ProjectManager()
        self.document_generator = DocumentGenerator()
        self.validator = ProjectValidator()
        self.citation_processor = CitationProcessor()
        self.reference_manager = ReferenceManager()
        self.section_manager = SectionManager()
        self.font_manager = FontManager()
    
    def _init_variables(self):
        """Inicializa las variables de la aplicación"""
        # Datos del proyecto
        self.proyecto_data = {}
        self.referencias = []
        self.documento_base = None
        self.usar_formato_base = False
        
        # Variables para imágenes
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        self.ruta_encabezado = None
        self.ruta_insignia = None
        
        # Configuración de marca de agua
        self.watermark_opacity = 0.3
        self.watermark_stretch = True
        self.watermark_mode = 'watermark'
        
        # Secciones dinámicas
        self.secciones_disponibles = self.get_secciones_iniciales()
        self.secciones_activas = list(self.secciones_disponibles.keys())
        self.content_texts = {}
        
        # Configuración de formato
        self.formato_config = {
            'fuente_texto': 'Times New Roman',
            'tamaño_texto': 12,
            'fuente_titulo': 'Times New Roman', 
            'tamaño_titulo': 14,
            'interlineado': 2.0,
            'margen': 2.54,
            'justificado': True,
            'sangria': True
        }
        
        # Estadísticas
        self.stats = {
            'total_words': 0,
            'total_chars': 0,
            'sections_completed': 0,
            'references_added': 0
        }
        
        # Buscar imágenes base
        self.buscar_imagenes_base()
    
    def _init_ui_components(self):
        """Inicializa componentes de UI"""
        self.preview_window = PreviewWindow(self)
        self.image_manager = ImageManagerDialog(self)
        self.help_dialog = HelpDialog(self)
    
    def configurar_ventana_responsiva(self):
        """Configura la ventana según el tamaño de pantalla"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        window_width = max(1000, min(window_width, 1600))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        if screen_width < 1366:
            self.modo_compacto = True
            self.ajustar_modo_compacto()
        elif screen_width > 1920:
            self.modo_expandido = True
            self.ajustar_modo_expandido()
        else:
            self.modo_compacto = False
            self.modo_expandido = False
    
    def ajustar_modo_compacto(self):
        """Ajusta la interfaz para pantallas pequeñas"""
        self.padding_x = 5
        self.padding_y = 5
        self.font_manager.scale = 0.9
        self.default_entry_height = 30
        self.default_button_height = 35
    
    def ajustar_modo_expandido(self):
        """Ajusta la interfaz para pantallas grandes"""
        self.padding_x = 20
        self.padding_y = 15
        self.font_manager.scale = 1.1
        self.default_entry_height = 40
        self.default_button_height = 45
    
    def configurar_atajos_accesibilidad(self):
        """Configura atajos de teclado para accesibilidad"""
        # Navegación entre pestañas
        self.root.bind('<Control-Tab>', self.siguiente_pestaña)
        self.root.bind('<Control-Shift-Tab>', self.pestaña_anterior)
        
        # Zoom de interfaz
        self.root.bind('<Control-plus>', self.aumentar_zoom)
        self.root.bind('<Control-equal>', self.aumentar_zoom)
        self.root.bind('<Control-minus>', self.disminuir_zoom)
        self.root.bind('<Control-0>', self.restablecer_zoom)
        
        # Navegación entre secciones
        self.root.bind('<Alt-Up>', lambda e: self.subir_seccion())
        self.root.bind('<Alt-Down>', lambda e: self.bajar_seccion())
        
        # Acceso rápido
        self.root.bind('<F1>', lambda e: self.mostrar_instrucciones())
        self.root.bind('<F2>', lambda e: self.ir_a_seccion_actual())
        self.root.bind('<F3>', lambda e: self.buscar_en_contenido())
        self.root.bind('<F4>', lambda e: self.mostrar_preview() if hasattr(self, 'mostrar_preview') else None)
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self._create_header(main_container)
        
        # Content container
        content_container = ctk.CTkFrame(main_container, corner_radius=10)
        content_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Tabview principal
        self.tabview = ctk.CTkTabview(content_container, width=1100, height=520)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Crear pestañas
        self._create_tabs()
        
        # Agregar menú de accesibilidad
        self._create_accessibility_menu(main_container)
        
        # Agregar tooltips después de crear widgets
        self.root.after(1000, self.agregar_tooltips)
    
    def _create_header(self, parent):
        """Crea el header con título y botones principales"""
        header_frame = ctk.CTkFrame(parent, height=120, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Título
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 Generador de Proyectos Académicos",
            font=self.font_manager.get_font("title", "bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Botones principales
        self._create_header_buttons(header_frame)
    
    def _create_header_buttons(self, parent):
            """Crea los botones del header"""
            from config.settings import UI_COLORS, BUTTON_COLORS
            button_frame = ctk.CTkFrame(parent, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(5, 10))
            
            # Primera fila
            btn_row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
            btn_row1.pack(fill="x", pady=(0, 5))
            
            # Botones de la primera fila - corregidos para evitar errores de color
            buttons_row1 = [
                ("📖 Guía", self.mostrar_instrucciones, None, None, 80),
                ("📋 Plantilla", self.cargar_documento_base, BUTTON_COLORS['purple'], BUTTON_COLORS['darkpurple'], 90),
                ("💾 Guardar", self.guardar_proyecto, BUTTON_COLORS['green'], BUTTON_COLORS['darkgreen'], 80),
                ("📂 Cargar", self.cargar_proyecto, BUTTON_COLORS['blue'], BUTTON_COLORS['darkblue'], 80)
            ]
            
            for text, command, fg_color, hover_color, width in buttons_row1:
                btn = ctk.CTkButton(
                    btn_row1, text=text, command=command,
                    width=width, height=30, 
                    font=self.font_manager.get_font("small", "bold"),
                    fg_color=fg_color,
                    hover_color=hover_color
                )
                btn.pack(side="left", padx=(0, 5))
            
            # Estadísticas
            self.stats_label = ctk.CTkLabel(
                btn_row1, text="📊 Palabras: 0 | Secciones: 0/13 | Referencias: 0",
                font=self.font_manager.get_font("small"), text_color="gray70"
            )
            self.stats_label.pack(side="right", padx=(5, 0))
            
            # Segunda fila
            btn_row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
            btn_row2.pack(fill="x")
            
            # Botones de la segunda fila - corregidos
            buttons_row2 = [
                ("🖼️ Imágenes", self.gestionar_imagenes, BUTTON_COLORS['blue'], BUTTON_COLORS['darkblue'], 90),
                ("📤 Exportar Config", self.exportar_configuracion, BUTTON_COLORS['orange'], BUTTON_COLORS['darkorange'], 110),
                ("🔍 Validar", self.validar_proyecto, BUTTON_COLORS['orange'], BUTTON_COLORS['darkorange'], 80),
                ("🗂️ Plantillas", self.gestionar_plantillas, BUTTON_COLORS['indigo'], BUTTON_COLORS['darkindigo'], 90)
            ]
            
            for text, command, fg_color, hover_color, width in buttons_row2:
                btn = ctk.CTkButton(
                    btn_row2, text=text, command=command,
                    width=width, height=30,
                    font=self.font_manager.get_font("small", "bold"),
                    fg_color=fg_color, 
                    hover_color=hover_color
                )
                btn.pack(side="left", padx=(0, 5))
            
            # Botón generar
            self.generate_btn = ctk.CTkButton(
                btn_row2, text="📄 Generar Documento", 
                command=self.generar_documento_async,
                width=140, height=30, 
                font=self.font_manager.get_font("small", "bold"),
                fg_color=BUTTON_COLORS['green'], 
                hover_color=BUTTON_COLORS['darkgreen']
            )
            self.generate_btn.pack(side="right", padx=(5, 0))
            
            # Guardar referencias a botones para tooltips (índices actualizados)
            self.help_btn = btn_row1.winfo_children()[0]
            self.template_btn = btn_row1.winfo_children()[1]
            self.save_btn = btn_row1.winfo_children()[2]
            self.load_btn = btn_row1.winfo_children()[3]
            self.images_btn = btn_row2.winfo_children()[0]
            self.export_btn = btn_row2.winfo_children()[1]
            self.validate_btn = btn_row2.winfo_children()[2]
            self.plantillas_btn = btn_row2.winfo_children()[3]
    
    def _create_tabs(self):
        """Crea las pestañas principales"""
        # Información General
        tab1 = self.tabview.add("📋 Información General")
        self.info_general_tab = InfoGeneralTab(tab1, self)
        
        # Contenido Dinámico
        tab2 = self.tabview.add("📝 Contenido Dinámico")
        self.contenido_dinamico_tab = ContenidoDinamicoTab(tab2, self)
        
        # Citas y Referencias
        tab3 = self.tabview.add("📚 Citas y Referencias")
        self.citas_referencias_tab = CitasReferenciasTab(tab3, self)
        
        # Formato Avanzado
        tab4 = self.tabview.add("🎨 Formato")
        self.formato_avanzado_tab = FormatoAvanzadoTab(tab4, self)
        
        # Generación
        tab5 = self.tabview.add("🔧 Generar")
        self.generacion_tab = GeneracionTab(tab5, self)
    
    def _create_accessibility_menu(self, parent):
        """Crea el menú de accesibilidad"""
        # Frame de accesibilidad en el header
        accessibility_frame = ctk.CTkFrame(parent.winfo_children()[0], fg_color="transparent")
        accessibility_frame.pack(side="right", padx=20)
        
        # Indicador de zoom
        self.zoom_label = ctk.CTkLabel(
            accessibility_frame, 
            text=f"🔍 {int(self.font_manager.get_current_scale() * 100)}%",
            font=self.font_manager.get_font("small")
        )
        self.zoom_label.pack(side="left", padx=(0, 10))
        
        # Botones de zoom
        zoom_buttons = [
            ("➖", self.disminuir_zoom, 30),
            ("100%", self.restablecer_zoom, 45),
            ("➕", self.aumentar_zoom, 30)
        ]
        
        for text, command, width in zoom_buttons:
            btn = ctk.CTkButton(
                accessibility_frame, text=text, width=width, height=25,
                command=command,
                font=self.font_manager.get_font("small", "bold" if text in ["➖", "➕"] else "normal")
            )
            btn.pack(side="left", padx=2)
        
        # Función para actualizar indicador
        self.actualizar_indicador_zoom = lambda: self.zoom_label.configure(
            text=f"🔍 {int(self.font_manager.get_current_scale() * 100)}%"
        ) if hasattr(self, 'zoom_label') else None
    
    def setup_keyboard_shortcuts(self):
        """Versión actualizada con undo/redo"""
        shortcuts = {
            '<Control-s>': lambda e: self.guardar_proyecto(),
            '<Control-o>': lambda e: self.cargar_proyecto(),
            '<Control-n>': lambda e: self.nuevo_proyecto(),
            '<Control-z>': lambda e: self.undo(),  # Nuevo
            '<Control-y>': lambda e: self.redo(),  # Nuevo
            '<Control-Shift-z>': lambda e: self.redo(),  # Nuevo (alternativo)
            '<F5>': lambda e: self.validar_proyecto(),
            '<F9>': lambda e: self.generar_documento_async(),
            '<Control-q>': lambda e: self.root.quit()
        }
        
        for key, func in shortcuts.items():
            self.root.bind(key, func)

    def undo(self):
        """Deshace la última acción"""
        state_manager.undo()
        self._sincronizar_con_estado()
        messagebox.showinfo("↩️ Deshacer", "Acción deshecha")

    def redo(self):
        """Rehace la última acción deshecha"""
        state_manager.redo()
        self._sincronizar_con_estado()
        messagebox.showinfo("↪️ Rehacer", "Acción rehecha")

    def _sincronizar_con_estado(self):
        """Sincroniza la UI con el estado actual"""
        current_state = state_manager.get_state()
        
        # Actualizar referencias
        self.referencias = current_state.referencias
        self.actualizar_lista_referencias()
        
        # Actualizar secciones
        self.secciones_disponibles = current_state.secciones_disponibles
        self.secciones_activas = current_state.secciones_activas
        self.actualizar_lista_secciones()
        self.crear_pestanas_contenido()
        
        # Actualizar contenido de secciones
        for seccion_id, contenido in current_state.contenido_secciones.items():
            if seccion_id in self.content_texts:
                self.content_texts[seccion_id].delete("1.0", "end")
                self.content_texts[seccion_id].insert("1.0", contenido)
        
        # Actualizar configuración
        self.formato_config = current_state.formato_config
    
    # Métodos principales delegados
    def guardar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.guardar_proyecto(self)
    
    def cargar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.cargar_proyecto(self)
    
    def nuevo_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.nuevo_proyecto(self)
    
    def exportar_configuracion(self):
        """Delega a ProjectManager"""
        self.project_manager.exportar_configuracion(self)
    
    def generar_documento_async(self):
        """Delega a DocumentGenerator"""
        self.document_generator.generar_documento_async(self)
    
    def validar_proyecto(self):
        """Delega a ProjectValidator"""
        self.validator.validar_proyecto(self)
    
    def cargar_documento_base(self):
        """Carga el documento base usando template_manager"""
        from template_manager import aplicar_plantilla_tercer_ano
        aplicar_plantilla_tercer_ano(self)
    
    def gestionar_plantillas(self):
        """Abre el gestor de plantillas avanzado"""
        from template_manager import mostrar_gestor_plantillas
        mostrar_gestor_plantillas(self)
    
    def gestionar_imagenes(self):
        """Abre el gestor de imágenes"""
        self.image_manager.show()
    
    def mostrar_instrucciones(self):
        """Muestra las instrucciones completas"""
        self.help_dialog.show()
    
    def mostrar_preview(self):
        """Muestra la ventana de vista previa"""
        self.preview_window.show()
    
    # Métodos de accesibilidad y zoom
    def aumentar_zoom(self, event=None):
        """Aumenta el tamaño de la interfaz"""
        if self.font_manager.increase_scale():
            self.actualizar_tamaños_fuente()
            self.actualizar_indicador_zoom()
            self.anunciar_estado(f"Zoom aumentado a {int(self.font_manager.get_current_scale() * 100)}%")
        else:
            messagebox.showinfo("🔍 Zoom", "Zoom máximo alcanzado (150%)")
    
    def disminuir_zoom(self, event=None):
        """Disminuye el tamaño de la interfaz"""
        if self.font_manager.decrease_scale():
            self.actualizar_tamaños_fuente()
            self.actualizar_indicador_zoom()
            self.anunciar_estado(f"Zoom reducido a {int(self.font_manager.get_current_scale() * 100)}%")
        else:
            messagebox.showinfo("🔍 Zoom", "Zoom mínimo alcanzado (70%)")
    
    def restablecer_zoom(self, event=None):
        """Restablece el tamaño por defecto"""
        self.font_manager.reset_scale()
        self.actualizar_tamaños_fuente()
        self.actualizar_indicador_zoom()
        self.anunciar_estado("Zoom restablecido a 100%")
    
    def actualizar_tamaños_fuente(self):
        """Actualiza todos los tamaños de fuente en la interfaz"""
        # Actualizar elementos principales
        if hasattr(self, 'title_label'):
            self.title_label.configure(font=self.font_manager.get_font("title", "bold"))
        
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(font=self.font_manager.get_font("small"))
        
        # Actualizar pestañas actuales
        current_tab = self.tabview.get()
        if current_tab in self.tabview._tab_dict:
            tab_widget = self.tabview.tab(current_tab)
            self._actualizar_fuentes_recursivo(tab_widget)
        
        self.anunciar_estado(f"Zoom: {int(self.font_manager.get_current_scale() * 100)}%")
    
    def _actualizar_fuentes_recursivo(self, widget):
        """Actualiza fuentes recursivamente en widgets hijos"""
        # Implementación simplificada
        pass
    
    def anunciar_estado(self, mensaje):
        """Anuncia un mensaje de estado para accesibilidad"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=mensaje)
    
    def siguiente_pestaña(self, event=None):
        """Navega a la siguiente pestaña"""
        tabs = list(self.tabview._tab_dict.keys())
        current = self.tabview.get()
        try:
            current_index = tabs.index(current)
            next_index = (current_index + 1) % len(tabs)
            self.tabview.set(tabs[next_index])
            self.anunciar_estado(f"Navegando a: {tabs[next_index]}")
        except ValueError:
            pass
    
    def pestaña_anterior(self, event=None):
        """Navega a la pestaña anterior"""
        tabs = list(self.tabview._tab_dict.keys())
        current = self.tabview.get()
        try:
            current_index = tabs.index(current)
            prev_index = (current_index - 1) % len(tabs)
            self.tabview.set(tabs[prev_index])
            self.anunciar_estado(f"Navegando a: {tabs[prev_index]}")
        except ValueError:
            pass
    
    # Métodos de utilidad
    def buscar_imagenes_base(self):
        """Busca imágenes base en la carpeta resources/images"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            recursos_dir = os.path.join(script_dir, "..", "resources", "images")
            recursos_dir = os.path.normpath(recursos_dir)
            
            print(f"🔍 Buscando imágenes en: {recursos_dir}")
            
            if not os.path.exists(recursos_dir):
                os.makedirs(recursos_dir)
                print(f"📁 Directorio creado: {recursos_dir}")
            
            # Buscar encabezado
            encabezado_extensions = ['Encabezado.png', 'Encabezado.jpg', 'Encabezado.jpeg', 'encabezado.png']
            for filename in encabezado_extensions:
                encabezado_path = os.path.join(recursos_dir, filename)
                if os.path.exists(encabezado_path):
                    self.ruta_encabezado = encabezado_path
                    print(f"✅ Encabezado encontrado: {filename}")
                    break
            else:
                print("⚠️ Encabezado.png no encontrado en resources/images")
            
            # Buscar insignia
            insignia_extensions = ['Insignia.png', 'Insignia.jpg', 'Insignia.jpeg', 'insignia.png']
            for filename in insignia_extensions:
                insignia_path = os.path.join(recursos_dir, filename)
                if os.path.exists(insignia_path):
                    self.ruta_insignia = insignia_path
                    print(f"✅ Insignia encontrada: {filename}")
                    break
            else:
                print("⚠️ Insignia.png no encontrada en resources/images")
                
        except Exception as e:
            print(f"❌ Error buscando imágenes base: {e}")
            messagebox.showwarning("⚠️ Imágenes", 
                f"Error al buscar imágenes base:\n{str(e)}\n\n"
                f"Coloca las imágenes en: resources/images/\n"
                f"• Encabezado.png\n• Insignia.png")
    
    def get_secciones_iniciales(self):
        """Define las secciones disponibles inicialmente"""
        # [Mantener el contenido original de este método]
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False
            },
            # ... resto de secciones ...
        }
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en tiempo real"""
        total_words = 0
        total_chars = 0
        sections_completed = 0
        
        for key, text_widget in self.content_texts.items():
            if key in self.secciones_disponibles:
                content = text_widget.get("1.0", "end").strip()
                if content and len(content) > 10:
                    sections_completed += 1
                    words = len(content.split())
                    total_words += words
                    total_chars += len(content)
        
        self.stats = {
            'total_words': total_words,
            'total_chars': total_chars,
            'sections_completed': sections_completed,
            'references_added': len(self.referencias)
        }
        
        # Actualizar label
        total_sections = len([s for s in self.secciones_disponibles.values() if not s['capitulo']])
        stats_text = f"📊 Palabras: {total_words} | Secciones: {sections_completed}/{total_sections} | Referencias: {len(self.referencias)}"
        self.stats_label.configure(text=stats_text)
        
        # Programar próxima actualización
        self.root.after(2000, self.actualizar_estadisticas)
    
    def mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida con atajos de teclado"""
        self.root.after(1000, lambda: messagebox.showinfo(
            "🎓 ¡Generador Profesional!",
            "Generador de Proyectos Académicos - Versión Profesional\n\n"
            "🆕 CARACTERÍSTICAS AVANZADAS:\n"
            "• Estructura modular mejorada\n"
            "• Auto-guardado cada 5 minutos\n"
            "• Estadísticas en tiempo real\n"
            "• Sistema de guardado/carga completo\n"
            "• Gestión avanzada de imágenes\n"
            "• Exportación de configuraciones\n\n"
            "⌨️ ATAJOS DE TECLADO:\n"
            "• Ctrl+S: Guardar proyecto\n"
            "• Ctrl+O: Cargar proyecto\n"
            "• Ctrl+N: Nuevo proyecto\n"
            "• F5: Validar proyecto\n"
            "• F9: Generar documento\n"
            "• Ctrl+Q: Salir\n\n"
            "🚀 ¡Crea proyectos profesionales únicos!"
        ))
    
    def agregar_tooltips(self):
        """Agrega tooltips a los botones principales"""
        # Implementación pendiente
        pass
    # Agregar estos métodos a la clase ProyectoAcademicoGenerator en ui/main_window.py

    # ========== MÉTODOS DE INTERFAZ DE USUARIO ==========

    def toggle_sidebar(self):
        """Alterna la visibilidad del panel lateral"""
        if hasattr(self, 'sidebar_collapsed') and hasattr(self, 'control_frame'):
            if self.sidebar_collapsed:
                # Expandir
                self.control_frame.pack(side="left", fill="y", padx=(0, 10))
                self.control_frame.configure(width=320)
                # Cambiar icono del botón
                for widget in self.control_frame.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for btn in widget.winfo_children():
                            if isinstance(btn, ctk.CTkButton) and btn.cget("text") in ["▶", "◀"]:
                                btn.configure(text="◀")
                        break
            else:
                # Colapsar
                self.control_frame.pack_forget()
                # O alternativamente, reducir el ancho
                # self.control_frame.configure(width=50)
            
            self.sidebar_collapsed = not self.sidebar_collapsed

    def filtrar_secciones(self, event=None):
        """Filtra las secciones según el término de búsqueda"""
        if hasattr(self, 'search_entry') and hasattr(self, 'secciones_listbox'):
            termino = self.search_entry.get().lower()
            
            # Limpiar lista actual
            for widget in self.secciones_listbox.winfo_children():
                widget.destroy()
            
            # Mostrar solo secciones que coincidan
            for seccion_id in self.secciones_activas:
                if seccion_id in self.secciones_disponibles:
                    seccion = self.secciones_disponibles[seccion_id]
                    titulo = seccion['titulo'].lower()
                    
                    if termino in titulo or termino in seccion_id:
                        self._crear_item_seccion(seccion_id, seccion)

    def _crear_item_seccion(self, seccion_id, seccion):
        """Crea un item visual para la lista de secciones"""
        if hasattr(self, 'secciones_listbox'):
            item_frame = ctk.CTkFrame(self.secciones_listbox, fg_color="gray20", corner_radius=5)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Texto de la sección
            label_text = seccion['titulo']
            if seccion.get('capitulo', False):
                label_text = f"📁 {label_text}"
            elif seccion.get('requerida', False):
                label_text = f"⚠️ {label_text}"
            
            label = ctk.CTkLabel(
                item_frame, text=label_text,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
            
            # Guardar referencia para selección
            item_frame.seccion_id = seccion_id
            item_frame.bind("<Button-1>", lambda e: self._seleccionar_seccion(seccion_id))
    def _seleccionar_seccion(self, seccion_id):
        """Maneja la selección de una sección en la lista"""
        # Buscar la pestaña correspondiente
        if seccion_id in self.secciones_disponibles:
            seccion = self.secciones_disponibles[seccion_id]
            if not seccion.get('capitulo', False) and hasattr(self, 'content_tabview'):
                # Buscar y seleccionar la pestaña
                for tab_name in self.content_tabview._tab_dict:
                    if tab_name == seccion['titulo']:
                        self.content_tabview.set(tab_name)
                        break
    def _toggle_seccion(self, seccion_id, activa):
        """Activa o desactiva una sección"""
        if activa and seccion_id not in self.secciones_activas:
            self.secciones_activas.append(seccion_id)
        elif not activa and seccion_id in self.secciones_activas:
            # Verificar si es requerida
            if self.secciones_disponibles[seccion_id].get('requerida', False):
                messagebox.showwarning("⚠️ Sección Requerida", 
                    "Esta sección es requerida y no puede ser desactivada")
                # Volver a marcar el checkbox
                return
            self.secciones_activas.remove(seccion_id)
        
        # Actualizar pestañas de contenido
        self.crear_pestanas_contenido()

    def actualizar_lista_secciones(self):
        """Actualiza la lista visual de secciones"""
        if hasattr(self, 'secciones_listbox'):
            # Limpiar lista actual
            for widget in self.secciones_listbox.winfo_children():
                widget.destroy()
            
            # Recrear items
            for seccion_id in self.secciones_activas:
                if seccion_id in self.secciones_disponibles:
                    self._crear_item_seccion(seccion_id, self.secciones_disponibles[seccion_id])

    def crear_pestanas_contenido(self):
        """Crea las pestañas de contenido dinámicamente"""
        if hasattr(self, 'content_tabview'):
            # Guardar contenido actual antes de recrear
            contenido_temporal = {}
            for seccion_id, text_widget in self.content_texts.items():
                contenido_temporal[seccion_id] = text_widget.get("1.0", "end-1c")
            
            # Limpiar pestañas existentes
            for tab in list(self.content_tabview._tab_dict.keys()):
                self.content_tabview.delete(tab)
            
            # Limpiar diccionario de widgets
            self.content_texts.clear()
            
            # Crear nuevas pestañas según secciones activas
            for seccion_id in self.secciones_activas:
                if seccion_id in self.secciones_disponibles:
                    seccion = self.secciones_disponibles[seccion_id]
                    
                    # No crear pestaña para capítulos (solo son títulos)
                    if not seccion.get('capitulo', False):
                        tab = self.content_tabview.add(seccion['titulo'])
                        self._crear_contenido_seccion(tab, seccion_id, seccion)
                        
                        # Restaurar contenido si existía
                        if seccion_id in contenido_temporal and seccion_id in self.content_texts:
                            self.content_texts[seccion_id].insert("1.0", contenido_temporal[seccion_id])
            
            # Actualizar breadcrumb si existe
            if hasattr(self, 'breadcrumb_label'):
                current_tab = self.content_tabview.get() if self.content_tabview._tab_dict else ""
                self.breadcrumb_label.configure(text=f"📍 Navegación: {current_tab}")

    def _crear_contenido_seccion(self, parent, seccion_id, seccion):
        """Crea el contenido para una sección"""
        # Frame contenedor
        section_frame = ctk.CTkFrame(parent, corner_radius=10)
        section_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header con instrucción
        header_frame = ctk.CTkFrame(section_frame, fg_color="gray25", height=60)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        instruc_label = ctk.CTkLabel(
            header_frame, text=f"💡 {seccion['instruccion']}",
            font=ctk.CTkFont(size=12),
            wraplength=700, justify="left"
        )
        instruc_label.pack(padx=15, pady=10)
        
        # Área de texto
        text_widget = ctk.CTkTextbox(
            section_frame,
            font=ctk.CTkFont(size=12, family="Georgia"),
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Guardar referencia al widget de texto
        self.content_texts[seccion_id] = text_widget
        
        # Barra de herramientas
        self._crear_toolbar_seccion(section_frame, seccion_id, text_widget)
    
    def _crear_toolbar_seccion(self, parent, seccion_id, text_widget):
        """Crea la barra de herramientas para una sección"""
        toolbar = ctk.CTkFrame(parent, height=40, fg_color="gray20")
        toolbar.pack(fill="x", padx=10, pady=(0, 10))
        
        # Botón insertar cita (solo para secciones específicas)
        if seccion_id in ['marco_teorico', 'introduccion', 'desarrollo', 'discusion']:
            cita_btn = ctk.CTkButton(
                toolbar, text="📚 Insertar Cita",
                command=lambda: self.insertar_cita_dialog(text_widget, seccion_id),
                width=120, height=30
            )
            cita_btn.pack(side="left", padx=5, pady=5)
        
        # Contador de palabras
        word_count = ctk.CTkLabel(
            toolbar, text="Palabras: 0",
            font=ctk.CTkFont(size=11)
        )
        word_count.pack(side="right", padx=10)
        
        # Actualizar contador al escribir
        def update_count(event=None):
            content = text_widget.get("1.0", "end-1c")
            words = len(content.split()) if content.strip() else 0
            word_count.configure(text=f"Palabras: {words}")
        
        text_widget.bind("<KeyRelease>", update_count)
        update_count()  # Actualizar inicialmente

    def insertar_cita_dialog(self, text_widget, seccion_tipo):
        """Abre el diálogo para insertar citas"""
        from .dialogs import CitationDialog
        
        dialog = CitationDialog(self.root, seccion_tipo)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Insertar la cita en la posición del cursor
            text_widget.insert("insert", dialog.result + " ")

    # ========== MÉTODOS DE GESTIÓN DE SECCIONES ==========

    def quitar_seccion(self):
        """Quita la sección seleccionada"""
        # Por ahora, quitar la última sección no requerida
        for i in range(len(self.secciones_activas) - 1, -1, -1):
            seccion_id = self.secciones_activas[i]
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                if not seccion.get('requerida', False) and not seccion.get('capitulo', False):
                    self.secciones_activas.pop(i)
                    self.actualizar_lista_secciones()
                    self.crear_pestanas_contenido()
                    messagebox.showinfo("✅ Eliminada", f"Sección '{seccion['titulo']}' eliminada")
                    return
        
        messagebox.showwarning("⚠️ Sin secciones", "No hay secciones que se puedan eliminar")

    def editar_seccion(self):
        """Edita una sección existente"""
        # Obtener la sección actual
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección por el título
            seccion_id = None
            for sid, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    seccion_id = sid
                    break
            
            if seccion_id:
                from .dialogs import SeccionDialog
                
                dialog = SeccionDialog(
                    self.root, 
                    self.secciones_disponibles,
                    editar=True,
                    seccion_actual=(seccion_id, self.secciones_disponibles[seccion_id])
                )
                
                self.root.wait_window(dialog.dialog)
                
                if dialog.result:
                    _, seccion_data = dialog.result
                    self.secciones_disponibles[seccion_id].update(seccion_data)
                    self.actualizar_lista_secciones()
                    self.crear_pestanas_contenido()
                    messagebox.showinfo("✅ Actualizada", "Sección actualizada correctamente")

    def subir_seccion(self):
        """Sube la sección actual en el orden"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección
            for seccion_id, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    if seccion_id in self.secciones_activas:
                        index = self.secciones_activas.index(seccion_id)
                        if index > 0:
                            # Intercambiar con la anterior
                            self.secciones_activas[index], self.secciones_activas[index-1] = \
                                self.secciones_activas[index-1], self.secciones_activas[index]
                            self.actualizar_lista_secciones()
                            self.crear_pestanas_contenido()
                            # Mantener la pestaña actual seleccionada
                            self.content_tabview.set(current_tab)
                    break

    def bajar_seccion(self):
        """Baja la sección actual en el orden"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección
            for seccion_id, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    if seccion_id in self.secciones_activas:
                        index = self.secciones_activas.index(seccion_id)
                        if index < len(self.secciones_activas) - 1:
                            # Intercambiar con la siguiente
                            self.secciones_activas[index], self.secciones_activas[index+1] = \
                                self.secciones_activas[index+1], self.secciones_activas[index]
                            self.actualizar_lista_secciones()
                            self.crear_pestanas_contenido()
                            # Mantener la pestaña actual seleccionada
                            self.content_tabview.set(current_tab)
                    break

    # ========== MÉTODOS DE REFERENCIAS ==========

    def agregar_referencia(self):
        """Agrega una referencia a la lista"""
        # Recopilar datos del formulario
        if all([
            hasattr(self, 'ref_tipo'),
            hasattr(self, 'ref_autor'),
            hasattr(self, 'ref_año'),
            hasattr(self, 'ref_titulo'),
            hasattr(self, 'ref_fuente')
        ]):
            ref_data = {
                'tipo': self.ref_tipo.get(),
                'autor': self.ref_autor.get().strip(),
                'año': self.ref_año.get().strip(),
                'titulo': self.ref_titulo.get().strip(),
                'fuente': self.ref_fuente.get().strip()
            }
            
            # Validar campos requeridos
            if not all([ref_data['autor'], ref_data['año'], ref_data['titulo'], ref_data['fuente']]):
                messagebox.showerror("❌ Error", "Todos los campos son obligatorios")
                return
            
            # Agregar a la lista
            self.referencias.append(ref_data)
            
            # Actualizar lista visual
            self.actualizar_lista_referencias()
            
            # Limpiar campos
            self.ref_autor.delete(0, "end")
            self.ref_año.delete(0, "end")
            self.ref_titulo.delete(0, "end")
            self.ref_fuente.delete(0, "end")
            
            # Actualizar contador
            if hasattr(self, 'ref_stats_label'):
                self.ref_stats_label.configure(text=f"Total: {len(self.referencias)} referencias")
            
            messagebox.showinfo("✅ Agregada", "Referencia agregada correctamente")

    def actualizar_lista_referencias(self):
        """Actualiza la lista visual de referencias"""
        if hasattr(self, 'ref_scroll_frame'):
            # Limpiar lista actual
            for widget in self.ref_scroll_frame.winfo_children():
                widget.destroy()
            
            # Mostrar referencias
            for i, ref in enumerate(self.referencias):
                ref_item_frame = ctk.CTkFrame(self.ref_scroll_frame, fg_color="gray20", corner_radius=8)
                ref_item_frame.pack(fill="x", padx=5, pady=5)
                
                # Formatear referencia APA
                if ref['tipo'] == 'Libro':
                    apa_ref = f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}."
                elif ref['tipo'] == 'Web':
                    apa_ref = f"{ref['autor']} ({ref['año']}). {ref['titulo']}. Recuperado de {ref['fuente']}"
                else:
                    apa_ref = f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}."
                
                ref_label = ctk.CTkLabel(
                    ref_item_frame, text=f"📖 {apa_ref}", 
                    font=ctk.CTkFont(size=11),
                    wraplength=800, justify="left"
                )
                ref_label.pack(padx=15, pady=10, anchor="w")
                
                # Botón eliminar individual
                delete_btn = ctk.CTkButton(
                    ref_item_frame, text="🗑️", width=30, height=30,
                    command=lambda idx=i: self.eliminar_referencia_individual(idx),
                    fg_color="red", hover_color="darkred"
                )
                delete_btn.pack(side="right", padx=10)

    def eliminar_referencia_individual(self, index):
        """Elimina una referencia específica"""
        if 0 <= index < len(self.referencias):
            ref = self.referencias[index]
            respuesta = messagebox.askyesno("🗑️ Confirmar", 
                f"¿Eliminar esta referencia?\n\n{ref['autor']} ({ref['año']})")
            
            if respuesta:
                self.referencias.pop(index)
                self.actualizar_lista_referencias()
                
                # Actualizar contador
                if hasattr(self, 'ref_stats_label'):
                    self.ref_stats_label.configure(text=f"Total: {len(self.referencias)} referencias")

    def actualizar_campos_referencia(self, tipo_seleccionado):
        """Actualiza los campos del formulario según el tipo de referencia"""
        if hasattr(self, 'fuente_label'):
            # Cambiar etiqueta según tipo
            if tipo_seleccionado == "Libro":
                self.fuente_label.configure(text="Editorial:")
                self.ref_fuente.configure(placeholder_text="Nombre de la editorial")
            elif tipo_seleccionado == "Artículo":
                self.fuente_label.configure(text="Revista:")
                self.ref_fuente.configure(placeholder_text="Nombre de la revista, volumen(número), páginas")
            elif tipo_seleccionado == "Web":
                self.fuente_label.configure(text="URL:")
                self.ref_fuente.configure(placeholder_text="https://www.ejemplo.com")
            elif tipo_seleccionado == "Tesis":
                self.fuente_label.configure(text="Universidad:")
                self.ref_fuente.configure(placeholder_text="Universidad, tipo de tesis")
            elif tipo_seleccionado == "Conferencia":
                self.fuente_label.configure(text="Evento:")
                self.ref_fuente.configure(placeholder_text="Nombre del evento, lugar")
            elif tipo_seleccionado == "Informe":
                self.fuente_label.configure(text="Organización:")
                self.ref_fuente.configure(placeholder_text="Organización que publica")

    # ========== MÉTODOS DE VISTA PREVIA ==========

    def actualizar_preview(self):
        """Actualiza el contenido de la vista previa"""
        if hasattr(self, 'preview_text') and hasattr(self, 'preview_mode'):
            modo = self.preview_mode.get() if hasattr(self.preview_mode, 'get') else "📝 Texto"
            
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            
            if modo == "📝 Texto":
                # Vista previa del texto compilado
                preview_content = self.generar_preview_texto()
            elif modo == "🎨 Formato":
                # Vista previa con formato aplicado
                preview_content = self.generar_preview_formato()
            elif modo == "📊 Estructura":
                # Vista previa de la estructura
                preview_content = self.generar_preview_estructura()
            else:
                preview_content = "Modo de vista previa no reconocido"
            
            self.preview_text.insert("1.0", preview_content)
            self.preview_text.configure(state="disabled")

    def generar_preview_texto(self):
        """Genera vista previa del texto compilado"""
        preview = []
        
        # Título
        if 'titulo' in self.proyecto_data:
            titulo = self.proyecto_data['titulo'].get()
            if titulo:
                preview.append(f"{titulo.upper()}\n")
                preview.append("="*len(titulo) + "\n\n")
        
        # Compilar secciones
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles and seccion_id in self.content_texts:
                seccion = self.secciones_disponibles[seccion_id]
                contenido = self.content_texts[seccion_id].get("1.0", "end").strip()
                
                if contenido:
                    # Agregar título de sección
                    titulo_seccion = seccion['titulo'].replace('📄', '').replace('🔍', '').replace('📖', '').strip()
                    preview.append(f"\n{titulo_seccion.upper()}\n")
                    preview.append("-"*len(titulo_seccion) + "\n\n")
                    
                    # Agregar contenido
                    preview.append(contenido + "\n")
        
        # Referencias
        if self.referencias:
            preview.append("\n\nREFERENCIAS\n")
            preview.append("-"*11 + "\n\n")
            
            for ref in sorted(self.referencias, key=lambda x: x['autor']):
                if ref['tipo'] == 'Libro':
                    preview.append(f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}.\n\n")
                else:
                    preview.append(f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}.\n\n")
        
        return ''.join(preview) if preview else "No hay contenido para mostrar"

    def generar_preview_estructura(self):
        """Genera vista previa de la estructura del documento"""
        preview = []
        preview.append("📊 ESTRUCTURA DEL DOCUMENTO\n")
        preview.append("="*30 + "\n\n")
        
        # Información general
        preview.append("📋 INFORMACIÓN GENERAL:\n")
        campos_info = ['institucion', 'titulo', 'estudiantes', 'tutores']
        for campo in campos_info:
            if campo in self.proyecto_data:
                valor = self.proyecto_data[campo].get()
                if valor:
                    preview.append(f"   • {campo.title()}: {valor}\n")
        
        preview.append("\n📑 SECCIONES ACTIVAS:\n")
        
        # Estructura de secciones
        num_capitulo = 0
        for i, seccion_id in enumerate(self.secciones_activas, 1):
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                if seccion.get('capitulo', False):
                    num_capitulo += 1
                    preview.append(f"\n{seccion['titulo']}\n")
                else:
                    # Contar palabras si existe contenido
                    palabras = 0
                    if seccion_id in self.content_texts:
                        contenido = self.content_texts[seccion_id].get("1.0", "end").strip()
                        if contenido:
                            palabras = len(contenido.split())
                    
                    estado = "✅" if palabras > 50 else "⚠️" if palabras > 0 else "❌"
                    preview.append(f"   {estado} {seccion['titulo']} ({palabras} palabras)\n")
        
        # Estadísticas
        preview.append(f"\n📈 ESTADÍSTICAS:\n")
        preview.append(f"   • Total de secciones: {len([s for s in self.secciones_activas if not self.secciones_disponibles.get(s, {}).get('capitulo', False)])}\n")
        preview.append(f"   • Referencias agregadas: {len(self.referencias)}\n")
        preview.append(f"   • Palabras totales: {self.stats.get('total_words', 0)}\n")
        
        return ''.join(preview)

    # ========== MÉTODOS DE VALIDACIÓN ==========

    def mostrar_bienvenida_validacion(self):
        """Muestra mensaje de bienvenida en el panel de validación"""
        if hasattr(self, 'validation_text'):
            mensaje = """🎯 PANEL DE VALIDACIÓN Y GENERACIÓN

    Este panel te ayudará a:
    • Validar que tu proyecto esté completo
    • Ver estadísticas y análisis
    • Revisar logs del sistema
    • Obtener sugerencias de mejora

    Presiona '🔍 Validar' en el header principal para comenzar la validación.

    OPCIONES DE GENERACIÓN:
    ✓ Incluir Portada - Página de presentación profesional
    ✓ Incluir Índice - Tabla de contenidos automática
    ✓ Incluir Agradecimientos - Sección de agradecimientos
    ✓ Numeración de páginas - Números de página automáticos

    Cuando todo esté listo, presiona '📄 Generar Documento' para crear tu archivo Word.
    """
            self.validation_text.insert("1.0", mensaje)

    def cambiar_tab_validacion(self, valor):
        """Cambia el contenido según la pestaña de validación seleccionada"""
        if hasattr(self, 'validation_text'):
            self.validation_text.delete("1.0", "end")
            
            if valor == "🔍 Validación":
                self.validar_proyecto()
            elif valor == "📋 Logs":
                self.mostrar_logs()
            elif valor == "📊 Estadísticas":
                self.mostrar_estadisticas()
            elif valor == "💡 Sugerencias":
                self.mostrar_sugerencias()

    def mostrar_estadisticas(self):
        """Muestra estadísticas detalladas del proyecto"""
        stats = []
        stats.append("📊 ESTADÍSTICAS DETALLADAS DEL PROYECTO\n")
        stats.append("="*50 + "\n\n")
        
        # Estadísticas generales
        stats.append("📈 MÉTRICAS GENERALES:\n")
        stats.append(f"   • Palabras totales: {self.stats.get('total_words', 0):,}\n")
        stats.append(f"   • Caracteres totales: {self.stats.get('total_chars', 0):,}\n")
        stats.append(f"   • Promedio palabras/sección: {self.stats.get('total_words', 0) // max(1, self.stats.get('sections_completed', 1))}\n\n")
        
        # Por sección
        stats.append("📑 ANÁLISIS POR SECCIÓN:\n")
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles and seccion_id in self.content_texts:
                seccion = self.secciones_disponibles[seccion_id]
                if not seccion.get('capitulo', False):
                    contenido = self.content_texts[seccion_id].get("1.0", "end").strip()
                    palabras = len(contenido.split()) if contenido else 0
                    caracteres = len(contenido) if contenido else 0
                    
                    stats.append(f"\n   {seccion['titulo']}:\n")
                    stats.append(f"      - Palabras: {palabras:,}\n")
                    stats.append(f"      - Caracteres: {caracteres:,}\n")
                    stats.append(f"      - Estado: {'✅ Completo' if palabras > 50 else '⚠️ En progreso' if palabras > 0 else '❌ Vacío'}\n")
        
        # Referencias
        stats.append(f"\n📚 REFERENCIAS:\n")
        stats.append(f"   • Total: {len(self.referencias)}\n")
        
        if self.referencias:
            tipos_ref = {}
            for ref in self.referencias:
                tipo = ref.get('tipo', 'Otro')
                tipos_ref[tipo] = tipos_ref.get(tipo, 0) + 1
            
            for tipo, cantidad in tipos_ref.items():
                stats.append(f"   • {tipo}: {cantidad}\n")
        
        self.validation_text.insert("1.0", ''.join(stats))

    # ========== MÉTODOS DE IMÁGENES ==========

    def cargar_imagen_personalizada(self, tipo, parent_window=None):
        """Carga una imagen personalizada (encabezado o insignia)"""
        from tkinter import filedialog
        from PIL import Image
        
        filename = filedialog.askopenfilename(
            title=f"Seleccionar {tipo}",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")],
            parent=parent_window
        )
        
        if filename:
            try:
                # Verificar que es una imagen válida
                img = Image.open(filename)
                
                # Redimensionar si es necesario
                if tipo == "encabezado":
                    # Recomendado: 600x100 px
                    if img.width > 800 or img.height > 150:
                        img.thumbnail((800, 150), Image.Resampling.LANCZOS)
                    self.encabezado_personalizado = filename
                    
                    # Actualizar estado en el diálogo
                    if hasattr(self, 'enc_custom_label'):
                        self.enc_custom_label.configure(text="Encabezado: ✅ Cargado")
                        
                elif tipo == "insignia":
                    # Recomendado: 100x100 px
                    if img.width > 150 or img.height > 150:
                        img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    self.insignia_personalizada = filename
                    
                    # Actualizar estado en el diálogo
                    if hasattr(self, 'ins_custom_label'):
                        self.ins_custom_label.configure(text="Insignia: ✅ Cargado")
                
                messagebox.showinfo("✅ Cargado", 
                    f"{tipo.title()} cargado correctamente:\n{os.path.basename(filename)}")
                    
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al cargar imagen:\n{str(e)}")

    def restablecer_imagenes(self, parent_window=None):
        """Restablece las imágenes a las predeterminadas"""
        respuesta = messagebox.askyesno("🔄 Restablecer", 
            "¿Restablecer a las imágenes base?", parent=parent_window)
        
        if respuesta:
            self.encabezado_personalizado = None
            self.insignia_personalizada = None
            
            # Actualizar estados
            if hasattr(self, 'enc_custom_label'):
                self.enc_custom_label.configure(text="Encabezado: ⏸️ No cargado")
            if hasattr(self, 'ins_custom_label'):
                self.ins_custom_label.configure(text="Insignia: ⏸️ No cargado")
            
            messagebox.showinfo("✅ Restablecido", "Imágenes restablecidas a las predeterminadas")

    # ========== MÉTODOS AUXILIARES ==========

    def get_secciones_iniciales(self):
        """Define las secciones disponibles inicialmente"""
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False
            },
            "introduccion": {
                "titulo": "🔍 Introducción", 
                "instruccion": "Presenta el tema, contexto e importancia",
                "requerida": True,
                "capitulo": False
            },
            "capitulo1": {
                "titulo": "📖 CAPÍTULO I", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "planteamiento": {
                "titulo": "❓ Planteamiento del Problema", 
                "instruccion": "Define el problema a investigar",
                "requerida": True,
                "capitulo": False
            },
            "preguntas": {
                "titulo": "❔ Preguntas de Investigación", 
                "instruccion": "Pregunta general y específicas",
                "requerida": True,
                "capitulo": False
            },
            "delimitaciones": {
                "titulo": "📏 Delimitaciones", 
                "instruccion": "Límites del estudio (temporal, espacial, conceptual)",
                "requerida": False,
                "capitulo": False
            },
            "justificacion": {
                "titulo": "💡 Justificación", 
                "instruccion": "Explica por qué es importante investigar",
                "requerida": True,
                "capitulo": False
            },
            "objetivos": {
                "titulo": "🎯 Objetivos", 
                "instruccion": "General y específicos (verbos en infinitivo)",
                "requerida": True,
                "capitulo": False
            },
            "capitulo2": {
                "titulo": "📚 CAPÍTULO II - ESTADO DEL ARTE", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "marco_teorico": {
                "titulo": "📖 Marco Teórico", 
                "instruccion": "Base teórica y antecedentes (USA CITAS)",
                "requerida": True,
                "capitulo": False
            },
            "capitulo3": {
                "titulo": "🔬 CAPÍTULO III", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "metodologia": {
                "titulo": "⚙️ Marco Metodológico", 
                "instruccion": "Tipo de estudio y técnicas de recolección",
                "requerida": True,
                "capitulo": False
            },
            "capitulo4": {
                "titulo": "🛠️ CAPÍTULO IV - DESARROLLO", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "desarrollo": {
                "titulo": "⚙️ Desarrollo", 
                "instruccion": "Proceso de investigación paso a paso",
                "requerida": False,
                "capitulo": False
            },
            "capitulo5": {
                "titulo": "📊 CAPÍTULO V - ANÁLISIS DE DATOS", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "resultados": {
                "titulo": "📊 Resultados", 
                "instruccion": "Datos obtenidos (gráficos, tablas)",
                "requerida": False,
                "capitulo": False
            },
            "analisis_datos": {
                "titulo": "📈 Análisis de Datos", 
                "instruccion": "Interpretación de resultados",
                "requerida": False,
                "capitulo": False
            },
            "capitulo6": {
                "titulo": "💬 CAPÍTULO VI", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "discusion": {
                "titulo": "💬 Discusión", 
                "instruccion": "Confronta resultados con teoría",
                "requerida": False,
                "capitulo": False
            },
            "conclusiones": {
                "titulo": "✅ Conclusiones", 
                "instruccion": "Hallazgos principales y respuestas a objetivos",
                "requerida": True,
                "capitulo": False
            }
        }

    def ir_a_seccion_actual(self):
        """Navega a la sección actual en el contenido"""
        if hasattr(self, 'content_tabview'):
            current_tab = self.content_tabview.get()
            if current_tab:
                self.tabview.set("📝 Contenido Dinámico")
                self.anunciar_estado(f"Navegando a sección: {current_tab}")

    def buscar_en_contenido(self):
        """Abre diálogo de búsqueda en el contenido"""
        # Por implementar: diálogo de búsqueda
        messagebox.showinfo("🔍 Buscar", "Función de búsqueda en desarrollo")
    # Agregar estos métodos a la clase ProyectoAcademicoGenerator en ui/main_window.py
    # ANTES del método run()

    # ========== MÉTODOS DE IMPORTACIÓN/EXPORTACIÓN ==========

    def importar_bibtex(self):
        """Importa referencias desde archivo BibTeX"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo BibTeX",
            filetypes=[("Archivos BibTeX", "*.bib"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    contenido_bibtex = f.read()
                
                # Parsear entradas BibTeX básicas
                import re
                entradas = re.findall(r'@\w+\{[^}]+\}', contenido_bibtex, re.DOTALL)
                
                referencias_importadas = 0
                for entrada in entradas:
                    try:
                        # Extraer tipo
                        tipo_match = re.match(r'@(\w+)\{', entrada)
                        tipo = tipo_match.group(1) if tipo_match else 'Libro'
                        
                        # Extraer campos
                        ref_data = {'tipo': tipo}
                        
                        # Buscar autor
                        autor_match = re.search(r'author\s*=\s*["{]([^"}]+)["}]', entrada, re.IGNORECASE)
                        if autor_match:
                            ref_data['autor'] = autor_match.group(1).strip()
                        
                        # Buscar año
                        year_match = re.search(r'year\s*=\s*["{]?(\d{4})["}]?', entrada, re.IGNORECASE)
                        if year_match:
                            ref_data['año'] = year_match.group(1)
                        
                        # Buscar título
                        title_match = re.search(r'title\s*=\s*["{]([^"}]+)["}]', entrada, re.IGNORECASE)
                        if title_match:
                            ref_data['titulo'] = title_match.group(1).strip()
                        
                        # Buscar fuente (journal, publisher, etc.)
                        fuente_match = re.search(r'(?:journal|publisher|booktitle)\s*=\s*["{]([^"}]+)["}]', entrada, re.IGNORECASE)
                        if fuente_match:
                            ref_data['fuente'] = fuente_match.group(1).strip()
                        else:
                            ref_data['fuente'] = ''
                        
                        # Agregar si tiene los campos mínimos
                        if all(key in ref_data for key in ['autor', 'año', 'titulo']):
                            self.referencias.append(ref_data)
                            referencias_importadas += 1
                            
                    except Exception as e:
                        print(f"Error procesando entrada: {e}")
                        continue
                
                # Actualizar lista visual
                self.actualizar_lista_referencias()
                
                # Actualizar contador
                if hasattr(self, 'ref_stats_label'):
                    self.ref_stats_label.configure(text=f"Total: {len(self.referencias)} referencias")
                
                messagebox.showinfo("✅ Importación Exitosa", 
                    f"Se importaron {referencias_importadas} referencias desde el archivo BibTeX")
                    
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al importar archivo BibTeX:\n{str(e)}")

    def eliminar_referencias_seleccionadas(self):
        """Elimina las referencias seleccionadas"""
        # Por ahora, elimina la última referencia
        if self.referencias:
            respuesta = messagebox.askyesno("🗑️ Confirmar", 
                "¿Eliminar la última referencia agregada?")
            
            if respuesta:
                self.referencias.pop()
                self.actualizar_lista_referencias()
                
                # Actualizar contador
                if hasattr(self, 'ref_stats_label'):
                    self.ref_stats_label.configure(text=f"Total: {len(self.referencias)} referencias")
                
                messagebox.showinfo("✅ Eliminada", "Referencia eliminada correctamente")
        else:
            messagebox.showwarning("⚠️ Sin referencias", "No hay referencias para eliminar")

    def exportar_referencias_apa(self):
        """Exporta las referencias en formato APA"""
        if not self.referencias:
            messagebox.showwarning("⚠️ Sin referencias", "No hay referencias para exportar")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Exportar Referencias APA"
        )
        
        if filename:
            try:
                # Ordenar referencias por autor
                referencias_ordenadas = sorted(self.referencias, 
                                            key=lambda x: x['autor'].split(',')[0].strip())
                
                # Generar formato APA
                referencias_apa = []
                for ref in referencias_ordenadas:
                    apa_ref = self._formatear_referencia_apa_export(ref)
                    referencias_apa.append(apa_ref)
                
                # Escribir archivo
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("REFERENCIAS\n")
                    f.write("="*50 + "\n\n")
                    f.write("\n\n".join(referencias_apa))
                
                messagebox.showinfo("✅ Exportado", 
                    f"Referencias exportadas exitosamente:\n{filename}")
                    
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al exportar referencias:\n{str(e)}")

    def _formatear_referencia_apa_export(self, ref):
        """Formatea una referencia individual para exportación"""
        tipo = ref.get('tipo', 'Libro')
        autor = ref.get('autor', '')
        año = ref.get('año', '')
        titulo = ref.get('titulo', '')
        fuente = ref.get('fuente', '')
        
        if tipo == 'Libro':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Artículo':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Web':
            return f"{autor} ({año}). {titulo}. Recuperado de {fuente}"
        elif tipo == 'Tesis':
            return f"{autor} ({año}). {titulo} [Tesis]. {fuente}."
        elif tipo == 'Conferencia':
            return f"{autor} ({año}). {titulo}. Presentado en {fuente}."
        elif tipo == 'Informe':
            return f"{autor} ({año}). {titulo}. {fuente}."
        else:
            return f"{autor} ({año}). {titulo}. {fuente}."

    def filtrar_referencias(self, event=None):
        """Filtra las referencias según el término de búsqueda"""
        termino = self.ref_search.get().lower() if hasattr(self, 'ref_search') else ""
        
        # Limpiar lista actual
        for widget in self.ref_scroll_frame.winfo_children():
            widget.destroy()
        
        # Mostrar solo referencias que coincidan
        referencias_filtradas = []
        for ref in self.referencias:
            if (termino in ref['autor'].lower() or 
                termino in ref['titulo'].lower() or 
                termino in ref.get('fuente', '').lower() or
                termino in ref.get('año', '')):
                referencias_filtradas.append(ref)
        
        # Recrear lista visual con referencias filtradas
        for i, ref in enumerate(referencias_filtradas):
            ref_item_frame = ctk.CTkFrame(self.ref_scroll_frame, fg_color="gray20", corner_radius=8)
            ref_item_frame.pack(fill="x", padx=5, pady=5)
            
            apa_ref = self._formatear_referencia_apa_export(ref)
            ref_label = ctk.CTkLabel(
                ref_item_frame, text=f"📖 {apa_ref}", 
                font=ctk.CTkFont(size=11),
                wraplength=800, justify="left"
            )
            ref_label.pack(padx=15, pady=10, anchor="w")
            
            # Botón eliminar individual
            delete_btn = ctk.CTkButton(
                ref_item_frame, text="🗑️", width=30, height=30,
                command=lambda idx=self.referencias.index(ref): self.eliminar_referencia_individual(idx),
                fg_color="red", hover_color="darkred"
            )
            delete_btn.pack(side="right", padx=10)
        
        # Mostrar mensaje si no hay coincidencias
        if not referencias_filtradas and termino:
            no_results_label = ctk.CTkLabel(
                self.ref_scroll_frame, 
                text="No se encontraron referencias que coincidan con la búsqueda",
                font=ctk.CTkFont(size=12),
                text_color="gray60"
            )
            no_results_label.pack(pady=20)

    def actualizar_opacidad_preview(self, value):
        """Actualiza el valor de opacidad de la marca de agua"""
        self.watermark_opacity = float(value)
        if hasattr(self, 'opacity_label'):
            self.opacity_label.configure(text=f"{int(self.watermark_opacity * 100)}%")

    def limpiar_validacion(self):
        """Limpia el área de validación"""
        if hasattr(self, 'validation_text'):
            self.validation_text.delete("1.0", "end")
            self.anunciar_estado("Panel de validación limpiado")

    def mostrar_logs(self):
        """Muestra los logs del sistema"""
        logs = []
        logs.append("📋 LOGS DEL SISTEMA\n")
        logs.append("="*60 + "\n\n")
        
        from datetime import datetime
        
        # Log de inicio
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Sistema iniciado\n")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Imágenes base cargadas\n")
        
        # Logs de actividad
        if hasattr(self, 'project_manager') and hasattr(self.project_manager, 'last_save_time'):
            if self.project_manager.last_save_time:
                logs.append(f"[{self.project_manager.last_save_time.strftime('%H:%M:%S')}] Proyecto guardado\n")
        
        # Estado actual
        logs.append(f"\n📊 ESTADO ACTUAL:\n")
        logs.append(f"   • Secciones activas: {len(self.secciones_activas)}\n")
        logs.append(f"   • Referencias: {len(self.referencias)}\n")
        logs.append(f"   • Palabras totales: {self.stats.get('total_words', 0)}\n")
        
        self.validation_text.insert("1.0", ''.join(logs))

    def mostrar_sugerencias(self):
        """Muestra sugerencias inteligentes para mejorar el proyecto"""
        sugerencias = []
        sugerencias.append("💡 SUGERENCIAS INTELIGENTES\n")
        sugerencias.append("="*60 + "\n\n")
        
        # Analizar estado del proyecto
        palabras_totales = self.stats.get('total_words', 0)
        secciones_completas = self.stats.get('sections_completed', 0)
        referencias_total = len(self.referencias)
        
        # Sugerencias basadas en análisis
        if palabras_totales < 1000:
            sugerencias.append("📝 CONTENIDO:\n")
            sugerencias.append("   • El proyecto tiene pocas palabras. Considera expandir las secciones principales.\n")
            sugerencias.append("   • Objetivo mínimo recomendado: 3000-5000 palabras\n\n")
        
        if referencias_total < 5:
            sugerencias.append("📚 REFERENCIAS:\n")
            sugerencias.append("   • Agrega más referencias bibliográficas (mínimo 10-15 recomendadas)\n")
            sugerencias.append("   • Incluye fuentes variadas: libros, artículos, sitios web confiables\n\n")
        
        # Verificar secciones críticas
        secciones_vacias = []
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles and seccion_id in self.content_texts:
                seccion = self.secciones_disponibles[seccion_id]
                if seccion.get('requerida', False) and not seccion.get('capitulo', False):
                    content = self.content_texts[seccion_id].get("1.0", "end").strip()
                    if len(content) < 50:
                        secciones_vacias.append(seccion['titulo'])
        
        if secciones_vacias:
            sugerencias.append("⚠️ SECCIONES REQUERIDAS VACÍAS:\n")
            for seccion in secciones_vacias:
                sugerencias.append(f"   • {seccion}\n")
            sugerencias.append("\n")
        
        # Sugerencias de formato
        sugerencias.append("🎨 FORMATO Y ESTILO:\n")
        if self.formato_config.get('interlineado', 2.0) != 2.0:
            sugerencias.append("   • Considera usar interlineado doble (estándar académico)\n")
        
        # Sugerencias de mejora
        sugerencias.append("\n✨ MEJORAS RECOMENDADAS:\n")
        sugerencias.append("   • Revisa la coherencia entre objetivos y conclusiones\n")
        sugerencias.append("   • Asegúrate de citar todas las referencias en el texto\n")
        sugerencias.append("   • Incluye gráficos o tablas si son relevantes\n")
        sugerencias.append("   • Verifica ortografía y gramática antes de generar\n")
        
        self.validation_text.insert("1.0", ''.join(sugerencias))

    def cambiar_modo_preview(self, valor):
        """Cambia el modo de vista previa"""
        self.actualizar_preview()

    def generar_preview_formato(self):
        """Genera vista previa con formato aplicado"""
        preview = []
        preview.append("VISTA PREVIA CON FORMATO\n")
        preview.append("="*40 + "\n\n")
        
        # Mostrar configuración actual
        preview.append("📋 FORMATO APLICADO:\n")
        preview.append(f"   • Fuente: {self.formato_config['fuente_texto']} {self.formato_config['tamaño_texto']}pt\n")
        preview.append(f"   • Títulos: {self.formato_config['fuente_titulo']} {self.formato_config['tamaño_titulo']}pt\n")
        preview.append(f"   • Interlineado: {self.formato_config['interlineado']}\n")
        preview.append(f"   • Márgenes: {self.formato_config['margen']}cm\n")
        preview.append(f"   • Justificado: {'Sí' if self.formato_config['justificado'] else 'No'}\n")
        preview.append(f"   • Sangría: {'Sí' if self.formato_config['sangria'] else 'No'}\n\n")
        
        preview.append("-"*40 + "\n\n")
        
        # Ejemplo de texto formateado
        preview.append("INTRODUCCIÓN\n\n")
        preview.append("     Este es un ejemplo de cómo se verá el texto con el formato aplicado. ")
        preview.append("La primera línea de cada párrafo tendrá sangría si está activada. ")
        preview.append("El texto estará justificado para una apariencia profesional.\n\n")
        
        preview.append("     Un segundo párrafo mostraría la consistencia del formato. ")
        preview.append("Las citas aparecerían así (García, 2020) integradas en el texto.\n\n")
        
        return ''.join(preview)

    def ocultar_preview(self):
        """Oculta la ventana de vista previa en lugar de destruirla"""
        if hasattr(self, 'preview_window'):
            self.preview_window.withdraw()

    @property
    def documento_base(self):
        """Getter para documento_base"""
        if not hasattr(self, '_documento_base'):
            self._documento_base = None
        return self._documento_base

    @documento_base.setter
    def documento_base(self, value):
        """Setter para documento_base"""
        self._documento_base = value

    @property
    def contenido_guardado(self):
        """Getter para contenido_guardado"""
        if not hasattr(self, '_contenido_guardado'):
            self._contenido_guardado = {}
        return self._contenido_guardado

    @contenido_guardado.setter
    def contenido_guardado(self, value):
        """Setter para contenido_guardado"""
        self._contenido_guardado = value
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# Incluir aquí todos los métodos restantes necesarios que no se han movido a módulos separados
# [Agregar métodos como actualizar_lista_secciones, crear_pestanas_contenido, etc.]

    
    # Métodos de secciones (coordinación con UI)
    def actualizar_lista_secciones(self):
        """Actualiza la lista visual de secciones activas"""
        # Implementación en contenido_dinamico_tab
        if hasattr(self, 'contenido_dinamico_tab'):
            # Delegar a la pestaña
            pass
    
    def crear_pestanas_contenido(self):
        """Crea las pestañas de contenido dinámicamente"""
        if hasattr(self, 'content_tabview'):
            # Guardar contenido actual antes de recrear
            contenido_temporal = {}
            for seccion_id, text_widget in self.content_texts.items():
                contenido_temporal[seccion_id] = text_widget.get("1.0", "end-1c")
            
            # Limpiar pestañas existentes
            for tab in list(self.content_tabview._tab_dict.keys()):
                self.content_tabview.delete(tab)
            
            # Limpiar diccionario de widgets
            self.content_texts.clear()
            
            # Crear nuevas pestañas según secciones activas
            for seccion_id in self.secciones_activas:
                if seccion_id in self.secciones_disponibles:
                    seccion = self.secciones_disponibles[seccion_id]
                    
                    # No crear pestaña para capítulos (solo son títulos)
                    if not seccion.get('capitulo', False):
                        tab = self.content_tabview.add(seccion['titulo'])
                        self._crear_contenido_seccion(tab, seccion_id, seccion)
                        
                        # Restaurar contenido si existía
                        if seccion_id in contenido_temporal and seccion_id in self.content_texts:
                            self.content_texts[seccion_id].insert("1.0", contenido_temporal[seccion_id])
            
            # Actualizar breadcrumb si existe
            if hasattr(self, 'breadcrumb_label'):
                current_tab = self.content_tabview.get() if self.content_tabview._tab_dict else ""
                self.breadcrumb_label.configure(text=f"📍 Navegación: {current_tab}")
    
    # Métodos de gestión de secciones
    def agregar_seccion(self):
        """Agrega una nueva sección personalizada"""
        from .dialogs import SeccionDialog
        
        dialog = SeccionDialog(self.root, self.secciones_disponibles)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            seccion_id, seccion_data = dialog.result
            try:
                # Agregar a secciones disponibles
                self.secciones_disponibles[seccion_id] = seccion_data
                self.secciones_activas.append(seccion_id)
                
                # Actualizar UI
                self.actualizar_lista_secciones()
                self.crear_pestanas_contenido()
                messagebox.showinfo("✅ Agregada", f"Sección '{seccion_data['titulo']}' agregada correctamente")
            except Exception as e:
                messagebox.showerror("❌ Error", str(e))
    
    def quitar_seccion(self):
        """Quita la sección seleccionada de las activas"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección por el título
            seccion_id = None
            for sid, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    seccion_id = sid
                    break
            
            if seccion_id and seccion_id in self.secciones_activas:
                seccion = self.secciones_disponibles[seccion_id]
                
                # Verificar si es requerida
                if seccion.get('requerida', False):
                    messagebox.showwarning("⚠️ Sección Requerida", 
                        "Esta sección es requerida y no puede ser eliminada")
                    return
                
                # Confirmar eliminación
                if messagebox.askyesno("🗑️ Confirmar", 
                    f"¿Desactivar la sección '{seccion['titulo']}'?"):
                    self.secciones_activas.remove(seccion_id)
                    self.actualizar_lista_secciones()
                    self.crear_pestanas_contenido()
                    messagebox.showinfo("✅ Desactivada", "Sección desactivada correctamente")

    def editar_seccion(self):
        """Edita la sección actual"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección
            seccion_id = None
            for sid, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    seccion_id = sid
                    break
            
            if seccion_id:
                from .dialogs import SeccionDialog
                
                dialog = SeccionDialog(
                    self.root, 
                    self.secciones_disponibles,
                    editar=True,
                    seccion_actual=(seccion_id, self.secciones_disponibles[seccion_id])
                )
                
                self.root.wait_window(dialog.dialog)
                
                if dialog.result:
                    _, seccion_data = dialog.result
                    self.secciones_disponibles[seccion_id].update(seccion_data)
                    self.actualizar_lista_secciones()
                    self.crear_pestanas_contenido()
                    messagebox.showinfo("✅ Actualizada", "Sección actualizada correctamente")

    def subir_seccion(self):
        """Sube la sección actual en el orden"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección
            for seccion_id, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    if seccion_id in self.secciones_activas:
                        index = self.secciones_activas.index(seccion_id)
                        if index > 0:
                            # Intercambiar con la anterior
                            self.secciones_activas[index], self.secciones_activas[index-1] = \
                                self.secciones_activas[index-1], self.secciones_activas[index]
                            self.actualizar_lista_secciones()
                            self.crear_pestanas_contenido()
                            # Mantener la pestaña actual seleccionada
                            self.content_tabview.set(current_tab)
                    break

    def bajar_seccion(self):
        """Baja la sección actual en el orden"""
        if hasattr(self, 'content_tabview') and self.content_tabview._tab_dict:
            current_tab = self.content_tabview.get()
            
            # Buscar el ID de la sección
            for seccion_id, seccion in self.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    if seccion_id in self.secciones_activas:
                        index = self.secciones_activas.index(seccion_id)
                        if index < len(self.secciones_activas) - 1:
                            # Intercambiar con la siguiente
                            self.secciones_activas[index], self.secciones_activas[index+1] = \
                                self.secciones_activas[index+1], self.secciones_activas[index]
                            self.actualizar_lista_secciones()
                            self.crear_pestanas_contenido()
                            # Mantener la pestaña actual seleccionada
                            self.content_tabview.set(current_tab)
                    break
    def agregar_referencia(self):
        """Versión actualizada usando state manager"""
        # Recopilar datos del formulario
        if all([
            hasattr(self, 'ref_tipo'),
            hasattr(self, 'ref_autor'),
            hasattr(self, 'ref_año'),
            hasattr(self, 'ref_titulo'),
            hasattr(self, 'ref_fuente')
        ]):
            ref_data = {
                'tipo': self.ref_tipo.get(),
                'autor': self.ref_autor.get().strip(),
                'año': self.ref_año.get().strip(),
                'titulo': self.ref_titulo.get().strip(),
                'fuente': self.ref_fuente.get().strip()
            }
            
            try:
                # Usar el reference_manager para validar
                ref_validada = self.reference_manager.agregar_referencia(ref_data)
                
                # Actualizar estado global
                state_manager.add_referencia(ref_validada)
                
                # Actualizar UI local
                self.referencias = state_manager.get_state().referencias
                self.actualizar_lista_referencias()
                
                # Limpiar campos
                self.ref_autor.delete(0, "end")
                self.ref_año.delete(0, "end")
                self.ref_titulo.delete(0, "end")
                self.ref_fuente.delete(0, "end")
                
                messagebox.showinfo("✅ Agregada", "Referencia agregada correctamente")
                
            except ValueError as e:
                messagebox.showerror("❌ Error", str(e))
    
    def actualizar_lista_referencias(self):
        """Actualiza la lista visual de referencias"""
        # Implementación básica
        pass
    
    # Métodos de formato
    def toggle_formato_base(self):
        """Activa/desactiva el uso del formato base"""
        if self.usar_base_var.get():
            if self.documento_base is None:
                self.cargar_documento_base()
            else:
                self.aplicar_formato_base()
        else:
            self.limpiar_formato_base()
    
    def aplicar_formato_base(self):
        """Aplica los datos del formato base"""
        if self.documento_base:
            for key, value in self.documento_base.items():
                if key in self.proyecto_data:
                    self.proyecto_data[key].delete(0, "end")
                    self.proyecto_data[key].insert(0, value)
            
            messagebox.showinfo("✅ Aplicado", "Formato base aplicado correctamente")
    
    def limpiar_formato_base(self):
        """Limpia los datos del formato base"""
        campos_base = ['institucion', 'ciclo', 'curso', 'enfasis', 'director']
        for campo in campos_base:
            if campo in self.proyecto_data:
                self.proyecto_data[campo].delete(0, "end")
    
    def aplicar_formato(self):
        """Aplica la configuración de formato"""
        self.formato_config = {
            'fuente_texto': self.fuente_texto.get(),
            'tamaño_texto': int(self.tamaño_texto.get()),
            'fuente_titulo': self.fuente_titulo.get(),
            'tamaño_titulo': int(self.tamaño_titulo.get()),
            'interlineado': float(self.interlineado.get()),
            'margen': float(self.margen.get()),
            'justificado': self.justificado_var.get(),
            'sangria': self.sangria_var.get()
        }
        
        messagebox.showinfo("✅ Aplicado", "Configuración de formato aplicada correctamente")
    
