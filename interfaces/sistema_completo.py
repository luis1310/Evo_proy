#!/usr/bin/env python3
"""
Sistema completo de optimización de horarios que integra todos los módulos.
VERSIÓN INTEGRADA - Con soporte para formato universitario y detección automática.

Este archivo va en: interfaces/sistema_completo.py

Integra:
- Lectura de PDF y Excel (estándar y universitario)
- Generación de datos de prueba
- Optimización con programación genética
- Detección y resolución de conflictos
- Visualización de resultados
"""

import os
import sys
import pandas as pd
import re
from typing import Dict, List, Optional

# Imports de módulos del proyecto (estructura modular)
from core.lector_horarios import LectorHorarios, LectorPDFHorarios
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
    VERSIÓN INTEGRADA con soporte universitario.
    """
    
    def __init__(self):
        self.datos_cargados = None
        self.tipo_datos = None  # 'pdf', 'excel_estandar', 'excel_universitario', 'generado'
        self.formato_detectado = None
        self.optimizador = None
        self.cursos_disponibles = {}
        self.ultimo_horario_optimizado = None
        self.ultimos_conflictos = None
        
        # Configuración por defecto
        self.config = {
            'mostrar_progreso': True,
            'guardar_automatico': False,
            'visualizacion_automatica': True,
            'analisis_detallado': True,
            'modo_universitario': False  # NUEVO
        }
        
        # Mapeo de días para formato universitario
        self.dias_semana = {
            'LU': 'Lunes',
            'MA': 'Martes', 
            'MI': 'Miércoles',
            'JU': 'Jueves',
            'VI': 'Viernes',
            'SA': 'Sábado'
        }
    
    def configurar_sistema(self, **kwargs):
        """Permite configurar comportamientos del sistema."""
        self.config.update(kwargs)
        
        # Activar modo universitario si se especifica
        if kwargs.get('modo_universitario', False):
            self.activar_modo_universitario()
    
    def activar_modo_universitario(self):
        """Activa el modo especializado para archivos universitarios."""
        self.config['modo_universitario'] = True
        self.config['analisis_detallado'] = True
        print("🎓 Modo universitario activado")
    
    def detectar_formato_archivo(self, archivo: str) -> str:
        """
        Detecta el formato del archivo para usar el procesador apropiado.
        
        Args:
            archivo: Ruta al archivo a procesar
            
        Returns:
            str: 'pdf', 'excel_estandar', 'excel_universitario'
        """
        extension = os.path.splitext(archivo)[1].lower()
        
        if extension == '.pdf':
            return 'pdf'
        elif extension in ['.xlsx', '.xls']:
            return self._detectar_formato_excel(archivo)
        else:
            return 'desconocido'
    
    def _detectar_formato_excel(self, archivo: str) -> str:
        """
        Detecta si un Excel es formato universitario o estándar.
        """
        try:
            # Leer primeras filas para detectar formato
            df = pd.read_excel(archivo, header=None, nrows=15)
            
            # Buscar indicadores de formato universitario
            for i, fila in df.iterrows():
                texto_fila = ' '.join([str(x) for x in fila.values if pd.notna(x)])
                texto_upper = texto_fila.upper()
                
                # Indicadores específicos de formato universitario
                if any(indicador in texto_upper for indicador in 
                      ['ESCUELA PROFESIONAL', 'CURSOS OFRECIDOS', 'PERIODO ACADÉMICO']):
                    return 'excel_universitario'
                
                # Buscar patrones de horarios universitarios
                if any(patron in texto_fila for patron in ['LU ', 'MA ', 'MI ', 'JU ', 'VI ']):
                    return 'excel_universitario'
                
                # Buscar códigos universitarios
                if re.search(r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?\s*\n?\s*[A-Z]', texto_fila):
                    return 'excel_universitario'
            
            return 'excel_estandar'
            
        except Exception:
            return 'excel_estandar'
    
    def detectar_y_cargar_archivo(self, archivo_entrada: str) -> bool:
        """
        Detecta el tipo de archivo y lo carga apropiadamente.
        VERSIÓN MEJORADA con detección automática.
        
        Args:
            archivo_entrada: Ruta al archivo a procesar
            
        Returns:
            bool: True si se cargó exitosamente
        """
        if not os.path.exists(archivo_entrada):
            print(f"❌ Error: El archivo '{archivo_entrada}' no existe")
            return False
        
        # Detectar formato
        self.formato_detectado = self.detectar_formato_archivo(archivo_entrada)
        print(f"🔍 Formato detectado: {self.formato_detectado}")
        
        try:
            if self.formato_detectado == 'pdf':
                return self._cargar_pdf(archivo_entrada)
            elif self.formato_detectado == 'excel_universitario':
                return self._cargar_excel_universitario(archivo_entrada)
            elif self.formato_detectado == 'excel_estandar':
                return self._cargar_excel_estandar(archivo_entrada)
            else:
                print(f"❌ Formato de archivo no soportado: {self.formato_detectado}")
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
    
    def _cargar_excel_universitario(self, archivo_excel: str) -> bool:
        """
        Carga un archivo Excel con formato universitario.
        NUEVA FUNCIONALIDAD.
        """
        print(f"🎓 Procesando archivo Excel universitario: {archivo_excel}")
        
        try:
            # Usar lector universitario especializado
            datos = self._procesar_excel_universitario(archivo_excel)
            self.datos_cargados = datos
            self.tipo_datos = 'excel_universitario'
            self.config['modo_universitario'] = True
            
            # Mostrar resumen universitario
            if self.config['mostrar_progreso']:
                self._mostrar_resumen_universitario(datos)
            
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar Excel universitario: {e}")
            return False
    
    def _cargar_excel_estandar(self, archivo_excel: str) -> bool:
        """Carga un archivo Excel estándar."""
        print(f"📊 Procesando archivo Excel estándar: {archivo_excel}")
        
        try:
            # Cargar usando el método original
            carga_horaria = self._cargar_excel_formato_original(archivo_excel)
            self.datos_cargados = {'carga_horaria': carga_horaria}
            self.tipo_datos = 'excel_estandar'
            
            print(f"✅ Archivo Excel estándar cargado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar Excel estándar: {e}")
            return False
    
    def _procesar_excel_universitario(self, archivo_excel: str) -> Dict:
        """
        Procesa archivo Excel con formato universitario específico.
        NUEVA FUNCIONALIDAD INTEGRADA.
        """
        df = pd.read_excel(archivo_excel, header=None)
        
        cursos = []
        curso_actual = None
        escuela_actual = None
        id_curso = 1
        
        print("🔄 Analizando estructura universitaria...")
        
        for i, fila in df.iterrows():
            # Convertir fila a lista y limpiar
            datos_fila = [str(x).strip() if pd.notna(x) else '' for x in fila.values]
            
            # Detectar encabezado de escuela
            if self._es_encabezado_escuela(datos_fila[0]):
                escuela_actual = self._extraer_codigo_escuela(datos_fila[0])
                print(f"🏫 Procesando escuela: {escuela_actual}")
                curso_actual = None
                continue
            
            # Detectar inicio de nuevo curso
            if self._es_inicio_curso_universitario(datos_fila):
                curso_actual = self._crear_curso_base_universitario(datos_fila, escuela_actual)
                continue
            
            # Procesar secciones del curso actual
            if curso_actual and self._es_seccion_curso_universitario(datos_fila):
                seccion_info = self._procesar_seccion_universitaria(datos_fila, curso_actual, id_curso)
                if seccion_info:
                    cursos.append(seccion_info)
                    id_curso += 1
        
        # Crear matriz de horarios
        matriz_horarios = self._crear_matriz_horarios_universitaria(cursos)
        
        # Generar estadísticas
        estadisticas = self._generar_estadisticas_universitarias(cursos)
        
        return {
            'cursos': cursos,
            'carga_horaria': matriz_horarios,
            'estadisticas': estadisticas,
            'formato': 'universitario'
        }
    
    def _es_encabezado_escuela(self, texto: str) -> bool:
        """Detecta si una línea es un encabezado de escuela."""
        if not texto or texto == 'nan':
            return False
        texto_upper = texto.upper()
        indicadores = [
            'ESCUELA PROFESIONAL',
            'FACULTAD DE',
            'CARRERA DE',
            'DEPARTAMENTO'
        ]
        return any(indicador in texto_upper for indicador in indicadores)
    
    def _extraer_codigo_escuela(self, texto: str) -> str:
        """Extrae el código de la escuela del encabezado."""
        texto_upper = texto.upper()
        
        # Mapeo de nombres a códigos
        mapeo_escuelas = {
            'FÍSICA': 'BF',
            'MATEMÁTICA': 'CM',
            'QUÍMICA': 'CQ',
            'BIOLOGÍA': 'CB',
            'COMPUTACIÓN': 'CC',
            'INGENIERÍA': 'IF',
            'ESTADÍSTICA': 'CE'
        }
        
        for nombre, codigo in mapeo_escuelas.items():
            if nombre in texto_upper:
                return codigo
        
        return 'XX'  # Código por defecto
    
    def _es_inicio_curso_universitario(self, datos_fila: List[str]) -> bool:
        """Detecta si la fila contiene el inicio de un nuevo curso."""
        if not datos_fila[0] or datos_fila[0] == 'nan':
            return False
        
        # Verificar si parece un nombre de curso
        nombre_posible = datos_fila[0].strip()
        if (len(nombre_posible) > 3 and 
            not re.match(r'^[A-Z]{2,3}\d{2,3}', nombre_posible) and
            'ESCUELA' not in nombre_posible.upper()):
            return True
        
        return False
    
    def _crear_curso_base_universitario(self, datos_fila: List[str], escuela: str) -> Dict:
        """Crea la información base de un curso universitario."""
        return {
            'nombre': datos_fila[0].strip(),
            'escuela': escuela,
            'secciones': []
        }
    
    def _es_seccion_curso_universitario(self, datos_fila: List[str]) -> bool:
        """Detecta si la fila contiene información de una sección."""
        return (len(datos_fila) >= 3 and 
                (self._contiene_codigo_seccion(datos_fila[1]) or 
                 self._contiene_horarios_universitarios(datos_fila[2])))
    
    def _contiene_codigo_seccion(self, texto: str) -> bool:
        """Verifica si el texto contiene un código de sección."""
        if not texto or texto == 'nan':
            return False
        
        # Buscar patrones como "BFI01\nA" o códigos similares
        patron_codigo = r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?\s*\n?\s*[A-Z]'
        return bool(re.search(patron_codigo, texto))
    
    def _contiene_horarios_universitarios(self, texto: str) -> bool:
        """Verifica si el texto contiene información de horarios universitarios."""
        if not texto or texto == 'nan':
            return False
        
        # Buscar patrones de horarios como "LU 10-12" o "MI 14-16"
        patron_horario = r'[A-Z]{2}\s+\d{1,2}-\d{1,2}'
        return bool(re.search(patron_horario, texto))
    
    def _procesar_seccion_universitaria(self, datos_fila: List[str], curso_base: Dict, id_curso: int) -> Optional[Dict]:
        """Procesa una sección específica de un curso universitario."""
        try:
            # Extraer información de la sección
            codigo_seccion = self._extraer_codigo_seccion_universitario(datos_fila[1])
            horarios_texto = datos_fila[2] if len(datos_fila) > 2 else ''
            salones_texto = datos_fila[3] if len(datos_fila) > 3 else ''
            profesores_texto = datos_fila[4] if len(datos_fila) > 4 else ''
            capacidad = self._extraer_capacidad_universitaria(datos_fila[5] if len(datos_fila) > 5 else '')
            
            # Procesar horarios
            horarios = self._procesar_horarios_universitarios(horarios_texto, salones_texto)
            
            # Procesar profesores
            profesores = self._procesar_profesores_universitarios(profesores_texto)
            
            if not horarios:
                return None
            
            # Crear objeto de curso completo
            curso_completo = {
                'id': id_curso,
                'codigo': codigo_seccion,
                'nombre': curso_base['nombre'],
                'escuela': curso_base['escuela'],
                'seccion': codigo_seccion.split('_')[-1] if '_' in codigo_seccion else 'A',
                'profesor': profesores[0] if profesores else 'SIN ASIGNAR',
                'profesores': profesores,
                'tipo': self._determinar_tipo_curso_universitario(horarios_texto, salones_texto),
                'capacidad': capacidad,
                'horarios': horarios,
                'salones': self._extraer_salones_universitarios(salones_texto)
            }
            
            return curso_completo
            
        except Exception as e:
            print(f"⚠️  Error procesando sección universitaria: {e}")
            return None
    
    def _extraer_codigo_seccion_universitario(self, texto: str) -> str:
        """Extrae el código de la sección universitaria."""
        if not texto or texto == 'nan':
            return f"CURSO_{id(self)}_{len(self.datos_cargados.get('cursos', []))}_A"
        
        # Limpiar el texto y buscar patrón de código
        texto_limpio = texto.replace('\n', ' ').strip()
        
        # Buscar patrón como "BFI01 A"
        patron = r'([A-Z]{2,3}[I]?\d{2,3}[A-Z]?)\s+([A-Z])'
        match = re.search(patron, texto_limpio)
        
        if match:
            codigo_base = match.group(1)
            seccion = match.group(2)
            return f"{codigo_base}_{seccion}"
        
        return f"CURSO_{id(self)}_{len(self.datos_cargados.get('cursos', []))}_A"
    
    def _procesar_horarios_universitarios(self, horarios_texto: str, salones_texto: str) -> List[Dict]:
        """Procesa el texto de horarios universitarios."""
        if not horarios_texto or horarios_texto == 'nan':
            return []
        
        horarios = []
        
        # Separar por líneas
        lineas_horario = [linea.strip() for linea in horarios_texto.split('\n') if linea.strip()]
        lineas_salon = [linea.strip() for linea in salones_texto.split('\n') if linea.strip()] if salones_texto else []
        
        for i, linea in enumerate(lineas_horario):
            # Buscar patrón de horario: "LU 10-12" o "MI 14-16"
            patron = r'([A-Z]{2})\s+(\d{1,2})-(\d{1,2})'
            matches = re.findall(patron, linea)
            
            salon = lineas_salon[i] if i < len(lineas_salon) else 'SALON NO ASIGNADO'
            salon = self._limpiar_salon_universitario(salon)
            
            for dia_codigo, hora_inicio, hora_fin in matches:
                if dia_codigo in self.dias_semana:
                    horario_info = {
                        'dia': self.dias_semana[dia_codigo],
                        'dia_codigo': dia_codigo,
                        'hora_inicio': f"{hora_inicio}:00",
                        'hora_fin': f"{hora_fin}:00",
                        'bloque_inicio': int(hora_inicio) - 7,
                        'bloque_fin': int(hora_fin) - 7,
                        'salon': salon
                    }
                    horarios.append(horario_info)
        
        return horarios
    
    def _limpiar_salon_universitario(self, salon_texto: str) -> str:
        """Limpia y extrae el nombre del salón universitario."""
        if not salon_texto or salon_texto == 'nan':
            return 'SALON NO ASIGNADO'
        
        # Remover información adicional como URLs de zoom
        salon_limpio = re.sub(r'/\s*zoom\d+.*', '', salon_texto)
        salon_limpio = re.sub(r'\(.*?\)', '', salon_limpio)  # Remover paréntesis
        
        return salon_limpio.strip()
    
    def _procesar_profesores_universitarios(self, profesores_texto: str) -> List[str]:
        """Procesa el texto de profesores universitarios."""
        if not profesores_texto or profesores_texto == 'nan':
            return []
        
        profesores = []
        for linea in profesores_texto.split('\n'):
            profesor = linea.strip()
            if profesor and profesor != 'nan':
                # Limpiar formato del nombre
                profesor = re.sub(r'^[A-Z]\.\s*', '', profesor)  # Remover inicial con punto
                profesores.append(profesor.upper())
        
        return profesores
    
    def _extraer_capacidad_universitaria(self, capacidad_texto: str) -> int:
        """Extrae la capacidad del curso universitario."""
        if not capacidad_texto or capacidad_texto == 'nan':
            return 30
        
        try:
            return int(float(capacidad_texto))
        except:
            return 30
    
    def _determinar_tipo_curso_universitario(self, horarios_texto: str, salones_texto: str) -> str:
        """Determina el tipo de curso basado en horarios y salones."""
        if 'LAB' in salones_texto.upper():
            return 'Práctico'
        elif 'TALLER' in salones_texto.upper():
            return 'Taller'
        else:
            return 'Teórico'
    
    def _extraer_salones_universitarios(self, salones_texto: str) -> List[str]:
        """Extrae la lista de salones universitarios."""
        if not salones_texto or salones_texto == 'nan':
            return ['SALON NO ASIGNADO']
        
        salones = []
        for linea in salones_texto.split('\n'):
            salon = self._limpiar_salon_universitario(linea)
            if salon and salon != 'SALON NO ASIGNADO':
                salones.append(salon)
        
        return salones if salones else ['SALON NO ASIGNADO']
    
    def _crear_matriz_horarios_universitaria(self, cursos: List[Dict]):
        """Crea matriz de horarios para formato universitario."""
        # Matriz 5 días x 14 bloques (7:00 AM - 9:00 PM)
        matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias_orden:
                    dia_idx = dias_orden.index(horario['dia'])
                    
                    # Calcular bloques ocupados
                    bloque_inicio = max(0, horario['bloque_inicio'])
                    bloque_fin = min(14, horario['bloque_fin'])
                    
                    for bloque in range(bloque_inicio, bloque_fin):
                        if 0 <= bloque < 14:
                            matriz_horarios[dia_idx][bloque] = {
                                'id': curso['id'],
                                'nombre': curso['nombre'],
                                'codigo': curso['codigo'],
                                'profesor': curso['profesor'],
                                'tipo': curso['tipo'],
                                'salon': horario['salon']
                            }
        
        return matriz_horarios
    
    def _generar_estadisticas_universitarias(self, cursos: List[Dict]) -> Dict:
        """Genera estadísticas para formato universitario."""
        escuelas = set()
        profesores = set()
        tipos_curso = set()
        cursos_por_escuela = {}
        
        for curso in cursos:
            escuelas.add(curso['escuela'])
            profesores.add(curso['profesor'])
            tipos_curso.add(curso['tipo'])
            
            escuela = curso['escuela']
            cursos_por_escuela[escuela] = cursos_por_escuela.get(escuela, 0) + 1
        
        return {
            'total_cursos': len(cursos),
            'total_escuelas': len(escuelas),
            'total_profesores': len([p for p in profesores if p != 'SIN ASIGNAR']),
            'escuelas': sorted(list(escuelas)),
            'tipos_curso': sorted(list(tipos_curso)),
            'cursos_por_escuela': cursos_por_escuela,
            'cursos_con_profesor': len([c for c in cursos if c['profesor'] != 'SIN ASIGNAR'])
        }
    
    def _mostrar_resumen_universitario(self, datos: Dict):
        """Muestra resumen especializado para formato universitario."""
        print("\n" + "="*60)
        print("RESUMEN DEL PROCESAMIENTO - FORMATO UNIVERSITARIO")
        print("="*60)
        
        stats = datos['estadisticas']
        
        print(f"📚 Total de cursos procesados: {stats['total_cursos']}")
        print(f"🏫 Total de escuelas: {stats['total_escuelas']}")
        print(f"👨‍🏫 Profesores asignados: {stats['cursos_con_profesor']}/{stats['total_cursos']}")
        print(f"📋 Tipos de curso: {', '.join(stats['tipos_curso'])}")
        
        print(f"\n🏫 Distribución por escuela:")
        for escuela, cantidad in stats['cursos_por_escuela'].items():
            print(f"   {escuela}: {cantidad} cursos")
        
        # Mostrar ejemplos de cursos por escuela
        print(f"\n📖 Ejemplos de cursos por escuela:")
        cursos_por_escuela = {}
        for curso in datos['cursos']:
            escuela = curso['escuela']
            if escuela not in cursos_por_escuela:
                cursos_por_escuela[escuela] = []
            cursos_por_escuela[escuela].append(curso)
        
        for escuela, cursos_escuela in cursos_por_escuela.items():
            print(f"\n   🏫 {escuela}:")
            for curso in cursos_escuela[:3]:  # Mostrar solo 3 ejemplos
                horario_info = ""
                if curso['horarios']:
                    h = curso['horarios'][0]
                    horario_info = f" ({h['dia']} {h['hora_inicio']}-{h['hora_fin']})"
                
                print(f"      {curso['codigo']:<12} {curso['nombre'][:30]:<30}{horario_info}")
            
            if len(cursos_escuela) > 3:
                print(f"      ... y {len(cursos_escuela) - 3} cursos más")
    
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
        
        if self.tipo_datos in ['pdf', 'generado', 'excel_universitario']:
            # Datos de PDF, generados o universitarios tienen lista de cursos
            cursos = {}
            for curso in self.datos_cargados['cursos']:
                cursos[curso['id']] = curso
            return cursos
        
        elif self.tipo_datos == 'excel_estandar':
            # Datos de Excel estándar - extraer de la carga horaria
            cursos = {}
            for dia in self.datos_cargados['carga_horaria']:
                for bloque in dia:
                    if bloque and bloque['id'] not in cursos:
                        cursos[bloque['id']] = bloque
            return cursos
        
        return {}
    
    def mostrar_cursos_disponibles(self, filtro_escuela: str = None):
        """
        Muestra los cursos disponibles de forma organizada.
        VERSIÓN MEJORADA con soporte universitario.
        """
        cursos = self.obtener_cursos_disponibles()
        
        if not cursos:
            print("❌ No hay cursos disponibles")
            return
        
        # Filtrar por escuela si se especifica
        if filtro_escuela:
            cursos = {id: curso for id, curso in cursos.items() 
                     if curso.get('escuela', '').upper() == filtro_escuela.upper()}
        
        print(f"\n📚 CURSOS DISPONIBLES ({len(cursos)} total)")
        if filtro_escuela:
            print(f"🔍 Filtrado por escuela: {filtro_escuela}")
        print("="*80)
        
        if self.tipo_datos in ['pdf', 'generado', 'excel_universitario']:
            self._mostrar_cursos_formato_universitario(cursos)
        else:
            self._mostrar_cursos_formato_estandar(cursos)
    
    def _mostrar_cursos_formato_universitario(self, cursos: Dict):
        """Muestra cursos en formato universitario agrupados."""
        # Agrupar por escuela
        por_escuela = {}
        for curso in cursos.values():
            escuela = curso.get('escuela', 'XX')
            if escuela not in por_escuela:
                por_escuela[escuela] = {}
            
            nombre_curso = curso['nombre']
            if nombre_curso not in por_escuela[escuela]:
                por_escuela[escuela][nombre_curso] = []
            por_escuela[escuela][nombre_curso].append(curso)
        
        for escuela, cursos_escuela in sorted(por_escuela.items()):
            print(f"\n🏫 {escuela} ({sum(len(secciones) for secciones in cursos_escuela.values())} cursos):")
            
            for nombre_curso, secciones in cursos_escuela.items():
                # Mostrar curso con todas sus secciones
                secciones_texto = ", ".join([s.get('seccion', 'A') for s in secciones])
                print(f"   📖 {nombre_curso}")
                if len(secciones) > 1:
                    print(f"      Secciones: {secciones_texto}")
                
                # Mostrar algunas secciones de ejemplo
                for seccion in secciones[:3]:  # Máximo 3 secciones por curso
                    horario_info = ""
                    if seccion.get('horarios'):
                        h = seccion['horarios'][0]
                        horario_info = f" ({h['dia']} {h['hora_inicio']}-{h['hora_fin']})"
                    
                    profesor_info = seccion.get('profesor', 'Sin profesor')[:15]
                    if profesor_info == 'SIN ASIGNAR':
                        profesor_info = 'Sin profesor'
                    
                    codigo = seccion.get('codigo', f"ID_{seccion['id']}")
                    print(f"      {seccion['id']:3d}. {codigo:<12} - {profesor_info:<15}{horario_info}")
                
                if len(secciones) > 3:
                    print(f"      ... y {len(secciones) - 3} secciones más")
                print()
    
    def _mostrar_cursos_formato_estandar(self, cursos: Dict):
        """Muestra cursos en formato estándar simple."""
        for i, (id_curso, curso) in enumerate(sorted(cursos.items())):
            if i >= 20:  # Límite para no saturar la pantalla
                print(f"   ... y {len(cursos) - 20} cursos más")
                break
            print(f"   {id_curso:3d}. {curso['nombre'][:40]} - {curso.get('profesor', 'Sin profesor')}")
    
    def seleccionar_cursos_interactivo(self) -> List[int]:
        """
        Selección interactiva mejorada de cursos.
        VERSIÓN AMPLIADA con soporte universitario.
        """
        cursos = self.obtener_cursos_disponibles()
        
        if not cursos:
            print("❌ No hay cursos disponibles para seleccionar")
            return []
        
        self.mostrar_cursos_disponibles()
        
        print(f"\n🎯 SELECCIÓN DE CURSOS")
        if self.config['modo_universitario']:
            print("   (Modo Universitario Activado)")
        print("="*50)
        print("Opciones de selección:")
        print("  • IDs individuales: 1, 5, 10")
        print("  • Rangos: 1-15")
        
        if self.tipo_datos in ['pdf', 'generado', 'excel_universitario']:
            print("  • Por escuela: BF, CF, CM, CQ, CC")
            print("  • Por curso: 'FÍSICA I' (todas las secciones)")
            print("  • 'ver ESCUELA' para mostrar solo una escuela")
        
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
                if self.config['modo_universitario']:
                    seleccionados = self._seleccion_automatica_universitaria(cursos)
                else:
                    seleccionados = self._seleccion_automatica_estandar(cursos)
                print(f"✅ Selección automática: {len(seleccionados)} cursos recomendados")
                break
            elif entrada.lower().startswith('ver '):
                escuela = entrada[4:].strip().upper()
                self.mostrar_cursos_disponibles(filtro_escuela=escuela)
                continue
            elif self._es_nombre_curso(entrada, cursos):
                # Seleccionar todas las secciones de un curso
                añadidos = self._seleccionar_por_nombre_curso(entrada, cursos, seleccionados)
                print(f"✅ Añadidas {añadidos} secciones de '{entrada}'")
            elif '-' in entrada and entrada.replace('-', '').replace(' ', '').isdigit():
                # Rango
                añadidos = self._seleccionar_por_rango(entrada, cursos, seleccionados)
                print(f"✅ Añadidos {añadidos} cursos del rango")
            elif entrada.isdigit():
                # ID individual
                id_curso = int(entrada)
                if id_curso in cursos:
                    if id_curso not in seleccionados:
                        seleccionados.append(id_curso)
                        curso = cursos[id_curso]
                        print(f"✅ Añadido: {curso.get('codigo', f'ID_{id_curso}')} - {curso['nombre'][:30]}")
                    else:
                        print("⚠️  Curso ya seleccionado")
                else:
                    print("❌ ID de curso no válido")
            elif len(entrada) == 2 and entrada.isalpha() and self.tipo_datos in ['pdf', 'generado', 'excel_universitario']:
                # Escuela completa
                entrada = entrada.upper()
                añadidos = self._seleccionar_por_escuela(entrada, cursos, seleccionados)
                if añadidos > 0:
                    print(f"✅ Añadidos {añadidos} cursos de la escuela {entrada}")
                else:
                    print(f"❌ No se encontraron cursos para la escuela {entrada}")
            else:
                print("❌ Formato no reconocido")
        
        return sorted(seleccionados)
    
    def _es_nombre_curso(self, entrada: str, cursos: Dict) -> bool:
        """Verifica si la entrada coincide con el nombre de algún curso."""
        entrada_upper = entrada.upper()
        for curso in cursos.values():
            if entrada_upper in curso['nombre'].upper():
                return True
        return False
    
    def _seleccionar_por_nombre_curso(self, nombre: str, cursos: Dict, seleccionados: List) -> int:
        """Selecciona todas las secciones de un curso por nombre."""
        añadidos = 0
        nombre_upper = nombre.upper()
        
        for curso in cursos.values():
            if (nombre_upper in curso['nombre'].upper() and 
                curso['id'] not in seleccionados):
                seleccionados.append(curso['id'])
                añadidos += 1
        
        return añadidos
    
    def _seleccionar_por_rango(self, rango: str, cursos: Dict, seleccionados: List) -> int:
        """Selecciona cursos por rango de IDs."""
        try:
            inicio, fin = map(int, rango.split('-'))
            añadidos = 0
            for id_curso in range(inicio, fin + 1):
                if id_curso in cursos and id_curso not in seleccionados:
                    seleccionados.append(id_curso)
                    añadidos += 1
            return añadidos
        except ValueError:
            return 0
    
    def _seleccionar_por_escuela(self, escuela: str, cursos: Dict, seleccionados: List) -> int:
        """Selecciona todos los cursos de una escuela."""
        añadidos = 0
        for curso in cursos.values():
            if (curso.get('escuela', '').upper() == escuela and 
                curso['id'] not in seleccionados):
                seleccionados.append(curso['id'])
                añadidos += 1
        return añadidos
    
    def _seleccion_automatica_universitaria(self, cursos: Dict) -> List[int]:
        """Selección automática inteligente para formato universitario."""
        seleccionados = []
        
        # Agrupar por escuela y curso
        por_escuela = {}
        for curso in cursos.values():
            escuela = curso.get('escuela', 'XX')
            if escuela not in por_escuela:
                por_escuela[escuela] = {}
            
            nombre_curso = curso['nombre']
            if nombre_curso not in por_escuela[escuela]:
                por_escuela[escuela][nombre_curso] = []
            por_escuela[escuela][nombre_curso].append(curso)
        
        # Seleccionar de manera inteligente
        for escuela, cursos_escuela in por_escuela.items():
            cursos_seleccionados_escuela = 0
            
            for nombre_curso, secciones in cursos_escuela.items():
                if cursos_seleccionados_escuela >= 3:  # Máximo 3 cursos por escuela
                    break
                
                # Seleccionar la mejor sección de cada curso
                if secciones:
                    mejor_seccion = self._elegir_mejor_seccion(secciones)
                    seleccionados.append(mejor_seccion['id'])
                    cursos_seleccionados_escuela += 1
        
        return seleccionados
    
    def _elegir_mejor_seccion(self, secciones: List[Dict]) -> Dict:
        """Elige la mejor sección de un curso basado en criterios."""
        # Preferir secciones con profesor asignado
        con_profesor = [s for s in secciones if s.get('profesor', 'SIN ASIGNAR') != 'SIN ASIGNAR']
        if con_profesor:
            return con_profesor[0]
        
        # Si no hay con profesor, tomar la primera
        return secciones[0]
    
    def _seleccion_automatica_estandar(self, cursos: Dict) -> List[int]:
        """Selección automática para formato estándar."""
        # Para Excel estándar, seleccionar los primeros 15 cursos
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
        if self.config['modo_universitario']:
            print("   Modo Universitario - Algoritmo Especializado")
        print("="*55)
        print(f"Cursos seleccionados: {len(cursos_seleccionados)}")
        print(f"Algoritmo: Programación Genética con detección de conflictos")
        
        # Mostrar resumen de selección si es universitario
        if self.config['modo_universitario']:
            self._mostrar_resumen_seleccion_universitaria(cursos_seleccionados)
        
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
    
    def _mostrar_resumen_seleccion_universitaria(self, cursos_seleccionados: List[int]):
        """Muestra resumen de cursos seleccionados en formato universitario."""
        cursos = self.obtener_cursos_disponibles()
        
        print(f"\n📋 Resumen de selección:")
        por_escuela = {}
        
        for id_curso in cursos_seleccionados:
            if id_curso in cursos:
                curso = cursos[id_curso]
                escuela = curso.get('escuela', 'XX')
                
                if escuela not in por_escuela:
                    por_escuela[escuela] = []
                por_escuela[escuela].append(curso)
        
        for escuela, cursos_escuela in por_escuela.items():
            print(f"   🏫 {escuela}: {len(cursos_escuela)} cursos")
            for curso in cursos_escuela[:3]:  # Mostrar primeros 3
                codigo = curso.get('codigo', f"ID_{curso['id']}")
                print(f"      {codigo:<12} {curso['nombre'][:25]}")
            if len(cursos_escuela) > 3:
                print(f"      ... y {len(cursos_escuela) - 3} más")
    
    def analizar_resultados(self, horario_optimizado, conflictos_finales):
        """
        Analiza y muestra los resultados de la optimización.
        VERSIÓN MEJORADA con análisis universitario.
        
        Args:
            horario_optimizado: Matriz del horario optimizado
            conflictos_finales: Conflictos detectados en el resultado
        """
        if horario_optimizado is None:
            return
        
        if self.config['modo_universitario']:
            print(f"\n📊 ANÁLISIS DE RESULTADOS UNIVERSITARIOS")
        else:
            print(f"\n📊 ANÁLISIS DE RESULTADOS")
        print("="*55)
        
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
        
        # Análisis específico universitario
        if self.config['modo_universitario']:
            self._analizar_resultados_universitarios_especifico(horario_optimizado)
        
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
    
    def _analizar_resultados_universitarios_especifico(self, horario_optimizado):
        """Análisis específico para resultados universitarios."""
        # Contar cursos únicos asignados
        cursos_unicos = set()
        distribución_escuelas = {}
        
        for dia in horario_optimizado:
            for bloque in dia:
                if bloque is not None:
                    cursos_unicos.add(bloque.get('id', 0))
                    
                    # Extraer escuela del código
                    codigo = bloque.get('codigo', '')
                    escuela = codigo[:2] if len(codigo) >= 2 else 'XX'
                    
                    if escuela not in distribución_escuelas:
                        distribución_escuelas[escuela] = {'cursos': set(), 'bloques': 0}
                    
                    distribución_escuelas[escuela]['cursos'].add(bloque.get('id', 0))
                    distribución_escuelas[escuela]['bloques'] += 1
        
        print(f"🎓 Métricas universitarias específicas:")
        print(f"   • Cursos únicos asignados: {len(cursos_unicos)}")
        print(f"   • Escuelas representadas: {len(distribución_escuelas)}")
        
        print(f"\n🏫 Distribución por escuela:")
        for escuela, info in distribución_escuelas.items():
            cursos_count = len(info['cursos'])
            bloques_count = info['bloques']
            print(f"   {escuela}: {cursos_count} cursos, {bloques_count} bloques horarios")
    
    def _guardar_reporte_automatico(self, horario, conflictos):
        """Guarda automáticamente reportes de la optimización."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Crear directorio si no existe
            os.makedirs("datos/resultados", exist_ok=True)
            
            # Guardar reporte de conflictos
            archivo_conflictos = f"datos/resultados/reporte_conflictos_{timestamp}.txt"
            guardar_reporte_conflictos(conflictos, archivo_conflictos)
            
            # Guardar horario
            if self.config['modo_universitario']:
                archivo_horario = f"datos/resultados/horario_universitario_{timestamp}.xlsx"
            else:
                archivo_horario = f"datos/resultados/horario_optimizado_{timestamp}.xlsx"
            
            self.guardar_horario_excel(horario, archivo_horario)
            
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
            if self.config['modo_universitario']:
                print("7. Mostrar estadísticas universitarias")
                print("8. Continuar")
            else:
                print("7. Continuar")
            
            max_opcion = 8 if self.config['modo_universitario'] else 7
            opcion = input(f"\nSeleccione una opción (1-{max_opcion}): ").strip()
            
            if opcion == '1':
                titulo = "HORARIO UNIVERSITARIO OPTIMIZADO" if self.config['modo_universitario'] else "HORARIO OPTIMIZADO"
                mostrar_horario_tabla(horario_optimizado, titulo)
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
                    if self.config['modo_universitario']:
                        nombre_archivo = "horario_universitario_optimizado"
                    else:
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
            elif opcion == '7' and self.config['modo_universitario']:
                self._mostrar_estadisticas_universitarias_detalladas(horario_optimizado)
            elif opcion == str(max_opcion) or (opcion == '7' and not self.config['modo_universitario']):
                break
            else:
                print("❌ Opción no válida")
    
    def _mostrar_estadisticas_universitarias_detalladas(self, horario_optimizado):
        """Muestra estadísticas universitarias detalladas."""
        print(f"\n📊 ESTADÍSTICAS UNIVERSITARIAS DETALLADAS")
        print("="*50)
        
        # Análisis por profesor
        profesores_carga = {}
        for dia in horario_optimizado:
            for bloque in dia:
                if bloque is not None:
                    profesor = bloque.get('profesor', 'SIN ASIGNAR')
                    if profesor not in profesores_carga:
                        profesores_carga[profesor] = 0
                    profesores_carga[profesor] += 1
        
        print(f"\n👨‍🏫 Carga por profesor:")
        for profesor, horas in sorted(profesores_carga.items(), key=lambda x: x[1], reverse=True):
            if profesor != 'SIN ASIGNAR':
                print(f"   {profesor[:20]:<20}: {horas:2d} horas")
        
        # Análisis por tipo de curso
        tipos_carga = {}
        for dia in horario_optimizado:
            for bloque in dia:
                if bloque is not None:
                    tipo = bloque.get('tipo', 'Teórico')
                    if tipo not in tipos_carga:
                        tipos_carga[tipo] = 0
                    tipos_carga[tipo] += 1
        
        print(f"\n📚 Distribución por tipo de curso:")
        for tipo, horas in tipos_carga.items():
            print(f"   {tipo:<15}: {horas:2d} bloques")
    
    def guardar_horario_excel(self, horario, nombre_archivo: str = None):
        """
        Guarda el horario optimizado en Excel.
        VERSIÓN MEJORADA con formato universitario.
        
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
                        
                        if self.config['modo_universitario']:
                            # Formato universitario detallado
                            texto = f"{curso.get('codigo', 'N/A')}"
                            texto += f"\n{curso.get('nombre', 'Sin nombre')[:25]}"
                            if curso.get('profesor', 'SIN ASIGNAR') != 'SIN ASIGNAR':
                                texto += f"\nProf: {curso['profesor'][:15]}"
                            if curso.get('salon'):
                                texto += f"\n{curso['salon']}"
                        else:
                            # Formato estándar
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
                if self.config['modo_universitario']:
                    nombre_archivo = f"horario_universitario_{timestamp}.xlsx"
                else:
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
        VERSIÓN INTEGRADA con detección automática de formato.
        
        Args:
            archivo_entrada: Archivo a procesar (opcional)
        """
        print("🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS")
        print("   Con detección automática de formato y resolución de conflictos")
        if self.config['modo_universitario']:
            print("   🎓 MODO UNIVERSITARIO ACTIVADO")
        print("="*75)
        
        try:
            # Paso 1: Cargar datos
            datos_cargados = False
            
            if archivo_entrada:
                datos_cargados = self.detectar_y_cargar_archivo(archivo_entrada)
                
                # Si se detectó formato universitario, activar modo
                if self.formato_detectado == 'excel_universitario':
                    self.activar_modo_universitario()
            
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
                    titulo = "HORARIO UNIVERSITARIO OPTIMIZADO" if self.config['modo_universitario'] else "HORARIO OPTIMIZADO"
                    mostrar_horario_tabla(horario_optimizado, titulo)
                
                # Ofrecer opciones adicionales
                self.ofrecer_opciones_post_optimizacion(horario_optimizado)
                
                mensaje_final = "🎓 ¡Optimización universitaria completada!" if self.config['modo_universitario'] else "✅ ¡Optimización completada exitosamente!"
                print(f"\n{mensaje_final}")
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
        """
        Obtiene estadísticas del sistema y datos cargados.
        VERSIÓN AMPLIADA con información universitaria.
        """
        stats = {
            'tipo_datos': self.tipo_datos,
            'formato_detectado': self.formato_detectado,
            'modo_universitario': self.config['modo_universitario'],
            'cursos_disponibles': len(self.obtener_cursos_disponibles()),
            'optimizador_inicializado': self.optimizador is not None,
            'ultimo_horario_disponible': self.ultimo_horario_optimizado is not None
        }
        
        if self.datos_cargados:
            if 'cursos' in self.datos_cargados:
                stats['total_cursos_sistema'] = len(self.datos_cargados['cursos'])
            if 'conflictos_iniciales' in self.datos_cargados:
                stats['conflictos_iniciales'] = len(self.datos_cargados['conflictos_iniciales'])
            
            # Estadísticas específicas universitarias
            if self.config['modo_universitario'] and 'estadisticas' in self.datos_cargados:
                stats_univ = self.datos_cargados['estadisticas']
                stats.update({
                    'escuelas_detectadas': stats_univ.get('total_escuelas', 0),
                    'profesores_asignados': stats_univ.get('cursos_con_profesor', 0),
                    'distribución_escuelas': stats_univ.get('cursos_por_escuela', {})
                })
        
        if self.optimizador and hasattr(self.optimizador, 'historia_fitness'):
            stats['generaciones_ejecutadas'] = len(self.optimizador.historia_fitness)
            stats['mejor_fitness'] = min(self.optimizador.historia_fitness) if self.optimizador.historia_fitness else None
        
        return stats
    
    def test_lector_solo(self, archivo: str) -> bool:
        """
        Modo de prueba solo para el lector (sin optimización).
        NUEVA FUNCIONALIDAD para testing.
        """
        print("🧪 MODO PRUEBA - SOLO LECTOR")
        print("="*40)
        
        try:
            # Detectar formato
            formato = self.detectar_formato_archivo(archivo)
            print(f"🔍 Formato detectado: {formato}")
            
            # Cargar según formato
            if self.detectar_y_cargar_archivo(archivo):
                print("✅ Archivo cargado exitosamente")
                
                # Mostrar estadísticas detalladas
                stats = self.obtener_estadisticas_sistema()
                
                print(f"\n📊 ESTADÍSTICAS DE PROCESAMIENTO:")
                print("-"*40)
                for key, value in stats.items():
                    if key != 'distribución_escuelas':  # Mostrar esto por separado
                        print(f"   {key}: {value}")
                
                if 'distribución_escuelas' in stats and stats['distribución_escuelas']:
                    print(f"\n🏫 Distribución por escuela:")
                    for escuela, cantidad in stats['distribución_escuelas'].items():
                        print(f"   {escuela}: {cantidad} cursos")
                
                # Mostrar algunos ejemplos de cursos
                cursos = self.obtener_cursos_disponibles()
                print(f"\n📚 EJEMPLOS DE CURSOS PROCESADOS:")
                print("-"*40)
                
                ejemplos_mostrados = 0
                for curso in cursos.values():
                    if ejemplos_mostrados >= 5:
                        break
                    
                    print(f"\n🔍 Curso {curso['id']}: {curso.get('codigo', 'Sin código')}")
                    print(f"   Nombre: {curso['nombre']}")
                    if 'escuela' in curso:
                        print(f"   Escuela: {curso['escuela']}")
                    print(f"   Profesor: {curso.get('profesor', 'Sin asignar')}")
                    print(f"   Tipo: {curso.get('tipo', 'Teórico')}")
                    
                    if curso.get('horarios'):
                        print(f"   Horarios:")
                        for h in curso['horarios'][:2]:  # Máximo 2 horarios por curso
                            print(f"     • {h['dia']} {h['hora_inicio']}-{h['hora_fin']} en {h.get('salon', 'Sin salón')}")
                        if len(curso['horarios']) > 2:
                            print(f"     ... y {len(curso['horarios']) - 2} horarios más")
                    
                    ejemplos_mostrados += 1
                
                if len(cursos) > 5:
                    print(f"\n   ... y {len(cursos) - 5} cursos más")
                
                print(f"\n✅ Prueba del lector completada exitosamente!")
                print(f"💡 Para optimizar horarios, ejecute sin modo de prueba")
                
                return True
            else:
                print("❌ Error al cargar el archivo")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba del lector: {e}")
            import traceback
            traceback.print_exc()
            return False


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
    if '--universitario' in sys.argv:
        sistema.activar_modo_universitario()
    elif '--debug' in sys.argv:
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
    elif '--test-lector' in sys.argv:
        if archivo:
            sistema.test_lector_solo(archivo)
        else:
            print("❌ Se requiere archivo para modo de prueba")
        return
    
    sistema.ejecutar(archivo)


