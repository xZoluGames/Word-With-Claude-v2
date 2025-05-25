"""
Sistema de validación mejorado con cache y soporte Unicode completo
"""

import re
import unicodedata
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any
from functools import lru_cache
from utils.logger import get_logger

logger = get_logger('Validators')


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


class Validators:
    """Clase con métodos estáticos de validación optimizados."""
    
    # Patrones regex compilados y optimizados
    AUTOR_SIMPLE = re.compile(
        r'^[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+(?:\s[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+)*,\s[A-ZА-Я\u4e00-\u9fff]\.(?:\s[A-ZА-Я\u4e00-\u9fff]\.)*$',
        re.UNICODE
    )
    
    AUTOR_MULTIPLE = re.compile(
        r'^[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+(?:\s[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+)*,\s[A-ZА-Я\u4e00-\u9fff]\.(?:\s[A-ZА-Я\u4e00-\u9fff]\.)?\s[yand&]\s[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+(?:\s[A-ZÁ-ŽА-Яа-я\u4e00-\u9fff][a-záñüа-я\u4e00-\u9fff]+)*,\s[A-ZА-Я\u4e00-\u9fff]\.(?:\s[A-ZА-Я\u4e00-\u9fff]\.)*$',
        re.UNICODE
    )
    
    EMAIL = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        re.IGNORECASE
    )
    
    URL = re.compile(
        r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$',
        re.IGNORECASE
    )
    
    YEAR = re.compile(r'^(19|20)\d{2}$')
    
    # Cache para validaciones frecuentes
    _validation_cache: Dict[Tuple[str, str], Tuple[bool, Optional[str]]] = {}
    
    @staticmethod
    @lru_cache(maxsize=256)
    def validar_autor(autor: str) -> Tuple[bool, Optional[str]]:
        """
        Valida el formato de autor según APA con soporte Unicode mejorado.
        
        Args:
            autor: String con el nombre del autor
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not autor or not autor.strip():
            return False, "El autor no puede estar vacío"
        
        autor = autor.strip()
        
        # Normalizar Unicode
        autor_normalizado = unicodedata.normalize('NFC', autor)
        
        # Casos especiales primero
        if autor_normalizado.endswith(" et al."):
            return True, None
        
        # Organizaciones (todo en mayúsculas o con siglas)
        if autor_normalizado.isupper() or re.match(r'^[A-Z]{2,}(?:\s[A-Z]{2,})*$', autor_normalizado):
            return True, None
        
        # Validar formato estándar
        if Validators.AUTOR_SIMPLE.match(autor_normalizado) or Validators.AUTOR_MULTIPLE.match(autor_normalizado):
            return True, None
        
        # Verificar si es un formato cercano al correcto
        sugerencia = Validators._sugerir_formato_autor(autor_normalizado)
        
        return False, f"Formato incorrecto. {sugerencia}"
    
    @staticmethod
    def _sugerir_formato_autor(autor: str) -> str:
        """Sugiere el formato correcto basado en el input"""
        # Detectar si tiene coma
        if ',' not in autor:
            partes = autor.split()
            if len(partes) >= 2:
                return f"¿Quizás quisiste escribir: '{partes[-1]}, {partes[0][0]}.'?"
        
        # Detectar si falta punto después de inicial
        if ',' in autor and not re.search(r'\.\s*$', autor):
            return "Recuerda agregar punto después de las iniciales"
        
        return "Use: 'Apellido, N.' o 'Apellido, N. y Apellido2, M.'"
    
    @staticmethod
    @lru_cache(maxsize=128)
    def validar_año(año: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un año de publicación con cache.
        
        Args:
            año: String con el año
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not año or not año.strip():
            return False, "El año no puede estar vacío"
        
        año = año.strip()
        
        # Verificar formato
        if not Validators.YEAR.match(año):
            # Verificar si es "en prensa" o similar
            if año.lower() in ['en prensa', 'in press', 's.f.', 'n.d.']:
                return True, None
            return False, "El año debe tener 4 dígitos (ej: 2023) o ser 'en prensa'"
        
        # Verificar rango
        año_num = int(año)
        año_actual = datetime.now().year
        
        if año_num < 1900:
            return False, "El año no puede ser anterior a 1900"
        
        if año_num > año_actual + 1:
            return False, f"El año no puede ser posterior a {año_actual + 1}"
        
        return True, None
    
    @staticmethod
    def validar_titulo(titulo: str, max_length: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Valida un título con verificación de caracteres Unicode.
        
        Args:
            titulo: String con el título
            max_length: Longitud máxima permitida
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not titulo or not titulo.strip():
            return False, "El título no puede estar vacío"
        
        titulo = titulo.strip()
        
        # Normalizar Unicode
        titulo_normalizado = unicodedata.normalize('NFC', titulo)
        
        if len(titulo_normalizado) < 3:
            return False, "El título debe tener al menos 3 caracteres"
        
        if len(titulo_normalizado) > max_length:
            return False, f"El título no puede exceder {max_length} caracteres (actual: {len(titulo_normalizado)})"
        
        # Verificar caracteres problemáticos
        caracteres_prohibidos = set('<>{}\\|')
        caracteres_encontrados = set(titulo_normalizado) & caracteres_prohibidos
        
        if caracteres_encontrados:
            return False, f"El título contiene caracteres no permitidos: {', '.join(caracteres_encontrados)}"
        
        # Verificar que no sea solo números o símbolos
        if not any(c.isalpha() for c in titulo_normalizado):
            return False, "El título debe contener al menos una letra"
        
        return True, None
    
    @staticmethod
    @lru_cache(maxsize=128)
    def validar_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Valida una URL con verificaciones adicionales.
        
        Args:
            url: String con la URL
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not url or not url.strip():
            return False, "La URL no puede estar vacía"
        
        url = url.strip()
        
        # Verificar formato básico
        if not Validators.URL.match(url):
            # Verificar si le falta el protocolo
            if not url.startswith(('http://', 'https://')):
                return False, "La URL debe comenzar con http:// o https://"
            return False, "URL inválida. Verifica el formato completo"
        
        # Verificar longitud razonable
        if len(url) > 2048:
            return False, "La URL es demasiado larga (máximo 2048 caracteres)"
        
        # Verificar dominios sospechosos (opcional)
        dominios_sospechosos = ['bit.ly', 'tinyurl.com', 'goo.gl']
        for dominio in dominios_sospechosos:
            if dominio in url.lower():
                logger.warning(f"URL acortada detectada: {url}")
        
        return True, None
    
    @staticmethod
    def validar_contenido_seccion(contenido: str, seccion_tipo: str) -> Tuple[bool, Optional[str]]:
        """
        Valida el contenido de una sección con reglas mejoradas.
        
        Args:
            contenido: Texto de la sección
            seccion_tipo: Tipo de sección
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not contenido or not contenido.strip():
            return False, "La sección no puede estar vacía"
        
        contenido_limpio = contenido.strip()
        palabras = len(contenido_limpio.split())
        caracteres = len(contenido_limpio)
        
        # Validaciones específicas por tipo
        validaciones = {
            'resumen': {
                'min_palabras': 150,
                'max_palabras': 300,
                'mensaje': "El resumen debe tener entre 150 y 300 palabras"
            },
            'introduccion': {
                'min_palabras': 200,
                'max_palabras': None,
                'mensaje': "La introducción debe tener al menos 200 palabras"
            },
            'objetivos': {
                'min_palabras': 50,
                'max_palabras': None,
                'validacion_extra': lambda c: Validators._validar_objetivos(c),
                'mensaje': "Los objetivos deben usar verbos en infinitivo"
            },
            'marco_teorico': {
                'min_palabras': 500,
                'max_palabras': None,
                'validacion_extra': lambda c: Validators._validar_citas(c),
                'mensaje': "El marco teórico debe tener al menos 500 palabras y contener citas"
            },
            'conclusiones': {
                'min_palabras': 150,
                'max_palabras': None,
                'mensaje': "Las conclusiones deben tener al menos 150 palabras"
            }
        }
        
        if seccion_tipo in validaciones:
            config = validaciones[seccion_tipo]
            
            # Validar mínimo de palabras
            if config['min_palabras'] and palabras < config['min_palabras']:
                return False, f"{config['mensaje']} (actual: {palabras} palabras)"
            
            # Validar máximo de palabras
            if config['max_palabras'] and palabras > config['max_palabras']:
                return False, f"{config['mensaje']} (actual: {palabras} palabras)"
            
            # Validación extra si existe
            if 'validacion_extra' in config:
                es_valido, mensaje = config['validacion_extra'](contenido_limpio)
                if not es_valido:
                    return False, mensaje
        
        return True, None
    
    @staticmethod
    def _validar_objetivos(contenido: str) -> Tuple[bool, Optional[str]]:
        """Valida que los objetivos usen verbos en infinitivo"""
        verbos_infinitivo = [
            'analizar', 'identificar', 'determinar', 'evaluar', 'comparar',
            'describir', 'explicar', 'investigar', 'desarrollar', 'proponer',
            'diseñar', 'implementar', 'validar', 'demostrar', 'establecer'
        ]
        
        contenido_lower = contenido.lower()
        tiene_infinitivos = any(verbo in contenido_lower for verbo in verbos_infinitivo)
        
        if not tiene_infinitivos:
            verbos_sugeridos = ', '.join(verbos_infinitivo[:5])
            return False, f"Los objetivos deben usar verbos en infinitivo como: {verbos_sugeridos}"
        
        return True, None
    
    @staticmethod
    def _validar_citas(contenido: str) -> Tuple[bool, Optional[str]]:
        """Valida que el contenido tenga citas"""
        # Buscar patrones de citas
        patron_cita = r'\([A-ZÁ-Ž][a-záñü]+(?:\s+(?:y|&)\s+[A-ZÁ-Ž][a-záñü]+)*,\s*\d{4}\)'
        patron_cita_tag = r'\[CITA:[^\]]+\]'
        
        tiene_citas = bool(re.search(patron_cita, contenido) or re.search(patron_cita_tag, contenido))
        
        if not tiene_citas:
            return False, "El marco teórico debe incluir citas bibliográficas"
        
        return True, None
    
    @staticmethod
    def sanitizar_entrada(texto: str, permitir_saltos: bool = True, 
                         max_length: int = None) -> str:
        """
        Sanitiza una entrada de texto con validaciones mejoradas.
        
        Args:
            texto: Texto a sanitizar
            permitir_saltos: Si se permiten saltos de línea
            max_length: Longitud máxima permitida
            
        Returns:
            str: Texto sanitizado
        """
        if not texto:
            return ""
        
        # Normalizar Unicode
        texto = unicodedata.normalize('NFC', texto)
        
        # Eliminar caracteres de control
        if permitir_saltos:
            # Preservar saltos de línea y tabulaciones
            texto = ''.join(
                char for char in texto 
                if char in '\n\r\t' or not unicodedata.category(char).startswith('C')
            )
        else:
            # Eliminar todos los caracteres de control
            texto = ''.join(
                char for char in texto 
                if not unicodedata.category(char).startswith('C')
            )
        
        # Normalizar espacios
        texto = re.sub(r'[ \t]+', ' ', texto)  # Espacios múltiples
        texto = re.sub(r'\n\s*\n\s*\n', '\n\n', texto)  # Máximo 2 saltos de línea
        
        # Eliminar espacios al inicio/final de líneas
        if permitir_saltos:
            lineas = texto.split('\n')
            texto = '\n'.join(linea.strip() for linea in lineas)
        
        # Limitar longitud si se especifica
        if max_length and len(texto) > max_length:
            texto = texto[:max_length].rsplit(' ', 1)[0] + '...'
        
        return texto.strip()


