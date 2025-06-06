#!/usr/bin/env python3
"""
Script para crear automáticamente la estructura completa del proyecto
de optimización de horarios con programación genética.
"""

import os
import sys
from pathlib import Path

def crear_estructura_proyecto():
    """Crea la estructura completa de directorios y archivos."""
    
    print("🏗️  Creando estructura del proyecto...")
    
    # Definir la estructura de directorios
    directorios = [
        "core",
        "generadores", 
        "interfaces",
        "visualizacion",
        "scripts",
        "datos",
        "datos/resultados",
        "ejemplos",
        "tests",
        "docs",
        "docs/imagenes",
        "setup_y_configuracion"
    ]
    
    # Crear directorios
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
        print(f"📁 Creado: {directorio}/")
        
        # Crear __init__.py para paquetes Python
        if directorio in ["core", "generadores", "interfaces", "visualizacion", "tests"]:
            init_file = Path(directorio) / "__init__.py"
            init_file.touch()
            print(f"📄 Creado: {init_file}")

def crear_archivos_configuracion():
    """Crea archivos de configuración del proyecto."""
    
    # requirements.txt
    requirements_content = """# Dependencias para el Sistema de Optimización de Horarios
pandas>=1.5.0
numpy>=1.20.0
matplotlib>=3.5.0
openpyxl>=3.0.0
PyMuPDF>=1.20.0
xlsxwriter>=3.0.0
pytest>=7.0.0
seaborn>=0.11.0
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    print("📄 Creado: requirements.txt")
    
    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Sistema
.DS_Store
Thumbs.db

# Archivos temporales del proyecto
datos/temp_*
datos/resultados/temp_*
*.tmp
temp_*
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("📄 Creado: .gitignore")

def crear_readme_principal():
    """Crea el README.md principal del proyecto."""
    
    readme_content = """# 🎓 Sistema de Optimización de Horarios Académicos

Sistema avanzado de optimización de horarios académicos utilizando programación genética, con soporte para archivos PDF y Excel, y detección automática de conflictos.

## 🚀 Características Principales

- **📄 Lectura de PDF**: Procesa automáticamente archivos PDF con horarios académicos
- **📊 Soporte Excel**: Compatible con archivos Excel en formato de matriz
- **🧬 Algoritmo Genético**: Optimización inteligente usando programación genética  
- **🔍 Detección de Conflictos**: Identifica y resuelve cruces de horarios automáticamente
- **📈 Visualización**: Gráficos interactivos y reportes detallados
- **🎯 Selección Flexible**: Selección por curso, rango o escuela completa

## 🔧 Instalación Rápida

```bash
# 1. Instalar dependencias automáticamente
python setup_y_configuracion/requirements_setup.py

# 2. Verificar instalación
python setup_y_configuracion/verificar_instalacion.py

# 3. Ejecutar ejemplo
python scripts/optimizar.py
```

## 🖥️ Uso del Sistema

### Procesar archivo PDF
```bash
python scripts/optimizar.py datos/Horarios_2023_1.pdf
```

### Procesar archivo Excel
```bash
python scripts/optimizar.py datos/carga_horaria.xlsx
```

### Generar datos de prueba
```bash
python scripts/optimizar.py
```

## 📊 Tipos de Conflictos Detectados

- ✅ **Profesores**: Clases simultáneas del mismo profesor
- ✅ **Salones**: Múltiples clases en el mismo salón
- ✅ **Sobrecarga**: Profesores con exceso de horas
- ✅ **Distribución**: Optimización de carga semanal

## 🏗️ Estructura del Proyecto

```
📦 optimizador-horarios-genetico/
├── 🧠 core/                    # Módulos principales
├── 🎲 generadores/             # Generadores de datos
├── 🖥️ interfaces/              # Interfaces de usuario
├── 📊 visualizacion/           # Gráficos y reportes
├── 🚀 scripts/                 # Scripts de ejecución
├── 📁 datos/                   # Archivos de datos
├── 🧪 ejemplos/                # Ejemplos de uso
└── 📚 docs/                    # Documentación
```

