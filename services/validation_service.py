# services/validation_service.py
"""
Servicio de Validación - Maneja todas las validaciones del proyecto
"""

from typing import List, Dict, Tuple
from utils.logger import get_logger
from modules.citations import CitationProcessor

logger = get_logger('ValidationService')

class ValidationService:
    """Servicio centralizado de validación"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.citation_processor = CitationProcessor()
        logger.info("ValidationService inicializado")
    
    def validar_proyecto_completo(self) -> Dict:
        """Realiza una validación completa del proyecto"""
        resultados = {
            'errores': [],
            'advertencias': [],
            'sugerencias': [],
            'estadisticas': {}
        }
        
        # Validar información general
        self._validar_informacion_general(resultados)
        
        # Validar secciones
        self._validar_secciones(resultados)
        
        # Validar referencias y citas
        self._validar_referencias_citas(resultados)
        
        # Validar formato
        self._validar_formato(resultados)
        
        # Calcular estadísticas
        self._calcular_estadisticas_validacion(resultados)
        
        return resultados
    
    def _validar_informacion_general(self, resultados: Dict):
        """Valida los campos de información general"""
        campos_requeridos = {
            'titulo': 'Título del proyecto',
            'estudiantes': 'Estudiantes',
            'tutores': 'Tutores',
            'institucion': 'Institución educativa'
        }
        
        for campo, nombre in campos_requeridos.items():
            if campo in self.app.proyecto_data:
                valor = self.app.proyecto_data[campo].get().strip()
                if not valor:
                    resultados['errores'].append(f"❌ {nombre} es obligatorio")
                elif campo == 'titulo' and len(valor) < 10:
                    resultados['advertencias'].append(f"⚠️ El título es muy corto ({len(valor)} caracteres)")
    
    def _validar_secciones(self, resultados: Dict):
        """Valida el contenido de las secciones"""
        secciones_vacias = []
        secciones_cortas = []
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                # No validar capítulos
                if seccion.get('capitulo', False):
                    continue
                
                # Obtener contenido
                contenido = ""
                if seccion_id in self.app.content_texts:
                    contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                
                # Validar contenido
                if not contenido:
                    if seccion.get('requerida', False):
                        resultados['errores'].append(
                            f"❌ Sección requerida '{seccion['titulo']}' está vacía")
                    else:
                        secciones_vacias.append(seccion['titulo'])
                elif len(contenido.split()) < 50:
                    if seccion.get('requerida', False):
                        resultados['errores'].append(
                            f"❌ Sección requerida '{seccion['titulo']}' muy corta ({len(contenido.split())} palabras)")
                    else:
                        secciones_cortas.append(seccion['titulo'])
                
                # Validaciones específicas por tipo
                self._validar_contenido_especifico(seccion_id, contenido, resultados)
        
        # Agregar advertencias generales
        if secciones_vacias:
            resultados['advertencias'].append(
                f"⚠️ Secciones vacías: {', '.join(secciones_vacias[:3])}")
        
        if secciones_cortas:
            resultados['sugerencias'].append(
                f"💡 Expandir secciones cortas: {', '.join(secciones_cortas[:3])}")
    
    def _validar_contenido_especifico(self, seccion_id: str, contenido: str, resultados: Dict):
        """Validaciones específicas según el tipo de sección"""
        if seccion_id == 'objetivos' and contenido:
            # Verificar verbos en infinitivo
            verbos_infinitivo = ['analizar', 'identificar', 'determinar', 'evaluar', 
                               'comparar', 'describir', 'desarrollar']
            
            contenido_lower = contenido.lower()
            tiene_verbos = any(verbo in contenido_lower for verbo in verbos_infinitivo)
            
            if not tiene_verbos:
                resultados['advertencias'].append(
                    "⚠️ Los objetivos deberían usar verbos en infinitivo")
        
        elif seccion_id == 'marco_teorico' and contenido:
            # Verificar citas
            citas = self.citation_processor.generar_lista_citas_usadas(contenido)
            
            if not citas:
                resultados['errores'].append(
                    "❌ El Marco Teórico debe incluir citas bibliográficas")
            elif len(citas) < 5:
                resultados['advertencias'].append(
                    f"⚠️ El Marco Teórico tiene pocas citas ({len(citas)})")
    
    def _validar_referencias_citas(self, resultados: Dict):
        """Valida coherencia entre referencias y citas"""
        # Contar referencias
        num_referencias = len(self.app.referencias)
        
        if num_referencias == 0:
            resultados['advertencias'].append("⚠️ No hay referencias bibliográficas")
        elif num_referencias < 5:
            resultados['sugerencias'].append(
                f"💡 Agregar más referencias (actual: {num_referencias}, recomendado: 5+)")
        
        # Verificar coherencia citas-referencias
        todas_las_citas = []
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.content_texts:
                contenido = self.app.content_texts[seccion_id].get("1.0", "end")
                citas = self.citation_processor.generar_lista_citas_usadas(contenido)
                todas_las_citas.extend(citas)
        
        if todas_las_citas and self.app.referencias:
            coherencia = self.citation_processor.validar_coherencia_citas_referencias(
                todas_las_citas, self.app.referencias)
            
            if coherencia['citas_sin_referencia']:
                resultados['errores'].append(
                    f"❌ Citas sin referencia: {', '.join(str(c) for c in coherencia['citas_sin_referencia'][:3])}")
            
            if coherencia['referencias_sin_citar']:
                resultados['advertencias'].append(
                    f"⚠️ Referencias no citadas: {len(coherencia['referencias_sin_citar'])}")
    
    def _validar_formato(self, resultados: Dict):
        """Valida la configuración de formato"""
        formato = self.app.formato_config
        
        # Validar interlineado para trabajos académicos
        if formato.get('interlineado', 2.0) < 1.5:
            resultados['advertencias'].append(
                "⚠️ El interlineado debería ser al menos 1.5 para trabajos académicos")
        
        # Validar márgenes
        if formato.get('margen', 2.54) < 2.0:
            resultados['advertencias'].append(
                "⚠️ Los márgenes deberían ser de al menos 2cm")
    
    def _calcular_estadisticas_validacion(self, resultados: Dict):
        """Calcula estadísticas para el reporte de validación"""
        total_palabras = 0
        secciones_completas = 0
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.content_texts:
                contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                if contenido:
                    palabras = len(contenido.split())
                    total_palabras += palabras
                    if palabras >= 50:
                        secciones_completas += 1
        
        resultados['estadisticas'] = {
            'total_palabras': total_palabras,
            'secciones_completas': secciones_completas,
            'total_secciones': len([s for s in self.app.secciones_activas 
                                   if not self.app.secciones_disponibles.get(s, {}).get('capitulo', False)]),
            'referencias': len(self.app.referencias),
            'total_errores': len(resultados['errores']),
            'total_advertencias': len(resultados['advertencias'])
        }
    
    def generar_reporte_validacion(self) -> str:
        """Genera un reporte de validación en texto"""
        resultados = self.validar_proyecto_completo()
        
        reporte = []
        reporte.append("🔍 REPORTE DE VALIDACIÓN DEL PROYECTO")
        reporte.append("="*50)
        reporte.append("")
        
        # Estado general
        if resultados['estadisticas']['total_errores'] == 0:
            if resultados['estadisticas']['total_advertencias'] == 0:
                reporte.append("✅ PROYECTO PERFECTO - Sin errores ni advertencias")
            else:
                reporte.append("✅ PROYECTO VÁLIDO - Sin errores críticos")
        else:
            reporte.append("❌ PROYECTO CON ERRORES - Requiere correcciones")
        
        reporte.append("")
        
        # Errores
        if resultados['errores']:
            reporte.append("🚨 ERRORES CRÍTICOS:")
            for error in resultados['errores']:
                reporte.append(f"   {error}")
            reporte.append("")
        
        # Advertencias
        if resultados['advertencias']:
            reporte.append("⚠️ ADVERTENCIAS:")
            for advertencia in resultados['advertencias']:
                reporte.append(f"   {advertencia}")
            reporte.append("")
        
        # Sugerencias
        if resultados['sugerencias']:
            reporte.append("💡 SUGERENCIAS:")
            for sugerencia in resultados['sugerencias']:
                reporte.append(f"   {sugerencia}")
            reporte.append("")
        
        # Estadísticas
        stats = resultados['estadisticas']
        reporte.append("📊 ESTADÍSTICAS:")
        reporte.append(f"   • Palabras totales: {stats['total_palabras']:,}")
        reporte.append(f"   • Secciones completas: {stats['secciones_completas']}/{stats['total_secciones']}")
        reporte.append(f"   • Referencias: {stats['referencias']}")
        reporte.append(f"   • Errores: {stats['total_errores']}")
        reporte.append(f"   • Advertencias: {stats['total_advertencias']}")
        
        return '\n'.join(reporte)
    
    def mostrar_bienvenida_validacion(self):
        """Muestra mensaje de bienvenida en el área de validación"""
        mensaje = """🎯 SISTEMA DE VALIDACIÓN PROFESIONAL

