"""
Tests para el módulo de referencias
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.references import ReferenceManager

class TestReferenceManager(unittest.TestCase):
    """Tests para ReferenceManager"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.ref_manager = ReferenceManager()
    
    def test_agregar_referencia_valida(self):
        """Test agregar una referencia válida"""
        ref_data = {
            'tipo': 'Libro',
            'autor': 'García, J.',
            'año': '2023',
            'titulo': 'Introducción a Python',
            'fuente': 'Editorial Tech'
        }
        
        referencia = self.ref_manager.agregar_referencia(ref_data)
        
        self.assertEqual(len(self.ref_manager.referencias), 1)
        self.assertEqual(referencia['autor'], 'García, J.')
    
    def test_agregar_referencia_sin_campos_requeridos(self):
        """Test agregar referencia sin campos requeridos"""
        ref_data = {
            'tipo': 'Libro',
            'autor': '',  # Campo vacío
            'año': '2023',
            'titulo': 'Test',
            'fuente': 'Test'
        }
        
        with self.assertRaises(ValueError) as context:
            self.ref_manager.agregar_referencia(ref_data)
        
        self.assertIn("El campo 'autor' es requerido", str(context.exception))
    
    def test_validar_formato_autor(self):
        """Test validación de formato de autor"""
        # Formatos válidos
        self.assertTrue(self.ref_manager._validar_formato_autor('García, J.'))
        self.assertTrue(self.ref_manager._validar_formato_autor('García López, J. M.'))
        self.assertTrue(self.ref_manager._validar_formato_autor('García, J. y López, M.'))
        
        # Formatos inválidos
        self.assertFalse(self.ref_manager._validar_formato_autor('García'))
        self.assertFalse(self.ref_manager._validar_formato_autor('J. García'))
        self.assertFalse(self.ref_manager._validar_formato_autor('garcia, j.'))  # Minúsculas
    
    def test_generar_apa_format(self):
        """Test generación de formato APA"""
        referencia = {
            'tipo': 'Libro',
            'autor': 'García, J.',
            'año': '2023',
            'titulo': 'Introducción a Python',
            'fuente': 'Editorial Tech'
        }
        
        apa = self.ref_manager.generar_apa_format(referencia)
        expected = "García, J. (2023). Introducción a Python. Editorial Tech."
        
        self.assertEqual(apa, expected)
    
    def test_ordenar_referencias(self):
        """Test ordenamiento de referencias"""
        # Agregar referencias desordenadas
        refs = [
            {'autor': 'Zúñiga, A.', 'año': '2021', 'titulo': 'Test 1', 'fuente': 'Test'},
            {'autor': 'Álvarez, B.', 'año': '2022', 'titulo': 'Test 2', 'fuente': 'Test'},
            {'autor': 'García, C.', 'año': '2023', 'titulo': 'Test 3', 'fuente': 'Test'}
        ]
        
        for ref in refs:
            self.ref_manager.agregar_referencia(ref)
        
        # Ordenar por autor
        self.ref_manager.ordenar_referencias('autor')
        
        # Verificar orden
        self.assertEqual(self.ref_manager.referencias[0]['autor'], 'Álvarez, B.')
        self.assertEqual(self.ref_manager.referencias[1]['autor'], 'García, C.')
        self.assertEqual(self.ref_manager.referencias[2]['autor'], 'Zúñiga, A.')
    
    def test_buscar_referencias(self):
        """Test búsqueda de referencias"""
        refs = [
            {'autor': 'García, J.', 'año': '2023', 'titulo': 'Python Avanzado', 'fuente': 'Tech Books'},
            {'autor': 'López, M.', 'año': '2022', 'titulo': 'JavaScript Moderno', 'fuente': 'Web Dev'},
            {'autor': 'Martínez, P.', 'año': '2023', 'titulo': 'Python para Ciencia', 'fuente': 'Science Pub'}
        ]
        
        for ref in refs:
            self.ref_manager.agregar_referencia(ref)
        
        # Buscar por término "Python"
        resultados = self.ref_manager.buscar_referencias('python')
        
        self.assertEqual(len(resultados), 2)
        self.assertTrue(all('Python' in r[1]['titulo'] for r in resultados))
    
    def test_eliminar_referencia(self):
        """Test eliminar referencia"""
        ref_data = {
            'tipo': 'Libro',
            'autor': 'García, J.',
            'año': '2023',
            'titulo': 'Test',
            'fuente': 'Test'
        }
        
        self.ref_manager.agregar_referencia(ref_data)
        self.assertEqual(len(self.ref_manager.referencias), 1)
        
        # Eliminar
        eliminada = self.ref_manager.eliminar_referencia(0)
        
        self.assertEqual(len(self.ref_manager.referencias), 0)
        self.assertEqual(eliminada['autor'], 'García, J.')
    
    def test_generar_estadisticas(self):
        """Test generación de estadísticas"""
        refs = [
            {'tipo': 'Libro', 'autor': 'A, A.', 'año': '2020', 'titulo': 'T1', 'fuente': 'F1'},
            {'tipo': 'Libro', 'autor': 'B, B.', 'año': '2021', 'titulo': 'T2', 'fuente': 'F2'},
            {'tipo': 'Artículo', 'autor': 'C, C.', 'año': '2023', 'titulo': 'T3', 'fuente': 'F3'}
        ]
        
        for ref in refs:
            self.ref_manager.agregar_referencia(ref)
        
        stats = self.ref_manager.generar_estadisticas()
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['por_tipo']['Libro'], 2)
        self.assertEqual(stats['por_tipo']['Artículo'], 1)
        self.assertEqual(stats['rango_años'], '2020-2023')

if __name__ == '__main__':
    unittest.main()