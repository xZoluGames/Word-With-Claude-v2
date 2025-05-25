#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Proyectos Académicos - Punto de entrada principal
"""

import sys
import os
import traceback
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Verificación de versión de Python
if sys.version_info < (3, 8):
    print("Error: Se requiere Python 3.8 o superior")
    sys.exit(1)

try:
    import customtkinter as ctk
    from ui.main_window import ProyectoAcademicoGenerator
    from utils.logger import get_logger, configure_module_logging
    from config.settings import APP_CONFIG
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    print("Instala las dependencias con: pip install -r requirements.txt")
    sys.exit(1)

logger = get_logger("main")

def verify_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = {
        'customtkinter': 'customtkinter',
        'PIL': 'Pillow',
        'docx': 'python-docx',
        'lxml': 'lxml'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"Paquetes faltantes: {', '.join(missing)}")
        print(f"\nError: Faltan las siguientes dependencias: {', '.join(missing)}")
        print(f"Instálalas con: pip install {' '.join(missing)}")
        sys.exit(1)

def setup_directories():
    """Crea los directorios necesarios"""
    directories = [
        'logs',
        'cache',
        'cache/images',
        'resources/images',
        'plantillas',
        'exports',
        'backup'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directorio verificado: {directory}")

def main():
    """Función principal con manejo robusto de errores"""
    try:
        logger.info("="*60)
        logger.info(f"Iniciando {APP_CONFIG['name']} v{APP_CONFIG['version']}")
        logger.info(f"Python {sys.version}")
        logger.info(f"Directorio de trabajo: {os.getcwd()}")
        
        # Verificar dependencias
        verify_dependencies()
        
        # Crear directorios necesarios
        setup_directories()
        
        # Configuración del tema
        ctk.set_appearance_mode(APP_CONFIG.get('theme', 'dark'))
        ctk.set_default_color_theme(APP_CONFIG.get('color_theme', 'blue'))
        
        # Crear y ejecutar aplicación
        app = ProyectoAcademicoGenerator()
        logger.info("Aplicación iniciada correctamente")
        
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Aplicación cerrada por el usuario (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}", exc_info=True)
        
        # Mostrar error al usuario
        error_msg = f"Error crítico:\n{str(e)}\n\nRevisa el archivo de log para más detalles."
        
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error Crítico", error_msg)
        except:
            print(f"\n{error_msg}")
        
        # Guardar traceback completo
        with open('crash_report.txt', 'w', encoding='utf-8') as f:
            f.write(f"Crash Report - {APP_CONFIG['name']} v{APP_CONFIG['version']}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Timestamp: {os.environ.get('TZ', 'UTC')}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"OS: {sys.platform}\n")
            f.write(f"{'='*60}\n\n")
            f.write(traceback.format_exc())
        
        print("\nSe ha guardado un reporte del error en 'crash_report.txt'")
        sys.exit(1)

if __name__ == "__main__":
    main()