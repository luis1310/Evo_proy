#!/usr/bin/env python3
"""
Generador de carga horaria mejorado que simula el formato de archivos PDF académicos.
Compatible con el nuevo sistema de optimización.
"""

import pandas as pd
import random
from typing import Dict, List, Tuple

class GeneradorCargaHorariaAvanzado:
    def __init__(self):
        # Configuración de escuelas y cursos
        self.escuelas = {
            'BF': {
                'nombre': 'Física - Pregrado',
                'cursos_base': [
                    'FÍSICA I', 'FÍSICA II', 'FÍSICA III',
                    'MECÁNICA CLÁSICA', 'ELECTROMAGNETISMO',
                    'MECÁNICA CUÁNTICA', 'TERMODINÁMICA'
                ]
            },
            'CF': {
                'nombre': 'Física - Avanzado', 
                'cursos_base': [
                    'ÓPTICA CLÁSICA', 'FÍSICA MODERNA',
                    'MECÁNICA CUÁNTICA II', 'FÍSICA NUCLEAR',
                    'FÍSICA DEL ESTADO SÓLIDO'
                ]
            },
            'CM': {
                'nombre': 'Matemática',
                'cursos_base': [
                    'CÁLCULO I', 'CÁLCULO II', 'ÁLGEBRA LINEAL',
                    'ANÁLISIS REAL', 'ECUACIONES DIFERENCIALES',
                    'MÉTODOS NUMÉRICOS'
                ]
            },
            'CQ': {
                'nombre': 'Química',
                'cursos_base': [
                    'QUÍMICA I', 'QUÍMICA ORGÁNICA', 'FISICOQUÍMICA',
                    'QUÍMICA ANALÍTICA', 'BIOQUÍMICA'
                ]
            },
            'CC': {
                'nombre': 'Computación',
                'cursos_base': [
                    'PROGRAMACIÓN I', 'ALGORITMOS', 'BASE DE DATOS',
                    'SISTEMAS OPERATIVOS', 'INTELIGENCIA ARTIFICIAL'
                ]
            }
        }
        
        # Pool de profesores por escuela
        self.profesores = {
            'BF': ['GARCÍA', 'MARTÍNEZ', 'LÓPEZ', 'TORRES', 'RAMÍREZ'],
            'CF': ['DÍAZ', 'MORALES', 'CASTRO', 'VARGAS', 'HERRERA'],
            'CM': ['SILVA', 'MENDOZA', 'ROJAS', 'PACHECO', 'VEGA'],
            'CQ': ['FLORES', 'SÁNCHEZ', 'GUZMÁN', 'PAREDES', 'NAVARRO'],
            'CC': ['RIVERA', 'CABRERA', 'ESPINOZA', 'DELGADO', 'AGUILAR']
        }
        
        # Salones disponibles
        self.salones = {
            'teoricos': ['R1-450', 'R1-460', 'J3-182A', 'J3-182B', 'J3-232', 'J3-242'],
            'laboratorios': ['LAB F', 'LAB FI', 'LAB 12', 'LAB 33C', 'LAB 33R1'],
            'salas': ['SALA 1', 'SALA 2', 'SALA 3', 'SALA 4']
        }
        
        # Horarios disponibles
        self.bloques_horarios = [
            ('7:00', '8:00'), ('8:00', '9:00'), ('9:00', '10:00'),
            ('10:00', '11:00'), ('11:00', '12:00'), ('12:00', '13:00'),
            ('13:00', '14:00'), ('14:00', '15:00'), ('15:00', '16:00'),
            ('16:00', '17:00'), ('17:00', '18:00'), ('18:00', '19:00'),
            ('19:00', '20:00'), ('20:00', '21:00')
        ]
        
        self.dias = ['LU', 'MA', 'MI', 'JU', 'VI']
        
    def generar_curso_completo(self, escuela: str, numero_curso: int, seccion: str) -> Dict:
        """
        Genera un curso completo con toda su información.
        """
        codigo_base = f"{escuela}{numero_curso:02d}"
        if random.random() > 0.7:  # 30% probabilidad de tener sufijo
            codigo_base += random.choice(['A', 'B', 'E'])
        
        codigo_completo = f"{codigo_base}_{seccion}"
        
        # Seleccionar nombre del curso
        nombres_base = self.escuelas[escuela]['cursos_base']
        nombre = random.choice(nombres_base)
        
        # Determinar si es teórico o práctico
        es_laboratorio = random.random() < 0.3  # 30% son laboratorios
        if es_laboratorio:
            nombre += " LAB"
            tipo = "Práctico"
        else:
            tipo = "Teórico"
        
        # Asignar profesor
        profesor = random.choice(self.profesores[escuela])
        
        # Generar capacidad realista
        if es_laboratorio:
            capacidad = random.randint(15, 25)
        else:
            capacidad = random.randint(25, 50)
        
        # Generar horarios (evitar conflictos)
        horarios = self.generar_horarios_curso(tipo, codigo_completo)
        
        return {
            'id': len(self.cursos_generados) + 1,
            'codigo': codigo_completo,
            'codigo_base': codigo_base,
            'nombre': nombre,
            'seccion': seccion,
            'escuela': escuela,
            'profesor': profesor,
            'tipo': tipo,
            'capacidad': capacidad,
            'horarios': horarios
        }
    
    def generar_horarios_curso(self, tipo: str, codigo: str) -> List[Dict]:
        """
        Genera horarios para un curso evitando conflictos básicos.
        """
        horarios = []
        
        if tipo == "Práctico":
            # Laboratorios: 1 sesión de 3-4 horas
            dia = random.choice(self.dias)
            inicio_idx = random.randint(0, 10)  # Evitar horarios muy tardíos
            duracion = random.choice([3, 4])  # 3 o 4 horas
            
            salon = random.choice(self.salones['laboratorios'])
            
            for i in range(duracion):
                if inicio_idx + i < len(self.bloques_horarios):
                    hora_inicio, hora_fin = self.bloques_horarios[inicio_idx + i]
                    horarios.append({
                        'dia': self.convertir_dia_completo(dia),
                        'dia_corto': dia,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'bloque_idx': inicio_idx + i,
                        'salon': salon
                    })
        else:
            # Cursos teóricos: 2 sesiones de 2 horas cada una
            dias_seleccionados = random.sample(self.dias, 2)
            
            for dia in dias_seleccionados:
                inicio_idx = random.randint(0, 12)  # Dejar espacio para 2 horas
                duracion = 2  # 2 horas por sesión
                
                salon = random.choice(self.salones['teoricos'])
                
                for i in range(duracion):
                    if inicio_idx + i < len(self.bloques_horarios):
                        hora_inicio, hora_fin = self.bloques_horarios[inicio_idx + i]
                        horarios.append({
                            'dia': self.convertir_dia_completo(dia),
                            'dia_corto': dia,
                            'hora_inicio': hora_inicio,
                            'hora_fin': hora_fin,
                            'bloque_idx': inicio_idx + i,
                            'salon': salon
                        })
        
        return horarios
    
    def convertir_dia_completo(self, dia_corto: str) -> str:
        """Convierte día corto a nombre completo."""
        conversion = {
            'LU': 'Lunes',
            'MA': 'Martes', 
            'MI': 'Miércoles',
            'JU': 'Jueves',
            'VI': 'Viernes'
        }
        return conversion.get(dia_corto, dia_corto)
    
    def generar_carga_completa(self, num_cursos_por_escuela: int = 15) -> List[Dict]:
        """
        Genera una carga horaria completa para todas las escuelas.
        """
        self.cursos_generados = []
        
        for escuela in self.escuelas.keys():
            print(f"Generando cursos para {escuela} - {self.escuelas[escuela]['nombre']}")
            
            for i in range(num_cursos_por_escuela):
                numero_curso = i + 1
                seccion = random.choice(['A', 'B', 'C'])
                
                curso = self.generar_curso_completo(escuela, numero_curso, seccion)
                self.cursos_generados.append(curso)
        
        print(f"\nTotal de cursos generados: {len(self.cursos_generados)}")
        return self.cursos_generados
    
    def detectar_conflictos(self, cursos: List[Dict]) -> List[Dict]:
        """
        Detecta conflictos de horario entre cursos.
        """
        conflictos = []
        
        for i, curso1 in enumerate(cursos):
            for j, curso2 in enumerate(cursos[i+1:], i+1):
                # Verificar conflictos de profesor
                if curso1['profesor'] == curso2['profesor']:
                    conflicto_horario = self.verificar_conflicto_horario(curso1, curso2)
                    if conflicto_horario:
                        conflictos.append({
                            'tipo': 'profesor',
                            'curso1': curso1['codigo'],
                            'curso2': curso2['codigo'],
                            'profesor': curso1['profesor'],
                            'conflicto': conflicto_horario
                        })
                
                # Verificar conflictos de salón
                conflicto_salon = self.verificar_conflicto_salon(curso1, curso2)
                if conflicto_salon:
                    conflictos.append({
                        'tipo': 'salon',
                        'curso1': curso1['codigo'],
                        'curso2': curso2['codigo'],
                        'salon': conflicto_salon['salon'],
                        'conflicto': conflicto_salon
                    })
        
        return conflictos
    
    def verificar_conflicto_horario(self, curso1: Dict, curso2: Dict) -> Dict:
        """
        Verifica si dos cursos tienen conflicto de horario.
        """
        for h1 in curso1['horarios']:
            for h2 in curso2['horarios']:
                if (h1['dia'] == h2['dia'] and 
                    h1['bloque_idx'] == h2['bloque_idx']):
                    return {
                        'dia': h1['dia'],
                        'hora': f"{h1['hora_inicio']}-{h1['hora_fin']}"
                    }
        return None
    
    def verificar_conflicto_salon(self, curso1: Dict, curso2: Dict) -> Dict:
        """
        Verifica si dos cursos tienen conflicto de salón.
        """
        for h1 in curso1['horarios']:
            for h2 in curso2['horarios']:
                if (h1['salon'] == h2['salon'] and 
                    h1['dia'] == h2['dia'] and 
                    h1['bloque_idx'] == h2['bloque_idx']):
                    return {
                        'salon': h1['salon'],
                        'dia': h1['dia'],
                        'hora': f"{h1['hora_inicio']}-{h1['hora_fin']}"
                    }
        return None
    
    def crear_matriz_horarios(self, cursos: List[Dict]):
        """
        Crea matriz de horarios compatible con el sistema de optimización.
        """
        # 5 días x 14 bloques
        matriz = [[None for _ in range(14)] for _ in range(5)]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for curso in cursos:
            for horario in curso['horarios']:
                if horario['dia'] in dias_orden:
                    dia_idx = dias_orden.index(horario['dia'])
                    bloque_idx = horario['bloque_idx']
                    
                    if 0 <= bloque_idx < 14:
                        matriz[dia_idx][bloque_idx] = {
                            'id': curso['id'],
                            'nombre': curso['nombre'],
                            'profesor': curso['profesor'],
                            'tipo': curso['tipo'],
                            'codigo': curso['codigo'],
                            'salon': horario['salon']
                        }
        
        return matriz
    
    def exportar_a_excel(self, cursos: List[Dict], archivo: str = 'carga_horaria_avanzada.xlsx'):
        """
        Exporta la carga horaria a formato Excel compatible.
        """
        matriz = self.crear_matriz_horarios(cursos)
        
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{inicio} - {fin}" for inicio, fin in self.bloques_horarios]
        
        # Crear DataFrame
        df = pd.DataFrame(index=horas, columns=dias)
        
        for dia_idx, dia in enumerate(dias):
            for bloque_idx in range(14):
                if matriz[dia_idx][bloque_idx]:
                    curso = matriz[dia_idx][bloque_idx]
                    # Formato compatible: "id|nombre|profesor|tipo"
                    celda = f"{curso['id']}|{curso['nombre']}|{curso['profesor']}|{curso['tipo']}"
                    df.iloc[bloque_idx, dia_idx] = celda
        
        df.to_excel(archivo)
        print(f"Archivo Excel creado: {archivo}")
        
        return df
    
    def generar_reporte_conflictos(self, conflictos: List[Dict]):
        """
        Genera un reporte detallado de conflictos.
        """
        if not conflictos:
            print("✅ No se encontraron conflictos de horario")
            return
        
        print(f"\n⚠️  CONFLICTOS DETECTADOS: {len(conflictos)}")
        print("="*60)
        
        conflictos_profesor = [c for c in conflictos if c['tipo'] == 'profesor']
        conflictos_salon = [c for c in conflictos if c['tipo'] == 'salon']
        
        if conflictos_profesor:
            print(f"\n🧑‍🏫 Conflictos de Profesor ({len(conflictos_profesor)}):")
            for conf in conflictos_profesor:
                print(f"   {conf['profesor']}: {conf['curso1']} ↔️ {conf['curso2']}")
                print(f"      {conf['conflicto']['dia']} {conf['conflicto']['hora']}")
        
        if conflictos_salon:
            print(f"\n🏫 Conflictos de Salón ({len(conflictos_salon)}):")
            for conf in conflictos_salon:
                print(f"   {conf['salon']}: {conf['curso1']} ↔️ {conf['curso2']}")
                print(f"      {conf['conflicto']['dia']} {conf['conflicto']['hora']}")

def generar_carga_horaria_ejemplo():
    """
    Función principal para generar carga horaria de ejemplo.
    """
    print("GENERADOR DE CARGA HORARIA AVANZADO")
    print("="*50)
    
    generador = GeneradorCargaHorariaAvanzado()
    
    # Generar cursos
    cursos = generador.generar_carga_completa(num_cursos_por_escuela=12)
    
    # Detectar conflictos
    print("\nDetectando conflictos...")
    conflictos = generador.detectar_conflictos(cursos)
    generador.generar_reporte_conflictos(conflictos)
    
    # Exportar a Excel
    print("\nExportando a Excel...")
    df = generador.exportar_a_excel(cursos)
    
    # Mostrar estadísticas
    print(f"\nESTADÍSTICAS GENERALES:")
    print(f"- Total cursos: {len(cursos)}")
    print(f"- Conflictos: {len(conflictos)}")
    
    por_escuela = {}
    for curso in cursos:
        escuela = curso['escuela']
        por_escuela[escuela] = por_escuela.get(escuela, 0) + 1
    
    for escuela, cantidad in por_escuela.items():
        print(f"- {escuela}: {cantidad} cursos")
    
    return cursos, df

if __name__ == "__main__":
    generar_carga_horaria_ejemplo()