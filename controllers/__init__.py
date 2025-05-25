# controllers/__init__.py
"""
Controladores - Separación de lógica de negocio de la UI
"""

from .section_controller import SectionController
from .reference_controller import ReferenceController
from .preview_controller import PreviewController
from .image_controller import ImageController
from .project_controller import ProjectController

__all__ = [
    'SectionController',
    'ReferenceController', 
    'PreviewController',
    'ImageController',
    'ProjectController'
]