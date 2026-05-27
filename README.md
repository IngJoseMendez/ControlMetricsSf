# ControlMetrics — Software SPC

Sistema de **Control Estadístico de Procesos (CEP)** desarrollado para la empresa **PMD y Cía S.C.A.**, exportadora de fruta prepesada de 3 libras ubicada en la Zona Bananera del Magdalena, Colombia.

## Módulos incluidos

| Módulo | Descripción |
|--------|-------------|
| 📊 Normalidad | Pruebas de normalidad (Shapiro-Wilk, histograma, Q-Q plot) |
| 📈 Cartas X̄-R | Cartas de control por variables con análisis de potencia |
| ⚙️ Capacidad | Índices Cp, Cpk, Pp, Ppk |
| 🔵 Cartas p/np/u | Cartas de control por atributos |
| 📉 Carta C / Pareto | Carta C y diagrama de Pareto de defectos |
| 🔍 Plan de Muestreo | Muestreo por atributos (MIL-STD-105E) |
| 🔧 Plan de Mejora | Evaluación de sensibilidad y cálculo de n óptimo |

## Requisitos

```
Python 3.9+
tkinter (incluido con Python)
numpy
scipy
matplotlib
openpyxl
```

## Instalación

```bash
git clone https://github.com/TU_USUARIO/ControlMetrics-SPC.git
cd ControlMetrics-SPC
pip install numpy scipy matplotlib openpyxl
python main.py
```

## Uso

Ejecuta `main.py` para abrir la aplicación de escritorio.

## Tecnologías

- **Python 3** + **Tkinter** (interfaz gráfica)
- **Matplotlib** (visualización de cartas de control)
- **SciPy / NumPy** (cálculos estadísticos)
- Metodología basada en **Montgomery (2020)** y **MIL-STD-105E**

## Autores

Proyecto académico — Universidad del Magdalena, 2025  
Aplicado en PMD y Cía S.C.A., Zona Bananera del Magdalena, Colombia.
