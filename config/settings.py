
from utils.logger import get_logger

logger = get_logger("settings")

"""
Configuración centralizada del proyecto
"""

# Configuración de la aplicación
APP_CONFIG = {
    'name': 'Generador de Proyectos Académicos',
    'version': '2.0',
    'window_size': '1200x700',
    'min_window_size': (1000, 600),
    'theme': 'dark',
    'color_theme': 'blue'
}

# Configuración de auto-guardado
AUTOSAVE_CONFIG = {
    'enabled': True,
    'interval': 300000,  # 5 minutos en milisegundos
    'filename': 'auto_save.json'
}

# Configuración de formato por defecto
DEFAULT_FORMAT = {
    'fuente_texto': 'Times New Roman',
    'tamaño_texto': 12,
    'fuente_titulo': 'Times New Roman',
    'tamaño_titulo': 14,
    'interlineado': 2.0,
    'margen': 2.54,
    'justificado': True,
    'sangria': True
}

# Validación
VALIDATION_CONFIG = {
    'min_section_length': 50,
    'min_references': 0,
    'required_fields': ['titulo', 'estudiantes', 'tutores']
}

# Rutas de recursos
RESOURCES_PATHS = {
    'images': 'resources/images',
    'templates': 'plantillas',
    'exports': 'exports'
}

# Colores válidos para botones
BUTTON_COLORS = {
    'default': None,
    'green': {'fg': '#228B22', 'hover': '#006400'},
    'blue': {'fg': '#4682B4', 'hover': '#191970'},
    'purple': {'fg': '#9370DB', 'hover': '#7B68EE'},
    'orange': {'fg': '#FF8C00', 'hover': '#FF6347'},
    'red': {'fg': '#DC143C', 'hover': '#8B0000'},
    'indigo': {'fg': '#4B0082', 'hover': '#8B008B'}
}

# Secciones que permiten citas
CITATION_SECTIONS = ['marco_teorico', 'introduccion', 'desarrollo', 'discusion']

# Límites de texto
TEXT_LIMITS = {
    'resumen_min': 150,
    'resumen_max': 300,
    'titulo_max': 200,
    'palabras_proyecto_min': 3000,
    'palabras_proyecto_max': 10000
}
# Colores de la interfaz
UI_COLORS = {
    'primary': '#4682B4',      # Steel Blue
    'success': '#228B22',      # Forest Green
    'danger': '#DC143C',       # Crimson
    'warning': '#FFA500',      # Orange
    'info': '#4B0082',         # Indigo
    'purple': '#9370DB',       # Medium Purple
    'dark': '#191970',         # Midnight Blue
    'light': '#F0F0F0',        # Light Gray
    'background': {
        'dark': '#212121',
        'medium': '#424242',
        'light': '#616161'
    },
    'text': {
        'primary': '#FFFFFF',
        'secondary': '#B0B0B0',
        'disabled': '#707070'
    }
}

# Reemplazar BUTTON_COLORS con colores válidos
BUTTON_COLORS = {
    'default': None,
    'green': '#228B22',        # Forest Green
    'darkgreen': '#006400',    # Dark Green
    'blue': '#4682B4',         # Steel Blue  
    'darkblue': '#191970',     # Midnight Blue
    'purple': '#9370DB',       # Medium Purple
    'darkpurple': '#6A0DAD',   # Valid dark purple
    'orange': '#FF8C00',       # Dark Orange
    'darkorange': '#FF6347',   # Tomato
    'red': '#DC143C',          # Crimson
    'darkred': '#8B0000',      # Dark Red
    'indigo': '#4B0082',       # Indigo
    'darkindigo': '#310062'    # Dark Indigo
}