## 🧪 Ejemplos de Uso

Ver el directorio `ejemplos/` para casos de uso específicos:

- `ejemplo_completo.py` - Flujo completo del sistema
- `ejemplo_pdf.py` - Procesamiento de PDF  
- `ejemplo_excel.py` - Procesamiento de Excel

## 🤝 Contribuciones

Este proyecto fue desarrollado como sistema académico para optimización de horarios universitarios.

## 📄 Licencia

Proyecto Académico - Universidad Nacional Mayor de San Marcos  
Facultad de Ciencias Físicas

---
**Desarrollado por**: Equipo de Programación Genética  
**Versión**: 2.0 con detección de conflictos
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("📄 Creado: README.md")

def crear_scripts_principales():
    """Crea los scripts principales de ejecución."""
    
    # Script principal de optimización
    optimizar_content = """#!/usr/bin/env python3
\"\"\"
Script principal para ejecutar el sistema de optimización de horarios.
Detecta automáticamente el tipo de archivo y ejecuta el proceso completo.
\"\"\"

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.sistema_completo import SistemaOptimizacionCompleto

def main():
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        if archivo in ['--help', '-h']:
            mostrar_ayuda()
            return
    else:
        archivo = None
    
    # Ejecutar sistema
    sistema = SistemaOptimizacionCompleto()
    sistema.ejecutar(archivo)

def mostrar_ayuda():
    print(\"\"\"
🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS
================================================

USO:
    python scripts/optimizar.py [archivo]

EJEMPLOS:
    python scripts/optimizar.py datos/Horarios_2023_1.pdf
    python scripts/optimizar.py datos/carga_horaria.xlsx
    python scripts/optimizar.py                           # Genera datos de prueba

TIPOS DE ARCHIVO SOPORTADOS:
    • PDF con horarios académicos
    • Excel con matriz de horarios
    • Sin archivo (genera datos automáticamente)
\"\"\")

if __name__ == "__main__":
    main()
"""
    
    with open("scripts/optimizar.py", "w", encoding="utf-8") as f:
        f.write(optimizar_content)
    print("📄 Creado: scripts/optimizar.py")
    
    # Script para generar datos
    generar_datos_content = """#!/usr/bin/env python3
\"\"\"
Script para generar datos de prueba con diferentes niveles de complejidad.
\"\"\"

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generadores.generador_avanzado import GeneradorCargaHorariaAvanzado

def main():
    print("🎲 GENERADOR DE DATOS DE PRUEBA")
    print("="*40)
    
    # Opciones de generación
    print("Opciones disponibles:")
    print("1. Datos básicos (30 cursos)")
    print("2. Datos medios (60 cursos)")  
    print("3. Datos complejos (100 cursos)")
    print("4. Datos personalizados")
    
    opcion = input("\\nSeleccione opción (1-4): ").strip()
    
    if opcion == "1":
        num_cursos = 6
    elif opcion == "2":
        num_cursos = 12
    elif opcion == "3":
        num_cursos = 20
    elif opcion == "4":
        try:
            num_cursos = int(input("Número de cursos por escuela: "))
        except ValueError:
            print("❌ Número inválido, usando 10")
            num_cursos = 10
    else:
        print("❌ Opción inválida, usando configuración básica")
        num_cursos = 6
    
    # Generar datos
    generador = GeneradorCargaHorariaAvanzado()
    cursos = generador.generar_carga_completa(num_cursos_por_escuela=num_cursos)
    
    # Detectar conflictos
    conflictos = generador.detectar_conflictos(cursos)
    generador.generar_reporte_conflictos(conflictos)
    
    # Exportar
    archivo = f"datos/carga_horaria_generada_{num_cursos*5}cursos.xlsx"
    generador.exportar_a_excel(cursos, archivo)
    
    print(f"\\n✅ Datos generados y guardados en: {archivo}")

if __name__ == "__main__":
    main()
"""
    
    with open("scripts/generar_datos.py", "w", encoding="utf-8") as f:
        f.write(generar_datos_content)
    print("📄 Creado: scripts/generar_datos.py")

