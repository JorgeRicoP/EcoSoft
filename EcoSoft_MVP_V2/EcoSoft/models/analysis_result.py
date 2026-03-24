# models/analysis_result.py
# Responsabilidad: encapsular los resultados del análisis energético

from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisResult:
    """
    Contiene todos los datos resultantes del análisis de un archivo Python.

    Atributos:
        filename       : Nombre del archivo analizado.
        energy_score   : Puntuación heurística de consumo energético.
        classification : 'Bajo', 'Medio' o 'Alto'.
        metrics        : Diccionario con los conteos de cada patrón detectado.
        recommendations: Lista de mensajes de optimización.
        error          : Mensaje de error si el análisis falló (opcional).
    """

    filename: str = ""
    energy_score: float = 0.0
    classification: str = ""
    metrics: dict = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    error: str = ""

    def is_valid(self) -> bool:
        """Devuelve True si el análisis se completó sin errores."""
        return self.error == ""
