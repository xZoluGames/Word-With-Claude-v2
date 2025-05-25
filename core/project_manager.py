"""
Gestor de proyectos - Guardar, cargar y gestionar proyectos académicos
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from copy import deepcopy
import hashlib

class ProjectManager:
    def __init__(self):
        self.auto_save_enabled = True
        self.last_save_time = None
        self.last_save_hash = None  # Nuevo: hash del último guardado

    def guardar_proyecto(self, app_instance):
        """Guarda el proyecto completo en un archivo JSON"""
        try:
            # Recopilar todos los datos
            proyecto_completo = {
                'version': '2.0',
                'fecha_creacion': datetime.now().isoformat(),
                'informacion_general': {},
                'contenido_secciones': {},
                'referencias': app_instance.referencias,
                'secciones_activas': app_instance.secciones_activas,
                'secciones_disponibles': app_instance.secciones_disponibles,
                'formato_config': app_instance.formato_config,
                'imagenes': {
                    'encabezado_personalizado': getattr(app_instance, 'encabezado_personalizado', None),
                    'insignia_personalizada': getattr(app_instance, 'insignia_personalizada', None)
                },
                'estadisticas': getattr(app_instance, 'stats', {})
            }
            
            # Información general
            for key, entry in app_instance.proyecto_data.items():
                if hasattr(entry, 'get'):
                    proyecto_completo['informacion_general'][key] = entry.get()
            
            # Contenido de secciones
            for key, text_widget in app_instance.content_texts.items():
                proyecto_completo['contenido_secciones'][key] = text_widget.get("1.0", "end")
            
            # Guardar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Proyecto Académico", "*.json"), ("Todos los archivos", "*.*")],
                title="Guardar Proyecto"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(proyecto_completo, f, ensure_ascii=False, indent=2)
                
                self.last_save_time = datetime.now()
                messagebox.showinfo("💾 Guardado", 
                    f"Proyecto guardado exitosamente:\n{os.path.basename(filename)}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar proyecto:\n{str(e)}")
    
    def cargar_proyecto(self, app_instance):
        """Carga un proyecto desde archivo JSON"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Proyecto Académico", "*.json"), ("Todos los archivos", "*.*")],
                title="Cargar Proyecto"
            )
            
            if not filename:
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                proyecto_completo = json.load(f)
            
            # Verificar versión
            version = proyecto_completo.get('version', '1.0')
            if version != '2.0':
                messagebox.showwarning("⚠️ Versión", 
                    "Este proyecto fue creado con una versión anterior. Algunas características pueden no funcionar correctamente.")
            
            # Cargar información general
            if 'informacion_general' in proyecto_completo:
                for key, value in proyecto_completo['informacion_general'].items():
                    if key in app_instance.proyecto_data and hasattr(app_instance.proyecto_data[key], 'delete'):
                        app_instance.proyecto_data[key].delete(0, "end")
                        app_instance.proyecto_data[key].insert(0, value)
            
            # Cargar configuración de formato
            if 'formato_config' in proyecto_completo:
                app_instance.formato_config.update(proyecto_completo['formato_config'])
                self.aplicar_config_cargada(app_instance)
            
            # Cargar secciones
            if 'secciones_disponibles' in proyecto_completo:
                app_instance.secciones_disponibles = proyecto_completo['secciones_disponibles']
            
            if 'secciones_activas' in proyecto_completo:
                app_instance.secciones_activas = proyecto_completo['secciones_activas']
            
            # Cargar referencias
            if 'referencias' in proyecto_completo:
                app_instance.referencias = proyecto_completo['referencias']
                app_instance.actualizar_lista_referencias()
            
            # Cargar imágenes
            if 'imagenes' in proyecto_completo:
                app_instance.encabezado_personalizado = proyecto_completo['imagenes'].get('encabezado_personalizado')
                app_instance.insignia_personalizada = proyecto_completo['imagenes'].get('insignia_personalizada')
            
            # Recrear interfaz
            app_instance.actualizar_lista_secciones()
            app_instance.crear_pestanas_contenido()
            
            # Cargar contenido de secciones
            if 'contenido_secciones' in proyecto_completo:
                for key, content in proyecto_completo['contenido_secciones'].items():
                    if key in app_instance.content_texts:
                        app_instance.content_texts[key].delete("1.0", "end")
                        app_instance.content_texts[key].insert("1.0", content)
            
            messagebox.showinfo("📂 Cargado", 
                f"Proyecto cargado exitosamente:\n{os.path.basename(filename)}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar proyecto:\n{str(e)}")
    
    def nuevo_proyecto(self, app_instance):
        """Crea un nuevo proyecto limpio"""
        respuesta = messagebox.askyesno("🆕 Nuevo Proyecto", 
            "¿Estás seguro? Se perderán todos los cambios no guardados.")
        
        if respuesta:
            # Reiniciar todas las variables
            app_instance.referencias = []
            app_instance.encabezado_personalizado = None
            app_instance.insignia_personalizada = None
            app_instance.secciones_disponibles = app_instance.get_secciones_iniciales()
            app_instance.secciones_activas = list(app_instance.secciones_disponibles.keys())
            
            # Limpiar campos
            for entry in app_instance.proyecto_data.values():
                if hasattr(entry, 'delete'):
                    entry.delete(0, "end")
            
            # Recrear interfaz
            app_instance.actualizar_lista_secciones()
            app_instance.crear_pestanas_contenido()
            app_instance.actualizar_lista_referencias()
            
            messagebox.showinfo("🆕 Nuevo Proyecto", "Proyecto nuevo creado")
    
    def auto_save_project(self, app_instance):
            """Guarda automáticamente el proyecto solo si hay cambios"""
            if self.auto_save_enabled:
                try:
                    from utils.logger import get_logger
                    logger = get_logger('ProjectManager')
                    
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    auto_save_path = os.path.join(script_dir, "..", "auto_save.json")
                    auto_save_path = os.path.normpath(auto_save_path)
                    
                    # Crear backup automático
                    proyecto_completo = {
                        'version': '2.0',
                        'fecha_auto_save': datetime.now().isoformat(),
                        'informacion_general': {},
                        'contenido_secciones': {},
                        'referencias': app_instance.referencias,
                        'secciones_activas': app_instance.secciones_activas,
                        'formato_config': app_instance.formato_config
                    }
                    
                    # Guardar información
                    for key, entry in app_instance.proyecto_data.items():
                        if hasattr(entry, 'get'):
                            proyecto_completo['informacion_general'][key] = entry.get()
                    
                    for key, text_widget in app_instance.content_texts.items():
                        proyecto_completo['contenido_secciones'][key] = text_widget.get("1.0", "end")
                    
                    # Calcular hash del contenido actual
                    content_str = json.dumps(proyecto_completo, sort_keys=True)
                    current_hash = hashlib.md5(content_str.encode()).hexdigest()
                    
                    # Solo guardar si hay cambios
                    if current_hash != self.last_save_hash:
                        with open(auto_save_path, 'w', encoding='utf-8') as f:
                            json.dump(proyecto_completo, f, ensure_ascii=False, indent=2)
                        
                        self.last_save_hash = current_hash
                        self.last_save_time = datetime.now()
                        logger.info(f"Auto-guardado realizado - Hash: {current_hash[:8]}")
                    else:
                        logger.debug("Auto-guardado omitido - Sin cambios")
                    
                except Exception as e:
                    logger.error(f"Error en auto-guardado: {e}")
                
                # Programar próximo auto-guardado
                app_instance.root.after(300000, lambda: self.auto_save_project(app_instance))  # 5 minutos
    
    def exportar_configuracion(self, app_instance):
        """Exporta solo la configuración de formato"""
        try:
            config_export = {
                'version': '2.0',
                'tipo': 'configuracion_formato',
                'fecha_export': datetime.now().isoformat(),
                'formato_config': app_instance.formato_config,
                'secciones_disponibles': app_instance.secciones_disponibles,
                'secciones_activas': app_instance.secciones_activas
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Configuración", "*.json")],
                title="Exportar Configuración"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_export, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("📤 Exportado", 
                    "Configuración exportada exitosamente")
                    
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
    
    def aplicar_config_cargada(self, app_instance):
        """Aplica configuración cargada a los controles"""
        try:
            # Actualizar controles de formato si existen
            if hasattr(app_instance, 'fuente_texto'):
                app_instance.fuente_texto.set(app_instance.formato_config.get('fuente_texto', 'Times New Roman'))
            if hasattr(app_instance, 'tamaño_texto'):
                app_instance.tamaño_texto.set(str(app_instance.formato_config.get('tamaño_texto', 12)))
            if hasattr(app_instance, 'fuente_titulo'):
                app_instance.fuente_titulo.set(app_instance.formato_config.get('fuente_titulo', 'Times New Roman'))
            if hasattr(app_instance, 'tamaño_titulo'):
                app_instance.tamaño_titulo.set(str(app_instance.formato_config.get('tamaño_titulo', 14)))
            if hasattr(app_instance, 'interlineado'):
                app_instance.interlineado.set(str(app_instance.formato_config.get('interlineado', 2.0)))
            if hasattr(app_instance, 'margen'):
                app_instance.margen.set(str(app_instance.formato_config.get('margen', 2.54)))
                
        except Exception as e:
            print(f"Error aplicando configuración: {e}")