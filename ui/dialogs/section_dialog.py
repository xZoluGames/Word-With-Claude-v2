
from utils.logger import get_logger

logger = get_logger("section_dialog")

"""
Section Dialog - Diálogo para agregar/editar secciones
"""

import customtkinter as ctk
from tkinter import messagebox
import re

class SeccionDialog:
    """Diálogo para agregar/editar secciones"""
    def __init__(self, parent, secciones_existentes, editar=False, seccion_actual=None):
        self.result = None
        self.secciones_existentes = secciones_existentes
        self.editar = editar
        self.seccion_actual = seccion_actual
        
        # Crear ventana de diálogo
        titulo = "✏️ Editar Sección" if editar else "➕ Agregar Nueva Sección"
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(titulo)
        self.dialog.geometry("550x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"550x450+{x}+{y}")
        
        self.setup_dialog()
        
        # Cargar datos si es edición
        if editar and seccion_actual:
            self.cargar_datos_existentes()
    
    def setup_dialog(self):
        """Configura el diálogo"""
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo_texto = "✏️ Editar Sección Existente" if self.editar else "➕ Crear Nueva Sección"
        title_label = ctk.CTkLabel(
            main_frame, text=titulo_texto,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Campos
        fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # ID único
        ctk.CTkLabel(fields_frame, text="ID único:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.id_entry = ctk.CTkEntry(fields_frame, placeholder_text="ejemplo: mi_seccion_personalizada")
        self.id_entry.pack(fill="x", pady=(0, 15))
        
        # Si es edición, el ID no se puede cambiar
        if self.editar:
            self.id_entry.configure(state="disabled")
        
        # Título
        ctk.CTkLabel(fields_frame, text="Título:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.titulo_entry = ctk.CTkEntry(fields_frame, placeholder_text="📝 Mi Nueva Sección")
        self.titulo_entry.pack(fill="x", pady=(0, 15))
        
        # Instrucción
        ctk.CTkLabel(fields_frame, text="Instrucción:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.instruccion_text = ctk.CTkTextbox(fields_frame, height=80)
        self.instruccion_text.insert("1.0", "Describe qué debe contener esta sección...")
        self.instruccion_text.pack(fill="x", pady=(0, 15))
        
        # Opciones
        options_frame = ctk.CTkFrame(fields_frame, fg_color="gray20", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(options_frame, text="⚙️ Opciones de Sección:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        self.es_capitulo = ctk.CTkCheckBox(options_frame, text="📖 Es título de capítulo (solo organizacional)")
        self.es_capitulo.pack(anchor="w", padx=20, pady=5)
        
        self.es_requerida = ctk.CTkCheckBox(options_frame, text="⚠️ Sección requerida (obligatoria para validación)")
        self.es_requerida.pack(anchor="w", padx=20, pady=5)
        
        # Información adicional
        info_text = """💡 INFORMACIÓN:
- ID único: Identificador interno (sin espacios, usar guiones bajos)
- Título: Nombre que aparecerá en pestañas y documento
- Instrucción: Guía para el usuario sobre qué escribir
- Capítulo: Solo aparece como título organizacional, sin contenido
- Requerida: Se valida que tenga contenido antes de generar"""
        
        info_label = ctk.CTkLabel(
            options_frame, text=info_text, font=ctk.CTkFont(size=10),
            justify="left", wraplength=450
        )
        info_label.pack(padx=15, pady=(5, 15))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=self.cancelar,
            fg_color="red", hover_color="darkred", width=120
        )
        cancel_btn.pack(side="left", padx=(20, 10))
        
        action_text = "✅ Actualizar Sección" if self.editar else "✅ Crear Sección"
        create_btn = ctk.CTkButton(
            btn_frame, text=action_text, command=self.procesar_seccion,
            fg_color="green", hover_color="darkgreen", width=150
        )
        create_btn.pack(side="right", padx=(10, 20))
    
    def cargar_datos_existentes(self):
        """Carga los datos de la sección existente para editar"""
        if self.seccion_actual:
            seccion_id, seccion_data = self.seccion_actual
            
            self.id_entry.delete(0, "end")
            self.id_entry.insert(0, seccion_id)
            
            self.titulo_entry.delete(0, "end")
            self.titulo_entry.insert(0, seccion_data['titulo'])
            
            self.instruccion_text.delete("1.0", "end")
            self.instruccion_text.insert("1.0", seccion_data['instruccion'])
            
            if seccion_data.get('capitulo', False):
                self.es_capitulo.select()
            else:
                self.es_capitulo.deselect()
            
            if seccion_data.get('requerida', False):
                self.es_requerida.select()
            else:
                self.es_requerida.deselect()
    
    def procesar_seccion(self):
        """Procesa la creación o edición de la sección"""
        seccion_id = self.id_entry.get().strip()
        titulo = self.titulo_entry.get().strip()
        instruccion = self.instruccion_text.get("1.0", "end").strip()
        
        if not all([seccion_id, titulo, instruccion]):
            messagebox.showerror("❌ Error", "Completa todos los campos obligatorios")
            return
        
        # Validar ID único (solo si no es edición o cambió el ID)
        if not self.editar:
            if seccion_id in self.secciones_existentes:
                messagebox.showerror("❌ Error", "Ya existe una sección con ese ID")
                return
        
        # Validar formato del ID
        if not re.match(r'^[a-z0-9_]+$', seccion_id):
            messagebox.showerror("❌ Error", 
                "El ID debe contener solo letras minúsculas, números y guiones bajos")
            return
        
        seccion_data = {
            'titulo': titulo,
            'instruccion': instruccion,
            'requerida': self.es_requerida.get(),
            'capitulo': self.es_capitulo.get()
        }
        
        self.result = (seccion_id, seccion_data)
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela la operación"""
        self.dialog.destroy()

