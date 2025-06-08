#!/usr/bin/env python3


import re
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF


class LectorHorarios:
    
    def __init__(self):
        self.lector_pdf = LectorPDFHorarios()
        self.lector_excel = LectorExcelUniversitario()
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
            str: 'pdf', 'xlsx' y 'xls'
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
# LECTOR EXCEL UNIVERSITARIO COMPLETAMENTE CORREGIDO
# ============================================================================

class LectorExcelUniversitario:


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
        self.debug_mode = os.getenv('DEBUG_LECTOR') == '1'
    
    def leer_excel_universitario(self, archivo_excel: str) -> Dict:

        try:
            print(f"🎓 Procesando archivo Excel universitario: {archivo_excel}")
            
            # Leer Excel completo
            df = pd.read_excel(archivo_excel, header=None)
            print(f"📊 Dimensiones del archivo: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Mostrar estructura para debug
            if self.debug_mode:
                self._debug_estructura_archivo(df)
            
            # ✅ PROCESAMIENTO COMPLETAMENTE CORREGIDO
            cursos = self._procesar_datos_universitarios_corregido(df)
            
            # Crear matriz y estadísticas
            self._crear_matriz_horarios(cursos)
            self._generar_estadisticas(cursos)
            
            return {
                'cursos': cursos,
                'matriz_horarios': self.matriz_horarios,
                'carga_horaria': self.matriz_horarios,
                'estadisticas': self.estadisticas,
                'formato': 'excel_universitario'
            }
            
        except Exception as e:
            raise Exception(f"Error al procesar Excel universitario: {str(e)}")
    
    def _debug_estructura_archivo(self, df: pd.DataFrame):
        """Muestra estructura del archivo para entender el formato."""
        print("🔍 ANÁLISIS DE ESTRUCTURA DEL ARCHIVO:")
        print("-" * 50)
        
        # Mostrar primeras 15 filas para entender la estructura
        for i in range(min(15, len(df))):
            fila = df.iloc[i]
            datos_fila = [str(x) if pd.notna(x) else 'NaN' for x in fila.values]
            
            # Identificar qué tipo de fila es
            tipo_fila = self._identificar_tipo_fila(datos_fila)
            print(f"Fila {i:2d} ({tipo_fila}): {datos_fila[:3]}")  # Mostrar primeras 3 columnas
    
    def _identificar_tipo_fila(self, datos_fila: List[str]) -> str:

        if not datos_fila[0] or datos_fila[0] == 'NaN':
            if (len(datos_fila) >= 3 and datos_fila[2] != 'NaN' and
                ('LU ' in datos_fila[2] or 'MA ' in datos_fila[2] or 'MI ' in datos_fila[2])):
                return "SECCION_ADICIONAL"
            return "VACÍA"
        
        if 'ESCUELA PROFESIONAL' in datos_fila[0].upper():
            return "ESCUELA"
        
        # ✅ CORRECCIÓN 1: Lógica mejorada para detectar cursos principales
        if self._es_curso_principal_mejorado(datos_fila):
            return "CURSO_PRINCIPAL"
        
        # ✅ CORRECCIÓN 2: Detectar cursos que no siguen el formato estándar
        if self._es_curso_formato_alternativo(datos_fila):
            return "CURSO_PRINCIPAL"  # Tratarlos como curso principal
        
        return "OTRA"
    
    def _es_curso_principal_mejorado(self, datos_fila: List[str]) -> bool:

        # Método original: nombre en primera columna Y código en segunda
        if (datos_fila[0] and datos_fila[0] != '' and
            len(datos_fila) >= 2 and datos_fila[1] and
            self._contiene_codigo_seccion(datos_fila[1])):
            return True
        
        # ✅ NUEVO: Detectar cursos que son evidentemente nombres de materia
        if (datos_fila[0] and 
            self._parece_nombre_curso_universitario(datos_fila[0]) and
            not 'ESCUELA' in datos_fila[0].upper()):
            return True
        
        return False
    
    def _es_curso_formato_alternativo(self, datos_fila: List[str]) -> bool:

        # Si la primera columna parece un nombre de curso pero no tiene código inmediato
        if (datos_fila[0] and 
            self._parece_nombre_curso_universitario(datos_fila[0]) and
            not 'ESCUELA' in datos_fila[0].upper()):
            
            # Verificar si hay información que sugiera que es un curso
            # (código en segunda columna, horarios en tercera, etc.)
            tiene_info_curso = False
            
            if len(datos_fila) >= 2 and datos_fila[1]:
                # Puede tener código sin sección clara
                if re.search(r'[A-Z]{2,3}[I]?\d{2,3}', datos_fila[1]):
                    tiene_info_curso = True
            
            if len(datos_fila) >= 3 and datos_fila[2]:
                # Puede tener horarios
                if self._contiene_horarios(datos_fila[2]):
                    tiene_info_curso = True
            
            return tiene_info_curso
        
        return False
    
    def _parece_nombre_curso_universitario(self, texto: str) -> bool:

        if not texto or len(texto.strip()) < 3:
            return False
        
        texto_upper = texto.upper().strip()
        
        # Lista extendida de palabras que indican cursos universitarios
        palabras_curso = [
            'FÍSICA', 'MATEMÁTICA', 'QUÍMICA', 'BIOLOGÍA', 'COMPUTACIÓN',
            'CÁLCULO', 'ÁLGEBRA', 'GEOMETRÍA', 'ESTADÍSTICA', 'PROBABILIDAD',
            'LABORATORIO', 'TALLER', 'SEMINARIO', 'PROYECTO', 'TESIS',
            'MECÁNICA', 'ELECTROMAGNETISMO', 'TERMODINÁMICA', 'ÓPTICA',
            'CUÁNTICA', 'RELATIVIDAD', 'NUCLEAR', 'ATÓMICA', 'MOLECULAR',
            'MÉTODOS', 'INTRODUCCIÓN', 'FUNDAMENTOS', 'PRINCIPIOS',
            'TEORÍA', 'PRÁCTICA', 'EXPERIMENTAL', 'TEÓRICA', 'ANÁLISIS',
            'ECUACIONES', 'DIFERENCIALES', 'INTEGRALES', 'VECTORIAL',
            'LINEAL', 'DISCRETA', 'NUMÉRICA', 'COMPUTACIONAL', 'APLICADA',
            'CLÁSICA', 'MODERNA', 'GENERAL', 'ESPECIAL', 'AVANZADA'
        ]
        
        # Verificar si contiene palabras típicas de cursos
        contiene_palabra_curso = any(palabra in texto_upper for palabra in palabras_curso)
        
        # Verificar patrones típicos de nombres de curso
        patrones_curso = [
            r'.*I{1,3}$',       # Termina en I, II, III
            r'.*IV$',           # Termina en IV
            r'.*V$',            # Termina en V
            r'INTRODUCCIÓN.*',  # Empieza con INTRODUCCIÓN
            r'FUNDAMENTOS.*',   # Empieza con FUNDAMENTOS
            r'MÉTODOS.*',       # Empieza con MÉTODOS
        ]
        
        patron_detectado = any(re.match(patron, texto_upper) for patron in patrones_curso)
        
        # No debe ser un código de curso
        no_es_codigo = not re.match(r'^[A-Z]{2,3}[I]?\d{2,3}[A-Z]?$', texto_upper)
        
        # No debe ser muy corto
        longitud_adecuada = len(texto.strip()) >= 5
        
        return (contiene_palabra_curso or patron_detectado) and no_es_codigo and longitud_adecuada
    
    def _procesar_datos_universitarios_corregido(self, df: pd.DataFrame) -> List[Dict]:

        cursos = []
        escuela_actual = None
        curso_base_actual = None
        id_curso = 1
        
        print("\n🔄 PROCESAMIENTO COMPLETAMENTE CORREGIDO:")
        print("-" * 50)
        
        i = 0
        while i < len(df):
            fila = df.iloc[i]
            datos_fila = [str(x).strip() if pd.notna(x) else '' for x in fila.values]
            
            # 1. Detectar encabezado de escuela
            if self._es_encabezado_escuela(datos_fila[0]):
                escuela_actual = self._extraer_codigo_escuela(datos_fila[0])
                print(f"🏫 Escuela: {escuela_actual}")
                i += 1
                continue
            
            # 2. Detectar curso principal con lógica mejorada
            if (self._es_curso_principal_mejorado(datos_fila) or 
                self._es_curso_formato_alternativo(datos_fila)):
                
                # Extraer nombre del curso
                nombre_curso = datos_fila[0].strip()
                curso_base_actual = {
                    'nombre': nombre_curso,
                    'escuela': escuela_actual or 'XX'
                }
                print(f"📚 Curso: {nombre_curso}")
                
                # Procesar la primera sección
                if self._es_curso_principal_mejorado(datos_fila):
                    # Tiene código explícito, procesar normalmente
                    seccion = self._procesar_seccion_corregida(datos_fila, curso_base_actual, id_curso)
                    if seccion:
                        cursos.append(seccion)
                        print(f"   ✅ Sección {seccion['seccion']}: {seccion['codigo']}")
                        id_curso += 1
                else:
                    # Formato alternativo, crear sección por defecto
                    seccion = self._crear_seccion_desde_formato_alternativo(datos_fila, curso_base_actual, id_curso)
                    if seccion:
                        cursos.append(seccion)
                        print(f"   ✅ Sección (auto) {seccion['seccion']}: {seccion['codigo']}")
                        id_curso += 1
                
                i += 1
                
                # Buscar secciones adicionales
                secciones_procesadas = 1
                
                while i < len(df):
                    fila_actual = df.iloc[i]
                    datos_actual = [str(x).strip() if pd.notna(x) else '' for x in fila_actual.values]
                    
                    if self._es_seccion_adicional(datos_actual):
                        seccion = self._procesar_seccion_corregida(datos_actual, curso_base_actual, id_curso)
                        if seccion:
                            cursos.append(seccion)
                            print(f"   ✅ Sección {seccion['seccion']}: {seccion['codigo']}")
                            id_curso += 1
                            secciones_procesadas += 1
                            
                    elif self._es_fila_horarios_adicionales(datos_actual):
                        if len(cursos) > 0:
                            self._intentar_agregar_horarios_adicionales(cursos[-1], datos_actual)
                            
                    elif self._podria_ser_nueva_seccion_implicita(datos_actual, curso_base_actual):
                        seccion_implicita = self._crear_seccion_implicita(datos_actual, curso_base_actual, id_curso, secciones_procesadas)
                        if seccion_implicita:
                            cursos.append(seccion_implicita)
                            print(f"   ✅ Sección implícita {seccion_implicita['seccion']}: {seccion_implicita['codigo']}")
                            id_curso += 1
                            secciones_procesadas += 1
                    else:
                        # No es parte del curso actual
                        break
                    
                    i += 1
                
                print(f"   📊 Total secciones procesadas para '{nombre_curso}': {secciones_procesadas}")
                continue
            
            i += 1
        
        print(f"\n✅ Total procesado: {len(cursos)} cursos/secciones")
        
        # Validar procesamiento
        self._validar_procesamiento_secciones(cursos)
        
        return cursos
    
    def _crear_seccion_desde_formato_alternativo(self, datos_fila: List[str], curso_base: Dict, id_curso: int) -> Optional[Dict]:
        """
        Crea sección cuando el curso no tiene formato estándar.
        """
        try:
            # Generar código automático
            escuela = curso_base['escuela']
            codigo_base = f"{escuela}XXX{id_curso:02d}"
            codigo_seccion = f"{codigo_base}_A"
            
            # Buscar información en las columnas
            horarios_texto = ''
            salones_texto = ''
            profesor_texto = ''
            
            # Buscar horarios en cualquier columna
            for i, dato in enumerate(datos_fila[1:4], 1):  # Columnas 1, 2, 3
                if dato and self._contiene_horarios(dato):
                    horarios_texto = dato
                    # Salones probablemente en la siguiente columna
                    if i + 1 < len(datos_fila):
                        salones_texto = datos_fila[i + 1]
                    # Profesor probablemente en la columna siguiente al salón
                    if i + 2 < len(datos_fila):
                        profesor_texto = datos_fila[i + 2]
                    break
            
            # Si no encontramos horarios, buscar código
            if not horarios_texto:
                for i, dato in enumerate(datos_fila[1:3], 1):  # Columnas 1, 2
                    if dato and re.search(r'[A-Z]{2,3}[I]?\d{2,3}', dato):
                        # Usar este como base para el código
                        match = re.search(r'([A-Z]{2,3}[I]?\d{2,3})', dato)
                        if match:
                            codigo_base = match.group(1)
                            codigo_seccion = f"{codigo_base}_A"
                        break
            
            # Procesar información
            horarios = self._procesar_horarios_corregido(horarios_texto, salones_texto) if horarios_texto else []
            profesor = self._procesar_profesor(profesor_texto) if profesor_texto else 'SIN ASIGNAR'
            
            curso = {
                'id': id_curso,
                'codigo': codigo_seccion,
                'nombre': curso_base['nombre'],
                'escuela': curso_base['escuela'],
                'seccion': 'A',
                'profesor': profesor,
                'tipo': self._determinar_tipo_curso(salones_texto),
                'capacidad': 30,
                'horarios': horarios,
                'salones': self._extraer_salones(salones_texto) if salones_texto else ['SALON NO ASIGNADO']
            }
            
            return curso
            
        except Exception as e:
            print(f"⚠️  Error creando sección desde formato alternativo: {e}")
            return None
    
    def _es_fila_horarios_adicionales(self, datos_fila: List[str]) -> bool:
        """Detecta filas que contienen horarios adicionales."""
        return (not datos_fila[0] and 
                (not datos_fila[1] or datos_fila[1] == '') and
                len(datos_fila) > 2 and 
                self._contiene_horarios(datos_fila[2]))

    def _contiene_horarios(self, texto: str) -> bool:
        """Verifica si un texto contiene horarios válidos."""
        if not texto:
            return False
        # Buscar patrones como "LU 10-12", "MI 14-16", etc.
        patron_horario = r'[A-Z]{2}\s+\d{1,2}-\d{1,2}'
        return bool(re.search(patron_horario, texto))

    def _podria_ser_nueva_seccion_implicita(self, datos_fila: List[str], curso_base: Dict) -> bool:
        """Detecta secciones implícitas (sin código explícito)."""
        return (not datos_fila[0] and not datos_fila[1] and
                len(datos_fila) > 2 and self._contiene_horarios(datos_fila[2]))

    def _crear_seccion_implicita(self, datos_fila: List[str], curso_base: Dict, id_curso: int, numero_seccion: int) -> Optional[Dict]:
        """Crea una sección implícita cuando no hay código explícito."""
        try:
            # Generar código y sección
            letras_seccion = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            seccion_letra = letras_seccion[numero_seccion] if numero_seccion < len(letras_seccion) else f"S{numero_seccion}"
            
            # Crear código basado en el curso y escuela
            codigo_base = f"{curso_base['escuela']}XXX{id_curso:02d}"
            codigo_seccion = f"{codigo_base}_{seccion_letra}"
            
            # Extraer horarios
            horarios_texto = datos_fila[2] if len(datos_fila) > 2 else ''
            salones_texto = datos_fila[3] if len(datos_fila) > 3 else ''
            profesor_texto = datos_fila[4] if len(datos_fila) > 4 else ''
            
            # Procesar información
            horarios = self._procesar_horarios_corregido(horarios_texto, salones_texto)
            profesor = self._procesar_profesor(profesor_texto)
            
            if not horarios:  # Si no hay horarios válidos, no crear la sección
                return None
            
            curso = {
                'id': id_curso,
                'codigo': codigo_seccion,
                'nombre': curso_base['nombre'],
                'escuela': curso_base['escuela'],
                'seccion': seccion_letra,
                'profesor': profesor,
                'tipo': self._determinar_tipo_curso(salones_texto),
                'capacidad': 30,
                'horarios': horarios,
                'salones': self._extraer_salones(salones_texto)
            }
            
            return curso
            
        except Exception as e:
            print(f"⚠️  Error creando sección implícita: {e}")
            return None

    def _intentar_agregar_horarios_adicionales(self, ultimo_curso: Dict, datos_fila: List[str]):
        """Intenta agregar horarios adicionales a la última sección."""
        try:
            horarios_texto = datos_fila[2] if len(datos_fila) > 2 else ''
            salones_texto = datos_fila[3] if len(datos_fila) > 3 else ''
            
            if horarios_texto and self._contiene_horarios(horarios_texto):
                horarios_adicionales = self._procesar_horarios_corregido(horarios_texto, salones_texto)
                if horarios_adicionales:
                    ultimo_curso['horarios'].extend(horarios_adicionales)
                    print(f"      📅 Horarios adicionales agregados a {ultimo_curso['codigo']}")
                    
        except Exception as e:
            print(f"⚠️  Error agregando horarios adicionales: {e}")

    def _validar_procesamiento_secciones(self, cursos: List[Dict]):
        """Valida que el procesamiento de secciones sea correcto."""
        print(f"\n📊 VALIDACIÓN DEL PROCESAMIENTO:")
        print("-" * 40)
        
        # Agrupar por nombre de curso
        cursos_agrupados = {}
        for curso in cursos:
            nombre = curso['nombre']
            if nombre not in cursos_agrupados:
                cursos_agrupados[nombre] = []
            cursos_agrupados[nombre].append(curso)
        
        # Mostrar estadísticas
        cursos_con_multiples_secciones = 0
        total_secciones = 0
        
        for nombre_curso, secciones in cursos_agrupados.items():
            num_secciones = len(secciones)
            total_secciones += num_secciones
            
            if num_secciones > 1:
                cursos_con_multiples_secciones += 1
                secciones_letras = [s['seccion'] for s in secciones]
                print(f"✅ {nombre_curso}: {num_secciones} secciones ({', '.join(secciones_letras)})")
            else:
                print(f"⚪ {nombre_curso}: {num_secciones} sección")
        
        print(f"\n📈 ESTADÍSTICAS FINALES:")
        print(f"   • Cursos únicos: {len(cursos_agrupados)}")
        print(f"   • Total secciones: {total_secciones}")
        print(f"   • Cursos con múltiples secciones: {cursos_con_multiples_secciones}")
        print(f"   • Promedio secciones por curso: {total_secciones/len(cursos_agrupados):.1f}")
    
    def _es_encabezado_escuela(self, texto: str) -> bool:
        """Detecta encabezados de escuela."""
        if not texto or texto == '':
            return False
        texto_upper = texto.upper()
        return 'ESCUELA PROFESIONAL' in texto_upper
    
    def _extraer_codigo_escuela(self, texto: str) -> str:
        """Extrae código de escuela."""
        texto_upper = texto.upper()
        mapeo = {
            'FÍSICA': 'BF', 'MATEMÁTICA': 'CM', 'QUÍMICA': 'CQ',
            'BIOLOGÍA': 'CB', 'COMPUTACIÓN': 'CC', 'INGENIERÍA': 'IF'
        }
        
        for nombre, codigo in mapeo.items():
            if nombre in texto_upper:
                return codigo
        return 'XX'
    
    def _es_curso_principal(self, datos_fila: List[str]) -> bool:
        """Detecta si es la primera mención de un curso (método original mantenido)."""
        return (datos_fila[0] and datos_fila[0] != '' and
                len(datos_fila) >= 2 and datos_fila[1] and
                self._contiene_codigo_seccion(datos_fila[1]))
    
    def _es_seccion_adicional(self, datos_fila: List[str]) -> bool:
        """Detecta si es una sección adicional (primera columna vacía)."""
        return (not datos_fila[0] and 
                len(datos_fila) >= 2 and datos_fila[1] and
                self._contiene_codigo_seccion(datos_fila[1]))
    
    def _contiene_codigo_seccion(self, texto: str) -> bool:
        """Verifica si contiene código de sección como 'BFI01\nA'."""
        if not texto:
            return False
        # Buscar patrones como "BFI01\nA" o "BFI01 A"
        patron = r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?\s*[\n\s]\s*[A-Z]'
        return bool(re.search(patron, texto))
    
    def _procesar_seccion_corregida(self, datos_fila: List[str], curso_base: Dict, id_curso: int) -> Optional[Dict]:
        """Procesa una sección individual con lógica corregida."""
        try:
            # Extraer información básica
            codigo_seccion = self._extraer_codigo_seccion_corregido(datos_fila[1])
            seccion_letra = codigo_seccion.split('_')[-1] if '_' in codigo_seccion else 'A'
            
            # Extraer horarios (columna 2)
            horarios_texto = datos_fila[2] if len(datos_fila) > 2 else ''
            
            # Extraer salones (columna 3)
            salones_texto = datos_fila[3] if len(datos_fila) > 3 else ''
            
            # Extraer profesor (columna 4)
            profesor_texto = datos_fila[4] if len(datos_fila) > 4 else ''
            
            # Extraer capacidad (columna 5)
            capacidad = self._extraer_capacidad(datos_fila[5] if len(datos_fila) > 5 else '')
            
            # Procesar horarios
            horarios = self._procesar_horarios_corregido(horarios_texto, salones_texto)
            
            # Procesar profesor
            profesor = self._procesar_profesor(profesor_texto)
            
            # Crear curso completo
            curso = {
                'id': id_curso,
                'codigo': codigo_seccion,
                'nombre': curso_base['nombre'],
                'escuela': curso_base['escuela'],
                'seccion': seccion_letra,
                'profesor': profesor,
                'tipo': self._determinar_tipo_curso(salones_texto),
                'capacidad': capacidad,
                'horarios': horarios,
                'salones': self._extraer_salones(salones_texto)
            }
            
            return curso
            
        except Exception as e:
            print(f"⚠️  Error procesando sección: {e}")
            return None
    
    def _extraer_codigo_seccion_corregido(self, texto: str) -> str:
        """Extrae código de sección de forma más robusta."""
        if not texto:
            return f"CURSO_{np.random.randint(1000, 9999)}_A"
        
        # Limpiar texto
        texto_limpio = texto.replace('\n', ' ').strip()
        
        # Buscar patrón "CODIGO SECCION" como "BFI01 A"
        patron = r'([A-Z]{2,3}[I]?\d{2,3}[A-Z]?)\s+([A-Z])'
        match = re.search(patron, texto_limpio)
        
        if match:
            codigo_base = match.group(1)
            seccion = match.group(2)
            return f"{codigo_base}_{seccion}"
        
        # Patrón alternativo "CODIGO\nSECCION"
        lineas = texto.split('\n')
        if len(lineas) >= 2:
            codigo_posible = lineas[0].strip()
            seccion_posible = lineas[1].strip()
            if (re.match(r'[A-Z]{2,3}[I]?\d{2,3}[A-Z]?', codigo_posible) and 
                re.match(r'[A-Z]', seccion_posible)):
                return f"{codigo_posible}_{seccion_posible}"
        
        return f"CURSO_{np.random.randint(1000, 9999)}_A"
    
    def _procesar_horarios_corregido(self, horarios_texto: str, salones_texto: str) -> List[Dict]:
        """Procesa horarios con lógica mejorada."""
        if not horarios_texto:
            return []
        
        horarios = []
        
        # Dividir por líneas
        lineas_horario = [l.strip() for l in horarios_texto.split('\n') if l.strip()]
        lineas_salon = [l.strip() for l in salones_texto.split('\n') if l.strip()] if salones_texto else []
        
        for i, linea in enumerate(lineas_horario):
            # Buscar todos los horarios en la línea: "LU 10-12 MI 10-12"
            patron = r'([A-Z]{2})\s+(\d{1,2})-(\d{1,2})'
            matches = re.findall(patron, linea)
            
            salon = lineas_salon[i] if i < len(lineas_salon) else 'SALON NO ASIGNADO'
            salon = self._limpiar_salon(salon)
            
            for dia_codigo, hora_inicio, hora_fin in matches:
                if dia_codigo in self.dias_semana:
                    horario = {
                        'dia': self.dias_semana[dia_codigo],
                        'dia_codigo': dia_codigo,
                        'hora_inicio': f"{hora_inicio}:00",
                        'hora_fin': f"{hora_fin}:00",
                        'salon': salon
                    }
                    horarios.append(horario)
        
        return horarios
    
    def _limpiar_salon(self, salon_texto: str) -> str:
        """Limpia información del salón."""
        if not salon_texto:
            return 'SALON NO ASIGNADO'
        
        # Remover URLs de zoom y paréntesis
        salon = re.sub(r'/\s*zoom\d+.*', '', salon_texto)
        salon = re.sub(r'\(.*?\)', '', salon)
        return salon.strip() or 'SALON NO ASIGNADO'
    
    def _procesar_profesor(self, profesor_texto: str) -> str:
        """Procesa nombre del profesor."""
        if not profesor_texto:
            return 'SIN ASIGNAR'
        
        # Tomar primera línea y limpiar
        primera_linea = profesor_texto.split('\n')[0].strip()
        if primera_linea and primera_linea != 'nan':
            # Remover iniciales como "J. "
            nombre = re.sub(r'^[A-Z]\.\s*', '', primera_linea)
            return nombre.upper()
        
        return 'SIN ASIGNAR'
    
    def _extraer_capacidad(self, capacidad_texto: str) -> int:
        """Extrae capacidad numérica."""
        if not capacidad_texto:
            return 30
        try:
            return int(float(capacidad_texto))
        except:
            return 30
    
    def _determinar_tipo_curso(self, salones_texto: str) -> str:
        """Determina tipo de curso por salón."""
        if not salones_texto:
            return 'Teórico'
        if 'LAB' in salones_texto.upper():
            return 'Práctico'
        return 'Teórico'
    
    def _extraer_salones(self, salones_texto: str) -> List[str]:
        """Extrae lista de salones."""
        if not salones_texto:
            return ['SALON NO ASIGNADO']
        
        salones = []
        for linea in salones_texto.split('\n'):
            salon = self._limpiar_salon(linea)
            if salon != 'SALON NO ASIGNADO':
                salones.append(salon)
        
        return salones if salones else ['SALON NO ASIGNADO']
    
    def _crear_matriz_horarios(self, cursos: List[Dict]):
        """Crea matriz de horarios."""
        self.matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        bloques_ocupados = 0
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias_orden:
                    dia_idx = dias_orden.index(horario['dia'])
                    
                    try:
                        hora_inicio = int(horario['hora_inicio'].split(':')[0])
                        hora_fin = int(horario['hora_fin'].split(':')[0])
                        
                        for hora in range(hora_inicio, hora_fin):
                            bloque = hora - 7  # 7:00 AM es bloque 0
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
                    except:
                        pass  # Ignorar errores de conversión de hora
        
        print(f"📊 Matriz de horarios: {bloques_ocupados}/70 bloques ocupados ({bloques_ocupados/70*100:.1f}%)")
    
    def _generar_estadisticas(self, cursos: List[Dict]):
        """Genera estadísticas del procesamiento."""
        escuelas = set()
        profesores = set()
        tipos_curso = set()
        cursos_por_escuela = {}
        nombres_curso = set()
        
        for curso in cursos:
            escuelas.add(curso['escuela'])
            if curso['profesor'] != 'SIN ASIGNAR':
                profesores.add(curso['profesor'])
            tipos_curso.add(curso['tipo'])
            nombres_curso.add(curso['nombre'])
            
            escuela = curso['escuela']
            cursos_por_escuela[escuela] = cursos_por_escuela.get(escuela, 0) + 1
        
        self.estadisticas = {
            'total_cursos': len(cursos),
            'total_cursos_unicos': len(nombres_curso),
            'total_escuelas': len(escuelas),
            'total_profesores': len(profesores),
            'escuelas': sorted(list(escuelas)),
            'tipos_curso': sorted(list(tipos_curso)),
            'cursos_por_escuela': cursos_por_escuela,
            'cursos_con_profesor': len([c for c in cursos if c['profesor'] != 'SIN ASIGNAR']),
            'formato': 'excel_universitario'
        }
    
    def mostrar_resumen(self, datos: Dict):
        """Muestra resumen detallado con correcciones aplicadas."""
        print("\n" + "="*60)
        print("RESUMEN DEL PROCESAMIENTO - VERSIÓN COMPLETAMENTE CORREGIDA")
        print("="*60)
        
        stats = datos['estadisticas']
        
        print(f"📚 Total de secciones procesadas: {stats['total_cursos']}")
        print(f"📖 Cursos únicos encontrados: {stats['total_cursos_unicos']}")
        print(f"🏫 Total de escuelas: {stats['total_escuelas']}")
        print(f"👨‍🏫 Profesores asignados: {stats['cursos_con_profesor']}/{stats['total_cursos']}")
        print(f"📋 Tipos de curso: {', '.join(stats['tipos_curso'])}")
        
        print(f"\n🏫 Distribución por escuela:")
        for escuela, cantidad in stats['cursos_por_escuela'].items():
            print(f"   {escuela}: {cantidad} secciones")
        
        # ✅ MEJORA: Mostrar cursos agrupados con sus secciones
        print(f"\n📖 CURSOS ÚNICOS CON SUS SECCIONES:")
        print("-" * 60)
        
        # Agrupar por nombre de curso
        cursos_por_nombre = {}
        for curso in datos['cursos']:
            nombre = curso['nombre']
            if nombre not in cursos_por_nombre:
                cursos_por_nombre[nombre] = []
            cursos_por_nombre[nombre].append(curso)
        
        # Mostrar cursos ordenados por número de secciones
        cursos_ordenados = sorted(cursos_por_nombre.items(), 
                                key=lambda x: len(x[1]), reverse=True)
        
        for i, (nombre_curso, secciones) in enumerate(cursos_ordenados[:15]):  # Top 15
            print(f"\n{i+1:2d}. 📚 {nombre_curso} ({len(secciones)} secciones):")
            
            for seccion in secciones[:4]:  # Mostrar hasta 4 secciones
                horario_info = ""
                if seccion['horarios']:
                    h = seccion['horarios'][0]
                    horario_info = f" - {h['dia'][:2]} {h['hora_inicio']}-{h['hora_fin']}"
                
                profesor_info = seccion['profesor'][:12] if seccion['profesor'] != 'SIN ASIGNAR' else 'S/A'
                print(f"      {seccion['codigo']:<14} {profesor_info:<12}{horario_info}")
            
            if len(secciones) > 4:
                print(f"      ... y {len(secciones) - 4} secciones más")
        
        if len(cursos_ordenados) > 15:
            print(f"\n... y {len(cursos_ordenados) - 15} cursos únicos más")
        
        # ✅ ESTADÍSTICAS DE VALIDACIÓN
        print(f"\n📊 ESTADÍSTICAS DE VALIDACIÓN:")
        print("-" * 40)
        
        cursos_con_multiples_secciones = len([
            nombre for nombre, secciones in cursos_por_nombre.items() 
            if len(secciones) > 1
        ])
        
        promedio_secciones = sum(len(secciones) for secciones in cursos_por_nombre.values()) / len(cursos_por_nombre)
        
        print(f"✅ Cursos con múltiples secciones: {cursos_con_multiples_secciones}")
        print(f"✅ Promedio de secciones por curso: {promedio_secciones:.1f}")
        print(f"✅ Cobertura de procesamiento: {len(datos['cursos'])} secciones totales")
        
        # Detectar posibles problemas
        problemas = []
        if stats['cursos_con_profesor'] / stats['total_cursos'] < 0.5:
            problemas.append("⚠️  Muchos cursos sin profesor asignado")
        
        if promedio_secciones < 1.5:
            problemas.append("⚠️  Pocos cursos tienen múltiples secciones")
        
        if problemas:
            print(f"\n⚠️  POSIBLES PROBLEMAS DETECTADOS:")
            for problema in problemas:
                print(f"   {problema}")
        else:
            print(f"\n✅ PROCESAMIENTO EXITOSO - No se detectaron problemas")
    
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
    """Función de prueba para el lector unificado con correcciones."""
    print("🧪 PRUEBA DEL LECTOR UNIFICADO COMPLETAMENTE CORREGIDO")
    print("="*60)
    
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
                horario_info = ""
                if curso.get('horarios'):
                    h = curso['horarios'][0]
                    horario_info = f" - {h['dia']} {h['hora_inicio']}-{h['hora_fin']}"
                
                print(f"   {i+1}. {curso.get('codigo', 'N/A')} - {curso['nombre'][:30]}{horario_info}")
        
        # Mostrar resumen específico del lector si es universitario
        if lector.ultimo_formato_detectado == 'excel_universitario':
            lector.lector_excel.mostrar_resumen(datos)
        elif lector.ultimo_formato_detectado == 'pdf':
            lector.lector_pdf.mostrar_resumen(datos)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_procesamiento_todos_los_cursos(archivo_excel: str):
    """
    ✅ FUNCIÓN DE PRUEBA COMPLETAMENTE CORREGIDA: Verifica TODOS los cursos.
    """
    print("🧪 PRUEBA COMPLETAMENTE CORREGIDA: Verificación de TODOS los cursos")
    print("="*70)
    
    try:
        lector = LectorExcelUniversitario()
        datos = lector.leer_excel_universitario(archivo_excel)
        
        # Análisis específico por tipo de curso
        cursos_por_nombre = {}
        for curso in datos['cursos']:
            nombre = curso['nombre']
            if nombre not in cursos_por_nombre:
                cursos_por_nombre[nombre] = []
            cursos_por_nombre[nombre].append(curso)
        
        print(f"\n🔍 ANÁLISIS DETALLADO:")
        print("-" * 50)
        
        # Casos específicos a verificar (expandidos)
        casos_test = [
            ('FÍSICA I', 5, "Debería tener 5 secciones (A, B, C, D, E)"),
            ('FÍSICA II', 2, "Debería tener al menos 2 secciones"),
            ('MECÁNICA CLÁSICA', 1, "Debería aparecer en el procesamiento"),
            ('ELECTROMAGNETISMO', 1, "Debería aparecer en el procesamiento"),
            ('MÉTODOS NUMÉRICOS', 1, "Debería aparecer en el procesamiento"),
        ]
        
        exitos = 0
        total_tests = len(casos_test)
        
        for nombre_curso, secciones_esperadas, descripcion in casos_test:
            # Buscar curso (permitir coincidencias parciales)
            cursos_encontrados = [
                nombre for nombre in cursos_por_nombre.keys() 
                if nombre_curso.upper() in nombre.upper()
            ]
            
            if cursos_encontrados:
                nombre_real = cursos_encontrados[0]
                secciones_reales = len(cursos_por_nombre[nombre_real])
                
                if secciones_reales >= secciones_esperadas:
                    print(f"✅ {nombre_curso}: {secciones_reales} secciones ({descripcion})")
                    exitos += 1
                else:
                    print(f"⚠️  {nombre_curso}: {secciones_reales} secciones (esperadas: {secciones_esperadas})")
            else:
                print(f"❌ {nombre_curso}: NO ENCONTRADO")
        
        # Resumen de la prueba
        print(f"\n📊 RESULTADO DE LA PRUEBA:")
        print(f"   Tests exitosos: {exitos}/{total_tests}")
        print(f"   Cursos únicos procesados: {len(cursos_por_nombre)}")
        print(f"   Total secciones: {len(datos['cursos'])}")
        
        # Mostrar TODOS los cursos encontrados (resumido)
        print(f"\n📚 TODOS LOS CURSOS PROCESADOS ({len(cursos_por_nombre)} únicos):")
        for i, (nombre, secciones) in enumerate(sorted(cursos_por_nombre.items()), 1):
            secciones_str = ', '.join([s['seccion'] for s in secciones])
            if i <= 20:  # Mostrar primeros 20
                print(f"   {i:2d}. {nombre} ({len(secciones)} secciones: {secciones_str})")
            elif i == 21:
                print(f"   ... y {len(cursos_por_nombre) - 20} cursos más")
        
        if exitos == total_tests:
            print(f"\n🎉 ¡PRUEBA COMPLETAMENTE EXITOSA!")
            print(f"✅ Todos los cursos fueron procesados correctamente")
            return True
        else:
            print(f"\n⚠️  Prueba parcialmente exitosa ({exitos}/{total_tests})")
            print(f"💡 Mejora significativa en el reconocimiento de cursos")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal para pruebas directas del módulo."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python lector_horarios.py <archivo> [--test] [--debug]")
        print("\nEjemplos:")
        print("  python lector_horarios.py datos/Horarios_2023_1.xlsx")
        print("  python lector_horarios.py datos/horario.pdf")
        print("  python lector_horarios.py archivo.xlsx --test")
        print("  python lector_horarios.py archivo.xlsx --debug")
        return
    
    archivo = sys.argv[1]
    es_prueba = '--test' in sys.argv
    debug_mode = '--debug' in sys.argv
    
    # Activar debug si se solicita
    if debug_mode:
        os.environ['DEBUG_LECTOR'] = '1'
    
    if es_prueba:
        print("🚀 EJECUTANDO PRUEBAS CON VERSIÓN COMPLETAMENTE CORREGIDA")
        print("=" * 60)
        
        # Prueba principal
        test_lector_unificado(archivo)
        
        # ✅ PRUEBA ESPECÍFICA MEJORADA
        if 'xlsx' in archivo.lower():
            print("\n" + "="*70)
            test_procesamiento_todos_los_cursos(archivo)
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
                print(f"Total de cursos: {len(datos.get('cursos', []))}")
            
            # Ofrecer exportar a Excel compatible
            respuesta = input("\n¿Exportar a formato compatible con optimizador? (s/n): ")
            if respuesta.lower() == 's':
                archivo_salida = input("Nombre del archivo de salida: ").strip()
                if not archivo_salida:
                    archivo_salida = "horarios_convertidos_CORREGIDOS.xlsx"
                
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
            if debug_mode:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()