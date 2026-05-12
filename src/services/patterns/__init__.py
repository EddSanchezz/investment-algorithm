"""
Módulo de Detección de Patrones y Análisis de Volatilidad.

Componentes:
- SlidingWindowAnalyzer: Detecta patrones mediante ventanas deslizantes
  - Patrón 1: Días consecutivos al alza
  - Patrón 2: Gap Up (apertura significativamente superior al cierre anterior)
- VolatilityAnalyzer: Calcula métricas de riesgo y clasifica activos
  - Desviación estándar de retornos diarios
  - Volatilidad histórica anualizada
  - Clasificación: Conservador / Moderado / Agresivo
"""

from src.services.patterns.sliding_window import (
    PatternAnalyzer,
    detect_consecutive_up,
    detect_gap_up,
)
from src.services.patterns.volatility import VolatilityAnalyzer

__all__ = ["PatternAnalyzer", "VolatilityAnalyzer", "detect_consecutive_up", "detect_gap_up"]
