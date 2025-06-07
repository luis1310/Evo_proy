#!/usr/bin/env python3
"""
Script principal INTEGRADO para ejecutar el sistema de optimización de horarios.
Detecta automáticamente el tipo de archivo y ejecuta el proceso completo.

VERSIÓN UNIFICADA - Combina funcionalidad original + soporte universitario.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports del sistema unificado
try:
    # Importar desde estructura unificada
    from interfaces.sistema_completo import SistemaOptimizacionCompleto
    from core.lector_horarios import LectorHorarios, test_lector_unificado
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Verifique que los archivos __init__.py estén actualizados")
    IMPORTS_OK = False

from interfaces.sistema_completo import SistemaOptimizacionCompleto
from core.lector_horarios import LectorHorarios, test_lector_unificado


def procesar_argumentos():
    """Procesa argumentos de línea de comandos de forma inteligente."""
    args = {
        'archivo': None,
        'ayuda': False,
        'test_lector': False,
        'universitario': False,
        'debug': False,
        'rapido': False,
        'export': None,
        'formato': None
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['--help', '-h']:
            args['ayuda'] = True
        elif arg == '--test-lector':
            args['test_lector'] = True
        elif arg == '--universitario':
            args['universitario'] = True
        elif arg == '--debug':
            args['debug'] = True
        elif arg == '--rapido':
            args['rapido'] = True
        elif arg.startswith('--export='):
            args['export'] = arg.split('=')[1]
        elif arg.startswith('--formato='):
            args['formato'] = arg.split('=')[1]
        elif not arg.startswith('--') and args['archivo'] is None:
            args['archivo'] = arg
        
        i += 1
    
    return args


def test_lector_solo(archivo: str, export: str = None) -> bool:
    """
    Modo de prueba especializado - solo prueba el lector.
    NUEVA FUNCIONALIDAD INTEGRADA.
    """
    print("🧪 MODO PRUEBA - LECTOR UNIFICADO")
    print("="*45)
    
    if not verificar_archivo(archivo):
        return False
    
    try:
        # Usar función de test del lector unificado
        exito = test_lector_unificado(archivo)
        
        if exito and export:
            print(f"\n📤 Exportando datos procesados...")
            lector = LectorHorarios()
            datos = lector.leer_archivo(archivo)
            
            if lector.ultimo_formato_detectado == 'excel_universitario':
                lector.lector_excel.exportar_a_excel_optimizador(datos, export)
            elif lector.ultimo_formato_detectado == 'pdf':
                lector.lector_pdf.exportar_a_excel(datos['cursos'], export)
            else:
                print("⚠️  Formato ya es compatible")
            
            print(f"✅ Datos exportados a: {export}")
        
        if exito:
            print(f"\n💡 Para optimización completa:")
            archivo_optimizar = export if export else archivo
            print(f"   python scripts/optimizar.py {archivo_optimizar}")
        
        return exito
        
    except Exception as e:
        print(f"❌ Error en prueba del lector: {e}")
        import traceback
        traceback.print_exc()
        return False


def ejecutar_optimizacion_completa(archivo: str, config: dict) -> bool:
    """
    Ejecuta la optimización completa con configuración personalizada.
    VERSIÓN MEJORADA con detección automática.
    """
    print("🚀 MODO OPTIMIZACIÓN COMPLETA")
    print("="*40)
    
    if archivo and not verificar_archivo(archivo):
        return False
    
    try:
        # Crear sistema con configuración
        sistema = SistemaOptimizacionCompleto()
        
        # Aplicar configuraciones según argumentos
        configuracion = {
            'mostrar_progreso': not config.get('rapido', False),
            'analisis_detallado': config.get('debug', False) or not config.get('rapido', False),
            'visualizacion_automatica': not config.get('rapido', False),
            'guardar_automatico': config.get('debug', False)
        }
        
        # Forzar modo universitario si se especifica
        if config.get('universitario', False):
            configuracion['modo_universitario'] = True
        
        sistema.configurar_sistema(**configuracion)
        
        # Ejecutar sistema completo
        sistema.ejecutar(archivo)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en optimización completa: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_archivo(archivo: str) -> bool:
    """Verifica que el archivo existe y tiene formato válido."""
    if not archivo:
        return True  # Permitir ejecución sin archivo (datos de prueba)
    
    if not os.path.exists(archivo):
        print(f"❌ Error: El archivo '{archivo}' no existe")
        return False
    
    extension = os.path.splitext(archivo)[1].lower()
    if extension not in ['.xlsx', '.xls', '.pdf']:
        print(f"❌ Error: Formato de archivo no soportado: {extension}")
        print("💡 Formatos soportados: .xlsx, .xls, .pdf")
        return False
    
    return True


def mostrar_ayuda():
    """Muestra la ayuda completa del sistema integrado."""
    print("""
🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS - VERSIÓN INTEGRADA
=====================================================================

DESCRIPCIÓN:
    Sistema completo con detección automática de formato y soporte
    especializado para archivos universitarios, estándar y PDF.

USO:
    python scripts/optimizar.py [archivo] [opciones]

ARCHIVOS SOPORTADOS:
    📄 PDF: Horarios académicos en formato tabular
    📊 Excel Universitario: Formato con escuelas y múltiples secciones
    📊 Excel Estándar: Matriz de horarios (formato original)
    🔧 Sin archivo: Genera datos de prueba automáticamente

OPCIONES PRINCIPALES:
    --test-lector     Solo probar lectura sin optimización
    --universitario   Forzar modo universitario especializado  
    --debug          Modo detallado con análisis completo
    --rapido         Modo rápido sin visualizaciones extra
    --export=FILE    Exportar datos procesados a archivo
    --formato=TIPO   Forzar formato específico
    --help, -h       Mostrar esta ayuda

EJEMPLOS DE USO:

    # 1. Optimización automática (recomendado)
    python scripts/optimizar.py datos/Horarios_2023_1.xlsx
    
    # 2. Solo probar lectura de archivo universitario
    python scripts/optimizar.py datos/Horarios_2023_1.xlsx --test-lector
    
    # 3. Modo universitario forzado
    python scripts/optimizar.py archivo.xlsx --universitario
    
    # 4. Modo debug con análisis completo
    python scripts/optimizar.py archivo.xlsx --debug
    
    # 5. Modo rápido sin visualizaciones
    python scripts/optimizar.py archivo.xlsx --rapido
    
    # 6. Exportar datos procesados
    python scripts/optimizar.py archivo.xlsx --export=convertido.xlsx
    
    # 7. Generar datos de prueba y optimizar
    python scripts/optimizar.py

DETECCIÓN AUTOMÁTICA:
    El sistema detecta automáticamente:
    ✅ Tipo de archivo: PDF vs Excel
    ✅ Formato Excel: Universitario vs Estándar
    ✅ Estructura de datos específica
    ✅ Códigos universitarios (BFI01, CM201, etc.)
    ✅ Horarios en formato "LU 10-12, MI 14-16"

FORMATO UNIVERSITARIO DETECTADO:
    Cuando se detecta formato universitario:
    📚 Reconoce cursos con múltiples secciones (A, B, C, D, E)
    🏫 Agrupa por escuela profesional
    👨‍🏫 Extrae profesores y salones automáticamente
    🎯 Permite selección por nombre de curso completo
    📊 Genera estadísticas especializadas

SELECCIÓN DE CURSOS:
    Durante la optimización puede seleccionar:
    • IDs individuales: 1, 5, 10
    • Rangos: 1-20 (cursos del 1 al 20)
    • Por escuela: BF (todos los cursos de Física)
    • Por nombre: "FÍSICA I" (todas las secciones)
    • 'ver ESCUELA' para filtrar visualización
    • 'todos' para seleccionar todos los cursos
    • 'auto' para selección automática inteligente

RESULTADOS GENERADOS:
    📊 Horario optimizado en tabla visual
    📈 Gráficos de evolución del algoritmo genético
    📋 Análisis detallado de conflictos
    📁 Archivo Excel con horario final
    📄 Reportes de calidad y distribución

