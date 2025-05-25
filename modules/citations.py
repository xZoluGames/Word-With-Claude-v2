
from utils.logger import get_logger

logger = get_logger("citations")

"""
Sistema de citas mejorado - Procesamiento avanzado de citas académicas APA
"""

import re
from tkinter import messagebox
from datetime import datetime

class CitationProcessor:
    def __init__(self):
        self.citation_patterns = {
            'textual': r'\[CITA:textual:([^:]+):([^:]+):?([^]]*)\]',
            'parafraseo': r'\[CITA:parafraseo:([^:]+):([^:]+)\]',
            'larga': r'\[CITA:larga:([^:]+):([^:]+):?([^]]*)\]',
            'web': r'\[CITA:web:([^:]+):([^:]+)\]',
            'multiple': r'\[CITA:multiple:([^:]+):([^:]+)\]',
            'personal': r'\[CITA:personal:([^:]+):([^:]+):([^]]+)\]',
            'institucional': r'\[CITA:institucional:([^:]+):([^:]+)\]'
        }
        
        self.citation_examples = {
            'textual': '[CITA:textual:García:2020:45] - Cita textual con página',
            'parafraseo': '[CITA:parafraseo:López:2019] - Parafraseo de idea',
            'larga': '[CITA:larga:Martínez:2021:78] - Cita larga (más de 40 palabras)',
            'web': '[CITA:web:OMS:2023] - Fuente web institucional',
            'multiple': '[CITA:multiple:García y López:2020] - Múltiples autores',
            'personal': '[CITA:personal:Pérez:2022:comunicación personal] - Comunicación personal',
            'institucional': '[CITA:institucional:UNESCO:2023] - Organización/Institución'
        }
        
        # Sugerencias contextuales
        self.contextual_suggestions = {
            'introduccion': [
                "💡 Usa citas de autoridad para establecer contexto",
                "📊 Incluye estadísticas recientes con [CITA:web:Fuente:Año]",
                "🔍 Cita definiciones clave con [CITA:textual:Autor:Año:Página]"
            ],
            'marco_teorico': [
                "📚 Mínimo 5-7 citas por página",
                "🔄 Alterna entre citas textuales y parafraseo",
                "👥 Incluye múltiples perspectivas teóricas",
                "⚖️ Contrasta autores: [CITA:parafraseo:Autor1:Año] vs [CITA:parafraseo:Autor2:Año]"
            ],
            'metodologia': [
                "🔬 Cita metodologías establecidas",
                "📐 Referencias instrumentos validados",
                "📊 Incluye citas de estudios similares"
            ],
            'resultados': [
                "📈 Compara con hallazgos previos",
                "🔍 Usa citas para contextualizar datos",
                "⚠️ Evita sobre-citar en esta sección"
            ],
            'discusion': [
                "🔄 Relaciona resultados con teoría citada",
                "💭 Contrasta interpretaciones de autores",
                "🎯 Cita implicaciones y aplicaciones"
            ]
        }
    
    def procesar_citas_avanzado(self, texto, seccion_tipo=None):
        """Procesa citas con validación y formato avanzado"""
        # Primero validar formato
        citas_invalidas = self._validar_formato_citas(texto)
        if citas_invalidas:
            sugerencias = self._generar_sugerencias_correccion(citas_invalidas)
            messagebox.showwarning("⚠️ Citas con formato incorrecto", 
                f"Se encontraron {len(citas_invalidas)} citas mal formateadas:\n\n" + 
                "\n".join(sugerencias[:5]))
        
        # Procesar citas válidas
        texto_procesado = self._procesar_todas_citas(texto)
        
        # Análisis de densidad si es necesario
        if seccion_tipo:
            analisis = self.analizar_densidad_contextual(texto_procesado, seccion_tipo)
            if analisis['recomendacion'] != 'Óptimo':
                print(f"Densidad de citas en {seccion_tipo}: {analisis['recomendacion']}")
        
        return texto_procesado
    
    def _validar_formato_citas(self, texto):
        """Valida el formato de todas las citas"""
        citas_invalidas = []
        
        # Buscar patrones que parecen citas pero están mal formateados
        patrones_comunes_errores = [
            r'\(([^,]+),\s*(\d{4})\)',  # (Autor, Año) sin [CITA:]
            r'\[([^:]+):(\d{4})\]',      # [Autor:Año] sin CITA:
            r'\[CITA:([^]]+)\]',           # [CITA:...] pero sin estructura correcta
        ]
        
        for patron in patrones_comunes_errores:
            matches = re.finditer(patron, texto)
            for match in matches:
                # Verificar si no es una cita válida
                cita_texto = match.group(0)
                es_valida = False
                
                for tipo_patron in self.citation_patterns.values():
                    if re.match(tipo_patron.replace('\\[', '\\[').replace('\\]', '\\]'), cita_texto):
                        es_valida = True
                        break
                
                if not es_valida and not any(tipo in cita_texto for tipo in ['CITA:textual', 'CITA:parafraseo', 'CITA:larga', 'CITA:web', 'CITA:multiple']):
                    citas_invalidas.append(cita_texto)
        
        return citas_invalidas
    
    def _generar_sugerencias_correccion(self, citas_invalidas):
        """Genera sugerencias para corregir citas mal formateadas"""
        sugerencias = []
        
        for cita in citas_invalidas:
            if '(' in cita and ')' in cita:
                # Parece formato (Autor, Año)
                sugerencias.append(f"❌ '{cita}' → Usar [CITA:parafraseo:Autor:Año]")
            elif '[' in cita and ']' in cita and ':' in cita:
                # Parece intento de cita pero mal formateada
                sugerencias.append(f"❌ '{cita}' → Revisar formato: [CITA:tipo:Autor:Año]")
            else:
                sugerencias.append(f"❌ '{cita}' → Formato no reconocido")
        
        return sugerencias
    
    def _procesar_todas_citas(self, texto):
        """Procesa todas las citas en el texto"""
        def reemplazar_cita(match):
            cita_completa = match.group(0)
            contenido = cita_completa[6:-1]  # Quita [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) >= 3:
                tipo = partes[0]
                autor = partes[1]
                año = partes[2]
                extra = partes[3] if len(partes) > 3 else None
                
                return self._formatear_cita_apa_avanzada(tipo, autor, año, extra)
            
            return cita_completa
        
        # Procesar cada tipo de cita
        texto_procesado = texto
        for patron in self.citation_patterns.values():
            texto_procesado = re.sub(patron, reemplazar_cita, texto_procesado)
        
        return texto_procesado
    
    def _formatear_cita_apa_avanzada(self, tipo, autor, año, extra=None):
        """Formatea citas con reglas APA avanzadas"""
        # Limpiar espacios
        autor = autor.strip()
        año = año.strip()
        
        # Detectar múltiples autores
        if ' y ' in autor or ' & ' in autor or ',' in autor:
            # Formatear múltiples autores
            if autor.count(',') >= 2:
                # Tres o más autores
                primer_autor = autor.split(',')[0].strip()
                return f" ({primer_autor} et al., {año})"
            else:
                # Dos autores
                return f" ({autor}, {año})"
        
        # Formatear según tipo
        if tipo == 'textual':
            if extra:
                return f' "{texto_cita}" ({autor}, {año}, p. {extra})'
            else:
                return f' ({autor}, {año})'
                
        elif tipo == 'parafraseo':
            return f" ({autor}, {año})"
            
        elif tipo == 'larga':
            # Cita en bloque con sangría
            if extra:
                return f"\n\n\t({autor}, {año}, p. {extra})\n\n"
            else:
                return f"\n\n\t({autor}, {año})\n\n"
                
        elif tipo == 'web':
            return f" ({autor}, {año})"
            
        elif tipo == 'multiple':
            return f" ({autor}, {año})"
            
        elif tipo == 'personal':
            return f" ({autor}, {extra}, {año})"
            
        elif tipo == 'institucional':
            # Para organizaciones, usar nombre completo primera vez
            return f" ({autor}, {año})"
            
        else:
            return f" ({autor}, {año})"
    
    def analizar_densidad_contextual(self, texto, seccion_tipo):
        """Analiza densidad de citas según el tipo de sección"""
        palabras_total = len(texto.split())
        citas_total = texto.count('(') - texto.count('http')  # Aproximación
        
        if palabras_total == 0:
            return {'densidad': 0, 'recomendacion': 'Sin contenido'}
        
        densidad = citas_total / (palabras_total / 100)
        
        # Recomendaciones por sección
        densidades_optimas = {
            'introduccion': (1, 3),
            'marco_teorico': (3, 7),
            'metodologia': (2, 5),
            'resultados': (0.5, 2),
            'discusion': (2, 5),
            'conclusiones': (0.5, 2)
        }
        
        rango = densidades_optimas.get(seccion_tipo, (1, 5))
        
        if densidad < rango[0]:
            recomendacion = f"⚠️ Pocas citas ({densidad:.1f}/100 palabras) - Se recomienda {rango[0]}-{rango[1]}"
        elif densidad > rango[1]:
            recomendacion = f"⚠️ Demasiadas citas ({densidad:.1f}/100 palabras) - Se recomienda {rango[0]}-{rango[1]}"
        else:
            recomendacion = "✅ Densidad de citas óptima"
        
        return {
            'densidad': round(densidad, 2),
            'citas_total': citas_total,
            'palabras_total': palabras_total,
            'recomendacion': recomendacion,
            'rango_optimo': rango
        }
    
    def insertar_cita_inteligente(self, texto_seleccionado, tipo_cita, contexto_seccion=None):
        """Inserta citas con formato inteligente según contexto"""
        # Sugerir formato según contexto
        if contexto_seccion == 'marco_teorico' and len(texto_seleccionado) > 40:
            tipo_sugerido = 'larga'
            messagebox.showinfo("💡 Sugerencia", 
                "Texto largo detectado. Considera usar [CITA:larga:...] para citas de más de 40 palabras")
        else:
            tipo_sugerido = tipo_cita
        
        # Generar plantilla de cita
        plantillas = {
            'textual': '[CITA:textual:Apellido:Año:Página]',
            'parafraseo': '[CITA:parafraseo:Apellido:Año]',
            'larga': '[CITA:larga:Apellido:Año:Página]',
            'web': '[CITA:web:Organización:Año]',
            'multiple': '[CITA:multiple:Apellido1 y Apellido2:Año]',
            'personal': '[CITA:personal:Apellido:Año:comunicación personal]',
            'institucional': '[CITA:institucional:NombreCompleto:Año]'
        }
        
        return f"{texto_seleccionado} {plantillas.get(tipo_sugerido, plantillas['parafraseo'])}"
    
    def generar_lista_citas_usadas(self, texto):
        """Genera lista de todas las citas usadas para verificación"""
        citas_encontradas = []
        
        for tipo, patron in self.citation_patterns.items():
            matches = re.finditer(patron, texto)
            for match in matches:
                grupos = match.groups()
                if len(grupos) >= 2:
                    cita_info = {
                        'tipo': tipo,
                        'autor': grupos[0],
                        'año': grupos[1],
                        'extra': grupos[2] if len(grupos) > 2 and grupos[2] else None,
                        'texto_completo': match.group(0)
                    }
                    citas_encontradas.append(cita_info)
        
        # Ordenar por autor y año
        citas_encontradas.sort(key=lambda x: (x['autor'], x['año']))
        
        return citas_encontradas
    
    def validar_coherencia_citas_referencias(self, citas_usadas, referencias):
        """Valida que todas las citas tengan su referencia correspondiente"""
        autores_citados = set()
        for cita in citas_usadas:
            # Extraer apellido principal
            autor = cita['autor'].split(',')[0].split(' y ')[0].split(' & ')[0].strip()
            autores_citados.add((autor, cita['año']))
        
        autores_referencias = set()
        for ref in referencias:
            autor = ref['autor'].split(',')[0].strip()
            autores_referencias.add((autor, ref['año']))
        
        # Encontrar discrepancias
        citas_sin_referencia = autores_citados - autores_referencias
        referencias_sin_citar = autores_referencias - autores_citados
        
        return {
            'citas_sin_referencia': list(citas_sin_referencia),
            'referencias_sin_citar': list(referencias_sin_citar),
            'coherencia_completa': len(citas_sin_referencia) == 0 and len(referencias_sin_citar) == 0
        }
    
    def exportar_informe_citas(self, texto, nombre_archivo="informe_citas.txt"):
        """Exporta un informe completo de citas del documento"""
        citas = self.generar_lista_citas_usadas(texto)
        
        informe = "INFORME DE CITAS DEL DOCUMENTO\n"
        informe += "="*50 + "\n\n"
        
        # Resumen
        informe += f"Total de citas: {len(citas)}\n"
        informe += f"Autores únicos: {len(set(c['autor'] for c in citas))}\n\n"
        
        # Por tipo
        informe += "CITAS POR TIPO:\n"
        for tipo in self.citation_patterns.keys():
            cantidad = len([c for c in citas if c['tipo'] == tipo])
            if cantidad > 0:
                informe += f"- {tipo.capitalize()}: {cantidad}\n"
        
        informe += "\nDETALLE DE CITAS:\n"
        informe += "-"*50 + "\n"
        
        for i, cita in enumerate(citas, 1):
            informe += f"\n{i}. {cita['autor']} ({cita['año']})\n"
            informe += f"   Tipo: {cita['tipo']}\n"
            if cita['extra']:
                informe += f"   Info adicional: {cita['extra']}\n"
            informe += f"   Formato original: {cita['texto_completo']}\n"
        
        return informe
