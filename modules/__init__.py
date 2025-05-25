"""
Modules - Módulos especializados del generador de proyectos académicos
"""

from .citations import CitationProcessor
from .references import ReferenceManager
from .sections import SectionManager

__all__ = [
    'CitationProcessor',
    'ReferenceManager',
    'SectionManager'
]