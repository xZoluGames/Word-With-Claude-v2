#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.logger import get_logger

logger = get_logger("main")

"""
Generador de Proyectos Académicos - Punto de entrada principal
"""
import customtkinter as ctk
from ui.main_window import ProyectoAcademicoGenerator

def main():
    # Configuración del tema
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ProyectoAcademicoGenerator()
    app.run()

if __name__ == "__main__":
    main()