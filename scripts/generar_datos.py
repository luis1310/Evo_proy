#!/usr/bin/env python3
"""
Script para generar datos de prueba con diferentes niveles de complejidad.
"""

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
    
    opcion = input("\nSeleccione opción (1-4): ").strip()
    
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
    
    print(f"\n✅ Datos generados y guardados en: {archivo}")

if __name__ == "__main__":
    main()
