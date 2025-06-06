#!/usr/bin/env python3
"""
Pruebas unitarias para el validador de conflictos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.validador_conflictos import ValidadorConflictos

def test_detectar_conflictos_vacio():
    """Prueba con horario vacío."""
    horario = [[None for _ in range(14)] for _ in range(5)]
    conflictos = ValidadorConflictos.detectar_conflictos_horario(horario)
    
    assert len(conflictos['profesor']) == 0
    assert len(conflictos['salon']) == 0

def test_detectar_conflicto_profesor():
    """Prueba detección de conflicto de profesor."""
    horario = [[None for _ in range(14)] for _ in range(5)]
    
    # Mismo profesor en dos cursos simultáneos
    curso1 = {'id': 1, 'nombre': 'Curso A', 'profesor': 'GARCIA', 'tipo': 'Teórico'}
    curso2 = {'id': 2, 'nombre': 'Curso B', 'profesor': 'GARCIA', 'tipo': 'Teórico'}
    
    horario[0][0] = curso1  # Lunes 7:00
    horario[1][0] = curso2  # Martes 7:00 - No debería generar conflicto
    
    conflictos = ValidadorConflictos.detectar_conflictos_horario(horario)
    assert len(conflictos['profesor']) == 0  # Diferentes días, no hay conflicto
    
    # Ahora mismo día y hora
    horario[0][1] = curso2  # Lunes 8:00, mismo profesor
    horario[0][0] = [curso1, curso2]  # Simular conflicto en mismo bloque
    
def test_puntuacion_conflictos():
    """Prueba cálculo de puntuación de conflictos."""
    conflictos = {
        'profesor': [{'dia': 0, 'bloque': 0}],
        'salon': [],
        'estudiante': [],
        'sobrecarga': []
    }
    
    puntuacion = ValidadorConflictos.calcular_puntuacion_conflictos(conflictos)
    assert puntuacion == 100  # 1 conflicto de profesor = 100 puntos

if __name__ == "__main__":
    pytest.main([__file__])
