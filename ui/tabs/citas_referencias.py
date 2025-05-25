
from utils.logger import get_logger

logger = get_logger("citas_referencias")

"""
Tab de Citas y Referencias - Gestión de citas y bibliografía
"""

import customtkinter as ctk
from tkinter import messagebox

class CitasReferenciasTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de citas y referencias"""
        # Contenedor principal con scroll
        main_scroll = ctk.CTkScrollableFrame(self.parent, label_text="")
        main_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Panel de instrucciones
        self.create_instructions_panel(main_scroll)
        
        # Panel de agregar referencias
        self.create_add_references_panel(main_scroll)
        
        # Lista de referencias
        self.create_references_list(main_scroll)
    
    def create_instructions_panel(self, parent):
        """Crea el panel de instrucciones de citas"""
        instruc_frame = ctk.CTkFrame(parent, fg_color="gray15", corner_radius=10)
        instruc_frame.pack(fill="x", pady=(0, 15))
        
        # Header con botón de colapsar
        instruc_header = ctk.CTkFrame(instruc_frame, fg_color="gray20", height=40)
        instruc_header.pack(fill="x")
        instruc_header.pack_propagate(False)
        
        self.app.instruc_collapsed = False
        
        def toggle_instructions():
            if self.app.instruc_collapsed:
                instruc_content.pack(fill="x", padx=15, pady=(0, 15))
                collapse_btn.configure(text="▼")
            else:
                instruc_content.pack_forget()
                collapse_btn.configure(text="▶")
            self.app.instruc_collapsed = not self.app.instruc_collapsed
        
        collapse_btn = ctk.CTkButton(
            instruc_header, text="▼", width=30, height=25,
            command=toggle_instructions,
            fg_color="transparent", hover_color="gray30"
        )
        collapse_btn.pack(side="left", padx=(10, 5))
        
        instruc_title = ctk.CTkLabel(
            instruc_header, text="🚀 SISTEMA DE CITAS - Guía Rápida",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="lightgreen"
        )
        instruc_title.pack(side="left", pady=10)
        
        # Contenido de instrucciones
        instruc_content = ctk.CTkFrame(instruc_frame, fg_color="transparent")
        instruc_content.pack(fill="x", padx=15, pady=(0, 15))
        
        self.create_citation_examples(instruc_content)
    
    def create_citation_examples(self, parent):
        """Crea los ejemplos de citas"""
        ejemplos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        ejemplos_frame.pack(fill="x")
        
        ejemplos = [
            ("📝 Textual corta", "[CITA:textual:García:2020:45]", "(García, 2020, p. 45)"),
            ("🔄 Parafraseo", "[CITA:parafraseo:López:2019]", "(López, 2019)"),
            ("📖 Textual larga", "[CITA:larga:Martínez:2021:78]", "Bloque con sangría"),
            ("👥 Múltiples autores", "[CITA:multiple:García y López:2020]", "(García y López, 2020)"),
            ("🌐 Fuente web", "[CITA:web:OMS:2023]", "(OMS, 2023)"),
            ("💬 Comunicación personal", "[CITA:personal:Pérez:2022:email]", "(Pérez, comunicación personal, 2022)")
        ]
        
        for i, (tipo, formato, resultado) in enumerate(ejemplos):
            ejemplo_frame = ctk.CTkFrame(ejemplos_frame, fg_color="gray25", corner_radius=8)
            ejemplo_frame.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            
            ctk.CTkLabel(
                ejemplo_frame, text=tipo,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(pady=(5, 2))
            
            ctk.CTkLabel(
                ejemplo_frame, text=formato,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color="lightblue"
            ).pack()
            
            ctk.CTkLabel(
                ejemplo_frame, text=f"→ {resultado}",
                font=ctk.CTkFont(size=10),
                text_color="lightgreen"
            ).pack(pady=(2, 5))
    
    def create_add_references_panel(self, parent):
        """Panel para agregar referencias"""
        ref_frame = ctk.CTkFrame(parent, corner_radius=10)
        ref_frame.pack(fill="x", pady=(0, 15))
        
        ref_title = ctk.CTkLabel(
            ref_frame, text="➕ Agregar Referencias",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ref_title.pack(pady=(15, 10))
        
        # Formulario
        form_frame = ctk.CTkFrame(ref_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.create_reference_form(form_frame)
        
        # Botones
        self.create_reference_buttons(ref_frame)
    
    def create_reference_form(self, parent):
        """Crea el formulario de referencias"""
        # Primera fila
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        # Tipo
        tipo_container = ctk.CTkFrame(row1, fg_color="transparent")
        tipo_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            tipo_container, text="Tipo de referencia:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_tipo = ctk.CTkComboBox(
            tipo_container,
            values=["Libro", "Artículo", "Web", "Tesis", "Conferencia", "Informe"],
            height=35, font=ctk.CTkFont(size=12),
            command=self.app.actualizar_campos_referencia
        )
        self.app.ref_tipo.pack(fill="x", pady=(5, 0))
        self.app.ref_tipo.set("Libro")
        
        # Autor(es)
        autor_container = ctk.CTkFrame(row1, fg_color="transparent")
        autor_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            autor_container, text="Autor(es):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_autor = ctk.CTkEntry(
            autor_container, placeholder_text="Apellido, N. o García, J. y López, M.",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_autor.pack(fill="x", pady=(5, 0))
        
        # Segunda fila
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        # Año
        año_container = ctk.CTkFrame(row2, fg_color="transparent")
        año_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            año_container, text="Año:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_año = ctk.CTkEntry(
            año_container, placeholder_text="2024",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_año.pack(fill="x", pady=(5, 0))
        
        # Título
        titulo_container = ctk.CTkFrame(row2, fg_color="transparent")
        titulo_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            titulo_container, text="Título:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_titulo = ctk.CTkEntry(
            titulo_container, placeholder_text="Título completo del trabajo",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_titulo.pack(fill="x", pady=(5, 0))
        
        # Tercera fila
        row3 = ctk.CTkFrame(parent, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.app.fuente_container = ctk.CTkFrame(row3, fg_color="transparent")
        self.app.fuente_container.pack(fill="x")
        
        self.app.fuente_label = ctk.CTkLabel(
            self.app.fuente_container, text="Editorial/Fuente:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.app.fuente_label.pack(anchor="w")
        
        self.app.ref_fuente = ctk.CTkEntry(
            self.app.fuente_container, placeholder_text="Editorial, revista o URL",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_fuente.pack(fill="x", pady=(5, 0))
    
    def create_reference_buttons(self, parent):
        """Crea los botones de acción para referencias"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        
        add_ref_btn = ctk.CTkButton(
            btn_frame, text="➕ Agregar Referencia",
            command=self.app.agregar_referencia,
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            width=180
        )
        add_ref_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(
            btn_frame, text="📥 Importar BibTeX",
            command=self.app.importar_bibtex,
            height=40, font=ctk.CTkFont(size=13),
            width=150, fg_color="purple", hover_color="darkviolet"
        )
        import_btn.pack(side="left", padx=5)
    
    def create_references_list(self, parent):
        """Crea la lista de referencias"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True)
        
        # Header con búsqueda
        list_header = ctk.CTkFrame(list_frame, height=50, fg_color="gray25")
        list_header.pack(fill="x")
        list_header.pack_propagate(False)
        
        list_title = ctk.CTkLabel(
            list_header, text="📋 Referencias Agregadas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.pack(side="left", padx=15)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        search_frame.pack(side="right", padx=15)
        
        ctk.CTkLabel(search_frame, text="🔍").pack(side="left", padx=(0, 5))
        
        self.app.ref_search = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar referencia...",
            width=200, height=30
        )
        self.app.ref_search.pack(side="left")
        self.app.ref_search.bind("<KeyRelease>", self.app.filtrar_referencias)
        
        # Lista scrollable
        self.app.ref_scroll_frame = ctk.CTkScrollableFrame(
            list_frame, height=300,
            fg_color="gray15", corner_radius=8
        )
        self.app.ref_scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Botones de gestión
        self.create_management_buttons(list_frame)
    
    def create_management_buttons(self, parent):
        """Crea botones de gestión de referencias"""
        manage_frame = ctk.CTkFrame(parent, fg_color="transparent")
        manage_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        delete_btn = ctk.CTkButton(
            manage_frame, text="🗑️ Eliminar Seleccionadas",
            command=self.app.eliminar_referencias_seleccionadas,
            fg_color="red", hover_color="darkred",
            height=35, width=180
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            manage_frame, text="📤 Exportar APA",
            command=self.app.exportar_referencias_apa,
            height=35, width=150
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        stats_label = ctk.CTkLabel(
            manage_frame, text=f"Total: {len(self.app.referencias)} referencias",
            font=ctk.CTkFont(size=12)
        )
        stats_label.pack(side="right")
        self.app.ref_stats_label = stats_label
