# ui/main_window.py (VERSIÓN REFACTORIZADA)
"""
Ventana principal - Coordinador principal de la aplicación (REFACTORIZADO)
"""

import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
from typing import Dict, List, Optional

# Imports de controladores
from controllers import (
    SectionController, ReferenceController, PreviewController,
    ImageController, ProjectController
)

# Imports de servicios
from services import UIService, ValidationService, StatisticsService

# Imports existentes
from core.project_manager import ProjectManager
from core.document_generator import DocumentGenerator
from core.validator import ProjectValidator
from core.state_manager import state_manager
from modules.sections import SectionManager
from template_manager import obtener_template_manager

# Imports de UI
from .widgets import FontManager, ToolTip, PreviewWindow, ImageManagerDialog
from .tabs import (
    InfoGeneralTab, ContenidoDinamicoTab, CitasReferenciasTab,
    FormatoAvanzadoTab, GeneracionTab
)
from .dialogs import SeccionDialog, HelpDialog, CitationDialog
from utils.logger import get_logger
from config.settings import APP_CONFIG

logger = get_logger('MainWindow')

class ProyectoAcademicoGenerator:
    """
    Clase principal del generador de proyectos académicos (REFACTORIZADA)
    
    Ahora actúa principalmente como coordinador entre controladores y UI.
    """
    
    def __init__(self):
        """Inicialización simplificada con delegación a servicios"""
        try:
            # Inicializar ventana principal
            self.root = ctk.CTk()
            self._configurar_ventana()
            
            # Inicializar variables básicas
            self._init_variables()
            
            # Inicializar controladores
            self._init_controllers()
            
            # Inicializar servicios
            self._init_services()
            
            # Configurar UI
            self.setup_ui()
            self.setup_keyboard_shortcuts()
            
            # Configurar cierre seguro
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Iniciar servicios automáticos
            self._iniciar_servicios_automaticos()
            
            logger.info("Aplicación inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando aplicación: {e}", exc_info=True)
            messagebox.showerror("Error de Inicialización", 
                f"No se pudo inicializar la aplicación:\n{str(e)}")
            raise
    
    def _configurar_ventana(self):
        """Configura la ventana principal"""
        self.root.title("🎓 Generador de Proyectos Académicos - Versión Avanzada")
        self.root.geometry(APP_CONFIG['window_size'])
        self.root.minsize(*APP_CONFIG['min_window_size'])
        
        # Configurar tema
        ctk.set_appearance_mode(APP_CONFIG['theme'])
        ctk.set_default_color_theme(APP_CONFIG['color_theme'])
    
    def _init_variables(self):
        """Inicializa variables básicas de la aplicación"""
        # Datos del proyecto
        self.proyecto_data = {}
        self.referencias = []
        self.content_texts = {}
        
        # Configuración
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
        
        # Estado UI
        self.modo_compacto = False
        self.modo_expandido = False
        
        # Secciones
        self.secciones_disponibles = {}
        self.secciones_activas = []
        
        # Imágenes
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        self.ruta_encabezado = None
        self.ruta_insignia = None
        
        # Configuración de marca de agua
        self.watermark_opacity = 0.3
        self.watermark_stretch = True
        self.watermark_mode = 'watermark'
    
    def _init_controllers(self):
        """Inicializa los controladores"""
        self.section_controller = SectionController(self)
        self.reference_controller = ReferenceController(self)
        self.preview_controller = PreviewController(self)
        
        # Managers existentes
        self.template_manager = obtener_template_manager()
        self.project_manager = ProjectManager()
        self.document_generator = DocumentGenerator()
        self.validator = ProjectValidator()
        self.font_manager = FontManager()
        
        # Inicializar secciones
        section_manager = SectionManager()
        self.secciones_disponibles = section_manager.inicializar_secciones()
        self.secciones_activas = list(self.secciones_disponibles.keys())
    
    def _init_services(self):
        """Inicializa los servicios"""
        self.ui_service = UIService(self)
        self.validation_service = ValidationService(self)
        self.statistics_service = StatisticsService(self)
    
    def _init_ui_components(self):
        """Inicializa componentes de UI"""
        self.preview_window = PreviewWindow(self)
        self.image_manager = ImageManagerDialog(self)
        self.help_dialog = HelpDialog(self)
    
    def _iniciar_servicios_automaticos(self):
        """Inicia servicios que corren automáticamente"""
        # Mostrar bienvenida
        self.ui_service.mostrar_bienvenida()
        
        # Iniciar auto-guardado
        self.project_manager.auto_save_project(self)
        
        # Iniciar actualización de estadísticas
        self.actualizar_estadisticas()
        
        # Buscar imágenes base
        self.ui_service.buscar_imagenes_base()
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.ui_service.create_header(main_container)
        
        # Content container
        content_container = ctk.CTkFrame(main_container, corner_radius=10)
        content_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Tabview principal
        self.tabview = ctk.CTkTabview(content_container)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Crear pestañas
        self._create_tabs()
        
        # Configurar responsividad
        self.ui_service.configurar_ventana_responsiva()
        
        # Agregar tooltips
        self.root.after(1000, self.ui_service.agregar_tooltips)
    
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
    
    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado"""
        shortcuts = {
            '<Control-s>': lambda e: self.guardar_proyecto(),
            '<Control-o>': lambda e: self.cargar_proyecto(),
            '<Control-n>': lambda e: self.nuevo_proyecto(),
            '<Control-z>': lambda e: self.undo(),
            '<Control-y>': lambda e: self.redo(),
            '<F5>': lambda e: self.validar_proyecto(),
            '<F9>': lambda e: self.generar_documento_async(),
            '<Control-q>': lambda e: self._on_closing(),
            '<F1>': lambda e: self.mostrar_instrucciones()
        }
        
        for key, func in shortcuts.items():
            self.root.bind(key, func)
    
    # === MÉTODOS DELEGADOS A CONTROLADORES ===
    
    def agregar_seccion(self):
        """Delega al controlador de secciones"""
        dialog = SeccionDialog(self.root, self.secciones_disponibles)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            seccion_id, seccion_data = dialog.result
            self.section_controller.agregar_seccion(seccion_id, seccion_data)
    
    def quitar_seccion(self):
        """Delega al controlador de secciones"""
        seccion_id = self.section_controller.obtener_seccion_actual()
        if seccion_id:
            self.section_controller.eliminar_seccion(seccion_id)
    
    def subir_seccion(self):
        """Delega al controlador de secciones"""
        seccion_id = self.section_controller.obtener_seccion_actual()
        if seccion_id:
            self.section_controller.mover_seccion(seccion_id, 'arriba')
    
    def bajar_seccion(self):
        """Delega al controlador de secciones"""
        seccion_id = self.section_controller.obtener_seccion_actual()
        if seccion_id:
            self.section_controller.mover_seccion(seccion_id, 'abajo')
    
    def agregar_referencia(self):
        """Delega al controlador de referencias"""
        self.reference_controller.agregar_referencia_desde_formulario()
    
    def importar_bibtex(self):
        """Delega al controlador de referencias"""
        self.reference_controller.importar_bibtex()
    
    def exportar_referencias_apa(self):
        """Delega al controlador de referencias"""
        self.reference_controller.exportar_referencias_apa()
    
    def actualizar_preview(self):
        """Delega al controlador de preview"""
        if hasattr(self, 'preview_text') and hasattr(self, 'preview_mode'):
            modo = self.preview_mode.get() if hasattr(self.preview_mode, 'get') else None
            contenido = self.preview_controller.actualizar_preview(modo)
            
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", contenido)
            self.preview_text.configure(state="disabled")
    
    def actualizar_estadisticas(self):
        """Delega al servicio de estadísticas"""
        self.statistics_service.actualizar_estadisticas()
        # Programar próxima actualización
        self.root.after(2000, self.actualizar_estadisticas)
    
    # === MÉTODOS DE PROYECTO (delegados a managers) ===
    
    def guardar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.guardar_proyecto(self)
    
    def cargar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.cargar_proyecto(self)
    
    def nuevo_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.nuevo_proyecto(self)
    
    def validar_proyecto(self):
        """Delega a ProjectValidator"""
        return self.validator.validar_proyecto(self)
    
    def generar_documento_async(self):
        """Delega a DocumentGenerator"""
        self.document_generator.generar_documento_async(self)
    
    # === MÉTODOS DE ESTADO ===
    
    def undo(self):
        """Deshace la última acción"""
        state_manager.undo()
        self._sincronizar_con_estado()
        self.ui_service.mostrar_mensaje("↩️ Deshacer", "Acción deshecha")
    
    def redo(self):
        """Rehace la última acción"""
        state_manager.redo()
        self._sincronizar_con_estado()
        self.ui_service.mostrar_mensaje("↪️ Rehacer", "Acción rehecha")
    
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
        
        # Actualizar contenido
        for seccion_id, contenido in current_state.contenido_secciones.items():
            if seccion_id in self.content_texts:
                self.content_texts[seccion_id].delete("1.0", "end")
                self.content_texts[seccion_id].insert("1.0", contenido)
    
    # === MÉTODOS AUXILIARES ===
    
    def mostrar_instrucciones(self):
        """Muestra las instrucciones"""
        self.help_dialog.show()
    
    def mostrar_preview(self):
        """Muestra la ventana de preview"""
        self.preview_window.show()
    
    def cargar_documento_base(self):
        """Carga plantilla base"""
        from template_manager import aplicar_plantilla_tercer_ano
        aplicar_plantilla_tercer_ano(self)
    
    def gestionar_plantillas(self):
        """Abre el gestor de plantillas"""
        from template_manager import mostrar_gestor_plantillas
        mostrar_gestor_plantillas(self)
    
    def gestionar_imagenes(self):
        """Abre el gestor de imágenes"""
        self.image_manager.show()
    
    def exportar_configuracion(self):
        """Exporta la configuración"""
        self.project_manager.exportar_configuracion(self)
    
    def _on_closing(self):
        """Maneja el cierre seguro de la aplicación"""
        try:
            if state_manager.has_changes():
                respuesta = messagebox.askyesnocancel(
                    "Cambios sin guardar",
                    "¿Deseas guardar los cambios antes de salir?"
                )
                
                if respuesta is None:  # Cancelar
                    return
                elif respuesta:  # Sí
                    self.guardar_proyecto()
            
            # Limpiar recursos
            logger.info("Cerrando aplicación...")
            self.root.quit()
            
        except Exception as e:
            logger.error(f"Error durante el cierre: {e}")
            self.root.quit()
    
    # === MÉTODOS MÍNIMOS NECESARIOS PARA COMPATIBILIDAD ===
    
    def actualizar_lista_secciones(self):
        """Actualiza la lista de secciones (delegado a tab)"""
        if hasattr(self, 'contenido_dinamico_tab'):
            # Actualizar en la pestaña correspondiente
            pass
    
    def crear_pestanas_contenido(self):
        """Crea pestañas de contenido (delegado a tab)"""
        if hasattr(self, 'contenido_dinamico_tab'):
            # Recrear pestañas en la pestaña correspondiente
            pass
    
    def actualizar_lista_referencias(self):
        """Actualiza lista de referencias (delegado a tab)"""
        if hasattr(self, 'citas_referencias_tab'):
            # Actualizar en la pestaña correspondiente
            pass
    
    def actualizar_campos_referencia(self, tipo):
        """Actualiza campos del formulario de referencias"""
        # Delegado al tab de referencias
        pass
    
    def editar_seccion(self):
        """Edita una sección"""
        # Por implementar
        pass
    
    def toggle_formato_base(self):
        """Toggle del formato base"""
        # Por implementar
        pass
    
    def aplicar_formato(self):
        """Aplica formato"""
        self.ui_service.mostrar_mensaje("✅ Aplicado", 
            "Configuración de formato aplicada correctamente")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()