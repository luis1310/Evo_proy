#!/usr/bin/env python3
"""
Módulo unificado para leer archivos PDF y Excel con horarios académicos.
VERSIÓN INTEGRADA - Combina lector PDF original + lector Excel universitario.

Este archivo reemplaza a: core/lector_pdf_horarios.py
Integra toda la funcionalidad de lectura en un solo módulo.
"""

import re
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF


class LectorHorarios:
    """
    Lector unificado que maneja PDF y Excel (estándar y universitario).
    Detecta automáticamente el formato y usa el procesador apropiado.
    """
    
    def __init__(self):
        self.lector_pdf = LectorPDFHorarios()
        self.lector_excel = LectorExcelHorarios()
        self.ultimo_formato_detectado = None
    
    def leer_archivo(self, archivo: str) -> Dict:
        """
        Punto de entrada principal. Detecta formato y procesa archivo.
        
        Args:
            archivo: Ruta al archivo a procesar
            
        Returns:
            Dict con datos procesados y metadata
        """
        if not os.path.exists(archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {archivo}")
        
        # Detectar formato
        formato = self.detectar_formato(archivo)
        self.ultimo_formato_detectado = formato
        
        print(f"🔍 Formato detectado: {formato}")
        
        if formato == 'pdf':
            return self.lector_pdf.leer_pdf(archivo)
        elif formato == 'excel_universitario':
            return self.lector_excel.leer_excel_universitario(archivo)
        elif formato == 'excel_estandar':
            return self.leer_excel_estandar(archivo)
        else:
            raise ValueError(f"Formato no soportado: {formato}")
    
    def detectar_formato(self, archivo: str) -> str:
        """
        Detecta el formato del archivo automáticamente.
        
        Returns:
            str: 'pdf', 'excel_universitario', 'excel_estandar'
        """
        extension = os.path.splitext(archivo)[1].lower()
        
        if extension == '.pdf':
            return 'pdf'
        elif extension in ['.xlsx', '.xls']:
            return self._detectar_formato_excel(archivo)
        else:
            raise ValueError(f"Extensión no soportada: {extension}")
    
    def _detectar_formato_excel(self, archivo: str) -> str:
        """Detecta si un Excel es universitario o estándar."""
        try:
            # Leer primeras filas para análisis
            df = pd.read_excel(archivo, header=None, nrows=15)
            
            for i, fila in df.iterrows():
                texto_fila = ' '.join([str(x) for x in fila.values if pd.notna(x)])
                texto_upper = texto_fila.upper()
                
                # Indicadores de formato universitario
                indicadores_universitarios = [
                    'ESCUELA PROFESIONAL', 'CURSOS OFRECIDOS', 'PERIODO ACADÉMICO',
                    'FACULTAD DE', 'CARRERA DE'
                ]
                
                if any(indicador in texto_upper for indicador in indicadores_universitarios):
                    return 'excel_universitario'
                
                # Patrones de horarios universitarios
                if any(patron in texto_fila for patron in ['LU ', 'MA ', 'MI ', 'JU ', 'VI ']):
                    return 'excel_universitario'
                
                # Códigos universitarios
                if re.search(r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?\s*\n?\s*[A-Z]', texto_fila):
                    return 'excel_universitario'
            
            return 'excel_estandar'
            
        except Exception:
            return 'excel_estandar'
    
    def leer_excel_estandar(self, archivo: str) -> Dict:
        """
        Lee archivos Excel en formato estándar (matriz de horarios).
        Mantiene compatibilidad con el formato original.
        """
        print(f"📊 Procesando Excel estándar: {archivo}")
        
        try:
            df = pd.read_excel(archivo, index_col=0)
            
            # Convertir a formato de lista de cursos
            cursos = []
            id_curso = 1
            
            for dia_col in df.columns:
                for hora_idx in df.index[:14]:
                    celda = df.loc[hora_idx, dia_col]
                    if pd.notna(celda):
                        partes = str(celda).split('|')
                        if len(partes) >= 3:
                            curso = {
                                'id': id_curso,
                                'nombre': partes[1],
                                'profesor': partes[2],
                                'tipo': partes[3] if len(partes) > 3 else 'Teórico',
                                'codigo': f"CURSO_{id_curso}",
                                'horarios': [{
                                    'dia': dia_col,
                                    'hora_inicio': f"{7 + df.index.get_loc(hora_idx)}:00",
                                    'hora_fin': f"{8 + df.index.get_loc(hora_idx)}:00",
                                    'salon': 'SALON NO ASIGNADO'
                                }]
                            }
                            cursos.append(curso)
                            id_curso += 1
            
            # Crear matriz de horarios compatible
            carga_horaria = self._crear_matriz_desde_dataframe(df)
            
            return {
                'cursos': cursos,
                'carga_horaria': carga_horaria,
                'estadisticas': {'total_cursos': len(cursos), 'formato': 'excel_estandar'},
                'formato': 'excel_estandar'
            }
            
        except Exception as e:
            raise Exception(f"Error procesando Excel estándar: {e}")
    
    def _crear_matriz_desde_dataframe(self, df: pd.DataFrame):
        """Convierte DataFrame a matriz de horarios."""
        matriz = [[None for _ in range(14)] for _ in range(5)]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for dia_idx, dia_col in enumerate(df.columns):
            if dia_idx >= 5:
                break
            for hora_idx in range(min(14, len(df.index))):
                celda = df.iloc[hora_idx, dia_idx]
                if pd.notna(celda):
                    partes = str(celda).split('|')
                    if len(partes) >= 3:
                        matriz[dia_idx][hora_idx] = {
                            'id': int(partes[0]) if partes[0].isdigit() else 1,
                            'nombre': partes[1],
                            'profesor': partes[2],
                            'tipo': partes[3] if len(partes) > 3 else 'Teórico'
                        }
        
        return matriz
    
    def obtener_estadisticas_ultimo_archivo(self) -> Dict:
        """Obtiene estadísticas del último archivo procesado."""
        return {
            'formato_detectado': self.ultimo_formato_detectado,
            'lector_utilizado': 'PDF' if self.ultimo_formato_detectado == 'pdf' else 'Excel'
        }


# ============================================================================
# LECTOR PDF ORIGINAL (Integrado)
# ============================================================================

class LectorPDFHorarios:
    """
    Lector de archivos PDF con horarios académicos.
    CÓDIGO ORIGINAL MANTENIDO para compatibilidad.
    """
    
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
        
    def leer_pdf(self, archivo_pdf: str) -> Dict:
        """
        Lee un archivo PDF y extrae la información de horarios.
        
        Args:
            archivo_pdf: Ruta al archivo PDF
            
        Returns:
            Dict con la información extraída
        """
        try:
            doc = fitz.open(archivo_pdf)
            texto_completo = ""
            
            # Extraer texto de todas las páginas
            for pagina in doc:
                texto_completo += pagina.get_text()
            
            doc.close()
            
            # Procesar el texto extraído
            cursos = self.procesar_texto_pdf(texto_completo)
            
            # Crear matriz de horarios
            self.crear_matriz_horarios(cursos)
            
            return {
                'cursos': cursos,
                'matriz_horarios': self.matriz_horarios,
                'carga_horaria': self.matriz_horarios,  # Alias para compatibilidad
                'estadisticas': self.generar_estadisticas(cursos),
                'formato': 'pdf'
            }
            
        except Exception as e:
            raise Exception(f"Error al leer el PDF: {str(e)}")
    
    def procesar_texto_pdf(self, texto: str) -> List[Dict]:
        """Procesa el texto extraído del PDF y extrae información de cursos."""
        cursos = []
        lineas = texto.split('\n')
        
        # Patrones para identificar información
        patron_horario = r'([A-Z]{2})\s+(\d{1,2}:\d{2})-(\d{1,2}:\d{2})'
        patron_codigo = r'([A-Z]{2,3}\d{1,3}[A-Z]?)\s*([A-Z])'
        patron_capacidad = r'\b(\d{1,3})\s*$'
        
        curso_actual = None
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea:
                continue
                
            # Buscar códigos de curso
            match_codigo = re.search(patron_codigo, linea)
            if match_codigo:
                codigo_base = match_codigo.group(1)
                seccion = match_codigo.group(2)
                codigo_completo = f"{codigo_base}_{seccion}"
                
                # Buscar el nombre del curso (líneas anteriores o siguientes)
                nombre_curso = self.extraer_nombre_curso(lineas, i)
                
                curso_actual = {
                    'id': len(cursos) + 1,
                    'codigo': codigo_completo,
                    'nombre': nombre_curso,
                    'seccion': seccion,
                    'horarios': [],
                    'profesor': '',
                    'capacidad': 0,
                    'tipo': 'Teórico'
                }
                continue
            
            # Buscar horarios
            match_horario = re.search(patron_horario, linea)
            if match_horario and curso_actual:
                dia = match_horario.group(1)
                hora_inicio = match_horario.group(2)
                hora_fin = match_horario.group(3)
                
                # Extraer información adicional de la línea
                salon = self.extraer_salon(linea)
                profesor = self.extraer_profesor(linea)
                
                horario_info = {
                    'dia': self.dias_semana.get(dia, dia),
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'salon': salon,
                    'profesor': profesor
                }
                
                curso_actual['horarios'].append(horario_info)
                
                # Actualizar profesor del curso si no está establecido
                if not curso_actual['profesor'] and profesor:
                    curso_actual['profesor'] = profesor
            
            # Buscar capacidad
            match_capacidad = re.search(patron_capacidad, linea)
            if match_capacidad and curso_actual:
                capacidad = int(match_capacidad.group(1))
                if capacidad < 200:  # Filtrar números que probablemente sean capacidades
                    curso_actual['capacidad'] = capacidad
                    
                    # Finalizar curso actual
                    if curso_actual['horarios']:
                        cursos.append(curso_actual.copy())
                    curso_actual = None
        
        return cursos
    
    def extraer_nombre_curso(self, lineas: List[str], indice_actual: int) -> str:
        """Extrae el nombre del curso buscando en líneas cercanas."""
        # Buscar en las líneas siguientes
        for i in range(indice_actual + 1, min(indice_actual + 5, len(lineas))):
            linea = lineas[i].strip()
            # Si la línea parece un nombre de curso (tiene letras y espacios)
            if re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', linea) and len(linea) > 5:
                return linea
        
        # Buscar en líneas anteriores
        for i in range(max(0, indice_actual - 5), indice_actual):
            linea = lineas[i].strip()
            if re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', linea) and len(linea) > 5:
                return linea
                
        return "CURSO SIN NOMBRE"
    
    def extraer_salon(self, linea: str) -> str:
        """Extrae información del salón de la línea."""
        # Buscar patrones como R1-450, J3-182A, LAB F, etc.
        patron_salon = r'([A-Z]+\d*[-\w]*|LAB\s*[A-Z0-9]*)'
        match = re.search(patron_salon, linea)
        return match.group(1) if match else ""
    
    def extraer_profesor(self, linea: str) -> str:
        """Extrae el nombre del profesor de la línea."""
        # Buscar patrones de nombres (palabras con solo letras mayúsculas)
        palabras = linea.split()
        nombres = []
        
        for palabra in palabras:
            # Si la palabra parece un nombre (solo letras mayúsculas y puntos)
            if re.match(r'^[A-ZÁÉÍÓÚÑ\.]+$', palabra) and len(palabra) > 2:
                # Evitar palabras que parecen códigos de sala
                if not re.match(r'^[A-Z]\d', palabra):
                    nombres.append(palabra)
        
        return ' '.join(nombres[:2])  # Tomar máximo 2 nombres
    
    def crear_matriz_horarios(self, cursos: List[Dict]):
        """Crea una matriz de horarios similar al formato Excel original."""
        # Crear estructura de 5 días x 14 bloques horarios
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias:
                    dia_idx = dias.index(horario['dia'])
                    
                    # Convertir hora a índice de bloque
                    bloque_inicio = self.hora_a_bloque(horario['hora_inicio'])
                    bloque_fin = self.hora_a_bloque(horario['hora_fin'])
                    
                    # Asignar curso a los bloques correspondientes
                    for bloque in range(bloque_inicio, bloque_fin):
                        if 0 <= bloque < 14:
                            self.matriz_horarios[dia_idx][bloque] = {
                                'id': curso['id'],
                                'nombre': curso['nombre'],
                                'profesor': curso['profesor'],
                                'tipo': curso['tipo'],
                                'codigo': curso['codigo'],
                                'salon': horario['salon']
                            }
    
    def hora_a_bloque(self, hora_str: str) -> int:
        """Convierte una hora en formato HH:MM a índice de bloque."""
        try:
            hora, minuto = map(int, hora_str.split(':'))
            # Calcular bloque (cada bloque es de 1 hora, empezando a las 7:00)
            bloque = hora - 7
            return max(0, bloque)
        except:
            return 0
    
    def generar_estadisticas(self, cursos: List[Dict]) -> Dict:
        """Genera estadísticas sobre los cursos procesados."""
        total_cursos = len(cursos)
        profesores = set()
        escuelas = set()
        
        for curso in cursos:
            if curso['profesor']:
                profesores.add(curso['profesor'])
            
            # Extraer escuela del código
            if curso['codigo']:
                escuela = curso['codigo'][:2]
                escuelas.add(escuela)
        
        return {
            'total_cursos': total_cursos,
            'total_profesores': len(profesores),
            'total_escuelas': len(escuelas),
            'profesores': list(profesores),
            'escuelas': list(escuelas),
            'formato': 'pdf'
        }
    
    def exportar_a_excel(self, cursos: List[Dict], archivo_salida: str):
        """Exporta los cursos procesados a formato Excel compatible con el optimizador."""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{7+i}:00 - {8+i}:00" for i in range(14)]
        
        # Crear DataFrame
        df = pd.DataFrame(index=horas, columns=dias)
        
        # Llenar con información de cursos
        for dia_idx, dia in enumerate(dias):
            for bloque in range(14):
                if self.matriz_horarios[dia_idx][bloque]:
                    curso = self.matriz_horarios[dia_idx][bloque]
                    # Formato: "id|nombre|profesor|tipo"
                    celda = f"{curso['id']}|{curso['nombre']}|{curso['profesor']}|{curso['tipo']}"
                    df.iloc[bloque, dia_idx] = celda
        
        # Guardar archivo
        df.to_excel(archivo_salida)
        print(f"Archivo Excel generado: {archivo_salida}")
    
    def mostrar_resumen(self, datos: Dict):
        """Muestra un resumen de los datos procesados."""
        print("\n" + "="*60)
        print("RESUMEN DE PROCESAMIENTO DEL PDF")
        print("="*60)
        
        estadisticas = datos['estadisticas']
        print(f"Total de cursos procesados: {estadisticas['total_cursos']}")
        print(f"Total de profesores: {estadisticas['total_profesores']}")
        print(f"Total de escuelas: {estadisticas['total_escuelas']}")
        
        print(f"\nEscuelas encontradas: {', '.join(estadisticas['escuelas'])}")
        
        print(f"\nPrimeros 10 cursos:")
        for i, curso in enumerate(datos['cursos'][:10]):
            print(f"{i+1:2d}. {curso['codigo']} - {curso['nombre'][:40]}")
            if curso['horarios']:
                horario = curso['horarios'][0]
                print(f"     {horario['dia']} {horario['hora_inicio']}-{horario['hora_fin']}")
        
        if len(datos['cursos']) > 10:
            print(f"     ... y {len(datos['cursos']) - 10} cursos más")


# ============================================================================
# LECTOR EXCEL UNIVERSITARIO (Integrado)
# ============================================================================

class LectorExcelHorarios:
    """
    Lector especializado para archivos Excel con horarios universitarios
    en el formato específico de la universidad.
    CÓDIGO NUEVO INTEGRADO para formato universitario.
    """
    
    def __init__(self):
        self.dias_semana = {
            'LU': 'Lunes',
            'MA': 'Martes', 
            'MI': 'Miércoles',
            'JU': 'Jueves',
            'VI': 'Viernes',
            'SA': 'Sábado'
        }
        
        self.cursos_procesados = []
        self.matriz_horarios = None
        self.estadisticas = {}
        
    def leer_excel_universitario(self, archivo_excel: str) -> Dict:
        """
        Lee un archivo Excel con formato universitario específico.
        
        Args:
            archivo_excel: Ruta al archivo Excel
            
        Returns:
            Dict con la información procesada
        """
        try:
            print(f"🎓 Procesando archivo Excel universitario: {archivo_excel}")
            
            # Leer Excel con configuración específica
            df = pd.read_excel(archivo_excel, header=None)
            
            print(f"📊 Dimensiones del archivo: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Procesar datos
            cursos = self._procesar_datos_universitarios(df)
            
            # Crear matriz de horarios
            self._crear_matriz_horarios(cursos)
            
            # Generar estadísticas
            self._generar_estadisticas(cursos)
            
            return {
                'cursos': cursos,
                'matriz_horarios': self.matriz_horarios,
                'carga_horaria': self.matriz_horarios,  # Alias para compatibilidad
                'estadisticas': self.estadisticas,
                'formato': 'excel_universitario'
            }
            
        except Exception as e:
            raise Exception(f"Error al procesar Excel universitario: {str(e)}")
    
    def _procesar_datos_universitarios(self, df: pd.DataFrame) -> List[Dict]:
        """Procesa los datos con el formato específico universitario."""
        cursos = []
        curso_actual = None
        escuela_actual = None
        id_curso = 1
        
        print("🔄 Analizando estructura del archivo...")
        
        for i, fila in df.iterrows():
            # Convertir fila a lista y limpiar
            datos_fila = [str(x).strip() if pd.notna(x) else '' for x in fila.values]
            
            # Detectar encabezado de escuela
            if self._es_encabezado_escuela(datos_fila[0]):
                escuela_actual = self._extraer_escuela(datos_fila[0])
                print(f"🏫 Procesando escuela: {escuela_actual}")
                curso_actual = None
                continue
            
            # Detectar inicio de nuevo curso
            if self._es_inicio_curso(datos_fila):
                curso_actual = self._crear_curso_base(datos_fila, escuela_actual)
                continue
            
            # Procesar secciones del curso actual
            if curso_actual and self._es_seccion_curso(datos_fila):
                seccion_info = self._procesar_seccion(datos_fila, curso_actual, id_curso)
                if seccion_info:
                    cursos.append(seccion_info)
                    id_curso += 1
        
        print(f"✅ Procesados {len(cursos)} cursos del archivo universitario")
        return cursos
    
    def _es_encabezado_escuela(self, texto: str) -> bool:
        """Detecta si una línea es un encabezado de escuela."""
        texto_upper = texto.upper()
        indicadores = [
            'ESCUELA PROFESIONAL',
            'FACULTAD DE',
            'CARRERA DE',
            'DEPARTAMENTO'
        ]
        return any(indicador in texto_upper for indicador in indicadores)
    
    def _extraer_escuela(self, texto: str) -> str:
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
    
    def _es_inicio_curso(self, datos_fila: List[str]) -> bool:
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
    
    def _crear_curso_base(self, datos_fila: List[str], escuela: str) -> Dict:
        """Crea la información base de un curso."""
        return {
            'nombre': datos_fila[0].strip(),
            'escuela': escuela,
            'secciones': []
        }
    
    def _es_seccion_curso(self, datos_fila: List[str]) -> bool:
        """Detecta si la fila contiene información de una sección."""
        return (len(datos_fila) >= 3 and 
                (self._contiene_codigo_seccion(datos_fila[1]) or 
                 self._contiene_horarios(datos_fila[2])))
    
    def _contiene_codigo_seccion(self, texto: str) -> bool:
        """Verifica si el texto contiene un código de sección."""
        if not texto or texto == 'nan':
            return False
        
        # Buscar patrones como "BFI01\nA" o códigos similares
        patron_codigo = r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?\s*\n?\s*[A-Z]'
        return bool(re.search(patron_codigo, texto))
    
    def _contiene_horarios(self, texto: str) -> bool:
        """Verifica si el texto contiene información de horarios."""
        if not texto or texto == 'nan':
            return False
        
        # Buscar patrones de horarios como "LU 10-12" o "MI 14-16"
        patron_horario = r'[A-Z]{2}\s+\d{1,2}-\d{1,2}'
        return bool(re.search(patron_horario, texto))
    
    def _procesar_seccion(self, datos_fila: List[str], curso_base: Dict, id_curso: int) -> Optional[Dict]:
        """Procesa una sección específica de un curso."""
        try:
            # Extraer información de la sección
            codigo_seccion = self._extraer_codigo_seccion(datos_fila[1])
            horarios_texto = datos_fila[2] if len(datos_fila) > 2 else ''
            salones_texto = datos_fila[3] if len(datos_fila) > 3 else ''
            profesores_texto = datos_fila[4] if len(datos_fila) > 4 else ''
            capacidad = self._extraer_capacidad(datos_fila[5] if len(datos_fila) > 5 else '')
            
            # Procesar horarios
            horarios = self._procesar_horarios_texto(horarios_texto, salones_texto)
            
            # Procesar profesores
            profesores = self._procesar_profesores_texto(profesores_texto)
            
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
                'tipo': self._determinar_tipo_curso(horarios_texto, salones_texto),
                'capacidad': capacidad,
                'horarios': horarios,
                'salones': self._extraer_salones(salones_texto)
            }
            
            return curso_completo
            
        except Exception as e:
            print(f"⚠️  Error procesando sección: {e}")
            return None
    
    def _extraer_codigo_seccion(self, texto: str) -> str:
        """Extrae el código de la sección."""
        if not texto or texto == 'nan':
            return f"CURSO_{np.random.randint(1000, 9999)}_A"
        
        # Limpiar el texto y buscar patrón de código
        texto_limpio = texto.replace('\n', ' ').strip()
        
        # Buscar patrón como "BFI01 A"
        patron = r'([A-Z]{2,3}[I]?\d{2,3}[A-Z]?)\s+([A-Z])'
        match = re.search(patron, texto_limpio)
        
        if match:
            codigo_base = match.group(1)
            seccion = match.group(2)
            return f"{codigo_base}_{seccion}"
        
        return f"CURSO_{np.random.randint(1000, 9999)}_A"
    
    def _procesar_horarios_texto(self, horarios_texto: str, salones_texto: str) -> List[Dict]:
        """Procesa el texto de horarios y lo convierte a estructura de datos."""
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
            salon = self._limpiar_salon(salon)
            
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
    
    def _limpiar_salon(self, salon_texto: str) -> str:
        """Limpia y extrae el nombre del salón."""
        if not salon_texto or salon_texto == 'nan':
            return 'SALON NO ASIGNADO'
        
        # Remover información adicional como URLs de zoom
        salon_limpio = re.sub(r'/\s*zoom\d+.*', '', salon_texto)
        salon_limpio = re.sub(r'\(.*?\)', '', salon_limpio)
        
        return salon_limpio.strip()
    
    def _procesar_profesores_texto(self, profesores_texto: str) -> List[str]:
        """Procesa el texto de profesores."""
        if not profesores_texto or profesores_texto == 'nan':
            return []
        
        profesores = []
        for linea in profesores_texto.split('\n'):
            profesor = linea.strip()
            if profesor and profesor != 'nan':
                # Limpiar formato del nombre
                profesor = re.sub(r'^[A-Z]\.\s*', '', profesor)
                profesores.append(profesor.upper())
        
        return profesores
    
    def _extraer_capacidad(self, capacidad_texto: str) -> int:
        """Extrae la capacidad del curso."""
        if not capacidad_texto or capacidad_texto == 'nan':
            return 30
        
        try:
            return int(float(capacidad_texto))
        except:
            return 30
    
    def _determinar_tipo_curso(self, horarios_texto: str, salones_texto: str) -> str:
        """Determina el tipo de curso basado en horarios y salones."""
        if 'LAB' in salones_texto.upper():
            return 'Práctico'
        elif 'TALLER' in salones_texto.upper():
            return 'Taller'
        else:
            return 'Teórico'
    
    def _extraer_salones(self, salones_texto: str) -> List[str]:
        """Extrae la lista de salones."""
        if not salones_texto or salones_texto == 'nan':
            return ['SALON NO ASIGNADO']
        
        salones = []
        for linea in salones_texto.split('\n'):
            salon = self._limpiar_salon(linea)
            if salon and salon != 'SALON NO ASIGNADO':
                salones.append(salon)
        
        return salones if salones else ['SALON NO ASIGNADO']
    
    def _crear_matriz_horarios(self, cursos: List[Dict]):
        """Crea la matriz de horarios compatible con el optimizador."""
        # Matriz 5 días x 14 bloques (7:00 AM - 9:00 PM)
        self.matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        bloques_ocupados = 0
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias_orden:
                    dia_idx = dias_orden.index(horario['dia'])
                    
                    # Calcular bloques ocupados
                    bloque_inicio = max(0, horario['bloque_inicio'])
                    bloque_fin = min(14, horario['bloque_fin'])
                    
                    for bloque in range(bloque_inicio, bloque_fin):
                        if 0 <= bloque < 14:
                            self.matriz_horarios[dia_idx][bloque] = {
                                'id': curso['id'],
                                'nombre': curso['nombre'],
                                'codigo': curso['codigo'],
                                'profesor': curso['profesor'],
                                'tipo': curso['tipo'],
                                'salon': horario['salon']
                            }
                            bloques_ocupados += 1
        
        print(f"📊 Matriz de horarios: {bloques_ocupados}/70 bloques ocupados ({bloques_ocupados/70*100:.1f}%)")
    
    def _generar_estadisticas(self, cursos: List[Dict]):
        """Genera estadísticas del procesamiento."""
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
        
        self.estadisticas = {
            'total_cursos': len(cursos),
            'total_escuelas': len(escuelas),
            'total_profesores': len([p for p in profesores if p != 'SIN ASIGNAR']),
            'escuelas': sorted(list(escuelas)),
            'tipos_curso': sorted(list(tipos_curso)),
            'cursos_por_escuela': cursos_por_escuela,
            'cursos_con_profesor': len([c for c in cursos if c['profesor'] != 'SIN ASIGNAR']),
            'formato': 'excel_universitario'
        }
    
    def mostrar_resumen(self, datos: Dict):
        """Muestra un resumen del procesamiento."""
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
            for curso in cursos_escuela[:3]:
                horario_info = ""
                if curso['horarios']:
                    h = curso['horarios'][0]
                    horario_info = f" ({h['dia']} {h['hora_inicio']}-{h['hora_fin']})"
                
                print(f"      {curso['codigo']:<12} {curso['nombre'][:30]:<30}{horario_info}")
            
            if len(cursos_escuela) > 3:
                print(f"      ... y {len(cursos_escuela) - 3} cursos más")
    
    def exportar_a_excel_optimizador(self, datos: Dict, archivo_salida: str):
        """Exporta a formato Excel compatible con el optimizador original."""
        try:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            horas = [f"{7+i}:00 - {8+i}:00" for i in range(14)]
            
            # Crear DataFrame
            df = pd.DataFrame(index=horas, columns=dias)
            
            # Llenar con datos de la matriz
            for dia_idx, dia in enumerate(dias):
                for bloque in range(14):
                    curso = self.matriz_horarios[dia_idx][bloque]
                    if curso:
                        # Formato compatible: "id|nombre|profesor|tipo"
                        celda = f"{curso['id']}|{curso['nombre']}|{curso['profesor']}|{curso['tipo']}"
                        df.iloc[bloque, dia_idx] = celda
            
            # Guardar archivo
            df.to_excel(archivo_salida)
            print(f"📊 Archivo Excel para optimizador generado: {archivo_salida}")
            
        except Exception as e:
            print(f"❌ Error al exportar: {e}")


# ============================================================================
# FUNCIONES DE UTILIDAD Y TESTING
# ============================================================================

def test_lector_unificado(archivo: str):
    """Función de prueba para el lector unificado."""
    print("🧪 PRUEBA DEL LECTOR UNIFICADO")
    print("="*45)
    
    try:
        lector = LectorHorarios()
        datos = lector.leer_archivo(archivo)
        
        print(f"✅ Archivo procesado exitosamente")
        print(f"📊 Formato detectado: {lector.ultimo_formato_detectado}")
        
        # Mostrar estadísticas
        stats = datos['estadisticas']
        print(f"\n📈 Estadísticas:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Mostrar algunos cursos de ejemplo
        if 'cursos' in datos and datos['cursos']:
            print(f"\n📚 Primeros 5 cursos:")
            for i, curso in enumerate(datos['cursos'][:5]):
                print(f"   {i+1}. {curso.get('codigo', 'N/A')} - {curso['nombre'][:30]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False


def main():
    """Función principal para pruebas directas del módulo."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python lector_horarios.py <archivo> [--test]")
        print("\nEjemplos:")
        print("  python lector_horarios.py datos/Horarios_2023_1.xlsx")
        print("  python lector_horarios.py datos/horario.pdf")
        print("  python lector_horarios.py archivo.xlsx --test")
        return
    
    archivo = sys.argv[1]
    es_prueba = '--test' in sys.argv
    
    if es_prueba:
        test_lector_unificado(archivo)
    else:
        try:
            lector = LectorHorarios()
            datos = lector.leer_archivo(archivo)
            
            # Mostrar resumen según el tipo
            if lector.ultimo_formato_detectado == 'pdf':
                lector.lector_pdf.mostrar_resumen(datos)
            elif lector.ultimo_formato_detectado == 'excel_universitario':
                lector.lector_excel.mostrar_resumen(datos)
            else:
                print("✅ Archivo procesado en formato estándar")
            
            # Ofrecer exportar a Excel compatible
            respuesta = input("\n¿Exportar a formato compatible con optimizador? (s/n): ")
            if respuesta.lower() == 's':
                archivo_salida = input("Nombre del archivo de salida: ").strip()
                if not archivo_salida:
                    archivo_salida = "horarios_convertidos.xlsx"
                
                if lector.ultimo_formato_detectado == 'excel_universitario':
                    lector.lector_excel.exportar_a_excel_optimizador(datos, archivo_salida)
                elif lector.ultimo_formato_detectado == 'pdf':
                    lector.lector_pdf.exportar_a_excel(datos['cursos'], archivo_salida)
                else:
                    print("Formato ya compatible")
                
                print(f"\n🚀 Para optimizar execute:")
                print(f"   python scripts/optimizar.py {archivo_salida}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()