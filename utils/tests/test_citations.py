"""
Tests para el módulo de citas
"""

import unittest
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.citations import CitationProcessor

class TestCitationProcessor(unittest.TestCase):
    """Tests para CitationProcessor"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.processor = CitationProcessor()
    
    def test_procesar_cita_parafraseo(self):
        """Test cita de parafraseo simple"""
        texto = "La educación es importante [CITA:parafraseo:García:2020]"
        resultado = self.processor.procesar_citas_avanzado(texto)
        self.assertIn("(García, 2020)", resultado)
        self.assertNotIn("[CITA:", resultado)
    
    def test_procesar_cita_textual_con_pagina(self):
        """Test cita textual con página"""
        texto = "Según el autor [CITA:textual:López:2019:45]"
        resultado = self.processor.procesar_citas_avanzado(texto)
        self.assertIn("(López, 2019, p. 45)", resultado)
    
    def test_procesar_multiples_citas(self):
        """Test múltiples citas en un texto"""
        texto = "Varios autores [CITA:parafraseo:García:2020] coinciden [CITA:parafraseo:López:2019]"
        resultado = self.processor.procesar_citas_avanzado(texto)
        self.assertIn("(García, 2020)", resultado)
        self.assertIn("(López, 2019)", resultado)
    
    def test_analizar_densidad_marco_teorico(self):
        """Test análisis de densidad para marco teórico"""
        texto = "Este es un texto de ejemplo con una cita (García, 2020) para analizar."
        analisis = self.processor.analizar_densidad_contextual(texto, 'marco_teorico')
        
        self.assertIn('densidad', analisis)
        self.assertIn('recomendacion', analisis)
        self.assertGreater(analisis['palabras_total'], 0)

if __name__ == '__main__':
    unittest.main()