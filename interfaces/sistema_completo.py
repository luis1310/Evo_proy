#!/usr/bin/env python3
"""
Sistema completo de optimización de horarios que integra todos los módulos.
Este archivo va en: interfaces/sistema_completo.py

Integra:
- Lectura de PDF y Excel
- Generación de datos de prueba
- Optimización con programación genética
- Detección y resolución de conflictos
- Visualización de resultados
"""

import os
import sys
import pandas as pd
from typing import Dict, List, Optional

# Imports de módulos del proyecto (estructura modular)
from core.lector_pdf_horarios import LectorPDFHorarios
from core.optimizador_genetico import ProgramacionGeneticaOptimizadorMejorado
from core.validador_conflictos import ValidadorConflictos
from generadores.generador_avanzado import GeneradorCargaHorariaAvanzado
from visualizacion.graficos_horarios import (
    visualizar_horario_grafico, 
    mostrar_horario_tabla,
    crear_grafico_evolucion
)
from visualizacion.reportes_conflictos import (
    mostrar_reporte_conflictos,
    mostrar_analisis_gravedad,
    guardar_reporte_conflictos
)


class SistemaOptimizacionCompleto:
    """
    Sistema completo que maneja todos los aspectos de la optimización de horarios.
    """
    
    def __init__(self):
        self.datos_cargados = None
        self.tipo_datos = None  # 'pdf', 'excel', 'generado'
        self.optimizador = None
        self.cursos_disponibles = {}
        self.ultimo_horario_optimizado = None
        self.ultimos_conflictos = None
        
        # Configuración por defecto
        self.config = {
            'mostrar_progreso': True,
            'guardar_automatico': False,
            'visualizacion_automatica': True,
            'analisis_detallado': True
        }
    
    def configurar_sistema(self, **kwargs):
        """Permite configurar comportamientos del sistema."""
        self.config.update(kwargs)
    
    def detectar_y_cargar_archivo(self, archivo_entrada: str) -> bool:
        """
        Detecta el tipo de archivo y lo carga apropiadamente.
        
        Args:
            archivo_entrada: Ruta al archivo a procesar
            
        Returns:
            bool: True si se cargó exitosamente
        """
        if not os.path.exists(archivo_entrada):
            print(f"❌ Error: El archivo '{archivo_entrada}' no existe")
            return False
        
        extension = os.path.splitext(archivo_entrada)[1].lower()
        
        try:
            if extension == '.pdf':
                return self._cargar_pdf(archivo_entrada)
            elif extension in ['.xlsx', '.xls']:
                return self._cargar_excel(archivo_entrada)
            else:
                print(f"❌ Formato de archivo no soportado: {extension}")
                return False
        except Exception as e:
            print(f"❌ Error al cargar archivo: {e}")
            return False
    
    def _cargar_pdf(self, archivo_pdf: str) -> bool:
        """Carga y procesa un archivo PDF."""
        print(f"📄 Procesando archivo PDF: {archivo_pdf}")
        
        try:
            lector = LectorPDFHorarios()
            self.datos_cargados = lector.leer_pdf(archivo_pdf)
            self.tipo_datos = 'pdf'
            
            # Mostrar resumen si está configurado
            if self.config['mostrar_progreso']:
                lector.mostrar_resumen(self.datos_cargados)
            
            # Convertir a formato compatible
            self._preparar_datos_pdf()
            
            return True
        except Exception as e:
            print(f"❌ Error al procesar PDF: {e}")
            return False
    
    def _cargar_excel(self, archivo_excel: str) -> bool:
        """Carga un archivo Excel existente."""
        print(f"📊 Procesando archivo Excel: {archivo_excel}")
        
        try:
            # Cargar usando el método original
            carga_horaria = self._cargar_excel_formato_original(archivo_excel)
            self.datos_cargados = {'carga_horaria': carga_horaria}
            self.tipo_datos = 'excel'
            
            print(f"✅ Archivo Excel cargado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar Excel: {e}")
            return False
    
    def _cargar_excel_formato_original(self, archivo: str):
        """Carga Excel en el formato original del sistema."""
        df = pd.read_excel(archivo, index_col=0)
        carga_horaria = []
        
        for dia_col in df.columns:
            dia_horario = []
            for hora_idx in df.index[:14]:  # Máximo 14 bloques
                celda = df.loc[hora_idx, dia_col]
                if pd.notna(celda):
                    partes = str(celda).split('|')
                    if len(partes) >= 3:
                        dia_horario.append({
                            'id': int(partes[0]),
                            'nombre': partes[1],
                            'profesor': partes[2],
                            'tipo': partes[3] if len(partes) > 3 else 'Teórico'
                        })
                    else:
                        dia_horario.append(None)
                else:
                    dia_horario.append(None)
            carga_horaria.append(dia_horario)
        
        return carga_horaria
    
    def _preparar_datos_pdf(self):
        """Prepara datos de PDF para el optimizador."""
        cursos = self.datos_cargados['cursos']
        
        # Crear carga horaria en formato de matriz
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        carga_horaria = [[None for _ in range(14)] for _ in range(5)]
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias:
                    dia_idx = dias.index(horario['dia'])
                    bloque_idx = self._hora_a_bloque(horario['hora_inicio'])
                    
                    if 0 <= bloque_idx < 14:
                        carga_horaria[dia_idx][bloque_idx] = {
                            'id': curso['id'],
                            'nombre': curso['nombre'],
                            'profesor': curso['profesor'],
                            'tipo': curso['tipo'],
                            'codigo': curso['codigo']
                        }
        
        self.datos_cargados['carga_horaria'] = carga_horaria
    
    def _hora_a_bloque(self, hora_str: str) -> int:
        """Convierte hora a índice de bloque."""
        try:
            hora = int(hora_str.split(':')[0])
            return max(0, hora - 7)
        except:
            return 0
    
    def generar_datos_prueba(self, num_cursos_por_escuela: int = 10) -> bool:
        """
        Genera datos de prueba usando el generador mejorado.
        
        Args:
            num_cursos_por_escuela: Número de cursos por escuela a generar
            
        Returns:
            bool: True si se generaron exitosamente
        """
        print("🔧 Generando datos de prueba...")
        
        try:
            generador = GeneradorCargaHorariaAvanzado()
            cursos = generador.generar_carga_completa(num_cursos_por_escuela=num_cursos_por_escuela)
            
            # Detectar conflictos en datos generados
            if self.config['analisis_detallado']:
                conflictos = generador.detectar_conflictos(cursos)
                generador.generar_reporte_conflictos(conflictos)
            
            # Crear matriz de horarios
            carga_horaria = generador.crear_matriz_horarios(cursos)
            
            self.datos_cargados = {
                'cursos': cursos,
                'carga_horaria': carga_horaria,
                'conflictos_iniciales': conflictos if self.config['analisis_detallado'] else []
            }
            self.tipo_datos = 'generado'
            
            print("✅ Datos de prueba generados exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al generar datos de prueba: {e}")
            return False
    
    def obtener_cursos_disponibles(self) -> Dict[int, Dict]:
        """Obtiene la lista de cursos disponibles según el tipo de datos."""
        if not self.datos_cargados:
            return {}
        
        if self.tipo_datos == 'pdf' or self.tipo_datos == 'generado':
            # Datos de PDF o generados tienen lista de cursos
            cursos = {}
            for curso in self.datos_cargados['cursos']:
                cursos[curso['id']] = curso
            return cursos
        
        elif self.tipo_datos == 'excel':
            # Datos de Excel - extraer de la carga horaria
            cursos = {}
            for dia in self.datos_cargados['carga_horaria']:
                for bloque in dia:
                    if bloque and bloque['id'] not in cursos:
                        cursos[bloque['id']] = bloque
            return cursos
        
        return {}
    
    def mostrar_cursos_disponibles(self):
        """Muestra los cursos disponibles de forma organizada."""
        cursos = self.obtener_cursos_disponibles()
        
        if not cursos:
            print("❌ No hay cursos disponibles")
            return
        
        print(f"\n📚 CURSOS DISPONIBLES ({len(cursos)} total)")
        print("="*60)
        
        if self.tipo_datos in ['pdf', 'generado']:
            # Agrupar por escuela
            por_escuela = {}
            for curso in cursos.values():
                codigo = curso.get('codigo', '')
                escuela = codigo[:2] if codigo else 'XX'
                if escuela not in por_escuela:
                    por_escuela[escuela] = []
                por_escuela[escuela].append(curso)
            
            for escuela, cursos_escuela in sorted(por_escuela.items()):
                print(f"\n🏫 {escuela}:")
                for curso in cursos_escuela[:8]:  # Mostrar máximo 8 por escuela
                    horarios_info = ""
                    if 'horarios' in curso and curso['horarios']:
                        h = curso['horarios'][0]
                        horarios_info = f" ({h['dia']} {h['hora_inicio']}-{h['hora_fin']})"
                    
                    nombre_corto = curso['nombre'][:25] + "..." if len(curso['nombre']) > 25 else curso['nombre']
                    codigo = curso.get('codigo', 'N/A')
                    print(f"   {curso['id']:3d}. {codigo[:8]:<8} {nombre_corto:<28}{horarios_info}")
                
                if len(cursos_escuela) > 8:
                    print(f"       ... y {len(cursos_escuela) - 8} cursos más")
        
        else:
            # Mostrar lista simple para Excel
            for i, (id_curso, curso) in enumerate(sorted(cursos.items())):
                if i >= 20:  # Límite para no saturar la pantalla
                    print(f"   ... y {len(cursos) - 20} cursos más")
                    break
                print(f"   {id_curso:3d}. {curso['nombre'][:40]} - {curso['profesor']}")
    
    def seleccionar_cursos_interactivo(self) -> List[int]:
        """Selección interactiva mejorada de cursos."""
        cursos = self.obtener_cursos_disponibles()
        
        if not cursos:
            print("❌ No hay cursos disponibles para seleccionar")
            return []
        
        self.mostrar_cursos_disponibles()
        
        print(f"\n🎯 SELECCIÓN DE CURSOS")
        print("="*40)
        print("Opciones de selección:")
        print("  • IDs individuales: 1, 5, 10")
        print("  • Rangos: 1-15")
        if self.tipo_datos in ['pdf', 'generado']:
            print("  • Por escuela: BF, CF, CM, CQ, CC")
        print("  • 'todos' para seleccionar todos")
        print("  • 'auto' para selección automática recomendada")
        print("  • 'fin' para terminar")
        
        seleccionados = []
        
        while True:
            prompt = f"\nSelección ({len(seleccionados)} cursos): "
            entrada = input(prompt).strip()
            
            if entrada.lower() == 'fin':
                break
            elif entrada.lower() == 'todos':
                seleccionados = list(cursos.keys())
                print(f"✅ Seleccionados todos los {len(seleccionados)} cursos")
                break
            elif entrada.lower() == 'auto':
                seleccionados = self._seleccion_automatica_recomendada(cursos)
                print(f"✅ Selección automática: {len(seleccionados)} cursos recomendados")
                break
            elif '-' in entrada and entrada.replace('-', '').isdigit():
                # Rango
                try:
                    inicio, fin = map(int, entrada.split('-'))
                    añadidos = 0
                    for id_curso in range(inicio, fin + 1):
                        if id_curso in cursos and id_curso not in seleccionados:
                            seleccionados.append(id_curso)
                            añadidos += 1
                    print(f"✅ Añadidos {añadidos} cursos del rango {inicio}-{fin}")
                except ValueError:
                    print("❌ Formato de rango inválido")
            elif entrada.isdigit():
                # ID individual
                id_curso = int(entrada)
                if id_curso in cursos:
                    if id_curso not in seleccionados:
                        seleccionados.append(id_curso)
                        curso = cursos[id_curso]
                        print(f"✅ Añadido: {curso['nombre'][:30]}")
                    else:
                        print("⚠️  Curso ya seleccionado")
                else:
                    print("❌ ID de curso no válido")
            elif len(entrada) == 2 and entrada.isalpha() and self.tipo_datos in ['pdf', 'generado']:
                # Escuela completa
                entrada = entrada.upper()
                añadidos = 0
                for curso in cursos.values():
                    codigo = curso.get('codigo', '')
                    if codigo.startswith(entrada) and curso['id'] not in seleccionados:
                        seleccionados.append(curso['id'])
                        añadidos += 1
                if añadidos > 0:
                    print(f"✅ Añadidos {añadidos} cursos de la escuela {entrada}")
                else:
                    print(f"❌ No se encontraron cursos para la escuela {entrada}")
            else:
                print("❌ Formato no reconocido")
        
        return sorted(seleccionados)
    
    def _seleccion_automatica_recomendada(self, cursos: Dict[int, Dict]) -> List[int]:
        """Genera una selección automática recomendada de cursos."""
        if self.tipo_datos in ['pdf', 'generado']:
            # Para datos estructurados, seleccionar algunos de cada escuela
            por_escuela = {}
            for curso in cursos.values():
                codigo = curso.get('codigo', '')
                escuela = codigo[:2] if codigo else 'XX'
                if escuela not in por_escuela:
                    por_escuela[escuela] = []
                por_escuela[escuela].append(curso['id'])
            
            seleccionados = []
            for escuela, ids_cursos in por_escuela.items():
                # Seleccionar máximo 6 cursos por escuela
                seleccionados.extend(ids_cursos[:6])
            
            return seleccionados
        else:
            # Para Excel, seleccionar los primeros 15 cursos
            return list(cursos.keys())[:15]
    
    def ejecutar_optimizacion(self, cursos_seleccionados: List[int]):
        """
        Ejecuta la optimización con el algoritmo genético mejorado.
        
        Args:
            cursos_seleccionados: Lista de IDs de cursos a optimizar
            
        Returns:
            Tuple[horario_optimizado, conflictos_finales]
        """
        if not cursos_seleccionados:
            print("❌ No se han seleccionado cursos para optimizar")
            return None, None
        
        print(f"\n🚀 INICIANDO OPTIMIZACIÓN")
        print("="*50)
        print(f"Cursos seleccionados: {len(cursos_seleccionados)}")
        print(f"Algoritmo: Programación Genética con detección de conflictos")
        
        # Inicializar optimizador mejorado
        carga_horaria = self.datos_cargados['carga_horaria']
        self.optimizador = ProgramacionGeneticaOptimizadorMejorado(carga_horaria)
        
        # Ejecutar evolución
        if self.config['mostrar_progreso']:
            print("\nIniciando evolución...")
        
        try:
            mejor_individuo, conflictos_finales = self.optimizador.evolucionar_mejorado(cursos_seleccionados)
            
            if not mejor_individuo:
                print("❌ No se pudo encontrar una solución válida")
                return None, None
            
            # Generar horario final
            horario_inicial = self.optimizador.crear_horario_inicial(cursos_seleccionados)
            horario_optimizado = mejor_individuo.ejecutar(
                horario_inicial, cursos_seleccionados, carga_horaria
            )
            
            # Guardar resultados para uso posterior
            self.ultimo_horario_optimizado = horario_optimizado
            self.ultimos_conflictos = conflictos_finales
            
            return horario_optimizado, conflictos_finales
            
        except Exception as e:
            print(f"❌ Error durante la optimización: {e}")
            return None, None
    
    def analizar_resultados(self, horario_optimizado, conflictos_finales):
        """
        Analiza y muestra los resultados de la optimización.
        
        Args:
            horario_optimizado: Matriz del horario optimizado
            conflictos_finales: Conflictos detectados en el resultado
        """
        if horario_optimizado is None:
            return
        
        print(f"\n📊 ANÁLISIS DE RESULTADOS")
        print("="*50)
        
        # Estadísticas básicas
        bloques_ocupados = sum(1 for dia in horario_optimizado for bloque in dia if bloque is not None)
        tiempos_muertos = self.optimizador.calcular_tiempos_muertos(horario_optimizado)
        compactacion = self.optimizador.evaluar_compactacion(horario_optimizado)
        distribucion = self.optimizador.evaluar_distribucion_semanal(horario_optimizado)
        
        print(f"📈 Métricas de calidad:")
        print(f"   • Bloques ocupados: {bloques_ocupados}")
        print(f"   • Tiempos muertos: {tiempos_muertos}")
        print(f"   • Puntuación compactación: {compactacion:.1f}")
        print(f"   • Varianza distribución: {distribucion:.1f}")
        
        # Mostrar conflictos
        if self.config['analisis_detallado']:
            mostrar_reporte_conflictos(conflictos_finales)
            mostrar_analisis_gravedad(conflictos_finales)
        
        # Distribución por día
        print(f"\n📅 Distribución semanal:")
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        for dia_idx, dia in enumerate(dias):
            cursos_dia = sum(1 for bloque in range(14) if horario_optimizado[dia_idx][bloque] is not None)
            print(f"   • {dia:<10}: {cursos_dia:2d} bloques")
        
        # Guardar reporte si está configurado
        if self.config['guardar_automatico']:
            self._guardar_reporte_automatico(horario_optimizado, conflictos_finales)
    
    def _guardar_reporte_automatico(self, horario, conflictos):
        """Guarda automáticamente reportes de la optimización."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar reporte de conflictos
            archivo_conflictos = f"datos/resultados/reporte_conflictos_{timestamp}.txt"
            guardar_reporte_conflictos(conflictos, archivo_conflictos)
            
            # Guardar horario
            self.guardar_horario_excel(horario, f"datos/resultados/horario_optimizado_{timestamp}.xlsx")
            
        except Exception as e:
            print(f"⚠️  No se pudo guardar automáticamente: {e}")
    
    def ofrecer_opciones_post_optimizacion(self, horario_optimizado):
        """Ofrece opciones después de la optimización."""
        if horario_optimizado is None:
            return
        
        print(f"\n🎛️  OPCIONES ADICIONALES")
        print("="*30)
        
        while True:
            print("\n¿Qué desea hacer?")
            print("1. Ver horario en tabla")
            print("2. Ver gráfico de evolución")
            print("3. Visualizar horario gráficamente")
            print("4. Guardar en Excel")
            print("5. Análisis detallado de conflictos")
            print("6. Reoptimizar con diferentes parámetros")
            print("7. Continuar")
            
            opcion = input("\nSeleccione una opción (1-7): ").strip()
            
            if opcion == '1':
                mostrar_horario_tabla(horario_optimizado)
            elif opcion == '2':
                if self.optimizador and hasattr(self.optimizador, 'historia_fitness'):
                    crear_grafico_evolucion(
                        self.optimizador.historia_fitness,
                        self.optimizador.historia_conflictos
                    )
                else:
                    print("❌ No hay datos de evolución disponibles")
            elif opcion == '3':
                if self.config['visualizacion_automatica']:
                    visualizar_horario_grafico(horario_optimizado)
                else:
                    print("❌ Visualización gráfica deshabilitada")
            elif opcion == '4':
                nombre_archivo = input("Nombre del archivo (sin extensión): ").strip()
                if not nombre_archivo:
                    nombre_archivo = "horario_optimizado"
                self.guardar_horario_excel(horario_optimizado, f"{nombre_archivo}.xlsx")
            elif opcion == '5':
                if self.ultimos_conflictos:
                    mostrar_reporte_conflictos(self.ultimos_conflictos)
                    mostrar_analisis_gravedad(self.ultimos_conflictos)
                else:
                    print("❌ No hay datos de conflictos disponibles")
            elif opcion == '6':
                respuesta = input("¿Reoptimizar con más generaciones? (s/n): ")
                if respuesta.lower() == 's':
                    if self.optimizador:
                        self.optimizador.generaciones += 20
                        print("✅ Configurado para 20 generaciones adicionales")
                    else:
                        print("❌ Optimizador no disponible")
            elif opcion == '7':
                break
            else:
                print("❌ Opción no válida")
    
    def guardar_horario_excel(self, horario, nombre_archivo: str = None):
        """
        Guarda el horario optimizado en Excel.
        
        Args:
            horario: Matriz del horario
            nombre_archivo: Nombre del archivo (opcional)
        """
        try:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            horas = [f"{7+i}:00 - {8+i}:00" for i in range(14)]
            
            # Crear DataFrame
            df = pd.DataFrame(index=horas, columns=dias)
            
            for dia in range(5):
                for bloque in range(14):
                    if horario[dia][bloque] is not None:
                        curso = horario[dia][bloque]
                        if 'codigo' in curso:
                            texto = f"{curso['codigo']} - {curso['nombre'][:20]}"
                        else:
                            texto = f"{curso['nombre'][:25]}"
                        if 'profesor' in curso:
                            texto += f"\n{curso['profesor']}"
                        df.iloc[bloque, dia] = texto
            
            # Generar nombre de archivo si no se proporciona
            if nombre_archivo is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"horario_optimizado_{timestamp}.xlsx"
            
            # Asegurar que el directorio existe
            directorio = os.path.dirname(nombre_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            
            df.to_excel(nombre_archivo)
            print(f"✅ Horario guardado en: {nombre_archivo}")
            
        except Exception as e:
            print(f"❌ Error al guardar archivo: {e}")
    
    def ejecutar(self, archivo_entrada: str = None):
        """
        Ejecuta el sistema completo.
        
        Args:
            archivo_entrada: Archivo a procesar (opcional)
        """
        print("🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS")
        print("   Con detección y resolución de conflictos")
        print("="*60)
        
        try:
            # Paso 1: Cargar datos
            datos_cargados = False
            
            if archivo_entrada:
                datos_cargados = self.detectar_y_cargar_archivo(archivo_entrada)
            
            if not datos_cargados:
                print("\n🔧 Generando datos de prueba...")
                # Preguntar nivel de complejidad
                print("Seleccione nivel de complejidad:")
                print("1. Básico (10 cursos por escuela)")
                print("2. Intermedio (15 cursos por escuela)")
                print("3. Avanzado (20 cursos por escuela)")
                
                nivel = input("Nivel (1-3, Enter para básico): ").strip()
                cursos_por_escuela = {'1': 10, '2': 15, '3': 20}.get(nivel, 10)
                
                datos_cargados = self.generar_datos_prueba(cursos_por_escuela)
            
            if not datos_cargados:
                print("❌ No se pudieron cargar o generar datos")
                return
            
            # Paso 2: Seleccionar cursos
            cursos_seleccionados = self.seleccionar_cursos_interactivo()
            
            if not cursos_seleccionados:
                print("❌ No se seleccionaron cursos. Saliendo...")
                return
            
            # Paso 3: Optimizar
            horario_optimizado, conflictos_finales = self.ejecutar_optimizacion(cursos_seleccionados)
            
            # Paso 4: Mostrar resultados
            if horario_optimizado:
                self.analizar_resultados(horario_optimizado, conflictos_finales)
                
                # Mostrar horario básico si está configurado
                if self.config['visualizacion_automatica']:
                    mostrar_horario_tabla(horario_optimizado)
                
                # Ofrecer opciones adicionales
                self.ofrecer_opciones_post_optimizacion(horario_optimizado)
                
                print("\n✅ Optimización completada exitosamente!")
            else:
                print("❌ La optimización no pudo generar un horario válido")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Proceso interrumpido por el usuario")
        except Exception as e:
            print(f"\n❌ Error durante la ejecución: {e}")
            if self.config['analisis_detallado']:
                import traceback
                traceback.print_exc()
    
    def obtener_estadisticas_sistema(self) -> Dict:
        """Obtiene estadísticas del sistema y datos cargados."""
        stats = {
            'tipo_datos': self.tipo_datos,
            'cursos_disponibles': len(self.obtener_cursos_disponibles()),
            'optimizador_inicializado': self.optimizador is not None,
            'ultimo_horario_disponible': self.ultimo_horario_optimizado is not None
        }
        
        if self.datos_cargados:
            if 'cursos' in self.datos_cargados:
                stats['total_cursos_sistema'] = len(self.datos_cargados['cursos'])
            if 'conflictos_iniciales' in self.datos_cargados:
                stats['conflictos_iniciales'] = len(self.datos_cargados['conflictos_iniciales'])
        
        if self.optimizador and hasattr(self.optimizador, 'historia_fitness'):
            stats['generaciones_ejecutadas'] = len(self.optimizador.historia_fitness)
            stats['mejor_fitness'] = min(self.optimizador.historia_fitness) if self.optimizador.historia_fitness else None
        
        return stats


def main():
    """Función principal para ejecución directa del módulo."""
    import sys
    
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        if archivo in ['--help', '-h']:
            mostrar_ayuda()
            return
    else:
        archivo = None
    
    # Crear y ejecutar sistema
    sistema = SistemaOptimizacionCompleto()
    
    # Configurar sistema según argumentos
    if '--debug' in sys.argv:
        sistema.configurar_sistema(
            mostrar_progreso=True,
            analisis_detallado=True,
            visualizacion_automatica=True
        )
    elif '--rapido' in sys.argv:
        sistema.configurar_sistema(
            mostrar_progreso=False,
            analisis_detallado=False,
            visualizacion_automatica=False
        )
    
    sistema.ejecutar(archivo)


def mostrar_ayuda():
    """Muestra la ayuda del sistema."""
    print("""
🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS
==================================================

USO:
    python interfaces/sistema_completo.py [archivo] [opciones]

ARCHIVOS SOPORTADOS:
    • PDF: Horarios académicos en formato tabular
    • Excel: Matriz de horarios (formato original)
    • Sin archivo: Genera datos de prueba automáticamente

OPCIONES:
    --debug     Modo detallado con todos los análisis
    --rapido    Modo rápido sin visualizaciones extra
    --help, -h  Muestra esta ayuda

EJEMPLOS:
    python interfaces/sistema_completo.py datos/Horarios_2023_1.pdf
    python interfaces/sistema_completo.py datos/carga_horaria.xlsx --debug
    python interfaces/sistema_completo.py --rapido

CARACTERÍSTICAS:
    ✅ Detección automática de conflictos de horarios
    ✅ Resolución inteligente de cruces de profesores y salones
    ✅ Optimización con programación genética avanzada
    ✅ Visualización gráfica y en tabla
    ✅ Exportación a Excel con formato profesional
    ✅ Selección flexible de cursos (individual, rango, escuela)
    ✅ Análisis detallado de resultados

TIPOS DE CONFLICTOS DETECTADOS:
    • Profesores con clases simultáneas
    • Salones con múltiples asignaciones  
    • Sobrecarga de horas por profesor
    • Distribución desigual de carga semanal

SELECCIÓN DE CURSOS:
    • IDs individuales: 1, 5, 10
    • Rangos: 1-20 (cursos del 1 al 20)
    • Por escuela: BF (todos los cursos de Física)
    • 'todos' para seleccionar todos los cursos
    • 'auto' para selección automática recomendada
    • 'fin' para terminar la selección

ESTRUCTURA MODULAR:
    Este sistema integra módulos de:
    • core/: Algoritmos principales y validación
    • generadores/: Creación de datos de prueba
    • visualizacion/: Gráficos y reportes
    • interfaces/: Esta interfaz de usuario

¿NECESITA MÁS AYUDA?
    Ejecute sin argumentos para modo interactivo con datos de prueba.
""")


# Configuración para importación como módulo
__all__ = [
    'SistemaOptimizacionCompleto',
    'main',
    'mostrar_ayuda'
]

if __name__ == "__main__":
    main()