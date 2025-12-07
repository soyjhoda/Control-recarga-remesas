"""
gui/remesas_tab.py - REMESAS INTERNACIONALES - NUEVA ESTRUCTURA
│
│ Propósito:
│ • Registrar remesas con nueva lógica de conversión:
│     1. Moneda origen → Bolívares
│     2. Moneda origen → USDT (COMPRA)
│     3. USDT → Bolívares (VENTA)
│ • Cálculos automáticos en tiempo real
│ • Conexión con nueva BD (operations.py actualizada)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database.operations import (
    listar_trabajadores_activos,
    listar_paises_activos,
    listar_monedas_activas,
    listar_metodos_pago_activos,
    agregar_remesa,
    editar_remesa,
    eliminar_remesa,
    listar_remesas,
)


class RemesasTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style="Card.TFrame")

        # Caches de catálogos
        self.trabajadores = []
        self.paises = []
        self.monedas = []
        self.metodos_pago = []

        # Variables para cálculos
        self.monto_bs_var = tk.StringVar(value="0.00")
        self.usdt_recibidos_var = tk.StringVar(value="0.0000")
        self.usdt_gastados_var = tk.StringVar(value="0.0000")
        self.ganancia_bruta_var = tk.StringVar(value="0.0000")
        self.ganancia_neta_var = tk.StringVar(value="0.0000")

        # Crear canvas con scroll
        self._crear_scrollable_frame()

        # Construir UI dentro del frame con scroll
        self._build_ui()
        self._cargar_catalogos()
        self._cargar_remesas()

    # ---------------------------------
    # MÉTODO PÚBLICO PARA REFRESCAR
    # ---------------------------------
    def recargar_catalogos(self):
        """Relee catálogos desde la BD y actualiza los combos."""
        self._cargar_catalogos()

    # ---------------------------------
    # SCROLLABLE FRAME
    # ---------------------------------
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

    # ---------------------------------
    # UI - FORMULARIO
    # ---------------------------------
    def _build_ui(self):
        # Título
        title = ttk.Label(
            self.scrollable_frame,
            text="💸 NUEVA REMESA",
            font=("Segoe UI", 22, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        )
        title.pack(pady=(15, 5))

        # Contador de remesas del día
        self.contador_label = ttk.Label(
            self.scrollable_frame,
            text="Remesas hoy: 0",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["accent"],
            background=self.colors["bg_card"]
        )
        self.contador_label.pack(pady=(0, 10))

        # Frame del formulario
        form = ttk.LabelFrame(
            self.scrollable_frame,
            text="📋 DATOS DE LA REMESA",
            padding=20
        )
        form.pack(fill="x", padx=20, pady=10)

        # ===== FILA 1: Fecha y Trabajador =====
        ttk.Label(form, text="📅 Fecha:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.fecha_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        fecha_entry = ttk.Entry(form, textvariable=self.fecha_var, width=14)
        fecha_entry.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(form, text="👤 Trabajador:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=0, column=2, sticky="w", padx=(20, 0)
        )
        self.trabajador_var = tk.StringVar()
        self.combo_trabajador = ttk.Combobox(
            form, textvariable=self.trabajador_var, state="readonly", width=24
        )
        self.combo_trabajador.grid(row=0, column=3, padx=5, sticky="w")

        # ===== FILA 2: País origen y Método de pago =====
        ttk.Label(form, text="🌍 País de origen:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.pais_var = tk.StringVar()
        self.combo_pais = ttk.Combobox(
            form, textvariable=self.pais_var, state="readonly", width=24
        )
        self.combo_pais.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(form, text="💳 Método de pago:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=1, column=2, sticky="w", padx=(20, 0)
        )
        self.metodo_var = tk.StringVar()
        self.combo_metodo = ttk.Combobox(
            form, textvariable=self.metodo_var, state="readonly", width=24
        )
        self.combo_metodo.grid(row=1, column=3, padx=5, sticky="w")

        # ===== FILA 3: Moneda origen =====
        ttk.Label(form, text="💰 Moneda origen:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.moneda_var = tk.StringVar()
        self.combo_moneda = ttk.Combobox(
            form, textvariable=self.moneda_var, state="readonly", width=24
        )
        self.combo_moneda.grid(row=2, column=1, padx=5, sticky="w")

        # Separador - REMITENTE
        ttk.Separator(form, orient="horizontal").grid(
            row=3, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="👤 REMITENTE (quien envía)",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=4, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 5: Datos del remitente =====
        ttk.Label(form, text="Nombre:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=5, column=0, sticky="w", pady=8
        )
        self.sender_nombre_var = tk.StringVar()
        sender_entry = ttk.Entry(form, textvariable=self.sender_nombre_var, width=24)
        sender_entry.grid(row=5, column=1, padx=5, sticky="w")

        ttk.Label(form, text="📞 Teléfono:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=5, column=2, sticky="w", padx=(20, 0)
        )
        self.sender_telefono_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.sender_telefono_var, width=24).grid(
            row=5, column=3, padx=5, sticky="w"
        )

        # Separador - MONTO Y CONVERSIÓN
        ttk.Separator(form, orient="horizontal").grid(
            row=6, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="💰 MONTO Y CONVERSIÓN A BOLÍVARES",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=7, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 8: Monto origen y tasa a Bs =====
        ttk.Label(form, text="Monto origen:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=8, column=0, sticky="w", pady=8
        )
        self.monto_origen_var = tk.StringVar()
        monto_entry = ttk.Entry(
            form,
            textvariable=self.monto_origen_var,
            width=18,
            font=("Segoe UI", 12, "bold")
        )
        monto_entry.grid(row=8, column=1, padx=5, sticky="w")

        ttk.Label(form, text="📊 Tasa origen → Bs:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=8, column=2, sticky="w", padx=(20, 0)
        )
        self.tasa_bs_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.tasa_bs_var, width=18).grid(
            row=8, column=3, padx=5, sticky="w"
        )

        # ===== FILA 9: Monto en Bs (CALCULADO) =====
        ttk.Label(form, text="Monto en Bs:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=9, column=0, sticky="w", pady=8
        )
        self.monto_bs_label = tk.Label(
            form,
            text="Bs 0.00",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["success"],
            background=self.colors["bg_card"]
        )
        self.monto_bs_label.grid(row=9, column=1, padx=5, sticky="w")

        # Separador - BENEFICIARIO
        ttk.Separator(form, orient="horizontal").grid(
            row=10, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="👥 BENEFICIARIO (quien recibe)",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=11, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 12: Datos del beneficiario =====
        ttk.Label(form, text="Nombre:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=12, column=0, sticky="w", pady=8
        )
        self.receiver_nombre_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.receiver_nombre_var, width=24).grid(
            row=12, column=1, padx=5, sticky="w"
        )

        ttk.Label(form, text="📞 Teléfono:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=12, column=2, sticky="w", padx=(20, 0)
        )
        self.receiver_telefono_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.receiver_telefono_var, width=24).grid(
            row=12, column=3, padx=5, sticky="w"
        )

        # Separador - CONVERSIÓN USDT
        ttk.Separator(form, orient="horizontal").grid(
            row=13, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="🔄 CONVERSIÓN USDT",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=14, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 15: Tasa COMPRA USDT =====
        ttk.Label(form, text="📈 Tasa COMPRA USDT:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=15, column=0, sticky="w", pady=8
        )
        self.tasa_compra_usdt_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.tasa_compra_usdt_var, width=18).grid(
            row=15, column=1, padx=5, sticky="w"
        )

        ttk.Label(form, text="USDT recibidos:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=15, column=2, sticky="w", padx=(20, 0)
        )
        self.usdt_recibidos_label = tk.Label(
            form,
            text="0.0000 USDT",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["accent"],
            background=self.colors["bg_card"]
        )
        self.usdt_recibidos_label.grid(row=15, column=3, padx=5, sticky="w")

        # ===== FILA 16: Tasa VENTA USDT =====
        ttk.Label(form, text="📉 Tasa VENTA USDT:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=16, column=0, sticky="w", pady=8
        )
        self.tasa_venta_usdt_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.tasa_venta_usdt_var, width=18).grid(
            row=16, column=1, padx=5, sticky="w"
        )

        ttk.Label(form, text="USDT gastados:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=16, column=2, sticky="w", padx=(20, 0)
        )
        self.usdt_gastados_label = tk.Label(
            form,
            text="0.0000 USDT",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["warning"],
            background=self.colors["bg_card"]
        )
        self.usdt_gastados_label.grid(row=16, column=3, padx=5, sticky="w")

        # Separador - GANANCIAS
        ttk.Separator(form, orient="horizontal").grid(
            row=17, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="💵 GANANCIAS EN USDT",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=18, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 19: Ganancias =====
        ttk.Label(form, text="💰 Ganancia bruta:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=19, column=0, sticky="w", pady=8
        )
        self.ganancia_bruta_label = tk.Label(
            form,
            text="0.0000 USDT",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["text_light"],
            background=self.colors["bg_card"]
        )
        self.ganancia_bruta_label.grid(row=19, column=1, padx=5, sticky="w")

        ttk.Label(form, text="👷 Comisión trabajador:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=19, column=2, sticky="w", padx=(20, 0)
        )
        self.comision_usdt_var = tk.StringVar(value="0.0000")
        comision_entry = ttk.Entry(
            form,
            textvariable=self.comision_usdt_var,
            width=18,
            font=("Segoe UI", 12, "bold")
        )
        comision_entry.grid(row=19, column=3, padx=5, sticky="w")

        # ===== FILA 20: Ganancia neta =====
        ttk.Label(form, text="✅ Ganancia neta:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=20, column=0, sticky="w", pady=8
        )
        self.ganancia_neta_label = tk.Label(
            form,
            text="0.0000 USDT",
            font=("Segoe UI", 14, "bold"),
            foreground=self.colors["success"],
            background=self.colors["bg_card"]
        )
        self.ganancia_neta_label.grid(row=20, column=1, padx=5, sticky="w")

        # Separador - NOTAS
        ttk.Separator(form, orient="horizontal").grid(
            row=21, column=0, columnspan=4, sticky="ew", pady=20
        )

        # ===== FILA 22: Notas =====
        ttk.Label(form, text="📝 Notas (opcional):", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=22, column=0, sticky="nw", pady=5
        )

        # Frame para el Text con scroll
        notes_frame = ttk.Frame(form)
        notes_frame.grid(row=22, column=1, columnspan=3, padx=5, sticky="w")

        # Scrollbar para notas
        notes_scroll = ttk.Scrollbar(notes_frame)
        notes_scroll.pack(side="right", fill="y")

        self.notas_text = tk.Text(
            notes_frame,
            width=50,
            height=4,
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"],
            insertbackground=self.colors["primary"],
            relief="flat",
            yscrollcommand=notes_scroll.set
        )
        self.notas_text.pack(side="left", fill="both", expand=True)
        notes_scroll.config(command=self.notas_text.yview)

        # ===== FILA 23: Botones =====
        btn_frame = ttk.Frame(form, style="Card.TFrame")
        btn_frame.grid(row=23, column=0, columnspan=4, pady=20)

        ttk.Button(
            btn_frame,
            text="🧮 CALCULAR TODO",
            command=self._calcular_todo,
            style="Primary.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="💾 GUARDAR REMESA",
            command=self._guardar_remesa,
            style="Success.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="🧹 LIMPIAR FORMULARIO",
            command=self._limpiar_formulario,
            style="Danger.TButton"
        ).pack(side="left", padx=10)

        # ===== TABLA DE REMESAS =====
        table_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📊 REMESAS REGISTRADAS",
            padding=15
        )
        table_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Frame interno para tabla y scrollbar
        table_inner_frame = ttk.Frame(table_frame)
        table_inner_frame.pack(fill="both", expand=True)

        # Treeview con scroll
        tree_scroll = ttk.Scrollbar(
            table_inner_frame,
            style="Vertical.TScrollbar"
        )
        tree_scroll.pack(side="right", fill="y")

        cols = ("id", "fecha", "trabajador", "remitente", "monto_origen", "monto_bs", "ganancia_usdt")
        self.tree_remesas = ttk.Treeview(
            table_inner_frame,
            columns=cols,
            show="headings",
            height=10,
            yscrollcommand=tree_scroll.set,
            style="Custom.Treeview"
        )
        tree_scroll.config(command=self.tree_remesas.yview)

        # Configurar columnas
        column_widths = {
            "id": 60,
            "fecha": 100,
            "trabajador": 140,
            "remitente": 160,
            "monto_origen": 120,
            "monto_bs": 130,
            "ganancia_usdt": 120
        }

        for col in cols:
            display_name = col.upper().replace("_", " ")
            if col == "monto_origen":
                display_name = "MONTO ORIGEN"
            elif col == "monto_bs":
                display_name = "BS ENTREGADOS"
            elif col == "ganancia_usdt":
                display_name = "GANANCIA USDT"

            self.tree_remesas.heading(col, text=display_name)
            self.tree_remesas.column(col, width=column_widths.get(col, 100))

        self.tree_remesas.pack(side="left", fill="both", expand=True)

        # Configurar tags para filas alternadas
        self.tree_remesas.tag_configure('oddrow', background=self.colors["table_odd"])
        self.tree_remesas.tag_configure('evenrow', background=self.colors["table_even"])
        self.tree_remesas.tag_configure('selected', background=self.colors["primary"])

        # Botones de gestión
        btn_table_frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame")
        btn_table_frame.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Button(
            btn_table_frame,
            text="🔄 ACTUALIZAR LISTA",
            command=self._cargar_remesas
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_table_frame,
            text="🗑️ ELIMINAR SELECCIONADA",
            command=self._eliminar_remesa,
            style="Danger.TButton"
        ).pack(side="left", padx=5)

        # ===== BINDS PARA CÁLCULO AUTOMÁTICO =====
        variables_para_calculo = [
            self.monto_origen_var,
            self.tasa_bs_var,
            self.tasa_compra_usdt_var,
            self.tasa_venta_usdt_var,
            self.comision_usdt_var
        ]

        for var in variables_para_calculo:
            var.trace_add("write", self._calcular_automatico)

    # ---------------------------------
    # CARGA DE CATÁLOGOS
    # ---------------------------------
    def _cargar_catalogos(self):
        """Carga todos los catálogos desde la base de datos"""
        # Trabajadores
        self.trabajadores = listar_trabajadores_activos()
        nombres_trab = [t["name"] for t in self.trabajadores]
        self.combo_trabajador["values"] = nombres_trab
        if nombres_trab:
            self.combo_trabajador.current(0)

        # Países
        self.paises = listar_paises_activos()
        nombres_pais = [p["name"] for p in self.paises]
        self.combo_pais["values"] = nombres_pais
        if nombres_pais:
            self.combo_pais.current(0)

        # Métodos de pago (solo tipo remesa o ambos)
        self.metodos_pago = [
            m for m in listar_metodos_pago_activos()
            if m["type"] in ["remesa", "ambos"]
        ]
        nombres_mp = [m["name"] for m in self.metodos_pago]
        self.combo_metodo["values"] = nombres_mp
        if nombres_mp:
            self.combo_metodo.current(0)

        # Monedas
        self.monedas = listar_monedas_activas()
        nombres_monedas = [f"{m['code']} - {m['name']}" for m in self.monedas]
        self.combo_moneda["values"] = nombres_monedas
        if nombres_monedas:
            self.combo_moneda.current(0)

    # ---------------------------------
    # CÁLCULOS AUTOMÁTICOS
    # ---------------------------------
    def _calcular_automatico(self, *args):
        """Calcula valores automáticamente mientras el usuario escribe"""
        try:
            # Obtener valores de entrada
            monto_origen = float(self.monto_origen_var.get() or 0)
            tasa_bs = float(self.tasa_bs_var.get() or 0)
            tasa_compra = float(self.tasa_compra_usdt_var.get() or 0)
            tasa_venta = float(self.tasa_venta_usdt_var.get() or 0)
            comision = float(self.comision_usdt_var.get() or 0)

            # 1. Calcular monto en Bolívares
            monto_bs = monto_origen * tasa_bs
            self.monto_bs_label.config(text=f"Bs {monto_bs:,.2f}")

            # 2. Calcular USDT recibidos (COMPRA)
            if tasa_compra > 0:
                usdt_recibidos = monto_origen / tasa_compra
                self.usdt_recibidos_label.config(text=f"{usdt_recibidos:.4f} USDT")
            else:
                usdt_recibidos = 0
                self.usdt_recibidos_label.config(text="0.0000 USDT")

            # 3. Calcular USDT gastados (VENTA)
            if tasa_venta > 0:
                usdt_gastados = monto_bs / tasa_venta
                self.usdt_gastados_label.config(text=f"{usdt_gastados:.4f} USDT")
            else:
                usdt_gastados = 0
                self.usdt_gastados_label.config(text="0.0000 USDT")

            # 4. Calcular ganancia bruta
            if usdt_recibidos > 0 and usdt_gastados > 0:
                ganancia_bruta = usdt_recibidos - usdt_gastados
                self.ganancia_bruta_label.config(text=f"{ganancia_bruta:.4f} USDT")

                # 5. Calcular ganancia neta
                ganancia_neta = ganancia_bruta - comision
                self.ganancia_neta_label.config(text=f"{ganancia_neta:.4f} USDT")
            else:
                self.ganancia_bruta_label.config(text="0.0000 USDT")
                self.ganancia_neta_label.config(text="0.0000 USDT")

        except ValueError:
            # Si hay error en conversión, mostrar ceros
            self.monto_bs_label.config(text="Bs 0.00")
            self.usdt_recibidos_label.config(text="0.0000 USDT")
            self.usdt_gastados_label.config(text="0.0000 USDT")
            self.ganancia_bruta_label.config(text="0.0000 USDT")
            self.ganancia_neta_label.config(text="0.0000 USDT")

    def _calcular_todo(self):
        """Forza el cálculo de todos los valores"""
        self._calcular_automatico()

    # ---------------------------------
    # LÓGICA: GUARDADO
    # ---------------------------------
    def _obtener_id_seleccion(self, nombre: str, lista: list[dict], key_name: str = "name") -> int | None:
        """Obtiene el ID de un elemento seleccionado en un combobox"""
        for item in lista:
            if item[key_name] == nombre:
                return item["id"]
        return None

    def _obtener_currency_id_desde_combo(self) -> int | None:
        """Extrae el ID de moneda del combobox formato 'USD - Dólar'"""
        seleccion = self.moneda_var.get()
        if not seleccion:
            return None

        try:
            # Formato: "USD - Dólar estadounidense"
            codigo = seleccion.split(" - ")[0].strip()
            for moneda in self.monedas:
                if moneda["code"] == codigo:
                    return moneda["id"]
        except:
            pass
        return None

    def _validar_formulario(self) -> bool:
        """Valida que todos los campos obligatorios estén llenos"""
        campos_obligatorios = [
            self.fecha_var.get().strip(),
            self.trabajador_var.get().strip(),
            self.pais_var.get().strip(),
            self.metodo_var.get().strip(),
            self.moneda_var.get().strip(),
            self.sender_nombre_var.get().strip(),
            self.monto_origen_var.get().strip(),
            self.tasa_bs_var.get().strip(),
            self.receiver_nombre_var.get().strip(),
            self.tasa_compra_usdt_var.get().strip(),
            self.tasa_venta_usdt_var.get().strip(),
            self.comision_usdt_var.get().strip(),
        ]

        if not all(campos_obligatorios):
            messagebox.showerror(
                "❌ Error de validación",
                "Debes llenar todos los campos obligatorios.\n"
                "Solo el teléfono y las notas son opcionales."
            )
            return False
        return True

    def _guardar_remesa(self):
        """Guarda una nueva remesa en la base de datos"""
        # Validar formulario
        if not self._validar_formulario():
            return

        try:
            # Obtener IDs de combobox
            worker_id = self._obtener_id_seleccion(self.trabajador_var.get(), self.trabajadores)
            country_id = self._obtener_id_seleccion(self.pais_var.get(), self.paises)
            metodo_id = self._obtener_id_seleccion(self.metodo_var.get(), self.metodos_pago)
            currency_id = self._obtener_currency_id_desde_combo()

            if not all([worker_id, country_id, metodo_id, currency_id]):
                messagebox.showerror(
                    "❌ Error",
                    "No se pudieron obtener los IDs necesarios. "
                    "Verifica que los catálogos estén cargados."
                )
                return

            # Preparar datos para la función de operations.py
            datos_remesa = {
                'date_str': self.fecha_var.get().strip(),
                'worker_id': worker_id,
                'country_id': country_id,
                'payment_method_id': metodo_id,
                'currency_id': currency_id,
                'sender_name': self.sender_nombre_var.get().strip(),
                'sender_phone': self.sender_telefono_var.get().strip() or None,
                'amount_origin': float(self.monto_origen_var.get()),
                'rate_origin_to_bs': float(self.tasa_bs_var.get()),
                'receiver_name': self.receiver_nombre_var.get().strip(),
                'receiver_phone': self.receiver_telefono_var.get().strip() or None,
                'rate_buy_usdt': float(self.tasa_compra_usdt_var.get()),
                'rate_sell_usdt_bs': float(self.tasa_venta_usdt_var.get()),
                'seller_commission_usdt': float(self.comision_usdt_var.get()),
                'notes': self.notas_text.get("1.0", "end").strip() or None
            }

            # Llamar a la función de operations.py
            remesa_id = agregar_remesa(**datos_remesa)

            if remesa_id:
                messagebox.showinfo(
                    "✅ ¡Éxito!",
                    f"Remesa guardada correctamente\n\n"
                    f"📋 ID: {remesa_id}\n"
                    f"👤 Remitente: {datos_remesa['sender_name']}\n"
                    f"💰 Monto origen: {datos_remesa['amount_origin']:.2f}\n"
                    f"💵 Ganancia neta: {self.ganancia_neta_label.cget('text')}"
                )
                self._limpiar_formulario()
                self._cargar_remesas()
            else:
                messagebox.showerror("❌ Error", "No se pudo guardar la remesa")

        except ValueError as e:
            messagebox.showerror("❌ Error de formato", f"Verifica los números:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("❌ Error inesperado", f"No se pudo guardar:\n{str(e)}")

    def _limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Restaurar fecha actual
        self.fecha_var.set(datetime.now().strftime("%Y-%m-%d"))

        # Restaurar combobox a primera opción
        if self.trabajadores:
            self.combo_trabajador.current(0)
        if self.paises:
            self.combo_pais.current(0)
        if self.metodos_pago:
            self.combo_metodo.current(0)
        if self.monedas:
            self.combo_moneda.current(0)

        # Limpiar campos de texto
        self.sender_nombre_var.set("")
        self.sender_telefono_var.set("")
        self.monto_origen_var.set("")
        self.tasa_bs_var.set("")
        self.receiver_nombre_var.set("")
        self.receiver_telefono_var.set("")
        self.tasa_compra_usdt_var.set("")
        self.tasa_venta_usdt_var.set("")
        self.comision_usdt_var.set("0.0000")
        self.notas_text.delete("1.0", "end")

        # Restaurar etiquetas calculadas
        self.monto_bs_label.config(text="Bs 0.00")
        self.usdt_recibidos_label.config(text="0.0000 USDT")
        self.usdt_gastados_label.config(text="0.0000 USDT")
        self.ganancia_bruta_label.config(text="0.0000 USDT")
        self.ganancia_neta_label.config(text="0.0000 USDT")

    # ---------------------------------
    # TABLA DE REMESAS
    # ---------------------------------
    def _cargar_remesas(self):
        """Carga las remesas desde la base de datos y actualiza la tabla"""
        # Limpiar tabla
        for item in self.tree_remesas.get_children():
            self.tree_remesas.delete(item)

        try:
            # Obtener remesas desde operations.py
            remesas = listar_remesas()

            # Contar remesas de hoy
            hoy = datetime.now().strftime("%Y-%m-%d")
            remesas_hoy = sum(1 for r in remesas if r["date"] == hoy)
            self.contador_label.config(text=f"📊 Remesas hoy: {remesas_hoy}")

            # Llenar tabla con estilos alternados
            for i, r in enumerate(remesas):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                # Formatear valores
                monto_bs_formatted = f"Bs {r['amount_destiny_bs']:,.2f}" if r['amount_destiny_bs'] else "Bs 0.00"

                self.tree_remesas.insert(
                    "",
                    "end",
                    tags=(tag,),  # Aplicar estilo alternado
                    values=(
                        r["id"],
                        r["date"],
                        r.get("worker_name", "N/A"),
                        r.get("sender_name", "N/A"),
                        f"{r['amount_origin']:.2f}",
                        monto_bs_formatted,
                        f"{r['profit_net_usdt']:.4f} USDT"
                    ),
                )

        except Exception as e:
            print(f"Error al cargar remesas: {str(e)}")
            messagebox.showerror("❌ Error", f"No se pudieron cargar las remesas:\n{str(e)}")

    def _eliminar_remesa(self):
        """Elimina la remesa seleccionada de la tabla"""
        seleccion = self.tree_remesas.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Sin selección", "Selecciona una remesa para eliminar.")
            return

        # Obtener ID de la remesa seleccionada
        item = self.tree_remesas.item(seleccion[0])
        remesa_id = item["values"][0]
        remitente = item["values"][3]

        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar la remesa #{remesa_id} de {remitente}?\n\n"
            "⚠️ Esta acción no se puede deshacer."
        )

        if respuesta:
            try:
                # Llamar a la función de operations.py
                if eliminar_remesa(remesa_id):
                    messagebox.showinfo("✅ Éxito", f"Remesa #{remesa_id} eliminada correctamente.")
                    self._cargar_remesas()
                else:
                    messagebox.showerror("❌ Error", "No se pudo eliminar la remesa.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo eliminar:\n{str(e)}")