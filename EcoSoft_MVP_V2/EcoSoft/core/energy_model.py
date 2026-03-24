# core/energy_model.py
# Responsabilidad: calcular el puntaje energético con base en métricas detectadas

from typing import Dict, List


class EnergyModel:
    """
    Modelo heurístico de consumo energético.

    Pesos definidos para cada tipo de patrón de código costoso.
    La fórmula es: energy_score = Σ(cantidad_métrica × peso)
    """

    # Pesos heurísticos por tipo de patrón
    WEIGHTS: Dict[str, int] = {
        "loops": 2,           # bucles for/while simples
        "nested_loops": 5,    # bucles anidados (muy costosos)
        "recursion": 4,       # funciones recursivas
        "large_lists": 3,     # list comprehensions / listas grandes
        "redundancy": 1,      # funciones o nombres duplicados
    }

    # Umbrales de clasificación
    THRESHOLDS = {
        "Bajo": (0, 10),
        "Medio": (11, 25),
        "Alto": (26, float("inf")),
    }

    def calculate_score(self, metrics: Dict[str, int]) -> float:
        """
        Calcula el puntaje energético total.

        Args:
            metrics: Conteos de cada patrón detectado.

        Returns:
            Puntaje energético (float >= 0).
        """
        score = 0.0
        for key, weight in self.WEIGHTS.items():
            count = metrics.get(key, 0)
            score += count * weight
        return score

    def classify(self, score: float) -> str:
        """
        Clasifica el puntaje en Bajo / Medio / Alto.

        Args:
            score: Puntaje calculado.

        Returns:
            Cadena con la clasificación.
        """
        if score <= 10:
            return "Bajo"
        elif score <= 25:
            return "Medio"
        else:
            return "Alto"

    def generate_recommendations(self, metrics: Dict[str, int]) -> List[str]:
        """
        Genera recomendaciones automáticas según los patrones encontrados.

        Args:
            metrics: Conteos de los patrones detectados.

        Returns:
            Lista de mensajes de recomendación.
        """
        recommendations = []

        if metrics.get("nested_loops", 0) > 0:
            recommendations.append(
                "⚠️  Evita bucles anidados: tienen complejidad O(n²) o mayor. "
                "Considera usar estructuras de datos más eficientes (diccionarios, conjuntos)."
            )

        if metrics.get("loops", 0) > 5:
            recommendations.append(
                "🔁  Tienes muchos bucles. Evalúa si puedes reemplazar algunos "
                "con funciones integradas como map(), filter() o sum()."
            )

        if metrics.get("recursion", 0) > 0:
            recommendations.append(
                "🔄  La recursividad puede consumir mucha memoria en la pila. "
                "Considera una versión iterativa o usa memoización (functools.lru_cache)."
            )

        if metrics.get("large_lists", 0) > 3:
            recommendations.append(
                "📋  Tienes varias list comprehensions. Si no necesitas la lista completa, "
                "usa generadores (gen = (x for x in ...)) para ahorrar memoria."
            )

        if metrics.get("redundancy", 0) > 0:
            recommendations.append(
                "🔍  Se detectaron posibles redundancias (funciones o nombres repetidos). "
                "Revisa si puedes refactorizar código duplicado en funciones reutilizables."
            )

        if not recommendations:
            recommendations.append(
                "✅  El código presenta un perfil energético eficiente. "
                "¡Sigue las buenas prácticas actuales!"
            )

        return recommendations
