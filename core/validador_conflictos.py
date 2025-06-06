from collections import defaultdict
from typing import Dict, List


class ValidadorConflictos:
    """
    Clase para validar y detectar conflictos en horarios.
    """

    @staticmethod
    def detectar_conflictos_horario(horario: List[List]) -> Dict[str, List]:
        """
        Detecta todos los tipos de conflictos en un horario.

        Returns:
            Dict con tipos de conflictos y sus detalles
        """
        conflictos = {
            'profesor': [],
            'salon': [],
            'estudiante': [],
            'sobrecarga': []
        }

        # Mapa de ocupación por bloque
        ocupacion = defaultdict(list)  # (dia, bloque) -> [cursos]

        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    ocupacion[(dia, bloque)].append(horario[dia][bloque])

        # Detectar conflictos por bloque
        for (dia, bloque), cursos in ocupacion.items():
            if len(cursos) > 1:
                ValidadorConflictos._analizar_conflictos_bloque(
                    cursos, dia, bloque, conflictos
                )

        # Detectar sobrecarga de profesores
        ValidadorConflictos._detectar_sobrecarga_profesores(horario, conflictos)

        return conflictos

    @staticmethod
    def _analizar_conflictos_bloque(cursos: List[Dict], dia: int, bloque: int,
                                   conflictos: Dict[str, List]):
        """
        Analiza conflictos en un bloque específico.
        """
        profesores = set()
        salones = set()

        for curso in cursos:
            # Conflicto de profesor
            if curso['profesor'] in profesores:
                conflictos['profesor'].append({
                    'dia': dia,
                    'bloque': bloque,
                    'profesor': curso['profesor'],
                    'cursos': [c['codigo'] for c in cursos if c['profesor'] == curso['profesor']]
                })
            profesores.add(curso['profesor'])

            # Conflicto de salón
            if 'salon' in curso and curso['salon'] in salones:
                conflictos['salon'].append({
                    'dia': dia,
                    'bloque': bloque,
                    'salon': curso['salon'],
                    'cursos': [c['codigo'] for c in cursos if c.get('salon') == curso['salon']]
                })
            if 'salon' in curso:
                salones.add(curso['salon'])

    @staticmethod
    def _detectar_sobrecarga_profesores(horario: List[List], conflictos: Dict[str, List]):
        """
        Detecta profesores con carga excesiva.
        """
        carga_profesores = defaultdict(int)

        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    profesor = horario[dia][bloque]['profesor']
                    carga_profesores[profesor] += 1

        # Profesores con más de 20 horas semanales
        for profesor, horas in carga_profesores.items():
            if horas > 20:
                conflictos['sobrecarga'].append({
                    'profesor': profesor,
                    'horas': horas
                })

    @staticmethod
    def calcular_puntuacion_conflictos(conflictos: Dict[str, List]) -> float:
        """
        Calcula una puntuación numérica de conflictos para la función fitness.
        """
        puntuacion = 0

        # Pesos por tipo de conflicto
        pesos = {
            'profesor': 100,    # Muy grave: un profesor no puede estar en dos lugares
            'salon': 80,        # Grave: un salón no puede tener dos clases
            'estudiante': 60,   # Moderado: estudiantes con horarios superpuestos
            'sobrecarga': 20    # Leve: carga excesiva de profesores
        }

        for tipo, lista_conflictos in conflictos.items():
            puntuacion += len(lista_conflictos) * pesos.get(tipo, 10)

        return puntuacion