def crear_ejemplo_completo():
    """Crea un ejemplo completo del sistema."""
    
    ejemplo_content = """#!/usr/bin/env python3
\"\"\"
Ejemplo completo del sistema de optimización de horarios.
Demuestra todas las funcionalidades principales.
\"\"\"

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.sistema_completo import SistemaOptimizacionCompleto
from generadores.generador_avanzado import GeneradorCargaHorariaAvanzado

def ejemplo_datos_generados():
    \"\"\"Ejemplo usando datos generados automáticamente.\"\"\"
    
    print("🧪 EJEMPLO: Datos Generados Automáticamente")
    print("="*50)
    
    # Crear sistema
    sistema = SistemaOptimizacionCompleto()
    
    # Generar datos de prueba
    print("Generando datos de prueba...")
    if sistema.generar_datos_prueba():
        print("✅ Datos generados exitosamente")
        
        # Mostrar cursos disponibles
        sistema.mostrar_cursos_disponibles()
        
        # Selección automática de algunos cursos
        cursos_disponibles = sistema.obtener_cursos_disponibles()
        if cursos_disponibles:
            # Seleccionar primeros 10 cursos automáticamente
            cursos_seleccionados = list(cursos_disponibles.keys())[:10]
            print(f"\\n🎯 Seleccionados automáticamente: {len(cursos_seleccionados)} cursos")
            
            # Ejecutar optimización
            horario, conflictos = sistema.ejecutar_optimizacion(cursos_seleccionados)
            
            if horario:
                # Mostrar resultados
                sistema.analizar_resultados(horario, conflictos)
                sistema.mostrar_horario_tabla(horario)
                
                # Guardar resultado
                sistema.guardar_horario_excel(horario)
                print("\\n✅ Ejemplo completado exitosamente!")
            else:
                print("❌ No se pudo generar horario optimizado")
        else:
            print("❌ No se encontraron cursos disponibles")
    else:
        print("❌ Error al generar datos de prueba")

def ejemplo_interactivo():
    \"\"\"Ejemplo con selección interactiva del usuario.\"\"\"
    
    print("\\n🎮 EJEMPLO: Modo Interactivo")
    print("="*50)
    
    sistema = SistemaOptimizacionCompleto()
    sistema.ejecutar()

def main():
    print("🎓 EJEMPLOS DEL SISTEMA DE OPTIMIZACIÓN")
    print("="*50)
    
    print("\\nOpciones de ejemplo:")
    print("1. Ejemplo automático (sin interacción)")
    print("2. Ejemplo interactivo completo")
    print("3. Ambos ejemplos")
    
    opcion = input("\\nSeleccione opción (1-3): ").strip()
    
    if opcion == "1":
        ejemplo_datos_generados()
    elif opcion == "2":
        ejemplo_interactivo()
    elif opcion == "3":
        ejemplo_datos_generados()
        input("\\n⏸️  Presione Enter para continuar con el ejemplo interactivo...")
        ejemplo_interactivo()
    else:
        print("❌ Opción inválida, ejecutando ejemplo automático")
        ejemplo_datos_generados()

if __name__ == "__main__":
    main()
"""
    
    with open("ejemplos/ejemplo_completo.py", "w", encoding="utf-8") as f:
        f.write(ejemplo_content)
    print("📄 Creado: ejemplos/ejemplo_completo.py")

