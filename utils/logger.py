"""
Sistema de logging para el proyecto
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class ProjectLogger:
    """Gestor de logging para el proyecto"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.setup_logger()
    
    def setup_logger(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar formato
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        # Logger principal
        self.logger = logging.getLogger('ProyectoAcademico')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo (con rotación)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'proyecto_academico.log'),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self, module_name):
        """Obtiene un logger para un módulo específico"""
        return logging.getLogger(f'ProyectoAcademico.{module_name}')

# Singleton
project_logger = ProjectLogger()

# Funciones de conveniencia
def get_logger(module_name):
    """Obtiene un logger para un módulo"""
    return project_logger.get_logger(module_name)

def log_error(module_name, error, context=""):
    """Registra un error con contexto"""
    logger = get_logger(module_name)
    logger.error(f"{context}: {str(error)}", exc_info=True)

def log_action(module_name, action, details=""):
    """Registra una acción del usuario"""
    logger = get_logger(module_name)
    logger.info(f"Acción: {action} - {details}")
# Agregar en utils/logger.py:
def configure_module_logging(module_name, level=logging.INFO):
    """Configura nivel de logging específico por módulo"""
    logger = logging.getLogger(f'ProyectoAcademico.{module_name}')
    logger.setLevel(level)
    return logger