class ReferenceValidator:
    """Validador especializado para referencias bibliográficas con mejoras."""
    
    @staticmethod
    def validar_referencia_completa(ref_data: dict) -> List[str]:
        """
        Valida una referencia completa con verificaciones adicionales.
        
        Args:
            ref_data: Diccionario con datos de la referencia
            
        Returns:
            List[str]: Lista de mensajes de error (vacía si es válida)
        """
        errores = []
        tipo = ref_data.get('tipo', 'Libro')
        
        # Validaciones básicas
        campos_requeridos = {
            'Libro': ['autor', 'año', 'titulo', 'fuente'],
            'Artículo': ['autor', 'año', 'titulo', 'fuente'],
            'Web': ['autor', 'año', 'titulo', 'fuente'],
            'Tesis': ['autor', 'año', 'titulo', 'fuente'],
            'Conferencia': ['autor', 'año', 'titulo', 'fuente'],
            'Informe': ['autor', 'año', 'titulo', 'fuente']
        }
        
        # Verificar campos requeridos según tipo
        for campo in campos_requeridos.get(tipo, ['autor', 'año', 'titulo']):
            if not ref_data.get(campo, '').strip():
                errores.append(f"Campo requerido vacío: {campo}")
        
        # Validar autor
        if ref_data.get('autor'):
            es_valido, error = Validators.validar_autor(ref_data['autor'])
            if not es_valido:
                errores.append(f"Autor: {error}")
        
        # Validar año
        if ref_data.get('año'):
            es_valido, error = Validators.validar_año(ref_data['año'])
            if not es_valido:
                errores.append(f"Año: {error}")
        
        # Validar título
        if ref_data.get('titulo'):
            es_valido, error = Validators.validar_titulo(ref_data['titulo'], max_length=500)
            if not es_valido:
                errores.append(f"Título: {error}")
        
        # Validaciones específicas por tipo
        if tipo == 'Web' and ref_data.get('fuente'):
            if not ref_data['fuente'].startswith(('http://', 'https://', 'www.')):
                errores.append("Para referencias web, incluye la URL completa")
        
        elif tipo == 'Artículo' and ref_data.get('fuente'):
            # Verificar formato de revista
            if not any(char in ref_data['fuente'] for char in [',', '(', ')']):
                errores.append("Para artículos, incluye: Revista, volumen(número), páginas")
        
        return errores