def crear_setup_verificacion():
    """Crea scripts de setup y verificación."""
    
    # Ya tenemos requirements_setup.py, crear verificador
    verificador_content = """#!/usr/bin/env python3
\"\"\"
Script para verificar que la instalación esté completa y funcional.
\"\"\"

import sys
import os
import importlib

def verificar_dependencias():
    \"\"\"Verifica que todas las dependencias estén instaladas.\"\"\"
    
    dependencias = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('openpyxl', 'openpyxl'),
        ('fitz', 'fitz'),  # PyMuPDF
        ('xlsxwriter', 'xlsxwriter')
    ]
    
    errores = []
    
    print("🔍 Verificando dependencias...")
    
    for modulo, alias in dependencias:
        try:
            importlib.import_module(modulo)
            print(f"✅ {modulo}")
        except ImportError:
            print(f"❌ {modulo}")
            errores.append(modulo)
    
    return len(errores) == 0

def verificar_estructura():
    \"\"\"Verifica que la estructura de archivos esté completa.\"\"\"
    
    directorios_requeridos = [
        'core', 'generadores', 'interfaces', 'visualizacion',
        'scripts', 'datos', 'ejemplos'
    ]
    
    print("\\n🏗️  Verificando estructura del proyecto...")
    
    errores = []
    for directorio in directorios_requeridos:
        if os.path.isdir(directorio):
            print(f"✅ {directorio}/")
        else:
            print(f"❌ {directorio}/")
            errores.append(directorio)
    
    return len(errores) == 0

def verificar_modulos():
    \"\"\"Verifica que los módulos principales se puedan importar.\"\"\"
    
    print("\\n🧠 Verificando módulos del proyecto...")
    
    # Agregar directorio actual al path
    sys.path.insert(0, os.getcwd())
    
    modulos_proyecto = [
        'core.validador_conflictos',
        'generadores.generador_avanzado', 
        'interfaces.sistema_completo'
    ]
    
    errores = []
    for modulo in modulos_proyecto:
        try:
            importlib.import_module(modulo)
            print(f"✅ {modulo}")
        except ImportError as e:
            print(f"❌ {modulo} - {e}")
            errores.append(modulo)
    
    return len(errores) == 0

def ejecutar_prueba_basica():
    \"\"\"Ejecuta una prueba básica del sistema.\"\"\"
    
    print("\\n🧪 Ejecutando prueba básica...")
    
    try:
        from generadores.generador_avanzado import GeneradorCargaHorariaAvanzado
        
        generador = GeneradorCargaHorariaAvanzado()
        cursos = generador.generar_carga_completa(num_cursos_por_escuela=2)
        
        if len(cursos) > 0:
            print(f"✅ Generación de datos: {len(cursos)} cursos creados")
            return True
        else:
            print("❌ Error en generación de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        return False

def main():
    print("🔧 VERIFICADOR DE INSTALACIÓN")
    print("="*40)
    
    # Ejecutar verificaciones
    dependencias_ok = verificar_dependencias()
    estructura_ok = verificar_estructura()
    modulos_ok = verificar_modulos()
    prueba_ok = ejecutar_prueba_basica()
    
    # Resumen final
    print(f"\n📊 RESUMEN DE VERIFICACIÓN")
    print("="*30)
    print(f"Dependencias: {'✅' if dependencias_ok else '❌'}")
    print(f"Estructura: {'✅' if estructura_ok else '❌'}")
    print(f"Módulos: {'✅' if modulos_ok else '❌'}")
    print(f"Prueba básica: {'✅' if prueba_ok else '❌'}")
    
    if all([dependencias_ok, estructura_ok, modulos_ok, prueba_ok]):
        print(f"\n🎉 ¡INSTALACIÓN COMPLETA Y FUNCIONAL!")
        print("Puede ejecutar:")
        print("  python scripts/optimizar.py")
        print("  python ejemplos/ejemplo_completo.py")
    else:
        print(f"\n⚠️  INSTALACIÓN INCOMPLETA")
        print("Ejecute: python setup_y_configuracion/requirements_setup.py")
        
        if not estructura_ok:
            print("Y asegúrese de tener todos los archivos del proyecto")

if __name__ == "__main__":
    main()
"""
    
    with open("setup_y_configuracion/verificar_instalacion.py", "w", encoding="utf-8") as f:
        f.write(verificador_content)
    print("📄 Creado: setup_y_configuracion/verificar_instalacion.py")

