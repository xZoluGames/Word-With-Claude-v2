
from utils.logger import get_logger

logger = get_logger("__init__")

"""
Tabs Module - Pestañas de la interfaz principal
"""

from .info_general import InfoGeneralTab
from .contenido_dinamico import ContenidoDinamicoTab
from .citas_referencias import CitasReferenciasTab
from .formato_avanzado import FormatoAvanzadoTab
from .generacion import GeneracionTab

__all__ = [
    'InfoGeneralTab',
    'ContenidoDinamicoTab',
    'CitasReferenciasTab',
    'FormatoAvanzadoTab',
    'GeneracionTab'
]
