# controllers/reference_controller.py
"""
Controlador de Referencias - Maneja la lógica de referencias bibliográficas
"""

from typing import Dict, List, Optional
from modules.references import ReferenceManager
from core.state_manager import state_manager
from utils.logger import get_logger
from tkinter import messagebox, filedialog

logger = get_logger('ReferenceController')

class ReferenceController:
    """Controlador para gestión de referencias"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.reference_manager = ReferenceManager()
        logger.info("ReferenceController inicializado")
    
    def agregar_referencia_desde_formulario(self) -> bool:
        """Agrega una referencia desde el formulario UI"""
        try:
            # Recopilar datos del formulario
            ref_data = self._obtener_datos_formulario()
            
            if not ref_data:
                return False
            
            # Agregar usando el manager
            referencia = self.reference_manager.agregar_referencia(ref_data)
            
            # Actualizar estado global
            state_manager.add_referencia(referencia)
            
            # Actualizar UI
            self._actualizar_ui()
            self._limpiar_formulario()
            
            messagebox.showinfo("✅ Agregada", "Referencia agregada correctamente")
            return True
            
        except ValueError as e:
            messagebox.showerror("❌ Error", str(e))
            return False
    
    def importar_bibtex(self) -> int:
        """Importa referencias desde archivo BibTeX"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo BibTeX",
            filetypes=[("Archivos BibTeX", "*.bib"), ("Todos los archivos", "*.*")]
        )
        
        if not filename:
            return 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            referencias_importadas = self.reference_manager.importar_referencias_bibtex(contenido)
            
            # Actualizar estado con todas las referencias
            for ref in self.reference_manager.referencias:
                state_manager.add_referencia(ref)
            
            self._actualizar_ui()
            
            messagebox.showinfo("✅ Importación Exitosa", 
                f"Se importaron {referencias_importadas} referencias")
                
            return referencias_importadas
            
        except Exception as e:
            logger.error(f"Error importando BibTeX: {e}")
            messagebox.showerror("❌ Error", f"Error al importar: {str(e)}")
            return 0
    
    def exportar_referencias_apa(self) -> bool:
        """Exporta referencias en formato APA"""
        if not self.reference_manager.referencias:
            messagebox.showwarning("⚠️ Sin referencias", "No hay referencias para exportar")
            return False
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Exportar Referencias APA"
        )
        
        if not filename:
            return False
        
        try:
            contenido_apa = self.reference_manager.exportar_referencias()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("REFERENCIAS\n")
                f.write("="*50 + "\n\n")
                f.write(contenido_apa)
            
            messagebox.showinfo("✅ Exportado", f"Referencias exportadas a:\n{filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando referencias: {e}")
            messagebox.showerror("❌ Error", f"Error al exportar: {str(e)}")
            return False
    
    def buscar_referencias(self, termino: str) -> List[Dict]:
        """Busca referencias por término"""
        return self.reference_manager.buscar_referencias(termino)
    
    def _obtener_datos_formulario(self) -> Optional[Dict]:
        """Obtiene los datos del formulario de referencias"""
        if not all([
            hasattr(self.app, 'ref_tipo'),
            hasattr(self.app, 'ref_autor'),
            hasattr(self.app, 'ref_año'),
            hasattr(self.app, 'ref_titulo'),
            hasattr(self.app, 'ref_fuente')
        ]):
            return None
        
        return {
            'tipo': self.app.ref_tipo.get(),
            'autor': self.app.ref_autor.get().strip(),
            'año': self.app.ref_año.get().strip(),
            'titulo': self.app.ref_titulo.get().strip(),
            'fuente': self.app.ref_fuente.get().strip()
        }
    
    def _limpiar_formulario(self):
        """Limpia el formulario de referencias"""
        if hasattr(self.app, 'ref_autor'):
            self.app.ref_autor.delete(0, "end")
        if hasattr(self.app, 'ref_año'):
            self.app.ref_año.delete(0, "end")
        if hasattr(self.app, 'ref_titulo'):
            self.app.ref_titulo.delete(0, "end")
        if hasattr(self.app, 'ref_fuente'):
            self.app.ref_fuente.delete(0, "end")
    
    def _actualizar_ui(self):
        """Actualiza la UI de referencias"""
        # Sincronizar con estado
        self.app.referencias = state_manager.get_state().referencias
        
        if hasattr(self.app, 'actualizar_lista_referencias'):
            self.app.actualizar_lista_referencias()
        
        if hasattr(self.app, 'ref_stats_label'):
            self.app.ref_stats_label.configure(
                text=f"Total: {len(self.app.referencias)} referencias"
            )