# controllers/image_controller.py
"""
Controlador de Imágenes - Maneja la lógica de gestión de imágenes
"""

import os
from tkinter import filedialog, messagebox
from PIL import Image
from typing import Optional, Tuple
from utils.logger import get_logger
from utils.cache import image_cache

logger = get_logger('ImageController')

class ImageController:
    """Controlador para gestión de imágenes del documento"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.formatos_soportados = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        logger.info("ImageController inicializado")
    
    def cargar_imagen_personalizada(self, tipo: str, parent_window=None) -> bool:
        """
        Carga una imagen personalizada (encabezado o insignia)
        
        Args:
            tipo: 'encabezado' o 'insignia'
            parent_window: Ventana padre para el diálogo
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            filename = filedialog.askopenfilename(
                parent=parent_window,
                title=f"Seleccionar imagen de {tipo}",
                filetypes=[
                    ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if not filename:
                return False
            
            # Validar archivo
            if not self._validar_imagen(filename):
                return False
            
            # Guardar ruta según tipo
            if tipo == "encabezado":
                self.app.encabezado_personalizado = filename
                logger.info(f"Encabezado personalizado cargado: {filename}")
                
                # Actualizar UI si existe
                if hasattr(self.app, 'enc_custom_label'):
                    self.app.enc_custom_label.configure(text="Encabezado: ✅ Cargado")
                    
            elif tipo == "insignia":
                self.app.insignia_personalizada = filename
                logger.info(f"Insignia personalizada cargada: {filename}")
                
                # Actualizar UI si existe
                if hasattr(self.app, 'ins_custom_label'):
                    self.app.ins_custom_label.configure(text="Insignia: ✅ Cargado")
            
            messagebox.showinfo("✅ Imagen Cargada", 
                f"Imagen de {tipo} cargada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            messagebox.showerror("❌ Error", f"Error al cargar imagen:\n{str(e)}")
            return False
    
    def _validar_imagen(self, filepath: str) -> bool:
        """Valida que el archivo sea una imagen válida"""
        # Verificar extensión
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.formatos_soportados:
            messagebox.showerror("❌ Formato no soportado", 
                f"El formato {ext} no está soportado.\n"
                f"Formatos válidos: {', '.join(self.formatos_soportados)}")
            return False
        
        # Verificar tamaño
        file_size = os.path.getsize(filepath)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            messagebox.showerror("❌ Archivo muy grande", 
                f"El archivo es demasiado grande ({file_size / 1024 / 1024:.1f}MB).\n"
                f"Tamaño máximo: 10MB")
            return False
        
        # Verificar que se pueda abrir
        try:
            with Image.open(filepath) as img:
                # Verificar dimensiones
                if img.width > 4000 or img.height > 4000:
                    messagebox.showwarning("⚠️ Imagen muy grande", 
                        "La imagen tiene dimensiones muy grandes.\n"
                        "Se recomienda usar imágenes de menos de 2000x2000 píxeles")
                
                logger.debug(f"Imagen válida: {img.size}, {img.mode}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", 
                f"No se pudo abrir la imagen:\n{str(e)}")
            return False
        
        return True
    
    def restablecer_imagenes(self, parent_window=None) -> bool:
        """Restablece las imágenes a las predeterminadas"""
        respuesta = messagebox.askyesno("🔄 Restablecer Imágenes", 
            "¿Estás seguro de restablecer las imágenes a las predeterminadas?",
            parent=parent_window)
        
        if respuesta:
            self.app.encabezado_personalizado = None
            self.app.insignia_personalizada = None
            
            # Actualizar UI
            if hasattr(self.app, 'enc_custom_label'):
                self.app.enc_custom_label.configure(text="Encabezado: ⏸️ No cargado")
            if hasattr(self.app, 'ins_custom_label'):
                self.app.ins_custom_label.configure(text="Insignia: ⏸️ No cargado")
            
            # Limpiar cache si existe
            if hasattr(image_cache, 'clear_image_cache'):
                image_cache.clear_image_cache()
            
            logger.info("Imágenes restablecidas a predeterminadas")
            messagebox.showinfo("✅ Restablecido", 
                "Imágenes restablecidas a las predeterminadas")
            return True
        
        return False
    
    def actualizar_opacidad_preview(self, valor: float):
        """Actualiza la opacidad de la marca de agua"""
        self.app.watermark_opacity = valor
        
        # Actualizar label si existe
        if hasattr(self.app, 'opacity_label'):
            self.app.opacity_label.configure(text=f"{int(valor * 100)}%")
        
        logger.debug(f"Opacidad actualizada: {valor}")
    
    def obtener_ruta_imagen(self, tipo: str) -> Optional[str]:
        """
        Obtiene la ruta de una imagen (personalizada o base)
        
        Args:
            tipo: 'encabezado' o 'insignia'
            
        Returns:
            str: Ruta de la imagen o None
        """
        if tipo == "encabezado":
            # Primero personalizada, luego base
            return (self.app.encabezado_personalizado or 
                   self.app.ruta_encabezado)
        elif tipo == "insignia":
            return (self.app.insignia_personalizada or 
                   self.app.ruta_insignia)
        
        return None
    
    def generar_preview_imagen(self, tipo: str) -> Optional[Tuple[int, int]]:
        """
        Genera información de preview de una imagen
        
        Returns:
            Tuple[int, int]: (ancho, alto) o None
        """
        ruta = self.obtener_ruta_imagen(tipo)
        
        if ruta and os.path.exists(ruta):
            try:
                with Image.open(ruta) as img:
                    return img.size
            except Exception as e:
                logger.error(f"Error obteniendo info de imagen: {e}")
        
        return None
    
    def exportar_configuracion_imagenes(self) -> dict:
        """Exporta la configuración actual de imágenes"""
        return {
            'encabezado_personalizado': self.app.encabezado_personalizado,
            'insignia_personalizada': self.app.insignia_personalizada,
            'watermark_opacity': self.app.watermark_opacity,
            'watermark_stretch': self.app.watermark_stretch,
            'watermark_mode': self.app.watermark_mode
        }
    
    def importar_configuracion_imagenes(self, config: dict):
        """Importa configuración de imágenes"""
        if 'encabezado_personalizado' in config:
            self.app.encabezado_personalizado = config['encabezado_personalizado']
        
        if 'insignia_personalizada' in config:
            self.app.insignia_personalizada = config['insignia_personalizada']
        
        if 'watermark_opacity' in config:
            self.app.watermark_opacity = config['watermark_opacity']
        
        if 'watermark_stretch' in config:
            self.app.watermark_stretch = config['watermark_stretch']
        
        if 'watermark_mode' in config:
            self.app.watermark_mode = config['watermark_mode']
        
        logger.info("Configuración de imágenes importada")