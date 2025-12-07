"""
main.py - [translate:APUNTAL PRINCIPAL - VENTANA CON PESTAÑAS]
│
│ Propósito:
│ • Inicializa base de datos
│ • Lanza gui/main_window.py con 5 pestañas
│ • Centrada 1200x800 profesional
"""

import tkinter as tk
from database.operations import (
    inicializar_base_de_datos,
)
from gui.main_window import MainWindow


# ========================================
# 🚀 FUNCIÓN PRINCIPAL
# ========================================
def main():
    """BLOQUE 1: Inicializa DB + lanza MainWindow con pestañas"""
    # Inicializa base de datos (sin prints de debug)
    inicializar_base_de_datos()

    # Lanza ventana principal con pestañas
    app = MainWindow()
    app.run()


# ========================================
# 🏃‍♂️ EJECUTAR
# ========================================
if __name__ == "__main__":
    main()
