"""
gui/main_window.py - DASHBOARD TRYHARDS COMPLETO CON LOGO + CAMBIO DE LOGO
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

from utils.config import LOGO_PATH
from utils.styles import apply_styles, TECH_COLORS
from gui.admin_panel import AdminPanel
from gui.recargas_tab import RecargasTab
from gui.remesas_tab import RemesasTab
from gui.historial_tab import HistorialTab

class MainWindow:
    def __init__(self, root):  # CAMBIADO: Recibe root como parámetro
        self.root = root  # CAMBIADO: Usa la ventana ya creada

        # ESTILOS GLOBALES
        self.style, self.colors = apply_styles(self.root)

        # referencias a tabs
        self.notebook = None
        self.dashboard_tab = None      # Referencia para el dashboard
        self.recargas_tab = None
        self.remesas_tab = None
        self.historial_tab = None

        # Cargar configuración del logo
        self.logo_config = self._cargar_configuracion_logo()

        self._create_header()
        self._create_tabs()

    # ---------------------------------
    # CONFIGURACIÓN DEL LOGO
    # ---------------------------------
    def _cargar_configuracion_logo(self):
        """Carga la configuración del logo, crea archivo si no existe"""
        config_path = "config/app_config.json"

        # Si no existe la carpeta config, la crea
        if not os.path.exists("config"):
            os.makedirs("config")

        # Si no existe el archivo, lo crea con valores por defecto
        if not os.path.exists(config_path):
            config_default = {
                "custom_logo": None,  # None = usa logo por defecto
                "company_name": "TRYHARDS"
            }
            with open(config_path, "w", encoding='utf-8') as f:
                json.dump(config_default, f, indent=4)
            return config_default

        # Si existe, lo carga
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Si hay error, usa valores por defecto
            return {"custom_logo": None, "company_name": "TRYHARDS"}

    def _guardar_configuracion_logo(self):
        """Guarda la configuración actual del logo"""
        config_path = "config/app_config.json"
        try:
            with open(config_path, "w", encoding='utf-8') as f:
                json.dump(self.logo_config, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error guardando configuración: {e}")

    def _obtener_logo_path_actual(self):
        """Obtiene la ruta del logo actual (personalizado o por defecto)"""
        custom_logo = self.logo_config.get("custom_logo")

        # Verificar si el logo personalizado existe y es válido
        if custom_logo and os.path.exists(custom_logo):
            try:
                # Verificar que sea una imagen válida
                Image.open(custom_logo)
                return custom_logo
            except Exception:
                print(f"⚠️ Logo personalizado inválido, usando por defecto: {custom_logo}")
                return LOGO_PATH
        else:
            return LOGO_PATH

    def _cargar_logo_actual(self):
        """Carga el logo actual (personalizado o por defecto)"""
        logo_path = self._obtener_logo_path_actual()

        try:
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(logo_img)
                return self.logo
            else:
                raise FileNotFoundError(f"Logo no encontrado: {logo_path}")
        except Exception as e:
            print(f"⚠️ Error cargando logo: {e}")
            # Retornar None para usar el logo de texto
            return None

    def _cambiar_logo(self):
        """Abre diálogo para cambiar el logo"""
        # Tipos de archivo permitidos
        filetypes = [
            ("Imágenes", "*.png *.jpg *.jpeg *.ico"),
            ("Todos los archivos", "*.*")
        ]

        # Abrir diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar nuevo logo",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )

        if not file_path:
            return  # Usuario canceló

        # Verificar que sea una imagen válida
        try:
            # Intentar abrir la imagen
            test_img = Image.open(file_path)
            test_img.verify()  # Verificar integridad del archivo
            test_img.close()

            # Si pasa la verificación, actualizar el logo
            self.logo_config["custom_logo"] = file_path
            self._guardar_configuracion_logo()

            # Recargar el logo
            self._actualizar_logo_header()

            messagebox.showinfo("✅ Éxito", "Logo cambiado correctamente")

        except Exception as e:
            messagebox.showerror("❌ Error",
                f"No se pudo cargar la imagen:\n{str(e)}\n\n"
                f"Asegúrate de que sea un archivo de imagen válido (PNG, JPG, JPEG, ICO).")

    def _actualizar_logo_header(self):
        """Actualiza el logo en el header"""
        # Cargar el nuevo logo
        nuevo_logo = self._cargar_logo_actual()

        if nuevo_logo:
            # Actualizar la imagen del label
            self.logo_label.config(image=nuevo_logo)
            self.logo_label.image = nuevo_logo  # Mantener referencia
        else:
            # Si no se pudo cargar imagen, mostrar logo de texto
            self.logo_label.config(
                image='',
                text="🏢",
                font=("Segoe UI", 60, "bold"),
                bg=self.colors["bg_secondary"],
                fg=self.colors["primary"]
            )

    def _restaurar_logo_predeterminado(self):
        """Restaura el logo por defecto"""
        respuesta = messagebox.askyesno(
            "Restaurar Logo",
            "¿Estás seguro de querer restaurar el logo predeterminado?\n\n"
            "Se perderá el logo personalizado actual."
        )

        if respuesta:
            self.logo_config["custom_logo"] = None
            self._guardar_configuracion_logo()
            self._actualizar_logo_header()
            messagebox.showinfo("✅ Restaurado", "Logo predeterminado restaurado")

    # ---------------------------------
    # HEADER: LOGO + TÍTULO TRYHARDS
    # ---------------------------------
    def _create_header(self):
        """HEADER: LOGO GRANDE + TÍTULO CENTRADO + BOTONES LOGO"""
        header = tk.Frame(self.root, bg=self.colors["bg_secondary"], height=140)
        header.pack(fill=tk.X, padx=25, pady=(25, 15))
        header.pack_propagate(False)

        # FRAME DEL LOGO (izquierda)
        logo_frame = tk.Frame(header, bg=self.colors["bg_secondary"])
        logo_frame.pack(side=tk.LEFT, padx=(5, 35), pady=10)

        # Cargar logo actual
        logo_image = self._cargar_logo_actual()

        # LOGO (imagen o texto)
        if logo_image:
            self.logo_label = tk.Label(
                logo_frame,
                image=logo_image,
                bg=self.colors["bg_secondary"]
            )
        else:
            self.logo_label = tk.Label(
                logo_frame,
                text="🏢",
                font=("Segoe UI", 60, "bold"),
                bg=self.colors["bg_secondary"],
                fg=self.colors["primary"],
            )

        self.logo_label.pack()

        # TÍTULO CENTRADO
        title_frame = tk.Frame(header, bg=self.colors["bg_secondary"])
        title_frame.pack(side=tk.TOP, pady=15)

        tk.Label(
            title_frame,
            text="SISTEMA DE GESTIÓN",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_light"],
        ).pack()

        # Nombre de la empresa (cargado de configuración o por defecto)
        company_name = self.logo_config.get("company_name", "TRYHARDS")

        tk.Label(
            title_frame,
            text=company_name,
            font=("Segoe UI", 42, "bold"),
            bg=self.colors["bg_secondary"],
            fg=self.colors["primary"],
        ).pack()

        # BOTONES DE CONFIGURACIÓN DEL LOGO (derecha, bien organizados)
        botones_frame = tk.Frame(header, bg=self.colors["bg_secondary"])
        botones_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-25, y=15)

        # Botón CAMBIAR LOGO (con ícono más claro)
        btn_cambiar = tk.Button(
            botones_frame,
            text="📷 Cambiar Logo",
            command=self._cambiar_logo,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            bd=0,
            activebackground=self.colors["accent"]
        )
        btn_cambiar.pack(side=tk.LEFT, padx=(0, 5))

        # Botón RESTAURAR LOGO
        btn_restaurar = tk.Button(
            botones_frame,
            text="🔄 Restaurar",
            command=self._restaurar_logo_predeterminado,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            bd=0,
            activebackground=self.colors["primary"]
        )
        btn_restaurar.pack(side=tk.LEFT)

    # ---------------------------------
    # PESTAÑAS (SIN CAMBIOS)
    # ---------------------------------
    def _create_tabs(self):
        """CREA 5 PESTAÑAS MODERNAS"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))

        self._create_dashboard_tab(self.notebook)
        self._create_admin_tab(self.notebook)
        self._create_recargas_tab(self.notebook)
        self._create_remesas_tab(self.notebook)
        self._create_historial_tab(self.notebook)

        # cuando cambie de pestaña, refrescar catálogos si es necesario
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # evento de cambio de pestaña
    def _on_tab_changed(self, event):
        if not self.notebook:
            return
        current_tab_id = self.notebook.select()
        tab_text = self.notebook.tab(current_tab_id, "text")

        # Refrescar catálogos cuando entres a Recargas o Remesas
        if "Recargas" in tab_text and self.recargas_tab is not None:
            self.recargas_tab.recargar_catalogos()
        elif "Remesas" in tab_text and self.remesas_tab is not None:
            self.remesas_tab.recargar_catalogos()
        # Refrescar historial
        elif "Historial" in tab_text and self.historial_tab is not None:
            self.historial_tab.refrescar_historial()
        # Refrescar dashboard
        elif "Dashboard" in tab_text and self.dashboard_tab is not None:
            # Si el dashboard tiene método de refresco, llamarlo
            if hasattr(self.dashboard_tab, '_actualizar_todo'):
                self.dashboard_tab._actualizar_todo()

    # DASHBOARD - ¡ACTUALIZADO Y CORREGIDO!
    def _create_dashboard_tab(self, notebook):
        """DASHBOARD EJECUTIVO COMPLETO CON PERSONALIZACIÓN"""
        from gui.dashboard_tab import DashboardTab  # Importar la clase, NO la función

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📈 Dashboard")

        # Crear la instancia del dashboard premium
        self.dashboard_tab = DashboardTab(frame, self.colors)

        # ¡ESTO ES LO QUE FALTABA! - Empaquetar el dashboard
        self.dashboard_tab.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ADMIN (scrollable)
    def _create_admin_tab(self, notebook):
        """PESTAÑA ADMIN: monta AdminPanel completo con scroll vertical"""
        outer_frame = ttk.Frame(notebook)
        notebook.add(outer_frame, text="⚙️ Admin")

        # Canvas + Scrollbar vertical
        canvas = tk.Canvas(
            outer_frame,
            bg=self.colors["bg_primary"],
            highlightthickness=0
        )
        v_scroll = ttk.Scrollbar(
            outer_frame,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame interno que contendrá el AdminPanel
        scrollable_frame = ttk.Frame(canvas)
        # crear window del frame dentro del canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # ajustar región desplazable cuando cambie tamaño del contenido
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_frame_configure)

        # opcional: que el frame se expanda al redimensionar
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)

        # montar AdminPanel dentro del frame desplazable
        admin_panel = AdminPanel(scrollable_frame)
        admin_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # RECARGAS
    def _create_recargas_tab(self, notebook):
        """PESTAÑA RECARGAS: usa RecargasTab conectado a BD en USD"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="💳 Recargas")

        self.recargas_tab = RecargasTab(frame, self.colors)
        self.recargas_tab.pack(fill=tk.BOTH, expand=True)

    # REMESAS
    def _create_remesas_tab(self, notebook):
        """PESTAÑA REMESAS: usa RemesasTab completamente funcional"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🌎 Remesas")

        self.remesas_tab = RemesasTab(frame, self.colors)
        self.remesas_tab.pack(fill=tk.BOTH, expand=True)

    # HISTORIAL
    def _create_historial_tab(self, notebook):
        """Pestaña HISTORIAL: Dashboard ejecutivo completo"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 Historial")

        self.historial_tab = HistorialTab(frame, self.colors)
        self.historial_tab.pack(fill=tk.BOTH, expand=True)

    def run(self):
        """Método mantenido para compatibilidad (ahora vacío)"""
        pass  # mainloop se maneja en main.py