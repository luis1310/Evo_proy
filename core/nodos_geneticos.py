#!/usr/bin/env python3
"""
Módulo de nodos genéticos para el sistema de programación genética.
Contiene todos los nodos (funcionales y terminales) utilizados en el algoritmo.

Este archivo va en: core/nodos_geneticos.py
"""

import random
import copy
from typing import List, Tuple, Dict, Any
from collections import defaultdict

# Importar el validador de conflictos
from .validador_conflictos import ValidadorConflictos


# ============================================================================
# CLASE BASE PARA TODOS LOS NODOS
# ============================================================================

class Node:
    """Clase base para todos los nodos del árbol de programación genética."""
    
    def __init__(self, tipo):
        self.tipo = tipo
        self.hijos = []
    
    def agregar_hijo(self, hijo):
        """Agrega un hijo al nodo."""
        self.hijos.append(hijo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Ejecuta la operación del nodo. Debe ser implementado por cada subclase."""
        raise NotImplementedError
    
    def clonar(self):
        """Crea una copia profunda del nodo y sus hijos."""
        nuevo_nodo = self.__class__(self.tipo)
        nuevo_nodo.hijos = [hijo.clonar() for hijo in self.hijos]
        return nuevo_nodo


# ============================================================================
# NODOS FUNCIONALES (INTERNOS) - Tienen hijos
# ============================================================================

class IfTiempoMuerto(Node):
    """Nodo condicional que evalúa tiempos muertos y ejecuta diferentes estrategias."""
    
    def __init__(self, tipo="if_tiempo_muerto"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Ejecuta una estrategia u otra dependiendo de los tiempos muertos."""
        tiempos_muertos = self._calcular_tiempos_muertos(horario)
        
        if tiempos_muertos > 3:  # Umbral ajustable
            # Muchos tiempos muertos -> ejecutar primera estrategia
            return self.hijos[0].ejecutar(horario, cursos_seleccionados, carga_horaria)
        else:
            # Pocos tiempos muertos -> ejecutar segunda estrategia
            return self.hijos[1].ejecutar(horario, cursos_seleccionados, carga_horaria)
    
    def _calcular_tiempos_muertos(self, horario):
        """Calcula los tiempos muertos en el horario."""
        total_tiempos_muertos = 0
        
        for dia in range(5):
            primer_curso = None
            ultimo_curso = None
            
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    if primer_curso is None:
                        primer_curso = bloque
                    ultimo_curso = bloque
            
            if primer_curso is not None and ultimo_curso is not None:
                for bloque in range(primer_curso, ultimo_curso + 1):
                    if horario[dia][bloque] is None:
                        total_tiempos_muertos += 1
        
        return total_tiempos_muertos


class Secuencia(Node):
    """Nodo que ejecuta múltiples operaciones en secuencia."""
    
    def __init__(self, tipo="secuencia"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Ejecuta todos los hijos en secuencia."""
        resultado = horario
        for hijo in self.hijos:
            resultado = hijo.ejecutar(resultado, cursos_seleccionados, carga_horaria)
        return resultado


class ProbarAlternativas(Node):
    """Nodo que prueba dos alternativas y elige la mejor según fitness."""
    
    def __init__(self, tipo="probar_alternativas"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Ejecuta dos estrategias y retorna la que tenga mejor fitness."""
        if len(self.hijos) < 2:
            return horario
        
        resultado1 = self.hijos[0].ejecutar(horario, cursos_seleccionados, carga_horaria)
        resultado2 = self.hijos[1].ejecutar(horario, cursos_seleccionados, carga_horaria)
        
        fitness1 = self._evaluar_horario_basico(resultado1)
        fitness2 = self._evaluar_horario_basico(resultado2)
        
        return resultado1 if fitness1 < fitness2 else resultado2
    
    def _evaluar_horario_basico(self, horario):
        """Evaluación básica de fitness para comparar alternativas."""
        tiempos_muertos = self._calcular_tiempos_muertos(horario)
        cursos_asignados = sum(1 for dia in horario for bloque in dia if bloque is not None)
        
        # Detectar conflictos
        conflictos = ValidadorConflictos.detectar_conflictos_horario(horario)
        penalizacion_conflictos = ValidadorConflictos.calcular_puntuacion_conflictos(conflictos)
        
        return tiempos_muertos * 10 + penalizacion_conflictos
    
    def _calcular_tiempos_muertos(self, horario):
        """Calcula tiempos muertos."""
        total = 0
        for dia in range(5):
            bloques_ocupados = [i for i in range(14) if horario[dia][i] is not None]
            if len(bloques_ocupados) > 1:
                primer_bloque = min(bloques_ocupados)
                ultimo_bloque = max(bloques_ocupados)
                for bloque in range(primer_bloque, ultimo_bloque + 1):
                    if horario[dia][bloque] is None:
                        total += 1
        return total


# ============================================================================
# NODOS TERMINALES (HOJAS) - No tienen hijos
# ============================================================================

class Compactar(Node):
    """Nodo que elimina espacios vacíos moviendo cursos hacia arriba."""
    
    def __init__(self, tipo="compactar"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Compacta el horario eliminando espacios vacíos."""
        nuevo_horario = [[None for _ in range(14)] for _ in range(5)]
        
        for dia in range(5):
            bloque_destino = 0
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    nuevo_horario[dia][bloque_destino] = horario[dia][bloque]
                    bloque_destino += 1
        
        return nuevo_horario


class MoverMañana(Node):
    """Nodo que mueve cursos hacia horarios matutinos."""
    
    def __init__(self, tipo="mover_mañana"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Mueve todos los cursos hacia las primeras horas del día."""
        nuevo_horario = [[None for _ in range(14)] for _ in range(5)]
        
        for dia in range(5):
            bloques_ocupados = []
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    bloques_ocupados.append(horario[dia][bloque])
            
            # Asignar desde el primer bloque disponible
            for i, curso in enumerate(bloques_ocupados):
                if i < 14:
                    nuevo_horario[dia][i] = curso
        
        return nuevo_horario


class IntercambioInteligente(Node):
    """Nodo que realiza intercambios considerando conflictos."""
    
    def __init__(self, tipo="intercambio_inteligente"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Ejecuta intercambios inteligentes que minimizan conflictos."""
        nuevo_horario = copy.deepcopy(horario)
        
        # Detectar conflictos actuales
        conflictos_actuales = ValidadorConflictos.detectar_conflictos_horario(nuevo_horario)
        
        if self._tiene_conflictos_graves(conflictos_actuales):
            # Si hay conflictos graves, intentar resolverlos
            nuevo_horario = self._resolver_conflictos(nuevo_horario, conflictos_actuales)
        else:
            # Si no hay conflictos graves, hacer intercambio normal para optimizar
            nuevo_horario = self._intercambio_optimizacion(nuevo_horario)
        
        return nuevo_horario
    
    def _tiene_conflictos_graves(self, conflictos: Dict[str, List]) -> bool:
        """Determina si hay conflictos que requieren resolución inmediata."""
        return (len(conflictos.get('profesor', [])) > 0 or 
                len(conflictos.get('salon', [])) > 0)
    
    def _resolver_conflictos(self, horario: List[List], conflictos: Dict[str, List]) -> List[List]:
        """Intenta resolver conflictos moviendo cursos a posiciones libres."""
        nuevo_horario = copy.deepcopy(horario)
        
        # Resolver conflictos de profesor primero (más críticos)
        for conflicto in conflictos.get('profesor', []):
            nuevo_horario = self._resolver_conflicto_profesor(nuevo_horario, conflicto)
        
        # Resolver conflictos de salón
        for conflicto in conflictos.get('salon', []):
            nuevo_horario = self._resolver_conflicto_salon(nuevo_horario, conflicto)
        
        return nuevo_horario
    
    def _resolver_conflicto_profesor(self, horario: List[List], conflicto: Dict) -> List[List]:
        """Resuelve un conflicto específico de profesor."""
        dia = conflicto['dia']
        bloque = conflicto['bloque']
        
        # Si hay múltiples cursos en el mismo bloque con el mismo profesor
        if horario[dia][bloque] is not None:
            curso_a_mover = horario[dia][bloque]
            horario[dia][bloque] = None
            
            # Buscar nueva posición
            nueva_posicion = self._encontrar_posicion_libre(horario, curso_a_mover)
            if nueva_posicion:
                dia_nuevo, bloque_nuevo = nueva_posicion
                horario[dia_nuevo][bloque_nuevo] = curso_a_mover
        
        return horario
    
    def _resolver_conflicto_salon(self, horario: List[List], conflicto: Dict) -> List[List]:
        """Resuelve un conflicto específico de salón."""
        # Similar al de profesor, pero considerando salones
        return self._resolver_conflicto_profesor(horario, conflicto)
    
    def _encontrar_posicion_libre(self, horario: List[List], curso: Dict) -> Tuple[int, int]:
        """Encuentra una posición libre para un curso sin crear nuevos conflictos."""
        posiciones_libres = []
        
        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is None:
                    # Verificar que no cree conflictos
                    if self._es_posicion_valida(horario, curso, dia, bloque):
                        posiciones_libres.append((dia, bloque))
        
        return random.choice(posiciones_libres) if posiciones_libres else None
    
    def _es_posicion_valida(self, horario: List[List], curso: Dict, dia: int, bloque: int) -> bool:
        """Verifica si colocar un curso en una posición es válido."""
        # Verificar conflictos de profesor en el mismo bloque de tiempo
        for d in range(5):
            for b in range(14):
                if horario[d][b] is not None:
                    if (horario[d][b]['profesor'] == curso['profesor'] and 
                        d == dia and b == bloque):
                        return False
        
        return True
    
    def _intercambio_optimizacion(self, horario: List[List]) -> List[List]:
        """Realiza intercambio para optimización cuando no hay conflictos graves."""
        nuevo_horario = copy.deepcopy(horario)
        
        # Encontrar cursos asignados
        cursos_asignados = []
        for dia in range(5):
            for bloque in range(14):
                if nuevo_horario[dia][bloque] is not None:
                    cursos_asignados.append({
                        'curso': nuevo_horario[dia][bloque],
                        'dia': dia,
                        'bloque': bloque
                    })
        
        if len(cursos_asignados) >= 2:
            # Seleccionar dos cursos para intercambiar
            curso1, curso2 = random.sample(cursos_asignados, 2)
            
            # Verificar que el intercambio no cree conflictos
            if self._intercambio_es_valido(nuevo_horario, curso1, curso2):
                # Realizar intercambio
                nuevo_horario[curso1['dia']][curso1['bloque']] = curso2['curso']
                nuevo_horario[curso2['dia']][curso2['bloque']] = curso1['curso']
        
        return nuevo_horario
    
    def _intercambio_es_valido(self, horario: List[List], curso1: Dict, curso2: Dict) -> bool:
        """Verifica si un intercambio entre dos cursos es válido."""
        # Simular el intercambio temporalmente
        horario_temp = copy.deepcopy(horario)
        horario_temp[curso1['dia']][curso1['bloque']] = curso2['curso']
        horario_temp[curso2['dia']][curso2['bloque']] = curso1['curso']
        
        # Verificar que no se generen conflictos
        conflictos = ValidadorConflictos.detectar_conflictos_horario(horario_temp)
        return (len(conflictos.get('profesor', [])) == 0 and 
                len(conflictos.get('salon', [])) == 0)


class ResolverConflictos(Node):
    """Nodo especializado en resolver conflictos de horarios."""
    
    def __init__(self, tipo="resolver_conflictos"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Resuelve sistemáticamente los conflictos en el horario."""
        nuevo_horario = copy.deepcopy(horario)
        
        # Detectar conflictos
        conflictos = ValidadorConflictos.detectar_conflictos_horario(nuevo_horario)
        
        # Resolver en orden de prioridad
        if conflictos.get('profesor', []):
            nuevo_horario = self._resolver_conflictos_profesor(nuevo_horario, conflictos['profesor'])
        
        if conflictos.get('salon', []):
            nuevo_horario = self._resolver_conflictos_salon(nuevo_horario, conflictos['salon'])
        
        return nuevo_horario
    
    def _resolver_conflictos_profesor(self, horario: List[List], conflictos_profesor: List) -> List[List]:
        """Resuelve conflictos de profesores redistribuyendo cursos."""
        for conflicto in conflictos_profesor:
            dia = conflicto['dia']
            bloque = conflicto['bloque']
            
            # Si hay múltiples cursos en el mismo bloque con el mismo profesor
            if horario[dia][bloque] is not None:
                # Mover uno de los cursos a otra posición
                curso_a_mover = horario[dia][bloque]
                horario[dia][bloque] = None
                
                # Buscar nueva posición
                nueva_pos = self._encontrar_posicion_libre_profesor(horario, curso_a_mover)
                if nueva_pos:
                    nuevo_dia, nuevo_bloque = nueva_pos
                    horario[nuevo_dia][nuevo_bloque] = curso_a_mover
        
        return horario
    
    def _resolver_conflictos_salon(self, horario: List[List], conflictos_salon: List) -> List[List]:
        """Resuelve conflictos de salones."""
        for conflicto in conflictos_salon:
            dia = conflicto['dia']
            bloque = conflicto['bloque']
            
            if horario[dia][bloque] is not None:
                curso = horario[dia][bloque]
                # Cambiar salón del curso o moverlo
                if 'salon' in curso:
                    curso['salon'] = self._asignar_nuevo_salon(curso.get('tipo', 'Teórico'))
        
        return horario
    
    def _encontrar_posicion_libre_profesor(self, horario: List[List], curso: Dict) -> Tuple[int, int]:
        """Encuentra posición libre considerando disponibilidad del profesor."""
        profesor = curso['profesor']
        
        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is None:
                    # Verificar que el profesor esté libre
                    profesor_libre = True
                    for d in range(5):
                        for b in range(14):
                            if (horario[d][b] is not None and 
                                horario[d][b]['profesor'] == profesor and
                                d == dia and b == bloque):
                                profesor_libre = False
                                break
                        if not profesor_libre:
                            break
                    
                    if profesor_libre:
                        return (dia, bloque)
        
        return None
    
    def _asignar_nuevo_salon(self, tipo_curso: str) -> str:
        """Asigna un nuevo salón según el tipo de curso."""
        if tipo_curso == "Práctico":
            salones = ['LAB F', 'LAB FI', 'LAB 12', 'LAB 33C']
        else:
            salones = ['R1-450', 'R1-460', 'J3-182A', 'J3-232', 'SALA 1']
        
        return random.choice(salones)


class NoOp(Node):
    """Nodo que no realiza ninguna operación (operación nula)."""
    
    def __init__(self, tipo="no_op"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """No modifica el horario."""
        return horario


# ============================================================================
# NODOS ADICIONALES PARA OPTIMIZACIÓN ESPECÍFICA
# ============================================================================

class DistribuirCarga(Node):
    """Nodo que intenta distribuir la carga uniformemente en la semana."""
    
    def __init__(self, tipo="distribuir_carga"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Redistribuye cursos para equilibrar la carga semanal."""
        nuevo_horario = copy.deepcopy(horario)
        
        # Calcular carga por día
        cargas_diarias = []
        for dia in range(5):
            carga = sum(1 for bloque in range(14) if nuevo_horario[dia][bloque] is not None)
            cargas_diarias.append(carga)
        
        # Encontrar día con más carga y día con menos carga
        dia_max = cargas_diarias.index(max(cargas_diarias))
        dia_min = cargas_diarias.index(min(cargas_diarias))
        
        # Mover un curso del día con más carga al día con menos carga
        if cargas_diarias[dia_max] > cargas_diarias[dia_min] + 1:
            # Buscar un curso para mover
            for bloque in range(13, -1, -1):  # Empezar desde el final
                if nuevo_horario[dia_max][bloque] is not None:
                    curso = nuevo_horario[dia_max][bloque]
                    
                    # Buscar espacio en el día con menos carga
                    for bloque_destino in range(14):
                        if nuevo_horario[dia_min][bloque_destino] is None:
                            # Verificar que el movimiento no cree conflictos
                            if self._movimiento_es_valido(nuevo_horario, curso, dia_min, bloque_destino):
                                nuevo_horario[dia_max][bloque] = None
                                nuevo_horario[dia_min][bloque_destino] = curso
                                break
                    break
        
        return nuevo_horario
    
    def _movimiento_es_valido(self, horario, curso, dia_destino, bloque_destino):
        """Verifica si mover un curso es válido."""
        # Verificar conflictos de profesor
        for d in range(5):
            for b in range(14):
                if (horario[d][b] is not None and 
                    horario[d][b]['profesor'] == curso['profesor'] and
                    d == dia_destino and b == bloque_destino):
                    return False
        return True


class OptimizarBloques(Node):
    """Nodo que optimiza la asignación de bloques consecutivos."""
    
    def __init__(self, tipo="optimizar_bloques"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados, carga_horaria=None):
        """Agrupa cursos del mismo tipo en bloques consecutivos."""
        nuevo_horario = copy.deepcopy(horario)
        
        for dia in range(5):
            # Extraer cursos del día
            cursos_dia = []
            for bloque in range(14):
                if nuevo_horario[dia][bloque] is not None:
                    cursos_dia.append(nuevo_horario[dia][bloque])
                    nuevo_horario[dia][bloque] = None
            
            # Agrupar por profesor
            cursos_por_profesor = defaultdict(list)
            for curso in cursos_dia:
                cursos_por_profesor[curso['profesor']].append(curso)
            
            # Reasignar agrupando por profesor
            bloque_actual = 0
            for profesor, cursos_profesor in cursos_por_profesor.items():
                for curso in cursos_profesor:
                    if bloque_actual < 14:
                        nuevo_horario[dia][bloque_actual] = curso
                        bloque_actual += 1
        
        return nuevo_horario


# ============================================================================
# REGISTRO DE NODOS DISPONIBLES
# ============================================================================

# Nodos funcionales (internos) - Tienen hijos
NODOS_FUNCIONALES = [
    IfTiempoMuerto,
    Secuencia,
    ProbarAlternativas
]

# Nodos terminales (hojas) - No tienen hijos
NODOS_TERMINALES = [
    Compactar,
    MoverMañana,
    IntercambioInteligente,
    ResolverConflictos,
    NoOp,
    DistribuirCarga,
    OptimizarBloques
]

# Todos los nodos disponibles
TODOS_LOS_NODOS = NODOS_FUNCIONALES + NODOS_TERMINALES


def obtener_nodo_aleatorio_funcional():
    """Retorna una instancia aleatoria de un nodo funcional."""
    return random.choice(NODOS_FUNCIONALES)()


def obtener_nodo_aleatorio_terminal():
    """Retorna una instancia aleatoria de un nodo terminal."""
    return random.choice(NODOS_TERMINALES)()


def obtener_nodo_por_nombre(nombre_nodo: str):
    """Retorna una instancia del nodo especificado por nombre."""
    mapa_nodos = {
        'if_tiempo_muerto': IfTiempoMuerto,
        'secuencia': Secuencia,
        'probar_alternativas': ProbarAlternativas,
        'compactar': Compactar,
        'mover_mañana': MoverMañana,
        'intercambio_inteligente': IntercambioInteligente,
        'resolver_conflictos': ResolverConflictos,
        'no_op': NoOp,
        'distribuir_carga': DistribuirCarga,
        'optimizar_bloques': OptimizarBloques
    }
    
    if nombre_nodo in mapa_nodos:
        return mapa_nodos[nombre_nodo]()
    else:
        raise ValueError(f"Nodo '{nombre_nodo}' no encontrado")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def crear_arbol_simple(estrategia: str = "basica"):
    """
    Crea un árbol simple predefinido para casos específicos.
    
    Args:
        estrategia: Tipo de estrategia ('basica', 'conflictos', 'compacta')
    
    Returns:
        Nodo raíz del árbol creado
    """
    if estrategia == "basica":
        # Secuencia simple: Compactar -> Mover a mañana
        raiz = Secuencia()
        raiz.agregar_hijo(Compactar())
        raiz.agregar_hijo(MoverMañana())
        return raiz
    
    elif estrategia == "conflictos":
        # Enfoque en resolver conflictos
        raiz = Secuencia()
        raiz.agregar_hijo(ResolverConflictos())
        raiz.agregar_hijo(IntercambioInteligente())
        return raiz
    
    elif estrategia == "compacta":
        # Enfoque en compactación y distribución
        raiz = Secuencia()
        raiz.agregar_hijo(Compactar())
        raiz.agregar_hijo(DistribuirCarga())
        raiz.agregar_hijo(OptimizarBloques())
        return raiz
    
    else:
        # Estrategia por defecto
        return Compactar()


def validar_arbol(nodo):
    """
    Valida que un árbol de programación genética esté bien formado.
    
    Args:
        nodo: Nodo raíz del árbol
    
    Returns:
        bool: True si el árbol es válido
    """
    try:
        # Verificar que el nodo tenga el método ejecutar
        if not hasattr(nodo, 'ejecutar'):
            return False
        
        # Verificar que los nodos funcionales tengan hijos
        if type(nodo) in NODOS_FUNCIONALES:
            if len(nodo.hijos) == 0:
                return False
            
            # Validar recursivamente los hijos
            for hijo in nodo.hijos:
                if not validar_arbol(hijo):
                    return False
        
        # Los nodos terminales no deberían tener hijos
        elif type(nodo) in NODOS_TERMINALES:
            if len(nodo.hijos) > 0:
                return False
        
        return True
    
    except Exception:
        return False


if __name__ == "__main__":
    # Ejemplo de uso del módulo
    print("🧬 MÓDULO DE NODOS GENÉTICOS")
    print("="*40)
    
    print(f"Nodos funcionales disponibles: {len(NODOS_FUNCIONALES)}")
    for nodo_class in NODOS_FUNCIONALES:
        print(f"  - {nodo_class.__name__}")
    
    print(f"\nNodos terminales disponibles: {len(NODOS_TERMINALES)}")
    for nodo_class in NODOS_TERMINALES:
        print(f"  - {nodo_class.__name__}")
    
    # Crear un árbol de ejemplo
    print("\n🌳 Creando árbol de ejemplo...")
    arbol_ejemplo = crear_arbol_simple("conflictos")
    print(f"Árbol válido: {validar_arbol(arbol_ejemplo)}")
    print(f"Tipo raíz: {type(arbol_ejemplo).__name__}")
    print(f"Número de hijos: {len(arbol_ejemplo.hijos)}")