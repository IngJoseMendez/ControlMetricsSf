# -*- coding: utf-8 -*-
"""
ControlMetrics – Punto de entrada
PMD y Cía S.C.A. | Sistema de Control Estadístico de Procesos
Universidad del Magdalena, 2025
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from app import SPCApp
    app = SPCApp()
    app.run()
