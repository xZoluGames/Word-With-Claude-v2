
from utils.logger import get_logger

logger = get_logger("state_manager")

"""
Gestión centralizada del estado de la aplicación
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime

@dataclass
class ProjectState:
    """Estado completo del proyecto"""
    # Información general
    proyecto_data: Dict[str, str] = field(default_factory=dict)
    
    # Secciones
    secciones_disponibles: Dict[str, Dict] = field(default_factory=dict)
    secciones_activas: List[str] = field(default_factory=list)
    contenido_secciones: Dict[str, str] = field(default_factory=dict)
    
    # Referencias
    referencias: List[Dict] = field(default_factory=list)
    
    # Configuración
    formato_config: Dict[str, Any] = field(default_factory=dict)
    
    # Imágenes
    encabezado_personalizado: Optional[str] = None
    insignia_personalizada: Optional[str] = None
    
    # Metadatos
    fecha_creacion: str = field(default_factory=lambda: datetime.now().isoformat())
    fecha_modificacion: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "2.0"

class StateManager:
    """Gestor centralizado del estado de la aplicación"""
    
    def __init__(self):
        self.state = ProjectState()
        self._observers = []
        self._undo_stack = []
        self._redo_stack = []
        self._max_undo_size = 50
    
    def get_state(self) -> ProjectState:
        """Obtiene el estado actual"""
        return self.state
    
    def update_state(self, **kwargs):
        """Actualiza el estado y notifica observadores"""
        # Guardar estado para undo
        self._save_undo_state()
        
        # Actualizar campos
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        
        self.state.fecha_modificacion = datetime.now().isoformat()
        
        # Notificar observadores
        self._notify_observers()
    
    def update_proyecto_data(self, key: str, value: str):
        """Actualiza un campo específico de proyecto_data"""
        self._save_undo_state()
        self.state.proyecto_data[key] = value
        self.state.fecha_modificacion = datetime.now().isoformat()
        self._notify_observers()
    
    def update_contenido_seccion(self, seccion_id: str, contenido: str):
        """Actualiza el contenido de una sección"""
        self._save_undo_state()
        self.state.contenido_secciones[seccion_id] = contenido
        self.state.fecha_modificacion = datetime.now().isoformat()
        self._notify_observers()
    
    def add_referencia(self, referencia: Dict):
        """Agrega una referencia"""
        self._save_undo_state()
        self.state.referencias.append(referencia)
        self.state.fecha_modificacion = datetime.now().isoformat()
        self._notify_observers()
    
    def remove_referencia(self, index: int):
        """Elimina una referencia"""
        if 0 <= index < len(self.state.referencias):
            self._save_undo_state()
            self.state.referencias.pop(index)
            self.state.fecha_modificacion = datetime.now().isoformat()
            self._notify_observers()
    
    def subscribe(self, callback):
        """Suscribe un observador para cambios de estado"""
        self._observers.append(callback)
    
    def unsubscribe(self, callback):
        """Desuscribe un observador"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notifica a todos los observadores de cambios"""
        for observer in self._observers:
            try:
                observer(self.state)
            except Exception as e:
                print(f"Error notificando observador: {e}")
    
    def _save_undo_state(self):
        """Guarda el estado actual para undo"""
        # Crear copia profunda del estado
        state_copy = self.export_state()
        self._undo_stack.append(state_copy)
        
        # Limpiar redo stack
        self._redo_stack.clear()
        
        # Limitar tamaño del stack
        if len(self._undo_stack) > self._max_undo_size:
            self._undo_stack.pop(0)
    
    def undo(self):
        """Deshace el último cambio"""
        if self._undo_stack:
            # Guardar estado actual en redo
            current_state = self.export_state()
            self._redo_stack.append(current_state)
            
            # Restaurar estado anterior
            previous_state = self._undo_stack.pop()
            self.import_state(previous_state)
            self._notify_observers()
    
    def redo(self):
        """Rehace el último cambio deshecho"""
        if self._redo_stack:
            # Guardar estado actual en undo
            current_state = self.export_state()
            self._undo_stack.append(current_state)
            
            # Restaurar estado siguiente
            next_state = self._redo_stack.pop()
            self.import_state(next_state)
            self._notify_observers()
    
    def export_state(self) -> Dict:
        """Exporta el estado a diccionario"""
        return {
            'proyecto_data': self.state.proyecto_data.copy(),
            'secciones_disponibles': self.state.secciones_disponibles.copy(),
            'secciones_activas': self.state.secciones_activas.copy(),
            'contenido_secciones': self.state.contenido_secciones.copy(),
            'referencias': self.state.referencias.copy(),
            'formato_config': self.state.formato_config.copy(),
            'encabezado_personalizado': self.state.encabezado_personalizado,
            'insignia_personalizada': self.state.insignia_personalizada,
            'fecha_creacion': self.state.fecha_creacion,
            'fecha_modificacion': self.state.fecha_modificacion,
            'version': self.state.version
        }
    
    def import_state(self, state_dict: Dict):
        """Importa estado desde diccionario"""
        for key, value in state_dict.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
    
    def reset_state(self):
        """Reinicia el estado a valores por defecto"""
        self._save_undo_state()
        self.state = ProjectState()
        self._notify_observers()
    
    def has_changes(self) -> bool:
        """Verifica si hay cambios sin guardar"""
        # Comparar con el último estado guardado
        if not self._undo_stack:
            return False
        
        current = self.export_state()
        last_saved = self._undo_stack[-1] if self._undo_stack else {}
        
        # Comparar excluyendo fecha_modificacion
        current.pop('fecha_modificacion', None)
        last_saved.pop('fecha_modificacion', None)
        
        return current != last_saved

# Instancia global
state_manager = StateManager()