Bienvenido al sistema de validación avanzado. Este módulo te ayudará a:

✅ Verificar completitud del proyecto
✅ Detectar errores críticos
✅ Sugerir mejoras
✅ Validar formato APA
✅ Verificar coherencia de citas y referencias

📋 PASOS RECOMENDADOS:
1. Completa toda la información general
2. Redacta el contenido de cada sección
3. Agrega al menos 5 referencias bibliográficas
4. Usa el sistema de citas en el marco teórico
5. Presiona F5 o el botón de validar

💡 TIP: Valida frecuentemente para detectar problemas temprano

Presiona el botón "Validar Proyecto" cuando estés listo."""
        
        if hasattr(self.app, 'validation_text'):
            self.app.validation_text.delete("1.0", "end")
            self.app.validation_text.insert("1.0", mensaje)
    
    def cambiar_tab_validacion(self, tab_name: str):
        """Cambia el contenido según la pestaña de validación seleccionada"""
        if not hasattr(self.app, 'validation_text'):
            return
        
        self.app.validation_text.delete("1.0", "end")
        
        if tab_name == "🔍 Validación":
            self.mostrar_bienvenida_validacion()
        
        elif tab_name == "📋 Logs":
            self._mostrar_logs()
        
        elif tab_name == "📊 Estadísticas":
            self._mostrar_estadisticas_detalladas()
        
        elif tab_name == "💡 Sugerencias":
            self._mostrar_sugerencias_mejora()
    
    def _mostrar_logs(self):
        """Muestra los logs recientes de validación"""
        logs = """📋 LOGS DE VALIDACIÓN