def mostrar_ayuda():
    """Muestra la ayuda del sistema integrado."""
    print("""
🎓 SISTEMA DE OPTIMIZACIÓN DE HORARIOS ACADÉMICOS - VERSIÓN INTEGRADA
=====================================================================

DESCRIPCIÓN:
    Sistema completo con detección automática de formato y soporte
    especializado para archivos universitarios y estándar.

USO:
    python interfaces/sistema_completo.py [archivo] [opciones]

ARCHIVOS SOPORTADOS:
    📄 PDF: Horarios académicos en formato tabular
    📊 Excel Universitario: Formato con escuelas, secciones múltiples
    📊 Excel Estándar: Matriz de horarios (formato original)
    🔧 Sin archivo: Genera datos de prueba automáticamente

OPCIONES:
    --universitario   Forzar modo universitario especializado
    --test-lector     Solo probar lectura sin optimización
    --debug          Modo detallado con todos los análisis
    --rapido         Modo rápido sin visualizaciones extra
    --help, -h       Muestra esta ayuda

EJEMPLOS:
    # Detección automática y optimización completa
    python interfaces/sistema_completo.py datos/Horarios_2023_1.xlsx
    
    # Modo universitario forzado
    python interfaces/sistema_completo.py archivo.xlsx --universitario
    
    # Solo probar lectura de datos
    python interfaces/sistema_completo.py archivo.xlsx --test-lector
    
    # Generar datos de prueba y optimizar
    python interfaces/sistema_completo.py

DETECCIÓN AUTOMÁTICA:
    El sistema detecta automáticamente:
    ✅ Formato PDF vs Excel
    ✅ Excel universitario vs estándar
    ✅ Estructura de escuelas y secciones
    ✅ Códigos universitarios (BFI01, CM201, etc.)
    ✅ Horarios en formato "LU 10-12, MI 14-16"

MODO UNIVERSITARIO:
    Características especiales:
    📚 Reconoce cursos con múltiples secciones
    🏫 Agrupa por escuela profesional
    👨‍🏫 Extrae profesores y salones
    🎯 Selección por nombre de curso completo
    📊 Estadísticas específicas universitarias

SELECCIÓN DE CURSOS:
    • IDs individuales: 1, 5, 10
    • Rangos: 1-20 (cursos del 1 al 20)
    • Por escuela: BF (todos los cursos de Física)
    • Por nombre: "FÍSICA I" (todas las secciones)
    • 'ver ESCUELA' para filtrar visualización
    • 'todos' para seleccionar todos los cursos
    • 'auto' para selección automática inteligente

CARACTERÍSTICAS PRINCIPALES:
    ✅ Detección automática de formato universitario
    ✅ Reconocimiento de cursos con múltiples secciones  
    ✅ Extracción inteligente de horarios y profesores
    ✅ Algoritmo genético mejorado para optimización
    ✅ Resolución automática de conflictos de horarios
    ✅ Visualización especializada por formato
    ✅ Exportación en formato Excel profesional

¿NECESITA MÁS AYUDA?
    Ejecute sin argumentos para modo interactivo o consulte
    la documentación en docs/manual_usuario.md
""")


# Configuración para importación como módulo
__all__ = [
    'SistemaOptimizacionCompleto',
    'main',
    'mostrar_ayuda'
]

if __name__ == "__main__":
    main()