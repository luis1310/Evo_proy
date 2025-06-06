# 📖 Manual de Usuario - Sistema de Optimización de Horarios

## 🚀 Inicio Rápido

### 1. Instalación
```bash
python setup_y_configuracion/requirements_setup.py
```

### 2. Verificación
```bash
python setup_y_configuracion/verificar_instalacion.py
```

### 3. Primer Uso
```bash
python scripts/optimizar.py
```

## 📋 Uso Detallado

### Procesar Archivo PDF
```bash
python scripts/optimizar.py datos/Horarios_2023_1.pdf
```

El sistema automáticamente:
1. Extrae cursos del PDF
2. Identifica horarios, profesores y salones
3. Permite seleccionar cursos
4. Optimiza el horario
5. Muestra resultados y conflictos

### Procesar Archivo Excel
```bash
python scripts/optimizar.py datos/carga_horaria.xlsx
```

### Generar Datos de Prueba
```bash
python scripts/generar_datos.py
```

## 🎯 Selección de Cursos

Durante la ejecución puede seleccionar cursos usando:

- **IDs individuales**: `1, 5, 10, 15`
- **Rangos**: `1-20` (cursos del 1 al 20)
- **Por escuela**: `BF` (todos los cursos de Física)
- **Todos**: `todos` (seleccionar todos los cursos)
- **Finalizar**: `fin`

## 📊 Interpretación de Resultados

### Métricas de Calidad
- **Bloques ocupados**: Número total de horas asignadas
- **Tiempos muertos**: Espacios vacíos entre clases
- **Compactación**: Qué tan agrupadas están las clases
- **Distribución**: Uniformidad de carga semanal

### Tipos de Conflictos
- **🧑‍🏫 Profesor**: Mismo profesor en dos lugares simultáneamente
- **🏫 Salón**: Mismo salón con múltiples clases
- **⚡ Sobrecarga**: Profesores con exceso de horas

### Valores Ideales
- **Tiempos muertos**: 0-2 (excelente), 3-5 (bueno), 6+ (mejorable)
- **Conflictos**: 0 (perfecto), 1-2 (aceptable), 3+ (requiere revisión)

## 🔧 Solución de Problemas

### "Error al leer PDF"
- Verifique que el PDF no esté protegido
- Asegúrese de que contenga texto seleccionable

### "No se encontraron cursos"
- Revise el formato del archivo
- Pruebe con datos generados: `python scripts/optimizar.py`

### "Optimización sin resultados"
- Reduzca el número de cursos seleccionados
- Verifique que no haya demasiados conflictos iniciales

## 📁 Archivos Generados

El sistema crea automáticamente:
- `datos/resultados/horario_optimizado_*.xlsx` - Horarios optimizados
- `datos/resultados/reporte_conflictos_*.txt` - Reportes de conflictos
- `datos/carga_horaria_generada_*.xlsx` - Datos de prueba generados

## 🎮 Ejemplos Interactivos

```bash
# Ejemplo completo automático
python ejemplos/ejemplo_completo.py

# Ejemplo específico para PDF
python ejemplos/ejemplo_pdf.py

# Ejemplo específico para Excel  
python ejemplos/ejemplo_excel.py
```
