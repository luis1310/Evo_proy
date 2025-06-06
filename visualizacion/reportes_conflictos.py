#!/usr/bin/env python3
"""
Módulo para generar reportes detallados de conflictos de horarios.
Este módulo debería estar en: visualizacion/reportes_conflictos.py
"""

from typing import Dict, List

def mostrar_reporte_conflictos(conflictos: Dict[str, List]):
    """
    Muestra un reporte detallado de conflictos de horarios.
    
    Args:
        conflictos: Diccionario con tipos de conflictos y sus detalles
                   {'profesor': [...], 'salon': [...], 'sobrecarga': [...]}
    """
    print("\n" + "="*60)
    print("REPORTE DE CONFLICTOS")
    print("="*60)
    
    total_conflictos = sum(len(lista) for lista in conflictos.values())
    
    if total_conflictos == 0:
        print("✅ ¡No se encontraron conflictos! Horario válido.")
        return
    
    print(f"⚠️  Total de conflictos encontrados: {total_conflictos}")
    
    # Conflictos de profesor
    if conflictos.get('profesor', []):
        print(f"\n🧑‍🏫 Conflictos de Profesor ({len(conflictos['profesor'])}):")
        for conf in conflictos['profesor']:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            dia_nombre = dias[conf['dia']] if conf['dia'] < len(dias) else f"Día {conf['dia']}"
            print(f"   {conf['profesor']}: {dia_nombre} bloque {conf['bloque']+1}")
            if 'cursos' in conf:
                print(f"      Cursos: {', '.join(conf['cursos'])}")
    
    # Conflictos de salón
    if conflictos.get('salon', []):
        print(f"\n🏫 Conflictos de Salón ({len(conflictos['salon'])}):")
        for conf in conflictos['salon']:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            dia_nombre = dias[conf['dia']] if conf['dia'] < len(dias) else f"Día {conf['dia']}"
            print(f"   {conf['salon']}: {dia_nombre} bloque {conf['bloque']+1}")
            if 'cursos' in conf:
                print(f"      Cursos: {', '.join(conf['cursos'])}")
    
    # Sobrecarga de profesores
    if conflictos.get('sobrecarga', []):
        print(f"\n⚡ Sobrecarga de Profesores ({len(conflictos['sobrecarga'])}):")
        for conf in conflictos['sobrecarga']:
            print(f"   {conf['profesor']}: {conf['horas']} horas semanales")
    
    # Conflictos de estudiantes (si existen)
    if conflictos.get('estudiante', []):
        print(f"\n🎓 Conflictos de Estudiantes ({len(conflictos['estudiante'])}):")
        for conf in conflictos['estudiante']:
            print(f"   Cursos superpuestos: {conf.get('cursos', 'N/A')}")

def generar_reporte_conflictos_texto(conflictos: Dict[str, List]) -> str:
    """
    Genera un reporte de conflictos en formato de texto.
    
    Args:
        conflictos: Diccionario con conflictos
        
    Returns:
        String con el reporte formateado
    """
    if not conflictos:
        return "✅ No se encontraron conflictos en el horario."
    
    total_conflictos = sum(len(lista) for lista in conflictos.values())
    
    if total_conflictos == 0:
        return "✅ No se encontraron conflictos en el horario."
    
    reporte = []
    reporte.append("REPORTE DE CONFLICTOS DE HORARIOS")
    reporte.append("=" * 40)
    reporte.append(f"Total de conflictos: {total_conflictos}")
    reporte.append("")
    
    # Conflictos de profesor
    if conflictos.get('profesor', []):
        reporte.append(f"🧑‍🏫 CONFLICTOS DE PROFESOR ({len(conflictos['profesor'])})")
        reporte.append("-" * 30)
        for i, conf in enumerate(conflictos['profesor'], 1):
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            dia_nombre = dias[conf['dia']] if conf['dia'] < len(dias) else f"Día {conf['dia']}"
            reporte.append(f"{i}. Profesor: {conf['profesor']}")
            reporte.append(f"   Día: {dia_nombre}, Bloque: {conf['bloque']+1}")
            if 'cursos' in conf:
                reporte.append(f"   Cursos en conflicto: {', '.join(conf['cursos'])}")
            reporte.append("")
    
    # Conflictos de salón
    if conflictos.get('salon', []):
        reporte.append(f"🏫 CONFLICTOS DE SALÓN ({len(conflictos['salon'])})")
        reporte.append("-" * 30)
        for i, conf in enumerate(conflictos['salon'], 1):
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            dia_nombre = dias[conf['dia']] if conf['dia'] < len(dias) else f"Día {conf['dia']}"
            reporte.append(f"{i}. Salón: {conf['salon']}")
            reporte.append(f"   Día: {dia_nombre}, Bloque: {conf['bloque']+1}")
            if 'cursos' in conf:
                reporte.append(f"   Cursos en conflicto: {', '.join(conf['cursos'])}")
            reporte.append("")
    
    # Sobrecarga
    if conflictos.get('sobrecarga', []):
        reporte.append(f"⚡ SOBRECARGA DE PROFESORES ({len(conflictos['sobrecarga'])})")
        reporte.append("-" * 30)
        for i, conf in enumerate(conflictos['sobrecarga'], 1):
            reporte.append(f"{i}. Profesor: {conf['profesor']}")
            reporte.append(f"   Horas semanales: {conf['horas']}")
            reporte.append("")
    
    return "\n".join(reporte)

