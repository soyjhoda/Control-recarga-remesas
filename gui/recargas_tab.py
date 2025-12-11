"""
gui/recargas_tab.py - RECARGAS EN USD - FORMULARIO + GUARDADO MEJORADO
│
│ Propósito:
│ • Registrar recargas 100% en USD con nuevo estilo visual
│ • Cálculos automáticos en tiempo real
│ • Interfaz oscura tech con máxima legibilidad
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database.operations import (
    listar_trabajadores_activos,
    listar_paises_activos,
    listar_juegos_activos,
    listar_productos_activos,
    listar_metodos_pago_activos,
    agregar_recarga,
    listar_recargas,           # NUEVA FUNCIÓN
    eliminar_recarga,          # NUEVA FUNCIÓN
)


class RecargasTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style="Card.TFrame")

        # caches de catálogos
        self.trabajadores = []
        self.paises = []
        self.juegos = []
        self.productos = []
        self.metodos_pago = []

        # Variables para el campo cliente (NUEVO)
        self.cliente_var = tk.StringVar()

        # Crear canvas con scroll
        self._crear_scrollable_frame()

        # Construir UI dentro del frame con scroll
        self._build_ui()
        self._cargar_catalogos()
        self._cargar_historial()

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
    # UI - FORMULARIO MEJORADO
    # ---------------------------------
    def _build_ui(self):
        # Título
        title = ttk.Label(
            self.scrollable_frame,
            text="💳 NUEVA RECARGA",
            font=("Segoe UI", 22, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        )
        title.pack(pady=(15, 5))

        # Contador de recargas del día
        self.contador_label = ttk.Label(
            self.scrollable_frame,
            text="📊 Recargas hoy: 0",
            font=("Segoe UI", 12, "bold"),
            foreground=self.colors["accent"],
            background=self.colors["bg_card"]
        )
        self.contador_label.pack(pady=(0, 10))

        # Frame del formulario
        form = ttk.LabelFrame(
            self.scrollable_frame,
            text="📋 DATOS DE LA RECARGA",
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

        # ===== FILA 2: País y Método de pago =====
        ttk.Label(form, text="🌍 País del cliente:", foreground=self.colors["text_light"],
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

        # ===== FILA 3: Cliente (NUEVO CAMPO) =====
        ttk.Label(form, text="👤 Cliente:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=2, column=0, sticky="w", pady=8
        )
        ttk.Entry(form, textvariable=self.cliente_var, width=40).grid(
            row=2, column=1, columnspan=3, padx=5, sticky="w", pady=8
        )

        # ===== FILA 4: Juego y Producto =====
        ttk.Label(form, text="🎮 Juego:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=3, column=0, sticky="w", pady=8
        )
        self.juego_var = tk.StringVar()
        self.combo_juego = ttk.Combobox(
            form, textvariable=self.juego_var, state="readonly", width=24
        )
        self.combo_juego.grid(row=3, column=1, padx=5, sticky="w")
        self.combo_juego.bind("<<ComboboxSelected>>", self._filtrar_productos_por_juego)

        ttk.Label(form, text="📦 Producto:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=3, column=2, sticky="w", padx=(20, 0)
        )
        self.producto_var = tk.StringVar()
        self.combo_producto = ttk.Combobox(
            form, textvariable=self.producto_var, state="readonly", width=24
        )
        self.combo_producto.grid(row=3, column=3, padx=5, sticky="w")

        # Separador - MONTO Y GANANCIAS
        ttk.Separator(form, orient="horizontal").grid(
            row=4, column=0, columnspan=4, sticky="ew", pady=20
        )

        ttk.Label(
            form,
            text="💰 MONTO Y GANANCIAS EN USD",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        ).grid(row=5, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== FILA 6: Montos principales =====
        ttk.Label(form, text="💵 Recibí del cliente (USD):", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=6, column=0, sticky="w", pady=8
        )
        self.recibi_var = tk.StringVar()
        recibi_entry = ttk.Entry(
            form,
            textvariable=self.recibi_var,
            width=18,
            font=("Segoe UI", 12, "bold")
        )
        recibi_entry.grid(row=6, column=1, padx=5, sticky="w")

        ttk.Label(form, text="📉 Costo real (USD):", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=6, column=2, sticky="w", padx=(20, 0)
        )
        self.costo_var = tk.StringVar()
        costo_entry = ttk.Entry(
            form,
            textvariable=self.costo_var,
            width=18,
            font=("Segoe UI", 12, "bold")
        )
        costo_entry.grid(row=6, column=3, padx=5, sticky="w")

        # ===== FILA 7: Comisión y Ganancia =====
        ttk.Label(form, text="👷 Comisión vendedor (USD):", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=7, column=0, sticky="w", pady=8
        )
        self.comision_var = tk.StringVar(value="0")
        comision_entry = ttk.Entry(
            form,
            textvariable=self.comision_var,
            width=18,
            font=("Segoe UI", 12, "bold")
        )
        comision_entry.grid(row=7, column=1, padx=5, sticky="w")

        ttk.Label(form, text="✅ Ganancia:", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=7, column=2, sticky="w", padx=(20, 0)
        )
        self.ganancia_label = tk.Label(
            form,
            text="$0.00",
            font=("Segoe UI", 14, "bold"),
            foreground=self.colors["success"],
            background=self.colors["bg_card"]
        )
        self.ganancia_label.grid(row=7, column=3, padx=5, sticky="w")

        # Separador - NOTAS
        ttk.Separator(form, orient="horizontal").grid(
            row=8, column=0, columnspan=4, sticky="ew", pady=20
        )

        # ===== FILA 9: Notas =====
        ttk.Label(form, text="📝 Notas (opcional):", foreground=self.colors["text_light"],
                 background=self.colors["bg_card"]).grid(
            row=9, column=0, sticky="nw", pady=5
        )

        # Frame para el Text con scroll
        notes_frame = ttk.Frame(form)
        notes_frame.grid(row=9, column=1, columnspan=3, padx=5, sticky="w")

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

        # ===== FILA 10: Botones =====
        btn_frame = ttk.Frame(form, style="Card.TFrame")
        btn_frame.grid(row=10, column=0, columnspan=4, pady=25)

        ttk.Button(
            btn_frame,
            text="🧮 CALCULAR GANANCIA",
            command=self._calcular_ganancia_manual,
            style="Primary.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="💾 GUARDAR RECARGA",
            command=self._guardar_recarga,
            style="Success.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="🧹 LIMPIAR FORMULARIO",
            command=self._limpiar_formulario,
            style="Danger.TButton"
        ).pack(side="left", padx=10)

        # ===== TABLA HISTÓRICO DE RECARGAS =====
        table_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📊 ÚLTIMAS RECARGAS",
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

        cols = ("id", "fecha", "trabajador", "cliente", "juego", "recibido", "costo", "ganancia")  # ✅ AGREGADO "cliente"
        self.tree_recargas = ttk.Treeview(
            table_inner_frame,
            columns=cols,
            show="headings",
            height=8,
            yscrollcommand=tree_scroll.set,
            style="Custom.Treeview"
        )
        tree_scroll.config(command=self.tree_recargas.yview)

        # Configurar columnas
        column_widths = {
            "id": 60,
            "fecha": 100,
            "trabajador": 120,  # Reducido un poco para espacio
            "cliente": 120,      # ✅ NUEVA COLUMNA
            "juego": 140,
            "recibido": 110,
            "costo": 110,
            "ganancia": 110
        }

        for col in cols:
            display_name = col.upper().replace("_", " ")
            if col == "recibido":
                display_name = "RECIBIDO USD"
            elif col == "costo":
                display_name = "COSTO USD"
            elif col == "ganancia":
                display_name = "GANANCIA USD"

            self.tree_recargas.heading(col, text=display_name)
            self.tree_recargas.column(col, width=column_widths.get(col, 100))

        self.tree_recargas.pack(side="left", fill="both", expand=True)

        # Configurar tags para filas alternadas
        self.tree_recargas.tag_configure('oddrow', background=self.colors["table_odd"])
        self.tree_recargas.tag_configure('evenrow', background=self.colors["table_even"])
        self.tree_recargas.tag_configure('selected', background=self.colors["primary"])

        # Botones de gestión
        btn_table_frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame")
        btn_table_frame.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Button(
            btn_table_frame,
            text="🔄 ACTUALIZAR HISTORIAL",
            command=self._cargar_historial
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_table_frame,
            text="🗑️ ELIMINAR SELECCIONADA",
            command=self._eliminar_recarga,
            style="Danger.TButton"
        ).pack(side="left", padx=5)

        # ===== BINDS PARA CÁLCULO AUTOMÁTICO =====
        variables_para_calculo = [
            self.recibi_var,
            self.costo_var,
            self.comision_var
        ]

        for var in variables_para_calculo:
            var.trace_add("write", self._calcular_ganancia)

    # ---------------------------------
    # CARGA DE CATÁLOGOS - MEJORADA
    # ---------------------------------
    def _cargar_catalogos(self):
        """Carga todos los catálogos desde la base de datos"""
        try:
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

            # Métodos de pago (solo tipo recarga o ambos)
            self.metodos_pago = [
                m for m in listar_metodos_pago_activos()
                if m["type"] in ["recarga", "ambos"]
            ]
            nombres_mp = [m["name"] for m in self.metodos_pago]
            self.combo_metodo["values"] = nombres_mp
            if nombres_mp:
                self.combo_metodo.current(0)

            # Juegos - FORZAR CARGA
            self.juegos = listar_juegos_activos()
            nombres_juegos = [j["name"] for j in self.juegos]
            self.combo_juego["values"] = nombres_juegos
            if nombres_juegos:
                self.combo_juego.current(0)

            # Productos - FORZAR CARGA (SOLUCIÓN AL PROBLEMA 1)
            self._cargar_productos_forzado()

        except Exception as e:
            print(f"Error al cargar catálogos: {e}")
            messagebox.showwarning("⚠️ Advertencia", f"Error al cargar algunos catálogos:\n{str(e)}")

    def _cargar_productos_forzado(self):
        """Carga productos forzadamente, asegurando que se actualicen"""
        try:
            self.productos = listar_productos_activos()
            nombres_prod = [p["name"] for p in self.productos]
            self.combo_producto["values"] = nombres_prod
            if nombres_prod:
                self.combo_producto.current(0)
            else:
                self.combo_producto.set("")
                self.combo_producto["values"] = []
        except Exception as e:
            print(f"Error al cargar productos: {e}")
            self.combo_producto.set("")
            self.combo_producto["values"] = []

    def _refrescar_combo_productos(self, juego_id: int | None = None):
        """Actualiza el combobox de productos según el juego seleccionado"""
        try:
            if juego_id is None:
                prods = self.productos
            else:
                prods = [p for p in self.productos if p.get("game_id") == juego_id]

            nombres_prod = [p["name"] for p in prods]
            self.combo_producto["values"] = nombres_prod
            if nombres_prod:
                self.combo_producto.current(0)
            else:
                self.combo_producto.set("")
        except Exception as e:
            print(f"Error al filtrar productos: {e}")
            self.combo_producto.set("")

    def _filtrar_productos_por_juego(self, event=None):
        """Filtra productos cuando se selecciona un juego"""
        nombre_juego = self.juego_var.get()
        juego_id = None
        for j in self.juegos:
            if j["name"] == nombre_juego:
                juego_id = j["id"]
                break
        self._refrescar_combo_productos(juego_id)

    # ---------------------------------
    # CÁLCULOS AUTOMÁTICOS
    # ---------------------------------
    def _calcular_ganancia(self, *args):
        """Calcula la ganancia automáticamente mientras el usuario escribe"""
        try:
            recibi = float(self.recibi_var.get() or 0)
            costo = float(self.costo_var.get() or 0)
            comision = float(self.comision_var.get() or 0)
            ganancia = recibi - costo - comision
            self.ganancia_label.config(text=f"${ganancia:.2f}")
        except ValueError:
            # Si hay error en conversión, mostrar cero
            self.ganancia_label.config(text="$0.00")

    def _calcular_ganancia_manual(self):
        """Forza el cálculo de la ganancia"""
        self._calcular_ganancia()

    # ---------------------------------
    # LÓGICA: GUARDADO
    # ---------------------------------
    def _obtener_id_seleccion(self, nombre: str, lista: list[dict], key_name: str = "name") -> int | None:
        """Obtiene el ID de un elemento seleccionado en un combobox"""
        for item in lista:
            if item[key_name] == nombre:
                return item["id"]
        return None

    def _validar_formulario(self) -> bool:
        """Valida que todos los campos obligatorios estén llenos"""
        campos_obligatorios = [
            self.fecha_var.get().strip(),
            self.trabajador_var.get().strip(),
            self.pais_var.get().strip(),
            self.metodo_var.get().strip(),
            self.recibi_var.get().strip(),
            self.costo_var.get().strip(),
        ]

        if not all(campos_obligatorios):
            messagebox.showerror(
                "❌ Error de validación",
                "Debes llenar todos los campos obligatorios:\n"
                "• Fecha\n• Trabajador\n• País\n• Método de pago\n• Recibí (USD)\n• Costo (USD)\n\n"
                "Solo comisión, cliente y notas son opcionales."
            )
            return False
        return True

    def _guardar_recarga(self):
        """Guarda una nueva recarga en la base de datos"""
        # Validar formulario
        if not self._validar_formulario():
            return

        try:
            # Obtener valores
            fecha = self.fecha_var.get().strip()
            recibi = float(self.recibi_var.get())
            costo = float(self.costo_var.get())
            comision = float(self.comision_var.get() or 0)
            cliente = self.cliente_var.get().strip() or None  # ✅ NUEVO: Obtener nombre del cliente

            # Obtener IDs de combobox
            worker_id = self._obtener_id_seleccion(self.trabajador_var.get(), self.trabajadores)
            country_id = self._obtener_id_seleccion(self.pais_var.get(), self.paises)
            metodo_id = self._obtener_id_seleccion(self.metodo_var.get(), self.metodos_pago)
            juego_id = self._obtener_id_seleccion(self.juego_var.get(), self.juegos)
            producto_id = self._obtener_id_seleccion(self.producto_var.get(), self.productos)

            if worker_id is None or country_id is None or metodo_id is None:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudieron obtener los IDs necesarios. "
                    "Verifica que los catálogos estén cargados."
                )
                return

            notas = self.notas_text.get("1.0", "end").strip() or None

            # Guardar en base de datos CON CLIENTE
            recarga_id = agregar_recarga(
                date_str=fecha,
                worker_id=worker_id,
                country_id=country_id,
                payment_method_id=metodo_id,
                amount_received_usd=recibi,
                cost_usd=costo,
                seller_commission_usd=comision,
                game_id=juego_id,
                product_id=producto_id,
                customer_name=cliente,  # ✅ NUEVO: Pasar nombre del cliente
                notes=notas,
            )

            if recarga_id:
                ganancia = recibi - costo - comision
                mensaje_cliente = f"👤 Cliente: {cliente or 'No especificado'}\n" if cliente else ""

                messagebox.showinfo(
                    "✅ ¡Éxito!",
                    f"Recarga guardada correctamente\n\n"
                    f"📋 ID: {recarga_id}\n"
                    f"👤 Trabajador: {self.trabajador_var.get()}\n"
                    f"{mensaje_cliente}"  # ✅ Agregado cliente (si existe)
                    f"💰 Recibido: ${recibi:.2f}\n"
                    f"📉 Costo: ${costo:.2f}\n"
                    f"✅ Ganancia: ${ganancia:.2f}"
                )

                # Limpiar formulario
                self._limpiar_formulario()

                # Cargar historial actualizado
                self._cargar_historial()
            else:
                messagebox.showerror("❌ Error", "No se pudo guardar la recarga")

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

        # Limpiar otros campos
        self.combo_juego.set("")
        self.combo_producto.set("")
        self.cliente_var.set("")  # ✅ NUEVO: Limpiar campo cliente
        self.recibi_var.set("")
        self.costo_var.set("")
        self.comision_var.set("0")
        self.notas_text.delete("1.0", "end")
        self.ganancia_label.config(text="$0.00")

    # ---------------------------------
    # TABLA HISTÓRICO - REAL
    # ---------------------------------
    def _cargar_historial(self):
        """Carga el historial REAL de recargas desde la base de datos"""
        # Limpiar tabla
        for item in self.tree_recargas.get_children():
            self.tree_recargas.delete(item)

        try:
            # Obtener recargas desde operations.py
            recargas = listar_recargas()

            if not recargas:
                # Si no hay recargas, mostrar mensaje
                self.tree_recargas.insert("", "end", values=(
                    "--", "--", "No hay recargas", "--", "--", "--", "--", "--"
                ))
                # Actualizar contador
                self.contador_label.config(text="📊 Recargas hoy: 0")
                return

            # Contar recargas de hoy
            hoy = datetime.now().strftime("%Y-%m-%d")
            recargas_hoy = sum(1 for r in recargas if r["date"] == hoy)
            self.contador_label.config(text=f"📊 Recargas hoy: {recargas_hoy}")

            # Llenar tabla con datos reales
            for i, r in enumerate(recargas):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                # Obtener nombre del juego o mostrar "Sin juego"
                juego_nombre = r.get("game_name", "Sin juego")
                if not juego_nombre or juego_nombre == "None":
                    juego_nombre = "Sin juego"

                # Obtener nombre del cliente
                cliente_nombre = r.get("customer_name", "")
                if not cliente_nombre:
                    cliente_nombre = "Sin cliente"

                self.tree_recargas.insert(
                    "",
                    "end",
                    tags=(tag,),
                    values=(
                        r.get("id", "--"),
                        r.get("date", "--"),
                        r.get("worker_name", "N/A"),
                        cliente_nombre,  # ✅ AGREGADO: Mostrar cliente
                        juego_nombre,
                        f"${r.get('amount_received_usd', 0):.2f}",
                        f"${r.get('cost_usd', 0):.2f}",
                        f"${r.get('profit_usd', 0):.2f}"
                    ),
                )

        except Exception as e:
            print(f"Error al cargar recargas: {str(e)}")
            # Mostrar mensaje de error en tabla
            self.tree_recargas.insert("", "end", values=(
                "--", "--", f"Error: {str(e)[:30]}...", "--", "--", "--", "--", "--"
            ))

    def _eliminar_recarga(self):
        """Elimina la recarga seleccionada de la base de datos"""
        seleccion = self.tree_recargas.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Sin selección", "Selecciona una recarga para eliminar.")
            return

        # Obtener ID de la recarga seleccionada
        item = self.tree_recargas.item(seleccion[0])
        recarga_id = item["values"][0]

        # Verificar que no sea un placeholder
        if recarga_id == "--":
            messagebox.showwarning("⚠️ No válido", "No puedes eliminar este elemento.")
            return

        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar la recarga #{recarga_id}?\n\n"
            f"Trabajador: {item['values'][2]}\n"
            f"Cliente: {item['values'][3]}\n"  # ✅ Agregado cliente en mensaje
            f"Juego: {item['values'][4]}\n"
            f"Monto: {item['values'][5]}\n\n"
            "⚠️ Esta acción no se puede deshacer."
        )

        if respuesta:
            try:
                # Llamar a la función de operations.py
                if eliminar_recarga(recarga_id):
                    messagebox.showinfo("✅ Éxito", f"Recarga #{recarga_id} eliminada correctamente.")
                    self._cargar_historial()  # Actualizar tabla
                else:
                    messagebox.showerror("❌ Error", "No se pudo eliminar la recarga.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo eliminar:\n{str(e)}")