"""
gui/admin_panel.py - PANEL ADMINISTRATIVO TRYHARDS
│
│ Propósito:
│ • Gestionar:
│   - Trabajadores
│   - Países
│   - Métodos de pago
│   - Juegos
│   - Productos
│   - Monedas
│ • Conectado a database/operations (CRUD real).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils.styles import TECH_COLORS
from database.operations import (
    # Trabajadores
    listar_trabajadores_activos,
    agregar_trabajador,
    editar_trabajador,
    eliminar_trabajador,
    # Países
    listar_paises_activos,
    agregar_pais,
    editar_pais,
    eliminar_pais,
    # Métodos de pago
    listar_metodos_pago_activos,
    agregar_metodo_pago,
    editar_metodo_pago,
    eliminar_metodo_pago,
    # Juegos
    listar_juegos_activos,
    agregar_juego,
    editar_juego,
    eliminar_juego,
    # Productos
    listar_productos_activos,
    agregar_producto,
    editar_producto,
    eliminar_producto,
    # Monedas
    listar_monedas_activas,
    agregar_moneda,
    editar_moneda,
    eliminar_moneda,
)


class AdminPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=TECH_COLORS["bg_primary"])
        self._build_layout()
        self._cargar_todos_los_listados()

    # ---------------------------------
    # LAYOUT GENERAL (2 columnas)
    # ---------------------------------
    def _build_layout(self):
        # Columna izquierda
        left_col = tk.Frame(self, bg=TECH_COLORS["bg_primary"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # Columna derecha
        right_col = tk.Frame(self, bg=TECH_COLORS["bg_primary"])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

        # Secciones columna izquierda
        self._build_trabajadores_section(left_col)
        self._build_paises_section(left_col)

        # Secciones columna derecha
        self._build_metodos_pago_section(right_col)
        self._build_juegos_section(right_col)
        self._build_productos_section(right_col)
        self._build_monedas_section(right_col)

    # =================================
    # TRABAJADORES
    # =================================
    def _build_trabajadores_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="TRABAJADORES",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="Nombre:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_trabajador_nombre = ttk.Entry(top, width=25)
        self.entry_trabajador_nombre.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._trabajador_nuevo)
        btn_edit = ttk.Button(top, text="Editar", command=self._trabajador_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._trabajador_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_trabajadores)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "nombre")
        self.tree_trabajadores = ttk.Treeview(
            frame, columns=cols, show="headings", height=5
        )
        self.tree_trabajadores.heading("id", text="ID")
        self.tree_trabajadores.heading("nombre", text="Nombre")
        self.tree_trabajadores.column("id", width=40, anchor="center")
        self.tree_trabajadores.column("nombre", width=180, anchor="w")
        self.tree_trabajadores.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_trabajadores(self):
        self.tree_trabajadores.delete(*self.tree_trabajadores.get_children())
        for row in listar_trabajadores_activos():
            self.tree_trabajadores.insert("", "end", values=(row["id"], row["name"]))

    def _get_trabajador_seleccionado(self):
        sel = self.tree_trabajadores.selection()
        if not sel:
            return None
        return self.tree_trabajadores.item(sel[0], "values")

    def _trabajador_nuevo(self):
        nombre = self.entry_trabajador_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa un nombre de trabajador.")
            return
        agregar_trabajador(nombre)
        self.entry_trabajador_nombre.delete(0, tk.END)
        self._refrescar_trabajadores()

    def _trabajador_editar(self):
        item = self._get_trabajador_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un trabajador.")
            return
        worker_id = int(item[0])
        nuevo_nombre = self.entry_trabajador_nombre.get().strip()
        if not nuevo_nombre:
            messagebox.showerror("Error", "Ingresa el nuevo nombre.")
            return
        editar_trabajador(worker_id, nuevo_nombre)
        self._refrescar_trabajadores()

    def _trabajador_eliminar(self):
        item = self._get_trabajador_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un trabajador.")
            return
        worker_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar este trabajador?"):
            eliminar_trabajador(worker_id)
            self._refrescar_trabajadores()

    # =================================
    # PAÍSES
    # =================================
    def _build_paises_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="PAÍSES",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="País:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_pais_nombre = ttk.Entry(top, width=20)
        self.entry_pais_nombre.pack(side=tk.LEFT, padx=(5, 10))

        tk.Label(
            top,
            text="Moneda:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_pais_moneda = ttk.Entry(top, width=10)
        self.entry_pais_moneda.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._pais_nuevo)
        btn_edit = ttk.Button(top, text="Editar", command=self._pais_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._pais_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_paises)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "nombre", "moneda")
        self.tree_paises = ttk.Treeview(
            frame, columns=cols, show="headings", height=4
        )
        self.tree_paises.heading("id", text="ID")
        self.tree_paises.heading("nombre", text="País")
        self.tree_paises.heading("moneda", text="Moneda")
        self.tree_paises.column("id", width=40, anchor="center")
        self.tree_paises.column("nombre", width=140, anchor="w")
        self.tree_paises.column("moneda", width=80, anchor="center")
        self.tree_paises.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_paises(self):
        self.tree_paises.delete(*self.tree_paises.get_children())
        for row in listar_paises_activos():
            self.tree_paises.insert(
                "", "end", values=(row["id"], row["name"], row["currency_code"])
            )

    def _get_pais_seleccionado(self):
        sel = self.tree_paises.selection()
        if not sel:
            return None
        return self.tree_paises.item(sel[0], "values")

    def _pais_nuevo(self):
        nombre = self.entry_pais_nombre.get().strip()
        moneda = self.entry_pais_moneda.get().strip() or "USD"
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del país.")
            return
        agregar_pais(nombre, moneda)
        self.entry_pais_nombre.delete(0, tk.END)
        self.entry_pais_moneda.delete(0, tk.END)
        self._refrescar_paises()

    def _pais_editar(self):
        item = self._get_pais_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un país.")
            return
        country_id = int(item[0])
        nuevo_nombre = self.entry_pais_nombre.get().strip() or item[1]
        nueva_moneda = self.entry_pais_moneda.get().strip() or item[2]
        editar_pais(country_id, nuevo_nombre, nueva_moneda)
        self._refrescar_paises()

    def _pais_eliminar(self):
        item = self._get_pais_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un país.")
            return
        country_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar este país?"):
            eliminar_pais(country_id)
            self._refrescar_paises()

    # =================================
    # MÉTODOS DE PAGO
    # =================================
    def _build_metodos_pago_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="MÉTODOS DE PAGO",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="Nombre:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_mp_nombre = ttk.Entry(top, width=18)
        self.entry_mp_nombre.pack(side=tk.LEFT, padx=(5, 10))

        tk.Label(
            top,
            text="Tipo:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.combo_mp_tipo = ttk.Combobox(
            top,
            values=["recarga", "remesa", "ambos"],
            width=10,
            state="readonly",
        )
        self.combo_mp_tipo.current(0)
        self.combo_mp_tipo.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._mp_nuevo)
        btn_edit = ttk.Button(top, text="Editar", command=self._mp_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._mp_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_metodos_pago)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "nombre", "tipo")
        self.tree_metodos_pago = ttk.Treeview(
            frame, columns=cols, show="headings", height=4
        )
        self.tree_metodos_pago.heading("id", text="ID")
        self.tree_metodos_pago.heading("nombre", text="Nombre")
        self.tree_metodos_pago.heading("tipo", text="Tipo")
        self.tree_metodos_pago.column("id", width=40, anchor="center")
        self.tree_metodos_pago.column("nombre", width=150, anchor="w")
        self.tree_metodos_pago.column("tipo", width=90, anchor="center")
        self.tree_metodos_pago.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_metodos_pago(self):
        self.tree_metodos_pago.delete(*self.tree_metodos_pago.get_children())
        for row in listar_metodos_pago_activos():
            self.tree_metodos_pago.insert(
                "", "end", values=(row["id"], row["name"], row["type"])
            )

    def _get_metodo_pago_seleccionado(self):
        sel = self.tree_metodos_pago.selection()
        if not sel:
            return None
        return self.tree_metodos_pago.item(sel[0], "values")

    def _mp_nuevo(self):
        nombre = self.entry_mp_nombre.get().strip()
        tipo = self.combo_mp_tipo.get().strip() or "recarga"
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del método de pago.")
            return
        agregar_metodo_pago(nombre, tipo)
        self.entry_mp_nombre.delete(0, tk.END)
        self._refrescar_metodos_pago()

    def _mp_editar(self):
        item = self._get_metodo_pago_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un método de pago.")
            return
        mp_id = int(item[0])
        nuevo_nombre = self.entry_mp_nombre.get().strip() or item[1]
        nuevo_tipo = self.combo_mp_tipo.get().strip() or item[2]
        editar_metodo_pago(mp_id, nuevo_nombre, nuevo_tipo)
        self._refrescar_metodos_pago()

    def _mp_eliminar(self):
        item = self._get_metodo_pago_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un método de pago.")
            return
        mp_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar este método de pago?"):
            eliminar_metodo_pago(mp_id)
            self._refrescar_metodos_pago()

    # =================================
    # JUEGOS
    # =================================
    def _build_juegos_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="JUEGOS",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="Nombre del juego:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_juego_nombre = ttk.Entry(top, width=25)
        self.entry_juego_nombre.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._juego_nuevo)
        btn_edit = ttk.Button(top, text="Editar", command=self._juego_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._juego_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_juegos)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "nombre")
        self.tree_juegos = ttk.Treeview(frame, columns=cols, show="headings", height=3)
        self.tree_juegos.heading("id", text="ID")
        self.tree_juegos.heading("nombre", text="Juego")
        self.tree_juegos.column("id", width=40, anchor="center")
        self.tree_juegos.column("nombre", width=180, anchor="w")
        self.tree_juegos.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_juegos(self):
        self.tree_juegos.delete(*self.tree_juegos.get_children())
        for row in listar_juegos_activos():
            self.tree_juegos.insert("", "end", values=(row["id"], row["name"]))
        # También refrescamos combo de juegos en productos
        juegos = [row["name"] for row in listar_juegos_activos()]
        self.combo_prod_juego["values"] = juegos

    def _get_juego_seleccionado(self):
        sel = self.tree_juegos.selection()
        if not sel:
            return None
        return self.tree_juegos.item(sel[0], "values")

    def _juego_nuevo(self):
        nombre = self.entry_juego_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del juego.")
            return
        agregar_juego(nombre)
        self.entry_juego_nombre.delete(0, tk.END)
        self._refrescar_juegos()

    def _juego_editar(self):
        item = self._get_juego_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un juego.")
            return
        juego_id = int(item[0])
        nuevo_nombre = self.entry_juego_nombre.get().strip()
        if not nuevo_nombre:
            messagebox.showerror("Error", "Ingresa el nuevo nombre del juego.")
            return
        editar_juego(juego_id, nuevo_nombre)
        self._refrescar_juegos()

    def _juego_eliminar(self):
        item = self._get_juego_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un juego.")
            return
        juego_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar este juego?"):
            eliminar_juego(juego_id)
            self._refrescar_juegos()

    # =================================
    # PRODUCTOS
    # =================================
    def _build_productos_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="PRODUCTOS",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="Producto:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_prod_nombre = ttk.Entry(top, width=18)
        self.entry_prod_nombre.pack(side=tk.LEFT, padx=(5, 10))

        tk.Label(
            top,
            text="Juego:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.combo_prod_juego = ttk.Combobox(top, values=[], width=15, state="readonly")
        self.combo_prod_juego.pack(side=tk.LEFT, padx=(5, 10))

        tk.Label(
            top,
            text="Precio base USD:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_prod_precio = ttk.Entry(top, width=8)
        self.entry_prod_precio.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._producto_nuevo)
        btn_edit = ttk.Button(top, text="Editar", command=self._producto_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._producto_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_productos)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "nombre", "juego", "precio")
        self.tree_productos = ttk.Treeview(
            frame, columns=cols, show="headings", height=4
        )
        self.tree_productos.heading("id", text="ID")
        self.tree_productos.heading("nombre", text="Producto")
        self.tree_productos.heading("juego", text="Juego")
        self.tree_productos.heading("precio", text="Precio USD")
        self.tree_productos.column("id", width=40, anchor="center")
        self.tree_productos.column("nombre", width=140, anchor="w")
        self.tree_productos.column("juego", width=120, anchor="w")
        self.tree_productos.column("precio", width=90, anchor="e")
        self.tree_productos.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_productos(self):
        self.tree_productos.delete(*self.tree_productos.get_children())
        for row in listar_productos_activos():
            self.tree_productos.insert(
                "", "end",
                values=(row["id"], row["name"], row.get("game_name", ""), row["price_base_usd"])
            )

    def _get_producto_seleccionado(self):
        sel = self.tree_productos.selection()
        if not sel:
            return None
        return self.tree_productos.item(sel[0], "values")

    def _producto_nuevo(self):
        nombre = self.entry_prod_nombre.get().strip()
        precio_txt = self.entry_prod_precio.get().strip()
        juego_nombre = self.combo_prod_juego.get().strip()

        if not nombre or not precio_txt:
            messagebox.showerror("Error", "Ingresa nombre y precio del producto.")
            return

        try:
            precio = float(precio_txt)
        except ValueError:
            messagebox.showerror("Error", "Precio inválido.")
            return

        # buscar id de juego
        game_id = None
        for row in listar_juegos_activos():
            if row["name"] == juego_nombre:
                game_id = row["id"]
                break

        agregar_producto(nombre, game_id, precio)
        self.entry_prod_nombre.delete(0, tk.END)
        self.entry_prod_precio.delete(0, tk.END)
        self._refrescar_productos()

    def _producto_editar(self):
        item = self._get_producto_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un producto.")
            return

        prod_id = int(item[0])
        nuevo_nombre = self.entry_prod_nombre.get().strip() or item[1]
        nuevo_precio_txt = self.entry_prod_precio.get().strip()
        juego_nombre = self.combo_prod_juego.get().strip()

        # Si no se ingresó precio, usar el actual
        if nuevo_precio_txt:
            try:
                nuevo_precio = float(nuevo_precio_txt)
            except ValueError:
                messagebox.showerror("Error", "Precio inválido.")
                return
        else:
            nuevo_precio = float(item[3])

        # Buscar id de juego
        game_id = None
        if juego_nombre:
            for row in listar_juegos_activos():
                if row["name"] == juego_nombre:
                    game_id = row["id"]
                    break

        editar_producto(prod_id, nuevo_nombre, game_id, nuevo_precio)
        self._refrescar_productos()

    def _producto_eliminar(self):
        item = self._get_producto_seleccionado()
        if not item:
            messagebox.showerror("Error", "Selecciona un producto.")
            return
        prod_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar este producto?"):
            eliminar_producto(prod_id)
            self._refrescar_productos()

    # =================================
    # MONEDAS
    # =================================
    def _build_monedas_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="MONEDAS",
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
            font=("Segoe UI", 11, "bold"),
            labelanchor="nw",
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        top = tk.Frame(frame, bg=TECH_COLORS["bg_primary"])
        top.pack(fill=tk.X, padx=10, pady=(5, 5))

        tk.Label(
            top,
            text="Código:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_moneda_codigo = ttk.Entry(top, width=8)
        self.entry_moneda_codigo.pack(side=tk.LEFT, padx=(5, 10))

        tk.Label(
            top,
            text="Nombre:",
            font=("Segoe UI", 10),
            bg=TECH_COLORS["bg_primary"],
            fg=TECH_COLORS["text_light"],
        ).pack(side=tk.LEFT)

        self.entry_moneda_nombre = ttk.Entry(top, width=18)
        self.entry_moneda_nombre.pack(side=tk.LEFT, padx=(5, 10))

        btn_new = ttk.Button(top, text="Nuevo", command=self._moneda_nueva)
        btn_edit = ttk.Button(top, text="Editar", command=self._moneda_editar)
        btn_delete = ttk.Button(top, text="Eliminar", command=self._moneda_eliminar)
        btn_refresh = ttk.Button(top, text="Refrescar", command=self._refrescar_monedas)

        btn_new.pack(side=tk.LEFT, padx=2)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_refresh.pack(side=tk.LEFT, padx=2)

        cols = ("id", "codigo", "nombre")
        self.tree_monedas = ttk.Treeview(
            frame, columns=cols, show="headings", height=3
        )
        self.tree_monedas.heading("id", text="ID")
        self.tree_monedas.heading("codigo", text="Código")
        self.tree_monedas.heading("nombre", text="Nombre")
        self.tree_monedas.column("id", width=40, anchor="center")
        self.tree_monedas.column("codigo", width=80, anchor="center")
        self.tree_monedas.column("nombre", width=160, anchor="w")
        self.tree_monedas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refrescar_monedas(self):
        self.tree_monedas.delete(*self.tree_monedas.get_children())
        for row in listar_monedas_activas():
            self.tree_monedas.insert(
                "", "end", values=(row["id"], row["code"], row["name"])
            )

    def _get_moneda_seleccionada(self):
        sel = self.tree_monedas.selection()
        if not sel:
            return None
        return self.tree_monedas.item(sel[0], "values")

    def _moneda_nueva(self):
        codigo = self.entry_moneda_codigo.get().strip()
        nombre = self.entry_moneda_nombre.get().strip()
        if not codigo or not nombre:
            messagebox.showerror("Error", "Ingresa código y nombre de la moneda.")
            return
        agregar_moneda(codigo, nombre)
        self.entry_moneda_codigo.delete(0, tk.END)
        self.entry_moneda_nombre.delete(0, tk.END)
        self._refrescar_monedas()

    def _moneda_editar(self):
        item = self._get_moneda_seleccionada()
        if not item:
            messagebox.showerror("Error", "Selecciona una moneda.")
            return
        moneda_id = int(item[0])
        nuevo_codigo = self.entry_moneda_codigo.get().strip() or item[1]
        nuevo_nombre = self.entry_moneda_nombre.get().strip() or item[2]
        editar_moneda(moneda_id, nuevo_codigo, nuevo_nombre)
        self._refrescar_monedas()

    def _moneda_eliminar(self):
        item = self._get_moneda_seleccionada()
        if not item:
            messagebox.showerror("Error", "Selecciona una moneda.")
            return
        moneda_id = int(item[0])
        if messagebox.askyesno("Confirmar", "¿Desactivar esta moneda?"):
            eliminar_moneda(moneda_id)
            self._refrescar_monedas()

    # =================================
    # CARGA INICIAL
    # =================================
    def _cargar_todos_los_listados(self):
        self._refrescar_trabajadores()
        self._refrescar_paises()
        self._refrescar_metodos_pago()
        self._refrescar_juegos()
        self._refrescar_productos()
        self._refrescar_monedas()