#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.logger import get_logger

logger = get_logger("template_manager")

"""
Template Manager - Gestor de plantillas para proyectos académicos
Maneja plantillas base, aplicación de formatos predefinidos y gestión de estructuras
"""

import json
import os
from datetime import datetime
from tkinter import messagebox, filedialog
from copy import deepcopy

class TemplateManager:
    def __init__(self):
        self.plantillas_disponibles = {}
        self.plantilla_activa = None
        self.ruta_plantillas = self._obtener_ruta_plantillas()
        
        # Inicializar plantillas base
        self._cargar_plantillas_base()
        self._buscar_plantillas_externas()
    
    def _obtener_ruta_plantillas(self):
        """Obtiene la ruta donde se almacenan las plantillas"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            plantillas_dir = os.path.join(script_dir, "plantillas")
            
            # Crear directorio si no existe
            if not os.path.exists(plantillas_dir):
                os.makedirs(plantillas_dir)
            
            return plantillas_dir
        except Exception as e:
            print(f"Error creando directorio de plantillas: {e}")
            return None
    
    def _cargar_plantillas_base(self):
        """Carga las plantillas base del sistema"""
        # Plantilla base extraída del documento FORMATO DE TRABAJ0 3º AÑO.docx
        plantilla_tercer_ano = {
            'id': 'tercer_ano_bti',
            'nombre': 'Plantilla 3º AÑO BTI',
            'descripcion': 'Formato base para proyectos de Tercer año BTI - Colegio Privado Divina Esperanza',
            'version': '1.0',
            'fecha_creacion': '2025-01-30',
            'tipo': 'base',
            'datos_predefinidos': {
                'institucion': 'COLEGIO PRIVADO DIVINA ESPERANZA',
                'ciclo': 'Tercer año',
                'curso': '3 BTI',
                'enfasis': 'Tecnología',
                'director': 'Cristina Raichakowski',
                'categoria': 'Tecnología'
            },
            'estructura_secciones': {
                'incluir_agradecimientos': True,
                'incluir_resumen': True,
                'incluir_indice': True,
                'incluir_tabla_ilustraciones': True,
                'estructura_capitulos': [
                    {
                        'id': 'capitulo1',
                        'titulo': 'CAPÍTULO I',
                        'secciones': ['introduccion', 'planteamiento', 'preguntas', 'delimitaciones', 'justificacion', 'objetivos']
                    },
                    {
                        'id': 'capitulo2',
                        'titulo': 'CAPÍTULO II - ESTADO DEL ARTE',
                        'secciones': ['marco_teorico']
                    },
                    {
                        'id': 'capitulo3',
                        'titulo': 'CAPÍTULO III',
                        'secciones': ['metodologia']
                    },
                    {
                        'id': 'capitulo4',
                        'titulo': 'CAPÍTULO IV - DESARROLLO',
                        'secciones': ['desarrollo']
                    },
                    {
                        'id': 'capitulo5',
                        'titulo': 'CAPÍTULO V - ANÁLISIS DE DATOS',
                        'secciones': ['resultados', 'analisis_datos']
                    },
                    {
                        'id': 'capitulo6',
                        'titulo': 'CAPÍTULO VI',
                        'secciones': ['discusion']
                    }
                ]
            },
            'formato_config': {
                'fuente_texto': 'Times New Roman',
                'tamaño_texto': 12,
                'fuente_titulo': 'Times New Roman',
                'tamaño_titulo': 14,
                'interlineado': 2.0,
                'margen': 2.54,
                'justificado': True,
                'sangria': True
            },
            'opciones_generacion': {
                'incluir_portada': True,
                'incluir_indice': True,
                'incluir_agradecimientos': True,
                'numeracion_paginas': True
            }
        }
        
        # Plantilla genérica básica
        plantilla_generica = {
            'id': 'generica_basica',
            'nombre': 'Plantilla Genérica',
            'descripcion': 'Plantilla básica para proyectos académicos generales',
            'version': '1.0',
            'fecha_creacion': datetime.now().isoformat(),
            'tipo': 'base',
            'datos_predefinidos': {
                'categoria': 'Ciencia'
            },
            'estructura_secciones': {
                'incluir_agradecimientos': False,
                'incluir_resumen': True,
                'incluir_indice': True,
                'incluir_tabla_ilustraciones': False
            },
            'formato_config': {
                'fuente_texto': 'Times New Roman',
                'tamaño_texto': 12,
                'fuente_titulo': 'Times New Roman',
                'tamaño_titulo': 14,
                'interlineado': 2.0,
                'margen': 2.54,
                'justificado': True,
                'sangria': True
            },
            'opciones_generacion': {
                'incluir_portada': True,
                'incluir_indice': True,
                'incluir_agradecimientos': False,
                'numeracion_paginas': True
            }
        }
        
        # Agregar plantillas base
        self.plantillas_disponibles[plantilla_tercer_ano['id']] = plantilla_tercer_ano
        self.plantillas_disponibles[plantilla_generica['id']] = plantilla_generica
    
    def _buscar_plantillas_externas(self):
        """Busca plantillas externas en el directorio de plantillas"""
        if not self.ruta_plantillas or not os.path.exists(self.ruta_plantillas):
            return
        
        try:
            for archivo in os.listdir(self.ruta_plantillas):
                if archivo.endswith('.json'):
                    ruta_archivo = os.path.join(self.ruta_plantillas, archivo)
                    try:
                        with open(ruta_archivo, 'r', encoding='utf-8') as f:
                            plantilla = json.load(f)
                        
                        # Validar estructura de plantilla
                        if self._validar_plantilla(plantilla):
                            plantilla['tipo'] = 'externa'
                            self.plantillas_disponibles[plantilla['id']] = plantilla
                    except Exception as e:
                        print(f"Error cargando plantilla {archivo}: {e}")
        except Exception as e:
            print(f"Error buscando plantillas externas: {e}")
    
    def _validar_plantilla(self, plantilla):
        """Valida que una plantilla tenga la estructura correcta"""
        campos_requeridos = ['id', 'nombre', 'descripcion', 'version']
        return all(campo in plantilla for campo in campos_requeridos)
    
    def obtener_plantillas_disponibles(self):
        """Retorna lista de plantillas disponibles"""
        return {
            id_plantilla: {
                'nombre': plantilla['nombre'],
                'descripcion': plantilla['descripcion'],
                'tipo': plantilla.get('tipo', 'desconocido'),
                'version': plantilla.get('version', '1.0')
            }
            for id_plantilla, plantilla in self.plantillas_disponibles.items()
        }
    
    def cargar_plantilla(self, id_plantilla, app_instance):
        """Carga una plantilla específica en la aplicación"""
        if id_plantilla not in self.plantillas_disponibles:
            raise ValueError(f"Plantilla '{id_plantilla}' no encontrada")
        
        plantilla = self.plantillas_disponibles[id_plantilla]
        
        try:
            # Aplicar datos predefinidos
            if 'datos_predefinidos' in plantilla:
                self._aplicar_datos_predefinidos(plantilla['datos_predefinidos'], app_instance)
            
            # Aplicar configuración de formato
            if 'formato_config' in plantilla:
                self._aplicar_formato_config(plantilla['formato_config'], app_instance)
            
            # Aplicar estructura de secciones
            if 'estructura_secciones' in plantilla:
                self._aplicar_estructura_secciones(plantilla['estructura_secciones'], app_instance)
            
            # Aplicar opciones de generación
            if 'opciones_generacion' in plantilla:
                self._aplicar_opciones_generacion(plantilla['opciones_generacion'], app_instance)
            
            self.plantilla_activa = id_plantilla
            
            messagebox.showinfo("✅ Plantilla Cargada", 
                f"Plantilla '{plantilla['nombre']}' aplicada correctamente.\n\n"
                f"Datos aplicados:\n"
                f"• Información predefinida\n"
                f"• Configuración de formato\n"
                f"• Estructura de secciones\n"
                f"• Opciones de generación")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar plantilla:\n{str(e)}")
    
    def _aplicar_datos_predefinidos(self, datos, app_instance):
        """Aplica datos predefinidos de la plantilla"""
        for campo, valor in datos.items():
            if campo in app_instance.proyecto_data:
                entry = app_instance.proyecto_data[campo]
                if hasattr(entry, 'delete') and hasattr(entry, 'insert'):
                    entry.delete(0, "end")
                    entry.insert(0, valor)
    
    def _aplicar_formato_config(self, formato_config, app_instance):
        """Aplica configuración de formato de la plantilla"""
        app_instance.formato_config.update(formato_config)
        
        # Actualizar controles de UI si existen
        controles_formato = {
            'fuente_texto': 'fuente_texto',
            'tamaño_texto': 'tamaño_texto',
            'fuente_titulo': 'fuente_titulo',
            'tamaño_titulo': 'tamaño_titulo',
            'interlineado': 'interlineado',
            'margen': 'margen'
        }
        
        for config_key, control_name in controles_formato.items():
            if hasattr(app_instance, control_name) and config_key in formato_config:
                control = getattr(app_instance, control_name)
                if hasattr(control, 'set'):
                    control.set(str(formato_config[config_key]))
        
        # Actualizar checkboxes de formato
        checkboxes_formato = {
            'justificado': 'justificado_var',
            'sangria': 'sangria_var'
        }
        
        for config_key, checkbox_name in checkboxes_formato.items():
            if hasattr(app_instance, checkbox_name) and config_key in formato_config:
                checkbox = getattr(app_instance, checkbox_name)
                if formato_config[config_key]:
                    checkbox.select()
                else:
                    checkbox.deselect()
    
    def _aplicar_estructura_secciones(self, estructura, app_instance):
        """Aplica estructura de secciones de la plantilla"""
        # Esta función puede expandirse para reorganizar secciones según la plantilla
        # Por ahora mantiene compatibilidad con la estructura existente
        pass
    
    def _aplicar_opciones_generacion(self, opciones, app_instance):
        """Aplica opciones de generación de la plantilla"""
        opciones_ui = {
            'incluir_portada': 'incluir_portada',
            'incluir_indice': 'incluir_indice',
            'incluir_agradecimientos': 'incluir_agradecimientos',
            'numeracion_paginas': 'numeracion_paginas'
        }
        
        for opcion_key, control_name in opciones_ui.items():
            if hasattr(app_instance, control_name) and opcion_key in opciones:
                control = getattr(app_instance, control_name)
                if opciones[opcion_key]:
                    control.select()
                else:
                    control.deselect()
    
    def crear_plantilla_desde_proyecto(self, app_instance, nombre_plantilla, descripcion=""):
        """Crea una nueva plantilla basada en el proyecto actual"""
        try:
            # Recopilar datos del proyecto actual
            datos_predefinidos = {}
            for campo, entry in app_instance.proyecto_data.items():
                if hasattr(entry, 'get') and entry.get().strip():
                    datos_predefinidos[campo] = entry.get().strip()
            
            # Crear estructura de plantilla
            nueva_plantilla = {
                'id': f"custom_{nombre_plantilla.lower().replace(' ', '_')}",
                'nombre': nombre_plantilla,
                'descripcion': descripcion or f"Plantilla personalizada basada en proyecto actual",
                'version': '1.0',
                'fecha_creacion': datetime.now().isoformat(),
                'tipo': 'personalizada',
                'datos_predefinidos': datos_predefinidos,
                'formato_config': deepcopy(app_instance.formato_config),
                'estructura_secciones': {
                    'secciones_activas': app_instance.secciones_activas.copy(),
                    'secciones_disponibles': deepcopy(app_instance.secciones_disponibles)
                },
                'opciones_generacion': {
                    'incluir_portada': getattr(app_instance, 'incluir_portada', None) and app_instance.incluir_portada.get(),
                    'incluir_indice': getattr(app_instance, 'incluir_indice', None) and app_instance.incluir_indice.get(),
                    'incluir_agradecimientos': getattr(app_instance, 'incluir_agradecimientos', None) and app_instance.incluir_agradecimientos.get(),
                    'numeracion_paginas': getattr(app_instance, 'numeracion_paginas', None) and app_instance.numeracion_paginas.get()
                }
            }
            
            # Guardar plantilla
            self.guardar_plantilla(nueva_plantilla)
            
            messagebox.showinfo("✅ Plantilla Creada", 
                f"Plantilla '{nombre_plantilla}' creada exitosamente.\n\n"
                f"Incluye:\n"
                f"• {len(datos_predefinidos)} campos predefinidos\n"
                f"• Configuración de formato actual\n"
                f"• {len(app_instance.secciones_activas)} secciones activas\n"
                f"• Opciones de generación")
            
            return nueva_plantilla['id']
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al crear plantilla:\n{str(e)}")
            return None
    
    def guardar_plantilla(self, plantilla):
        """Guarda una plantilla en archivo"""
        if not self.ruta_plantillas:
            raise Exception("Directorio de plantillas no disponible")
        
        nombre_archivo = f"{plantilla['id']}.json"
        ruta_archivo = os.path.join(self.ruta_plantillas, nombre_archivo)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(plantilla, f, ensure_ascii=False, indent=2)
        
        # Agregar a plantillas disponibles
        self.plantillas_disponibles[plantilla['id']] = plantilla
    
    def eliminar_plantilla(self, id_plantilla):
        """Elimina una plantilla (solo personalizadas)"""
        if id_plantilla not in self.plantillas_disponibles:
            raise ValueError(f"Plantilla '{id_plantilla}' no encontrada")
        
        plantilla = self.plantillas_disponibles[id_plantilla]
        
        # No permitir eliminar plantillas base
        if plantilla.get('tipo') == 'base':
            raise ValueError("No se pueden eliminar plantillas base del sistema")
        
        # Eliminar archivo si existe
        if plantilla.get('tipo') in ['externa', 'personalizada'] and self.ruta_plantillas:
            nombre_archivo = f"{id_plantilla}.json"
            ruta_archivo = os.path.join(self.ruta_plantillas, nombre_archivo)
            
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        
        # Eliminar de memoria
        del self.plantillas_disponibles[id_plantilla]
        
        # Si era la plantilla activa, limpiar
        if self.plantilla_activa == id_plantilla:
            self.plantilla_activa = None
        
        messagebox.showinfo("🗑️ Eliminada", f"Plantilla '{plantilla['nombre']}' eliminada correctamente")
    
    def exportar_plantilla(self, id_plantilla):
        """Exporta una plantilla a archivo externo"""
        if id_plantilla not in self.plantillas_disponibles:
            raise ValueError(f"Plantilla '{id_plantilla}' no encontrada")
        
        plantilla = self.plantillas_disponibles[id_plantilla]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Plantilla JSON", "*.json"), ("Todos los archivos", "*.*")],
            title=f"Exportar Plantilla - {plantilla['nombre']}"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(plantilla, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("📤 Exportada", 
                f"Plantilla exportada exitosamente:\n{os.path.basename(filename)}")
    
    def importar_plantilla(self):
        """Importa una plantilla desde archivo externo"""
        filename = filedialog.askopenfilename(
            filetypes=[("Plantilla JSON", "*.json"), ("Todos los archivos", "*.*")],
            title="Importar Plantilla"
        )
        
        if not filename:
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                plantilla = json.load(f)
            
            # Validar plantilla
            if not self._validar_plantilla(plantilla):
                raise ValueError("La plantilla no tiene un formato válido")
            
            # Verificar ID único
            if plantilla['id'] in self.plantillas_disponibles:
                respuesta = messagebox.askyesno("🔄 Plantilla Existente", 
                    f"Ya existe una plantilla con ID '{plantilla['id']}'.\n"
                    f"¿Deseas sobrescribir la existente?")
                
                if not respuesta:
                    return None
            
            # Guardar plantilla
            plantilla['tipo'] = 'importada'
            self.guardar_plantilla(plantilla)
            
            messagebox.showinfo("📥 Importada", 
                f"Plantilla '{plantilla['nombre']}' importada correctamente")
            
            return plantilla['id']
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al importar plantilla:\n{str(e)}")
            return None
    
    def obtener_plantilla_activa(self):
        """Retorna información de la plantilla actualmente activa"""
        if not self.plantilla_activa:
            return None
        
        return self.plantillas_disponibles.get(self.plantilla_activa)
    
    def limpiar_plantilla_activa(self, app_instance):
        """Limpia la aplicación de datos de plantilla"""
        # Limpiar campos predefinidos
        campos_limpiar = ['institucion', 'ciclo', 'curso', 'enfasis', 'director', 'categoria']
        
        for campo in campos_limpiar:
            if campo in app_instance.proyecto_data:
                entry = app_instance.proyecto_data[campo]
                if hasattr(entry, 'delete'):
                    entry.delete(0, "end")
        
        self.plantilla_activa = None
        messagebox.showinfo("🧹 Limpiado", "Plantilla desactivada y campos limpiados")
    
    def generar_reporte_plantillas(self):
        """Genera un reporte de todas las plantillas disponibles"""
        reporte = "📋 REPORTE DE PLANTILLAS DISPONIBLES\n"
        reporte += "=" * 50 + "\n\n"
        
        for id_plantilla, plantilla in self.plantillas_disponibles.items():
            reporte += f"🔹 {plantilla['nombre']} (ID: {id_plantilla})\n"
            reporte += f"   Tipo: {plantilla.get('tipo', 'Desconocido')}\n"
            reporte += f"   Versión: {plantilla.get('version', 'N/A')}\n"
            reporte += f"   Descripción: {plantilla.get('descripcion', 'Sin descripción')}\n"
            
            if 'datos_predefinidos' in plantilla:
                reporte += f"   Campos predefinidos: {len(plantilla['datos_predefinidos'])}\n"
            
            reporte += "\n"
        
        if self.plantilla_activa:
            plantilla_activa = self.plantillas_disponibles[self.plantilla_activa]
            reporte += f"🔥 PLANTILLA ACTIVA: {plantilla_activa['nombre']}\n"
        
        return reporte
    
    def validar_compatibilidad_plantilla(self, id_plantilla, app_instance):
        """Valida si una plantilla es compatible con la versión actual"""
        if id_plantilla not in self.plantillas_disponibles:
            return False, "Plantilla no encontrada"
        
        plantilla = self.plantillas_disponibles[id_plantilla]
        
        # Verificaciones de compatibilidad
        advertencias = []
        
        # Verificar campos requeridos
        if 'datos_predefinidos' in plantilla:
            for campo in plantilla['datos_predefinidos']:
                if campo not in app_instance.proyecto_data:
                    advertencias.append(f"Campo '{campo}' no existe en la aplicación actual")
        
        # Verificar secciones
        if 'estructura_secciones' in plantilla:
            estructura = plantilla['estructura_secciones']
            if 'secciones_disponibles' in estructura:
                for seccion_id in estructura['secciones_disponibles']:
                    if seccion_id not in app_instance.secciones_disponibles:
                        advertencias.append(f"Sección '{seccion_id}' no está disponible")
        
        es_compatible = len(advertencias) == 0
        mensaje = "Plantilla compatible" if es_compatible else "; ".join(advertencias)
        
        return es_compatible, mensaje

# Funciones de utilidad para integración con main_window.py
def obtener_template_manager():
    """Función helper para obtener instancia singleton del TemplateManager"""
    if not hasattr(obtener_template_manager, '_instance'):
        obtener_template_manager._instance = TemplateManager()
    return obtener_template_manager._instance

def aplicar_plantilla_tercer_ano(app_instance):
    """Función de conveniencia para aplicar la plantilla de 3º año BTI"""
    template_manager = obtener_template_manager()
    template_manager.cargar_plantilla('tercer_ano_bti', app_instance)

def mostrar_gestor_plantillas(app_instance):
    """Muestra ventana del gestor de plantillas"""
    import customtkinter as ctk
    from tkinter import messagebox
    
    template_manager = obtener_template_manager()
    
    # Crear ventana del gestor
    gestor_window = ctk.CTkToplevel(app_instance.root)
    gestor_window.title("📋 Gestor de Plantillas")
    gestor_window.geometry("800x600")
    gestor_window.transient(app_instance.root)
    gestor_window.grab_set()
    
    # Centrar ventana
    gestor_window.update_idletasks()
    x = (gestor_window.winfo_screenwidth() // 2) - (800 // 2)
    y = (gestor_window.winfo_screenheight() // 2) - (600 // 2)
    gestor_window.geometry(f"800x600+{x}+{y}")
    
    main_frame = ctk.CTkFrame(gestor_window, corner_radius=0)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    title_label = ctk.CTkLabel(
        main_frame, text="📋 Gestor de Plantillas Avanzado",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=(10, 20))
    
    # Lista de plantillas
    plantillas_frame = ctk.CTkFrame(main_frame)
    plantillas_frame.pack(fill="both", expand=True, pady=(0, 20))
    
    list_title = ctk.CTkLabel(
        plantillas_frame, text="🗂️ Plantillas Disponibles",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    list_title.pack(pady=(15, 10))
    
    # Scrollable frame para plantillas
    plantillas_scroll = ctk.CTkScrollableFrame(plantillas_frame, height=300)
    plantillas_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Mostrar plantillas
    plantillas_disponibles = template_manager.obtener_plantillas_disponibles()
    for id_plantilla, info in plantillas_disponibles.items():
        plantilla_item = ctk.CTkFrame(plantillas_scroll, fg_color="gray20", corner_radius=8)
        plantilla_item.pack(fill="x", pady=5, padx=5)
        
        # Información de la plantilla
        info_frame = ctk.CTkFrame(plantilla_item, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        nombre_label = ctk.CTkLabel(
            info_frame, text=f"📋 {info['nombre']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        nombre_label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            info_frame, text=f"📝 {info['descripcion']}",
            font=ctk.CTkFont(size=11), wraplength=500
        )
        desc_label.pack(anchor="w", pady=(2, 5))
        
        tipo_version = f"🏷️ {info['tipo'].title()} - v{info['version']}"
        tipo_label = ctk.CTkLabel(
            info_frame, text=tipo_version,
            font=ctk.CTkFont(size=10), text_color="gray70"
        )
        tipo_label.pack(anchor="w")
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(plantilla_item, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Botón aplicar
        aplicar_btn = ctk.CTkButton(
            btn_frame, text="✅ Aplicar",
            command=lambda pid=id_plantilla: aplicar_y_cerrar(pid),
            width=80, height=28, fg_color="green", hover_color="darkgreen"
        )
        aplicar_btn.pack(side="left", padx=(0, 5))
        
        # Botón exportar
        export_btn = ctk.CTkButton(
            btn_frame, text="📤 Exportar",
            command=lambda pid=id_plantilla: template_manager.exportar_plantilla(pid),
            width=80, height=28, fg_color="blue", hover_color="darkblue"
        )
        export_btn.pack(side="left", padx=(0, 5))
        
        # Botón eliminar (solo para plantillas no base)
        if info['tipo'] != 'base':
            delete_btn = ctk.CTkButton(
                btn_frame, text="🗑️ Eliminar",
                command=lambda pid=id_plantilla: eliminar_plantilla(pid),
                width=80, height=28, fg_color="red", hover_color="darkred"
            )
            delete_btn.pack(side="left")
    
    # Botones principales
    buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    buttons_frame.pack(fill="x")
    
    import_btn = ctk.CTkButton(
        buttons_frame, text="📥 Importar Plantilla",
        command=lambda: [template_manager.importar_plantilla(), actualizar_lista()],
        width=150, height=35
    )
    import_btn.pack(side="left", padx=(0, 10))
    
    create_btn = ctk.CTkButton(
        buttons_frame, text="➕ Crear desde Actual",
        command=crear_desde_actual,
        width=150, height=35, fg_color="purple", hover_color="darkviolet"
    )
    create_btn.pack(side="left", padx=(0, 10))
    
    close_btn = ctk.CTkButton(
        buttons_frame, text="❌ Cerrar",
        command=gestor_window.destroy,
        width=100, height=35
    )
    close_btn.pack(side="right")
    
    # Funciones auxiliares
    def aplicar_y_cerrar(id_plantilla):
        template_manager.cargar_plantilla(id_plantilla, app_instance)
        gestor_window.destroy()
    
    def eliminar_plantilla(id_plantilla):
        try:
            template_manager.eliminar_plantilla(id_plantilla)
            actualizar_lista()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def crear_desde_actual():
        # Diálogo simple para nombre
        dialog = ctk.CTkInputDialog(
            text="Nombre para la nueva plantilla:",
            title="Crear Plantilla"
        )
        nombre = dialog.get_input()
        
        if nombre:
            template_manager.crear_plantilla_desde_proyecto(app_instance, nombre)
            actualizar_lista()
    
    def actualizar_lista():
        # Recargar la ventana (implementación simple)
        gestor_window.destroy()
        mostrar_gestor_plantillas(app_instance)