# Funciones de conveniencia mejoradas
def validar_y_sanitizar_entrada(texto: str, tipo: str = 'general', 
                               max_length: int = None) -> Tuple[str, List[str]]:
    """
    Valida y sanitiza una entrada según su tipo con límites opcionales.
    
    Args:
        texto: Texto a validar y sanitizar
        tipo: Tipo de validación ('autor', 'titulo', 'url', 'general')
        max_length: Longitud máxima permitida
        
    Returns:
        Tuple[str, List[str]]: (texto_sanitizado, lista_de_errores)
    """
    # Sanitizar primero
    permitir_saltos = tipo not in ['autor', 'url']
    texto_sanitizado = Validators.sanitizar_entrada(texto, permitir_saltos, max_length)
    
    errores = []
    
    # Validar según tipo
    validadores = {
        'autor': Validators.validar_autor,
        'titulo': lambda t: Validators.validar_titulo(t, max_length or 300),
        'url': Validators.validar_url
    }
    
    if tipo in validadores:
        es_valido, error = validadores[tipo](texto_sanitizado)
        if not es_valido:
            errores.append(error)
    
    return texto_sanitizado, errores


# Cache para limpiar periódicamente
def limpiar_cache_validacion():
    """Limpia el cache de validación"""
    Validators._validation_cache.clear()
    Validators.validar_autor.cache_clear()
    Validators.validar_año.cache_clear()
    Validators.validar_url.cache_clear()
    logger.info("Cache de validación limpiado")