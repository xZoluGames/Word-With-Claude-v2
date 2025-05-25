
from utils.logger import get_logger

logger = get_logger("citation_dialog")

"""
Citation Dialog - Diálogo para insertar citas
"""

import customtkinter as ctk
from tkinter import messagebox

class CitationDialog:
    """Diálogo para insertar citas de manera guiada"""
    def __init__(self, parent, seccion_tipo=None):
        self.result = None
        self.seccion_tipo = seccion_tipo
        
        # Crear ventana
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("📚 Insertar Cita")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Configura el diálogo de citas"""
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="📚 Asistente de Citas APA",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Tipo de cita
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(type_frame, text="Tipo de cita:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.tipo_var = ctk.StringVar(value="parafraseo")
        tipos = [
            ("Parafraseo", "parafraseo", "Idea del autor con tus palabras"),
            ("Textual corta", "textual", "Cita exacta (menos de 40 palabras)"),
            ("Textual larga", "larga", "Cita exacta (más de 40 palabras)"),
            ("Fuente web", "web", "Sitio web o recurso en línea"),
            ("Múltiples autores", "multiple", "Dos o más autores"),
            ("Comunicación personal", "personal", "Email, entrevista, etc."),
            ("Institución", "institucional", "Organización como autor")
        ]
        
        for texto, valor, descripcion in tipos:
            frame = ctk.CTkFrame(type_frame, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            
            radio = ctk.CTkRadioButton(
                frame, text=texto, variable=self.tipo_var, value=valor,
                command=self.actualizar_campos
            )
            radio.pack(side="left")
            
            desc_label = ctk.CTkLabel(
                frame, text=f" - {descripcion}",
                font=ctk.CTkFont(size=10), text_color="gray"
            )
            desc_label.pack(side="left", padx=(10, 0))
        
        # Campos dinámicos
        self.fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Autor
        ctk.CTkLabel(self.fields_frame, text="Autor(es):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.autor_entry = ctk.CTkEntry(self.fields_frame, placeholder_text="Apellido, N. o García y López")
        self.autor_entry.pack(fill="x", pady=(0, 10))
        
        # Año
        ctk.CTkLabel(self.fields_frame, text="Año:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.año_entry = ctk.CTkEntry(self.fields_frame, placeholder_text="2024")
        self.año_entry.pack(fill="x", pady=(0, 10))
        
        # Página (opcional)
        self.pagina_label = ctk.CTkLabel(self.fields_frame, text="Página (opcional):", font=ctk.CTkFont(weight="bold"))
        self.pagina_label.pack(anchor="w", pady=(0, 5))
        self.pagina_entry = ctk.CTkEntry(self.fields_frame, placeholder_text="45")
        self.pagina_entry.pack(fill="x", pady=(0, 10))
        
        # Vista previa
        preview_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=10)
        preview_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            preview_frame, text="Vista previa:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame, text="[CITA:parafraseo:Autor:Año]",
            font=ctk.CTkFont(family="Courier", size=12),
            text_color="lightgreen"
        )
        self.preview_label.pack(padx=15, pady=(0, 10))
        
        # Actualizar vista previa cuando cambien los campos
        self.autor_entry.bind("<KeyRelease>", lambda e: self.actualizar_preview())
        self.año_entry.bind("<KeyRelease>", lambda e: self.actualizar_preview())
        self.pagina_entry.bind("<KeyRelease>", lambda e: self.actualizar_preview())
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=self.cancelar,
            fg_color="red", hover_color="darkred", width=120
        )
        cancel_btn.pack(side="left", padx=(20, 10))
        
        insert_btn = ctk.CTkButton(
            btn_frame, text="✅ Insertar Cita", command=self.insertar_cita,
            fg_color="green", hover_color="darkgreen", width=150
        )
        insert_btn.pack(side="right", padx=(10, 20))
    
    def actualizar_campos(self):
        """Actualiza los campos según el tipo de cita"""
        tipo = self.tipo_var.get()
        
        # Mostrar/ocultar campo de página
        if tipo in ['textual', 'larga']:
            self.pagina_label.pack(anchor="w", pady=(0, 5))
            self.pagina_entry.pack(fill="x", pady=(0, 10))
        else:
            self.pagina_label.pack_forget()
            self.pagina_entry.pack_forget()
        
        self.actualizar_preview()
    
    def actualizar_preview(self):
        """Actualiza la vista previa de la cita"""
        tipo = self.tipo_var.get()
        autor = self.autor_entry.get() or "Autor"
        año = self.año_entry.get() or "Año"
        pagina = self.pagina_entry.get()
        
        if tipo in ['textual', 'larga'] and pagina:
            preview = f"[CITA:{tipo}:{autor}:{año}:{pagina}]"
        elif tipo == 'personal':
            preview = f"[CITA:{tipo}:{autor}:{año}:comunicación personal]"
        else:
            preview = f"[CITA:{tipo}:{autor}:{año}]"
        
        self.preview_label.configure(text=preview)
    
    def insertar_cita(self):
        """Valida e inserta la cita"""
        autor = self.autor_entry.get().strip()
        año = self.año_entry.get().strip()
        
        if not autor or not año:
            messagebox.showerror("❌ Error", "Autor y año son obligatorios")
            return
        
        # Validar año
        try:
            año_num = int(año)
            if año_num < 1900 or año_num > 2050:
                raise ValueError()
        except:
            messagebox.showerror("❌ Error", "Año debe ser un número válido")
            return
        
        self.result = self.preview_label.cget("text")
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela la operación"""
        self.dialog.destroy()
