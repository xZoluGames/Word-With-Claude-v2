
from utils.logger import get_logger

logger = get_logger("__init__")

"""
UI - Interfaz de usuario del generador de proyectos académicos
"""

from .main_window import ProyectoAcademicoGenerator
from .widgets import FontManager, ToolTip
from .components import StatsPanel, FormatPanel

__all__ = [
    'ProyectoAcademicoGenerator',
    'FontManager',
    'ToolTip',
    'StatsPanel',
    'FormatPanel'
]
