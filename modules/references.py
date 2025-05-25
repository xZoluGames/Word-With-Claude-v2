"""
Ejemplo de cómo deben quedar los archivos con imports limpios y docstrings completos
"""

# modules/references.py - VERSION MEJORADA
"""
Gestión de referencias bibliográficas - Sistema completo de referencias APA

Este módulo proporciona funcionalidad completa para gestionar referencias
bibliográficas siguiendo el formato APA 7ma edición.

Classes:
    ReferenceManager: Gestor principal de referencias bibliográficas

Example:
    >>> ref_manager = ReferenceManager()
    >>> ref_data = {
    ...     'tipo': 'Libro',
    ...     'autor': 'García, J.',
    ...     'año': '2023',
    ...     'titulo': 'Python Avanzado',
    ...     'fuente': 'Editorial Tech'
    ... }
    >>> ref_manager.agregar_referencia(ref_data)
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.logger import get_logger
from utils.validators import Validators, ReferenceValidator, validar_y_sanitizar_entrada

logger = get_logger('ReferenceManager')
class ReferenceManager:
    """
    Gestor de referencias bibliográficas con soporte completo para APA.
    
    Attributes:
        referencias (List[Dict]): Lista de referencias almacenadas
        tipos_referencia (Dict[str, Dict]): Tipos de referencia soportados
    
    Methods:
        agregar_referencia: Agrega una nueva referencia con validación
        eliminar_referencia: Elimina una referencia por índice
        generar_apa_format: Genera formato APA para una referencia
        ordenar_referencias: Ordena las referencias según criterio
        buscar_referencias: Busca referencias por término
    """
    def __init__(self):
        """Inicializa el gestor de referencias."""
        logger.info("Inicializando ReferenceManager")
        self.referencias: List[Dict] = []
        self.tipos_referencia = self._get_tipos_referencia()
    
    def _get_tipos_referencia(self) -> Dict[str, Dict]:
        """
        Obtiene los tipos de referencia soportados.
        
        Returns:
            Dict[str, Dict]: Diccionario con tipos de referencia y sus campos
        """
        return {
            'Libro': {
                'campos': ['autor', 'año', 'titulo', 'editorial', 'ciudad'],
                'formato': '{autor} ({año}). {titulo}. {editorial}.',
                'campos_requeridos': ['autor', 'año', 'titulo', 'editorial']
            },
            'Artículo': {
                'campos': ['autor', 'año', 'titulo', 'revista', 'volumen', 'paginas'],
                'formato': '{autor} ({año}). {titulo}. {revista}, {volumen}, {paginas}.',
                'campos_requeridos': ['autor', 'año', 'titulo', 'revista']
            },
            'Web': {
                'campos': ['autor', 'año', 'titulo', 'sitio_web', 'url', 'fecha_acceso'],
                'formato': '{autor} ({año}). {titulo}. {sitio_web}. {url}',
                'campos_requeridos': ['autor', 'año', 'titulo', 'url']
            },
            'Tesis': {
                'campos': ['autor', 'año', 'titulo', 'tipo_tesis', 'institucion'],
                'formato': '{autor} ({año}). {titulo} ({tipo_tesis}). {institucion}.',
                'campos_requeridos': ['autor', 'año', 'titulo', 'institucion']
            }
        }
    def exportar_bibtex(self, archivo: str = None) -> str:
        """
        Exporta referencias en formato BibTeX.
        
        Args:
            archivo: Ruta del archivo a guardar (opcional)
            
        Returns:
            str: Contenido BibTeX
        """
        bibtex_entries = []
        
        for i, ref in enumerate(self.referencias):
            # Determinar tipo BibTeX
            tipo_map = {
                'Libro': 'book',
                'Artículo': 'article',
                'Web': 'misc',
                'Tesis': 'phdthesis',
                'Conferencia': 'inproceedings',
                'Informe': 'techreport'
            }
            
            bibtex_type = tipo_map.get(ref.get('tipo', 'Libro'), 'misc')
            
            # Generar clave única
            autor_key = ref['autor'].split(',')[0].replace(' ', '').lower()
            year_key = ref.get('año', 'nodate')
            entry_key = f"{autor_key}{year_key}{i}"
            
            # Construir entrada BibTeX
            entry = f"@{bibtex_type}{{{entry_key},\n"
            entry += f"  author = {{{ref['autor']}}},\n"
            entry += f"  title = {{{ref['titulo']}}},\n"
            entry += f"  year = {{{ref['año']}}},\n"
            
            if bibtex_type == 'book':
                entry += f"  publisher = {{{ref.get('fuente', 'Unknown')}}},\n"
            elif bibtex_type == 'article':
                entry += f"  journal = {{{ref.get('fuente', 'Unknown')}}},\n"
            elif bibtex_type == 'misc' and ref.get('tipo') == 'Web':
                entry += f"  url = {{{ref.get('fuente', '')}}},\n"
                entry += f"  note = {{Accessed: {datetime.now().strftime('%Y-%m-%d')}}},\n"
            
            entry = entry.rstrip(',\n') + "\n}"
            bibtex_entries.append(entry)
        
        bibtex_content = '\n\n'.join(bibtex_entries)
        
        # Guardar si se especifica archivo
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)
            logger.info(f"Referencias exportadas a BibTeX: {archivo}")
        
        return bibtex_content

    def fusionar_referencias(self, otras_referencias: List[Dict]) -> int:
        """
        Fusiona referencias evitando duplicados.
        
        Args:
            otras_referencias: Lista de referencias a fusionar
            
        Returns:
            int: Número de referencias agregadas
        """
        agregadas = 0
        
        for ref in otras_referencias:
            # Verificar si ya existe
            existe = False
            for ref_existente in self.referencias:
                if (ref_existente['autor'] == ref.get('autor') and
                    ref_existente['año'] == ref.get('año') and
                    ref_existente['titulo'] == ref.get('titulo')):
                    existe = True
                    break
            
            if not existe:
                try:
                    self.agregar_referencia(ref)
                    agregadas += 1
                except Exception as e:
                    logger.warning(f"No se pudo agregar referencia: {e}")
        
        logger.info(f"Referencias fusionadas: {agregadas} de {len(otras_referencias)}")
        return agregadas

    def detectar_duplicados(self) -> List[Tuple[int, int]]:
        """
        Detecta posibles referencias duplicadas.
        
        Returns:
            List[Tuple[int, int]]: Pares de índices de posibles duplicados
        """
        duplicados = []
        
        for i in range(len(self.referencias)):
            for j in range(i + 1, len(self.referencias)):
                ref1 = self.referencias[i]
                ref2 = self.referencias[j]
                
                # Comparar por similitud
                if self._son_duplicados(ref1, ref2):
                    duplicados.append((i, j))
        
        return duplicados

    def _son_duplicados(self, ref1: Dict, ref2: Dict) -> bool:
        """
        Determina si dos referencias son duplicadas.
        
        Usa comparación fuzzy para detectar variaciones menores.
        """
        # Comparación exacta primero
        if (ref1['autor'] == ref2['autor'] and
            ref1['año'] == ref2['año'] and
            ref1['titulo'] == ref2['titulo']):
            return True
        
        # Comparación fuzzy (requiere instalar python-Levenshtein)
        try:
            from difflib import SequenceMatcher
            
            # Similitud de autor
            autor_sim = SequenceMatcher(None, ref1['autor'], ref2['autor']).ratio()
            
            # Similitud de título
            titulo_sim = SequenceMatcher(None, 
                                    ref1['titulo'].lower(), 
                                    ref2['titulo'].lower()).ratio()
            
            # Mismo año y alta similitud en autor y título
            if (ref1['año'] == ref2['año'] and 
                autor_sim > 0.85 and titulo_sim > 0.85):
                return True
                
        except ImportError:
            pass
        
        return False
    def agregar_referencia(self, ref_data: Dict[str, str]) -> Dict[str, any]:
        """
        Agrega una nueva referencia con validación completa.
        
        Args:
            ref_data: Diccionario con los datos de la referencia
            
        Returns:
            Dict: La referencia agregada con ID y metadatos
            
        Raises:
            ValueError: Si hay errores de validación
        """
        logger.debug(f"Agregando referencia: {ref_data.get('titulo', 'Sin título')}")
        
        # Sanitizar entradas
        for campo in ['autor', 'titulo', 'fuente']:
            if campo in ref_data:
                ref_data[campo], errores = validar_y_sanitizar_entrada(
                    ref_data[campo], 
                    tipo=campo if campo in ['autor', 'titulo'] else 'general'
                )
                if errores:
                    raise ValueError(f"Error en {campo}: {'; '.join(errores)}")
        
        # Validación completa usando el nuevo sistema
        errores = ReferenceValidator.validar_referencia_completa(ref_data)
        if errores:
            logger.warning(f"Errores de validación: {errores}")
            raise ValueError("Errores de validación:\n" + "\n".join(errores))
        
        # Si es una URL, validar específicamente
        if ref_data.get('tipo') == 'Web' and 'fuente' in ref_data:
            es_valida, error = Validators.validar_url(ref_data['fuente'])
            if not es_valida:
                raise ValueError(f"URL inválida: {error}")
        
        # Crear referencia con metadatos
        referencia = {
            'id': len(self.referencias) + 1,
            'fecha_agregada': datetime.now().isoformat(),
            'tipo': ref_data.get('tipo', 'Libro'),
            **ref_data
        }
        
        self.referencias.append(referencia)
        logger.info(f"Referencia agregada: ID={referencia['id']}, Tipo={referencia['tipo']}")
        
        return referencia
    
    def eliminar_referencia(self, index=-1):
        """Elimina una referencia por índice (por defecto la última)"""
        if not self.referencias:
            raise ValueError("No hay referencias para eliminar")
        
        if index == -1:
            index = len(self.referencias) - 1
        
        if 0 <= index < len(self.referencias):
            referencia_eliminada = self.referencias.pop(index)
            return referencia_eliminada
        else:
            raise ValueError("Índice de referencia inválido")
    
    def editar_referencia(self, index, nuevos_datos):
        """Edita una referencia existente"""
        if 0 <= index < len(self.referencias):
            self.referencias[index].update(nuevos_datos)
            self.referencias[index]['fecha_modificada'] = datetime.now().isoformat()
            return self.referencias[index]
        else:
            raise ValueError("Índice de referencia inválido")
    
    def generar_apa_format(self, referencia):
        """Genera formato APA para una referencia"""
        tipo = referencia.get('tipo', 'Libro')
        
        if tipo == 'Libro':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Editorial desconocida')}."
        elif tipo == 'Artículo':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Revista desconocida')}."
        elif tipo == 'Web':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Sitio web')}."
        elif tipo == 'Tesis':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']} (Tesis). {referencia.get('fuente', 'Institución')}."
        else:
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', '')}."
    
    def ordenar_referencias(self, criterio='autor'):
        """Ordena las referencias según el criterio especificado"""
        if criterio == 'autor':
            self.referencias.sort(key=lambda x: x['autor'].lower())
        elif criterio == 'año':
            self.referencias.sort(key=lambda x: int(x['año']), reverse=True)
        elif criterio == 'titulo':
            self.referencias.sort(key=lambda x: x['titulo'].lower())
        elif criterio == 'tipo':
            self.referencias.sort(key=lambda x: x.get('tipo', 'Libro').lower())
    
    def buscar_referencias(self, termino):
        """Busca referencias por término en autor, título o fuente"""
        termino = termino.lower()
        resultados = []
        
        for i, ref in enumerate(self.referencias):
            if (termino in ref['autor'].lower() or 
                termino in ref['titulo'].lower() or 
                termino in ref.get('fuente', '').lower()):
                resultados.append((i, ref))
        
        return resultados
    
    def exportar_referencias(self, formato='apa'):
        """Exporta todas las referencias en el formato especificado"""
        if formato == 'apa':
            referencias_formateadas = []
            for ref in sorted(self.referencias, key=lambda x: x['autor'].lower()):
                referencias_formateadas.append(self.generar_apa_format(ref))
            return '\n\n'.join(referencias_formateadas)
        else:
            return str(self.referencias)
    
    def importar_referencias_bibtex(self, contenido_bibtex):
        """Importa referencias desde formato BibTeX (básico)"""
        # Implementación básica para BibTeX
        entradas = re.findall(r'@\w+\{[^}]+\}', contenido_bibtex, re.DOTALL)
        referencias_importadas = 0
        
        for entrada in entradas:
            try:
                ref_data = self._parsear_bibtex_entrada(entrada)
                if ref_data:
                    self.agregar_referencia(ref_data)
                    referencias_importadas += 1
            except Exception as e:
                print(f"Error importando entrada: {e}")
        
        return referencias_importadas
    
    def validar_referencias_citadas(self, texto_documento):
        """Valida que todas las citas tengan su referencia correspondiente"""
        from .citations import CitationProcessor
        
        processor = CitationProcessor()
        autores_citados = processor.extraer_autores_citados(texto_documento)
        autores_referencias = [ref['autor'] for ref in self.referencias]
        
        citas_sin_referencia = []
        for autor in autores_citados:
            if not any(autor.lower() in ref_autor.lower() for ref_autor in autores_referencias):
                citas_sin_referencia.append(autor)
        
        referencias_sin_citar = []
        for ref in self.referencias:
            autor_ref = ref['autor'].split(',')[0]  # Tomar solo el apellido
            if not any(autor_ref.lower() in autor.lower() for autor in autores_citados):
                referencias_sin_citar.append(ref['autor'])
        
        return {
            'citas_sin_referencia': citas_sin_referencia,
            'referencias_sin_citar': referencias_sin_citar,
            'total_citas': len(autores_citados),
            'total_referencias': len(self.referencias)
        }
    
    def generar_estadisticas(self):
        """Genera estadísticas de las referencias"""
        if not self.referencias:
            return {'total': 0, 'mensaje': 'No hay referencias agregadas'}
        
        tipos_count = {}
        años_count = {}
        
        for ref in self.referencias:
            tipo = ref.get('tipo', 'Libro')
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
            año = ref.get('año', 'Sin año')
            años_count[año] = años_count.get(año, 0) + 1
        
        año_mas_reciente = max([int(ref['año']) for ref in self.referencias if ref['año'].isdigit()])
        año_mas_antiguo = min([int(ref['año']) for ref in self.referencias if ref['año'].isdigit()])
        
        return {
            'total': len(self.referencias),
            'por_tipo': tipos_count,
            'por_año': años_count,
            'rango_años': f"{año_mas_antiguo}-{año_mas_reciente}",
            'año_mas_reciente': año_mas_reciente,
            'tipo_mas_usado': max(tipos_count.items(), key=lambda x: x[1])[0] if tipos_count else 'N/A'
        }
    
    def _validar_formato_autor(self, autor: str) -> bool:
        """
        Valida que el autor tenga formato APA correcto.
        
        Args:
            autor: String con el autor
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        es_valido, _ = Validators.validar_autor(autor)
        return es_valido
    
    def _parsear_bibtex_entrada(self, entrada):
        """Parsea una entrada BibTeX y extrae los datos"""
        # Implementación básica para parsear BibTeX
        lineas = entrada.split('\n')
        ref_data = {}
        
        for linea in lineas:
            if '=' in linea:
                campo, valor = linea.split('=', 1)
                campo = campo.strip()
                valor = valor.strip().strip(',').strip('{}').strip('"')
                
                if campo == 'author':
                    ref_data['autor'] = valor
                elif campo == 'year':
                    ref_data['año'] = valor
                elif campo == 'title':
                    ref_data['titulo'] = valor
                elif campo == 'publisher':
                    ref_data['fuente'] = valor
                elif campo == 'journal':
                    ref_data['fuente'] = valor
        
        return ref_data if len(ref_data) >= 3 else None
    
    def limpiar_referencias(self):
        """Limpia todas las referencias"""
        cantidad = len(self.referencias)
        self.referencias.clear()
        return cantidad
    
    def duplicar_referencia(self, index):
        """Duplica una referencia existente"""
        if 0 <= index < len(self.referencias):
            ref_original = self.referencias[index].copy()
            ref_original['id'] = len(self.referencias) + 1
            ref_original['titulo'] = f"{ref_original['titulo']} (Copia)"
            ref_original['fecha_agregada'] = datetime.now().isoformat()
            self.referencias.append(ref_original)
            return ref_original
        else:
            raise ValueError("Índice de referencia inválido")