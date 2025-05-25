# controllers/project_controller.py
"""
Controlador de Proyecto - Maneja operaciones generales del proyecto
"""

import json
import os
from datetime import datetime
from tkinter import messagebox
from typing import Dict, Optional
from utils.logger import get_logger
from core.state_manager import state_manager
from typing import Tuple, List
logger = get_logger('ProjectController')

class ProjectController:
    """Controlador para operaciones generales del proyecto"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        logger.info("ProjectController inicializado")
    
    def validar_campos_requeridos(self) -> Tuple[bool, list]:
        """
        Valida que los campos requeridos estén completos
        
        Returns:
            tuple[bool, list]: (es_valido, lista_errores)
        """
        errores = []
        campos_requeridos = {
            'titulo': 'Título del proyecto',
            'estudiantes': 'Estudiantes',
            'tutores': 'Tutores'
        }
        
        for campo, nombre in campos_requeridos.items():
            if campo in self.app.proyecto_data:
                valor = self.app.proyecto_data[campo].get().strip()
                if not valor:
                    errores.append(f"❌ {nombre} es obligatorio")
        
        return len(errores) == 0, errores
    
    def obtener_resumen_proyecto(self) -> Dict:
        """Obtiene un resumen del estado actual del proyecto"""
        # Estadísticas básicas
        total_palabras = 0
        secciones_completas = 0
        total_secciones = 0
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                if not seccion.get('capitulo', False):
                    total_secciones += 1
                    
                    if seccion_id in self.app.content_texts:
                        contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                        if contenido and len(contenido) > 50:
                            secciones_completas += 1
                            total_palabras += len(contenido.split())
        
        # Información general
        titulo = ""
        if 'titulo' in self.app.proyecto_data:
            titulo = self.app.proyecto_data['titulo'].get()
        
        return {
            'titulo': titulo,
            'fecha_creacion': state_manager.get_state().fecha_creacion,
            'fecha_modificacion': state_manager.get_state().fecha_modificacion,
            'total_palabras': total_palabras,
            'secciones_completas': secciones_completas,
            'total_secciones': total_secciones,
            'porcentaje_completado': round((secciones_completas / total_secciones * 100) 
                                         if total_secciones > 0 else 0),
            'referencias': len(self.app.referencias),
            'tiene_imagenes': bool(self.app.encabezado_personalizado or 
                                 self.app.insignia_personalizada)
        }
    
    def verificar_integridad_proyecto(self) -> Dict:
        """Verifica la integridad del proyecto"""
        problemas = []
        advertencias = []
        
        # Verificar campos obligatorios
        es_valido, errores_campos = self.validar_campos_requeridos()
        if not es_valido:
            problemas.extend(errores_campos)
        
        # Verificar secciones requeridas
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                if seccion.get('requerida', False) and not seccion.get('capitulo', False):
                    if seccion_id in self.app.content_texts:
                        contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                        if len(contenido) < 50:
                            problemas.append(f"❌ Sección requerida '{seccion['titulo']}' muy corta")
                    else:
                        problemas.append(f"❌ Sección requerida '{seccion['titulo']}' sin contenido")
        
        # Verificar referencias
        if len(self.app.referencias) == 0:
            advertencias.append("⚠️ No hay referencias bibliográficas")
        elif len(self.app.referencias) < 5:
            advertencias.append(f"⚠️ Pocas referencias ({len(self.app.referencias)}), se recomiendan al menos 5")
        
        # Verificar imágenes
        if not (self.app.ruta_encabezado or self.app.encabezado_personalizado):
            advertencias.append("⚠️ No hay imagen de encabezado configurada")
        
        return {
            'es_valido': len(problemas) == 0,
            'problemas': problemas,
            'advertencias': advertencias,
            'total_errores': len(problemas),
            'total_advertencias': len(advertencias)
        }
    
    def preparar_para_generacion(self) -> bool:
        """
        Prepara el proyecto para generación del documento
        
        Returns:
            bool: True si está listo para generar
        """
        # Verificar integridad
        integridad = self.verificar_integridad_proyecto()
        
        if not integridad['es_valido']:
            mensaje = "El proyecto tiene los siguientes problemas:\n\n"
            mensaje += "\n".join(integridad['problemas'])
            
            if integridad['advertencias']:
                mensaje += "\n\nAdvertencias:\n"
                mensaje += "\n".join(integridad['advertencias'])
            
            respuesta = messagebox.askyesno("⚠️ Problemas detectados", 
                mensaje + "\n\n¿Deseas generar el documento de todos modos?")
            
            return respuesta
        
        elif integridad['advertencias']:
            mensaje = "El proyecto tiene las siguientes advertencias:\n\n"
            mensaje += "\n".join(integridad['advertencias'])
            
            respuesta = messagebox.askyesno("⚠️ Advertencias", 
                mensaje + "\n\n¿Deseas continuar?")
            
            return respuesta
        
        return True
    
    def limpiar_proyecto(self):
        """Limpia todos los datos del proyecto actual"""
        # Limpiar campos de información general
        for campo, entry in self.app.proyecto_data.items():
            if hasattr(entry, 'delete'):
                entry.delete(0, "end")
        
        # Limpiar contenido de secciones
        for text_widget in self.app.content_texts.values():
            text_widget.delete("1.0", "end")
        
        # Limpiar referencias
        self.app.referencias.clear()
        
        # Limpiar imágenes personalizadas
        self.app.encabezado_personalizado = None
        self.app.insignia_personalizada = None
        
        # Resetear estado
        state_manager.reset_state()
        
        logger.info("Proyecto limpiado")
    
    def generar_nombre_archivo(self) -> str:
        """Genera un nombre de archivo sugerido para el proyecto"""
        titulo = ""
        if 'titulo' in self.app.proyecto_data:
            titulo = self.app.proyecto_data['titulo'].get().strip()
        
        if titulo:
            # Limpiar caracteres no válidos
            titulo_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_'))
            titulo_limpio = titulo_limpio.replace(' ', '_')[:50]
            return f"{titulo_limpio}_{datetime.now().strftime('%Y%m%d')}"
        else:
            return f"proyecto_academico_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def exportar_metadatos(self) -> Dict:
        """Exporta metadatos del proyecto"""
        resumen = self.obtener_resumen_proyecto()
        
        return {
            'version_app': '2.0',
            'fecha_exportacion': datetime.now().isoformat(),
            'titulo': resumen['titulo'],
            'estadisticas': {
                'palabras': resumen['total_palabras'],
                'secciones': f"{resumen['secciones_completas']}/{resumen['total_secciones']}",
                'referencias': resumen['referencias'],
                'completado': f"{resumen['porcentaje_completado']}%"
            },
            'configuracion': {
                'formato': self.app.formato_config,
                'tiene_imagenes': resumen['tiene_imagenes']
            }
        }