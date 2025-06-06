from .nodos_geneticos import IntercambioInteligente, ResolverConflictos, Compactar, IfTiempoMuerto, NoOp, ProbarAlternativas, Secuencia, MoverMañana
from .validador_conflictos import ValidadorConflictos


import random


class ProgramacionGeneticaOptimizadorMejorado:
    """
    Versión mejorada del optimizador que considera conflictos de horarios.
    """

    def __init__(self, carga_horaria):
        self.carga_horaria = carga_horaria
        self.poblacion = []
        self.max_profundidad = 6  # Aumentado para más complejidad
        self.tam_poblacion = 30   # Reducido para mejor convergencia
        self.prob_cruce = 0.8
        self.prob_mutacion = 0.3
        self.generaciones = 50    # Aumentado para mejor optimización

        # Nodos mejorados que consideran conflictos
        self.nodos_funcionales = [IfTiempoMuerto, Secuencia, ProbarAlternativas]
        self.nodos_terminales = [
            Compactar, MoverMañana, IntercambioInteligente,
            ResolverConflictos, NoOp
        ]

        # Estadísticas de evolución
        self.historia_fitness = []
        self.historia_conflictos = []

    def evaluar_individuo_mejorado(self, individuo, cursos_seleccionados):
        """
        Evaluación mejorada que considera conflictos y optimización.
        """
        horario_inicial = self.crear_horario_inicial(cursos_seleccionados)
        horario_final = individuo.ejecutar(horario_inicial, cursos_seleccionados, self.carga_horaria)

        # Calcular componentes del fitness
        fitness_original = self.evaluar_horario_basico(horario_final)

        # Detectar y penalizar conflictos
        conflictos = ValidadorConflictos.detectar_conflictos_horario(horario_final)
        penalizacion_conflictos = ValidadorConflictos.calcular_puntuacion_conflictos(conflictos)

        # Métricas adicionales
        compactacion = self.evaluar_compactacion(horario_final)
        distribucion = self.evaluar_distribucion_semanal(horario_final)

        # Fitness total (menor es mejor)
        fitness_total = (fitness_original +
                        penalizacion_conflictos +
                        compactacion * 5 +
                        distribucion * 2)

        return fitness_total, conflictos

    def evaluar_horario_basico(self, horario):
        """
        Evaluación básica del horario (tiempos muertos, asignaciones).
        """
        tiempos_muertos = self.calcular_tiempos_muertos(horario)
        cursos_asignados = sum(1 for dia in horario for bloque in dia if bloque is not None)
        penalizacion_no_asignados = max(0, 20 - cursos_asignados) * 10

        return tiempos_muertos * 8 + penalizacion_no_asignados

    def evaluar_compactacion(self, horario):
        """
        Evalúa qué tan compactos están los horarios por día.
        """
        penalizacion = 0

        for dia in range(5):
            bloques_ocupados = [i for i in range(14) if horario[dia][i] is not None]
            if bloques_ocupados:
                rango = max(bloques_ocupados) - min(bloques_ocupados) + 1
                bloques_reales = len(bloques_ocupados)
                # Penalizar si hay muchos huecos
                if rango > bloques_reales:
                    penalizacion += (rango - bloques_reales) * 2

        return penalizacion

    def evaluar_distribucion_semanal(self, horario):
        """
        Evalúa la distribución de carga a lo largo de la semana.
        """
        cargas_diarias = []
        for dia in range(5):
            carga = sum(1 for bloque in range(14) if horario[dia][bloque] is not None)
            cargas_diarias.append(carga)

        if not cargas_diarias:
            return 0

        # Penalizar distribución muy desigual
        promedio = sum(cargas_diarias) / len(cargas_diarias)
        varianza = sum((carga - promedio) ** 2 for carga in cargas_diarias) / len(cargas_diarias)

        return varianza

    def calcular_tiempos_muertos(self, horario):
        """
        Calcula tiempos muertos mejorado.
        """
        total_tiempos_muertos = 0

        for dia in range(5):
            bloques_ocupados = [i for i in range(14) if horario[dia][i] is not None]
            if len(bloques_ocupados) > 1:
                primer_bloque = min(bloques_ocupados)
                ultimo_bloque = max(bloques_ocupados)

                for bloque in range(primer_bloque, ultimo_bloque + 1):
                    if horario[dia][bloque] is None:
                        total_tiempos_muertos += 1

        return total_tiempos_muertos

    def evolucionar_mejorado(self, cursos_seleccionados):
        """
        Proceso evolutivo mejorado con seguimiento de conflictos.
        """
        self.inicializar_poblacion()
        mejor_individuo = None
        mejor_fitness = float('inf')
        mejor_conflictos = None

        print(f"Iniciando evolución con {self.tam_poblacion} individuos...")

        for generacion in range(self.generaciones):
            # Evaluar población
            fitness_scores = []
            conflictos_generacion = []

            for individuo in self.poblacion:
                fitness, conflictos = self.evaluar_individuo_mejorado(individuo, cursos_seleccionados)
                fitness_scores.append(fitness)
                conflictos_generacion.append(conflictos)

                if fitness < mejor_fitness:
                    mejor_fitness = fitness
                    mejor_individuo = individuo.clonar()
                    mejor_conflictos = conflictos

            # Estadísticas de la generación
            self.historia_fitness.append(mejor_fitness)
            total_conflictos = sum(len(c['profesor']) + len(c['salon'])
                                 for c in conflictos_generacion)
            self.historia_conflictos.append(total_conflictos)

            # Mostrar progreso
            if generacion % 10 == 0 or generacion == self.generaciones - 1:
                print(f"Gen {generacion+1:2d}: Fitness={mejor_fitness:.1f}, "
                      f"Conflictos={len(mejor_conflictos['profesor']) + len(mejor_conflictos['salon'])}")

            # Crear nueva población
            nueva_poblacion = []

            # Elitismo: mantener mejores individuos
            mejores_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
            for i in range(min(3, len(mejores_indices))):
                nueva_poblacion.append(self.poblacion[mejores_indices[i]].clonar())

            # Generar resto de la población
            while len(nueva_poblacion) < self.tam_poblacion:
                padre1 = self.seleccion_torneo(self.poblacion, fitness_scores)
                padre2 = self.seleccion_torneo(self.poblacion, fitness_scores)

                hijo = self.cruce(padre1, padre2)
                hijo = self.mutacion(hijo)

                nueva_poblacion.append(hijo)

            self.poblacion = nueva_poblacion

        return mejor_individuo, mejor_conflictos

    # Métodos heredados del sistema original
    def generar_arbol_aleatorio(self, profundidad=0):
        if profundidad >= self.max_profundidad:
            return random.choice(self.nodos_terminales)()

        if profundidad == 0 or random.random() < 0.6:
            nodo = random.choice(self.nodos_funcionales)()

            if isinstance(nodo, (IfTiempoMuerto, ProbarAlternativas)):
                num_hijos = 2
            elif isinstance(nodo, Secuencia):
                num_hijos = random.randint(2, 4)
            else:
                num_hijos = 1

            for _ in range(num_hijos):
                hijo = self.generar_arbol_aleatorio(profundidad + 1)
                nodo.agregar_hijo(hijo)

            return nodo
        else:
            return random.choice(self.nodos_terminales)()

    def inicializar_poblacion(self):
        self.poblacion = []
        for _ in range(self.tam_poblacion):
            arbol = self.generar_arbol_aleatorio()
            self.poblacion.append(arbol)

    def crear_horario_inicial(self, cursos_seleccionados):
        """
        Crea horario inicial evitando conflictos obvios.
        """
        horario = [[None for _ in range(14)] for _ in range(5)]

        for curso_id in cursos_seleccionados:
            # Buscar curso en carga horaria
            posiciones_validas = []
            for dia, bloques in enumerate(self.carga_horaria):
                for bloque, curso in enumerate(bloques):
                    if curso and curso['id'] == curso_id:
                        posiciones_validas.append((dia, bloque, curso))

            if posiciones_validas:
                dia, bloque, curso_info = random.choice(posiciones_validas)

                # Verificar que no haya conflictos antes de asignar
                if self._posicion_libre_de_conflictos(horario, curso_info, dia, bloque):
                    horario[dia][bloque] = curso_info

        return horario

    def _posicion_libre_de_conflictos(self, horario, curso, dia, bloque):
        """
        Verifica que una posición esté libre de conflictos.
        """
        # Verificar conflicto de profesor
        for d in range(5):
            for b in range(14):
                if (horario[d][b] is not None and
                    horario[d][b]['profesor'] == curso['profesor'] and
                    d == dia and b == bloque):
                    return False

        return True

    def seleccion_torneo(self, poblacion, fitness_scores, tam_torneo=3):
        tam_torneo = min(tam_torneo, len(poblacion))
        participantes = random.sample(list(zip(poblacion, fitness_scores)), tam_torneo)
        ganador = min(participantes, key=lambda x: x[1])
        return ganador[0].clonar()

    def cruce(self, padre1, padre2):
        clon1 = padre1.clonar()
        clon2 = padre2.clonar()

        if random.random() < self.prob_cruce:
            punto1 = self.obtener_nodo_aleatorio(clon1)
            punto2 = self.obtener_nodo_aleatorio(clon2)

            if punto1 and punto2:
                temp = punto1['nodo']
                punto1['padre'].hijos[punto1['indice']] = punto2['nodo']
                punto2['padre'].hijos[punto2['indice']] = temp

        return clon1

    def mutacion(self, individuo):
        if random.random() < self.prob_mutacion:
            punto = self.obtener_nodo_aleatorio(individuo)
            if punto:
                nuevo_subarbol = self.generar_arbol_aleatorio(profundidad=2)
                punto['padre'].hijos[punto['indice']] = nuevo_subarbol

        return individuo

    def obtener_nodo_aleatorio(self, arbol, padre=None, indice=None):
        if len(arbol.hijos) == 0 or (padre is not None and random.random() < 0.1):
            if padre:
                return {'nodo': arbol, 'padre': padre, 'indice': indice}
            return None

        for i, hijo in enumerate(arbol.hijos):
            resultado = self.obtener_nodo_aleatorio(hijo, arbol, i)
            if resultado:
                return resultado

        if padre:
            return {'nodo': arbol, 'padre': padre, 'indice': indice}

        return None

    