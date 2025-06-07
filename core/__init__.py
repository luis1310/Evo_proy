# 1. ARCHIVO: core/__init__.py
# Reemplazar completamente el contenido actual

"""
Módulo core unificado con lector de horarios integrado.
"""

from .validador_conflictos import ValidadorConflictos
from .optimizador_genetico import ProgramacionGeneticaOptimizadorMejorado
from .nodos_geneticos import IntercambioInteligente, ResolverConflictos

# Imports del lector unificado
from .lector_horarios import (
    LectorHorarios,           # Lector principal unificado
    LectorPDFHorarios,        # Lector PDF específico (si se necesita acceso directo)
    LectorExcelUniversitario, # Lector Excel universitario específico (si se necesita acceso directo)
    test_lector_unificado     # Función de prueba
)

# Mantener compatibilidad con imports antiguos
LectorExcelHorarios = LectorExcelUniversitario  # Alias para compatibilidad

__all__ = [
    'ValidadorConflictos',
    'ProgramacionGeneticaOptimizadorMejorado', 
    'IntercambioInteligente',
    'ResolverConflictos',
    'LectorHorarios',          # Principal
    'LectorPDFHorarios',       # Específico PDF
    'LectorExcelUniversitario', # Específico Excel universitario
    'LectorExcelHorarios',     # Alias para compatibilidad
    'test_lector_unificado'
]
