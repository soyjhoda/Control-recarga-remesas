"""
gui/saldos_tab.py - GESTIÓN DE SALDOS FINANCIEROS
│
│ Propósito:
│ • Gestionar saldos de cuentas (bancos, wallets, efectivo)
│ • Controlar deducciones pendientes (vueltos, gastos)
│ • Ver resumen financiero automático
│ • Crear snapshots de situación
│ • Interfaz oscura tech con máxima legibilidad
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

from database.operations import (
    # Funciones para cuentas
    listar_cuentas_financieras_activas,
    agregar_cuenta_financiera,
    editar_cuenta_financiera,
    eliminar_cuenta_financiera,
    actualizar_balance_cuenta,

    # Funciones para deducciones
    listar_deducciones_pendientes,
    agregar_deduccion,
    marcar_deduccion_resuelta,
    eliminar_deduccion,

    # Funciones para resumen y snapshots
    obtener_resumen_financiero,
    crear_snapshot_financiero,
    listar_snapshots_financieros,
    eliminar_snapshot_financiero,

    # Funciones de búsqueda/filtro
    buscar_cuentas_por_nombre,
    filtrar_cuentas_por_tipo,
    filtrar_cuentas_por_saldo,
)


class SaldosTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style="Card.TFrame")

        # Caché de datos
        self.cuentas = []
        self.deducciones = []
        self.snapshots = []

        # Variables para filtros
        self.filtro_tipo = tk.StringVar(value="todos")
        self.filtro_saldo_min = tk.StringVar(value="0")
        self.busqueda_nombre = tk.StringVar()

        # Crear canvas con scroll
        self._crear_scrollable_frame()

        # Construir UI
        self._build_ui()
        self.recargar_datos()

    # ---------------------------------
    # MÉTODO PÚBLICO PARA REFRESCAR
    # ---------------------------------
    def recargar_datos(self):
        """Recarga todos los datos desde la base de datos"""
        self._cargar_cuentas()
        self._cargar_deducciones()
        self._cargar_snapshots()
        self._actualizar_resumen()

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
    # UI PRINCIPAL
    # ---------------------------------
    def _build_ui(self):
        # Título principal
        title = ttk.Label(
            self.scrollable_frame,
            text="💰 GESTIÓN DE SALDOS FINANCIEROS",
            font=("Segoe UI", 22, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["bg_card"]
        )
        title.pack(pady=(15, 5))

        # Sección 1: Filtros y búsqueda
        self._crear_seccion_filtros()

        # Sección 2: Cuentas financieras
        self._crear_seccion_cuentas()

        # Sección 3: Actualización masiva
        self._crear_seccion_actualizacion_masiva()

        # Sección 4: Deducciones pendientes
        self._crear_seccion_deducciones()

        # Sección 5: Resumen financiero
        self._crear_seccion_resumen()

        # Sección 6: Snapshots
        self._crear_seccion_snapshots()

    # ---------------------------------
    # SECCIÓN 1: FILTROS
    # ---------------------------------
    def _crear_seccion_filtros(self):
        """Crea la sección de filtros y búsqueda"""
        filtros_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="🔍 FILTROS Y BÚSQUEDA",
            padding=15
        )
        filtros_frame.pack(fill="x", padx=20, pady=10)

        # Fila 1: Búsqueda por nombre
        row1 = ttk.Frame(filtros_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(
            row1,
            text="Buscar cuenta:",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 10))

        self.entry_busqueda = ttk.Entry(
            row1,
            textvariable=self.busqueda_nombre,
            width=30
        )
        self.entry_busqueda.pack(side="left", padx=(0, 20))
        self.entry_busqueda.bind("<KeyRelease>", self._aplicar_filtros)

        ttk.Button(
            row1,
            text="🔍 Buscar",
            command=self._aplicar_filtros,
            style="Secondary.TButton"
        ).pack(side="left", padx=(0, 20))

        ttk.Button(
            row1,
            text="🔄 Limpiar",
            command=self._limpiar_filtros,
            style="Secondary.TButton"
        ).pack(side="left")

        # Fila 2: Filtros por tipo y saldo
        row2 = ttk.Frame(filtros_frame)
        row2.pack(fill="x", pady=10)

        # Filtro por tipo
        ttk.Label(
            row2,
            text="Tipo:",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 10))

        tipos = ["todos", "banco", "wallet", "efectivo", "otro"]
        combo_tipo = ttk.Combobox(
            row2,
            textvariable=self.filtro_tipo,
            values=tipos,
            state="readonly",
            width=12
        )
        combo_tipo.pack(side="left", padx=(0, 20))
        combo_tipo.bind("<<ComboboxSelected>>", self._aplicar_filtros)

        # Filtro por saldo mínimo
        ttk.Label(
            row2,
            text="Saldo >=",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 10))

        entry_saldo_min = ttk.Entry(
            row2,
            textvariable=self.filtro_saldo_min,
            width=10
        )
        entry_saldo_min.pack(side="left", padx=(0, 20))
        entry_saldo_min.bind("<KeyRelease>", self._aplicar_filtros)

        ttk.Label(
            row2,
            text="USD",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 20))

    # ---------------------------------
    # SECCIÓN 2: CUENTAS FINANCIERAS
    # ---------------------------------
    def _crear_seccion_cuentas(self):
        """Crea la sección de cuentas financieras"""
        cuentas_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="🏦 CUENTAS / MÉTODOS DE PAGO",
            padding=15
        )
        cuentas_frame.pack(fill="x", padx=20, pady=10)

        # Frame interno para tabla
        table_frame = ttk.Frame(cuentas_frame)
        table_frame.pack(fill="both", expand=True)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        # Treeview para cuentas
        cols = ("id", "nombre", "tipo", "saldo", "moneda", "etiquetas")
        self.tree_cuentas = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=8,
            yscrollcommand=tree_scroll.set,
            style="Custom.Treeview"
        )
        tree_scroll.config(command=self.tree_cuentas.yview)

        # Configurar columnas
        column_widths = {
            "id": 50,
            "nombre": 180,
            "tipo": 100,
            "saldo": 120,
            "moneda": 80,
            "etiquetas": 150
        }

        headings = {
            "id": "ID",
            "nombre": "NOMBRE",
            "tipo": "TIPO",
            "saldo": "SALDO",
            "moneda": "MONEDA",
            "etiquetas": "ETIQUETAS"
        }

        for col in cols:
            self.tree_cuentas.heading(col, text=headings[col])
            self.tree_cuentas.column(col, width=column_widths.get(col, 100))

        self.tree_cuentas.pack(side="left", fill="both", expand=True)

        # Tags para filas alternadas
        self.tree_cuentas.tag_configure('oddrow', background=self.colors["table_odd"])
        self.tree_cuentas.tag_configure('evenrow', background=self.colors["table_even"])

        # Botones de gestión de cuentas
        btn_frame = ttk.Frame(cuentas_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="➕ AGREGAR CUENTA",
            command=self._abrir_agregar_cuenta,
            style="Success.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="✏️ EDITAR",
            command=self._abrir_editar_cuenta,
            style="Primary.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="🗑️ ELIMINAR",
            command=self._eliminar_cuenta,
            style="Danger.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="💾 GUARDAR CAMBIOS",
            command=self._guardar_actualizacion_masiva,
            style="Success.TButton"
        ).pack(side="right", padx=5)

    # ---------------------------------
    # SECCIÓN 3: ACTUALIZACIÓN MASIVA
    # ---------------------------------
    def _crear_seccion_actualizacion_masiva(self):
        """Crea la sección para actualización masiva de saldos"""
        actualizacion_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📝 ACTUALIZACIÓN MASIVA DE SALDOS",
            padding=15
        )
        actualizacion_frame.pack(fill="x", padx=20, pady=10)

        # Frame para los inputs
        self.frame_actualizacion = ttk.Frame(actualizacion_frame)
        self.frame_actualizacion.pack(fill="x")

        # Encabezados
        headers = ["Cuenta", "Saldo Actual", "Nuevo Saldo", "Diferencia"]
        for i, header in enumerate(headers):
            label = ttk.Label(
                self.frame_actualizacion,
                text=header,
                font=("Segoe UI", 10, "bold"),
                foreground=self.colors["primary"]
            )
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Botón para guardar
        ttk.Button(
            actualizacion_frame,
            text="💾 ACTUALIZAR TODAS LAS CUENTAS",
            command=self._guardar_actualizacion_masiva,
            style="Primary.TButton"
        ).pack(pady=(10, 0))

    # ---------------------------------
    # SECCIÓN 4: DEDUCCIONES
    # ---------------------------------
    def _crear_seccion_deducciones(self):
        """Crea la sección de deducciones pendientes"""
        deducciones_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📉 DEDUCCIONES PENDIENTES",
            padding=15
        )
        deducciones_frame.pack(fill="x", padx=20, pady=10)

        # Frame para lista de deducciones
        self.frame_deducciones = ttk.Frame(deducciones_frame)
        self.frame_deducciones.pack(fill="x")

        # Botones para deducciones
        btn_frame = ttk.Frame(deducciones_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="➕ AGREGAR DEDUCCIÓN",
            command=self._abrir_agregar_deduccion,
            style="Secondary.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="🔄 ACTUALIZAR",
            command=self._cargar_deducciones,
            style="Secondary.TButton"
        ).pack(side="left", padx=5)

    # ---------------------------------
    # SECCIÓN 5: RESUMEN
    # ---------------------------------
    def _crear_seccion_resumen(self):
        """Crea la sección de resumen financiero"""
        resumen_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📊 RESUMEN FINANCIERO",
            padding=20
        )
        resumen_frame.pack(fill="x", padx=20, pady=10)

        # Frame para métricas
        self.frame_resumen = ttk.Frame(resumen_frame)
        self.frame_resumen.pack(fill="x")

        # Botón para refrescar
        ttk.Button(
            resumen_frame,
            text="🔄 ACTUALIZAR RESUMEN",
            command=self._actualizar_resumen,
            style="Primary.TButton"
        ).pack(pady=(10, 0))

    # ---------------------------------
    # SECCIÓN 6: SNAPSHOTS
    # ---------------------------------
    def _crear_seccion_snapshots(self):
        """Crea la sección para snapshots/hitos"""
        snapshots_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📸 SNAPSHOT / HITO ACTUAL",
            padding=15
        )
        snapshots_frame.pack(fill="x", padx=20, pady=(10, 20))

        # Entradas para snapshot
        row1 = ttk.Frame(snapshots_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(
            row1,
            text="Nombre:",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 10))

        self.snapshot_nombre = tk.StringVar(value=f"Saldo {datetime.now().strftime('%d-%b')}")
        entry_nombre = ttk.Entry(row1, textvariable=self.snapshot_nombre, width=30)
        entry_nombre.pack(side="left", padx=(0, 20))

        ttk.Label(
            row1,
            text="Notas:",
            foreground=self.colors["text_light"]
        ).pack(side="left", padx=(0, 10))

        self.snapshot_notas = tk.StringVar()
        entry_notas = ttk.Entry(row1, textvariable=self.snapshot_notas, width=40)
        entry_notas.pack(side="left", padx=(0, 20))

        # Botón para crear snapshot
        ttk.Button(
            snapshots_frame,
            text="💾 GUARDAR SNAPSHOT",
            command=self._crear_snapshot,
            style="Success.TButton"
        ).pack(pady=(10, 0))

    # ---------------------------------
    # FUNCIONES DE CARGA DE DATOS
    # ---------------------------------
    def _cargar_cuentas(self):
        """Carga las cuentas desde la base de datos"""
        try:
            self.cuentas = listar_cuentas_financieras_activas()
            self._actualizar_tabla_cuentas()
            self._actualizar_actualizacion_masiva()
        except Exception as e:
            print(f"Error al cargar cuentas: {e}")
            messagebox.showwarning("⚠️ Advertencia", f"Error al cargar cuentas:\n{str(e)}")

    def _cargar_deducciones(self):
        """Carga las deducciones pendientes"""
        try:
            self.deducciones = listar_deducciones_pendientes()
            self._actualizar_lista_deducciones()
        except Exception as e:
            print(f"Error al cargar deducciones: {e}")

    def _cargar_snapshots(self):
        """Carga los snapshots guardados"""
        try:
            self.snapshots = listar_snapshots_financieros(limite=10)
        except Exception as e:
            print(f"Error al cargar snapshots: {e}")

    def _actualizar_resumen(self):
        """Actualiza el resumen financiero"""
        try:
            resumen = obtener_resumen_financiero()
            self._mostrar_resumen(resumen)
        except Exception as e:
            print(f"Error al obtener resumen: {e}")

    # ---------------------------------
    # FUNCIONES PARA TABLA DE CUENTAS
    # ---------------------------------
    def _actualizar_tabla_cuentas(self):
        """Actualiza la tabla de cuentas con los datos cargados"""
        # Limpiar tabla
        for item in self.tree_cuentas.get_children():
            self.tree_cuentas.delete(item)

        if not self.cuentas:
            self.tree_cuentas.insert("", "end", values=(
                "--", "No hay cuentas", "--", "--", "--", "--"
            ))
            return

        # Aplicar filtros
        cuentas_filtradas = self._aplicar_filtros_a_cuentas()

        # Llenar tabla
        for i, cuenta in enumerate(cuentas_filtradas):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            # Icono según tipo
            icono = "🏦" if cuenta["type"] == "banco" else "💳" if cuenta["type"] == "wallet" else "💰" if cuenta["type"] == "efectivo" else "📁"
            nombre_con_icono = f"{icono} {cuenta['name']}"

            # Color para saldo
            saldo = cuenta["balance"]
            saldo_str = f"${saldo:,.2f}"

            self.tree_cuentas.insert(
                "",
                "end",
                tags=(tag,),
                values=(
                    cuenta["id"],
                    nombre_con_icono,
                    cuenta["type"].capitalize(),
                    saldo_str,
                    cuenta["currency"],
                    cuenta.get("tags", "") or ""
                ),
            )

    def _aplicar_filtros_a_cuentas(self):
        """Aplica los filtros actuales a las cuentas"""
        cuentas_filtradas = self.cuentas.copy()

        # Filtrar por tipo
        tipo_filtro = self.filtro_tipo.get()
        if tipo_filtro != "todos":
            cuentas_filtradas = [c for c in cuentas_filtradas if c["type"] == tipo_filtro]

        # Filtrar por saldo mínimo
        try:
            saldo_min = float(self.filtro_saldo_min.get() or 0)
            cuentas_filtradas = [c for c in cuentas_filtradas if c["balance"] >= saldo_min]
        except ValueError:
            pass

        # Filtrar por búsqueda de nombre
        busqueda = self.busqueda_nombre.get().strip().lower()
        if busqueda:
            cuentas_filtradas = [c for c in cuentas_filtradas if busqueda in c["name"].lower()]

        return cuentas_filtradas

    def _aplicar_filtros(self, event=None):
        """Aplica los filtros actuales"""
        self._actualizar_tabla_cuentas()

    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.filtro_tipo.set("todos")
        self.filtro_saldo_min.set("0")
        self.busqueda_nombre.set("")
        self._actualizar_tabla_cuentas()

    # ---------------------------------
    # FUNCIONES PARA ACTUALIZACIÓN MASIVA
    # ---------------------------------
    def _actualizar_actualizacion_masiva(self):
        """Actualiza la sección de actualización masiva"""
        # Limpiar frame
        for widget in self.frame_actualizacion.winfo_children():
            if widget.grid_info()["row"] > 0:  # Mantener encabezados
                widget.destroy()

        # Crear inputs para cada cuenta
        cuentas = self._aplicar_filtros_a_cuentas()
        for i, cuenta in enumerate(cuentas, start=1):
            # Nombre de la cuenta
            label_nombre = ttk.Label(
                self.frame_actualizacion,
                text=cuenta["name"],
                foreground=self.colors["text_light"]
            )
            label_nombre.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            # Saldo actual
            label_saldo_actual = ttk.Label(
                self.frame_actualizacion,
                text=f"${cuenta['balance']:,.2f}",
                foreground=self.colors["success"]
            )
            label_saldo_actual.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            # Input para nuevo saldo
            nuevo_saldo_var = tk.StringVar(value=str(cuenta["balance"]))
            entry_nuevo_saldo = ttk.Entry(
                self.frame_actualizacion,
                textvariable=nuevo_saldo_var,
                width=15
            )
            entry_nuevo_saldo.grid(row=i, column=2, padx=10, pady=5, sticky="w")
            entry_nuevo_saldo.cuenta_id = cuenta["id"]
            entry_nuevo_saldo.nuevo_saldo_var = nuevo_saldo_var

            # Diferencia (se actualizará después)
            label_diferencia = ttk.Label(
                self.frame_actualizacion,
                text="$0.00",
                foreground=self.colors["accent"]
            )
            label_diferencia.grid(row=i, column=3, padx=10, pady=5, sticky="w")
            label_diferencia.cuenta_id = cuenta["id"]

            # Bind para calcular diferencia
            nuevo_saldo_var.trace_add("write", lambda *args, l=label_diferencia, s=label_saldo_actual, ns=nuevo_saldo_var:
                                     self._calcular_diferencia(l, s, ns))

    def _calcular_diferencia(self, label_diferencia, label_saldo_actual, nuevo_saldo_var):
        """Calcula la diferencia entre saldo actual y nuevo"""
        try:
            saldo_actual_text = label_saldo_actual.cget("text").replace("$", "").replace(",", "")
            saldo_actual = float(saldo_actual_text)
            nuevo_saldo = float(nuevo_saldo_var.get() or 0)
            diferencia = nuevo_saldo - saldo_actual

            # Actualizar etiqueta
            if diferencia > 0:
                color = self.colors["success"]
                signo = "+"
            elif diferencia < 0:
                color = self.colors["danger"]
                signo = ""
            else:
                color = self.colors["text_light"]
                signo = ""

            label_diferencia.config(
                text=f"{signo}${diferencia:,.2f}",
                foreground=color
            )
        except ValueError:
            label_diferencia.config(text="$0.00", foreground=self.colors["text_light"])

    def _guardar_actualizacion_masiva(self):
        """Guarda los cambios de la actualización masiva"""
        cambios = []

        # Recorrer todas las filas de actualización masiva
        for widget in self.frame_actualizacion.winfo_children():
            if hasattr(widget, 'cuenta_id') and hasattr(widget, 'nuevo_saldo_var'):
                try:
                    cuenta_id = widget.cuenta_id
                    nuevo_saldo = float(widget.nuevo_saldo_var.get() or 0)

                    # Encontrar cuenta para obtener saldo actual
                    cuenta = next((c for c in self.cuentas if c["id"] == cuenta_id), None)
                    if cuenta:
                        saldo_actual = cuenta["balance"]
                        if nuevo_saldo != saldo_actual:
                            cambios.append({
                                "id": cuenta_id,
                                "nombre": cuenta["name"],
                                "actual": saldo_actual,
                                "nuevo": nuevo_saldo,
                                "diferencia": nuevo_saldo - saldo_actual
                            })
                except ValueError:
                    continue

        if not cambios:
            messagebox.showinfo("ℹ️ Sin cambios", "No hay cambios para guardar.")
            return

        # Mostrar confirmación
        mensaje = "¿Guardar los siguientes cambios?\n\n"
        for cambio in cambios:
            signo = "+" if cambio["diferencia"] > 0 else ""
            mensaje += f"• {cambio['nombre']}: ${cambio['actual']:.2f} → ${cambio['nuevo']:.2f} ({signo}${cambio['diferencia']:.2f})\n"

        if messagebox.askyesno("💾 Confirmar cambios", mensaje):
            try:
                for cambio in cambios:
                    actualizar_balance_cuenta(
                        cambio["id"],
                        cambio["nuevo"],
                        f"Actualización masiva - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    )

                messagebox.showinfo("✅ Éxito", f"{len(cambios)} cuentas actualizadas correctamente.")
                self.recargar_datos()

            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudieron guardar los cambios:\n{str(e)}")

    # ---------------------------------
    # FUNCIONES PARA DEDUCCIONES
    # ---------------------------------
    def _actualizar_lista_deducciones(self):
        """Actualiza la lista de deducciones pendientes"""
        # Limpiar frame
        for widget in self.frame_deducciones.winfo_children():
            widget.destroy()

        if not self.deducciones:
            label = ttk.Label(
                self.frame_deducciones,
                text="✅ No hay deducciones pendientes",
                foreground=self.colors["success"],
                font=("Segoe UI", 11)
            )
            label.pack(pady=10)
            return

        # Mostrar cada deducción
        for i, ded in enumerate(self.deducciones):
            ded_frame = ttk.Frame(self.frame_deducciones)
            ded_frame.pack(fill="x", pady=5)

            # Checkbox para marcar como resuelta
            var_resuelta = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(
                ded_frame,
                variable=var_resuelta,
                command=lambda d=ded: self._marcar_deduccion_resuelta(d["id"])
            )
            checkbox.pack(side="left", padx=(0, 10))

            # Descripción y monto
            texto = f"• {ded['description']}: ${ded['amount']:.2f}"
            if ded.get('due_date'):
                texto += f" (Vence: {ded['due_date']})"
            if ded.get('account_name'):
                texto += f" [Cuenta: {ded['account_name']}]"

            label = ttk.Label(
                ded_frame,
                text=texto,
                foreground=self.colors["text_light"]
            )
            label.pack(side="left", padx=(0, 10))

            # Botón eliminar
            ttk.Button(
                ded_frame,
                text="🗑️",
                command=lambda d=ded: self._eliminar_deduccion(d["id"]),
                style="Danger.TButton",
                width=3
            ).pack(side="right")

    def _marcar_deduccion_resuelta(self, deduccion_id):
        """Marca una deducción como resuelta"""
        if messagebox.askyesno("✅ Marcar como resuelta", "¿Marcar esta deducción como resuelta?"):
            try:
                if marcar_deduccion_resuelta(deduccion_id):
                    messagebox.showinfo("✅ Éxito", "Deducción marcada como resuelta.")
                    self._cargar_deducciones()
                    self._actualizar_resumen()
                else:
                    messagebox.showerror("❌ Error", "No se pudo marcar la deducción como resuelta.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo marcar como resuelta:\n{str(e)}")

    def _eliminar_deduccion(self, deduccion_id):
        """Elimina una deducción"""
        if messagebox.askyesno("🗑️ Eliminar deducción", "¿Eliminar esta deducción permanentemente?"):
            try:
                if eliminar_deduccion(deduccion_id):
                    messagebox.showinfo("✅ Éxito", "Deducción eliminada.")
                    self._cargar_deducciones()
                    self._actualizar_resumen()
                else:
                    messagebox.showerror("❌ Error", "No se pudo eliminar la deducción.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo eliminar:\n{str(e)}")

    # ---------------------------------
    # FUNCIONES PARA RESUMEN
    # ---------------------------------
    def _mostrar_resumen(self, resumen):
        """Muestra el resumen financiero"""
        # Limpiar frame
        for widget in self.frame_resumen.winfo_children():
            widget.destroy()

        # Crear métricas
        metricas = [
            ("💰 Subtotal (suma cuentas)", f"${resumen['subtotal']:,.2f}", self.colors["primary"]),
            ("📉 Deducciones pendientes", f"-${resumen['total_deducciones']:,.2f}", self.colors["danger"]),
            ("✅ TOTAL REAL", f"${resumen['total_real']:,.2f}", self.colors["success"]),
        ]

        # Mostrar métricas principales
        for i, (texto, valor, color) in enumerate(metricas):
            frame = ttk.Frame(self.frame_resumen)
            frame.grid(row=0, column=i, padx=15, pady=5, sticky="n")

            ttk.Label(
                frame,
                text=texto,
                font=("Segoe UI", 10),
                foreground=self.colors["text_light"]
            ).pack()

            ttk.Label(
                frame,
                text=valor,
                font=("Segoe UI", 18, "bold"),
                foreground=color
            ).pack()

        # Mostrar desglose por tipo
        if resumen.get('desglose_por_tipo'):
            desglose_frame = ttk.Frame(self.frame_resumen)
            desglose_frame.grid(row=1, column=0, columnspan=3, pady=(20, 0), sticky="w")

            ttk.Label(
                desglose_frame,
                text="📊 Desglose por tipo:",
                font=("Segoe UI", 11, "bold"),
                foreground=self.colors["text_light"]
            ).pack(anchor="w")

            for tipo in resumen['desglose_por_tipo']:
                if tipo['total'] > 0:
                    texto = f"  • {tipo['type'].capitalize()}: ${tipo['total']:,.2f}"
                    ttk.Label(
                        desglose_frame,
                        text=texto,
                        foreground=self.colors["text_light"]
                    ).pack(anchor="w")

    # ---------------------------------
    # FUNCIONES PARA SNAPSHOTS
    # ---------------------------------
    def _crear_snapshot(self):
        """Crea un nuevo snapshot"""
        nombre = self.snapshot_nombre.get().strip()
        notas = self.snapshot_notas.get().strip() or None

        if not nombre:
            messagebox.showwarning("⚠️ Nombre requerido", "Debes ingresar un nombre para el snapshot.")
            return

        try:
            snapshot_id = crear_snapshot_financiero(nombre, notas)
            messagebox.showinfo("✅ Éxito", f"Snapshot '{nombre}' guardado correctamente.")

            # Limpiar campos
            self.snapshot_notas.set("")
            self.snapshot_nombre.set(f"Saldo {datetime.now().strftime('%d-%b')}")

            # Recargar snapshots
            self._cargar_snapshots()

        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo crear el snapshot:\n{str(e)}")

    # ---------------------------------
    # FUNCIONES PARA AGREGAR/EDITAR CUENTAS
    # ---------------------------------
    def _abrir_agregar_cuenta(self):
        """Abre ventana para agregar nueva cuenta"""
        self._abrir_ventana_cuenta(None)

    def _abrir_editar_cuenta(self):
        """Abre ventana para editar cuenta seleccionada"""
        seleccion = self.tree_cuentas.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Sin selección", "Selecciona una cuenta para editar.")
            return

        item = self.tree_cuentas.item(seleccion[0])
        cuenta_id = item["values"][0]

        if cuenta_id == "--":
            return

        self._abrir_ventana_cuenta(cuenta_id)

    def _abrir_ventana_cuenta(self, cuenta_id):
        """Abre ventana para agregar/editar cuenta"""
        ventana = tk.Toplevel(self)
        ventana.title("➕ Agregar Cuenta" if cuenta_id is None else "✏️ Editar Cuenta")
        # AUMENTÉ EL TAMAÑO: de "500x400" a "500x550" para que muestre TODO
        ventana.geometry("540x530")
        ventana.configure(bg=self.colors["bg_primary"])
        ventana.resizable(False, False)

        # Centrar ventana
        ventana.transient(self)
        ventana.grab_set()

        # Frame principal con scroll para muchos campos
        main_frame = ttk.Frame(ventana, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Crear canvas con scroll para muchos campos
        canvas = tk.Canvas(main_frame, highlightthickness=0, bg=self.colors["bg_primary"])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Campos del formulario en el frame con scroll
        row_num = 0

        ttk.Label(scrollable_frame, text="Nombre:", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        nombre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=nombre_var, width=40).grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        ttk.Label(scrollable_frame, text="Tipo:", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        tipo_var = tk.StringVar(value="wallet")
        combo_tipo = ttk.Combobox(scrollable_frame, textvariable=tipo_var, values=["banco", "wallet", "efectivo", "otro"], state="readonly", width=37)
        combo_tipo.grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        ttk.Label(scrollable_frame, text="Saldo inicial:", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        saldo_var = tk.StringVar(value="0.00")
        ttk.Entry(scrollable_frame, textvariable=saldo_var, width=40).grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        ttk.Label(scrollable_frame, text="Moneda:", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        moneda_var = tk.StringVar(value="USD")
        ttk.Entry(scrollable_frame, textvariable=moneda_var, width=40).grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        ttk.Label(scrollable_frame, text="Etiquetas (opcional):", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        etiquetas_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=etiquetas_var, width=40).grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        ttk.Label(scrollable_frame, text="Notas (opcional):", foreground=self.colors["text_light"]).grid(row=row_num, column=0, sticky="w", pady=10)
        notas_text = tk.Text(scrollable_frame, width=30, height=6)  # Más alto para notas
        notas_text.grid(row=row_num, column=1, pady=10, padx=(10, 0))
        row_num += 1

        # Si es edición, cargar datos existentes
        if cuenta_id is not None:
            cuenta = next((c for c in self.cuentas if c["id"] == cuenta_id), None)
            if cuenta:
                nombre_var.set(cuenta["name"])
                tipo_var.set(cuenta["type"])
                saldo_var.set(str(cuenta["balance"]))
                moneda_var.set(cuenta["currency"])
                etiquetas_var.set(cuenta.get("tags", "") or "")
                notas_text.delete("1.0", "end")
                notas_text.insert("1.0", cuenta.get("notes", "") or "")

        # Frame para botones (FUERA del scroll para que siempre sean visibles)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        def guardar_cuenta():
            try:
                nombre = nombre_var.get().strip()
                tipo = tipo_var.get()
                saldo = float(saldo_var.get() or 0)
                moneda = moneda_var.get().strip().upper()
                etiquetas = etiquetas_var.get().strip() or None
                notas = notas_text.get("1.0", "end").strip() or None

                if not nombre:
                    messagebox.showwarning("⚠️ Nombre requerido", "Debes ingresar un nombre para la cuenta.")
                    return

                if cuenta_id is None:
                    # Agregar nueva cuenta
                    nueva_id = agregar_cuenta_financiera(
                        nombre, tipo, saldo, moneda, etiquetas, notas
                    )
                    if nueva_id:
                        messagebox.showinfo("✅ Éxito", f"Cuenta '{nombre}' agregada correctamente.")
                        ventana.destroy()
                        self.recargar_datos()
                    else:
                        messagebox.showerror("❌ Error", "No se pudo agregar la cuenta.")
                else:
                    # Editar cuenta existente
                    if editar_cuenta_financiera(
                        cuenta_id,
                        nuevo_nombre=nombre,
                        nuevo_tipo=tipo,
                        nuevo_balance=saldo,
                        nueva_currency=moneda,
                        nuevos_tags=etiquetas,
                        nuevas_notas=notas
                    ):
                        messagebox.showinfo("✅ Éxito", f"Cuenta '{nombre}' actualizada correctamente.")
                        ventana.destroy()
                        self.recargar_datos()
                    else:
                        messagebox.showerror("❌ Error", "No se pudo actualizar la cuenta.")

            except ValueError as e:
                messagebox.showerror("❌ Error de formato", f"Verifica los valores ingresados:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo guardar la cuenta:\n{str(e)}")

        ttk.Button(
            btn_frame,
            text="💾 GUARDAR",
            command=guardar_cuenta,
            style="Success.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="❌ CANCELAR",
            command=ventana.destroy,
            style="Danger.TButton"
        ).pack(side="left", padx=10)

        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _eliminar_cuenta(self):
        """Elimina la cuenta seleccionada"""
        seleccion = self.tree_cuentas.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Sin selección", "Selecciona una cuenta para eliminar.")
            return

        item = self.tree_cuentas.item(seleccion[0])
        cuenta_id = item["values"][0]
        cuenta_nombre = item["values"][1].split(" ", 1)[1] if " " in item["values"][1] else item["values"][1]

        if cuenta_id == "--":
            return

        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar la cuenta '{cuenta_nombre}'?\n\n"
            "⚠️ Esta acción marcará la cuenta como inactiva, pero no eliminará su historial."
        )

        if respuesta:
            try:
                if eliminar_cuenta_financiera(cuenta_id):
                    messagebox.showinfo("✅ Éxito", f"Cuenta '{cuenta_nombre}' eliminada correctamente.")
                    self.recargar_datos()
                else:
                    messagebox.showerror("❌ Error", "No se pudo eliminar la cuenta.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo eliminar:\n{str(e)}")

    # ---------------------------------
    # FUNCIONES PARA AGREGAR DEDUCCIÓN
    # ---------------------------------
    def _abrir_agregar_deduccion(self):
        """Abre ventana para agregar nueva deducción"""
        ventana = tk.Toplevel(self)
        ventana.title("➕ Agregar Deducción")
        # AUMENTÉ EL TAMAÑO: de "500x350" a "500x500" para asegurar que se vea todo
        ventana.geometry("600x600")
        ventana.configure(bg=self.colors["bg_primary"])
        ventana.resizable(False, False)

        # Centrar ventana
        ventana.transient(self)
        ventana.grab_set()

        # Frame principal
        main_frame = ttk.Frame(ventana, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Campos del formulario
        ttk.Label(main_frame, text="Descripción:", foreground=self.colors["text_light"]).grid(row=0, column=0, sticky="w", pady=10)
        descripcion_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=descripcion_var, width=40).grid(row=0, column=1, pady=10, padx=(10, 0))

        ttk.Label(main_frame, text="Monto:", foreground=self.colors["text_light"]).grid(row=1, column=0, sticky="w", pady=10)
        monto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=monto_var, width=40).grid(row=1, column=1, pady=10, padx=(10, 0))

        ttk.Label(main_frame, text="Cuenta relacionada (opcional):", foreground=self.colors["text_light"]).grid(row=2, column=0, sticky="w", pady=10)
        cuenta_var = tk.StringVar()
        nombres_cuentas = [c["name"] for c in self.cuentas]
        combo_cuenta = ttk.Combobox(main_frame, textvariable=cuenta_var, values=nombres_cuentas, width=37)
        combo_cuenta.grid(row=2, column=1, pady=10, padx=(10, 0))

        ttk.Label(main_frame, text="Fecha límite (opcional):", foreground=self.colors["text_light"]).grid(row=3, column=0, sticky="w", pady=10)
        fecha_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=fecha_var, width=40).grid(row=3, column=1, pady=10, padx=(10, 0))

        ttk.Label(main_frame, text="Notas (opcional):", foreground=self.colors["text_light"]).grid(row=4, column=0, sticky="w", pady=10)
        notas_text = tk.Text(main_frame, width=30, height=6)  # Más alto
        notas_text.grid(row=4, column=1, pady=10, padx=(10, 0))

        # Botones (en fila adicional para mejor visibilidad)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        def guardar_deduccion():
            try:
                descripcion = descripcion_var.get().strip()
                monto = float(monto_var.get() or 0)
                cuenta_nombre = cuenta_var.get().strip()
                fecha_limite = fecha_var.get().strip() or None
                notas = notas_text.get("1.0", "end").strip() or None

                if not descripcion:
                    messagebox.showwarning("⚠️ Descripción requerida", "Debes ingresar una descripción.")
                    return

                if monto <= 0:
                    messagebox.showwarning("⚠️ Monto inválido", "El monto debe ser mayor a cero.")
                    return

                # Obtener ID de la cuenta si se seleccionó una
                cuenta_id = None
                if cuenta_nombre:
                    cuenta = next((c for c in self.cuentas if c["name"] == cuenta_nombre), None)
                    if cuenta:
                        cuenta_id = cuenta["id"]

                # Agregar deducción
                nueva_id = agregar_deduccion(descripcion, monto, cuenta_id, fecha_limite, notas)
                if nueva_id:
                    messagebox.showinfo("✅ Éxito", f"Deducción '{descripcion}' agregada correctamente.")
                    ventana.destroy()
                    self._cargar_deducciones()
                    self._actualizar_resumen()
                else:
                    messagebox.showerror("❌ Error", "No se pudo agregar la deducción.")

            except ValueError as e:
                messagebox.showerror("❌ Error de formato", f"Verifica los valores ingresados:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo guardar la deducción:\n{str(e)}")

        ttk.Button(
            btn_frame,
            text="💾 GUARDAR",
            command=guardar_deduccion,
            style="Success.TButton"
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="❌ CANCELAR",
            command=ventana.destroy,
            style="Danger.TButton"
        ).pack(side="left", padx=10)