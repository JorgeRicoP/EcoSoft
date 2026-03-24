# utils/file_loader.py
# Responsabilidad: cargar y validar archivos .py del sistema de archivos

import os


class FileLoader:
    """Carga un archivo Python desde el disco y devuelve su contenido."""

    ALLOWED_EXTENSION = ".py"

    def load(self, filepath: str) -> str:
        """
        Carga el contenido de un archivo .py.

        Args:
            filepath: Ruta absoluta o relativa al archivo.

        Returns:
            Contenido del archivo como cadena de texto.

        Raises:
            ValueError: Si la extensión no es .py.
            FileNotFoundError: Si el archivo no existe.
            IOError: Si ocurre un error de lectura.
        """
        if not filepath.endswith(self.ALLOWED_EXTENSION):
            raise ValueError(
                f"Solo se admiten archivos Python (.py). "
                f"Se recibió: '{os.path.basename(filepath)}'"
            )

        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"No se encontró el archivo: '{filepath}'")

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def get_filename(self, filepath: str) -> str:
        """Devuelve solo el nombre del archivo (sin la ruta completa)."""
        return os.path.basename(filepath)
