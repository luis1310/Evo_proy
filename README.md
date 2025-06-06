# 🎓 Sistema de Optimización de Horarios Académicos

Sistema avanzado de optimización de horarios académicos utilizando programación genética, con soporte para archivos PDF y Excel, y detección automática de conflictos.

## 🚀 Características Principales

- **📄 Lectura de PDF**: Procesa automáticamente archivos PDF con horarios académicos
- **📊 Soporte Excel**: Compatible con archivos Excel en formato de matriz
- **🧬 Algoritmo Genético**: Optimización inteligente usando programación genética  
- **🔍 Detección de Conflictos**: Identifica y resuelve cruces de horarios automáticamente
- **📈 Visualización**: Gráficos interactivos y reportes detallados
- **🎯 Selección Flexible**: Selección por curso, rango o escuela completa

## 🔧 Instalación Rápida

```bash
# 1. Instalar dependencias automáticamente
python setup_y_configuracion/requirements_setup.py

# 2. Verificar instalación
python setup_y_configuracion/verificar_instalacion.py

# 3. Ejecutar ejemplo
python scripts/optimizar.py
```

## 🖥️ Uso del Sistema

### Procesar archivo PDF
```bash
python scripts/optimizar.py datos/Horarios_2023_1.pdf
```

### Procesar archivo Excel
```bash
python scripts/optimizar.py datos/carga_horaria.xlsx
```

### Generar datos de prueba
```bash
python scripts/optimizar.py
```

## 📊 Tipos de Conflictos Detectados

- ✅ **Profesores**: Clases simultáneas del mismo profesor
- ✅ **Salones**: Múltiples clases en el mismo salón
- ✅ **Sobrecarga**: Profesores con exceso de horas
- ✅ **Distribución**: Optimización de carga semanal

## 🏗️ Estructura del Proyecto

```
📦 optimizador-horarios-genetico/
├── 🧠 core/                    # Módulos principales
├── 🎲 generadores/             # Generadores de datos
├── 🖥️ interfaces/              # Interfaces de usuario
├── 📊 visualizacion/           # Gráficos y reportes
├── 🚀 scripts/                 # Scripts de ejecución
├── 📁 datos/                   # Archivos de datos
├── 🧪 ejemplos/                # Ejemplos de uso
└── 📚 docs/                    # Documentación
```

## 🧪 Ejemplos de Uso

Ver el directorio `ejemplos/` para casos de uso específicos:

- `ejemplo_completo.py` - Flujo completo del sistema
- `ejemplo_pdf.py` - Procesamiento de PDF  
- `ejemplo_excel.py` - Procesamiento de Excel

## 🤝 Contribuciones

Este proyecto fue desarrollado como sistema académico para optimización de horarios universitarios.

## 📄 Licencia

Proyecto Académico - Universidad Nacional Mayor de San Marcos  
Facultad de Ciencias Físicas

---
**Desarrollado por**: Equipo de Programación Genética  
**Versión**: 2.0 con detección de conflictos
