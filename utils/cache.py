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
import hashlib
import pickle
import json
from collections import OrderedDict
from threading import Lock
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
    
    def __init__(self, cache_dir: str = "cache", max_memory_items: int = 100, 
                 default_ttl: int = 3600, max_disk_size_mb: int = 100):
        """
        Inicializa el gestor de cache con límites mejorados.
        
        Args:
            cache_dir: Directorio para almacenar cache en disco
            max_memory_items: Número máximo de items en memoria
            default_ttl: Tiempo de vida por defecto (segundos)
            max_disk_size_mb: Tamaño máximo del cache en disco (MB)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = OrderedDict()
        self.max_memory_items = max_memory_items
        self.default_ttl = default_ttl
        self.max_disk_size = max_disk_size_mb * 1024 * 1024  # Convertir a bytes
        
        # Thread safety
        self._lock = Lock()
        
        # Estadísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'evictions': 0
        }
        
        # Archivo de metadatos
        self.metadata_file = self.cache_dir / '.cache_metadata.json'
        self._load_metadata()
        
        # Limpiar cache antiguo al iniciar
        self._cleanup_old_cache()
        
        logger.info(f"CacheManager inicializado - Dir: {self.cache_dir}, "
                   f"Max memoria: {max_memory_items}, Max disco: {max_disk_size_mb}MB")


    def _load_metadata(self):
        """Carga metadatos del cache"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    'version': '1.0',
                    'created': time.time(),
                    'files': {}
                }
        except Exception as e:
            logger.error(f"Error cargando metadatos: {e}")
            self.metadata = {'version': '1.0', 'created': time.time(), 'files': {}}
    
    def _save_metadata(self):
        """Guarda metadatos del cache"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error guardando metadatos: {e}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Genera una clave única basada en los argumentos con hash seguro.
        """
        # Crear representación estable
        key_data = {
            'args': [self._make_hashable(arg) for arg in args],
            'kwargs': {k: self._make_hashable(v) for k, v in sorted(kwargs.items())}
        }
        
        # Usar SHA256 para mejor distribución
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Verifica si un item del cache ha expirado."""
        return time.time() - timestamp > ttl
    def _make_hashable(self, obj):
        """Convierte objetos a formato hashable"""
        if isinstance(obj, (list, tuple)):
            return tuple(self._make_hashable(item) for item in obj)
        elif isinstance(obj, dict):
            return tuple(sorted((k, self._make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, set):
            return tuple(sorted(self._make_hashable(item) for item in obj))
        else:
            return obj
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Obtiene un valor del cache con estadísticas.
        """
        with self._lock:
            # Buscar en memoria primero
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if not self._is_expired(item['timestamp'], item['ttl']):
                    # Mover al final (LRU)
                    self.memory_cache.move_to_end(key)
                    self.stats['hits'] += 1
                    self.stats['memory_hits'] += 1
                    logger.debug(f"Cache hit (memoria): {key[:8]}...")
                    return item['value']
                else:
                    # Expirado, eliminar
                    del self.memory_cache[key]
            
            # Buscar en disco
            cache_file = self.cache_dir / f"{key}.cache"
            if cache_file.exists():
                try:
                    # Verificar integridad
                    if key in self.metadata.get('files', {}):
                        expected_size = self.metadata['files'][key].get('size', 0)
                        actual_size = cache_file.stat().st_size
                        
                        if expected_size != actual_size:
                            logger.warning(f"Cache corrupto detectado: {key}")
                            cache_file.unlink()
                            self.stats['misses'] += 1
                            return default
                    
                    with open(cache_file, 'rb') as f:
                        item = pickle.load(f)
                    
                    if not self._is_expired(item['timestamp'], item['ttl']):
                        # Cargar a memoria si hay espacio
                        if len(self.memory_cache) < self.max_memory_items:
                            self.memory_cache[key] = item
                        
                        self.stats['hits'] += 1
                        self.stats['disk_hits'] += 1
                        logger.debug(f"Cache hit (disco): {key[:8]}...")
                        return item['value']
                    else:
                        # Expirado, eliminar
                        cache_file.unlink()
                        if key in self.metadata.get('files', {}):
                            del self.metadata['files'][key]
                        
                except Exception as e:
                    logger.error(f"Error leyendo cache: {e}")
                    # Eliminar archivo corrupto
                    try:
                        cache_file.unlink()
                    except:
                        pass
            
            self.stats['misses'] += 1
            logger.debug(f"Cache miss: {key[:8]}...")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            disk: bool = True, priority: int = 0):
        """
        Guarda un valor con prioridad y límites de tamaño.
        """
        if ttl is None:
            ttl = self.default_ttl
        
        item = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl,
            'priority': priority
        }
        
        with self._lock:
            # Guardar en memoria
            if len(self.memory_cache) >= self.max_memory_items:
                # Eliminar item con menor prioridad o más antiguo
                self._evict_from_memory()
            
            self.memory_cache[key] = item
            self.memory_cache.move_to_end(key)  # Mover al final (más reciente)
            
            # Guardar en disco si se requiere
            if disk:
                try:
                    # Verificar espacio en disco
                    if self._get_cache_size() > self.max_disk_size:
                        self._cleanup_disk_cache()
                    
                    cache_file = self.cache_dir / f"{key}.cache"
                    with open(cache_file, 'wb') as f:
                        pickle.dump(item, f, protocol=pickle.HIGHEST_PROTOCOL)
                    
                    # Actualizar metadatos
                    self.metadata['files'][key] = {
                        'size': cache_file.stat().st_size,
                        'timestamp': item['timestamp'],
                        'ttl': ttl,
                        'priority': priority
                    }
                    self._save_metadata()
                    
                    logger.debug(f"Cache guardado: {key[:8]}... (prioridad: {priority})")
                    
                except Exception as e:
                    logger.error(f"Error guardando cache en disco: {e}")
    def _evict_from_memory(self):
        """Desaloja items de memoria según LRU y prioridad"""
        # Encontrar item con menor prioridad
        min_priority = float('inf')
        min_key = None
        
        for k, v in self.memory_cache.items():
            if v.get('priority', 0) < min_priority:
                min_priority = v.get('priority', 0)
                min_key = k
        
        if min_key:
            del self.memory_cache[min_key]
            self.stats['evictions'] += 1
            logger.debug(f"Item desalojado de memoria: {min_key[:8]}...")
    
    def _get_cache_size(self) -> int:
        """Obtiene el tamaño total del cache en disco"""
        total_size = 0
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                total_size += cache_file.stat().st_size
        except Exception as e:
            logger.error(f"Error calculando tamaño del cache: {e}")
        return total_size
    
    def _cleanup_disk_cache(self):
        """Limpia cache en disco para liberar espacio"""
        try:
            # Obtener archivos ordenados por prioridad y antigüedad
            files_info = []
            
            for key, info in self.metadata.get('files', {}).items():
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    files_info.append({
                        'key': key,
                        'file': cache_file,
                        'priority': info.get('priority', 0),
                        'timestamp': info.get('timestamp', 0),
                        'size': cache_file.stat().st_size
                    })
            
            # Ordenar por prioridad (ascendente) y timestamp (ascendente)
            files_info.sort(key=lambda x: (x['priority'], x['timestamp']))
            
            # Eliminar hasta tener 80% del límite
            target_size = self.max_disk_size * 0.8
            current_size = self._get_cache_size()
            
            for file_info in files_info:
                if current_size <= target_size:
                    break
                
                try:
                    file_info['file'].unlink()
                    current_size -= file_info['size']
                    
                    # Actualizar metadatos
                    if file_info['key'] in self.metadata['files']:
                        del self.metadata['files'][file_info['key']]
                    
                    logger.debug(f"Cache eliminado por espacio: {file_info['key'][:8]}...")
                    
                except Exception as e:
                    logger.error(f"Error eliminando cache: {e}")
            
            self._save_metadata()
            
        except Exception as e:
            logger.error(f"Error en limpieza de disco: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.1f}%",
                'memory_hits': self.stats['memory_hits'],
                'disk_hits': self.stats['disk_hits'],
                'evictions': self.stats['evictions'],
                'memory_items': len(self.memory_cache),
                'disk_size_mb': self._get_cache_size() / (1024 * 1024),
                'disk_items': len(list(self.cache_dir.glob("*.cache")))
            }
    
    def clear_stats(self):
        """Limpia las estadísticas"""
        with self._lock:
            self.stats = {
                'hits': 0,
                'misses': 0,
                'memory_hits': 0,
                'disk_hits': 0,
                'evictions': 0
            }
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