TIPOS DE CONFLICTOS RESUELTOS:
    🧑‍🏫 Profesores: Clases simultáneas del mismo profesor
    🏫 Salones: Múltiples clases en el mismo salón
    ⚡ Sobrecarga: Profesores con exceso de horas
    📚 Distribución: Optimización de carga semanal

FLUJO DE TRABAJO TÍPICO:
    1. El sistema detecta automáticamente el formato del archivo
    2. Activa el modo apropiado (universitario/estándar/PDF)
    3. Extrae y procesa todos los cursos con sus secciones
    4. Permite selección inteligente de cursos
    5. Ejecuta optimización con algoritmo genético
    6. Muestra resultados y resuelve conflictos
    7. Genera archivos de salida

CASOS DE USO COMUNES:
    📚 Universidad: Horarios con múltiples secciones por curso
    🏫 Institutos: Horarios estándar en matriz Excel
    📄 Documentos: Horarios en PDF que necesitan digitalización
    🔧 Testing: Generación de datos para pruebas

¿NECESITA MÁS AYUDA?
    • Ejecute sin argumentos para modo interactivo
    • Use --test-lector para verificar que su archivo se lee correctamente
    • Consulte docs/manual_usuario.md para documentación completa
    • Revise ejemplos/ para casos de uso específicos

COMPATIBILIDAD:
    ✅ Funciona con archivos del sistema original
    ✅ Detecta y procesa nuevos formatos automáticamente
    ✅ Mantiene todas las funcionalidades existentes
    ✅ Agrega capacidades universitarias especializadas