def crear_documentacion():
    """Crea documentación adicional."""
    
    # Manual de usuario
    manual_content = """# 📖 Manual de Usuario - Sistema de Optimización de Horarios

## 🚀 Inicio Rápido

### 1. Instalación
```bash
python setup_y_configuracion/requirements_setup.py
```

### 2. Verificación
```bash
python setup_y_configuracion/verificar_instalacion.py
```

### 3. Primer Uso
```bash
python scripts/optimizar.py
```

## 📋 Uso Detallado

### Procesar Archivo PDF
```bash
python scripts/optimizar.py datos/Horarios_2023_1.pdf
```

El sistema automáticamente:
1. Extrae cursos del PDF
2. Identifica horarios, profesores y salones
3. Permite seleccionar cursos
4. Optimiza el horario
5. Muestra resultados y conflictos

### Procesar Archivo Excel
```bash
python scripts/optimizar.py datos/carga_horaria.xlsx
```

### Generar Datos de Prueba
```bash
python scripts/generar_datos.py
```

## 🎯 Selección de Cursos

Durante la ejecución puede seleccionar cursos usando:

- **IDs individuales**: `1, 5, 10, 15`
- **Rangos**: `1-20` (cursos del 1 al 20)
- **Por escuela**: `BF` (todos los cursos de Física)
- **Todos**: `todos` (seleccionar todos los cursos)
- **Finalizar**: `fin`

## 📊 Interpretación de Resultados

### Métricas de Calidad
- **Bloques ocupados**: Número total de horas asignadas
- **Tiempos muertos**: Espacios vacíos entre clases
- **Compactación**: Qué tan agrupadas están las clases
- **Distribución**: Uniformidad de carga semanal

### Tipos de Conflictos
- **🧑‍🏫 Profesor**: Mismo profesor en dos lugares simultáneamente
- **🏫 Salón**: Mismo salón con múltiples clases
- **⚡ Sobrecarga**: Profesores con exceso de horas

### Valores Ideales
- **Tiempos muertos**: 0-2 (excelente), 3-5 (bueno), 6+ (mejorable)
- **Conflictos**: 0 (perfecto), 1-2 (aceptable), 3+ (requiere revisión)

## 🔧 Solución de Problemas

### "Error al leer PDF"
- Verifique que el PDF no esté protegido
- Asegúrese de que contenga texto seleccionable

### "No se encontraron cursos"
- Revise el formato del archivo
- Pruebe con datos generados: `python scripts/optimizar.py`

### "Optimización sin resultados"
- Reduzca el número de cursos seleccionados
- Verifique que no haya demasiados conflictos iniciales

## 📁 Archivos Generados

El sistema crea automáticamente:
- `datos/resultados/horario_optimizado_*.xlsx` - Horarios optimizados
- `datos/resultados/reporte_conflictos_*.txt` - Reportes de conflictos
- `datos/carga_horaria_generada_*.xlsx` - Datos de prueba generados

## 🎮 Ejemplos Interactivos

```bash
# Ejemplo completo automático
python ejemplos/ejemplo_completo.py

# Ejemplo específico para PDF
python ejemplos/ejemplo_pdf.py

# Ejemplo específico para Excel  
python ejemplos/ejemplo_excel.py
```
"""
    
    with open("docs/manual_usuario.md", "w", encoding="utf-8") as f:
        f.write(manual_content)
    print("📄 Creado: docs/manual_usuario.md")

