# core/analyzer.py
# Responsabilidad: coordinar el análisis completo de un archivo Python

import ast
from typing import Dict

from core.ast_parser import ASTParser
from core.energy_model import EnergyModel
from models.analysis_result import AnalysisResult
from utils.file_loader import FileLoader


# ---------------------------------------------------------------------------
# CodeVisitor – recorre el AST y recolecta métricas
# ---------------------------------------------------------------------------

class CodeVisitor(ast.NodeVisitor):
    """
    Visita cada nodo del AST y acumula conteos de patrones costosos.

    Métricas recolectadas:
        - loops        : bucles for/while de primer nivel
        - nested_loops : bucles que contienen otro bucle directamente
        - recursion    : funciones que se llaman a sí mismas
        - large_lists  : list comprehensions
        - redundancy   : nombres de función que se repiten
    """

    def __init__(self):
        self.metrics: Dict[str, int] = {
            "loops": 0,
            "nested_loops": 0,
            "recursion": 0,
            "large_lists": 0,
            "redundancy": 0,
        }
        # Registro de nombres de funciones para detectar redundancias
        self._function_names: list = []
        # Nombre de la función que se está visitando actualmente
        self._current_function: str = ""
        # Nivel de profundidad de bucles (para detectar anidamiento)
        self._loop_depth: int = 0

    # -----------------------------------------------------------------------
    # Detección de bucles simples y anidados
    # -----------------------------------------------------------------------

    def _visit_loop(self, node):
        """Lógica común para For y While."""
        if self._loop_depth == 0:
            self.metrics["loops"] += 1

        self._loop_depth += 1

        # Si ya estamos dentro de otro bucle, es un bucle anidado
        if self._loop_depth > 1:
            self.metrics["nested_loops"] += 1

        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_For(self, node):
        self._visit_loop(node)

    def visit_While(self, node):
        self._visit_loop(node)

    # -----------------------------------------------------------------------
    # Detección de recursividad
    # -----------------------------------------------------------------------

    def visit_FunctionDef(self, node):
        """Registra el nombre de la función y busca llamadas recursivas."""
        prev_function = self._current_function
        self._current_function = node.name

        # Detectar redundancia de nombres
        if node.name in self._function_names:
            self.metrics["redundancy"] += 1
        else:
            self._function_names.append(node.name)

        # Visitar el cuerpo de la función para detectar auto-llamadas
        self.generic_visit(node)
        self._current_function = prev_function

    # Soportar también funciones async
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        """Detecta si una función se llama a sí misma (recursividad directa)."""
        called_name = None

        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = node.func.attr

        if called_name and called_name == self._current_function:
            self.metrics["recursion"] += 1

        self.generic_visit(node)

    # -----------------------------------------------------------------------
    # Detección de list comprehensions
    # -----------------------------------------------------------------------

    def visit_ListComp(self, node):
        """Cuenta cada list comprehension como uso de lista grande."""
        self.metrics["large_lists"] += 1
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Analyzer – orquestador principal
# ---------------------------------------------------------------------------

class Analyzer:
    """
    Coordina el flujo completo:
    FileLoader → ASTParser → CodeVisitor → EnergyModel → AnalysisResult
    """

    def __init__(self):
        self.file_loader = FileLoader()
        self.ast_parser = ASTParser()
        self.energy_model = EnergyModel()

    def analyze_source(self, source_code: str, filename: str = "<editor>") -> AnalysisResult:
        """
        Analiza código Python escrito directamente (sin necesidad de archivo).

        Args:
            source_code: Código Python como cadena de texto.
            filename   : Nombre descriptivo para mostrar en los resultados.

        Returns:
            AnalysisResult con puntaje, clasificación, métricas y recomendaciones.
        """
        result = AnalysisResult()
        result.filename = filename

        try:
            tree = self.ast_parser.parse(source_code)

            visitor = CodeVisitor()
            visitor.visit(tree)
            result.metrics = visitor.metrics

            result.energy_score = self.energy_model.calculate_score(result.metrics)
            result.classification = self.energy_model.classify(result.energy_score)
            result.recommendations = self.energy_model.generate_recommendations(
                result.metrics
            )
        except SyntaxError as e:
            result.error = str(e)
        except Exception as e:
            result.error = f"Error inesperado durante el análisis: {e}"

        return result

    def analyze(self, filepath: str) -> AnalysisResult:
        """
        Analiza un archivo Python y retorna un AnalysisResult.

        Args:
            filepath: Ruta al archivo .py a analizar.

        Returns:
            AnalysisResult con puntaje, clasificación, métricas y recomendaciones.
        """
        result = AnalysisResult()
        result.filename = self.file_loader.get_filename(filepath)

        try:
            # 1. Cargar el código fuente
            source_code = self.file_loader.load(filepath)

            # 2. Parsear a AST
            tree = self.ast_parser.parse(source_code)

            # 3. Recorrer el AST y recolectar métricas
            visitor = CodeVisitor()
            visitor.visit(tree)
            result.metrics = visitor.metrics

            # 4. Calcular puntaje energético
            result.energy_score = self.energy_model.calculate_score(result.metrics)

            # 5. Clasificar el puntaje
            result.classification = self.energy_model.classify(result.energy_score)

            # 6. Generar recomendaciones
            result.recommendations = self.energy_model.generate_recommendations(
                result.metrics
            )

        except (ValueError, FileNotFoundError) as e:
            result.error = str(e)
        except SyntaxError as e:
            result.error = str(e)
        except Exception as e:
            result.error = f"Error inesperado durante el análisis: {e}"

        return result
