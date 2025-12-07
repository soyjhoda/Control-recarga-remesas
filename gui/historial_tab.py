"""
gui/historial_tab.py - DASHBOARD EJECUTIVO COMPLETO TRYHARDS
│
│ Secciones:
│ 1. 📊 RESUMEN EJECUTIVO (ganancias, ventas, métricas clave)
│ 2. 🔍 FILTROS AVANZADOS (fechas, trabajador, tipo, país)
│ 3. 📋 TABLA DETALLADA CON TODAS LAS TRANSACCIONES
│ 4. 📈 GRÁFICOS INTERACTIVOS (clickeables)
│ 5. 👥 CALCULADORA DE COMISIONES POR TRABAJADOR
│ 6. 💰 MIS GANANCIAS PERSONALES (solo dueño)
│ 7. 📤 EXPORTACIÓN A EXCEL/PDF/IMPRESIÓN
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')  # Para compatibilidad con Tkinter

from database.operations import (
    obtener_transacciones_combinadas,
    obtener_resumen_ganancias,
    obtener_comisiones_trabajador,
    obtener_ganancias_por_dia,
    obtener_top_trabajadores,
    listar_trabajadores_activos,
    listar_paises_activos,
    listar_recargas,
    listar_remesas
)
from reports.generator import (
    exportar_a_excel,
    exportar_a_pdf,
    exportar_dashboard,
    generar_reporte_comisiones
)
from utils.helpers import format_currency
from utils.styles import TECH_COLORS

class HistorialTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style="Card.TFrame")

        # Variables de filtro
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()
        self.trabajador_var = tk.StringVar(value="todos")
        self.tipo_var = tk.StringVar(value="todos")
        self.pais_var = tk.StringVar(value="todos")

        # Variables para gráficos
        self.figuras_graficos = []  # Para mantener referencia a las figuras
        self.canvas_graficos = []   # Para mantener referencia a los canvas

        # Caches
        self.trabajadores = []
        self.paises = []

        # Crear canvas con scroll
        self._crear_scrollable_frame()

        # Construir UI
        self._build_ui()
        self._cargar_catalogos()
        self._cargar_datos_iniciales()

    # ========================================
    # SCROLLABLE FRAME
    # ========================================
    def _crear_scrollable_frame(self):
        """Crea un frame con scrollbar vertical"""
        # Crear canvas y scrollbar
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bg=self.colors["bg_primary"],
            relief='flat'
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar"
        )

        # Frame que contendrá todo (dentro del canvas)
        self.scrollable_frame = ttk.Frame(
            self.canvas,
            style="Card.TFrame"
        )

        # Configurar scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Crear ventana en el canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetar
        self.canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        self.scrollbar.pack(side="right", fill="y", padx=0, pady=0)

    # ========================================
    # UI PRINCIPAL
    # ========================================
    def _build_ui(self):
        """Construye toda la interfaz del dashboard"""
        # Título principal
        title = tk.Label(
            self.scrollable_frame,
            text="📊 DASHBOARD EJECUTIVO - HISTORIAL COMPLETO",
            font=("Segoe UI", 22, "bold"),
            foreground=self.colors["primary"],  # Usar color primario para el título
            background=self.colors["bg_card"]
        )
        title.pack(pady=(15, 5))

        # Sección 1: RESUMEN EJECUTIVO
        self._crear_seccion_resumen()

        # Sección 2: FILTROS AVANZADOS
        self._crear_seccion_filtros()

        # Sección 3: TABLA DE TRANSACCIONES
        self._crear_seccion_tabla()

        # Sección 4: GRÁFICOS
        self._crear_seccion_graficos()

        # Sección 5: COMISIONES TRABAJADORES
        self._crear_seccion_comisiones()

        # Sección 6: MIS GANANCIAS
        self._crear_seccion_mis_ganancias()

        # Sección 7: EXPORTACIÓN
        self._crear_seccion_exportacion()

    # ========================================
    # SECCIÓN 1: RESUMEN EJECUTIVO
    # ========================================
    def _crear_seccion_resumen(self):
        """Crea la sección de resumen ejecutivo"""
        resumen_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📈 RESUMEN EJECUTIVO",
            padding=20
        )
        resumen_frame.pack(fill="x", padx=20, pady=10)

        # 4 tarjetas de métricas
        metrics_container = ttk.Frame(resumen_frame)
        metrics_container.pack(fill="x", expand=True)

        # Tarjeta 1: Ganancia Total
        self.tarjeta_ganancia = self._crear_tarjeta_metrica(
            metrics_container,
            "💰 GANANCIA TOTAL",
            "$0.00",
            "Ganancia neta (dueño)",
            0
        )

        # Tarjeta 2: Transacciones Hoy
        self.tarjeta_transacciones = self._crear_tarjeta_metrica(
            metrics_container,
            "📊 TRANSACCIONES HOY",
            "0",
            "Recargas + Remesas",
            1
        )

        # Tarjeta 3: Comisiones a Pagar
        self.tarjeta_comisiones = self._crear_tarjeta_metrica(
            metrics_container,
            "👥 COMISIONES A PAGAR",
            "$0.00",
            "Total a trabajadores",
            2
        )

        # Tarjeta 4: Top Trabajador
        self.tarjeta_top_trabajador = self._crear_tarjeta_metrica(
            metrics_container,
            "🏆 TOP TRABAJADOR",
            "N/A",
            "Más productivo",
            3
        )

    def _crear_tarjeta_metrica(self, parent, titulo, valor, subtitulo, columna):
        """Crea una tarjeta de métrica individual"""
        tarjeta = tk.Frame(
            parent,
            bg=self.colors["bg_card"],
            relief="solid",
            bd=1,
            highlightbackground=self.colors["primary"],
            highlightthickness=1
        )
        tarjeta.grid(row=0, column=columna, padx=5, pady=5, sticky="nsew")
        parent.grid_columnconfigure(columna, weight=1)

        # Título - Cambiado a color oscuro para mejor visibilidad
        tk.Label(
            tarjeta,
            text=titulo,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_card"],
            fg="#333333"  # Cambiado de text_light a gris oscuro
        ).pack(pady=(10, 5))

        # Valor (se actualizará)
        valor_label = tk.Label(
            tarjeta,
            text=valor,
            font=("Segoe UI", 24, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["success"]
        )
        valor_label.pack(pady=5)

        # Subtítulo - Cambiado a color oscuro
        tk.Label(
            tarjeta,
            text=subtitulo,
            font=("Segoe UI", 9),
            bg=self.colors["bg_card"],
            fg="#666666"  # Cambiado de text_dark a gris medio
        ).pack(pady=(0, 10))

        return valor_label

    # ========================================
    # SECCIÓN 2: FILTROS AVANZADOS
    # ========================================
    def _crear_seccion_filtros(self):
        """Crea la sección de filtros avanzados"""
        filtros_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="🔍 FILTROS AVANZADOS",
            padding=20
        )
        filtros_frame.pack(fill="x", padx=20, pady=10)

        # Fila 1: Fechas
        fecha_frame = ttk.Frame(filtros_frame)
        fecha_frame.pack(fill="x", pady=(0, 10))

        # Cambiar colores de etiquetas a oscuro
        tk.Label(fecha_frame, text="📅 Fecha desde:",
                 foreground="#333333",  # Gris oscuro
                 background=self.colors["bg_primary"]).pack(side="left", padx=(0, 5))

        # Establecer fechas por defecto (últimos 30 días)
        fecha_inicio_default = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        fecha_fin_default = datetime.now().strftime("%Y-%m-%d")

        self.fecha_inicio_var.set(fecha_inicio_default)
        tk.Entry(fecha_frame, textvariable=self.fecha_inicio_var,
                width=12, bg="white", fg="black").pack(side="left", padx=5)

        tk.Label(fecha_frame, text="hasta:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).pack(side="left", padx=(10, 5))

        self.fecha_fin_var.set(fecha_fin_default)
        tk.Entry(fecha_frame, textvariable=self.fecha_fin_var,
                width=12, bg="white", fg="black").pack(side="left", padx=5)

        # Botones rápidos de fecha
        ttk.Button(fecha_frame, text="Hoy",
                  command=lambda: self._establecer_fecha_hoy()).pack(side="left", padx=5)
        ttk.Button(fecha_frame, text="Última semana",
                  command=lambda: self._establecer_fecha_semana()).pack(side="left", padx=5)
        ttk.Button(fecha_frame, text="Último mes",
                  command=lambda: self._establecer_fecha_mes()).pack(side="left", padx=5)

        # Fila 2: Filtros adicionales
        filtros_row = tk.Frame(filtros_frame, bg=self.colors["bg_primary"])
        filtros_row.pack(fill="x", pady=(0, 10))

        # Trabajador
        tk.Label(filtros_row, text="👤 Trabajador:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).grid(row=0, column=0, padx=(0, 5))
        self.combo_trabajador = ttk.Combobox(
            filtros_row,
            textvariable=self.trabajador_var,
            width=20,
            state="readonly"
        )
        self.combo_trabajador.grid(row=0, column=1, padx=5)

        # Tipo
        tk.Label(filtros_row, text="📋 Tipo:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).grid(row=0, column=2, padx=(10, 5))
        tipo_combo = ttk.Combobox(
            filtros_row,
            textvariable=self.tipo_var,
            values=["todos", "RECARGA", "REMESA"],
            width=12,
            state="readonly"
        )
        tipo_combo.grid(row=0, column=3, padx=5)

        # País
        tk.Label(filtros_row, text="🌍 País:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).grid(row=0, column=4, padx=(10, 5))
        self.combo_pais = ttk.Combobox(
            filtros_row,
            textvariable=self.pais_var,
            width=15,
            state="readonly"
        )
        self.combo_pais.grid(row=0, column=5, padx=5)

        # Botones de acción
        btn_frame = ttk.Frame(filtros_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="🔄 APLICAR FILTROS",
            command=self._aplicar_filtros,
            style="Primary.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="🧹 LIMPIAR FILTROS",
            command=self._limpiar_filtros,
            style="Danger.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="📊 ACTUALIZAR TODO",
            command=self._actualizar_todo
        ).pack(side="left", padx=5)

    # ========================================
    # SECCIÓN 3: TABLA DE TRANSACCIONES
    # ========================================
    def _crear_seccion_tabla(self):
        """Crea la sección de tabla de transacciones"""
        tabla_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📋 TRANSACCIONES DETALLADAS",
            padding=15
        )
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Frame interno para tabla y scrollbar
        tabla_inner_frame = ttk.Frame(tabla_frame)
        tabla_inner_frame.pack(fill="both", expand=True)

        # Treeview con scroll
        tree_scroll_y = ttk.Scrollbar(
            tabla_inner_frame,
            style="Vertical.TScrollbar"
        )
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ttk.Scrollbar(
            tabla_inner_frame,
            orient="horizontal",
            style="Horizontal.TScrollbar"
        )
        tree_scroll_x.pack(side="bottom", fill="x")

        # Definir columnas
        cols = ("id", "fecha", "tipo", "trabajador", "pais", "moneda", "monto", "ganancia", "comision", "notas")
        self.tree_transacciones = ttk.Treeview(
            tabla_inner_frame,
            columns=cols,
            show="headings",
            height=12,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            style="Custom.Treeview"
        )

        tree_scroll_y.config(command=self.tree_transacciones.yview)
        tree_scroll_x.config(command=self.tree_transacciones.xview)

        # Configurar columnas
        column_widths = {
            "id": 60,
            "fecha": 100,
            "tipo": 80,
            "trabajador": 120,
            "pais": 100,
            "moneda": 80,
            "monto": 100,
            "ganancia": 100,
            "comision": 100,
            "notas": 150
        }

        for col in cols:
            display_name = col.upper().replace("_", " ")
            if col == "id":
                display_name = "ID"
            elif col == "monto":
                display_name = "MONTO"
            elif col == "ganancia":
                display_name = "GANANCIA"
            elif col == "comision":
                display_name = "COMISIÓN"

            self.tree_transacciones.heading(col, text=display_name)
            self.tree_transacciones.column(col, width=column_widths.get(col, 100))

        self.tree_transacciones.pack(side="left", fill="both", expand=True)

        # Configurar tags para filas alternadas
        self.tree_transacciones.tag_configure('oddrow', background=self.colors["table_odd"])
        self.tree_transacciones.tag_configure('evenrow', background=self.colors["table_even"])
        self.tree_transacciones.tag_configure('recarga', foreground=self.colors["primary"])
        self.tree_transacciones.tag_configure('remesa', foreground=self.colors["accent"])

        # Contador de registros - Cambiado a color oscuro
        self.contador_registros = tk.Label(
            tabla_frame,
            text="Mostrando 0 registros",
            foreground="#333333",  # Gris oscuro
            background=self.colors["bg_card"]
        )
        self.contador_registros.pack(side="bottom", anchor="w", pady=(5, 0))

    # ========================================
    # SECCIÓN 4: GRÁFICOS INTERACTIVOS
    # ========================================
    def _crear_seccion_graficos(self):
        """Crea la sección de gráficos interactivos"""
        graficos_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📈 GRÁFICOS Y ESTADÍSTICAS",
            padding=15
        )
        graficos_frame.pack(fill="x", padx=20, pady=10)

        # Contenedor para gráficos (2 columnas)
        graficos_container = ttk.Frame(graficos_frame)
        graficos_container.pack(fill="both", expand=True)

        # Gráfico 1: Ganancias diarias (columna 0)
        self.frame_grafico1 = ttk.Frame(graficos_container)
        self.frame_grafico1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Gráfico 2: Distribución por tipo (columna 1)
        self.frame_grafico2 = ttk.Frame(graficos_container)
        self.frame_grafico2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        graficos_container.grid_columnconfigure(0, weight=1)
        graficos_container.grid_columnconfigure(1, weight=1)

        # Botones de control de gráficos
        btn_graficos_frame = ttk.Frame(graficos_frame)
        btn_graficos_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_graficos_frame,
            text="📊 ACTUALIZAR GRÁFICOS",
            command=self._actualizar_graficos
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_graficos_frame,
            text="💾 GUARDAR GRÁFICOS",
            command=self._guardar_graficos
        ).pack(side="left", padx=5)

    # ========================================
    # SECCIÓN 5: COMISIONES TRABAJADORES
    # ========================================
    def _crear_seccion_comisiones(self):
        """Crea la sección de cálculo de comisiones"""
        comisiones_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="👥 CALCULADORA DE COMISIONES",
            padding=20
        )
        comisiones_frame.pack(fill="x", padx=20, pady=10)

        # Fila 1: Selección de trabajador y fechas
        seleccion_frame = tk.Frame(comisiones_frame, bg=self.colors["bg_primary"])
        seleccion_frame.pack(fill="x", pady=(0, 10))

        # Cambiar colores a oscuro
        tk.Label(seleccion_frame, text="Trabajador:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).pack(side="left", padx=(0, 5))

        self.combo_trabajador_comisiones = ttk.Combobox(
            seleccion_frame,
            width=25,
            state="readonly"
        )
        self.combo_trabajador_comisiones.pack(side="left", padx=5)

        tk.Label(seleccion_frame, text="Desde:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).pack(side="left", padx=(10, 5))

        self.fecha_comision_inicio = tk.Entry(seleccion_frame, width=12, bg="white", fg="black")
        self.fecha_comision_inicio.pack(side="left", padx=5)
        self.fecha_comision_inicio.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(seleccion_frame, text="Hasta:",
                 foreground="#333333",
                 background=self.colors["bg_primary"]).pack(side="left", padx=(5, 5))

        self.fecha_comision_fin = tk.Entry(seleccion_frame, width=12, bg="white", fg="black")
        self.fecha_comision_fin.pack(side="left", padx=5)
        self.fecha_comision_fin.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Fila 2: Resultados de comisiones
        self.resultados_frame = tk.Frame(comisiones_frame, bg=self.colors["bg_primary"])
        self.resultados_frame.pack(fill="x", pady=(10, 0))

        # Inicialmente vacío, se llenará al calcular

        # Fila 3: Botones de acción
        btn_comisiones_frame = ttk.Frame(comisiones_frame)
        btn_comisiones_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_comisiones_frame,
            text="🧮 CALCULAR COMISIONES",
            command=self._calcular_comisiones,
            style="Primary.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_comisiones_frame,
            text="📄 GENERAR REPORTE",
            command=self._generar_reporte_comisiones,
            style="Success.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_comisiones_frame,
            text="📋 VER DETALLES",
            command=self._ver_detalles_comisiones
        ).pack(side="left", padx=5)

    # ========================================
    # SECCIÓN 6: MIS GANANCIAS
    # ========================================
    def _crear_seccion_mis_ganancias(self):
        """Crea la sección de ganancias personales del dueño"""
        ganancias_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="💰 MIS GANANCIAS PERSONALES",
            padding=20
        )
        ganancias_frame.pack(fill="x", padx=20, pady=10)

        # Contenedor para métricas de ganancias
        ganancias_container = tk.Frame(ganancias_frame, bg=self.colors["bg_primary"])
        ganancias_container.pack(fill="x", pady=(0, 10))

        # 3 métricas clave
        self.metrica_ganancia_neta = self._crear_metrica_ganancia(
            ganancias_container,
            "💵 GANANCIA NETA",
            "$0.00",
            "Total (dueño)",
            0
        )

        self.metrica_ganancia_recargas = self._crear_metrica_ganancia(
            ganancias_container,
            "🎮 DE RECARGAS",
            "$0.00",
            "Solo recargas",
            1
        )

        self.metrica_ganancia_remesas = self._crear_metrica_ganancia(
            ganancias_container,
            "🌍 DE REMESAS",
            "$0.00",
            "Solo remesas",
            2
        )

        ganancias_container.grid_columnconfigure(0, weight=1)
        ganancias_container.grid_columnconfigure(1, weight=1)
        ganancias_container.grid_columnconfigure(2, weight=1)

        # Filtro rápido para mis ganancias
        filtro_rapido_frame = tk.Frame(ganancias_frame, bg=self.colors["bg_primary"])
        filtro_rapido_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            filtro_rapido_frame,
            text="📅 HOY",
            command=lambda: self._filtrar_mis_ganancias("hoy")
        ).pack(side="left", padx=2)

        ttk.Button(
            filtro_rapido_frame,
            text="📅 ESTA SEMANA",
            command=lambda: self._filtrar_mis_ganancias("semana")
        ).pack(side="left", padx=2)

        ttk.Button(
            filtro_rapido_frame,
            text="📅 ESTE MES",
            command=lambda: self._filtrar_mis_ganancias("mes")
        ).pack(side="left", padx=2)

        ttk.Button(
            filtro_rapido_frame,
            text="📅 PERSONALIZADO",
            command=self._filtrar_mis_ganancias_personalizado
        ).pack(side="left", padx=2)

    def _crear_metrica_ganancia(self, parent, titulo, valor, subtitulo, columna):
        """Crea una métrica individual de ganancias"""
        frame = tk.Frame(
            parent,
            bg=self.colors["bg_card"],
            relief="solid",
            bd=1
        )
        frame.grid(row=0, column=columna, padx=5, pady=5, sticky="nsew")

        # Título - Cambiado a color oscuro
        tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg="#333333"  # Cambiado de text_light a gris oscuro
        ).pack(pady=(5, 2))

        valor_label = tk.Label(
            frame,
            text=valor,
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["success"]
        )
        valor_label.pack(pady=2)

        # Subtítulo - Cambiado a color oscuro
        tk.Label(
            frame,
            text=subtitulo,
            font=("Segoe UI", 8),
            bg=self.colors["bg_card"],
            fg="#666666"  # Cambiado de text_dark a gris medio
        ).pack(pady=(2, 5))

        return valor_label

    # ========================================
    # SECCIÓN 7: EXPORTACIÓN
    # ========================================
    def _crear_seccion_exportacion(self):
        """Crea la sección de exportación de reportes"""
        export_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📤 EXPORTAR REPORTES",
            padding=20
        )
        export_frame.pack(fill="x", padx=20, pady=(10, 20))

        # Botones de exportación
        btn_export_frame = ttk.Frame(export_frame)
        btn_export_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            btn_export_frame,
            text="📊 EXPORTAR DASHBOARD (EXCEL)",
            command=self._exportar_dashboard_excel,
            style="Success.TButton"
        ).pack(side="left", padx=5, pady=5)

        ttk.Button(
            btn_export_frame,
            text="📋 EXPORTAR TRANSACCIONES (EXCEL)",
            command=self._exportar_transacciones_excel
        ).pack(side="left", padx=5, pady=5)

        ttk.Button(
            btn_export_frame,
            text="📄 EXPORTAR A PDF",
            command=self._exportar_a_pdf
        ).pack(side="left", padx=5, pady=5)

        # Información de exportación - Cambiado a color oscuro
        info_frame = tk.Frame(export_frame, bg=self.colors["bg_primary"])
        info_frame.pack(fill="x", pady=(5, 0))

        tk.Label(
            info_frame,
            text="📁 Los reportes se guardan en la carpeta 'reports/'",
            font=("Segoe UI", 9),
            foreground="#333333",  # Gris oscuro
            background=self.colors["bg_primary"]
        ).pack(side="left")

        ttk.Button(
            info_frame,
            text="📂 ABRIR CARPETA",
            command=self._abrir_carpeta_reportes
        ).pack(side="right", padx=5)

    # ========================================
    # FUNCIONES DE CARGA DE DATOS
    # ========================================
    def _cargar_catalogos(self):
        """Carga los catálogos necesarios"""
        try:
            # Trabajadores
            self.trabajadores = listar_trabajadores_activos()
            nombres_trab = ['todos'] + [t['name'] for t in self.trabajadores]
            self.combo_trabajador['values'] = nombres_trab
            self.combo_trabajador_comisiones['values'] = [t['name'] for t in self.trabajadores]

            # Países
            self.paises = listar_paises_activos()
            nombres_pais = ['todos'] + [p['name'] for p in self.paises]
            self.combo_pais['values'] = nombres_pais

        except Exception as e:
            print(f"Error al cargar catálogos: {e}")

    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales al abrir la pestaña"""
        self._aplicar_filtros()
        self._actualizar_resumen()
        self._actualizar_graficos()

    # ========================================
    # FUNCIONES DE FILTROS
    # ========================================
    def _aplicar_filtros(self):
        """Aplica los filtros y actualiza la tabla"""
        try:
            # Obtener valores de filtros
            fecha_inicio = self.fecha_inicio_var.get()
            fecha_fin = self.fecha_fin_var.get()
            trabajador = self.trabajador_var.get()
            tipo = self.tipo_var.get()
            pais = self.pais_var.get()

            # Convertir trabajador a ID si no es "todos"
            worker_id = None
            if trabajador != "todos":
                for t in self.trabajadores:
                    if t['name'] == trabajador:
                        worker_id = t['id']
                        break

            # Obtener transacciones filtradas
            transacciones = obtener_transacciones_combinadas(
                fecha_inicio=fecha_inicio if fecha_inicio else None,
                fecha_fin=fecha_fin if fecha_fin else None,
                worker_id=worker_id,
                tipo=tipo if tipo != "todos" else None
            )

            # Filtrar por país si es necesario
            if pais != "todos":
                transacciones = [t for t in transacciones if t.get('country_name') == pais]

            # Actualizar tabla
            self._actualizar_tabla(transacciones)

            # Actualizar resumen con los mismos filtros
            self._actualizar_resumen(fecha_inicio, fecha_fin, worker_id)

            # Actualizar mis ganancias
            self._actualizar_mis_ganancias(fecha_inicio, fecha_fin)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron aplicar los filtros:\n{str(e)}")

    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.fecha_inicio_var.set("")
        self.fecha_fin_var.set("")
        self.trabajador_var.set("todos")
        self.tipo_var.set("todos")
        self.pais_var.set("todos")
        self._aplicar_filtros()

    def _actualizar_todo(self):
        """Actualiza todo el dashboard"""
        self._aplicar_filtros()
        self._actualizar_graficos()

    # Funciones de fechas rápidas
    def _establecer_fecha_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        self.fecha_inicio_var.set(hoy)
        self.fecha_fin_var.set(hoy)
        self._aplicar_filtros()

    def _establecer_fecha_semana(self):
        hoy = datetime.now()
        semana_pasada = hoy - timedelta(days=7)
        self.fecha_inicio_var.set(semana_pasada.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        self._aplicar_filtros()

    def _establecer_fecha_mes(self):
        hoy = datetime.now()
        mes_pasado = hoy - timedelta(days=30)
        self.fecha_inicio_var.set(mes_pasado.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        self._aplicar_filtros()

    # ========================================
    # FUNCIONES DE TABLA
    # ========================================
    def _actualizar_tabla(self, transacciones):
        """Actualiza la tabla con las transacciones proporcionadas"""
        # Limpiar tabla
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        if not transacciones:
            self.contador_registros.config(text="No hay registros para mostrar")
            return

        # Llenar tabla
        for i, trans in enumerate(transacciones):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tipo_tag = 'recarga' if trans.get('tipo') == 'RECARGA' else 'remesa'

            # Formatear valores
            monto = trans.get('monto', 0)
            ganancia = trans.get('ganancia', 0)
            comision = trans.get('comision', 0)

            monto_str = f"${monto:,.2f}" if monto else ""
            ganancia_str = f"${ganancia:,.2f}" if ganancia else ""
            comision_str = f"${comision:,.2f}" if comision else ""

            # Insertar en tabla
            self.tree_transacciones.insert(
                "",
                "end",
                tags=(tag, tipo_tag),
                values=(
                    trans.get('id', ''),
                    trans.get('date', ''),
                    trans.get('tipo', ''),
                    trans.get('worker_name', ''),
                    trans.get('country_name', ''),
                    trans.get('currency_code', ''),
                    monto_str,
                    ganancia_str,
                    comision_str,
                    (trans.get('notes', '') or '')[:30] + ('...' if len(trans.get('notes', '') or '') > 30 else '')
                )
            )

        self.contador_registros.config(text=f"Mostrando {len(transacciones)} registros")

    # ========================================
    # FUNCIONES DE RESUMEN
    # ========================================
    def _actualizar_resumen(self, fecha_inicio=None, fecha_fin=None, worker_id=None):
        """Actualiza el resumen ejecutivo"""
        try:
            # Obtener resumen de ganancias
            resumen = obtener_resumen_ganancias(fecha_inicio, fecha_fin)

            # Actualizar tarjeta de ganancia total
            ganancia_neta = resumen.get('ganancia_neta_dueño_usd', 0) + resumen.get('ganancia_neta_dueño_usdt', 0)
            self.tarjeta_ganancia.config(text=f"${ganancia_neta:,.2f}")

            # Actualizar tarjeta de transacciones
            total_transacciones = resumen.get('total_transacciones', 0)
            self.tarjeta_transacciones.config(text=str(total_transacciones))

            # Actualizar tarjeta de comisiones
            comisiones_totales = resumen.get('comisiones_total_usd', 0) + resumen.get('comisiones_total_usdt', 0)
            self.tarjeta_comisiones.config(text=f"${comisiones_totales:,.2f}")

            # Actualizar tarjeta de top trabajador
            top_trabajadores = obtener_top_trabajadores(1, fecha_inicio, fecha_fin)
            if top_trabajadores:
                nombre_top = top_trabajadores[0]['nombre']
                ganancia_top = top_trabajadores[0]['ganancia_generada']
                self.tarjeta_top_trabajador.config(text=f"{nombre_top}\n(${ganancia_top:,.2f})")
            else:
                self.tarjeta_top_trabajador.config(text="N/A")

        except Exception as e:
            print(f"Error al actualizar resumen: {e}")

    # ========================================
    # FUNCIONES DE GRÁFICOS
    # ========================================
    def _actualizar_graficos(self):
        """Actualiza los gráficos con datos actuales"""
        try:
            # Limpiar gráficos anteriores
            for canvas in self.canvas_graficos:
                canvas.get_tk_widget().destroy()
            self.figuras_graficos.clear()
            self.canvas_graficos.clear()

            # Obtener datos para gráficos
            ganancias_diarias = obtener_ganancias_por_dia(7)
            resumen = obtener_resumen_ganancias()

            # Crear gráfico 1: Ganancias diarias
            self._crear_grafico_ganancias_diarias(ganancias_diarias)

            # Crear gráfico 2: Distribución por tipo
            self._crear_grafico_distribucion_tipo(resumen)

        except Exception as e:
            print(f"Error al actualizar gráficos: {e}")

    def _crear_grafico_ganancias_diarias(self, datos):
        """Crea gráfico de ganancias diarias"""
        if not datos:
            return

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors["bg_card"])
        ax = fig.add_subplot(111)

        # Configurar colores del gráfico
        ax.set_facecolor(self.colors["bg_card"])
        fig.patch.set_facecolor(self.colors["bg_card"])

        # Extraer datos
        fechas = [d['fecha'] for d in datos]
        ganancias = [d['ganancia_total'] for d in datos]
        comisiones = [d['comisiones_total'] for d in datos]

        # Crear gráfico de barras
        x = range(len(fechas))
        width = 0.35

        ax.bar([i - width/2 for i in x], ganancias, width, label='Ganancia', color=self.colors["primary"])
        ax.bar([i + width/2 for i in x], comisiones, width, label='Comisiones', color=self.colors["accent"])

        # Configurar eje X
        ax.set_xticks(x)
        ax.set_xticklabels([f.split('-')[-1] for f in fechas], color="#333333")  # Gris oscuro

        # Configurar eje Y
        ax.set_ylabel('USD', color="#333333")  # Gris oscuro
        ax.tick_params(axis='y', colors="#333333")  # Gris oscuro

        # Título y leyenda
        ax.set_title('Ganancias vs Comisiones (Últimos 7 días)', color=self.colors["primary"], fontweight='bold')
        ax.legend(facecolor=self.colors["bg_card"], edgecolor=self.colors["primary"])

        # Añadir grid
        ax.grid(True, alpha=0.3, color="#666666")  # Gris medio

        # Ajustar layout
        fig.tight_layout()

        # Añadir al frame
        canvas = FigureCanvasTkAgg(fig, self.frame_grafico1)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Guardar referencia
        self.figuras_graficos.append(fig)
        self.canvas_graficos.append(canvas)

        # Hacer interactivo (click)
        canvas.mpl_connect('button_press_event', lambda event: self._on_grafico_click(event, 'diario'))

    def _crear_grafico_distribucion_tipo(self, resumen):
        """Crea gráfico de distribución por tipo"""
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors["bg_card"])
        ax = fig.add_subplot(111)

        # Configurar colores
        ax.set_facecolor(self.colors["bg_card"])
        fig.patch.set_facecolor(self.colors["bg_card"])

        # Datos
        labels = ['Recargas', 'Remesas']
        ganancias = [
            resumen.get('ganancia_total_usd', 0),
            resumen.get('ganancia_total_usdt', 0)
        ]
        comisiones = [
            resumen.get('comisiones_total_usd', 0),
            resumen.get('comisiones_total_usdt', 0)
        ]

        # Crear gráfico de barras apiladas
        x = range(len(labels))

        ax.bar(x, ganancias, label='Ganancia', color=self.colors["primary"])
        ax.bar(x, comisiones, bottom=ganancias, label='Comisiones', color=self.colors["accent"])

        # Configurar
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color="#333333")  # Gris oscuro
        ax.set_ylabel('USD/USDT', color="#333333")  # Gris oscuro
        ax.tick_params(axis='y', colors="#333333")  # Gris oscuro

        # Título
        ax.set_title('Distribución por Tipo de Transacción', color=self.colors["primary"], fontweight='bold')
        ax.legend(facecolor=self.colors["bg_card"], edgecolor=self.colors["primary"])

        # Añadir valores encima de las barras
        for i, (g, c) in enumerate(zip(ganancias, comisiones)):
            total = g + c
            if total > 0:
                ax.text(i, total + max(ganancias + comisiones) * 0.02,
                       f'${total:,.0f}', ha='center', color="#333333")  # Gris oscuro

        # Ajustar layout
        fig.tight_layout()

        # Añadir al frame
        canvas = FigureCanvasTkAgg(fig, self.frame_grafico2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Guardar referencia
        self.figuras_graficos.append(fig)
        self.canvas_graficos.append(canvas)

        # Hacer interactivo
        canvas.mpl_connect('button_press_event', lambda event: self._on_grafico_click(event, 'distribucion'))

    def _on_grafico_click(self, event, tipo_grafico):
        """Maneja clicks en los gráficos"""
        if event.inaxes:
            messagebox.showinfo("Gráfico Interactivo",
                              f"Hiciste click en el gráfico de {tipo_grafico}\n\n"
                              f"Posición: x={event.xdata:.2f}, y={event.ydata:.2f}")

    def _guardar_graficos(self):
        """Guarda los gráficos como imágenes"""
        try:
            for i, fig in enumerate(self.figuras_graficos):
                filename = f"grafico_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                fig.savefig(f"reports/{filename}", dpi=300, facecolor=fig.get_facecolor())

            messagebox.showinfo("Éxito", "Gráficos guardados en la carpeta 'reports/'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los gráficos:\n{str(e)}")

    # ========================================
    # FUNCIONES DE COMISIONES
    # ========================================
    def _calcular_comisiones(self):
        """Calcula las comisiones para el trabajador seleccionado"""
        try:
            trabajador_nombre = self.combo_trabajador_comisiones.get()
            fecha_inicio = self.fecha_comision_inicio.get()
            fecha_fin = self.fecha_comision_fin.get()

            if not trabajador_nombre:
                messagebox.showwarning("Advertencia", "Selecciona un trabajador")
                return

            if not fecha_inicio or not fecha_fin:
                messagebox.showwarning("Advertencia", "Ingresa las fechas")
                return

            # Buscar ID del trabajador
            worker_id = None
            for t in self.trabajadores:
                if t['name'] == trabajador_nombre:
                    worker_id = t['id']
                    break

            if not worker_id:
                messagebox.showerror("Error", "Trabajador no encontrado")
                return

            # Obtener datos de comisiones
            datos = obtener_comisiones_trabajador(worker_id, fecha_inicio, fecha_fin)

            # Limpiar frame de resultados
            for widget in self.resultados_frame.winfo_children():
                widget.destroy()

            # Mostrar resultados
            tk.Label(
                self.resultados_frame,
                text=f"📋 REPORTE DE COMISIONES - {trabajador_nombre}",
                font=("Segoe UI", 12, "bold"),
                foreground=self.colors["primary"],
                bg=self.colors["bg_primary"]
            ).pack(anchor="w", pady=(0, 10))

            # Crear tabla simple
            datos_tabla = [
                ("Periodo:", f"{fecha_inicio} a {fecha_fin}"),
                ("Total Transacciones:", str(datos['total_transacciones'])),
                ("Recargas:", str(datos['total_recargas'])),
                ("Remesas:", str(datos['total_remesas'])),
                ("Venta Recargas:", f"${datos['total_venta_usd']:,.2f}"),
                ("Venta Remesas:", f"{datos['total_venta_origen']:,.2f}"),
                ("Comisiones Recargas:", f"${datos['total_comisiones_usd']:,.2f}"),
                ("Comisiones Remesas:", f"{datos['total_comisiones_usdt']:,.4f} USDT"),
                ("", ""),
                ("💰 TOTAL A PAGAR:", f"${datos['total_comisiones_usd'] + datos['total_comisiones_usdt']:,.2f}")
            ]

            for label, valor in datos_tabla:
                frame = tk.Frame(self.resultados_frame, bg=self.colors["bg_card"])
                frame.pack(fill="x", pady=2)

                tk.Label(
                    frame,
                    text=label,
                    font=("Segoe UI", 10, "bold"),
                    bg=self.colors["bg_card"],
                    fg="#333333",  # Gris oscuro
                    width=25,
                    anchor="w"
                ).pack(side="left")

                tk.Label(
                    frame,
                    text=valor,
                    font=("Segoe UI", 10),
                    bg=self.colors["bg_card"],
                    fg=self.colors["success"] if "TOTAL" in label else "#666666"  # Gris medio
                ).pack(side="left")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron calcular las comisiones:\n{str(e)}")

    def _generar_reporte_comisiones(self):
        """Genera reporte de comisiones en Excel"""
        try:
            trabajador_nombre = self.combo_trabajador_comisiones.get()
            fecha_inicio = self.fecha_comision_inicio.get()
            fecha_fin = self.fecha_comision_fin.get()

            if not trabajador_nombre or not fecha_inicio or not fecha_fin:
                messagebox.showwarning("Advertencia", "Completa todos los campos")
                return

            # Buscar ID del trabajador
            worker_id = None
            for t in self.trabajadores:
                if t['name'] == trabajador_nombre:
                    worker_id = t['id']
                    break

            if worker_id:
                generar_reporte_comisiones(worker_id, fecha_inicio, fecha_fin)
            else:
                messagebox.showerror("Error", "Trabajador no encontrado")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")

    def _ver_detalles_comisiones(self):
        """Muestra detalles de las transacciones del trabajador"""
        trabajador_nombre = self.combo_trabajador_comisiones.get()
        if trabajador_nombre:
            self.trabajador_var.set(trabajador_nombre)
            self._aplicar_filtros()
            messagebox.showinfo("Detalles", f"Mostrando todas las transacciones de {trabajador_nombre}")

    # ========================================
    # FUNCIONES DE MIS GANANCIAS
    # ========================================
    def _actualizar_mis_ganancias(self, fecha_inicio=None, fecha_fin=None):
        """Actualiza la sección de mis ganancias"""
        try:
            resumen = obtener_resumen_ganancias(fecha_inicio, fecha_fin)

            # Ganancia neta (dueño)
            ganancia_neta = resumen.get('ganancia_neta_dueño_usd', 0) + resumen.get('ganancia_neta_dueño_usdt', 0)
            self.metrica_ganancia_neta.config(text=f"${ganancia_neta:,.2f}")

            # Ganancia de recargas (dueño)
            ganancia_recargas = resumen.get('ganancia_neta_dueño_usd', 0)
            self.metrica_ganancia_recargas.config(text=f"${ganancia_recargas:,.2f}")

            # Ganancia de remesas (dueño)
            ganancia_remesas = resumen.get('ganancia_neta_dueño_usdt', 0)
            self.metrica_ganancia_remesas.config(text=f"${ganancia_remesas:,.2f}")

        except Exception as e:
            print(f"Error al actualizar mis ganancias: {e}")

    def _filtrar_mis_ganancias(self, periodo):
        """Filtra mis ganancias por periodo"""
        hoy = datetime.now()

        if periodo == "hoy":
            fecha = hoy.strftime("%Y-%m-%d")
            self._actualizar_mis_ganancias(fecha, fecha)

        elif periodo == "semana":
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            self._actualizar_mis_ganancias(
                inicio_semana.strftime("%Y-%m-%d"),
                hoy.strftime("%Y-%m-%d")
            )

        elif periodo == "mes":
            inicio_mes = hoy.replace(day=1)
            self._actualizar_mis_ganancias(
                inicio_mes.strftime("%Y-%m-%d"),
                hoy.strftime("%Y-%m-%d")
            )

    def _filtrar_mis_ganancias_personalizado(self):
        """Abre diálogo para filtro personalizado de mis ganancias"""
        dialog = tk.Toplevel(self)
        dialog.title("Filtrar Mis Ganancias")
        dialog.geometry("300x150")
        dialog.configure(bg=self.colors["bg_primary"])

        tk.Label(dialog, text="Fecha desde:", bg=self.colors["bg_primary"],
                fg="#333333").pack(pady=(10, 5))  # Gris oscuro
        entry_inicio = tk.Entry(dialog, bg="white", fg="black")
        entry_inicio.pack(pady=5)
        entry_inicio.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(dialog, text="Fecha hasta:", bg=self.colors["bg_primary"],
                fg="#333333").pack(pady=(5, 5))  # Gris oscuro
        entry_fin = tk.Entry(dialog, bg="white", fg="black")
        entry_fin.pack(pady=5)
        entry_fin.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def aplicar():
            self._actualizar_mis_ganancias(entry_inicio.get(), entry_fin.get())
            dialog.destroy()

        ttk.Button(dialog, text="Aplicar", command=aplicar).pack(pady=10)

    # ========================================
    # FUNCIONES DE EXPORTACIÓN
    # ========================================
    def _exportar_dashboard_excel(self):
        """Exporta el dashboard completo a Excel"""
        try:
            fecha_inicio = self.fecha_inicio_var.get() or None
            fecha_fin = self.fecha_fin_var.get() or None

            exportar_dashboard(fecha_inicio, fecha_fin)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el dashboard:\n{str(e)}")

    def _exportar_transacciones_excel(self):
        """Exporta las transacciones filtradas a Excel"""
        try:
            # Obtener transacciones actuales
            fecha_inicio = self.fecha_inicio_var.get() or None
            fecha_fin = self.fecha_fin_var.get() or None
            trabajador = self.trabajador_var.get()
            tipo = self.tipo_var.get()

            # Convertir trabajador a ID
            worker_id = None
            if trabajador != "todos":
                for t in self.trabajadores:
                    if t['name'] == trabajador:
                        worker_id = t['id']
                        break

            # Obtener transacciones
            transacciones = obtener_transacciones_combinadas(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                worker_id=worker_id,
                tipo=tipo if tipo != "todos" else None
            )

            # Preparar filtros para el reporte
            filtros = {
                'Fecha desde': fecha_inicio or 'No especificado',
                'Fecha hasta': fecha_fin or 'No especificado',
                'Trabajador': trabajador,
                'Tipo': tipo,
                'País': self.pais_var.get()
            }

            # Exportar
            exportar_a_excel(transacciones, filtros)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar las transacciones:\n{str(e)}")

    def _exportar_a_pdf(self):
        """Exporta a PDF"""
        try:
            # Obtener transacciones actuales
            fecha_inicio = self.fecha_inicio_var.get() or None
            fecha_fin = self.fecha_fin_var.get() or None
            trabajador = self.trabajador_var.get()

            # Convertir trabajador a ID
            worker_id = None
            if trabajador != "todos":
                for t in self.trabajadores:
                    if t['name'] == trabajador:
                        worker_id = t['id']
                        break

            # Obtener transacciones
            transacciones = obtener_transacciones_combinadas(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                worker_id=worker_id,
                tipo=self.tipo_var.get() if self.tipo_var.get() != "todos" else None
            )

            # Preparar filtros
            filtros = {
                'Periodo': f"{fecha_inicio or 'Inicio'} a {fecha_fin or 'Fin'}",
                'Trabajador': trabajador,
                'Tipo': self.tipo_var.get(),
                'País': self.pais_var.get()
            }

            # Exportar
            exportar_a_pdf(transacciones, "Reporte de Transacciones Tryhards", filtros)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")

    def _abrir_carpeta_reportes(self):
        """Abre la carpeta de reportes en el explorador de archivos"""
        import os
        import subprocess
        import platform

        reports_path = os.path.abspath("reports")

        if not os.path.exists(reports_path):
            os.makedirs(reports_path)

        try:
            if platform.system() == "Windows":
                os.startfile(reports_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", reports_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", reports_path])
        except Exception as e:
            messagebox.showinfo("Carpeta de Reportes",
                              f"Ruta: {reports_path}\n\n"
                              f"No se pudo abrir automáticamente. Copia la ruta y ábrela manualmente.")

    # Función para refrescar el historial (usada desde main_window.py)
    def refrescar_historial(self):
        """Refresca todos los datos del historial"""
        self._cargar_catalogos()
        self._aplicar_filtros()
        self._actualizar_graficos()

# Función para crear la pestaña en main_window.py
def create_historial_tab(notebook, colors):
    """Crea y retorna la pestaña de historial"""
    frame = ttk.Frame(notebook)
    historial_tab = HistorialTab(frame, colors)
    historial_tab.pack(fill="both", expand=True)
    return frame