""")


def mostrar_ejemplos():
    """Muestra ejemplos de uso cuando no hay argumentos."""
    print("🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS")
    print("   Detección automática y optimización inteligente")
    print("="*55)
    
    print("\n📋 Comandos más comunes:")
    
    print("\n🚀 Optimización completa (recomendado):")
    print("   python scripts/optimizar.py datos/Horarios_2023_1.xlsx")
    print("   → Detecta formato y optimiza automáticamente")
    
    print("\n🧪 Solo probar lectura de archivo:")
    print("   python scripts/optimizar.py datos/Horarios_2023_1.xlsx --test-lector")
    print("   → Verifica que el archivo se procese correctamente")
    
    print("\n🎓 Forzar modo universitario:")
    print("   python scripts/optimizar.py archivo.xlsx --universitario")
    print("   → Activa procesamiento especializado universitario")
    
    print("\n🔧 Generar datos de prueba:")
    print("   python scripts/optimizar.py")
    print("   → Crea datos automáticamente para testing")
    
    print("\n📤 Exportar datos procesados:")
    print("   python scripts/optimizar.py archivo.xlsx --export=convertido.xlsx")
    print("   → Convierte a formato compatible")
    
    print(f"\n📁 Archivos de ejemplo soportados:")
    print("   • Horarios_2023_1.xlsx (formato universitario)")
    print("   • carga_horaria.xlsx (formato estándar)")
    print("   • horarios.pdf (formato PDF)")
    
    print(f"\n💡 Para empezar:")
    print("   1. Coloque su archivo en la carpeta 'datos/'")
    print("   2. Ejecute: python scripts/optimizar.py datos/su_archivo.xlsx")
    print("   3. Siga las instrucciones interactivas")
    
    print(f"\n🆘 Si tiene problemas:")
    print("   • Use --test-lector para verificar lectura del archivo")
    print("   • Use --help para ver todas las opciones")
    print("   • Revise que el archivo no esté corrupto o protegido")


def main():
    """Función principal mejorada con detección automática."""
    try:
        # Procesar argumentos
        args = procesar_argumentos()
        
        # Mostrar ayuda si se solicita
        if args['ayuda']:
            mostrar_ayuda()
            return
        
        # Si no hay archivo ni opciones, mostrar ejemplos
        if not args['archivo'] and not any([args['test_lector'], args['debug'], args['rapido']]):
            mostrar_ejemplos()
            
            # Preguntar si quiere generar datos de prueba
            print(f"\n❓ ¿Generar datos de prueba y ejecutar optimización? (s/n): ", end="")
            respuesta = input().strip().lower()
            if respuesta == 's':
                args['archivo'] = None  # Forzar generación de datos
            else:
                return
        
        print(f"🎓 INICIANDO SISTEMA DE OPTIMIZACIÓN")
        if args['archivo']:
            print(f"📂 Archivo: {args['archivo']}")
        else:
            print(f"🔧 Modo: Generación de datos de prueba")
        print("="*50)
        
        # Detectar formato si hay archivo
        if args['archivo']:
            try:
                lector = LectorHorarios()
                formato_detectado = lector.detectar_formato(args['archivo'])
                print(f"🔍 Formato detectado: {formato_detectado}")
                
                # Activar modo universitario automáticamente si se detecta
                if formato_detectado == 'excel_universitario':
                    args['universitario'] = True
                    print("🎓 Modo universitario activado automáticamente")
                
            except Exception as e:
                print(f"⚠️  No se pudo detectar formato: {e}")
        
        # Ejecutar según modo
        if args['test_lector']:
            if not args['archivo']:
                print("❌ Se requiere archivo para modo de prueba")
                return
            
            exito = test_lector_solo(args['archivo'], args.get('export'))
        
        else:
            # Preparar configuración para optimización completa
            config = {
                'universitario': args['universitario'],
                'debug': args['debug'],
                'rapido': args['rapido'],
                'formato': args['formato']
            }
            
            exito = ejecutar_optimizacion_completa(args['archivo'], config)
        
        # Mostrar resultado final
        if exito:
            print(f"\n🎉 ¡Proceso completado exitosamente!")
            
            if args['test_lector']:
                print(f"✅ El archivo se procesó correctamente")
                print(f"💡 Ahora puede ejecutar optimización completa")
            else:
                print(f"✅ Optimización finalizada con éxito")
                print(f"📁 Revise la carpeta 'datos/resultados/' para archivos generados")
        else:
            print(f"\n⚠️  El proceso terminó con errores")
            print(f"💡 Use --test-lector para verificar el archivo")
            print(f"💡 Use --help para ver todas las opciones")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print(f"💡 Use --debug para más información")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def mostrar_estado_archivos():
    """Función auxiliar para mostrar estado de archivos en el proyecto."""
    print("📁 ESTADO DE ARCHIVOS DEL PROYECTO:")
    print("-"*40)
    
    archivos_importantes = [
        ('datos/Horarios_2023_1.xlsx', 'Archivo universitario principal'),
        ('datos/carga_horaria.xlsx', 'Archivo estándar de ejemplo'),
        ('core/lector_horarios.py', 'Lector unificado'),
        ('interfaces/sistema_completo.py', 'Sistema principal'),
        ('scripts/optimizar.py', 'Este script')
    ]
    
    for archivo, descripcion in archivos_importantes:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - {descripcion}")
        else:
            print(f"❌ {archivo} - {descripcion} (FALTANTE)")


def verificar_dependencias():
    """Verifica que las dependencias estén instaladas."""
    dependencias = ['pandas', 'numpy', 'matplotlib', 'openpyxl']
    
    for dep in dependencias:
        try:
            __import__(dep)
        except ImportError:
            print(f"❌ Dependencia faltante: {dep}")
            print(f"💡 Instale con: pip install {dep}")
            return False
    
    return True


def modo_diagnostico():
    """Modo de diagnóstico para verificar el sistema."""
    print("🔧 MODO DIAGNÓSTICO DEL SISTEMA")
    print("="*40)
    
    print("\n1. Verificando dependencias...")
    if verificar_dependencias():
        print("✅ Todas las dependencias están instaladas")
    else:
        print("❌ Hay dependencias faltantes")
        return False
    
    print("\n2. Verificando estructura de archivos...")
    mostrar_estado_archivos()
    
    print("\n3. Verificando módulos del proyecto...")
    try:
        from core.lector_horarios import LectorHorarios
        from interfaces.sistema_completo import SistemaOptimizacionCompleto
        print("✅ Módulos principales importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    
    print("\n4. Probando lector unificado...")
    try:
        lector = LectorHorarios()
        print("✅ Lector unificado inicializado")
    except Exception as e:
        print(f"❌ Error en lector: {e}")
        return False
    
    print("\n✅ DIAGNÓSTICO COMPLETADO - Sistema operativo")
    return True


# ============================================================================
# FUNCIONES ADICIONALES PARA CASOS ESPECÍFICOS
# ============================================================================

def convertir_archivo(archivo_entrada: str, archivo_salida: str):
    """
    Convierte un archivo a formato compatible con el optimizador.
    Función utilitaria para conversión rápida.
    """
    print(f"🔄 CONVIRTIENDO ARCHIVO")
    print(f"   Entrada: {archivo_entrada}")
    print(f"   Salida: {archivo_salida}")
    print("-"*40)
    
    try:
        lector = LectorHorarios()
        datos = lector.leer_archivo(archivo_entrada)
        
        if lector.ultimo_formato_detectado == 'excel_universitario':
            lector.lector_excel.exportar_a_excel_optimizador(datos, archivo_salida)
        elif lector.ultimo_formato_detectado == 'pdf':
            lector.lector_pdf.exportar_a_excel(datos['cursos'], archivo_salida)
        else:
            print("⚠️  El archivo ya está en formato compatible")
            return False
        
        print(f"✅ Conversión completada: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False


def modo_interactivo():
    """Modo interactivo para usuarios nuevos."""
    print("🎮 MODO INTERACTIVO")
    print("="*25)
    
    print("Este modo le ayudará a usar el sistema paso a paso.\n")
    
    # Paso 1: Verificar archivo
    print("📂 PASO 1: Seleccionar archivo")
    archivo = input("Ingrese la ruta al archivo (o Enter para datos de prueba): ").strip()
    
    if not archivo:
        print("🔧 Usando datos de prueba...")
        return ejecutar_optimizacion_completa(None, {'debug': True})
    
    if not verificar_archivo(archivo):
        return False
    
    # Paso 2: Detectar formato
    print(f"\n🔍 PASO 2: Detectando formato...")
    try:
        lector = LectorHorarios()
        formato = lector.detectar_formato(archivo)
        print(f"✅ Formato detectado: {formato}")
    except Exception as e:
        print(f"❌ Error detectando formato: {e}")
        return False
    
    # Paso 3: Elegir modo
    print(f"\n⚙️  PASO 3: Seleccionar modo de ejecución")
    print("1. Solo probar lectura (recomendado primero)")
    print("2. Optimización completa")
    print("3. Modo debug (análisis detallado)")
    
    opcion = input("Seleccione opción (1-3): ").strip()
    
    if opcion == '1':
        return test_lector_solo(archivo)
    elif opcion == '2':
        config = {'universitario': formato == 'excel_universitario'}
        return ejecutar_optimizacion_completa(archivo, config)
    elif opcion == '3':
        config = {'debug': True, 'universitario': formato == 'excel_universitario'}
        return ejecutar_optimizacion_completa(archivo, config)
    else:
        print("❌ Opción no válida")
        return False


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL MEJORADO
# ============================================================================

if __name__ == "__main__":
    # Verificar argumentos especiales primero
    if '--diagnostico' in sys.argv:
        modo_diagnostico()
    elif '--interactivo' in sys.argv:
        modo_interactivo()
    elif '--convertir' in sys.argv:
        if len(sys.argv) >= 4:
            convertir_archivo(sys.argv[2], sys.argv[3])
        else:
            print("Uso: python scripts/optimizar.py --convertir entrada.xlsx salida.xlsx")
    else:
        # Ejecutar función principal normal
        main()


# ============================================================================
# CONFIGURACIÓN PARA IMPORTACIÓN COMO MÓDULO
# ============================================================================

__all__ = [
    'main',
    'mostrar_ayuda',
    'test_lector_solo',
    'ejecutar_optimizacion_completa',
    'verificar_archivo',
    'convertir_archivo',
    'modo_diagnostico'
]