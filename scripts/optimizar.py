#!/usr/bin/env python3
"""
Script principal para ejecutar el sistema de optimización de horarios.
Detecta automáticamente el tipo de archivo y ejecuta el proceso completo.
"""

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
    print("""
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
""")

if __name__ == "__main__":
    main()
