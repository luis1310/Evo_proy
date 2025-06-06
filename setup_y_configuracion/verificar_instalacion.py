#!/usr/bin/env python3
"""
Script para verificar que la instalación esté completa y funcional.
"""

import sys
import os
import importlib

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas."""
    
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
    """Verifica que la estructura de archivos esté completa."""
    
    directorios_requeridos = [
        'core', 'generadores', 'interfaces', 'visualizacion',
        'scripts', 'datos', 'ejemplos'
    ]
    
    print("\n🏗️  Verificando estructura del proyecto...")
    
    errores = []
    for directorio in directorios_requeridos:
        if os.path.isdir(directorio):
            print(f"✅ {directorio}/")
        else:
            print(f"❌ {directorio}/")
            errores.append(directorio)
    
    return len(errores) == 0

def verificar_modulos():
    """Verifica que los módulos principales se puedan importar."""
    
    print("\n🧠 Verificando módulos del proyecto...")
    
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
    """Ejecuta una prueba básica del sistema."""
    
    print("\n🧪 Ejecutando prueba básica...")
    
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
    print(f"📊 RESUMEN DE VERIFICACIÓN")
    print("="*30)
    print(f"Dependencias: {'✅' if dependencias_ok else '❌'}")
    print(f"Estructura: {'✅' if estructura_ok else '❌'}")
    print(f"Módulos: {'✅' if modulos_ok else '❌'}")
    print(f"Prueba básica: {'✅' if prueba_ok else '❌'}")
    
    if all([dependencias_ok, estructura_ok, modulos_ok, prueba_ok]):
        print(f"🎉 ¡INSTALACIÓN COMPLETA Y FUNCIONAL!")
        print("Puede ejecutar:")
        print("  python scripts/optimizar.py")
        print("  python ejemplos/ejemplo_completo.py")
    else:
        print(f"⚠️  INSTALACIÓN INCOMPLETA")
        print("Ejecute: python setup_y_configuracion/requirements_setup.py")
        
        if not estructura_ok:
            print("Y asegúrese de tener todos los archivos del proyecto")

if __name__ == "__main__":
    main()
