#!/usr/bin/env python3
"""
Módulo para leer archivos PDF con horarios académicos y convertirlos 
al formato requerido por el optimizador.
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
                'estadisticas': self.generar_estadisticas(cursos)
            }
            
        except Exception as e:
            raise Exception(f"Error al leer el PDF: {str(e)}")
    
    def procesar_texto_pdf(self, texto: str) -> List[Dict]:
        """
        Procesa el texto extraído del PDF y extrae información de cursos.
        """
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
                partes = linea.split()
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
        """
        Extrae el nombre del curso buscando en líneas cercanas.
        """
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
        """
        Extrae información del salón de la línea.
        """
        # Buscar patrones como R1-450, J3-182A, LAB F, etc.
        patron_salon = r'([A-Z]+\d*[-\w]*|LAB\s*[A-Z0-9]*)'
        match = re.search(patron_salon, linea)
        return match.group(1) if match else ""
    
    def extraer_profesor(self, linea: str) -> str:
        """
        Extrae el nombre del profesor de la línea.
        """
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
        """
        Crea una matriz de horarios similar al formato Excel original.
        """
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
        """
        Convierte una hora en formato HH:MM a índice de bloque.
        Asume que los bloques empiezan a las 7:00 AM.
        """
        try:
            hora, minuto = map(int, hora_str.split(':'))
            # Calcular bloque (cada bloque es de 1 hora, empezando a las 7:00)
            bloque = hora - 7
            return max(0, bloque)
        except:
            return 0
    
    def generar_estadisticas(self, cursos: List[Dict]) -> Dict:
        """
        Genera estadísticas sobre los cursos procesados.
        """
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
            'escuelas': list(escuelas)
        }
    
    def exportar_a_excel(self, cursos: List[Dict], archivo_salida: str):
        """
        Exporta los cursos procesados a formato Excel compatible con el optimizador.
        """
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
        """
        Muestra un resumen de los datos procesados.
        """
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


def main():
    """
    Función principal para probar el lector de PDF.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python lector_pdf.py <archivo.pdf> [archivo_salida.xlsx]")
        return
    
    archivo_pdf = sys.argv[1]
    archivo_excel = sys.argv[2] if len(sys.argv) > 2 else "horarios_convertidos.xlsx"
    
    try:
        print(f"Procesando archivo PDF: {archivo_pdf}")
        
        lector = LectorPDFHorarios()
        datos = lector.leer_pdf(archivo_pdf)
        
        # Mostrar resumen
        lector.mostrar_resumen(datos)
        
        # Exportar a Excel
        lector.exportar_a_excel(datos['cursos'], archivo_excel)
        
        print(f"\nProceso completado exitosamente!")
        print(f"Archivo Excel generado: {archivo_excel}")
        print(f"Ahora puede usar este archivo con el optimizador de horarios.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()