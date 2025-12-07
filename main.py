"""
main.py - [translate:APUNTAL PRINCIPAL - VENTANA CON PESTAÑAS]
│
│ Propósito:
│ • Inicializa base de datos
│ • Lanza gui/main_window.py con 5 pestañas
│ • Centrada 1200x800 profesional
"""

import tkinter as tk
import os
import sys
from PIL import Image, ImageTk
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

    # Crea ventana principal
    root = tk.Tk()
    root.title("Sistema De Gestión Tryhards")
    root.geometry("1400x900")
    root.minsize(1200, 700)

    # **MÉTODO ALTERNATIVO PARA ÍCONO**
    try:
        ico_path = os.path.join("icons", "app.ico")
        ico_path_abs = os.path.abspath(ico_path)

        print(f"🔍 Buscando ícono en: {ico_path_abs}")
        print(f"📂 Existe: {os.path.exists(ico_path_abs)}")

        if os.path.exists(ico_path_abs):
            # PRIMERO: Método normal
            root.iconbitmap(ico_path_abs)
            print("✅ Método 1: iconbitmap aplicado")

            # SEGUNDO: Método para Windows (forzar)
            if sys.platform == "win32":
                try:
                    # Limpiar caché de íconos de Windows
                    import ctypes

                    # ID único
                    app_id = 'Tryhards.Sistema.Gestion.v1'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    print("✅ Método 2: AppUserModelID configurado")

                    # También intentar con wm_iconbitmap
                    root.tk.call('wm', 'iconbitmap', root._w, ico_path_abs)
                    print("✅ Método 3: wm_iconbitmap aplicado")

                except Exception as e:
                    print(f"⚠️ Método Windows: {e}")

            # TERCERO: Usar PhotoImage como respaldo
            try:
                img = Image.open(ico_path_abs)
                photo = ImageTk.PhotoImage(img)
                root.iconphoto(True, photo)  # True = usar para todos los diálogos
                print("✅ Método 4: iconphoto aplicado")
            except:
                print("⚠️ Método iconphoto no funcionó")

        else:
            print(f"❌ ERROR: Archivo no encontrado")
            print(f"   Ruta probada: {ico_path_abs}")
            print(f"   Directorio actual: {os.getcwd()}")
            print(f"   Contenido de icons/: {os.listdir('icons')}")

    except Exception as e:
        print(f"⚠️ Error general: {e}")
        import traceback
        traceback.print_exc()

    # Crea y ejecuta la aplicación
    app = MainWindow(root)  # Pasa la ventana ya creada
    root.mainloop()


# ========================================
# 🏃‍♂️ EJECUTAR
# ========================================
if __name__ == "__main__":
    main()