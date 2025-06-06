#!/usr/bin/env python3
"""
Ejemplo completo del sistema de optimización de horarios.
Demuestra todas las funcionalidades principales.

VERSION CORREGIDA - Compatible con estructura modular
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports corregidos para la nueva estructura modular
from interfaces.sistema_completo import SistemaOptimizacionCompleto
from generadores.generador_avanzado import GeneradorCargaHorariaAvanzado
from visualizacion.graficos_horarios import (
    mostrar_horario_tabla,
    visualizar_horario_grafico, 
    crear_grafico_evolucion
)
from visualizacion.reportes_conflictos import mostrar_reporte_conflictos


def ejemplo_datos_generados():
    """Ejemplo usando datos generados automáticamente."""
    
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
            print(f"\n🎯 Seleccionados automáticamente: {len(cursos_seleccionados)} cursos")
            
            # Ejecutar optimización
            horario, conflictos = sistema.ejecutar_optimizacion(cursos_seleccionados)
            
            if horario:
                # Mostrar resultados usando las funciones modulares
                sistema.analizar_resultados(horario, conflictos)
                
                # ✅ CORRECCIÓN: Usar función modular en lugar del método de clase
                mostrar_horario_tabla(horario, "Horario Optimizado - Ejemplo Automático")
                
                # Mostrar gráficas si hay datos de evolución
                if (sistema.optimizador and 
                    hasattr(sistema.optimizador, 'historia_fitness') and 
                    len(sistema.optimizador.historia_fitness) > 1):
                    
                    print("\n📈 Mostrando evolución del algoritmo...")
                    crear_grafico_evolucion(
                        sistema.optimizador.historia_fitness,
                        sistema.optimizador.historia_conflictos,
                        "Evolución - Ejemplo Automático"
                    )
                
                # Guardar resultado automáticamente
                sistema.guardar_horario_excel(horario, "ejemplos/resultado_ejemplo_automatico.xlsx")
                print("\n✅ Ejemplo completado exitosamente!")
                
                return True
            else:
                print("❌ No se pudo generar horario optimizado")
                return False
        else:
            print("❌ No se encontraron cursos disponibles")
            return False
    else:
        print("❌ Error al generar datos de prueba")
        return False


def ejemplo_interactivo():
    """Ejemplo con selección interactiva del usuario."""
    
    print("\n🎮 EJEMPLO: Modo Interactivo")
    print("="*50)
    
    sistema = SistemaOptimizacionCompleto()
    
    # Configurar para modo interactivo
    sistema.configurar_sistema(
        mostrar_progreso=True,
        analisis_detallado=True,
        visualizacion_automatica=True,
        guardar_automatico=False  # Que el usuario decida
    )
    
    sistema.ejecutar()


def ejemplo_comparativo():
    """Ejemplo que compara diferentes configuraciones."""
    
    print("\n🔬 EJEMPLO: Comparación de Configuraciones")
    print("="*50)
    
    resultados = {}
    
    # Configuración 1: Básica
    print("\n1️⃣ Configuración Básica (10 cursos):")
    sistema1 = SistemaOptimizacionCompleto()
    sistema1.configurar_sistema(mostrar_progreso=False, analisis_detallado=False)
    
    if sistema1.generar_datos_prueba(num_cursos_por_escuela=2):  # Pocos cursos
        cursos = list(sistema1.obtener_cursos_disponibles().keys())[:10]
        horario1, conflictos1 = sistema1.ejecutar_optimizacion(cursos)
        if horario1:
            resultados['basico'] = {
                'horario': horario1,
                'conflictos': conflictos1,
                'fitness_historia': sistema1.optimizador.historia_fitness,
                'cursos_count': len(cursos)
            }
            print(f"✅ Configuración básica: {len(conflictos1.get('profesor', []))} conflictos de profesor")
    
    # Configuración 2: Intermedia
    print("\n2️⃣ Configuración Intermedia (20 cursos):")
    sistema2 = SistemaOptimizacionCompleto()
    sistema2.configurar_sistema(mostrar_progreso=False, analisis_detallado=False)
    
    if sistema2.generar_datos_prueba(num_cursos_por_escuela=4):  # Cursos medios
        cursos = list(sistema2.obtener_cursos_disponibles().keys())[:20]
        horario2, conflictos2 = sistema2.ejecutar_optimizacion(cursos)
        if horario2:
            resultados['intermedio'] = {
                'horario': horario2,
                'conflictos': conflictos2,
                'fitness_historia': sistema2.optimizador.historia_fitness,
                'cursos_count': len(cursos)
            }
            print(f"✅ Configuración intermedia: {len(conflictos2.get('profesor', []))} conflictos de profesor")
    
    # Mostrar comparación
    if len(resultados) >= 2:
        print("\n📊 COMPARACIÓN DE RESULTADOS:")
        print("="*40)
        
        for config, datos in resultados.items():
            fitness_final = datos['fitness_historia'][-1] if datos['fitness_historia'] else 'N/A'
            conflictos_total = sum(len(v) for v in datos['conflictos'].values())
            
            print(f"{config.capitalize()}:")
            print(f"  - Cursos: {datos['cursos_count']}")
            print(f"  - Fitness final: {fitness_final}")
            print(f"  - Conflictos totales: {conflictos_total}")
            print(f"  - Generaciones: {len(datos['fitness_historia'])}")
        
        # Mostrar horarios lado a lado
        print(f"\nHorarios generados:")
        for config, datos in resultados.items():
            mostrar_horario_tabla(datos['horario'], f"Horario {config.capitalize()}")


def ejemplo_con_pdf(archivo_pdf: str = None):
    """Ejemplo específico para procesamiento de PDF."""
    
    print("\n📄 EJEMPLO: Procesamiento de PDF")
    print("="*50)
    
    if archivo_pdf is None:
        archivo_pdf = "datos/Horarios_2023_1.pdf"
        if not os.path.exists(archivo_pdf):
            print(f"❌ Archivo PDF no encontrado: {archivo_pdf}")
            print("💡 Coloque el archivo PDF en la ruta datos/Horarios_2023_1.pdf")
            return False
    
    sistema = SistemaOptimizacionCompleto()
    
    # Configurar para procesamiento de PDF
    sistema.configurar_sistema(
        mostrar_progreso=True,
        analisis_detallado=True,
        visualizacion_automatica=True
    )
    
    # Procesar PDF
    if sistema.detectar_y_cargar_archivo(archivo_pdf):
        print("✅ PDF procesado exitosamente")
        
        # Mostrar algunos cursos disponibles
        cursos = sistema.obtener_cursos_disponibles()
        print(f"📚 Total de cursos encontrados: {len(cursos)}")
        
        # Selección automática inteligente
        seleccionados = sistema._seleccion_automatica_recomendada(cursos)
        print(f"🎯 Selección automática recomendada: {len(seleccionados)} cursos")
        
        # Optimizar
        horario, conflictos = sistema.ejecutar_optimizacion(seleccionados)
        
        if horario:
            sistema.analizar_resultados(horario, conflictos)
            mostrar_horario_tabla(horario, "Horario desde PDF")
            
            # Guardar resultado
            archivo_resultado = f"ejemplos/resultado_pdf_{len(seleccionados)}cursos.xlsx"
            sistema.guardar_horario_excel(horario, archivo_resultado)
            
            return True
    
    return False


def mostrar_menu_ejemplos():
    """Muestra el menú de ejemplos disponibles."""
    
    print("\n🎯 MENÚ DE EJEMPLOS DISPONIBLES:")
    print("="*40)
    print("1. Ejemplo automático (datos generados)")
    print("2. Ejemplo interactivo completo")
    print("3. Ejemplo comparativo (múltiples configuraciones)")
    print("4. Ejemplo con PDF (si disponible)")
    print("5. Todos los ejemplos en secuencia")
    print("6. Salir")
    
    return input("\nSeleccione una opción (1-6): ").strip()


def main():
    print("🎓 EJEMPLOS DEL SISTEMA DE OPTIMIZACIÓN")
    print("="*50)
    
    # Si se ejecuta con argumentos específicos
    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            ejemplo_datos_generados()
        elif sys.argv[1] == "interactivo":
            ejemplo_interactivo()
        elif sys.argv[1] == "comparativo":
            ejemplo_comparativo()
        elif sys.argv[1] == "pdf" and len(sys.argv) > 2:
            ejemplo_con_pdf(sys.argv[2])
        else:
            print(f"❌ Argumento no reconocido: {sys.argv[1]}")
            print("Argumentos válidos: auto, interactivo, comparativo, pdf")
        return
    
    # Menú interactivo
    while True:
        opcion = mostrar_menu_ejemplos()
        
        if opcion == "1":
            ejemplo_datos_generados()
        elif opcion == "2":
            ejemplo_interactivo()
        elif opcion == "3":
            ejemplo_comparativo()
        elif opcion == "4":
            ejemplo_con_pdf()
        elif opcion == "5":
            # Ejecutar todos los ejemplos
            print("\n🚀 Ejecutando todos los ejemplos...")
            
            if ejemplo_datos_generados():
                input("\n⏸️  Presione Enter para continuar con el ejemplo comparativo...")
                ejemplo_comparativo()
                
                input("\n⏸️  Presione Enter para continuar con el ejemplo de PDF...")
                ejemplo_con_pdf()
                
                input("\n⏸️  Presione Enter para el ejemplo interactivo final...")
                ejemplo_interactivo()
        elif opcion == "6":
            print("👋 ¡Gracias por probar el sistema!")
            break
        else:
            print("❌ Opción no válida")
        
        # Preguntar si continuar
        if opcion in ["1", "2", "3", "4"]:
            continuar = input("\n¿Ejecutar otro ejemplo? (s/n): ").strip().lower()
            if continuar != 's':
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error en los ejemplos: {e}")
        import traceback
        traceback.print_exc()