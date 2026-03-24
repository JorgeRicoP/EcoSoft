# main.py
# Punto de entrada de EcoSoft – Ejecuta: python main.py

import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Inicializa la ventana principal y arranca el loop de eventos."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
