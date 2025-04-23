#!/usr/bin/env python3
"""
Script para ejecutar el optimizador de horarios con programación genética.
"""

import os
import sys
from generador_carga_horaria import generar_carga_horaria_ejemplo
from pg_desde_cero import SistemaOptimizacionHorarios

def mostrar_ayuda():
    print("""
Optimizador de Horarios con Programación Genética
================================================

Uso:
    python ejecutar_optimizador.py                 # Usa archivo de ejemplo
    python ejecutar_optimizador.py archivo.xlsx    # Usa archivo específico
    python ejecutar_optimizador.py generar         # Genera archivo de ejemplo

Estructura del archivo Excel:
    - La primera columna contiene las horas (formato: "7:00 - 8:00")
    - Las columnas siguientes representan los días (Lunes a Viernes)
    - Cada celda contiene: "id|nombre_curso|profesor|tipo"
    
Ejemplo de celda: "1|Cálculo I|García|Teórico"
    """)

def main():
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            mostrar_ayuda()
            return
        elif sys.argv[1] == "generar":
            print("Generando archivo de carga horaria de ejemplo...")
            generar_carga_horaria_ejemplo()
            print("¡Archivo generado! Ahora puede ejecutar el programa sin argumentos.")
            return
        else:
            archivo = sys.argv[1]
            if not os.path.exists(archivo):
                print(f"Error: El archivo '{archivo}' no existe.")
                print("Use 'python ejecutar_optimizador.py generar' para crear un archivo de ejemplo.")
                return
    else:
        # Si no se proporciona archivo, verificar si existe el de ejemplo
        archivo = 'carga_horaria_ejemplo.xlsx'
        if not os.path.exists(archivo):
            print("No se encontró el archivo de ejemplo. Generando uno nuevo...")
            generar_carga_horaria_ejemplo()
    
    # Ejecutar el sistema
    try:
        print("\nIniciando el sistema de optimización de horarios...")
        print("="*50)
        sistema = SistemaOptimizacionHorarios(archivo)
        sistema.ejecutar()
    except Exception as e:
        print(f"Error al ejecutar el sistema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()