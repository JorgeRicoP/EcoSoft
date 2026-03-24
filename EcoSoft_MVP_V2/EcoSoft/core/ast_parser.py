# core/ast_parser.py
# Responsabilidad: convertir código fuente Python en un árbol AST

import ast


class ASTParser:
    """Parsea código Python y retorna su árbol de sintaxis abstracta (AST)."""

    def parse(self, source_code: str) -> ast.AST:
        """
        Convierte el código fuente en un AST.

        Args:
            source_code: Código Python como cadena.

        Returns:
            El árbol AST generado por la librería estándar `ast`.

        Raises:
            SyntaxError: Si el código tiene errores de sintaxis.
        """
        try:
            tree = ast.parse(source_code)
            return tree
        except SyntaxError as e:
            raise SyntaxError(
                f"Error de sintaxis en el archivo (línea {e.lineno}): {e.msg}"
            ) from e
