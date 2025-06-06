#!/usr/bin/env python3
"""
Módulo de visualización gráfica para horarios académicos.
Este archivo va en: visualizacion/graficos_horarios.py

Incluye:
- Visualización de horarios en tabla
- Gráficos interactivos de horarios
- Gráficas de evolución del algoritmo genético
- Exportación de visualizaciones
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import seaborn as sns
from datetime import datetime


# ============================================================================
# CONFIGURACIÓN GLOBAL DE GRÁFICOS
# ============================================================================

# Configurar estilo de matplotlib
plt.style.use('default')
sns.set_palette("husl")

# Configuración de colores para diferentes tipos de cursos
COLORES_TIPO = {
    'Teórico': '#3498db',     # Azul
    'Práctico': '#e74c3c',    # Rojo
    'Laboratorio': '#f39c12', # Naranja
    'Seminario': '#9b59b6',   # Púrpura
    'Taller': '#2ecc71'       # Verde
}

# Configuración de días y horas
DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
HORAS_DIA = [f"{7+i}:00" for i in range(14)]  # 7:00 AM a 8:00 PM


# ============================================================================
# VISUALIZACIÓN DE HORARIOS EN TABLA
# ============================================================================

def mostrar_horario_tabla(horario: List[List], titulo: str = "HORARIO OPTIMIZADO", 
                         mostrar_profesores: bool = True, mostrar_codigos: bool = True):
    """
    Muestra el horario en formato de tabla en la consola.
    
    Args:
        horario: Matriz 5x14 con el horario
        titulo: Título a mostrar
        mostrar_profesores: Si mostrar nombres de profesores
        mostrar_codigos: Si mostrar códigos de cursos
    """
    if horario is None:
        print("❌ No hay horario para mostrar")
        return
    
    print(f"\n📋 {titulo}")
    print("=" * 100)
    
    # Encabezado de días
    print(f"{'Hora':>8}", end="")
    for dia in DIAS_SEMANA:
        print(f"{dia:>18}", end="")
    print()
    print("-" * 100)
    
    # Filas de horario
    for bloque in range(14):
        print(f"{HORAS_DIA[bloque]:>8}", end="")
        for dia in range(5):
            curso = horario[dia][bloque]
            if curso:
                texto = _formatear_celda_tabla(curso, mostrar_profesores, mostrar_codigos)
                print(f"{texto:>18}", end="")
            else:
                print(f"{'---':>18}", end="")
        print()
    
    print("-" * 100)
    _mostrar_estadisticas_tabla(horario)


def _formatear_celda_tabla(curso: Dict, mostrar_profesores: bool, mostrar_codigos: bool) -> str:
    """Formatea el contenido de una celda para la tabla."""
    if mostrar_codigos and 'codigo' in curso:
        texto = curso['codigo'][:8]
    else:
        texto = curso['nombre'][:12]
        if len(curso['nombre']) > 12:
            texto += "..."
    
    return texto


def _mostrar_estadisticas_tabla(horario: List[List]):
    """Muestra estadísticas básicas del horario en tabla."""
    bloques_ocupados = sum(1 for dia in horario for bloque in dia if bloque is not None)
    
    # Distribución por día
    distribucion = []
    for dia in range(5):
        cursos_dia = sum(1 for bloque in range(14) if horario[dia][bloque] is not None)
        distribucion.append(cursos_dia)
    
    print(f"\n📊 Estadísticas:")
    print(f"   Total bloques ocupados: {bloques_ocupados}")
    print(f"   Distribución por día: {dict(zip(DIAS_SEMANA, distribucion))}")


def mostrar_horario_tabla_detallada(horario: List[List], incluir_salones: bool = True):
    """
    Muestra una tabla más detallada con información completa de cada curso.
    
    Args:
        horario: Matriz del horario
        incluir_salones: Si incluir información de salones
    """
    if horario is None:
        print("❌ No hay horario para mostrar")
        return
    
    print(f"\n📋 HORARIO DETALLADO")
    print("=" * 120)
    
    for dia_idx, dia in enumerate(DIAS_SEMANA):
        print(f"\n🗓️  {dia.upper()}")
        print("-" * 80)
        
        hay_cursos = False
        for bloque in range(14):
            curso = horario[dia_idx][bloque]
            if curso:
                hay_cursos = True
                nombre = curso['nombre'][:30]
                profesor = curso.get('profesor', 'N/A')[:15]
                tipo = curso.get('tipo', 'N/A')[:10]
                salon = curso.get('salon', 'N/A')[:10] if incluir_salones else ''
                
                info_salon = f" | {salon}" if incluir_salones else ""
                print(f"   {HORAS_DIA[bloque]}: {nombre:<30} | {profesor:<15} | {tipo:<10}{info_salon}")
        
        if not hay_cursos:
            print("   (Sin cursos asignados)")


# ============================================================================
# VISUALIZACIÓN GRÁFICA DE HORARIOS
# ============================================================================

def visualizar_horario_grafico(horario: List[List], titulo: str = "Horario Optimizado",
                              guardar_archivo: str = None, mostrar_profesores: bool = True):
    """
    Crea una visualización gráfica del horario usando matplotlib.
    
    Args:
        horario: Matriz del horario
        titulo: Título del gráfico
        guardar_archivo: Si guardar el gráfico (nombre del archivo)
        mostrar_profesores: Si mostrar nombres de profesores en las celdas
    """
    try:
        if horario is None:
            print("❌ No hay horario para visualizar")
            return
        
        # Configurar el gráfico
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Crear matriz de colores y textos
        matriz_colores, matriz_textos = _preparar_matrices_visualizacion(horario, mostrar_profesores)
        
        # Crear el heatmap
        im = ax.imshow(matriz_colores, cmap='tab20', aspect='auto', alpha=0.8)
        
        # Configurar ejes
        ax.set_xticks(range(5))
        ax.set_xticklabels(DIAS_SEMANA, fontsize=12, fontweight='bold')
        ax.set_yticks(range(14))
        ax.set_yticklabels(HORAS_DIA, fontsize=10)
        
        # Añadir texto en cada celda
        for dia in range(5):
            for bloque in range(14):
                if matriz_textos[bloque][dia]:
                    ax.text(dia, bloque, matriz_textos[bloque][dia], 
                           ha='center', va='center', fontsize=8, 
                           color='white', weight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Configurar título y etiquetas
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Días de la Semana', fontsize=12, fontweight='bold')
        ax.set_ylabel('Horas del Día', fontsize=12, fontweight='bold')
        
        # Añadir grid
        ax.set_xticks(np.arange(-0.5, 5, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 14, 1), minor=True)
        ax.grid(which="minor", color="white", linestyle='-', linewidth=2)
        
        # Añadir leyenda de tipos de curso
        _agregar_leyenda_tipos(ax, horario)
        
        plt.tight_layout()
        
        # Guardar si se especifica
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"📊 Gráfico guardado en: {guardar_archivo}")
        
        plt.show()
        
    except ImportError:
        print("❌ matplotlib no está disponible para visualización gráfica")
    except Exception as e:
        print(f"❌ Error al crear visualización: {e}")


def _preparar_matrices_visualizacion(horario: List[List], mostrar_profesores: bool) -> Tuple[np.ndarray, List[List]]:
    """Prepara las matrices de colores y textos para la visualización."""
    matriz_colores = np.zeros((14, 5))
    matriz_textos = [['' for _ in range(5)] for _ in range(14)]
    
    # Mapear cursos a colores
    cursos_unicos = set()
    for dia in range(5):
        for bloque in range(14):
            if horario[dia][bloque] is not None:
                curso_id = horario[dia][bloque].get('id', 0)
                cursos_unicos.add(curso_id)
    
    colores_cursos = {curso_id: i + 1 for i, curso_id in enumerate(cursos_unicos)}
    
    # Llenar matrices
    for dia in range(5):
        for bloque in range(14):
            if horario[dia][bloque] is not None:
                curso = horario[dia][bloque]
                curso_id = curso.get('id', 0)
                
                # Color
                matriz_colores[bloque, dia] = colores_cursos.get(curso_id, 1)
                
                # Texto
                if 'codigo' in curso:
                    texto = curso['codigo'][:8]
                else:
                    texto = curso['nombre'][:10]
                
                if mostrar_profesores and 'profesor' in curso:
                    texto += f"\n{curso['profesor'][:8]}"
                
                matriz_textos[bloque][dia] = texto
    
    return matriz_colores, matriz_textos


def _agregar_leyenda_tipos(ax, horario: List[List]):
    """Agrega una leyenda con los tipos de curso."""
    tipos_encontrados = set()
    for dia in range(5):
        for bloque in range(14):
            if horario[dia][bloque] is not None:
                tipo = horario[dia][bloque].get('tipo', 'Teórico')
                tipos_encontrados.add(tipo)
    
    if tipos_encontrados:
        leyenda_elementos = []
        for tipo in sorted(tipos_encontrados):
            color = COLORES_TIPO.get(tipo, '#95a5a6')
            leyenda_elementos.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, label=tipo))
        
        ax.legend(handles=leyenda_elementos, loc='upper left', bbox_to_anchor=(1.02, 1))


# ============================================================================
# NUEVA FUNCIÓN: GRÁFICAS DE EVOLUCIÓN DEL ALGORITMO GENÉTICO
# ============================================================================

def crear_grafico_evolucion(historia_fitness: List[float], historia_conflictos: List[int],
                           titulo: str = "Evolución del Algoritmo Genético",
                           guardar_archivo: str = None):
    """
    Crea gráficas que muestran la evolución del fitness y conflictos durante el algoritmo genético.
    
    Args:
        historia_fitness: Lista con valores de fitness por generación
        historia_conflictos: Lista con número de conflictos por generación
        titulo: Título del gráfico
        guardar_archivo: Si guardar el gráfico (nombre del archivo)
    """
    try:
        if not historia_fitness or not historia_conflictos:
            print("❌ No hay datos de evolución para mostrar")
            return
        
        # Crear subgráficos
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        generaciones = range(1, len(historia_fitness) + 1)
        
        # Gráfico 1: Evolución del Fitness
        ax1.plot(generaciones, historia_fitness, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_title('Evolución del Fitness (menor es mejor)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Generación')
        ax1.set_ylabel('Fitness')
        ax1.grid(True, alpha=0.3)
        
        # Añadir línea de tendencia
        if len(historia_fitness) > 2:
            z = np.polyfit(generaciones, historia_fitness, 1)
            p = np.poly1d(z)
            ax1.plot(generaciones, p(generaciones), "r--", alpha=0.8, linewidth=1)
        
        # Resaltar mejor valor
        mejor_fitness = min(historia_fitness)
        mejor_gen = historia_fitness.index(mejor_fitness) + 1
        ax1.annotate(f'Mejor: {mejor_fitness:.1f}\nGen: {mejor_gen}', 
                    xy=(mejor_gen, mejor_fitness), xytext=(mejor_gen + 5, mejor_fitness + 5),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        # Gráfico 2: Evolución de Conflictos
        ax2.plot(generaciones, historia_conflictos, 'r-', linewidth=2, marker='s', markersize=4)
        ax2.set_title('Evolución de Conflictos', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Generación')
        ax2.set_ylabel('Número de Conflictos')
        ax2.grid(True, alpha=0.3)
        
        # Resaltar cuando se resolvieron todos los conflictos
        if 0 in historia_conflictos:
            primera_gen_sin_conflictos = historia_conflictos.index(0) + 1
            ax2.axvline(x=primera_gen_sin_conflictos, color='green', linestyle='--', alpha=0.7)
            ax2.annotate(f'Sin conflictos\nGen: {primera_gen_sin_conflictos}', 
                        xy=(primera_gen_sin_conflictos, 0), xytext=(primera_gen_sin_conflictos + 3, max(historia_conflictos) * 0.7),
                        arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
        
        # Gráfico 3: Fitness vs Conflictos (correlación)
        ax3.scatter(historia_conflictos, historia_fitness, alpha=0.6, s=30, c=generaciones, cmap='viridis')
        ax3.set_title('Relación Fitness vs Conflictos', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Número de Conflictos')
        ax3.set_ylabel('Fitness')
        ax3.grid(True, alpha=0.3)
        
        # Añadir colorbar para las generaciones
        cbar = plt.colorbar(ax3.collections[0], ax=ax3)
        cbar.set_label('Generación', rotation=270, labelpad=15)
        
        # Configuración general
        fig.suptitle(titulo, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Estadísticas en texto
        _mostrar_estadisticas_evolucion(historia_fitness, historia_conflictos)
        
        # Guardar si se especifica
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"📊 Gráfico de evolución guardado en: {guardar_archivo}")
        
        plt.show()
        
    except ImportError:
        print("❌ matplotlib/seaborn no están disponibles para visualización")
    except Exception as e:
        print(f"❌ Error al crear gráfico de evolución: {e}")


def _mostrar_estadisticas_evolucion(historia_fitness: List[float], historia_conflictos: List[int]):
    """Muestra estadísticas de la evolución."""
    print(f"\n📈 ESTADÍSTICAS DE EVOLUCIÓN")
    print("=" * 35)
    print(f"Generaciones ejecutadas: {len(historia_fitness)}")
    print(f"Fitness inicial: {historia_fitness[0]:.2f}")
    print(f"Fitness final: {historia_fitness[-1]:.2f}")
    print(f"Mejora total: {historia_fitness[0] - historia_fitness[-1]:.2f}")
    print(f"Conflictos iniciales: {historia_conflictos[0]}")
    print(f"Conflictos finales: {historia_conflictos[-1]}")
    
    if 0 in historia_conflictos:
        primera_sin_conflictos = historia_conflictos.index(0) + 1
        print(f"Primera generación sin conflictos: {primera_sin_conflictos}")
    else:
        print("⚠️  No se resolvieron todos los conflictos")


# ============================================================================
# VISUALIZACIONES COMPARATIVAS
# ============================================================================

def comparar_horarios(horario_antes: List[List], horario_despues: List[List],
                     titulo: str = "Comparación de Horarios"):
    """
    Compara dos horarios lado a lado.
    
    Args:
        horario_antes: Horario antes de la optimización
        horario_despues: Horario después de la optimización
        titulo: Título del gráfico
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Horario antes
        _crear_subgrafico_horario(ax1, horario_antes, "Antes de la Optimización")
        
        # Horario después
        _crear_subgrafico_horario(ax2, horario_despues, "Después de la Optimización")
        
        fig.suptitle(titulo, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ Error al crear comparación: {e}")


def _crear_subgrafico_horario(ax, horario: List[List], titulo: str):
    """Crea un subgráfico de horario."""
    if horario is None:
        ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(titulo)
        return
    
    matriz_colores, matriz_textos = _preparar_matrices_visualizacion(horario, False)
    
    im = ax.imshow(matriz_colores, cmap='tab20', aspect='auto', alpha=0.8)
    
    ax.set_xticks(range(5))
    ax.set_xticklabels(DIAS_SEMANA, fontsize=10)
    ax.set_yticks(range(14))
    ax.set_yticklabels(HORAS_DIA, fontsize=8)
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    
    # Añadir texto en celdas (simplificado)
    for dia in range(5):
        for bloque in range(14):
            if matriz_textos[bloque][dia]:
                ax.text(dia, bloque, matriz_textos[bloque][dia].split('\n')[0], 
                       ha='center', va='center', fontsize=6, color='white', weight='bold')


# ============================================================================
# EXPORTACIÓN DE VISUALIZACIONES
# ============================================================================

def exportar_horario_imagen(horario: List[List], nombre_archivo: str, 
                           formato: str = 'png', dpi: int = 300):
    """
    Exporta el horario como imagen.
    
    Args:
        horario: Matriz del horario
        nombre_archivo: Nombre del archivo (sin extensión)
        formato: Formato de imagen ('png', 'jpg', 'pdf', 'svg')
        dpi: Resolución de la imagen
    """
    try:
        # Crear el gráfico sin mostrarlo
        plt.ioff()  # Desactivar modo interactivo
        
        fig, ax = plt.subplots(figsize=(14, 10))
        matriz_colores, matriz_textos = _preparar_matrices_visualizacion(horario, True)
        
        im = ax.imshow(matriz_colores, cmap='tab20', aspect='auto', alpha=0.8)
        
        # Configurar como en visualizar_horario_grafico
        ax.set_xticks(range(5))
        ax.set_xticklabels(DIAS_SEMANA, fontsize=12, fontweight='bold')
        ax.set_yticks(range(14))
        ax.set_yticklabels(HORAS_DIA, fontsize=10)
        ax.set_title('Horario Optimizado', fontsize=16, fontweight='bold', pad=20)
        
        # Añadir textos
        for dia in range(5):
            for bloque in range(14):
                if matriz_textos[bloque][dia]:
                    ax.text(dia, bloque, matriz_textos[bloque][dia], 
                           ha='center', va='center', fontsize=8, 
                           color='white', weight='bold')
        
        # Guardar
        archivo_completo = f"{nombre_archivo}.{formato}"
        plt.savefig(archivo_completo, format=formato, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()  # Cerrar la figura
        plt.ion()   # Reactivar modo interactivo
        
        print(f"📸 Imagen exportada: {archivo_completo}")
        
    except Exception as e:
        print(f"❌ Error al exportar imagen: {e}")


def crear_reporte_visual_completo(horario: List[List], historia_fitness: List[float] = None,
                                 historia_conflictos: List[int] = None, 
                                 nombre_archivo: str = None):
    """
    Crea un reporte visual completo con horario y estadísticas.
    
    Args:
        horario: Matriz del horario
        historia_fitness: Historia del fitness (opcional)
        historia_conflictos: Historia de conflictos (opcional)
        nombre_archivo: Nombre base para guardar archivos
    """
    try:
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_visual_{timestamp}"
        
        # Crear figura con múltiples subgráficos
        if historia_fitness and historia_conflictos:
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])
            
            # Horario principal
            ax_horario = fig.add_subplot(gs[0, :])
            _crear_subgrafico_horario(ax_horario, horario, "Horario Optimizado")
            
            # Evolución del fitness
            ax_fitness = fig.add_subplot(gs[1, 0])
            generaciones = range(1, len(historia_fitness) + 1)
            ax_fitness.plot(generaciones, historia_fitness, 'b-', linewidth=2)
            ax_fitness.set_title('Evolución del Fitness')
            ax_fitness.set_xlabel('Generación')
            ax_fitness.set_ylabel('Fitness')
            ax_fitness.grid(True, alpha=0.3)
            
            # Evolución de conflictos
            ax_conflictos = fig.add_subplot(gs[1, 1])
            ax_conflictos.plot(generaciones, historia_conflictos, 'r-', linewidth=2)
            ax_conflictos.set_title('Evolución de Conflictos')
            ax_conflictos.set_xlabel('Generación')
            ax_conflictos.set_ylabel('Conflictos')
            ax_conflictos.grid(True, alpha=0.3)
        else:
            # Solo horario
            fig, ax = plt.subplots(figsize=(14, 10))
            _crear_subgrafico_horario(ax, horario, "Horario Optimizado")
        
        plt.tight_layout()
        
        # Guardar
        archivo_pdf = f"{nombre_archivo}.pdf"
        plt.savefig(archivo_pdf, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Reporte visual completo guardado: {archivo_pdf}")
        
    except Exception as e:
        print(f"❌ Error al crear reporte visual: {e}")


# ============================================================================
# UTILIDADES ADICIONALES
# ============================================================================

def validar_horario_para_visualizacion(horario: List[List]) -> bool:
    """
    Valida que el horario tenga el formato correcto para visualización.
    
    Args:
        horario: Matriz del horario
        
    Returns:
        bool: True si es válido
    """
    if horario is None:
        return False
    
    if not isinstance(horario, list) or len(horario) != 5:
        return False
    
    for dia in horario:
        if not isinstance(dia, list) or len(dia) != 14:
            return False
    
    return True


def obtener_estadisticas_visualizacion(horario: List[List]) -> Dict:
    """
    Obtiene estadísticas para mostrar en visualizaciones.
    
    Args:
        horario: Matriz del horario
        
    Returns:
        Dict con estadísticas
    """
    if not validar_horario_para_visualizacion(horario):
        return {}
    
    stats = {
        'bloques_ocupados': 0,
        'bloques_vacios': 0,
        'cursos_unicos': set(),
        'profesores_unicos': set(),
        'tipos_curso': set(),
        'distribucion_diaria': []
    }
    
    for dia in range(5):
        cursos_dia = 0
        for bloque in range(14):
            curso = horario[dia][bloque]
            if curso is not None:
                stats['bloques_ocupados'] += 1
                cursos_dia += 1
                stats['cursos_unicos'].add(curso.get('id', 'N/A'))
                stats['profesores_unicos'].add(curso.get('profesor', 'N/A'))
                stats['tipos_curso'].add(curso.get('tipo', 'Teórico'))
            else:
                stats['bloques_vacios'] += 1
        
        stats['distribucion_diaria'].append(cursos_dia)
    
    # Convertir sets a listas para serialización
    stats['cursos_unicos'] = len(stats['cursos_unicos'])
    stats['profesores_unicos'] = len(stats['profesores_unicos'])
    stats['tipos_curso'] = list(stats['tipos_curso'])
    
    return stats


# ============================================================================
# FUNCIÓN PRINCIPAL PARA PRUEBAS
# ============================================================================

if __name__ == "__main__":
    print("🎨 MÓDULO DE VISUALIZACIÓN DE HORARIOS")
    print("=" * 45)
    
    # Crear horario de ejemplo para pruebas
    horario_ejemplo = [[None for _ in range(14)] for _ in range(5)]
    
    # Llenar con algunos cursos de ejemplo
    horario_ejemplo[0][0] = {'id': 1, 'nombre': 'Matemáticas I', 'profesor': 'García', 'tipo': 'Teórico', 'codigo': 'MAT101'}
    horario_ejemplo[0][1] = {'id': 1, 'nombre': 'Matemáticas I', 'profesor': 'García', 'tipo': 'Teórico', 'codigo': 'MAT101'}
    horario_ejemplo[1][2] = {'id': 2, 'nombre': 'Física I', 'profesor': 'López', 'tipo': 'Teórico', 'codigo': 'FIS101'}
    horario_ejemplo[2][0] = {'id': 3, 'nombre': 'Lab Química', 'profesor': 'Martín', 'tipo': 'Práctico', 'codigo': 'QUI101L'}
    
    print("Mostrando ejemplo de tabla:")
    mostrar_horario_tabla(horario_ejemplo, "Horario de Ejemplo")
    
    print(f"\nEstadísticas del horario:")
    stats = obtener_estadisticas_visualizacion(horario_ejemplo)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Ejemplo de datos de evolución
    fitness_ejemplo = [100, 85, 70, 55, 45, 40, 35, 32, 30, 28]
    conflictos_ejemplo = [15, 12, 10, 8, 5, 3, 2, 1, 0, 0]
    
    print(f"\nCreando gráfico de evolución de ejemplo...")
    crear_grafico_evolucion(fitness_ejemplo, conflictos_ejemplo, 
                           "Ejemplo de Evolución del Algoritmo")
    
    print(f"\nVisualizando horario gráfico...")
    visualizar_horario_grafico(horario_ejemplo, "Ejemplo de Horario Gráfico")
    
    print(f"\n✅ Ejemplos de visualización completados!")


# ============================================================================
# CONFIGURACIÓN DE EXPORTACIÓN
# ============================================================================

__all__ = [
    'mostrar_horario_tabla',
    'mostrar_horario_tabla_detallada',
    'visualizar_horario_grafico',
    'crear_grafico_evolucion',
    'comparar_horarios',
    'exportar_horario_imagen',
    'crear_reporte_visual_completo',
    'validar_horario_para_visualizacion',
    'obtener_estadisticas_visualizacion'
]