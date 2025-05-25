# controllers/preview_controller.py
"""
Controlador de Vista Previa - Maneja la generación y actualización de vistas previas
"""

from typing import Dict, Optional
from utils.logger import get_logger
from modules.citations import CitationProcessor

logger = get_logger('PreviewController')

class PreviewController:
    """Controlador para vista previa del documento"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.citation_processor = CitationProcessor()
        self.modo_actual = "📝 Texto"
    
    def actualizar_preview(self, modo: Optional[str] = None) -> str:
        """Actualiza el contenido de la vista previa"""
        if modo:
            self.modo_actual = modo
        
        logger.debug(f"Actualizando preview - Modo: {self.modo_actual}")
        
        try:
            if self.modo_actual == "📝 Texto":
                return self._generar_preview_texto()
            elif self.modo_actual == "🎨 Formato":
                return self._generar_preview_formato()
            elif self.modo_actual == "📊 Estructura":
                return self._generar_preview_estructura()
            else:
                return "Modo de vista previa no reconocido"
                
        except Exception as e:
            logger.error(f"Error generando preview: {e}")
            return f"Error generando vista previa: {str(e)}"
    
    def _generar_preview_texto(self) -> str:
        """Genera vista previa del texto compilado"""
        preview = []
        
        # Título
        titulo = self._obtener_campo('titulo')
        if titulo:
            preview.append(f"{titulo.upper()}\n")
            preview.append("="*len(titulo) + "\n\n")
        
        # Compilar secciones activas
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                # Saltar capítulos (solo son títulos)
                if seccion.get('capitulo', False):
                    preview.append(f"\n{seccion['titulo']}\n")
                    preview.append("="*40 + "\n\n")
                    continue
                
                # Obtener contenido
                contenido = self._obtener_contenido_seccion(seccion_id)
                if contenido:
                    titulo_limpio = self._limpiar_titulo(seccion['titulo'])
                    preview.append(f"\n{titulo_limpio.upper()}\n")
                    preview.append("-"*len(titulo_limpio) + "\n\n")
                    
                    # Procesar citas si corresponde
                    if seccion_id in ['marco_teorico', 'introduccion', 'desarrollo', 'discusion']:
                        contenido = self.citation_processor.procesar_citas_avanzado(contenido)
                    
                    preview.append(contenido + "\n")
        
        # Referencias
        if self.app.referencias:
            preview.append("\n\nREFERENCIAS\n")
            preview.append("-"*11 + "\n\n")
            
            for ref in sorted(self.app.referencias, key=lambda x: x['autor']):
                preview.append(self._formatear_referencia_apa(ref) + "\n\n")
        
        return ''.join(preview) if preview else "No hay contenido para mostrar"
    
    def _generar_preview_formato(self) -> str:
        """Genera vista previa con información de formato"""
        preview = []
        preview.append("🎨 VISTA PREVIA CON FORMATO\n")
        preview.append("="*40 + "\n\n")
        
        # Configuración actual
        config = self.app.formato_config
        preview.append("📋 FORMATO APLICADO:\n")
        preview.append(f"   • Fuente: {config['fuente_texto']} {config['tamaño_texto']}pt\n")
        preview.append(f"   • Títulos: {config['fuente_titulo']} {config['tamaño_titulo']}pt\n")
        preview.append(f"   • Interlineado: {config['interlineado']}\n")
        preview.append(f"   • Márgenes: {config['margen']}cm\n")
        preview.append(f"   • Justificado: {'Sí' if config['justificado'] else 'No'}\n")
        preview.append(f"   • Sangría: {'Sí' if config['sangria'] else 'No'}\n\n")
        
        preview.append("-"*40 + "\n\n")
        
        # Ejemplo de texto formateado
        preview.append("EJEMPLO DE FORMATO:\n\n")
        preview.append("     Este es un ejemplo de cómo se verá el texto con el formato aplicado. ")
        preview.append("La primera línea de cada párrafo tendrá sangría si está activada. ")
        preview.append("El texto estará justificado para una apariencia profesional.\n\n")
        
        preview.append("     Las citas aparecerían así (García, 2020) integradas en el texto. ")
        preview.append("Los títulos tendrán el tamaño y fuente configurados.\n")
        
        return ''.join(preview)
    
    def _generar_preview_estructura(self) -> str:
        """Genera vista previa de la estructura del documento"""
        preview = []
        preview.append("📊 ESTRUCTURA DEL DOCUMENTO\n")
        preview.append("="*40 + "\n\n")
        
        # Información general
        preview.append("📋 INFORMACIÓN GENERAL:\n")
        campos = ['institucion', 'titulo', 'estudiantes', 'tutores', 'categoria']
        for campo in campos:
            valor = self._obtener_campo(campo)
            if valor:
                preview.append(f"   • {campo.title()}: {valor}\n")
        
        preview.append("\n📑 SECCIONES ACTIVAS:\n")
        
        # Estadísticas por sección
        total_palabras = 0
        secciones_completas = 0
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion = self.app.secciones_disponibles[seccion_id]
                
                if seccion.get('capitulo', False):
                    preview.append(f"\n{seccion['titulo']}\n")
                else:
                    contenido = self._obtener_contenido_seccion(seccion_id)
                    palabras = len(contenido.split()) if contenido else 0
                    total_palabras += palabras
                    
                    if palabras > 50:
                        secciones_completas += 1
                        estado = "✅"
                    elif palabras > 0:
                        estado = "⚠️"
                    else:
                        estado = "❌"
                    
                    preview.append(f"   {estado} {seccion['titulo']} ({palabras} palabras)\n")
        
        # Resumen
        preview.append(f"\n📈 RESUMEN:\n")
        preview.append(f"   • Secciones completas: {secciones_completas}\n")
        preview.append(f"   • Total de palabras: {total_palabras:,}\n")
        preview.append(f"   • Referencias: {len(self.app.referencias)}\n")
        
        # Validación rápida
        if total_palabras < 1000:
            preview.append("\n⚠️ ADVERTENCIA: El documento tiene menos de 1000 palabras\n")
        if len(self.app.referencias) < 5:
            preview.append("⚠️ ADVERTENCIA: Se recomiendan al menos 5 referencias\n")
        
        return ''.join(preview)
    
    def _obtener_campo(self, campo: str) -> str:
        """Obtiene el valor de un campo del proyecto"""
        if campo in self.app.proyecto_data:
            entry = self.app.proyecto_data[campo]
            if hasattr(entry, 'get'):
                return entry.get().strip()
        return ""
    
    def _obtener_contenido_seccion(self, seccion_id: str) -> str:
        """Obtiene el contenido de una sección"""
        if seccion_id in self.app.content_texts:
            return self.app.content_texts[seccion_id].get("1.0", "end").strip()
        return ""
    
    def _limpiar_titulo(self, titulo: str) -> str:
        """Limpia emojis y caracteres especiales del título"""
        import re
        return re.sub(r'[^\w\s-]', '', titulo).strip()
    
    def _formatear_referencia_apa(self, ref: Dict) -> str:
        """Formatea una referencia en APA"""
        tipo = ref.get('tipo', 'Libro')
        
        if tipo == 'Web':
            return f"{ref['autor']} ({ref['año']}). {ref['titulo']}. Recuperado de {ref['fuente']}"
        else:
            return f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}."