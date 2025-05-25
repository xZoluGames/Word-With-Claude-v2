
from utils.logger import get_logger

logger = get_logger("sections")

"""
Gestión dinámica de secciones - Sistema completo de administración de secciones
"""

import customtkinter as ctk
from tkinter import messagebox
import re
from copy import deepcopy

class SectionManager:
    def __init__(self):
        self.secciones_disponibles = {}
        self.secciones_activas = []
        self.secciones_base = self._get_secciones_base()
        self.orden_personalizado = []
    
    def _get_secciones_base(self):
        """Define las secciones base del sistema (extraídas del código original)"""
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "introduccion": {
                "titulo": "🔍 Introducción", 
                "instruccion": "Presenta el tema, contexto e importancia",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "capitulo1": {
                "titulo": "📖 CAPÍTULO I", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "planteamiento": {
                "titulo": "❓ Planteamiento del Problema", 
                "instruccion": "Define el problema a investigar",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "preguntas": {
                "titulo": "❔ Preguntas de Investigación", 
                "instruccion": "Pregunta general y específicas",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "delimitaciones": {
                "titulo": "📏 Delimitaciones", 
                "instruccion": "Límites del estudio (temporal, espacial, conceptual)",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "justificacion": {
                "titulo": "💡 Justificación", 
                "instruccion": "Explica por qué es importante investigar",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "objetivos": {
                "titulo": "🎯 Objetivos", 
                "instruccion": "General y específicos (verbos en infinitivo)",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "capitulo2": {
                "titulo": "📚 CAPÍTULO II - ESTADO DEL ARTE", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "marco_teorico": {
                "titulo": "📖 Marco Teórico", 
                "instruccion": "Base teórica y antecedentes (USA CITAS)",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "capitulo3": {
                "titulo": "🔬 CAPÍTULO III", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "metodologia": {
                "titulo": "⚙️ Marco Metodológico", 
                "instruccion": "Tipo de estudio y técnicas de recolección",
                "requerida": True,
                "capitulo": False,
                "base": True
            },
            "capitulo4": {
                "titulo": "🛠️ CAPÍTULO IV - DESARROLLO", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "desarrollo": {
                "titulo": "⚙️ Desarrollo", 
                "instruccion": "Proceso de investigación paso a paso",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "capitulo5": {
                "titulo": "📊 CAPÍTULO V - ANÁLISIS DE DATOS", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "resultados": {
                "titulo": "📊 Resultados", 
                "instruccion": "Datos obtenidos (gráficos, tablas)",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "analisis_datos": {
                "titulo": "📈 Análisis de Datos", 
                "instruccion": "Interpretación de resultados",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "capitulo6": {
                "titulo": "💬 CAPÍTULO VI", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True,
                "base": True
            },
            "discusion": {
                "titulo": "💬 Discusión", 
                "instruccion": "Confronta resultados con teoría",
                "requerida": False,
                "capitulo": False,
                "base": True
            },
            "conclusiones": {
                "titulo": "✅ Conclusiones", 
                "instruccion": "Hallazgos principales y respuestas a objetivos",
                "requerida": True,
                "capitulo": False,
                "base": True
            }
        }
    
    def inicializar_secciones(self):
        """Inicializa las secciones con la configuración base"""
        self.secciones_disponibles = deepcopy(self.secciones_base)
        self.secciones_activas = list(self.secciones_disponibles.keys())
        return self.secciones_disponibles
    
    def agregar_seccion(self, seccion_id, seccion_data):
        """Agrega una nueva sección personalizada"""
        # Validar ID único
        if seccion_id in self.secciones_disponibles:
            raise ValueError(f"Ya existe una sección con ID: {seccion_id}")
        
        # Validar formato del ID
        if not re.match(r'^[a-z0-9_]+$', seccion_id):
            raise ValueError("El ID debe contener solo letras minúsculas, números y guiones bajos")
        
        # Validar campos requeridos
        campos_requeridos = ['titulo', 'instruccion']
        for campo in campos_requeridos:
            if not seccion_data.get(campo, '').strip():
                raise ValueError(f"El campo '{campo}' es requerido")
        
        # Completar datos por defecto
        seccion_completa = {
            'titulo': seccion_data['titulo'],
            'instruccion': seccion_data['instruccion'],
            'requerida': seccion_data.get('requerida', False),
            'capitulo': seccion_data.get('capitulo', False),
            'base': False,  # Las secciones personalizadas no son base
            'personalizada': True,
            'orden': len(self.secciones_disponibles)
        }
        
        self.secciones_disponibles[seccion_id] = seccion_completa
        self.secciones_activas.append(seccion_id)
        
        return seccion_completa
    
    def eliminar_seccion(self, seccion_id):
        """Elimina una sección (solo si no es requerida ni base)"""
        if seccion_id not in self.secciones_disponibles:
            raise ValueError(f"La sección '{seccion_id}' no existe")
        
        seccion = self.secciones_disponibles[seccion_id]
        
        # Proteger secciones requeridas
        if seccion.get('requerida', False):
            raise ValueError(f"No se puede eliminar la sección requerida: {seccion['titulo']}")
        
        # Proteger secciones base críticas (opcional)
        secciones_criticas = ['introduccion', 'objetivos', 'marco_teorico', 'metodologia', 'conclusiones']
        if seccion_id in secciones_criticas:
            raise ValueError(f"No se puede eliminar la sección crítica: {seccion['titulo']}")
        
        # Eliminar de diccionario y lista activa
        del self.secciones_disponibles[seccion_id]
        if seccion_id in self.secciones_activas:
            self.secciones_activas.remove(seccion_id)
        
        return seccion
    
    def editar_seccion(self, seccion_id, nuevos_datos):
        """Edita una sección existente"""
        if seccion_id not in self.secciones_disponibles:
            raise ValueError(f"La sección '{seccion_id}' no existe")
        
        seccion = self.secciones_disponibles[seccion_id]
        
        # Permitir edición limitada de secciones base
        if seccion.get('base', False):
            campos_editables = ['instruccion']  # Solo instrucción editable en secciones base
            for campo in nuevos_datos:
                if campo not in campos_editables:
                    raise ValueError(f"No se puede editar el campo '{campo}' en secciones base")
        
        # Actualizar datos
        seccion.update(nuevos_datos)
        return seccion
    
    def reordenar_secciones(self, nuevo_orden):
        """Reordena las secciones según una nueva lista de IDs"""
        # Validar que todos los IDs existan
        for seccion_id in nuevo_orden:
            if seccion_id not in self.secciones_disponibles:
                raise ValueError(f"La sección '{seccion_id}' no existe")
        
        # Validar que no falten secciones
        if set(nuevo_orden) != set(self.secciones_activas):
            raise ValueError("El nuevo orden debe incluir todas las secciones activas")
        
        self.secciones_activas = nuevo_orden
        return self.secciones_activas
    
    def mover_seccion(self, seccion_id, direccion):
        """Mueve una sección hacia arriba o abajo"""
        if seccion_id not in self.secciones_activas:
            raise ValueError(f"La sección '{seccion_id}' no está activa")
        
        index_actual = self.secciones_activas.index(seccion_id)
        
        if direccion == 'arriba' and index_actual > 0:
            # Intercambiar con la anterior
            self.secciones_activas[index_actual], self.secciones_activas[index_actual - 1] = \
            self.secciones_activas[index_actual - 1], self.secciones_activas[index_actual]
            return index_actual - 1
        elif direccion == 'abajo' and index_actual < len(self.secciones_activas) - 1:
            # Intercambiar con la siguiente
            self.secciones_activas[index_actual], self.secciones_activas[index_actual + 1] = \
            self.secciones_activas[index_actual + 1], self.secciones_activas[index_actual]
            return index_actual + 1
        else:
            raise ValueError(f"No se puede mover la sección '{direccion}'")
    
    def activar_seccion(self, seccion_id):
        """Activa una sección desactivada"""
        if seccion_id not in self.secciones_disponibles:
            raise ValueError(f"La sección '{seccion_id}' no existe")
        
        if seccion_id not in self.secciones_activas:
            self.secciones_activas.append(seccion_id)
        
        return True
    
    def desactivar_seccion(self, seccion_id):
        """Desactiva una sección (solo si no es requerida)"""
        if seccion_id not in self.secciones_disponibles:
            raise ValueError(f"La sección '{seccion_id}' no existe")
        
        seccion = self.secciones_disponibles[seccion_id]
        if seccion.get('requerida', False):
            raise ValueError(f"No se puede desactivar la sección requerida: {seccion['titulo']}")
        
        if seccion_id in self.secciones_activas:
            self.secciones_activas.remove(seccion_id)
        
        return True
    
    def obtener_secciones_por_tipo(self, tipo):
        """Obtiene secciones filtradas por tipo"""
        if tipo == 'capitulos':
            return {k: v for k, v in self.secciones_disponibles.items() if v.get('capitulo', False)}
        elif tipo == 'contenido':
            return {k: v for k, v in self.secciones_disponibles.items() if not v.get('capitulo', False)}
        elif tipo == 'requeridas':
            return {k: v for k, v in self.secciones_disponibles.items() if v.get('requerida', False)}
        elif tipo == 'personalizadas':
            return {k: v for k, v in self.secciones_disponibles.items() if v.get('personalizada', False)}
        elif tipo == 'base':
            return {k: v for k, v in self.secciones_disponibles.items() if v.get('base', False)}
        else:
            return self.secciones_disponibles
    
    def validar_estructura(self):
        """Valida que la estructura de secciones sea coherente"""
        errores = []
        advertencias = []
        
        # Verificar secciones requeridas
        secciones_requeridas = [k for k, v in self.secciones_disponibles.items() if v.get('requerida', False)]
        for seccion_id in secciones_requeridas:
            if seccion_id not in self.secciones_activas:
                errores.append(f"Sección requerida desactivada: {self.secciones_disponibles[seccion_id]['titulo']}")
        
        # Verificar orden lógico básico
        orden_logico = ['introduccion', 'planteamiento', 'objetivos', 'marco_teorico', 'metodologia', 'conclusiones']
        indices = {}
        for seccion in orden_logico:
            if seccion in self.secciones_activas:
                indices[seccion] = self.secciones_activas.index(seccion)
        
        orden_indices = sorted(indices.items(), key=lambda x: x[1])
        orden_actual = [item[0] for item in orden_indices]
        
        if orden_actual != [s for s in orden_logico if s in orden_actual]:
            advertencias.append("El orden de las secciones principales podría no ser el más lógico")
        
        return {
            'errores': errores,
            'advertencias': advertencias,
            'valida': len(errores) == 0
        }
    
    def generar_estadisticas(self):
        """Genera estadísticas de las secciones"""
        total_disponibles = len(self.secciones_disponibles)
        total_activas = len(self.secciones_activas)
        
        por_tipo = {
            'capitulos': len(self.obtener_secciones_por_tipo('capitulos')),
            'contenido': len(self.obtener_secciones_por_tipo('contenido')),
            'requeridas': len(self.obtener_secciones_por_tipo('requeridas')),
            'personalizadas': len(self.obtener_secciones_por_tipo('personalizadas'))
        }
        
        return {
            'total_disponibles': total_disponibles,
            'total_activas': total_activas,
            'inactivas': total_disponibles - total_activas,
            'por_tipo': por_tipo,
            'porcentaje_activas': round((total_activas / total_disponibles) * 100, 1) if total_disponibles > 0 else 0
        }
    
    def exportar_estructura(self):
        """Exporta la estructura actual de secciones"""
        return {
            'secciones_disponibles': deepcopy(self.secciones_disponibles),
            'secciones_activas': self.secciones_activas.copy(),
            'estadisticas': self.generar_estadisticas()
        }
    
    def importar_estructura(self, estructura):
        """Importa una estructura de secciones"""
        if 'secciones_disponibles' in estructura:
            self.secciones_disponibles = estructura['secciones_disponibles']
        
        if 'secciones_activas' in estructura:
            self.secciones_activas = estructura['secciones_activas']
        
        # Validar integridad después de importar
        return self.validar_estructura()
    
    def restablecer_estructura_base(self):
        """Restablece la estructura a la configuración base"""
        self.secciones_disponibles = deepcopy(self.secciones_base)
        self.secciones_activas = list(self.secciones_disponibles.keys())
        return True