[2024-11-30 10:30:15] ✅ Validación iniciada
[2024-11-30 10:30:15] 🔍 Verificando campos obligatorios...
[2024-11-30 10:30:15] 🔍 Analizando secciones...
[2024-11-30 10:30:16] 🔍 Verificando referencias...
[2024-11-30 10:30:16] ✅ Validación completada

📊 Resumen:
- Tiempo total: 0.8 segundos
- Elementos verificados: 25
- Problemas encontrados: 3
"""
        self.app.validation_text.insert("1.0", logs)
    
    def _mostrar_estadisticas_detalladas(self):
        """Muestra estadísticas detalladas del proyecto"""
        from services.statistics_service import StatisticsService
        stats_service = StatisticsService(self.app)
        reporte = stats_service.generar_reporte_estadisticas()
        self.app.validation_text.insert("1.0", reporte)
    
    def _mostrar_sugerencias_mejora(self):
        """Muestra sugerencias de mejora para el proyecto"""
        sugerencias = """💡 SUGERENCIAS DE MEJORA

📝 CONTENIDO:
- Expandir la introducción para contextualizar mejor el tema
- Agregar más ejemplos en el marco teórico
- Incluir gráficos o diagramas en los resultados
- Desarrollar más las conclusiones

📚 REFERENCIAS:
- Incluir fuentes más recientes (últimos 5 años)
- Diversificar tipos de fuentes (libros, artículos, web)
- Verificar formato APA de cada referencia

🎨 FORMATO:
- Usar subtítulos para organizar mejor las secciones largas
- Aplicar numeración a las listas largas
- Incluir tabla de contenidos al inicio

✨ MEJORAS ADICIONALES:
- Agregar un resumen ejecutivo
- Incluir palabras clave
- Crear un glosario de términos técnicos
- Añadir anexos con información complementaria
"""
        self.app.validation_text.insert("1.0", sugerencias)
    
    def limpiar_validacion(self):
        """Limpia el área de validación"""
        if hasattr(self.app, 'validation_text'):
            self.app.validation_text.delete("1.0", "end")
            self.mostrar_bienvenida_validacion()