"""
Sistema de validación para datos del proyecto académico

Este módulo proporciona validadores reutilizables para diferentes
tipos de datos utilizados en la aplicación.
"""

import re
from datetime import datetime
from typing import Tuple, Optional, List
from utils.logger import get_logger

logger = get_logger('Validators')


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


class Validators:
    """Clase con métodos estáticos de validación."""
    
    # Patrones regex compilados para mejor rendimiento
    AUTOR_SIMPLE = re.compile(r'^[A-ZÁ-Žа-я][a-záñüа-я]+(?:\s[A-ZÁ-Žа-я][a-záñüа-я]+)*,\s[A-ZА-Я]\.(?:\s[A-ZА-Я]\.)*$')
    AUTOR_MULTIPLE = re.compile(r'^[A-ZÁ-Žа-я][a-záñüа-я]+(?:\s[A-ZÁ-Žа-я][a-záñüа-я]+)*,\s[A-ZА-Я]\.(?:\s[A-ZА-Я]\.)?\s[yand&]\s[A-ZÁ-Žа-я][a-záñüа-я]+(?:\s[A-ZÁ-Žа-я][a-záñüа-я]+)*,\s[A-ZА-Я]\.(?:\s[A-ZА-Я]\.)*$')
    EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL = re.compile(r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$')
    YEAR = re.compile(r'^(19|20)\d{2}$')
    
    @staticmethod
    def validar_autor(autor: str) -> Tuple[bool, Optional[str]]:
        """
        Valida el formato de autor según APA.
        
        Args:
            autor: String con el nombre del autor
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
            
        Examples:
            >>> Validators.validar_autor("García, J.")
            (True, None)
            >>> Validators.validar_autor("García López, J. M.")
            (True, None)
            >>> Validators.validar_autor("García, J. y López, M.")
            (True, None)
            >>> Validators.validar_autor("Juan García")
            (False, "Formato incorrecto. Use: 'Apellido, N.' o 'Apellido, N. y Apellido2, M.'")
        """
        if not autor or not autor.strip():
            return False, "El autor no puede estar vacío"
        
        autor = autor.strip()
        
        # Verificar formatos válidos
        if Validators.AUTOR_SIMPLE.match(autor) or Validators.AUTOR_MULTIPLE.match(autor):
            return True, None
        
        # Casos especiales: et al., organizaciones
        if autor.endswith(" et al.") or autor.isupper():
            return True, None
        
        return False, "Formato incorrecto. Use: 'Apellido, N.' o 'Apellido, N. y Apellido2, M.'"
    
    @staticmethod
    def validar_año(año: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un año de publicación.
        
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
            return False, "El año debe tener 4 dígitos (ej: 2023)"
        
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
        Valida un título de obra.
        
        Args:
            titulo: String con el título
            max_length: Longitud máxima permitida
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not titulo or not titulo.strip():
            return False, "El título no puede estar vacío"
        
        titulo = titulo.strip()
        
        if len(titulo) < 3:
            return False, "El título debe tener al menos 3 caracteres"
        
        if len(titulo) > max_length:
            return False, f"El título no puede exceder {max_length} caracteres"
        
        # Verificar caracteres extraños
        if re.search(r'[<>{}\\]', titulo):
            return False, "El título contiene caracteres no permitidos"
        
        return True, None
    
    @staticmethod
    def validar_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Valida una URL.
        
        Args:
            url: String con la URL
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not url or not url.strip():
            return False, "La URL no puede estar vacía"
        
        url = url.strip()
        
        if not Validators.URL.match(url):
            return False, "URL inválida. Debe comenzar con http:// o https://"
        
        return True, None
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida una dirección de email.
        
        Args:
            email: String con el email
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not email or not email.strip():
            return False, "El email no puede estar vacío"
        
        email = email.strip().lower()
        
        if not Validators.EMAIL.match(email):
            return False, "Email inválido. Use el formato: usuario@dominio.com"
        
        return True, None
    
    @staticmethod
    def validar_paginas(paginas: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un rango de páginas.
        
        Args:
            paginas: String con las páginas (ej: "45-67" o "123")
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not paginas or not paginas.strip():
            return True, None  # Las páginas son opcionales
        
        paginas = paginas.strip()
        
        # Página única
        if paginas.isdigit():
            return True, None
        
        # Rango de páginas
        if re.match(r'^\d+\s*-\s*\d+$', paginas):
            partes = re.split(r'\s*-\s*', paginas)
            inicio = int(partes[0])
            fin = int(partes[1])
            
            if inicio >= fin:
                return False, "El rango de páginas es inválido (inicio >= fin)"
            
            return True, None
        
        return False, "Formato de páginas inválido. Use: '45' o '45-67'"
    
    @staticmethod
    def validar_contenido_seccion(contenido: str, seccion_tipo: str) -> Tuple[bool, Optional[str]]:
        """
        Valida el contenido de una sección según su tipo.
        
        Args:
            contenido: Texto de la sección
            seccion_tipo: Tipo de sección (resumen, introduccion, etc.)
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not contenido or not contenido.strip():
            return False, "La sección no puede estar vacía"
        
        palabras = len(contenido.split())
        
        # Validaciones específicas por tipo
        if seccion_tipo == 'resumen':
            if palabras < 150:
                return False, "El resumen debe tener al menos 150 palabras"
            if palabras > 300:
                return False, "El resumen no debe exceder 300 palabras"
        
        elif seccion_tipo == 'introduccion':
            if palabras < 200:
                return False, "La introducción debe tener al menos 200 palabras"
        
        elif seccion_tipo == 'objetivos':
            # Verificar que contenga verbos en infinitivo
            verbos_infinitivo = ['ar', 'er', 'ir']
            tiene_infinitivos = any(
                palabra.endswith(terminacion) 
                for palabra in contenido.split() 
                for terminacion in verbos_infinitivo
                if len(palabra) > 3
            )
            if not tiene_infinitivos:
                return False, "Los objetivos deben usar verbos en infinitivo (terminados en -ar, -er, -ir)"
        
        return True, None
    
    @staticmethod
    def sanitizar_entrada(texto: str, permitir_saltos: bool = True) -> str:
        """
        Sanitiza una entrada de texto eliminando caracteres peligrosos.
        
        Args:
            texto: Texto a sanitizar
            permitir_saltos: Si se permiten saltos de línea
            
        Returns:
            str: Texto sanitizado
        """
        if not texto:
            return ""
        
        # Eliminar caracteres de control excepto saltos de línea si están permitidos
        if permitir_saltos:
            texto = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', texto)
        else:
            texto = re.sub(r'[\x00-\x1f\x7f]', '', texto)
        
        # Eliminar caracteres que podrían ser problemáticos en XML/Word
        texto = texto.replace('\x00', '')
        
        # Normalizar espacios múltiples
        texto = re.sub(r' +', ' ', texto)
        
        return texto.strip()


class ReferenceValidator:
    """Validador especializado para referencias bibliográficas."""
    
    @staticmethod
    def validar_referencia_completa(ref_data: dict) -> List[str]:
        """
        Valida una referencia completa y retorna lista de errores.
        
        Args:
            ref_data: Diccionario con datos de la referencia
            
        Returns:
            List[str]: Lista de mensajes de error (vacía si todo es válido)
        """
        errores = []
        
        # Validar autor
        es_valido, error = Validators.validar_autor(ref_data.get('autor', ''))
        if not es_valido:
            errores.append(f"Autor: {error}")
        
        # Validar año
        es_valido, error = Validators.validar_año(ref_data.get('año', ''))
        if not es_valido:
            errores.append(f"Año: {error}")
        
        # Validar título
        es_valido, error = Validators.validar_titulo(ref_data.get('titulo', ''))
        if not es_valido:
            errores.append(f"Título: {error}")
        
        # Validar URL si es referencia web
        if ref_data.get('tipo') == 'Web':
            es_valido, error = Validators.validar_url(ref_data.get('fuente', ''))
            if not es_valido:
                errores.append(f"URL: {error}")
        
        return errores


# Funciones de conveniencia
def validar_y_sanitizar_entrada(texto: str, tipo: str = 'general') -> Tuple[str, List[str]]:
    """
    Valida y sanitiza una entrada según su tipo.
    
    Args:
        texto: Texto a validar y sanitizar
        tipo: Tipo de validación ('autor', 'titulo', 'url', 'general')
        
    Returns:
        Tuple[str, List[str]]: (texto_sanitizado, lista_de_errores)
    """
    texto_sanitizado = Validators.sanitizar_entrada(texto)
    errores = []
    
    if tipo == 'autor':
        es_valido, error = Validators.validar_autor(texto_sanitizado)
        if not es_valido:
            errores.append(error)
    elif tipo == 'titulo':
        es_valido, error = Validators.validar_titulo(texto_sanitizado)
        if not es_valido:
            errores.append(error)
    elif tipo == 'url':
        es_valido, error = Validators.validar_url(texto_sanitizado)
        if not es_valido:
            errores.append(error)
    
    return texto_sanitizado, errores