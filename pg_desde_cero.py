import random
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any

# Clase base para nodos del árbol
class Node:
    def __init__(self, tipo):
        self.tipo = tipo
        self.hijos = []
    
    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        raise NotImplementedError
    
    def clonar(self):
        nuevo_nodo = self.__class__(self.tipo)
        nuevo_nodo.hijos = [hijo.clonar() for hijo in self.hijos]
        return nuevo_nodo

# Nodos funcionales (internos)
class IfTiempoMuerto(Node):
    def __init__(self, tipo="if_tiempo_muerto"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        tiempos_muertos = calcular_tiempos_muertos(horario)
        if tiempos_muertos > 3:  # Umbral ajustable
            return self.hijos[0].ejecutar(horario, cursos_seleccionados)
        else:
            return self.hijos[1].ejecutar(horario, cursos_seleccionados)

class Secuencia(Node):
    def __init__(self, tipo="secuencia"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        resultado = horario
        for hijo in self.hijos:
            resultado = hijo.ejecutar(resultado, cursos_seleccionados)
        return resultado

class ProbarAlternativas(Node):
    def __init__(self, tipo="probar_alternativas"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        resultado1 = self.hijos[0].ejecutar(horario, cursos_seleccionados)
        resultado2 = self.hijos[1].ejecutar(horario, cursos_seleccionados)
        
        fitness1 = evaluar_horario(resultado1)
        fitness2 = evaluar_horario(resultado2)
        
        return resultado1 if fitness1 < fitness2 else resultado2

# Nodos terminales (hojas)
class Compactar(Node):
    def __init__(self, tipo="compactar"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        nuevo_horario = [[None for _ in range(14)] for _ in range(5)]
        
        for dia in range(5):
            bloque_destino = 0
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    nuevo_horario[dia][bloque_destino] = horario[dia][bloque]
                    bloque_destino += 1
        
        return nuevo_horario

class MoverMañana(Node):
    def __init__(self, tipo="mover_mañana"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        nuevo_horario = [[None for _ in range(14)] for _ in range(5)]
        
        for dia in range(5):
            bloques_ocupados = []
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    bloques_ocupados.append(horario[dia][bloque])
            
            for i, curso in enumerate(bloques_ocupados):
                nuevo_horario[dia][i] = curso
        
        return nuevo_horario

class IntercambioAleatorio(Node):
    def __init__(self, tipo="intercambio_aleatorio"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        nuevo_horario = copy.deepcopy(horario)
        
        # Encontrar bloques con cursos
        bloques_ocupados = []
        for dia in range(5):
            for bloque in range(14):
                if nuevo_horario[dia][bloque] is not None:
                    bloques_ocupados.append((dia, bloque))
        
        if len(bloques_ocupados) >= 2:
            (dia1, bloque1), (dia2, bloque2) = random.sample(bloques_ocupados, 2)
            nuevo_horario[dia1][bloque1], nuevo_horario[dia2][bloque2] = \
                nuevo_horario[dia2][bloque2], nuevo_horario[dia1][bloque1]
        
        return nuevo_horario

class NoOp(Node):
    def __init__(self, tipo="no_op"):
        super().__init__(tipo)
    
    def ejecutar(self, horario, cursos_seleccionados):
        return horario

# Clase para manejar la programación genética
class ProgramacionGeneticaOptimizador:
    def __init__(self, carga_horaria):
        self.carga_horaria = carga_horaria
        self.poblacion = []
        self.max_profundidad = 5
        self.tam_poblacion = 50
        self.prob_cruce = 0.7
        self.prob_mutacion = 0.2
        self.generaciones = 30
        
        # Tipos de nodos disponibles
        self.nodos_funcionales = [IfTiempoMuerto, Secuencia, ProbarAlternativas]
        self.nodos_terminales = [Compactar, MoverMañana, IntercambioAleatorio, NoOp]
    
    def generar_arbol_aleatorio(self, profundidad=0):
        """Genera un árbol aleatorio utilizando el método grow"""
        if profundidad >= self.max_profundidad:
            # Crear nodo terminal
            return random.choice(self.nodos_terminales)()
        
        if profundidad == 0 or random.random() < 0.5:
            # Crear nodo funcional
            nodo = random.choice(self.nodos_funcionales)()
            
            # Determinar número de hijos según el tipo
            if isinstance(nodo, (IfTiempoMuerto, ProbarAlternativas)):
                num_hijos = 2
            elif isinstance(nodo, Secuencia):
                num_hijos = random.randint(1, 3)  # Secuencia puede tener 1-3 hijos
            else:
                num_hijos = 1
            
            for _ in range(num_hijos):
                hijo = self.generar_arbol_aleatorio(profundidad + 1)
                nodo.agregar_hijo(hijo)
            
            return nodo
        else:
            # Crear nodo terminal
            return random.choice(self.nodos_terminales)()
    
    def inicializar_poblacion(self):
        """Crea una población inicial de árboles"""
        self.poblacion = []
        for _ in range(self.tam_poblacion):
            arbol = self.generar_arbol_aleatorio()
            self.poblacion.append(arbol)
    
    def evaluar_individuo(self, individuo, cursos_seleccionados):
        """Evalúa un individuo aplicándolo a un horario inicial"""
        horario_inicial = self.crear_horario_inicial(cursos_seleccionados)
        horario_final = individuo.ejecutar(horario_inicial, cursos_seleccionados)
        return evaluar_horario(horario_final)
    
    def crear_horario_inicial(self, cursos_seleccionados):
        """Crea un horario inicial basado en la carga horaria y cursos seleccionados"""
        horario = [[None for _ in range(14)] for _ in range(5)]
        
        for curso_id in cursos_seleccionados:
            asignaciones = [(dia, bloque) for dia, bloques in enumerate(self.carga_horaria)
                           for bloque, curso in enumerate(bloques) if curso and curso['id'] == curso_id]
            
            if asignaciones:
                dia, bloque = random.choice(asignaciones)
                horario[dia][bloque] = self.carga_horaria[dia][bloque]
        
        return horario
    
    def seleccion_torneo(self, poblacion, fitness_scores, tam_torneo=3):
        """Selección por torneo"""
        # Asegurarse de que tam_torneo no sea mayor que el número de individuos
        tam_torneo = min(tam_torneo, len(poblacion))
        participantes = random.sample(list(zip(poblacion, fitness_scores)), tam_torneo)
        ganador = min(participantes, key=lambda x: x[1])
        return ganador[0].clonar()
    
    def cruce(self, padre1, padre2):
        """Cruce de dos árboles, intercambiando subárboles"""
        clon1 = padre1.clonar()
        clon2 = padre2.clonar()
        
        if random.random() < self.prob_cruce:
            punto1 = self.obtener_nodo_aleatorio(clon1)
            punto2 = self.obtener_nodo_aleatorio(clon2)
            
            if punto1 and punto2:
                # Intercambiar subárboles
                temp = punto1['nodo']
                punto1['padre'].hijos[punto1['indice']] = punto2['nodo']
                punto2['padre'].hijos[punto2['indice']] = temp
        
        return clon1
    
    def mutacion(self, individuo):
        """Mutación de un árbol"""
        if random.random() < self.prob_mutacion:
            punto = self.obtener_nodo_aleatorio(individuo)
            if punto:
                nuevo_subarbol = self.generar_arbol_aleatorio(profundidad=2)  # Profundidad reducida para subárboles
                punto['padre'].hijos[punto['indice']] = nuevo_subarbol
        
        return individuo
    
    def obtener_nodo_aleatorio(self, arbol, padre=None, indice=None):
        """Obtiene un nodo aleatorio del árbol para mutación o cruce"""
        # Si es un nodo hoja o decidimos aleatoriamente seleccionar este nodo
        if len(arbol.hijos) == 0 or (padre is not None and random.random() < 0.1):
            if padre:
                return {'nodo': arbol, 'padre': padre, 'indice': indice}
            return None
        
        # De lo contrario, buscamos recursivamente en los hijos
        for i, hijo in enumerate(arbol.hijos):
            resultado = self.obtener_nodo_aleatorio(hijo, arbol, i)
            if resultado:
                return resultado
        
        # Si llegamos aquí y este nodo tiene hijos pero no seleccionamos ninguno
        # podemos seleccionar este nodo si tiene un padre
        if padre:
            return {'nodo': arbol, 'padre': padre, 'indice': indice}
        
        return None
    
    def evolucionar(self, cursos_seleccionados):
        """Ejecuta el algoritmo evolutivo"""
        self.inicializar_poblacion()
        mejor_individuo = None
        mejor_fitness = float('inf')
        
        for generacion in range(self.generaciones):
            # Evaluar la población
            fitness_scores = []
            for individuo in self.poblacion:
                fitness = self.evaluar_individuo(individuo, cursos_seleccionados)
                fitness_scores.append(fitness)
                
                if fitness < mejor_fitness:
                    mejor_fitness = fitness
                    mejor_individuo = individuo.clonar()
            
            print(f"Generación {generacion + 1}: Mejor fitness = {mejor_fitness}")
            
            # Crear nueva población
            nueva_poblacion = []
            
            # Elitismo: mantener el mejor individuo
            if mejor_individuo:
                nueva_poblacion.append(mejor_individuo.clonar())
            
            # Generar el resto de la población
            while len(nueva_poblacion) < self.tam_poblacion:
                # Selección de padres
                padre1 = self.seleccion_torneo(self.poblacion, fitness_scores)
                padre2 = self.seleccion_torneo(self.poblacion, fitness_scores)
                
                # Cruce y mutación
                hijo = self.cruce(padre1, padre2)
                hijo = self.mutacion(hijo)
                
                nueva_poblacion.append(hijo)
            
            self.poblacion = nueva_poblacion
        
        # Si no se encontró un buen individuo, crear uno predeterminado
        if not mejor_individuo or mejor_fitness == float('inf'):
            mejor_individuo = self.crear_individuo_predeterminado()
        
        return mejor_individuo
    
    def crear_individuo_predeterminado(self):
        """Crea un individuo predeterminado para casos donde la evolución no encuentra buenas soluciones"""
        # Estrategia simple: Secuencia(Compactar, MoverMañana)
        raiz = Secuencia()
        raiz.agregar_hijo(Compactar())
        raiz.agregar_hijo(MoverMañana())
        return raiz

# Funciones auxiliares
def calcular_tiempos_muertos(horario):
    """Calcula los tiempos muertos en el horario"""
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

def evaluar_horario(horario):
    """Evalúa la calidad de un horario (menor es mejor)"""
    tiempos_muertos = calcular_tiempos_muertos(horario)
    
    # Penalización por cursos no asignados
    cursos_asignados = sum(1 for dia in horario for bloque in dia if bloque is not None)
    penalizacion_no_asignados = max(0, 10 - cursos_asignados) * 10
    
    return tiempos_muertos * 10 + penalizacion_no_asignados

# Interfaz para el usuario
class SistemaOptimizacionHorarios:
    def __init__(self, archivo_carga_horaria):
        self.carga_horaria = self.cargar_carga_horaria(archivo_carga_horaria)
        self.cursos_disponibles = self.obtener_cursos_disponibles()
    
    def cargar_carga_horaria(self, archivo):
        """Carga la carga horaria desde un archivo Excel"""
        try:
            df = pd.read_excel(archivo, index_col=0)  # Primera columna es el índice (horas)
            carga_horaria = []
            
            # Para cada día (columna)
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
        except Exception as e:
            print(f"Error al cargar la carga horaria: {e}")
            # Retornar una carga horaria vacía en caso de error
            return [([None] * 14) for _ in range(5)]
    
    def obtener_cursos_disponibles(self):
        """Obtiene la lista de cursos únicos de la carga horaria"""
        cursos = {}
        for dia in self.carga_horaria:
            for bloque in dia:
                if bloque and bloque['id'] not in cursos:
                    cursos[bloque['id']] = bloque
        return cursos
    
    def mostrar_cursos_disponibles(self):
        """Muestra los cursos disponibles para selección"""
        print("\nCursos disponibles:")
        for id, curso in self.cursos_disponibles.items():
            print(f"{id}: {curso['nombre']} - Prof. {curso['profesor']} ({curso['tipo']})")
    
    def seleccionar_cursos(self):
        """Permite al usuario seleccionar los cursos que desea"""
        self.mostrar_cursos_disponibles()
        seleccionados = []
        
        while True:
            entrada = input("\nIngrese el ID del curso (o 'fin' para terminar): ")
            if entrada.lower() == 'fin':
                break
            
            try:
                curso_id = int(entrada)
                if curso_id in self.cursos_disponibles:
                    if curso_id not in seleccionados:
                        seleccionados.append(curso_id)
                        print(f"Curso {self.cursos_disponibles[curso_id]['nombre']} añadido")
                    else:
                        print("Curso ya seleccionado")
                else:
                    print("ID de curso no válido")
            except ValueError:
                print("Por favor ingrese un número válido")
        
        return seleccionados
    
    def optimizar_horario(self, cursos_seleccionados):
        """Optimiza el horario para los cursos seleccionados"""
        if not cursos_seleccionados:
            print("No se han seleccionado cursos")
            return None
        
        print(f"\nOptimizando horario para {len(cursos_seleccionados)} cursos...")
        
        optimizador = ProgramacionGeneticaOptimizador(self.carga_horaria)
        mejor_individuo = optimizador.evolucionar(cursos_seleccionados)
        
        horario_inicial = optimizador.crear_horario_inicial(cursos_seleccionados)
        horario_final = mejor_individuo.ejecutar(horario_inicial, cursos_seleccionados)
        
        return horario_final
    
    def visualizar_horario(self, horario):
        """Visualiza el horario generado"""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{7+i}:00" for i in range(14)]
        
        plt.figure(figsize=(12, 8))
        
        matriz = np.zeros((5, 14))
        texto = np.empty((5, 14), dtype=object)
        colores = {}
        contador_color = 1
        
        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    curso = horario[dia][bloque]
                    if curso['id'] not in colores:
                        colores[curso['id']] = contador_color
                        contador_color += 1
                    matriz[dia, bloque] = colores[curso['id']]
                    texto[dia, bloque] = curso['nombre']
        
        plt.imshow(matriz, cmap='viridis', aspect='auto')
        
        for dia in range(5):
            for bloque in range(14):
                if texto[dia, bloque] is not None:
                    plt.text(bloque, dia, texto[dia, bloque], ha='center', va='center', color='white')
        
        plt.yticks(range(5), dias)
        plt.xticks(range(14), horas, rotation=90)
        plt.title('Horario Optimizado')
        plt.tight_layout()
        plt.colorbar(label='Cursos')
        plt.show()
    
    def ejecutar(self):
        """Ejecuta el sistema completo"""
        print("Sistema de Optimización de Horarios")
        print("===================================")
        
        # Permitir al usuario seleccionar cursos
        cursos_seleccionados = self.seleccionar_cursos()
        
        if cursos_seleccionados:
            # Optimizar horario
            horario_optimizado = self.optimizar_horario(cursos_seleccionados)
            
            if horario_optimizado:
                # Mostrar resultados
                print("\nHorario optimizado generado:")
                tiempos_muertos = calcular_tiempos_muertos(horario_optimizado)
                print(f"Tiempos muertos: {tiempos_muertos}")
                
                # Visualizar horario
                self.visualizar_horario(horario_optimizado)
                
                # Guardar en Excel si se desea
                guardar = input("\n¿Desea guardar el horario en Excel? (s/n): ")
                if guardar.lower() == 's':
                    self.guardar_horario_excel(horario_optimizado)
        else:
            print("No se seleccionaron cursos. Saliendo...")
    
    def guardar_horario_excel(self, horario):
        """Guarda el horario en un archivo Excel"""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas = [f"{7+i}:00" for i in range(14)]
        
        df = pd.DataFrame(index=horas, columns=dias)
        
        for dia in range(5):
            for bloque in range(14):
                if horario[dia][bloque] is not None:
                    curso = horario[dia][bloque]
                    df.iloc[bloque, dia] = f"{curso['nombre']}\n{curso['profesor']}"
        
        archivo = f"horario_optimizado_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(archivo)
        print(f"Horario guardado en: {archivo}")

# Programa principal
if __name__ == "__main__":
    import sys
    
    # Si no se proporciona archivo, generar uno de ejemplo
    if len(sys.argv) < 2:
        print("Generando archivo de carga horaria de ejemplo...")
        import generador_carga_horaria
        generador_carga_horaria.generar_carga_horaria_ejemplo()
        archivo = 'carga_horaria_ejemplo.xlsx'
    else:
        archivo = sys.argv[1]
    
    # Ejecutar el sistema
    try:
        sistema = SistemaOptimizacionHorarios(archivo)
        sistema.ejecutar()
    except Exception as e:
        print(f"Error: {e}")
        print("Asegúrese de que el archivo tenga el formato correcto:")