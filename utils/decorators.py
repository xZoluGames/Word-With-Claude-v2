"""
Decoradores útiles para el proyecto
"""

import functools
import time
import threading
from typing import Callable, Any
from utils.logger import get_logger

logger = get_logger('decorators')


def timeit(func: Callable) -> Callable:
    """
    Decorador para medir tiempo de ejecución.
    
    Example:
        @timeit
        def slow_function():
            time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        elapsed = end_time - start_time
        logger.debug(f"{func.__name__} tomó {elapsed:.3f} segundos")
        
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Decorador para reintentar operaciones que pueden fallar.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Retraso inicial entre intentos (segundos)
        backoff: Factor de multiplicación para el retraso
        exceptions: Tupla de excepciones a capturar
    
    Example:
        @retry(max_attempts=3, delay=1, exceptions=(IOError, ValueError))
        def unstable_operation():
            # código que puede fallar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} falló (intento {attempt + 1}/{max_attempts}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} falló después de {max_attempts} intentos"
                        )
            
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def synchronized(lock=None):
    """
    Decorador para sincronizar acceso a métodos.
    
    Args:
        lock: Lock a usar, si no se provee se crea uno nuevo
    
    Example:
        class Counter:
            def __init__(self):
                self._lock = threading.Lock()
                self._count = 0
            
            @synchronized(lambda self: self._lock)
            def increment(self):
                self._count += 1
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Obtener el lock
            if lock is None:
                # Crear un lock por instancia
                if not hasattr(self, '_synchronized_lock'):
                    self._synchronized_lock = threading.Lock()
                actual_lock = self._synchronized_lock
            elif callable(lock):
                actual_lock = lock(self)
            else:
                actual_lock = lock
            
            with actual_lock:
                return func(self, *args, **kwargs)
                
        return wrapper
    return decorator


def validate_types(**expected_types):
    """
    Decorador para validar tipos de argumentos.
    
    Example:
        @validate_types(name=str, age=int, active=bool)
        def create_user(name, age, active=True):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener nombres de parámetros
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validar tipos
            for param_name, expected_type in expected_types.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{func.__name__}: '{param_name}' debe ser {expected_type.__name__}, "
                            f"recibido {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def memoize(maxsize: int = 128):
    """
    Decorador para cachear resultados de funciones puras.
    Similar a lru_cache pero con logging.
    
    Example:
        @memoize(maxsize=256)
        def expensive_calculation(n):
            return n ** 2
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_order = []
        hits = misses = 0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            
            # Crear clave del cache
            key = str(args) + str(sorted(kwargs.items()))
            
            if key in cache:
                hits += 1
                # Mover al final (LRU)
                cache_order.remove(key)
                cache_order.append(key)
                logger.debug(f"{func.__name__} cache hit (ratio: {hits/(hits+misses):.2%})")
                return cache[key]
            
            misses += 1
            result = func(*args, **kwargs)
            
            # Agregar al cache
            cache[key] = result
            cache_order.append(key)
            
            # Eliminar más antiguo si excede maxsize
            if len(cache) > maxsize:
                oldest = cache_order.pop(0)
                del cache[oldest]
            
            return result
        
        # Agregar método para limpiar cache
        def clear_cache():
            nonlocal hits, misses
            cache.clear()
            cache_order.clear()
            hits = misses = 0
            logger.info(f"{func.__name__} cache cleared")
        
        wrapper.clear_cache = clear_cache
        wrapper.cache_info = lambda: {'hits': hits, 'misses': misses, 'size': len(cache)}
        
        return wrapper
    return decorator


def debounce(wait: float):
    """
    Decorador para evitar llamadas múltiples en corto tiempo.
    Útil para eventos de UI.
    
    Args:
        wait: Tiempo de espera en segundos
    
    Example:
        @debounce(0.5)
        def on_text_changed(text):
            # Se ejecutará solo 0.5 segundos después de la última llamada
            process_text(text)
    """
    def decorator(func: Callable) -> Callable:
        timer = None
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                nonlocal timer
                timer = None
                return func(*args, **kwargs)
            
            # Cancelar timer anterior si existe
            if timer is not None:
                timer.cancel()
            
            # Crear nuevo timer
            timer = threading.Timer(wait, call_func)
            timer.start()
        
        return wrapper
    return decorator


def run_in_thread(daemon: bool = True):
    """
    Decorador para ejecutar función en un thread separado.
    
    Args:
        daemon: Si el thread debe ser daemon
    
    Example:
        @run_in_thread(daemon=True)
        def background_task():
            # Esta función se ejecutará en un thread separado
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(
                target=func,
                args=args,
                kwargs=kwargs,
                daemon=daemon
            )
            thread.start()
            return thread
        return wrapper
    return decorator


def deprecated(reason: str = "", version: str = ""):
    """
    Marca una función como obsoleta.
    
    Args:
        reason: Razón o alternativa sugerida
        version: Versión en la que se marcó como obsoleta
    
    Example:
        @deprecated(reason="Usa new_function() en su lugar", version="2.0")
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            
            msg = f"{func.__name__} está obsoleto"
            if version:
                msg += f" desde la versión {version}"
            if reason:
                msg += f". {reason}"
            
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            logger.warning(msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator