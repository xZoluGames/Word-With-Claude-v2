# controllers/section_controller.py
"""
Controlador de Secciones - Maneja toda la lógica relacionada con secciones
"""

from typing import Dict, List, Optional
from modules.sections import SectionManager
from core.state_manager import state_manager
from utils.logger import get_logger
from tkinter import messagebox

logger = get_logger('SectionController')

class SectionController:
    """Controlador para gestión de secciones"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.section_manager = SectionManager()
        logger.info("SectionController inicializado")
    
    def agregar_seccion(self, seccion_id: str, seccion_data: Dict) -> bool:
        """Agrega una nueva sección con validación completa"""
        try:
            # Usar el section_manager existente
            seccion = self.section_manager.agregar_seccion(seccion_id, seccion_data)
            
            # Actualizar estado global
            state_manager.update_state(
                secciones_disponibles=self.section_manager.secciones_disponibles,
                secciones_activas=self.section_manager.secciones_activas
            )
            
            # Actualizar UI
            self._actualizar_ui()
            
            logger.info(f"Sección agregada: {seccion_id}")
            return True
            
        except ValueError as e:
            logger.error(f"Error agregando sección: {e}")
            messagebox.showerror("Error", str(e))
            return False
    
    def eliminar_seccion(self, seccion_id: str) -> bool:
        """Elimina una sección"""
        try:
            self.section_manager.eliminar_seccion(seccion_id)
            
            # Actualizar estado
            state_manager.update_state(
                secciones_disponibles=self.section_manager.secciones_disponibles,
                secciones_activas=self.section_manager.secciones_activas
            )
            
            self._actualizar_ui()
            return True
            
        except ValueError as e:
            logger.error(f"Error eliminando sección: {e}")
            messagebox.showerror("Error", str(e))
            return False
    
    def mover_seccion(self, seccion_id: str, direccion: str) -> bool:
        """Mueve una sección arriba o abajo"""
        try:
            nueva_posicion = self.section_manager.mover_seccion(seccion_id, direccion)
            
            # Actualizar estado
            state_manager.update_state(
                secciones_activas=self.section_manager.secciones_activas
            )
            
            self._actualizar_ui()
            return True
            
        except ValueError as e:
            logger.error(f"Error moviendo sección: {e}")
            return False
    
    def obtener_seccion_actual(self) -> Optional[str]:
        """Obtiene el ID de la sección actualmente seleccionada"""
        if hasattr(self.app, 'content_tabview') and self.app.content_tabview._tab_dict:
            current_tab = self.app.content_tabview.get()
            
            # Buscar el ID por título
            for seccion_id, seccion in self.section_manager.secciones_disponibles.items():
                if seccion['titulo'] == current_tab:
                    return seccion_id
        return None
    
    def _actualizar_ui(self):
        """Actualiza la UI después de cambios"""
        if hasattr(self.app, 'actualizar_lista_secciones'):
            self.app.actualizar_lista_secciones()
        if hasattr(self.app, 'crear_pestanas_contenido'):
            self.app.crear_pestanas_contenido()
        if hasattr(self.app, 'actualizar_estadisticas'):
            self.app.actualizar_estadisticas()