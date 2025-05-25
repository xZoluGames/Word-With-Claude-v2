
from utils.logger import get_logger

logger = get_logger("validator")

"""
Validador de proyectos - Valida completitud y calidad del proyecto académico
"""

import re
from tkinter import messagebox
from datetime import datetime

class ProjectValidator:
    def __init__(self):
        self.criterios_validacion = {
            'campos_requeridos': ['titulo', 'estudiantes', 'tutores'],
            'longitud_minima_seccion': 50,
            'referencias_minimas': 0
        }
    
    def validar_proyecto(self, app_instance):
        """Valida el proyecto con las nuevas funcionalidades"""
        app_instance.validation_text.delete("1.0", "end")
        errores = []
        advertencias = []
        sugerencias = []
        
        # Validar información general
        for campo in self.criterios_validacion['campos_requeridos']:
            if campo in app_instance.proyecto_data:
                if not app_instance.proyecto_data[campo].get().strip():
                    errores.append(f"❌ Campo requerido faltante: {campo}")
        
        # Validar secciones requeridas
        for seccion_id in app_instance.secciones_activas:
            if seccion_id in app_instance.secciones_disponibles:
                seccion = app_instance.secciones_disponibles[seccion_id]
                if seccion['requerida'] and not seccion['capitulo']:
                    if seccion_id in app_instance.content_texts:
                        content = app_instance.content_texts[seccion_id].get("1.0", "end").strip()
                        if len(content) < self.criterios_validacion['longitud_minima_seccion']:
                            errores.append(f"❌ Sección requerida '{seccion['titulo']}' muy corta")
                    else:
                        errores.append(f"❌ Sección requerida '{seccion['titulo']}' faltante")
        
        # Validar citas en marco teórico
        if 'marco_teorico' in app_instance.content_texts:
            content = app_instance.content_texts['marco_teorico'].get("1.0", "end")
            citas_encontradas = re.findall(r'\[CITA:[^\]]+\]', content)
            if not citas_encontradas:
                advertencias.append("⚠️ Marco Teórico sin citas detectadas")
        
        # Validar referencias
        if len(app_instance.referencias) == 0:
            advertencias.append("⚠️ No hay referencias bibliográficas")
        
        # Validar coherencia entre objetivos y contenido
        self._validar_coherencia_objetivos(app_instance, advertencias)
        
        # Mostrar resultados
        resultado = self._generar_reporte_validacion(errores, advertencias, app_instance)
        app_instance.validation_text.insert("1.0", resultado)
        
        # Actualizar progreso
        self._actualizar_progreso_validacion(errores, app_instance)
        
        return len(errores) == 0
    
    def _validar_coherencia_objetivos(self, app_instance, advertencias):
        """Valida coherencia entre objetivos y contenido"""
        if 'objetivos' in app_instance.content_texts:
            objetivos_content = app_instance.content_texts['objetivos'].get("1.0", "end").lower()
            
            # Verificar que los objetivos usen verbos en infinitivo
            verbos_infinitivo = ['identificar', 'determinar', 'analizar', 'evaluar', 'comparar', 'describir', 'explicar']
            tiene_verbos_correctos = any(verbo in objetivos_content for verbo in verbos_infinitivo)
            
            if not tiene_verbos_correctos:
                advertencias.append("⚠️ Los objetivos deberían usar verbos en infinitivo")
    
    def _generar_reporte_validacion(self, errores, advertencias, app_instance):
        """Genera el reporte completo de validación"""
        resultado = "🔍 VALIDACIÓN AVANZADA DEL PROYECTO\n" + "="*60 + "\n\n"
        
        if errores:
            resultado += "🚨 ERRORES CRÍTICOS:\n"
            for error in errores:
                resultado += f"{error}\n"
            resultado += "\n"
        
        if advertencias:
            resultado += "⚠️ ADVERTENCIAS:\n"
            for advertencia in advertencias:
                resultado += f"{advertencia}\n"
            resultado += "\n"
        
        # Estadísticas del proyecto
        resultado += "📊 ESTADÍSTICAS DEL PROYECTO:\n"
        resultado += f"• Secciones activas: {len(app_instance.secciones_activas)}\n"
        resultado += f"• Secciones con contenido: {len([s for s in app_instance.content_texts if app_instance.content_texts[s].get('1.0', 'end').strip()])}\n"
        resultado += f"• Referencias bibliográficas: {len(app_instance.referencias)}\n"
        resultado += f"• Formato personalizado: {'Sí' if app_instance.formato_config['fuente_texto'] != 'Times New Roman' else 'Estándar'}\n"
        
        # Verificar si tiene plantilla base
        if hasattr(app_instance, 'usar_base_var'):
            resultado += f"• Plantilla base: {'Activada' if app_instance.usar_base_var.get() else 'No usada'}\n\n"
        else:
            resultado += f"• Plantilla base: No disponible\n\n"
        
        # Palabras totales
        total_palabras = self._contar_palabras_total(app_instance)
        resultado += f"• Total de palabras: {total_palabras}\n\n"
        
        if not errores and not advertencias:
            resultado += "✅ ¡PROYECTO PERFECTO!\n\n"
            resultado += "🎉 El proyecto cumple con todos los requisitos\n"
            resultado += "📄 Listo para generar con formato personalizado\n"
        elif not errores:
            resultado += "✅ PROYECTO VÁLIDO\n\n"
            resultado += "🎯 Proyecto listo para generar\n"
            resultado += "💡 Revisa las advertencias para mejorar\n"
        else:
            resultado += "❌ PROYECTO INCOMPLETO\n\n"
            resultado += "🔧 Corrige los errores marcados\n"
        
        return resultado
    
    def _actualizar_progreso_validacion(self, errores, app_instance):
        """Actualiza la barra de progreso basada en la validación"""
        total_items = len(self.criterios_validacion['campos_requeridos']) + \
                     len([s for s in app_instance.secciones_disponibles.values() if s['requerida']]) + 1
        items_completos = total_items - len(errores)
        progreso = max(0, items_completos / total_items)
        app_instance.progress.set(progreso)
    
    def _contar_palabras_total(self, app_instance):
        """Cuenta el total de palabras en todas las secciones"""
        total_palabras = 0
        for key, text_widget in app_instance.content_texts.items():
            if key in app_instance.secciones_disponibles:
                content = text_widget.get("1.0", "end").strip()
                if content:
                    palabras = len(content.split())
                    total_palabras += palabras
        return total_palabras
    

    def _validar_imagenes(self, app_instance, advertencias, sugerencias):
        """Valida disponibilidad y calidad de imágenes"""
        enc_activo = (getattr(app_instance, 'encabezado_personalizado', None) or 
                     getattr(app_instance, 'ruta_encabezado', None))
        ins_activo = (getattr(app_instance, 'insignia_personalizada', None) or 
                     getattr(app_instance, 'ruta_insignia', None))
        
        if not enc_activo and not ins_activo:
            advertencias.append("⚠️ No hay imágenes configuradas (encabezado/insignia)")
        elif not enc_activo:
            sugerencias.append("💡 Considera agregar imagen de encabezado")
        elif not ins_activo:
            sugerencias.append("💡 Considera agregar imagen de insignia")

    def _validar_formato_referencias(self, referencias, advertencias):
        """Valida formato APA básico en referencias"""
        for i, ref in enumerate(referencias, 1):
            # Validar formato básico de autor
            if not re.match(r'^[A-ZÁ-Ž].*,\s*[A-Z]\.', ref.get('autor', '')):
                advertencias.append(f"⚠️ Referencia {i}: Formato de autor incorrecto (usar: Apellido, N.)")
            
            # Validar año
            año = ref.get('año', '')
            if not año.isdigit() or not (1900 <= int(año) <= datetime.now().year + 1):
                advertencias.append(f"⚠️ Referencia {i}: Año inválido ({año})")


    def validar_niveles_esquema(self, app_instance, sugerencias):
        """Valida que la configuración garantice niveles de esquema correctos"""
        # Verificar que hay secciones que generarán títulos con nivel de esquema
        titulos_principales = 0
        for seccion_id in app_instance.secciones_activas:
            if seccion_id in app_instance.secciones_disponibles:
                seccion = app_instance.secciones_disponibles[seccion_id]
                if seccion.get('capitulo', False) or seccion.get('requerida', False):
                    titulos_principales += 1
        
        if titulos_principales < 3:
            sugerencias.append("💡 Considera activar más secciones principales para mejor estructura de índice")
        else:
            sugerencias.append(f"✅ {titulos_principales} títulos principales configurados para índice automático")

    def validacion_rapida(self, app_instance):
        """Validación rápida para estadísticas en tiempo real"""
        errores_criticos = 0
        
        # Verificar campos críticos
        for campo in self.criterios_validacion['campos_requeridos']:
            if campo in app_instance.proyecto_data:
                if not app_instance.proyecto_data[campo].get().strip():
                    errores_criticos += 1
        
        # Verificar secciones requeridas
        for seccion_id in app_instance.secciones_activas:
            if seccion_id in app_instance.secciones_disponibles:
                seccion = app_instance.secciones_disponibles[seccion_id]
                if seccion['requerida'] and not seccion['capitulo']:
                    if seccion_id in app_instance.content_texts:
                        content = app_instance.content_texts[seccion_id].get("1.0", "end").strip()
                        if len(content) < self.criterios_validacion['longitud_minima_seccion']:
                            errores_criticos += 1
                    else:
                        errores_criticos += 1
        
        return errores_criticos == 0