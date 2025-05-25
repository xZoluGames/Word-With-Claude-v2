# services/statistics_service.py
"""
Servicio de Estadísticas - Calcula y actualiza estadísticas del proyecto
"""

from utils.logger import get_logger

logger = get_logger('StatisticsService')

class StatisticsService:
    """Servicio para cálculo de estadísticas"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def actualizar_estadisticas(self):
        """Actualiza todas las estadísticas del proyecto"""
        stats = self.calcular_estadisticas()
        
        # Actualizar label si existe
        if hasattr(self.app, 'stats_label'):
            texto = (f"📊 Palabras: {stats['total_words']:,} | "
                    f"Secciones: {stats['sections_completed']}/{stats['total_sections']} | "
                    f"Referencias: {stats['references']}")
            self.app.stats_label.configure(text=texto)
        
        logger.debug(f"Estadísticas actualizadas: {stats}")
        return stats
    
    def calcular_estadisticas(self) -> dict:
        """Calcula las estadísticas actuales"""
        total_words = 0
        total_chars = 0
        sections_completed = 0
        total_sections = 0
        
        # Contar secciones y palabras
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                # No contar capítulos
                if not seccion.get('capitulo', False):
                    total_sections += 1
                    
                    if seccion_id in self.app.content_texts:
                        content = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                        if content and len(content) > 10:
                            sections_completed += 1
                            words = len(content.split())
                            total_words += words
                            total_chars += len(content)
        
        return {
            'total_words': total_words,
            'total_chars': total_chars,
            'sections_completed': sections_completed,
            'total_sections': total_sections,
            'references': len(self.app.referencias),
            'completion_percentage': round((sections_completed / total_sections * 100) 
                                         if total_sections > 0 else 0, 1)
        }
    
    def generar_reporte_estadisticas(self) -> str:
        """Genera un reporte detallado de estadísticas"""
        stats = self.calcular_estadisticas()
        
        reporte = []
        reporte.append("📊 REPORTE DE ESTADÍSTICAS DEL PROYECTO")
        reporte.append("="*50)
        reporte.append("")
        
        reporte.append(f"📝 Contenido:")
        reporte.append(f"   • Palabras totales: {stats['total_words']:,}")
        reporte.append(f"   • Caracteres totales: {stats['total_chars']:,}")
        reporte.append(f"   • Promedio palabras/sección: {stats['total_words'] // max(1, stats['sections_completed'])}")
        reporte.append("")
        
        reporte.append(f"📑 Secciones:")
        reporte.append(f"   • Completadas: {stats['sections_completed']}/{stats['total_sections']}")
        reporte.append(f"   • Porcentaje: {stats['completion_percentage']}%")
        reporte.append("")
        
        reporte.append(f"📚 Referencias:")
        reporte.append(f"   • Total: {stats['references']}")
        
        return '\n'.join(reporte)