def guardar_reporte_conflictos(conflictos: Dict[str, List], archivo: str):
    """
    Guarda un reporte de conflictos en un archivo de texto.
    
    Args:
        conflictos: Diccionario con conflictos
        archivo: Nombre del archivo donde guardar
    """
    try:
        reporte_texto = generar_reporte_conflictos_texto(conflictos)
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(reporte_texto)
        
        print(f"📄 Reporte de conflictos guardado en: {archivo}")
        
    except Exception as e:
        print(f"❌ Error al guardar reporte: {e}")

def analizar_gravedad_conflictos(conflictos: Dict[str, List]) -> Dict[str, any]:
    """
    Analiza la gravedad de los conflictos encontrados.
    
    Args:
        conflictos: Diccionario con conflictos
        
    Returns:
        Diccionario con análisis de gravedad
    """
    analisis = {
        'total_conflictos': sum(len(lista) for lista in conflictos.values()),
        'gravedad': 'Ninguna',
        'puntuacion': 0,
        'recomendaciones': []
    }
    
    # Calcular puntuación de gravedad
    pesos = {
        'profesor': 100,    # Muy grave
        'salon': 80,        # Grave  
        'sobrecarga': 20,   # Moderado
        'estudiante': 60    # Grave
    }
    
    puntuacion = 0
    for tipo, lista_conflictos in conflictos.items():
        if tipo in pesos:
            puntuacion += len(lista_conflictos) * pesos[tipo]
    
    analisis['puntuacion'] = puntuacion
    
    # Determinar gravedad
    if puntuacion == 0:
        analisis['gravedad'] = 'Ninguna'
        analisis['recomendaciones'] = ['✅ Horario perfecto, sin conflictos']
    elif puntuacion <= 50:
        analisis['gravedad'] = 'Leve'
        analisis['recomendaciones'] = [
            '🟡 Conflictos menores detectados',
            'Revisar sobrecarga de profesores',
            'Optimización adicional recomendada'
        ]
    elif puntuacion <= 200:
        analisis['gravedad'] = 'Moderada'
        analisis['recomendaciones'] = [
            '🟠 Conflictos importantes detectados',
            'Resolver conflictos de profesores/salones',
            'Redistribuir carga horaria',
            'Ejecutar más generaciones del algoritmo'
        ]
    else:
        analisis['gravedad'] = 'Grave'
        analisis['recomendaciones'] = [
            '🔴 Conflictos graves requieren atención inmediata',
            'Revisar datos de entrada por inconsistencias',
            'Reducir número de cursos seleccionados',
            'Verificar disponibilidad de profesores y salones',
            'Considerar horarios adicionales (sábados)'
        ]
    
    return analisis

def mostrar_analisis_gravedad(conflictos: Dict[str, List]):
    """
    Muestra un análisis detallado de la gravedad de conflictos.
    
    Args:
        conflictos: Diccionario con conflictos
    """
    analisis = analizar_gravedad_conflictos(conflictos)
    
    print(f"\n📊 ANÁLISIS DE GRAVEDAD")
    print("="*30)
    print(f"Total conflictos: {analisis['total_conflictos']}")
    print(f"Puntuación: {analisis['puntuacion']}")
    print(f"Gravedad: {analisis['gravedad']}")
    
    print(f"\n💡 RECOMENDACIONES:")
    for i, recomendacion in enumerate(analisis['recomendaciones'], 1):
        print(f"   {i}. {recomendacion}")

# Función para compatibilidad con el código existente
def mostrar_reporte_conflictos_completo(conflictos: Dict[str, List], mostrar_analisis: bool = True):
    """
    Función completa que muestra reporte y análisis de conflictos.
    
    Args:
        conflictos: Diccionario con conflictos
        mostrar_analisis: Si mostrar también el análisis de gravedad
    """
    mostrar_reporte_conflictos(conflictos)
    
    if mostrar_analisis:
        mostrar_analisis_gravedad(conflictos)

# Alias para compatibilidad con código existente
reporte_conflictos = mostrar_reporte_conflictos

if __name__ == "__main__":
    # Ejemplo de uso
    conflictos_ejemplo = {
        'profesor': [
            {
                'dia': 0,
                'bloque': 2,
                'profesor': 'GARCÍA',
                'cursos': ['BF101_A', 'CF201_B']
            }
        ],
        'salon': [
            {
                'dia': 1,
                'bloque': 5,
                'salon': 'R1-450',
                'cursos': ['CM301_A', 'CQ101_C']
            }
        ],
        'sobrecarga': [
            {
                'profesor': 'LÓPEZ',
                'horas': 25
            }
        ],
        'estudiante': []
    }
    
    print("Ejemplo de reporte de conflictos:")
    mostrar_reporte_conflictos_completo(conflictos_ejemplo)