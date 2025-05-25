"""
Sistema de cache para operaciones costosas

Proporciona cache en memoria y disco para operaciones como
procesamiento de imágenes, cálculos complejos, etc.
"""

import os
import json
import pickle
import hashlib
import time
from functools import wraps, lru_cache
from typing import Any, Optional, Callable, Dict
from pathlib import Path
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger('CacheSystem')


class CacheManager:
    """
    Gestor de cache con soporte para memoria y disco.
    
    Attributes:
        cache_dir (Path): Directorio para cache en disco
        memory_cache (Dict): Cache en memoria
        max_memory_items (int): Máximo de items en memoria
        default_ttl (int): Tiempo de vida por defecto en segundos
    """
    
    def __init__(self, cache_dir: str = "cache", max_memory_items: int = 100, default_ttl: int = 3600):
        """
        Inicializa el gestor de cache.
        
        Args:
            cache_dir: Directorio para almacenar cache en disco
            max_memory_items: Número máximo de items en memoria
            default_ttl: Tiempo de vida por defecto (segundos)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.max_memory_items = max_memory_items
        self.default_ttl = default_ttl
        
        # Limpiar cache antiguo al iniciar
        self._cleanup_old_cache()
        
        logger.info(f"CacheManager inicializado - Dir: {self.cache_dir}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Genera una clave única basada en los argumentos.
        
        Returns:
            str: Hash MD5 de los argumentos
        """
        # Crear string representativo de los argumentos
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        
        # Generar hash MD5
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Verifica si un item del cache ha expirado."""
        return time.time() - timestamp > ttl
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave del item
            default: Valor por defecto si no existe o expiró
            
        Returns:
            El valor del cache o el valor por defecto
        """
        # Buscar en memoria primero
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if not self._is_expired(item['timestamp'], item['ttl']):
                logger.debug(f"Cache hit (memoria): {key[:8]}...")
                return item['value']
            else:
                # Expirado, eliminar
                del self.memory_cache[key]
        
        # Buscar en disco
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    item = pickle.load(f)
                
                if not self._is_expired(item['timestamp'], item['ttl']):
                    # Cargar a memoria si hay espacio
                    if len(self.memory_cache) < self.max_memory_items:
                        self.memory_cache[key] = item
                    
                    logger.debug(f"Cache hit (disco): {key[:8]}...")
                    return item['value']
                else:
                    # Expirado, eliminar
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"Error leyendo cache: {e}")
        
        logger.debug(f"Cache miss: {key[:8]}...")
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, disk: bool = True):
        """
        Guarda un valor en el cache.
        
        Args:
            key: Clave del item
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (None = usar default)
            disk: Si también guardar en disco
        """
        if ttl is None:
            ttl = self.default_ttl
        
        item = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        # Guardar en memoria
        if len(self.memory_cache) >= self.max_memory_items:
            # Eliminar el más antiguo
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]['timestamp'])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = item
        
        # Guardar en disco si se requiere
        if disk:
            cache_file = self.cache_dir / f"{key}.cache"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(item, f)
                logger.debug(f"Cache guardado: {key[:8]}...")
            except Exception as e:
                logger.error(f"Error guardando cache: {e}")
    
    def invalidate(self, key: str):
        """Invalida un item específico del cache."""
        # Eliminar de memoria
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Eliminar de disco
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            cache_file.unlink()
        
        logger.debug(f"Cache invalidado: {key[:8]}...")
    
    def clear(self):
        """Limpia todo el cache."""
        # Limpiar memoria
        self.memory_cache.clear()
        
        # Limpiar disco
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        logger.info("Cache completamente limpiado")
    
    def _cleanup_old_cache(self):
        """Elimina archivos de cache antiguos del disco."""
        cleaned = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                # Verificar si el archivo es muy antiguo (más de 7 días)
                if cache_file.stat().st_mtime < time.time() - (7 * 24 * 3600):
                    cache_file.unlink()
                    cleaned += 1
            except Exception as e:
                logger.error(f"Error limpiando cache antiguo: {e}")
        
        if cleaned > 0:
            logger.info(f"Eliminados {cleaned} archivos de cache antiguos")


# Instancia global del cache
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, key_prefix: str = "", use_disk: bool = True):
    """
    Decorador para cachear el resultado de una función.
    
    Args:
        ttl: Tiempo de vida en segundos
        key_prefix: Prefijo para la clave del cache
        use_disk: Si usar cache en disco además de memoria
    
    Example:
        @cached(ttl=3600, key_prefix="image_process")
        def process_image(path):
            # Operación costosa
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_manager._generate_key(*args, **kwargs)
            if key_prefix:
                cache_key = f"{key_prefix}_{cache_key}"
            
            # Buscar en cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            cache_manager.set(cache_key, result, ttl=ttl, disk=use_disk)
            
            return result
        
        # Agregar método para invalidar cache
        def invalidate_cache(*args, **kwargs):
            cache_key = cache_manager._generate_key(*args, **kwargs)
            if key_prefix:
                cache_key = f"{key_prefix}_{cache_key}"
            cache_manager.invalidate(cache_key)
        
        wrapper.invalidate_cache = invalidate_cache
        return wrapper
    
    return decorator


class ImageCache:
    """Cache especializado para imágenes procesadas."""
    
    def __init__(self):
        self.cache_dir = Path("cache/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @cached(ttl=86400, key_prefix="image", use_disk=True)  # 24 horas
    def get_processed_image(self, image_path: str, width: int, height: int, 
                          opacity: float = 1.0) -> Optional[bytes]:
        """
        Obtiene una imagen procesada del cache o la procesa.
        
        Args:
            image_path: Ruta de la imagen original
            width: Ancho deseado
            height: Alto deseado
            opacity: Opacidad (0.0 - 1.0)
            
        Returns:
            bytes: Imagen procesada o None si hay error
        """
        from PIL import Image, ImageEnhance
        import io
        
        try:
            # Abrir imagen
            img = Image.open(image_path)
            
            # Redimensionar
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Aplicar opacidad si es necesario
            if opacity < 1.0:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Aplicar transparencia
                alpha = img.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                img.putalpha(alpha)
            
            # Convertir a bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return None
    
    def clear_image_cache(self):
        """Limpia el cache de imágenes."""
        for file in self.cache_dir.glob("*"):
            file.unlink()
        logger.info("Cache de imágenes limpiado")


# Instancia global del cache de imágenes
image_cache = ImageCache()


# Cache LRU para operaciones frecuentes
@lru_cache(maxsize=128)
def get_cached_word_count(text: str) -> int:
    """
    Cuenta palabras con cache LRU.
    
    Args:
        text: Texto a contar
        
    Returns:
        int: Número de palabras
    """
    return len(text.split())


@lru_cache(maxsize=64)
def get_cached_char_count(text: str) -> int:
    """
    Cuenta caracteres con cache LRU.
    
    Args:
        text: Texto a contar
        
    Returns:
        int: Número de caracteres
    """
    return len(text)