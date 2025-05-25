"""
Script de utilidad para limpiar y actualizar el código del proyecto

Este script ayuda a:
- Limpiar imports no utilizados
- Agregar imports necesarios para logging y validación
- Verificar y actualizar docstrings
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Set, Tuple

# Imports que deben agregarse a cada tipo de archivo
REQUIRED_IMPORTS = {
    'modules': [
        'from utils.logger import get_logger',
        'from config.settings import *'
    ],
    'ui': [
        'from utils.logger import get_logger',
        'from config.settings import APP_CONFIG, BUTTON_COLORS'
    ],
    'core': [
        'from utils.logger import get_logger',
        'from utils.cache import cached',
        'from config.settings import *'
    ]
}

# Imports comunes no utilizados
UNUSED_IMPORTS = [
    'import sys',  # A menos que se use explícitamente
    'import platform',
    'from typing import *',  # Preferir imports específicos
]


class CodeCleaner:
    """Limpiador de código para el proyecto."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = list(self.project_root.rglob("*.py"))
        self.report = []
    
    def analyze_file(self, filepath: Path) -> Tuple[List[str], List[str]]:
        """
        Analiza un archivo Python para encontrar imports no utilizados.
        
        Returns:
            Tuple[List[str], List[str]]: (imports_no_usados, imports_faltantes)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return [], []
        
        # Encontrar todos los imports
        imports = []
        imported_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
                    imported_names.add(alias.asname or alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
                    imported_names.add(alias.asname or alias.name)
        
        # Verificar uso
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Imports no utilizados
        unused = imported_names - used_names
        unused_imports = [imp for imp in imports if any(name in imp for name in unused)]
        
        # Verificar imports faltantes
        missing_imports = []
        
        # Determinar tipo de archivo
        rel_path = filepath.relative_to(self.project_root)
        if rel_path.parts[0] in REQUIRED_IMPORTS:
            required = REQUIRED_IMPORTS[rel_path.parts[0]]
            for req_import in required:
                if req_import not in content:
                    missing_imports.append(req_import)
        
        # Verificar si usa logging sin importarlo
        if 'logger' in content and 'get_logger' not in content:
            missing_imports.append('from utils.logger import get_logger')
        
        return unused_imports, missing_imports
    
    def check_docstrings(self, filepath: Path) -> List[str]:
        """
        Verifica que las funciones y clases tengan docstrings.
        
        Returns:
            List[str]: Lista de elementos sin docstring
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        missing_docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Verificar si tiene docstring
                has_docstring = (
                    node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                
                if not has_docstring and not node.name.startswith('_'):
                    missing_docstrings.append(f"{node.__class__.__name__}: {node.name}")
        
        return missing_docstrings
    
    def update_button_colors(self, filepath: Path):
        """
        Actualiza los colores de botones para usar BUTTON_COLORS de settings.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar colores problemáticos
        color_patterns = [
            (r'"darkindigo"', '"#4B0082"'),
            (r'"darkpurple"', '"#8B008B"'),
            (r'"darkdarkblue"', '"#00008B"'),
        ]
        
        modified = False
        for pattern, replacement in color_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        if modified:
            # Agregar import si no existe
            if 'from config.settings import' not in content:
                lines = content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import') or line.startswith('from'):
                        import_index = i
                
                lines.insert(import_index + 1, 'from config.settings import BUTTON_COLORS')
                content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.report.append(f"✅ Actualizado colores en: {filepath}")
    
    def add_logging(self, filepath: Path):
        """
        Agrega logging básico a un archivo.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Si ya tiene logger, saltar
        if 'logger = get_logger' in content:
            return
        
        # Determinar nombre del módulo
        module_name = filepath.stem
        
        # Agregar imports y logger
        lines = content.split('\n')
        
        # Encontrar dónde insertar
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(('import', 'from', '#')):
                import_end = i
                break
        
        # Insertar import y logger
        lines.insert(import_end, '')
        lines.insert(import_end + 1, 'from utils.logger import get_logger')
        lines.insert(import_end + 2, '')
        lines.insert(import_end + 3, f'logger = get_logger("{module_name}")')
        lines.insert(import_end + 4, '')
        
        content = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.report.append(f"✅ Agregado logging a: {filepath}")
    
    def run_cleanup(self, fix: bool = False):
        """
        Ejecuta la limpieza en todos los archivos.
        
        Args:
            fix: Si True, aplica las correcciones automáticamente
        """
        print("🔍 Analizando archivos Python...")
        print("="*60)
        
        for filepath in self.python_files:
            # Saltar archivos de prueba y este script
            if 'test' in str(filepath) or 'cleanup' in str(filepath):
                continue
            
            print(f"\n📄 {filepath}")
            
            # Analizar imports
            unused, missing = self.analyze_file(filepath)
            if unused:
                print(f"  ❌ Imports no utilizados: {', '.join(unused)}")
            if missing:
                print(f"  ⚠️  Imports faltantes: {', '.join(missing)}")
            
            # Verificar docstrings
            missing_docs = self.check_docstrings(filepath)
            if missing_docs:
                print(f"  📝 Sin docstring: {', '.join(missing_docs[:5])}")
                if len(missing_docs) > 5:
                    print(f"     ... y {len(missing_docs) - 5} más")
            
            # Si es modo fix, aplicar correcciones
            if fix:
                # Actualizar colores si es archivo UI
                if 'ui' in str(filepath):
                    self.update_button_colors(filepath)
                
                # Agregar logging si no existe
                if 'utils' not in str(filepath):
                    self.add_logging(filepath)
        
        # Mostrar reporte
        if self.report:
            print("\n" + "="*60)
            print("📋 REPORTE DE CAMBIOS:")
            for item in self.report:
                print(item)
    
    def generate_import_report(self):
        """Genera un reporte de todos los imports del proyecto."""
        all_imports = {}
        
        for filepath in self.python_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(f"import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"from {module} import {alias.name}")
                
                if imports:
                    all_imports[str(filepath)] = imports
            except:
                pass
        
        # Guardar reporte
        with open('import_report.txt', 'w', encoding='utf-8') as f:
            f.write("REPORTE DE IMPORTS DEL PROYECTO\n")
            f.write("="*60 + "\n\n")
            
            for filepath, imports in sorted(all_imports.items()):
                f.write(f"{filepath}:\n")
                for imp in sorted(set(imports)):
                    f.write(f"  - {imp}\n")
                f.write("\n")
        
        print("✅ Reporte de imports generado: import_report.txt")


def main():
    """Función principal del script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Limpiador de código del proyecto")
    parser.add_argument('--fix', action='store_true', help='Aplicar correcciones automáticas')
    parser.add_argument('--report', action='store_true', help='Generar reporte de imports')
    parser.add_argument('--path', default='.', help='Ruta del proyecto')
    
    args = parser.parse_args()
    
    cleaner = CodeCleaner(args.path)
    
    if args.report:
        cleaner.generate_import_report()
    else:
        cleaner.run_cleanup(fix=args.fix)


if __name__ == "__main__":
    main()