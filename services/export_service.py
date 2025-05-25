# services/export_service.py
"""
Servicio de Exportación - Maneja las exportaciones del proyecto
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger('ExportService')

class ExportService:
    """Servicio para exportar datos del proyecto"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        logger.info("ExportService inicializado")
    
    def exportar_proyecto_completo(self, incluir_contenido: bool = True) -> bool:
        """
        Exporta el proyecto completo a JSON
        
        Args:
            incluir_contenido: Si incluir el contenido de las secciones
            
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            # Preparar datos
            proyecto_data = {
                'version': '2.0',
                'fecha_exportacion': datetime.now().isoformat(),
                'metadatos': {
                    'titulo': self._obtener_campo('titulo'),
                    'institucion': self._obtener_campo('institucion'),
                    'fecha_creacion': datetime.now().isoformat()
                },
                'informacion_general': {},
                'formato_config': self.app.formato_config,
                'referencias': self.app.referencias,
                'secciones_activas': self.app.secciones_activas,
                'configuracion_imagenes': {
                    'encabezado_personalizado': self.app.encabezado_personalizado,
                    'insignia_personalizada': self.app.insignia_personalizada,
                    'watermark_config': {
                        'opacity': self.app.watermark_opacity,
                        'stretch': self.app.watermark_stretch,
                        'mode': self.app.watermark_mode
                    }
                }
            }
            
            # Información general
            for campo, entry in self.app.proyecto_data.items():
                if hasattr(entry, 'get'):
                    proyecto_data['informacion_general'][campo] = entry.get()
            
            # Contenido de secciones si se solicita
            if incluir_contenido:
                proyecto_data['contenido_secciones'] = {}
                for seccion_id, text_widget in self.app.content_texts.items():
                    proyecto_data['contenido_secciones'][seccion_id] = text_widget.get("1.0", "end")
            
            # Solicitar ubicación
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Proyecto JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Exportar Proyecto Completo",
                initialfile=f"proyecto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(proyecto_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Proyecto exportado: {filename}")
                messagebox.showinfo("✅ Exportado", 
                    f"Proyecto exportado exitosamente:\n{os.path.basename(filename)}")
                return True
                
        except Exception as e:
            logger.error(f"Error exportando proyecto: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            
        return False
    
    def exportar_estadisticas(self) -> bool:
        """
        Exporta estadísticas del proyecto a archivo de texto
        
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            from services.statistics_service import StatisticsService
            stats_service = StatisticsService(self.app)
            
            # Generar reporte
            reporte = stats_service.generar_reporte_estadisticas()
            
            # Agregar información adicional
            reporte += "\n\n" + "="*50
            reporte += "\n📋 INFORMACIÓN DEL PROYECTO\n"
            reporte += f"   • Título: {self._obtener_campo('titulo')}\n"
            reporte += f"   • Institución: {self._obtener_campo('institucion')}\n"
            reporte += f"   • Estudiantes: {self._obtener_campo('estudiantes')}\n"
            reporte += f"   • Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Guardar
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Exportar Estadísticas",
                initialfile=f"estadisticas_{datetime.now().strftime('%Y%m%d')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(reporte)
                
                logger.info(f"Estadísticas exportadas: {filename}")
                messagebox.showinfo("✅ Exportado", "Estadísticas exportadas correctamente")
                return True
                
        except Exception as e:
            logger.error(f"Error exportando estadísticas: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            
        return False
    
    def exportar_solo_referencias(self) -> bool:
        """
        Exporta solo las referencias bibliográficas
        
        Returns:
            bool: True si se exportó exitosamente
        """
        if not self.app.referencias:
            messagebox.showwarning("⚠️ Sin referencias", 
                "No hay referencias para exportar")
            return False
        
        try:
            # Preparar datos
            referencias_data = {
                'version': '1.0',
                'fecha_exportacion': datetime.now().isoformat(),
                'total_referencias': len(self.app.referencias),
                'referencias': self.app.referencias
            }
            
            # Solicitar ubicación
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Referencias JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Exportar Referencias",
                initialfile=f"referencias_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(referencias_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Referencias exportadas: {filename}")
                messagebox.showinfo("✅ Exportado", 
                    f"Referencias exportadas: {len(self.app.referencias)} referencias")
                return True
                
        except Exception as e:
            logger.error(f"Error exportando referencias: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            
        return False
    
    def exportar_estructura_secciones(self) -> bool:
        """
        Exporta la estructura de secciones del proyecto
        
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            # Preparar datos
            estructura = {
                'version': '1.0',
                'fecha_exportacion': datetime.now().isoformat(),
                'secciones_disponibles': self.app.secciones_disponibles,
                'secciones_activas': self.app.secciones_activas,
                'estadisticas': {
                    'total_secciones': len(self.app.secciones_disponibles),
                    'secciones_activas': len(self.app.secciones_activas),
                    'capitulos': len([s for s in self.app.secciones_disponibles.values() 
                                    if s.get('capitulo', False)]),
                    'secciones_requeridas': len([s for s in self.app.secciones_disponibles.values() 
                                               if s.get('requerida', False)])
                }
            }
            
            # Solicitar ubicación
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Estructura JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Exportar Estructura de Secciones",
                initialfile=f"estructura_secciones_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(estructura, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Estructura exportada: {filename}")
                messagebox.showinfo("✅ Exportado", "Estructura de secciones exportada")
                return True
                
        except Exception as e:
            logger.error(f"Error exportando estructura: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            
        return False
    
    def exportar_informe_completo(self) -> bool:
        """
        Exporta un informe completo del proyecto en formato texto
        
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            # Generar informe completo
            informe = self._generar_informe_completo()
            
            # Solicitar ubicación
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Exportar Informe Completo",
                initialfile=f"informe_proyecto_{datetime.now().strftime('%Y%m%d')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(informe)
                
                logger.info(f"Informe exportado: {filename}")
                messagebox.showinfo("✅ Exportado", "Informe completo exportado")
                return True
                
        except Exception as e:
            logger.error(f"Error exportando informe: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            
        return False
    
    def _generar_informe_completo(self) -> str:
        """Genera un informe completo del proyecto"""
        informe = []
        
        # Encabezado
        informe.append("="*60)
        informe.append("INFORME COMPLETO DEL PROYECTO ACADÉMICO")
        informe.append("="*60)
        informe.append("")
        
        # Información general
        informe.append("📋 INFORMACIÓN GENERAL")
        informe.append("-"*30)
        informe.append(f"Título: {self._obtener_campo('titulo')}")
        informe.append(f"Institución: {self._obtener_campo('institucion')}")
        informe.append(f"Estudiantes: {self._obtener_campo('estudiantes')}")
        informe.append(f"Tutores: {self._obtener_campo('tutores')}")
        informe.append(f"Categoría: {self._obtener_campo('categoria')}")
        informe.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        informe.append("")
        
        # Estadísticas
        from services.statistics_service import StatisticsService
        stats_service = StatisticsService(self.app)
        stats = stats_service.calcular_estadisticas()
        
        informe.append("📊 ESTADÍSTICAS")
        informe.append("-"*30)
        informe.append(f"Palabras totales: {stats['total_words']:,}")
        informe.append(f"Caracteres totales: {stats['total_chars']:,}")
        informe.append(f"Secciones completadas: {stats['sections_completed']}/{stats['total_sections']}")
        informe.append(f"Referencias bibliográficas: {stats['references']}")
        informe.append(f"Porcentaje de completitud: {stats['completion_percentage']}%")
        informe.append("")
        
        # Estructura de secciones
        informe.append("📑 ESTRUCTURA DE SECCIONES")
        informe.append("-"*30)
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                # Estado de la sección
                contenido = ""
                if seccion_id in self.app.content_texts:
                    contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                
                palabras = len(contenido.split()) if contenido else 0
                estado = "✅" if palabras > 50 else "⚠️" if palabras > 0 else "❌"
                
                informe.append(f"{estado} {seccion['titulo']} - {palabras} palabras")
        
        informe.append("")
        
        # Configuración de formato
        informe.append("🎨 CONFIGURACIÓN DE FORMATO")
        informe.append("-"*30)
        formato = self.app.formato_config
        informe.append(f"Fuente de texto: {formato.get('fuente_texto', 'Times New Roman')} {formato.get('tamaño_texto', 12)}pt")
        informe.append(f"Fuente de títulos: {formato.get('fuente_titulo', 'Times New Roman')} {formato.get('tamaño_titulo', 14)}pt")
        informe.append(f"Interlineado: {formato.get('interlineado', 2.0)}")
        informe.append(f"Márgenes: {formato.get('margen', 2.54)}cm")
        informe.append(f"Texto justificado: {'Sí' if formato.get('justificado', True) else 'No'}")
        informe.append(f"Sangría: {'Sí' if formato.get('sangria', True) else 'No'}")
        informe.append("")
        
        # Validación
        from services.validation_service import ValidationService
        val_service = ValidationService(self.app)
        val_results = val_service.validar_proyecto_completo()
        
        informe.append("🔍 VALIDACIÓN")
        informe.append("-"*30)
        informe.append(f"Errores críticos: {val_results['estadisticas']['total_errores']}")
        informe.append(f"Advertencias: {val_results['estadisticas']['total_advertencias']}")
        
        if val_results['errores']:
            informe.append("\nErrores encontrados:")
            for error in val_results['errores'][:5]:
                informe.append(f"  {error}")
        
        if val_results['advertencias']:
            informe.append("\nAdvertencias:")
            for advertencia in val_results['advertencias'][:5]:
                informe.append(f"  {advertencia}")
        
        return '\n'.join(informe)
    
    def _obtener_campo(self, campo: str) -> str:
        """
        Obtiene el valor de un campo del proyecto
        
        Args:
            campo: Nombre del campo
            
        Returns:
            str: Valor del campo o cadena vacía
        """
        if campo in self.app.proyecto_data and hasattr(self.app.proyecto_data[campo], 'get'):
            return self.app.proyecto_data[campo].get()
        return ""