#!/usr/bin/env python3
"""
Lector directo para archivos Excel de horarios UNMSM.
Procesa archivos como Horarios_2023_1.xlsx y los convierte al formato
requerido por el sistema de optimización genética.

AGREGAR COMO: core/lector_excel_horarios.py
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional


class LectorExcelHorarios:
    def __init__(self):
        self.dias_semana = {
            'LU': 'Lunes',
            'MA': 'Martes', 
            'MI': 'Miércoles',
            'JU': 'Jueves',
            'VI': 'Viernes',
            'SA': 'Sábado',
            'DO': 'Domingo'
        }
        
        self.cursos_procesados = {}
        self.matriz_horarios = None
        
    def leer_excel(self, archivo_excel: str) -> Dict:
        """
        Lee un archivo Excel de horarios y lo convierte al formato del optimizador.
        
        Args:
            archivo_excel: Ruta al archivo Excel con horarios
            
        Returns:
            Dict con cursos, matriz de horarios y estadísticas
        """
        try:
            print(f"📊 Leyendo archivo Excel: {archivo_excel}")
            
            # Leer el archivo Excel
            df = pd.read_excel(archivo_excel)
            
            print(f"   Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Procesar los datos del Excel
            cursos = self._procesar_datos_excel(df)
            
            # Crear matriz de horarios
            self.crear_matriz_horarios(cursos)
            
            return {
                'cursos': cursos,
                'matriz_horarios': self.matriz_horarios,
                'estadisticas': self.generar_estadisticas(cursos)
            }
            
        except Exception as e:
            raise Exception(f"Error al leer el archivo Excel: {str(e)}")
    
    def _procesar_datos_excel(self, df: pd.DataFrame) -> List[Dict]:
        """Procesa los datos del DataFrame de Excel."""
        cursos = []
        
        print("🔄 Procesando datos del Excel...")
        
        # Analizar la estructura del DataFrame
        print(f"   Columnas: {list(df.columns)}")
        print(f"   Primeras filas:")
        for i in range(min(5, len(df))):
            print(f"     {i}: {list(df.iloc[i].values)}")
        
        # Detectar el formato del Excel
        if self._es_formato_tabla_horarios(df):
            cursos = self._procesar_formato_tabla(df)
        elif self._es_formato_lista_cursos(df):
            cursos = self._procesar_formato_lista(df)
        else:
            # Intentar auto-detección
            cursos = self._procesar_formato_automatico(df)
        
        print(f"✅ Procesados {len(cursos)} cursos del Excel")
        return cursos
    
    def _es_formato_tabla_horarios(self, df: pd.DataFrame) -> bool:
        """Detecta si el Excel está en formato de tabla de horarios por días."""
        columnas = [str(col).upper() for col in df.columns]
        dias_en_columnas = sum(1 for dia in ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES'] 
                              if any(dia in col for col in columnas))
        return dias_en_columnas >= 3
    
    def _es_formato_lista_cursos(self, df: pd.DataFrame) -> bool:
        """Detecta si el Excel está en formato de lista de cursos."""
        columnas = [str(col).upper() for col in df.columns]
        campos_curso = ['CODIGO', 'NOMBRE', 'PROFESOR', 'HORARIO', 'SALON', 'SECCION']
        campos_encontrados = sum(1 for campo in campos_curso 
                                if any(campo in col for col in columnas))
        return campos_encontrados >= 3
    
    def _procesar_formato_tabla(self, df: pd.DataFrame) -> List[Dict]:
        """Procesa Excel en formato de tabla (días como columnas)."""
        print("   📅 Formato detectado: Tabla de horarios por días")
        
        cursos = []
        id_contador = 1
        
        # Identificar columnas de días
        dias_columnas = self._identificar_columnas_dias(df)
        
        # Procesar cada fila como un bloque de tiempo
        for idx, fila in df.iterrows():
            hora_inicio, hora_fin = self._extraer_horas_fila(fila, idx)
            
            for dia, col_name in dias_columnas.items():
                if col_name in df.columns:
                    celda = fila[col_name]
                    
                    if pd.notna(celda) and str(celda).strip():
                        curso_info = self._parsear_celda_horario(
                            str(celda), dia, hora_inicio, hora_fin, id_contador
                        )
                        
                        if curso_info:
                            cursos.append(curso_info)
                            id_contador += 1
        
        return cursos
    
    def _procesar_formato_lista(self, df: pd.DataFrame) -> List[Dict]:
        """Procesa Excel en formato de lista de cursos."""
        print("   📋 Formato detectado: Lista de cursos")
        
        cursos = []
        
        # Identificar columnas importantes
        mapa_columnas = self._identificar_columnas_lista(df)
        
        for idx, fila in df.iterrows():
            curso_info = self._extraer_curso_de_fila(fila, mapa_columnas, idx + 1)
            if curso_info:
                cursos.append(curso_info)
        
        return cursos
    
    def _procesar_formato_automatico(self, df: pd.DataFrame) -> List[Dict]:
        """Procesamiento automático cuando no se detecta el formato."""
        print("   🔍 Formato no reconocido, intentando procesamiento automático...")
        
        cursos = []
        id_contador = 1
        
        # Buscar cualquier celda que contenga información de curso
        for idx, fila in df.iterrows():
            for col_name in df.columns:
                celda = fila[col_name]
                
                if pd.notna(celda) and str(celda).strip():
                    curso_info = self._intentar_extraer_curso(str(celda), id_contador)
                    
                    if curso_info:
                        cursos.append(curso_info)
                        id_contador += 1
        
        return cursos
    
    def _identificar_columnas_dias(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identifica qué columnas corresponden a cada día."""
        dias_mapa = {}
        
        for col in df.columns:
            col_str = str(col).upper()
            if 'LUN' in col_str or 'MONDAY' in col_str:
                dias_mapa['Lunes'] = col
            elif 'MAR' in col_str or 'TUESDAY' in col_str:
                dias_mapa['Martes'] = col
            elif 'MIE' in col_str or 'MIÉ' in col_str or 'WEDNESDAY' in col_str:
                dias_mapa['Miércoles'] = col
            elif 'JUE' in col_str or 'THURSDAY' in col_str:
                dias_mapa['Jueves'] = col
            elif 'VIE' in col_str or 'FRIDAY' in col_str:
                dias_mapa['Viernes'] = col
            elif 'SAB' in col_str or 'SATURDAY' in col_str:
                dias_mapa['Sábado'] = col
        
        return dias_mapa
    
    def _identificar_columnas_lista(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identifica columnas en formato de lista."""
        mapa = {}
        
        for col in df.columns:
            col_str = str(col).upper()
            if 'CODIGO' in col_str or 'CODE' in col_str:
                mapa['codigo'] = col
            elif 'NOMBRE' in col_str or 'NAME' in col_str or 'CURSO' in col_str:
                mapa['nombre'] = col
            elif 'PROFESOR' in col_str or 'TEACHER' in col_str or 'DOCENTE' in col_str:
                mapa['profesor'] = col
            elif 'HORARIO' in col_str or 'SCHEDULE' in col_str or 'HORA' in col_str:
                mapa['horario'] = col
            elif 'SALON' in col_str or 'AULA' in col_str or 'ROOM' in col_str:
                mapa['salon'] = col
            elif 'SECCION' in col_str or 'SECTION' in col_str:
                mapa['seccion'] = col
            elif 'CAPACIDAD' in col_str or 'CAPACITY' in col_str:
                mapa['capacidad'] = col
        
        return mapa
    
    def _extraer_horas_fila(self, fila, idx: int) -> Tuple[str, str]:
        """Extrae las horas de inicio y fin de una fila."""
        # Buscar en el índice o primera columna
        primera_col = str(fila.iloc[0]) if len(fila) > 0 else str(idx)
        
        # Buscar patrón de hora
        match = re.search(r'(\d{1,2}):?(\d{0,2})\s*[-–]\s*(\d{1,2}):?(\d{0,2})', primera_col)
        if match:
            hora_inicio = f"{match.group(1).zfill(2)}:{match.group(2).zfill(2) if match.group(2) else '00'}"
            hora_fin = f"{match.group(3).zfill(2)}:{match.group(4).zfill(2) if match.group(4) else '00'}"
            return hora_inicio, hora_fin
        
        # Valores por defecto basados en el índice
        hora_base = 7 + idx
        return f"{hora_base:02d}:00", f"{hora_base + 1:02d}:00"
    
    def _parsear_celda_horario(self, celda: str, dia: str, hora_inicio: str, 
                              hora_fin: str, id_curso: int) -> Optional[Dict]:
        """Parsea una celda que contiene información de horario."""
        
        # Limpiar la celda
        celda = celda.strip()
        
        # Intentar extraer información usando diferentes patrones
        
        # Patrón 1: "ID|NOMBRE|PROFESOR|TIPO"
        if '|' in celda:
            partes = celda.split('|')
            if len(partes) >= 3:
                return {
                    'id': int(partes[0]) if partes[0].isdigit() else id_curso,
                    'codigo': f"CURSO_{partes[0]}" if partes[0].isdigit() else partes[0],
                    'codigo_base': partes[0][:6] if len(partes[0]) > 6 else partes[0],
                    'nombre': partes[1] if len(partes) > 1 else 'Sin nombre',
                    'seccion': 'A',
                    'horarios': [{
                        'dia': dia,
                        'dia_corto': dia[:2].upper(),
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'salon': 'SIN ASIGNAR',
                        'profesor': partes[2] if len(partes) > 2 else 'SIN ASIGNAR',
                        'bloque_idx': self._hora_a_bloque(hora_inicio)
                    }],
                    'profesor': partes[2] if len(partes) > 2 else 'SIN ASIGNAR',
                    'capacidad': 30,
                    'tipo': partes[3] if len(partes) > 3 else 'Teórico',
                    'escuela': partes[0][:2] if len(partes[0]) >= 2 else 'XX'
                }
        
        # Patrón 2: Texto libre con código/nombre
        codigo_match = re.search(r'([A-Z]{2,4}\d{1,3}[A-Z]?\d?)', celda)
        if codigo_match:
            codigo = codigo_match.group(1)
            nombre_resto = celda.replace(codigo, '').strip()
            
            return {
                'id': id_curso,
                'codigo': codigo + '_A',
                'codigo_base': codigo,
                'nombre': nombre_resto or self._generar_nombre_desde_codigo(codigo),
                'seccion': 'A',
                'horarios': [{
                    'dia': dia,
                    'dia_corto': dia[:2].upper(),
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'salon': 'SIN ASIGNAR',
                    'profesor': 'SIN ASIGNAR',
                    'bloque_idx': self._hora_a_bloque(hora_inicio)
                }],
                'profesor': 'SIN ASIGNAR',
                'capacidad': 30,
                'tipo': 'Teórico',
                'escuela': codigo[:2]
            }
        
        # Patrón 3: Solo texto (crear curso genérico)
        if len(celda) > 3:
            return {
                'id': id_curso,
                'codigo': f'CURSO_{id_curso}_A',
                'codigo_base': f'CURSO_{id_curso}',
                'nombre': celda[:50],  # Limitar longitud
                'seccion': 'A',
                'horarios': [{
                    'dia': dia,
                    'dia_corto': dia[:2].upper(),
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'salon': 'SIN ASIGNAR',
                    'profesor': 'SIN ASIGNAR',
                    'bloque_idx': self._hora_a_bloque(hora_inicio)
                }],
                'profesor': 'SIN ASIGNAR',
                'capacidad': 30,
                'tipo': 'Teórico',
                'escuela': 'XX'
            }
        
        return None
    
    def _extraer_curso_de_fila(self, fila, mapa_columnas: Dict[str, str], id_curso: int) -> Optional[Dict]:
        """Extrae información de curso de una fila en formato lista."""
        
        curso_info = {
            'id': id_curso,
            'codigo': f'CURSO_{id_curso}_A',
            'codigo_base': f'CURSO_{id_curso}',
            'nombre': 'Sin nombre',
            'seccion': 'A',
            'horarios': [],
            'profesor': 'SIN ASIGNAR',
            'capacidad': 30,
            'tipo': 'Teórico',
            'escuela': 'XX'
        }
        
        # Extraer información según las columnas disponibles
        for campo, col_name in mapa_columnas.items():
            if col_name in fila.index and pd.notna(fila[col_name]):
                valor = str(fila[col_name]).strip()
                
                if campo == 'codigo':
                    curso_info['codigo'] = valor + '_A' if not valor.endswith('_A') else valor
                    curso_info['codigo_base'] = valor.split('_')[0]
                    curso_info['escuela'] = valor[:2] if len(valor) >= 2 else 'XX'
                elif campo == 'nombre':
                    curso_info['nombre'] = valor
                elif campo == 'profesor':
                    curso_info['profesor'] = valor
                elif campo == 'capacidad':
                    try:
                        curso_info['capacidad'] = int(valor)
                    except:
                        curso_info['capacidad'] = 30
                elif campo == 'horario':
                    # Parsear horario
                    horarios = self._parsear_horario_texto(valor)
                    curso_info['horarios'] = horarios
        
        # Si no se encontraron horarios, crear uno por defecto
        if not curso_info['horarios']:
            curso_info['horarios'] = [{
                'dia': 'Lunes',
                'dia_corto': 'LU',
                'hora_inicio': '08:00',
                'hora_fin': '10:00',
                'salon': 'SIN ASIGNAR',
                'profesor': curso_info['profesor'],
                'bloque_idx': 1
            }]
        
        return curso_info
    
    def _parsear_horario_texto(self, texto_horario: str) -> List[Dict]:
        """Parsea texto de horario en formato libre."""
        horarios = []
        
        # Buscar patrones de día y hora
        patron = r'([A-Z]{2})\s+(\d{1,2}):?(\d{0,2})\s*[-–]\s*(\d{1,2}):?(\d{0,2})'
        matches = re.finditer(patron, texto_horario.upper())
        
        for match in matches:
            dia_corto = match.group(1)
            hora_inicio = f"{match.group(2).zfill(2)}:{match.group(3).zfill(2) if match.group(3) else '00'}"
            hora_fin = f"{match.group(4).zfill(2)}:{match.group(5).zfill(2) if match.group(5) else '00'}"
            
            horarios.append({
                'dia': self.dias_semana.get(dia_corto, dia_corto),
                'dia_corto': dia_corto,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'salon': 'SIN ASIGNAR',
                'profesor': 'SIN ASIGNAR',
                'bloque_idx': self._hora_a_bloque(hora_inicio)
            })
        
        return horarios
    
    def _intentar_extraer_curso(self, celda: str, id_curso: int) -> Optional[Dict]:
        """Intenta extraer información de curso de una celda cualquiera."""
        
        # Solo procesar celdas con contenido sustancial
        if len(celda.strip()) < 3:
            return None
        
        # Si contiene horarios, intentar procesarla
        if re.search(r'[A-Z]{2}\s+\d{1,2}[-:]\d{1,2}', celda):
            return self._parsear_celda_horario(celda, 'Lunes', '08:00', '10:00', id_curso)
        
        # Si parece un código de curso
        if re.match(r'^[A-Z]{2,4}\d{1,3}', celda.strip()):
            return {
                'id': id_curso,
                'codigo': celda.strip() + '_A',
                'codigo_base': celda.strip(),
                'nombre': self._generar_nombre_desde_codigo(celda.strip()),
                'seccion': 'A',
                'horarios': [{
                    'dia': 'Lunes',
                    'dia_corto': 'LU',
                    'hora_inicio': '08:00',
                    'hora_fin': '10:00',
                    'salon': 'SIN ASIGNAR',
                    'profesor': 'SIN ASIGNAR',
                    'bloque_idx': 1
                }],
                'profesor': 'SIN ASIGNAR',
                'capacidad': 30,
                'tipo': 'Teórico',
                'escuela': celda.strip()[:2]
            }
        
        return None
    
    def _generar_nombre_desde_codigo(self, codigo: str) -> str:
        """Genera nombre de curso desde código."""
        mapeo_nombres = {
            'BFI01': 'FÍSICA I',
            'CF1B2': 'FÍSICA II', 
            'CF2B1': 'FÍSICA III',
            'BMA01': 'CÁLCULO DIFERENCIAL',
            'BMA02': 'CÁLCULO INTEGRAL',
            'BMA03': 'ÁLGEBRA LINEAL',
            'BQU01': 'QUÍMICA I',
            'BIC01': 'INTRODUCCIÓN A LA COMPUTACIÓN',
            'CC112': 'FUNDAMENTOS DE PROGRAMACIÓN'
        }
        
        if codigo in mapeo_nombres:
            return mapeo_nombres[codigo]
        
        # Generar basado en prefijo
        prefijo = codigo[:2] if len(codigo) >= 2 else codigo
        if prefijo in ['BF', 'CF']:
            return 'FÍSICA'
        elif prefijo in ['BM', 'CM']:
            return 'MATEMÁTICA'
        elif prefijo in ['BQ', 'CQ']:
            return 'QUÍMICA'
        elif prefijo in ['BI', 'CC']:
            return 'COMPUTACIÓN'
        else:
            return f'CURSO {codigo}'
    
    def _hora_a_bloque(self, hora_str: str) -> int:
        """Convierte hora a índice de bloque."""
        try:
            hora = int(hora_str.split(':')[0])
            return max(0, hora - 7)
        except:
            return 0
    
    # Métodos de creación de matriz y estadísticas (reutilizados)
    def crear_matriz_horarios(self, cursos: List[Dict]):
        """Crea la matriz de horarios."""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias:
                    dia_idx = dias.index(horario['dia'])
                    bloque_inicio = horario['bloque_idx']
                    
                    try:
                        inicio = int(horario['hora_inicio'].split(':')[0])
                        fin = int(horario['hora_fin'].split(':')[0])
                        duracion = fin - inicio
                    except:
                        duracion = 1
                    
                    for i in range(duracion):
                        bloque = bloque_inicio + i
                        if 0 <= bloque < 14:
                            self.matriz_horarios[dia_idx][bloque] = {
                                'id': curso['id'],
                                'nombre': curso['nombre'],
                                'profesor': horario.get('profesor', curso['profesor']),
                                'tipo': curso['tipo'],
                                'codigo': curso['codigo'],
                                'salon': horario['salon'],
                                'escuela': curso['escuela']
                            }
    
    def generar_estadisticas(self, cursos: List[Dict]) -> Dict:
        """Genera estadísticas."""
        total_cursos = len(cursos)
        profesores = set()
        escuelas = set()
        tipos = set()
        
        for curso in cursos:
            if curso['profesor'] and curso['profesor'] != 'SIN ASIGNAR':
                profesores.add(curso['profesor'])
            
            for horario in curso.get('horarios', []):
                if horario.get('profesor') and horario['profesor'] != 'SIN ASIGNAR':
                    profesores.add(horario['profesor'])
            
            if curso.get('escuela'):
                escuelas.add(curso['escuela'])
            
            if curso.get('tipo'):
                tipos.add(curso['tipo'])
        
        return {
            'total_cursos': total_cursos,
            'total_profesores': len(profesores),
            'total_escuelas': len(escuelas),
            'profesores': list(profesores),
            'escuelas': list(escuelas),
            'tipos_curso': list(tipos),
            'cursos_con_horario': len([c for c in cursos if c.get('horarios')]),
            'cursos_con_profesor': len([c for c in cursos if c.get('profesor') and c['profesor'] != 'SIN ASIGNAR']),
        }
    
    def exportar_a_excel(self, cursos: List[Dict], archivo_salida: str):
        """Exporta a Excel en formato del optimizador."""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{7+i}:00 - {8+i}:00" for i in range(14)]
        
        df = pd.DataFrame(index=horas, columns=dias)
        
        for dia_idx, dia in enumerate(dias):
            for bloque in range(14):
                if self.matriz_horarios[dia_idx][bloque]:
                    curso = self.matriz_horarios[dia_idx][bloque]
                    celda = f"{curso['id']}|{curso['nombre']}|{curso['profesor']}|{curso['tipo']}"
                    df.iloc[bloque, dia_idx] = celda
        
        df.to_excel(archivo_salida)
        print(f"📊 Archivo Excel convertido: {archivo_salida}")
    
    def mostrar_resumen(self, datos: Dict):
        """Muestra resumen."""
        print("\n" + "="*60)
        print("RESUMEN DE PROCESAMIENTO DEL EXCEL")
        print("="*60)
        
        estadisticas = datos['estadisticas']
        print(f"Total de cursos procesados: {estadisticas['total_cursos']}")
        print(f"Cursos con horarios: {estadisticas['cursos_con_horario']}")
        print(f"Cursos con profesor asignado: {estadisticas['cursos_con_profesor']}")
        print(f"Total de profesores: {estadisticas['total_profesores']}")
        print(f"Total de escuelas: {estadisticas['total_escuelas']}")
        
        print(f"\nEscuelas encontradas: {', '.join(sorted(estadisticas['escuelas']))}")
        print(f"Tipos de curso: {', '.join(estadisticas['tipos_curso'])}")
        
        print(f"\nPrimeros 15 cursos procesados:")
        for i, curso in enumerate(datos['cursos'][:15]):
            horarios_info = ""
            if curso['horarios']:
                h = curso['horarios'][0]
                profesor_h = h.get('profesor', 'N/A')[:10]
                horarios_info = f" ({h['dia_corto']} {h['hora_inicio']}-{h['hora_fin']}, Prof: {profesor_h})"
            
            nombre_corto = curso['nombre'][:25] + "..." if len(curso['nombre']) > 25 else curso['nombre']
            print(f"{i+1:2d}. {curso['codigo']:<12} {nombre_corto:<30}{horarios_info}")
        
        if len(datos['cursos']) > 15:
            print(f"     ... y {len(datos['cursos']) - 15} cursos más")
        
        if self.matriz_horarios:
            bloques_ocupados = sum(1 for dia in self.matriz_horarios for bloque in dia if bloque is not None)
            print(f"\nMatriz de horarios creada: 5 días x 14 bloques")
            print(f"Bloques ocupados: {bloques_ocupados}/70 ({bloques_ocupados/70*100:.1f}%)")


def main():
    """Función principal."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python lector_excel_horarios.py <archivo.xlsx> [archivo_salida.xlsx]")
        return
    
    archivo_excel = sys.argv[1]
    archivo_salida = sys.argv[2] if len(sys.argv) > 2 else "horarios_convertidos.xlsx"
    
    try:
        print(f"🚀 Procesando archivo Excel: {archivo_excel}")
        
        lector = LectorExcelHorarios()
        datos = lector.leer_excel(archivo_excel)
        
        lector.mostrar_resumen(datos)
        lector.exportar_a_excel(datos['cursos'], archivo_salida)
        
        print(f"\n✅ Conversión completada!")
        print(f"📊 Archivo convertido: {archivo_salida}")
        print(f"🎯 Comando para optimizar:")
        print(f"     python scripts/optimizar.py {archivo_salida}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()