def crear_pruebas_basicas():
    """Crea pruebas unitarias básicas."""
    
    test_validador_content = """#!/usr/bin/env python3
\"\"\"
Pruebas unitarias para el validador de conflictos.
\"\"\"

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.validador_conflictos import ValidadorConflictos

def test_detectar_conflictos_vacio():
    \"\"\"Prueba con horario vacío.\"\"\"
    horario = [[None for _ in range(14)] for _ in range(5)]
    conflictos = ValidadorConflictos.detectar_conflictos_horario(horario)
    
    assert len(conflictos['profesor']) == 0
    assert len(conflictos['salon']) == 0

def test_detectar_conflicto_profesor():
    \"\"\"Prueba detección de conflicto de profesor.\"\"\"
    horario = [[None for _ in range(14)] for _ in range(5)]
    
    # Mismo profesor en dos cursos simultáneos
    curso1 = {'id': 1, 'nombre': 'Curso A', 'profesor': 'GARCIA', 'tipo': 'Teórico'}
    curso2 = {'id': 2, 'nombre': 'Curso B', 'profesor': 'GARCIA', 'tipo': 'Teórico'}
    
    horario[0][0] = curso1  # Lunes 7:00
    horario[1][0] = curso2  # Martes 7:00 - No debería generar conflicto
    
    conflictos = ValidadorConflictos.detectar_conflictos_horario(horario)
    assert len(conflictos['profesor']) == 0  # Diferentes días, no hay conflicto
    
    # Ahora mismo día y hora
    horario[0][1] = curso2  # Lunes 8:00, mismo profesor
    horario[0][0] = [curso1, curso2]  # Simular conflicto en mismo bloque
    
def test_puntuacion_conflictos():
    \"\"\"Prueba cálculo de puntuación de conflictos.\"\"\"
    conflictos = {
        'profesor': [{'dia': 0, 'bloque': 0}],
        'salon': [],
        'estudiante': [],
        'sobrecarga': []
    }
    
    puntuacion = ValidadorConflictos.calcular_puntuacion_conflictos(conflictos)
    assert puntuacion == 100  # 1 conflicto de profesor = 100 puntos

if __name__ == "__main__":
    pytest.main([__file__])
"""
    
    with open("tests/test_validador.py", "w", encoding="utf-8") as f:
        f.write(test_validador_content)
    print("📄 Creado: tests/test_validador.py")

def main():
    """Función principal que ejecuta la creación completa."""
    
    print("🎓 CREADOR DE ESTRUCTURA DEL PROYECTO")
    print("Sistema de Optimización de Horarios Académicos")
    print("="*55)
    
    try:
        # Crear estructura de directorios
        crear_estructura_proyecto()
        
        print(f"\n📋 Creando archivos de configuración...")
        crear_archivos_configuracion()
        
        print(f"\n📖 Creando documentación...")
        crear_readme_principal()
        
        print(f"\n🚀 Creando scripts principales...")
        crear_scripts_principales()
        
        print(f"\n🧪 Creando ejemplos...")
        crear_ejemplo_completo()
        
        print(f"\n🔧 Creando setup y verificación...")
        crear_setup_verificacion()
        
        print(f"\n📚 Creando documentación adicional...")
        crear_documentacion()
        
        print(f"\n🧪 Creando pruebas básicas...")
        crear_pruebas_basicas()
        
        print(f"\n✅ ESTRUCTURA CREADA EXITOSAMENTE!")
        print("="*40)
        
        print(f"\n📋 Próximos pasos:")
        print("1. Copiar los archivos de código de los módulos principales")
        print("2. Ejecutar: python setup_y_configuracion/requirements_setup.py")
        print("3. Verificar: python setup_y_configuracion/verificar_instalacion.py") 
        print("4. Probar: python ejemplos/ejemplo_completo.py")
        
        print(f"\n📁 Archivos creados:")
        mostrar_estructura_creada()
        
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        import traceback
        traceback.print_exc()

def mostrar_estructura_creada():
    """Muestra la estructura de archivos creada."""
    
    print(f"\n📂 Estructura creada:")
    
    for root, dirs, files in os.walk("."):
        # Filtrar directorios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        
        sub_indent = " " * 2 * (level + 1)
        for file in sorted(files):
            if not file.startswith('.') and file != "crear_estructura.py":
                if file.endswith('.py'):
                    icon = "🐍"
                elif file.endswith('.md'):
                    icon = "📖"
                elif file.endswith('.txt'):
                    icon = "📄"
                else:
                    icon = "📄"
                print(f"{sub_indent}{icon} {file}")

if __name__ == "__main__":
    main()