# Optimizador de Horarios con Programación Genética

Este proyecto implementa un sistema de optimización de horarios académicos usando Programación Genética (PG) completamente desde cero, sin fines de llucro

## Características Principales

- **Selección de cursos por usuario**: Los estudiantes pueden seleccionar sus cursos de una carga horaria preestablecida
- **Programación Genética desde cero**: Implementación completa del algoritmo evolutivo sin dependencias
- **Representación en árbol**: Evoluciona estrategias para optimizar horarios
- **Minimización de tiempos muertos**: El objetivo principal es reducir los espacios vacíos entre clases

## Estructura del Proyecto

```
├── pg_desde_cero.py          # Implementación principal de PG
├── generador_carga_horaria.py # Generador de datos de ejemplo
├── ejecutar_optimizador.py    # Script principal para ejecutar el sistema
├── README.md                  # Este archivo
```

## Requisitos

- Python 3.7+
- numpy
- pandas
- matplotlib

Instalar dependencias:
```bash
pip install numpy pandas matplotlib openpyxl
```

## Estructura del Archivo Excel

El archivo Excel debe tener la siguiente estructura:

- **Primera columna**: Horas del día (formato: "7:00 - 8:00")
- **Columnas restantes**: Días de la semana (Lunes a Viernes)
- **Celdas**: Formato "id|nombre_curso|profesor|tipo"

Ejemplo de celda: `1|Cálculo I|García|Teórico`

## Cómo Usar

### 1. Generar una carga horaria de ejemplo:

```bash
python ejecutar_optimizador.py generar
```

### 2. Ejecutar el optimizador:

```bash
# Usar archivo de ejemplo
python ejecutar_optimizador.py

# Usar archivo específico
python ejecutar_optimizador.py mi_carga_horaria.xlsx
```

### 3. Proceso de optimización:

1. El sistema mostrará los cursos disponibles
2. El usuario selecciona los cursos que desea tomar escribiendo los IDs
3. El algoritmo evolutivo optimiza el horario
4. Se muestra el horario optimizado con métricas
5. Opción de guardar el resultado en Excel

## Cómo Funciona la Programación Genética

### Representación en Árbol

Cada individuo es un árbol con:
- **Nodos funcionales**: `if_tiempo_muerto`, `secuencia`, `probar_alternativas`
- **Nodos terminales**: `compactar`, `mover_mañana`, `intercambio_aleatorio`, etc.

### Proceso Evolutivo

1. **Inicialización**: Población de árboles aleatorios
2. **Evaluación**: Cada árbol optimiza un horario y se evalúa su calidad
3. **Selección**: Torneo entre individuos
4. **Reproducción**: Cruce de árboles e intercambio de subárboles
5. **Mutación**: Reemplazo de subárboles
6. **Reemplazo**: Nueva generación con elitismo

### Función de Fitness

La calidad de un horario se evalúa según:
- Número de tiempos muertos entre clases
- Penalización por cursos no asignados
- Distribución de clases a lo largo de la semana

## Ejemplo de Uso

```python
from pg_desde_cero import SistemaOptimizacionHorarios

# Cargar carga horaria
sistema = SistemaOptimizacionHorarios('carga_horaria_ejemplo.xlsx')

# Ejecutar sistema completo
sistema.ejecutar()
```

## Resultados Esperados

El sistema genera:
- Un horario optimizado que minimiza tiempos muertos
- Visualización gráfica del horario
- Métricas de calidad (tiempos muertos, distribución)
- Archivo Excel con el horario resultante

## Limitaciones y Consideraciones

- El sistema no considera restricciones específicas de aulas
- No incorpora preferencias de horarios específicas
- La optimización puede variar entre ejecuciones debido a la naturaleza estocástica del algoritmo

## Mejoras Futuras

- Agregar restricciones de capacidad de aulas
- Considerar preferencias de horarios por estudiante
- Implementar optimización multiobjetivo
- Añadir interfaz gráfica de usuario

## Autor

Desarrollado como proyecto académico para la Facultad de Ciencias de la Universidad Nacional de Ingeniería.