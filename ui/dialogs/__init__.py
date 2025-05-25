
from utils.logger import get_logger

logger = get_logger("__init__")

"""
Dialogs Module - Ventanas de diálogo de la aplicación
"""

from .section_dialog import SeccionDialog
from .citation_dialog import CitationDialog
from .help_dialog import HelpDialog

__all__ = [
    'SeccionDialog',
    'CitationDialog',
    'HelpDialog'
]
