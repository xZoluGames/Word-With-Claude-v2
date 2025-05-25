"""
Core - Módulos principales del generador de proyectos académicos
"""

from .project_manager import ProjectManager
from .document_generator import DocumentGenerator
from .validator import ProjectValidator

__all__ = [
    'ProjectManager',
    'DocumentGenerator', 
    'ProjectValidator'
]