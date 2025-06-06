#!/usr/bin/env python3
"""
Lector PDF específico para el formato de tabla de horarios UNMSM.
Diseñado para procesar el formato exacto del PDF Horarios_2023_1.pdf

REEMPLAZAR: core/lector_pdf_horarios.py
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF


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
        """Lee el PDF extrayendo texto y procesando como tabla."""
        try:
            doc = fitz.open(archivo_pdf)
            
            print("🔍 Extrayendo y analizando contenido del PDF...")
            
            # Extraer todo el texto
            texto_completo = ""
            for page_num, page in enumerate(doc):
                texto_pagina = page.get_text()
                texto_completo += texto_pagina + "\n"
                print(f"   Página {page_num + 1}: {len(texto_pagina)} caracteres")
            
            doc.close()
            print(f"📝 Total extraído: {len(texto_completo)} caracteres")
            
            # Procesar el texto para extraer la información de la tabla
            cursos = self._procesar_tabla_horarios(texto_completo)
            
            # Crear matriz de horarios
            self.crear_matriz_horarios(cursos)
            
            return {
                'cursos': cursos,
                'matriz_horarios': self.matriz_horarios,
                'estadisticas': self.generar_estadisticas(cursos)
            }
            
        except Exception as e:
            raise Exception(f"Error al leer el PDF: {str(e)}")
    
    def _procesar_tabla_horarios(self, texto: str) -> List[Dict]:
        """Procesa el texto extraído para formar una tabla de horarios."""
        cursos = []
        lineas = texto.split('\n')
        
        print("🔄 Analizando estructura de tabla de horarios...")
        
        # Variables para rastrear el contexto
        nombre_curso_actual = None
        codigo_base_actual = None
        capacidad_actual = 30
        id_contador = 1
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            
            if not linea:
                i += 1
                continue
            
            # Debug: Mostrar líneas procesadas
            if len(linea) > 5:
                print(f"   Analizando: {linea[:50]}...")
            
            # 1. Detectar nombres de cursos
            if self._es_nombre_curso_tabla(linea):
                nombre_curso_actual = linea
                print(f"   📚 Curso encontrado: {nombre_curso_actual}")
                i += 1
                continue
            
            # 2. Detectar códigos de curso
            if self._es_codigo_curso_simple(linea):
                codigo_base_actual = linea.strip()
                print(f"   🔤 Código encontrado: {codigo_base_actual}")
                i += 1
                continue
            
            # 3. CLAVE: Detectar líneas con información de horarios y secciones
            # Buscar líneas que contengan horarios (LU 10-12, MA 08-10, etc.)
            if self._contiene_informacion_horarios(linea):
                print(f"   🕐 Línea con horarios detectada: {linea[:60]}...")
                
                # Procesar esta línea y posiblemente las siguientes para formar una sección completa
                seccion_data = self._extraer_seccion_de_bloque(
                    lineas, i, codigo_base_actual, nombre_curso_actual, capacidad_actual
                )
                
                if seccion_data:
                    for seccion in seccion_data:
                        seccion['id'] = id_contador
                        cursos.append(seccion)
                        print(f"     ✅ Sección procesada: {seccion['codigo']} con {len(seccion['horarios'])} horarios")
                        id_contador += 1
            
            i += 1
        
        print(f"✅ Total de secciones procesadas: {len(cursos)}")
        return cursos
    
    def _es_nombre_curso_tabla(self, linea: str) -> bool:
        """Detecta nombres de cursos en el formato de tabla del PDF."""
        # Los nombres aparecen como líneas en mayúsculas, sin horarios, con palabras clave
        return (len(linea) > 8 and 
                linea.isupper() and
                not re.search(r'\d{1,2}[-:]\d{1,2}', linea) and  # No contiene horarios
                not re.search(r'^[A-Z]{2,4}\d+', linea) and     # No es código
                not linea.startswith('ESCUELA') and
                not linea.startswith('CURSOS') and
                # Palabras clave que indican nombres de cursos
                any(palabra in linea for palabra in [
                    'FÍSICA', 'MATEMÁTICA', 'QUÍMICA', 'COMPUTACIÓN', 
                    'LABORATORIO', 'PROYECTO', 'CÁLCULO', 'ÁLGEBRA',
                    'ANÁLISIS', 'ÓPTICA', 'MECÁNICA', 'ELECTROMAGNETISMO',
                    'TESIS', 'PROGRAMACIÓN', 'ALGORITMOS', 'BASE DE DATOS'
                ]))
    
    def _es_codigo_curso_simple(self, linea: str) -> bool:
        """Detecta códigos de curso como líneas independientes."""
        return bool(re.match(r'^[A-Z]{2,4}\d{1,3}[A-Z]?\d?$', linea.strip()))
    
    def _contiene_informacion_horarios(self, linea: str) -> bool:
        """Detecta líneas que contienen información de horarios."""
        # Buscar patrones de horarios en la línea
        tiene_horarios = bool(re.search(r'[A-Z]{2}\s+\d{1,2}[-:]\d{1,2}', linea))
        
        # También buscar patrones que indican información de curso
        tiene_seccion = bool(re.search(r'\b[A-E]\b', linea))
        tiene_salon = bool(re.search(r'(R\d+[-]\d+|LAB\s*[A-Z]|J\d+[-]\d+|SALA)', linea))
        
        return tiene_horarios and (tiene_seccion or tiene_salon)
    
    def _extraer_seccion_de_bloque(self, lineas: List[str], indice_inicio: int, 
                                  codigo_base: str, nombre_curso: str, capacidad: int) -> List[Dict]:
        """Extrae información de sección de un bloque de líneas."""
        secciones = []
        
        # Procesar líneas desde el índice actual
        linea_actual = lineas[indice_inicio].strip()
        
        # Buscar todas las secciones en esta línea y posibles líneas siguientes
        texto_bloque = linea_actual
        
        # Revisar líneas siguientes para información adicional de la misma sección
        for j in range(indice_inicio + 1, min(indice_inicio + 5, len(lineas))):
            linea_siguiente = lineas[j].strip()
            
            # Si la línea siguiente tiene horarios pero no código/nombre nuevo, es continuación
            if (self._contiene_informacion_horarios(linea_siguiente) and 
                not self._es_codigo_curso_simple(linea_siguiente) and
                not self._es_nombre_curso_tabla(linea_siguiente)):
                texto_bloque += " " + linea_siguiente
            else:
                break
        
        # Extraer secciones del bloque de texto
        secciones_encontradas = self._extraer_secciones_del_texto(
            texto_bloque, codigo_base, nombre_curso, capacidad
        )
        
        return secciones_encontradas
    
    def _extraer_secciones_del_texto(self, texto: str, codigo_base: str, 
                                   nombre_curso: str, capacidad: int) -> List[Dict]:
        """Extrae todas las secciones de un bloque de texto."""
        secciones = []
        
        # Buscar todas las secciones (A, B, C, D, E) en el texto
        secciones_matches = re.finditer(r'\b([A-E])\b', texto)
        
        for match_seccion in secciones_matches:
            seccion = match_seccion.group(1)
            
            # Para cada sección, buscar los horarios cercanos
            horarios = self._extraer_horarios_para_seccion(texto, match_seccion)
            
            if horarios:
                codigo_completo = f"{codigo_base}_{seccion}" if codigo_base else f"UNK_{seccion}"
                
                seccion_info = {
                    'id': 0,  # Se asignará después
                    'codigo': codigo_completo,
                    'codigo_base': codigo_base or 'UNK',
                    'nombre': nombre_curso or self._generar_nombre_desde_codigo(codigo_base or 'UNK'),
                    'seccion': seccion,
                    'horarios': horarios,
                    'profesor': self._extraer_profesor_principal_texto(texto),
                    'capacidad': capacidad,
                    'tipo': 'Práctico' if any('LAB' in h.get('salon', '') for h in horarios) else 'Teórico',
                    'escuela': codigo_base[:2] if codigo_base and len(codigo_base) >= 2 else 'XX'
                }
                secciones.append(seccion_info)
        
        return secciones
    
    def _extraer_horarios_para_seccion(self, texto: str, match_seccion) -> List[Dict]:
        """Extrae horarios específicos para una sección."""
        horarios = []
        
        # Buscar horarios en el texto
        patron_horario = r'([A-Z]{2})\s+(\d{1,2})[-:](\d{1,2})'
        horarios_matches = list(re.finditer(patron_horario, texto))
        
        # Buscar salones
        patron_salon = r'([A-Z]\d+[-/][A-Z0-9]+|LAB\s*[A-Z0-9]*|SALA\s*\d+|R\d+[-]\d+[A-Z]?|J\d+[-]\d+[A-Z]*)'
        salones_matches = list(re.finditer(patron_salon, texto))
        
        # Buscar profesores
        patron_profesor = r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b'
        profesores_matches = list(re.finditer(patron_profesor, texto))
        
        # Para cada horario encontrado, crear entrada
        for match_horario in horarios_matches:
            dia = match_horario.group(1)
            hora_inicio = match_horario.group(2).zfill(2)
            hora_fin = match_horario.group(3).zfill(2)
            
            # Buscar salón más cercano
            salon = self._buscar_mas_cercano(match_horario, salones_matches, 'salon')
            
            # Buscar profesor más cercano
            profesor = self._buscar_mas_cercano(match_horario, profesores_matches, 'profesor')
            
            horario_info = {
                'dia': self.dias_semana.get(dia, dia),
                'dia_corto': dia,
                'hora_inicio': f"{hora_inicio}:00",
                'hora_fin': f"{hora_fin}:00",
                'salon': salon or 'SIN ASIGNAR',
                'profesor': profesor or 'SIN ASIGNAR',
                'bloque_idx': self._hora_a_bloque(f"{hora_inicio}:00")
            }
            horarios.append(horario_info)
        
        return horarios
    
    def _buscar_mas_cercano(self, match_referencia, matches_elementos, tipo: str) -> str:
        """Busca el elemento más cercano al match de referencia."""
        pos_referencia = match_referencia.start()
        mejor_elemento = None
        menor_distancia = float('inf')
        
        for match_elemento in matches_elementos:
            elemento = match_elemento.group(1)
            
            # Filtrar elementos inválidos según el tipo
            if not self._es_elemento_valido(elemento, tipo):
                continue
            
            # Calcular distancia
            distancia = abs(match_elemento.start() - pos_referencia)
            if distancia < menor_distancia:
                menor_distancia = distancia
                mejor_elemento = elemento
        
        return mejor_elemento
    
    def _es_elemento_valido(self, elemento: str, tipo: str) -> bool:
        """Verifica si un elemento es válido según su tipo."""
        if tipo == 'salon':
            return (len(elemento) >= 2 and 
                   elemento not in ['LU', 'MA', 'MI', 'JU', 'VI', 'SA', 'DO'])
        elif tipo == 'profesor':
            return (len(elemento) >= 3 and 
                   elemento not in ['LAB', 'SALA', 'ZOOM', 'LU', 'MA', 'MI', 'JU', 'VI', 'SA', 'DO'] and
                   not re.match(r'^[A-Z]\d+', elemento) and
                   not elemento.isdigit())
        return False
    
    def _extraer_profesor_principal_texto(self, texto: str) -> str:
        """Extrae el profesor principal del texto."""
        # Buscar nombres al final del texto
        patron = r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})?)\s*$'
        match = re.search(patron, texto)
        if match:
            nombre = match.group(1)
            if self._es_elemento_valido(nombre, 'profesor'):
                return nombre
        
        # Buscar cualquier nombre válido
        patron_general = r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})?)\b'
        nombres = re.findall(patron_general, texto)
        for nombre in nombres:
            if self._es_elemento_valido(nombre, 'profesor'):
                return nombre
        
        return 'SIN ASIGNAR'
    
    def _generar_nombre_desde_codigo(self, codigo: str) -> str:
        """Genera nombre de curso desde código."""
        mapeo_nombres = {
            # Física
            'BFI01': 'FÍSICA I',
            'CF1B2': 'FÍSICA II', 
            'CF2B1': 'FÍSICA III',
            'CF1C2': 'ÓPTICA CLÁSICA',
            'CF2C1': 'ÁLGEBRA LINEAL PARA FÍSICOS I',
            'CF2C2': 'MÉTODOS MATEMÁTICOS PARA FÍSICOS I',
            'CF3F1': 'MECÁNICA CLÁSICA',
            'CF3F2': 'MECÁNICA CUÁNTICA I',
            'CF3F3': 'FÍSICA MODERNA',
            'CF3C1': 'MÉTODOS MATEMÁTICOS PARA FÍSICOS II',
            'CF3F4': 'ELECTROMAGNETISMO I',
            'CF4F1': 'TERMODINÁMICA Y MECÁNICA ESTADÍSTICA',
            'CF4F2': 'FÍSICA ATÓMICA Y MOLECULAR',
            'CF4F3': 'MECÁNICA CUÁNTICA II',
            'CF5F1': 'FÍSICA DEL ESTADO SÓLIDO I',
            'CF5F3': 'FÍSICA NUCLEAR Y DE PARTÍCULAS',
            'CF4E1': 'LABORATORIO DE FÍSICA INTERMEDIA',
            'CF4E2': 'LABORATORIO DE FÍSICA AVANZADA',
            
            # Matemática
            'BMA01': 'CÁLCULO DIFERENCIAL',
            'BMA02': 'CÁLCULO INTEGRAL',
            'BMA03': 'ÁLGEBRA LINEAL',
            'CM1A2': 'LÓGICA Y TEORÍA DE CONJUNTOS',
            'CM1H2': 'CÁLCULO DE PROBABILIDADES',
            'CM2H1': 'MATEMÁTICA DISCRETA',
            'CM2F1': 'PROGRAMACIÓN ESTRUCTURADA',
            'CM2A1': 'CÁLCULO DIFERENCIAL E INTEGRAL AVANZADO',
            'CM2A2': 'ANÁLISIS REAL',
            'CM2H2': 'ESTADÍSTICA INFERENCIAL',
            
            # Química
            'BQU01': 'QUÍMICA I',
            'CQ132': 'QUÍMICA CIENCIA Y TECNOLOGÍA',
            'CQ102': 'QUÍMICA EXPERIMENTAL',
            'CQ261': 'ELEMENTOS QUÍMICOS',
            'CQ271': 'HIDROCARBUROS ALIFÁTICOS',
            'CQ242': 'PRINCIPIOS DE FISICOQUÍMICA',
            'CQ221': 'ESTRUCTURA QUÍMICA Y REACTIVIDAD',
            'CQ241': 'INTRODUCCIÓN A LA ELECTRICIDAD Y MAGNETISMO',
            
            # Computación
            'BIC01': 'INTRODUCCIÓN A LA COMPUTACIÓN',
            'CC112': 'FUNDAMENTOS DE PROGRAMACIÓN',
            'CC211': 'PROGRAMACIÓN ORIENTADA A OBJETOS',
            'CC221': 'ARQUITECTURA DE COMPUTADORES',
            'CC222': 'SISTEMAS OPERATIVOS',
            'CC232': 'ALGORITMOS Y ESTRUCTURAS DE DATOS',
            'CC202': 'BASE DE DATOS',
            
            # Ingeniería Física
            'IF242': 'INTRODUCCIÓN A LA METROLOGÍA',
            'IF3A2': 'INGENIERÍA ECONÓMICA',
            'IF281': 'DIBUJO Y DISEÑO PARA INGENIERÍA',
            'IF252': 'MÉTODOS MATEMÁTICOS PARA INGENIERÍA',
            'IF292': 'INGENIERÍA DE PROCESOS MECÁNICOS'
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
        elif prefijo == 'IF':
            return 'INGENIERÍA FÍSICA'
        elif prefijo in ['BR', 'BE']:
            return 'ESTUDIOS GENERALES'
        else:
            return f'CURSO {codigo}'
    
    def _hora_a_bloque(self, hora_str: str) -> int:
        """Convierte hora a índice de bloque."""
        try:
            hora = int(hora_str.split(':')[0])
            return max(0, hora - 7)
        except:
            return 0
    
    def crear_matriz_horarios(self, cursos: List[Dict]):
        """Crea la matriz de horarios compatible con el optimizador."""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.matriz_horarios = [[None for _ in range(14)] for _ in range(5)]
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias:
                    dia_idx = dias.index(horario['dia'])
                    bloque_inicio = horario['bloque_idx']
                    
                    # Calcular duración
                    try:
                        inicio = int(horario['hora_inicio'].split(':')[0])
                        fin = int(horario['hora_fin'].split(':')[0])
                        duracion = fin - inicio
                    except:
                        duracion = 1
                    
                    # Asignar a los bloques
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
        """Exporta a Excel en el formato requerido."""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{7+i}:00 - {8+i}:00" for i in range(14)]
        
        df = pd.DataFrame(index=horas, columns=dias)
        
        for dia_idx, dia in enumerate(dias):
            for bloque in range(14):
                if self.matriz_horarios[dia_idx][bloque]:
                    curso = self.matriz_horarios[dia_idx][bloque]
                    # Formato específico: "id|nombre|profesor|tipo"
                    celda = f"{curso['id']}|{curso['nombre']}|{curso['profesor']}|{curso['tipo']}"
                    df.iloc[bloque, dia_idx] = celda
        
        df.to_excel(archivo_salida)
        print(f"📊 Archivo Excel generado: {archivo_salida}")
    
    def mostrar_resumen(self, datos: Dict):
        """Muestra resumen detallado."""
        print("\n" + "="*60)
        print("RESUMEN DE PROCESAMIENTO DEL PDF")
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
        print("Uso: python lector_pdf_horarios.py <archivo.pdf> [archivo_salida.xlsx]")
        return
    
    archivo_pdf = sys.argv[1]
    archivo_excel = sys.argv[2] if len(sys.argv) > 2 else "horarios_unmsm_procesados.xlsx"
    
    try:
        print(f"🚀 Procesando PDF UNMSM con enfoque de tabla: {archivo_pdf}")
        
        lector = LectorPDFHorarios()
        datos = lector.leer_pdf(archivo_pdf)
        
        lector.mostrar_resumen(datos)
        lector.exportar_a_excel(datos['cursos'], archivo_excel)
        
        print(f"\n✅ Proceso completado!")
        print(f"📊 Archivo Excel: {archivo_excel}")
        print(f"🎯 Comando para optimizar:")
        print(f"     python scripts/optimizar.py {archivo_excel}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()