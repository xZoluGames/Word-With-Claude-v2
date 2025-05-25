"""
Constantes centralizadas del proyecto
"""

# Secciones que permiten citas
CITATION_ALLOWED_SECTIONS = [
    'marco_teorico', 
    'introduccion', 
    'desarrollo', 
    'discusion',
    'resultados',
    'metodologia'
]

# Secciones sin sangría
NO_INDENT_SECTIONS = [
    "RESUMEN", 
    "PALABRAS CLAVE", 
    "AGRADECIMIENTOS",
    "ÍNDICE", 
    "TABLA DE ILUSTRACIONES", 
    "REFERENCIAS",
    "ABSTRACT"
]

# Tipos de referencias soportados
REFERENCE_TYPES = [
    "Libro", 
    "Artículo", 
    "Web", 
    "Tesis", 
    "Conferencia", 
    "Informe",
    "Capítulo",
    "Video",
    "Podcast"
]

# Verbos para objetivos
OBJECTIVE_VERBS = [
    'analizar', 'identificar', 'determinar', 'evaluar', 'comparar',
    'describir', 'explicar', 'investigar', 'desarrollar', 'proponer',
    'diseñar', 'implementar', 'validar', 'demostrar', 'establecer',
    'examinar', 'explorar', 'formular', 'generar', 'interpretar',
    'medir', 'observar', 'plantear', 'resolver', 'sintetizar'
]

# Límites de texto por sección
SECTION_LIMITS = {
    'resumen': {'min': 150, 'max': 300},
    'introduccion': {'min': 200, 'max': None},
    'objetivos': {'min': 50, 'max': 500},
    'marco_teorico': {'min': 500, 'max': None},
    'metodologia': {'min': 300, 'max': None},
    'conclusiones': {'min': 150, 'max': None},
    'titulo': {'min': 10, 'max': 200},
    'pregunta_investigacion': {'min': 20, 'max': 150}
}

# Formatos de fecha soportados
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%B %d, %Y",
    "%d de %B de %Y"
]

# Extensiones de imagen soportadas
SUPPORTED_IMAGE_FORMATS = [
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'
]

# Tamaños máximos (en bytes)
MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,  # 10MB
    'document': 50 * 1024 * 1024,  # 50MB
    'export': 100 * 1024 * 1024  # 100MB
}

# Timeouts (en segundos)
TIMEOUTS = {
    'autosave': 300,  # 5 minutos
    'validation': 30,  # 30 segundos
    'generation': 300,  # 5 minutos
    'cache_ttl': 86400  # 24 horas
}

# Mensajes de error comunes
ERROR_MESSAGES = {
    'file_not_found': "El archivo especificado no existe: {file}",
    'invalid_format': "Formato inválido. Se esperaba: {expected}",
    'required_field': "El campo '{field}' es obligatorio",
    'connection_error': "Error de conexión. Verifica tu conexión a internet.",
    'permission_denied': "Sin permisos para acceder a: {resource}",
    'generic_error': "Ocurrió un error inesperado. Consulta el log para más detalles."
}

# Plantillas de mensajes
MESSAGE_TEMPLATES = {
    'save_success': "✅ {item} guardado correctamente",
    'delete_confirm': "¿Estás seguro de eliminar {item}?",
    'validation_passed': "✅ Validación completada sin errores",
    'generation_complete': "📄 Documento generado exitosamente"
}