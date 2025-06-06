#!/usr/bin/env python3
"""
Script de configuración e instalación de dependencias para el sistema 
de optimización de horarios con soporte para PDF.
"""

import subprocess
import sys
import os

def instalar_dependencias():
    """
    Instala las dependencias necesarias.
    """
    print("Instalando dependencias necesarias...")
    
    dependencias = [
        'pandas',
        'numpy', 
        'matplotlib',
        'openpyxl',  # Para trabajar con archivos Excel
        'PyMuPDF',   # Para leer archivos PDF (fitz)
        'xlsxwriter' # Para escribir archivos Excel con formato
    ]
    
    for dependencia in dependencias:
        try:
            print(f"Instalando {dependencia}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependencia])
            print(f"✓ {dependencia} instalado correctamente")
        except subprocess.CalledProcessError:
            print(f"✗ Error al instalar {dependencia}")
            return False
    
    print("\n✓ Todas las dependencias instaladas correctamente!")
    return True

def verificar_instalacion():
    """
    Verifica que todas las dependencias estén correctamente instaladas.
    """
    print("\nVerificando instalación...")
    
    modulos = {
        'pandas': 'pd',
        'numpy': 'np',
        'matplotlib.pyplot': 'plt',
        'fitz': 'fitz',  # PyMuPDF
        'openpyxl': 'openpyxl'
    }
    
    errores = []
    
    for modulo, alias in modulos.items():
        try:
            if alias == 'pd':
                import pandas as pd
            elif alias == 'np':
                import numpy as np
            elif alias == 'plt':
                import matplotlib.pyplot as plt
            elif alias == 'fitz':
                import fitz
            elif alias == 'openpyxl':
                import openpyxl
            
            print(f"✓ {modulo}")
        except ImportError as e:
            print(f"✗ {modulo}: {e}")
            errores.append(modulo)
    
    if errores:
        print(f"\n⚠ Errores en: {', '.join(errores)}")
        return False
    else:
        print("\n✓ Todos los módulos verificados correctamente!")
        return True

def crear_estructura_proyecto():
    """
    Crea la estructura de archivos necesaria para el proyecto.
    """
    print("\nCreando estructura del proyecto...")
    
    archivos_necesarios = [
        'lector_pdf_horarios.py',
        'pg_desde_cero.py', 
        'generador_carga_horaria.py',
        'ejecutar_optimizador.py'
    ]
    
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            print(f"⚠ Archivo faltante: {archivo}")
        else:
            print(f"✓ {archivo}")

def crear_archivo_requirements():
    """
    Crea un archivo requirements.txt para instalación futura.
    """
    requirements_content = """# Dependencias para el Sistema de Optimización de Horarios
pandas>=1.5.0
numpy>=1.20.0
matplotlib>=3.5.0
openpyxl>=3.0.0
PyMuPDF>=1.20.0
xlsxwriter>=3.0.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✓ Archivo requirements.txt creado")

def mostrar_instrucciones():
    """
    Muestra las instrucciones de uso del sistema.
    """
    print("\n" + "="*60)
    print("INSTRUCCIONES DE USO")
    print("="*60)
    
    print("""
ARCHIVOS PRINCIPALES:
├── lector_pdf_horarios.py      - Módulo para leer archivos PDF
├── pg_desde_cero.py           - Sistema de programación genética
├── sistema_optimizacion_pdf.py - Sistema integrado con soporte PDF
├── generador_carga_horaria.py - Generador de datos de ejemplo
└── ejecutar_optimizador.py   - Script de ejecución original

COMANDOS PRINCIPALES:

1. Para procesar un archivo PDF:
   python sistema_optimizacion_pdf.py Horarios_2023_1.pdf

2. Para usar un archivo Excel (formato original):
   python sistema_optimizacion_pdf.py archivo.xlsx

3. Para generar datos de ejemplo:
   python generador_carga_horaria.py

4. Para usar el sistema original:
   python ejecutar_optimizador.py

FLUJO DE TRABAJO RECOMENDADO:

1. Si tiene un PDF con horarios académicos:
   → Use: python sistema_optimizacion_pdf.py archivo.pdf
   
2. El sistema automáticamente:
   - Extraerá los cursos del PDF
   - Los convertirá al formato requerido
   - Permitirá seleccionar cursos para optimizar
   - Ejecutará el algoritmo genético
   - Mostrará los resultados optimizados

3. Puede guardar los resultados en Excel para uso posterior

FORMATOS SOPORTADOS:
- PDF: Archivos con tablas de horarios académicos
- Excel: Formato de matriz horaria (compatible con versión original)

SELECCIÓN DE CURSOS:
- Por ID individual: 1, 5, 10
- Por rango: 1-10 (cursos del 1 al 10)
- Por escuela: BF (todos los cursos de Física)
- Escribir 'fin' para terminar la selección
""")

def main():
    """
    Función principal del script de configuración.
    """
    print("CONFIGURACIÓN DEL SISTEMA DE OPTIMIZACIÓN DE HORARIOS")
    print("Soporte para archivos PDF y Excel")
    print("="*60)
    
    print("\n1. Instalando dependencias...")
    if not instalar_dependencias():
        print("Error en la instalación. Abortando.")
        return
    
    print("\n2. Verificando instalación...")
    if not verificar_instalacion():
        print("Error en la verificación. Algunas dependencias faltan.")
        return
    
    print("\n3. Verificando estructura del proyecto...")
    crear_estructura_proyecto()
    
    print("\n4. Creando archivo requirements.txt...")
    crear_archivo_requirements()
    
    print("\n5. Configuración completada!")
    mostrar_instrucciones()
    
    # Preguntar si quiere ejecutar una prueba
    respuesta = input("\n¿Desea ejecutar una prueba con datos de ejemplo? (s/n): ")
    if respuesta.lower() == 's':
        print("\nGenerando datos de ejemplo...")
        try:
            import generadores.generador_basico as generador_basico
            generador_basico.generar_carga_horaria_ejemplo()
            print("✓ Datos de ejemplo generados")
            print("\nAhora puede ejecutar:")
            print("python sistema_optimizacion_pdf.py carga_horaria_ejemplo.xlsx")
        except Exception as e:
            print(f"Error al generar datos de ejemplo: {e}")

if __name__ == "__main__":
    main()