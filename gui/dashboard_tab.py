"""
gui/dashboard_tab.py - DASHBOARD MEJORADO
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
import os

# Importar solo la función que necesitamos
try:
    from database.operations import obtener_resumen_ganancias
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ Dashboard: No se pudo importar obtener_resumen_ganancias")

class DashboardTab(ttk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent)
        self.colors = colors

        # Frame principal
        main_frame = tk.Frame(self, bg=self.colors["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título principal - MÁS GRANDE
        tk.Label(
            main_frame,
            text="📊 DASHBOARD TRYHARDS",
            font=("Segoe UI", 40, "bold"),  # Aumentado de 36 a 40
            bg=self.colors["bg_primary"],
            fg=self.colors["primary"]
        ).pack(pady=(70, 10))

        # Subtítulo - MÁS GRANDE
        tk.Label(
            main_frame,
            text="Sistema de Gestión de Recargas y Remesas",
            font=("Segoe UI", 20),  # Aumentado de 18 a 20
            bg=self.colors["bg_primary"],
            fg=self.colors["text_light"]
        ).pack(pady=(0, 40))

        # **CONTENEDOR DE DATOS REALES**
        datos_frame = tk.Frame(main_frame, bg=self.colors["bg_card"])
        datos_frame.pack(pady=20, padx=80, fill=tk.X)  # Menos padding lateral

        # Título de la sección de datos - MÁS GRANDE
        tk.Label(
            datos_frame,
            text="📈 RESUMEN DEL DÍA",
            font=("Segoe UI", 18, "bold"),  # Aumentado de 16 a 18
            bg=self.colors["bg_card"],
            fg=self.colors["accent"]
        ).pack(pady=(15, 25))  # Más espacio

        # **FILA 1: DOS DATOS PRINCIPALES**
        fila1 = tk.Frame(datos_frame, bg=self.colors["bg_card"])
        fila1.pack(pady=(0, 15))

        # 1. TOTAL TRANSACCIONES HOY - TEXTO MÁS GRANDE
        frame_transacciones = tk.Frame(fila1, bg=self.colors["bg_card"])
        frame_transacciones.pack(side=tk.LEFT, expand=True)

        tk.Label(
            frame_transacciones,
            text="🔄 TRANSACCIONES HOY",
            font=("Segoe UI", 14, "bold"),  # Aumentado de 12 a 14
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"]
        ).pack()

        self.label_transacciones_hoy = tk.Label(
            frame_transacciones,
            text="Cargando...",
            font=("Segoe UI", 28, "bold"),  # Aumentado de 24 a 28
            bg=self.colors["bg_card"],
            fg=self.colors["success"]
        )
        self.label_transacciones_hoy.pack(pady=(8, 5))

        tk.Label(
            frame_transacciones,
            text="Recargas + Remesas",
            font=("Segoe UI", 12),  # Aumentado de 10 a 12
            bg=self.colors["bg_card"],
            fg=self.colors["text_dark"]
        ).pack()

        # Separador vertical
        tk.Frame(
            fila1,
            bg=self.colors["primary"],
            width=2,
            height=80  # Más alto
        ).pack(side=tk.LEFT, padx=40)  # Más espacio

        # 2. GANANCIA TOTAL HOY - TEXTO MÁS GRANDE
        frame_ganancia = tk.Frame(fila1, bg=self.colors["bg_card"])
        frame_ganancia.pack(side=tk.LEFT, expand=True)

        tk.Label(
            frame_ganancia,
            text="💰 GANANCIA TOTAL HOY",
            font=("Segoe UI", 14, "bold"),  # Aumentado de 12 a 14
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"]
        ).pack()

        self.label_ganancia_hoy = tk.Label(
            frame_ganancia,
            text="Cargando...",
            font=("Segoe UI", 28, "bold"),  # Aumentado de 24 a 28
            bg=self.colors["bg_card"],
            fg=self.colors["success"]
        )
        self.label_ganancia_hoy.pack(pady=(8, 5))

        tk.Label(
            frame_ganancia,
            text="Ganancia neta (dueño)",
            font=("Segoe UI", 12),  # Aumentado de 10 a 12
            bg=self.colors["bg_card"],
            fg=self.colors["text_dark"]
        ).pack()

        # **ESPACIO PARA MÁS DATOS FUTUROS** (en lugar del mensaje eliminado)
        espacio_futuro = tk.Frame(main_frame, bg=self.colors["bg_primary"], height=50)
        espacio_futuro.pack(fill=tk.X, pady=(30, 20))

        # Separador
        separator = tk.Frame(main_frame, height=2, bg=self.colors["primary"])
        separator.pack(fill=tk.X, pady=20, padx=80)

        # **FOOTER MEJORADO - CON MARCA PERSONAL MÁS GRANDE**
        footer_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 30))

        # Frame interno para centrar contenido
        footer_inner = tk.Frame(footer_frame, bg=self.colors["bg_primary"])
        footer_inner.pack()

        # Texto "Creado por:" - MÁS GRANDE
        tk.Label(
            footer_inner,
            text="Desarrollado por",
            font=("Segoe UI", 12, "bold"),  # Aumentado y con bold
            bg=self.colors["bg_primary"],
            fg=self.colors["text_light"]
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Cargar y mostrar tu marca personal - MÁS GRANDE
        self._cargar_marca_personal(footer_inner)

        # Separador y versión - MÁS GRANDE
        tk.Label(
            footer_inner,
            text="•",
            font=("Segoe UI", 12),
            bg=self.colors["bg_primary"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT, padx=8)

        tk.Label(
            footer_inner,
            text="Versión 1.0",
            font=("Segoe UI", 12),  # Aumentado
            bg=self.colors["bg_primary"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT)

        # Cargar datos reales después de crear la interfaz
        self._cargar_datos_reales()

    def _cargar_marca_personal(self, parent):
        """Carga y muestra la marca personal en el footer - MÁS GRANDE"""
        try:
            # Ruta de la imagen
            marca_path = "icons/logobajo.png"

            # Verificar si existe
            if os.path.exists(marca_path):
                # Cargar imagen
                marca_img = Image.open(marca_path)

                # Redimensionar manteniendo proporción - MÁS GRANDE (40px de alto)
                img_height = 40  # Aumentado de 25 a 40
                img_width = int(marca_img.width * (img_height / marca_img.height))
                marca_img = marca_img.resize((img_width, img_height), Image.Resampling.LANCZOS)

                # Convertir a PhotoImage
                self.marca_foto = ImageTk.PhotoImage(marca_img)

                # Mostrar imagen
                tk.Label(
                    parent,
                    image=self.marca_foto,
                    bg=self.colors["bg_primary"]
                ).pack(side=tk.LEFT, padx=(0, 10))
            else:
                # Si no existe la imagen, mostrar texto alternativo - MÁS GRANDE
                tk.Label(
                    parent,
                    text="[MI MARCA]",
                    font=("Segoe UI", 14, "bold", "italic"),  # Aumentado
                    bg=self.colors["bg_primary"],
                    fg=self.colors["accent"]
                ).pack(side=tk.LEFT, padx=(0, 10))

        except Exception as e:
            # En caso de error, mostrar texto - MÁS GRANDE
            print(f"⚠️ Error cargando marca personal: {e}")
            tk.Label(
                parent,
                text="[MARCA]",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg_primary"],
                fg=self.colors["accent"]
            ).pack(side=tk.LEFT, padx=(0, 10))

    def _cargar_datos_reales(self):
        """Carga los datos reales del día"""
        if not DATABASE_AVAILABLE:
            self.label_transacciones_hoy.config(text="Error BD", fg="red")
            self.label_ganancia_hoy.config(text="Error BD", fg="red")
            return

        try:
            # Obtener la fecha de hoy
            hoy = datetime.now().strftime("%Y-%m-%d")

            # Llamar a la MISMA función que usa historial_tab.py
            resumen = obtener_resumen_ganancias(hoy, hoy)

            # 1. Total de transacciones (recargas + remesas)
            total_transacciones = resumen.get('total_transacciones', 0)
            self.label_transacciones_hoy.config(text=str(total_transacciones))

            # 2. Ganancia total hoy (dueño)
            ganancia_usd = resumen.get('ganancia_neta_dueño_usd', 0)
            ganancia_usdt = resumen.get('ganancia_neta_dueño_usdt', 0)
            ganancia_total = ganancia_usd + ganancia_usdt

            self.label_ganancia_hoy.config(text=f"${ganancia_total:,.2f}")

        except Exception as e:
            print(f"❌ Error cargando datos en dashboard: {e}")
            self.label_transacciones_hoy.config(text="Error", fg="red")
            self.label_ganancia_hoy.config(text="Error", fg="red")

    def refrescar_dashboard(self):
        """Método llamado desde main_window al cambiar de pestaña"""
        self._cargar_datos_reales()