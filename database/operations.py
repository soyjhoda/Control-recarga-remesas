"""
database/operations.py - [translate:BASE DE DATOS TRYHARDS - CATÁLOGOS + TRANSACCIONES]
│
│ Propósito:
│ • Inicializar base de datos SQLite (app.db)
│ • CRUD para catálogos usados en AdminPanel:
│     - Trabajadores, Países, Métodos de pago, Juegos, Productos, Monedas
│ • Tablas operacionales para Recargas y Remesas
│ • Funciones especiales para Dashboard/Historial
│ • ✅ NUEVO: Gestión de saldos financieros
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from utils.config import DB_PATH

# ========================================
# 🔗 CONEXIÓN BÁSICA
# ========================================

def get_connection() -> sqlite3.Connection:
    """
    Abre conexión a app.db (en carpeta data).
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ========================================
# 🧱 CREACIÓN Y ACTUALIZACIÓN DE TABLAS
# ========================================

def _create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Trabajadores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            is_active   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Países
    cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            currency_code TEXT NOT NULL DEFAULT 'USD',
            is_active     INTEGER NOT NULL DEFAULT 1,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Métodos de pago
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            type       TEXT NOT NULL,  -- recarga | remesa | ambos
            is_active  INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Juegos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            is_active  INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Productos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            game_id          INTEGER,
            price_base_usd   REAL NOT NULL DEFAULT 0.0,
            is_active        INTEGER NOT NULL DEFAULT 1,
            created_at       TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (game_id) REFERENCES games(id)
        );
    """)

    # Monedas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT NOT NULL,  -- CLP, COP, USD, etc.
            name       TEXT NOT NULL,
            is_active  INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Recargas (TODO EN USD) - CON CAMPO CLIENTE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recharges (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            date                  TEXT NOT NULL,
            worker_id             INTEGER NOT NULL,
            country_id            INTEGER NOT NULL,
            game_id               INTEGER,
            product_id            INTEGER,
            payment_method_id     INTEGER NOT NULL,
            amount_received_usd   REAL NOT NULL,
            cost_usd              REAL NOT NULL,
            seller_commission_usd REAL NOT NULL,
            profit_usd            REAL NOT NULL,
            customer_name         TEXT,               -- ✅ NUEVO CAMPO: Nombre del cliente
            notes                 TEXT,
            created_at            TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (worker_id)         REFERENCES workers(id),
            FOREIGN KEY (country_id)        REFERENCES countries(id),
            FOREIGN KEY (game_id)           REFERENCES games(id),
            FOREIGN KEY (product_id)        REFERENCES products(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
        );
    """)

    # REMESAS - NUEVA ESTRUCTURA COMPLETA
    cur.execute("""
        CREATE TABLE IF NOT EXISTS remittances (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            date                    TEXT NOT NULL,
            worker_id               INTEGER NOT NULL,
            country_id              INTEGER NOT NULL,
            payment_method_id       INTEGER NOT NULL,

            -- REMITENTE (quien envía)
            sender_name             TEXT NOT NULL,
            sender_phone            TEXT,

            -- MONEDA Y CONVERSIÓN A BOLIVARES
            currency_id             INTEGER NOT NULL,
            amount_origin           REAL NOT NULL,      -- 100,000 CLP
            rate_origin_to_bs       REAL NOT NULL,      -- 0.4170 (por cada peso)
            amount_destiny_bs       REAL NOT NULL,      -- 41,700 Bs (calculado: origin * rate)

            -- BENEFICIARIO (quien recibe)
            receiver_name           TEXT NOT NULL,
            receiver_phone          TEXT,

            -- CONVERSIÓN A USDT (COMPRA)
            rate_buy_usdt           REAL NOT NULL,      -- 939.06 CLP/USDT
            usdt_received           REAL NOT NULL,      -- 106.41 USDT (calculado: origin / rate_buy)

            -- CONVERSIÓN USDT A BS (VENTA)
            rate_sell_usdt_bs       REAL NOT NULL,      -- 414.00 Bs/USDT
            usdt_spent              REAL NOT NULL,      -- 100.78 USDT (calculado: destiny_bs / rate_sell)

            -- GANANCIAS EN USDT
            profit_gross_usdt       REAL NOT NULL,      -- 5.63 USDT (recibido - gastado)
            seller_commission_usdt  REAL NOT NULL,      -- 0.50 USDT (comisión trabajador)
            profit_net_usdt         REAL NOT NULL,      -- 5.13 USDT (ganancia neta)

            notes                   TEXT,
            created_at              TEXT NOT NULL DEFAULT (datetime('now')),

            FOREIGN KEY (worker_id)         REFERENCES workers(id),
            FOREIGN KEY (country_id)        REFERENCES countries(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
            FOREIGN KEY (currency_id)       REFERENCES currencies(id)
        );
    """)

    # ✅ NUEVO: CUENTAS FINANCIERAS (para gestión de saldos)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS financial_accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,  -- Ej: "Banco Venezuela", "Airtm", "Binance"
            type        TEXT NOT NULL,         -- banco, wallet, efectivo, otro
            balance     REAL NOT NULL DEFAULT 0.0,
            currency    TEXT NOT NULL DEFAULT 'USD',
            tags        TEXT,                  -- JSON o texto separado por comas: "liquidez,recargas"
            notes       TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # ✅ NUEVO: DEDUCCIONES / GASTOS PENDIENTES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS financial_deductions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,          -- "Vuelto a Carlos", "Comisión PayPal"
            amount      REAL NOT NULL,          -- Monto negativo (siempre positivo en BD, tiene signo negativo en lógica)
            status      TEXT NOT NULL DEFAULT 'pending',  -- pending, resolved
            account_id  INTEGER,                -- Opcional: relacionado con una cuenta específica
            due_date    TEXT,                   -- Fecha límite opcional
            notes       TEXT,
            resolved_at TEXT,                   -- Cuando se marca como resuelto
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (account_id) REFERENCES financial_accounts(id)
        );
    """)

    # ✅ NUEVO: HISTORIAL DE MOVIMIENTOS DE CUENTAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS account_movements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER NOT NULL,
            type        TEXT NOT NULL,          -- deposit, withdrawal, adjustment
            amount      REAL NOT NULL,
            old_balance REAL NOT NULL,
            new_balance REAL NOT NULL,
            description TEXT NOT NULL,
            notes       TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (account_id) REFERENCES financial_accounts(id)
        );
    """)

    # ✅ NUEVO: SNAPSHOTS DE SITUACIÓN FINANCIERA
    cur.execute("""
        CREATE TABLE IF NOT EXISTS financial_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,          -- "Saldo 10-Dic", "Antes de pagar proveedores"
            total_balance REAL NOT NULL,
            subtotal     REAL NOT NULL,         -- Suma de todas las cuentas
            total_deductions REAL NOT NULL,     -- Suma de deducciones pendientes
            notes        TEXT,
            snapshot_data TEXT NOT NULL,        -- JSON con detalles completos
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    conn.commit()

def _actualizar_esquema(conn: sqlite3.Connection) -> None:
    """
    ✅ SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA DE ESQUEMA
    Agrega columnas faltantes a tablas existentes SIN perder datos.
    Se ejecuta cada vez que se inicia la aplicación.
    """
    cur = conn.cursor()

    try:
        # Verificar si la columna customer_name existe en recharges
        cur.execute("PRAGMA table_info(recharges)")
        columnas = [col[1] for col in cur.fetchall()]  # Nombre de columnas

        if 'customer_name' not in columnas:
            print("🔄 Actualizando esquema: agregando customer_name a recharges...")
            cur.execute("ALTER TABLE recharges ADD COLUMN customer_name TEXT")
            conn.commit()
            print("✅ Columna customer_name agregada exitosamente")

    except Exception as e:
        print(f"⚠️ Error al verificar/esquema recharges: {e}")
        # No hacemos commit si hay error

    # En el futuro, puedes agregar más verificaciones aquí:
    # Ejemplo: verificar otras columnas nuevas, tablas nuevas, etc.

    # try:
    #     cur.execute("PRAGMA table_info(otra_tabla)")
    #     columnas = [col[1] for col in cur.fetchall()]
    #     if 'nueva_columna' not in columnas:
    #         cur.execute("ALTER TABLE otra_tabla ADD COLUMN nueva_columna TEXT")
    #         conn.commit()
    # except Exception as e:
    #     print(f"⚠️ Error al verificar otra_tabla: {e}")

# ========================================
# 🚀 INICIALIZAR DESDE main.py
# ========================================

def inicializar_base_de_datos() -> None:
    """
    Crea app.db y todas las tablas necesarias si no existen.
    Actualiza el esquema de tablas existentes.
    Se llama una sola vez al iniciar la aplicación.
    """
    conn = get_connection()
    _create_tables(conn)       # ✅ Crea tablas si no existen
    _actualizar_esquema(conn)  # ✅ Actualiza tablas existentes (NUEVO)
    conn.close()

# ========================================
# 🏢 TRABAJADORES (CRUD)
# ========================================

def agregar_trabajador(nombre: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO workers (name) VALUES (?)", (nombre,))
    conn.commit()
    worker_id = cur.lastrowid
    conn.close()
    return worker_id

def editar_trabajador(worker_id: int, nuevo_nombre: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE workers SET name = ? WHERE id = ?", (nuevo_nombre, worker_id))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_trabajador(worker_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE workers SET is_active = 0 WHERE id = ?", (worker_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_trabajadores_activos() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM workers WHERE is_active = 1 ORDER BY name;"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 🌍 PAÍSES (CRUD)
# ========================================

def agregar_pais(nombre: str, currency_code: str = "USD") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO countries (name, currency_code) VALUES (?, ?)",
        (nombre, currency_code),
    )
    conn.commit()
    country_id = cur.lastrowid
    conn.close()
    return country_id

def editar_pais(country_id: int, nuevo_nombre: str, nuevo_currency: Optional[str] = None) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    if nuevo_currency:
        cur.execute(
            "UPDATE countries SET name = ?, currency_code = ? WHERE id = ?",
            (nuevo_nombre, nuevo_currency, country_id),
        )
    else:
        cur.execute(
            "UPDATE countries SET name = ? WHERE id = ?",
            (nuevo_nombre, country_id),
        )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_pais(country_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE countries SET is_active = 0 WHERE id = ?", (country_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_paises_activos() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, currency_code FROM countries WHERE is_active = 1 ORDER BY name;"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 💳 MÉTODOS DE PAGO (CRUD)
# ========================================

def agregar_metodo_pago(nombre: str, tipo: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payment_methods (name, type) VALUES (?, ?)",
        (nombre, tipo),
    )
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid

def editar_metodo_pago(mp_id: int, nuevo_nombre: str, nuevo_tipo: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE payment_methods SET name = ?, type = ? WHERE id = ?",
        (nuevo_nombre, nuevo_tipo, mp_id)
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_metodo_pago(mp_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE payment_methods SET is_active = 0 WHERE id = ?", (mp_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_metodos_pago_activos() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, type FROM payment_methods WHERE is_active = 1 ORDER BY name;"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 🎮 JUEGOS (CRUD)
# ========================================

def agregar_juego(nombre: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO games (name) VALUES (?)", (nombre,))
    conn.commit()
    gid = cur.lastrowid
    conn.close()
    return gid

def editar_juego(game_id: int, nuevo_nombre: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE games SET name = ? WHERE id = ?", (nuevo_nombre, game_id))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_juego(game_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE games SET is_active = 0 WHERE id = ?", (game_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_juegos_activos() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM games WHERE is_active = 1 ORDER BY name;")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 📦 PRODUCTOS (CRUD)
# ========================================

def agregar_producto(nombre: str, game_id: Optional[int], precio_base_usd: float) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, game_id, price_base_usd) VALUES (?, ?, ?)",
        (nombre, game_id, precio_base_usd),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid

def editar_producto(prod_id: int, nuevo_nombre: str, nuevo_game_id: Optional[int], nuevo_precio: float) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET name = ?, game_id = ?, price_base_usd = ? WHERE id = ?",
        (nuevo_nombre, nuevo_game_id, nuevo_precio, prod_id)
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_producto(prod_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET is_active = 0 WHERE id = ?", (prod_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_productos_activos() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.name, p.price_base_usd, g.name AS game_name
        FROM products p
        LEFT JOIN games g ON p.game_id = g.id
        WHERE p.is_active = 1
        ORDER BY p.name;
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 💱 MONEDAS (CRUD)
# ========================================

def agregar_moneda(code: str, name: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO currencies (code, name) VALUES (?, ?)",
        (code.upper(), name),
    )
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid

def editar_moneda(currency_id: int, nuevo_codigo: str, nuevo_nombre: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE currencies SET code = ?, name = ? WHERE id = ?",
        (nuevo_codigo.upper(), nuevo_nombre, currency_id)
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_moneda(currency_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE currencies SET is_active = 0 WHERE id = ?", (currency_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_monedas_activas() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, code, name FROM currencies WHERE is_active = 1 ORDER BY code;"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 🔁 RECARGAS: INSERCIÓN BÁSICA EN USD
# ========================================

def agregar_recarga(
    date_str: str,
    worker_id: int,
    country_id: int,
    payment_method_id: int,
    amount_received_usd: float,
    cost_usd: float,
    seller_commission_usd: float,
    game_id: Optional[int] = None,
    product_id: Optional[int] = None,
    customer_name: Optional[str] = None,  # ✅ NUEVO PARÁMETRO: Nombre del cliente
    notes: Optional[str] = None,
) -> int:
    """
    Crea una recarga calculando ganancia en USD:
    ganancia = recibido - costo - comisión_vendedor
    """
    profit_usd = amount_received_usd - cost_usd - seller_commission_usd

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO recharges (
            date, worker_id, country_id, game_id, product_id,
            payment_method_id, amount_received_usd, cost_usd,
            seller_commission_usd, profit_usd, customer_name, notes  -- ✅ Agregado customer_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  -- ✅ Un parámetro más
    """, (
        date_str, worker_id, country_id, game_id, product_id,
        payment_method_id, amount_received_usd, cost_usd,
        seller_commission_usd, profit_usd, customer_name, notes  # ✅ Agregado customer_name
    ))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid

# ========================================
# 🔁 RECARGAS: FUNCIONES COMPLETAS
# ========================================

def listar_recargas() -> list[dict[str, Any]]:
    """
    Lista todas las recargas con información completa.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.*,
            w.name as worker_name,
            c.name as country_name,
            g.name as game_name,
            p.name as product_name,
            pm.name as payment_method_name
        FROM recharges r
        LEFT JOIN workers w ON r.worker_id = w.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN games g ON r.game_id = g.id
        LEFT JOIN products p ON r.product_id = p.id
        LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
        ORDER BY r.date DESC, r.id DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def eliminar_recarga(recarga_id: int) -> bool:
    """
    Elimina físicamente una recarga (DELETE).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recharges WHERE id = ?", (recarga_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def editar_recarga(
    recarga_id: int,
    date_str: str,
    worker_id: int,
    country_id: int,
    payment_method_id: int,
    amount_received_usd: float,
    cost_usd: float,
    seller_commission_usd: float,
    game_id: Optional[int] = None,
    product_id: Optional[int] = None,
    customer_name: Optional[str] = None,  # ✅ NUEVO PARÁMETRO: Nombre del cliente
    notes: Optional[str] = None,
) -> bool:
    """
    Edita una recarga recalculando la ganancia.
    """
    profit_usd = amount_received_usd - cost_usd - seller_commission_usd

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE recharges SET
            date = ?, worker_id = ?, country_id = ?, game_id = ?, product_id = ?,
            payment_method_id = ?, amount_received_usd = ?, cost_usd = ?,
            seller_commission_usd = ?, profit_usd = ?, customer_name = ?, notes = ?  -- ✅ Agregado customer_name
        WHERE id = ?
    """, (
        date_str, worker_id, country_id, game_id, product_id,
        payment_method_id, amount_received_usd, cost_usd,
        seller_commission_usd, profit_usd, customer_name, notes, recarga_id  # ✅ Agregado customer_name
    ))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

# ========================================
# 🔁 REMESAS: NUEVA ESTRUCTURA COMPLETA
# ========================================

def agregar_remesa(
    date_str: str,
    worker_id: int,
    country_id: int,
    payment_method_id: int,
    currency_id: int,
    sender_name: str,
    sender_phone: str,
    amount_origin: float,
    rate_origin_to_bs: float,
    receiver_name: str,
    receiver_phone: str,
    rate_buy_usdt: float,
    rate_sell_usdt_bs: float,
    seller_commission_usdt: float,
    notes: Optional[str] = None,
) -> int:
    """
    Registra una remesa con la nueva lógica de conversión:

    PASO 1: Conversión a Bolívares
    - amount_destiny_bs = amount_origin * rate_origin_to_bs

    PASO 2: Conversión a USDT (COMPRA)
    - usdt_received = amount_origin / rate_buy_usdt

    PASO 3: Conversión USDT a Bs (VENTA)
    - usdt_spent = amount_destiny_bs / rate_sell_usdt_bs

    PASO 4: Ganancias
    - profit_gross = usdt_received - usdt_spent
    - profit_net = profit_gross - seller_commission_usdt
    """

    # CÁLCULOS AUTOMÁTICOS
    amount_destiny_bs = amount_origin * rate_origin_to_bs
    usdt_received = amount_origin / rate_buy_usdt
    usdt_spent = amount_destiny_bs / rate_sell_usdt_bs
    profit_gross_usdt = usdt_received - usdt_spent
    profit_net_usdt = profit_gross_usdt - seller_commission_usdt

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO remittances (
            date, worker_id, country_id, payment_method_id, currency_id,
            sender_name, sender_phone,
            amount_origin, rate_origin_to_bs, amount_destiny_bs,
            receiver_name, receiver_phone,
            rate_buy_usdt, usdt_received,
            rate_sell_usdt_bs, usdt_spent,
            profit_gross_usdt, seller_commission_usdt, profit_net_usdt,
            notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date_str, worker_id, country_id, payment_method_id, currency_id,
        sender_name, sender_phone,
        amount_origin, rate_origin_to_bs, amount_destiny_bs,
        receiver_name, receiver_phone,
        rate_buy_usdt, usdt_received,
        rate_sell_usdt_bs, usdt_spent,
        profit_gross_usdt, seller_commission_usdt, profit_net_usdt,
        notes
    ))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid

def editar_remesa(
    remesa_id: int,
    date_str: str,
    worker_id: int,
    country_id: int,
    payment_method_id: int,
    currency_id: int,
    sender_name: str,
    sender_phone: str,
    amount_origin: float,
    rate_origin_to_bs: float,
    receiver_name: str,
    receiver_phone: str,
    rate_buy_usdt: float,
    rate_sell_usdt_bs: float,
    seller_commission_usdt: float,
    notes: Optional[str] = None,
) -> bool:
    """
    Edita una remesa recalculando todos los valores.
    """
    # RECALCULAR
    amount_destiny_bs = amount_origin * rate_origin_to_bs
    usdt_received = amount_origin / rate_buy_usdt
    usdt_spent = amount_destiny_bs / rate_sell_usdt_bs
    profit_gross_usdt = usdt_received - usdt_spent
    profit_net_usdt = profit_gross_usdt - seller_commission_usdt

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE remittances SET
            date = ?, worker_id = ?, country_id = ?, payment_method_id = ?, currency_id = ?,
            sender_name = ?, sender_phone = ?,
            amount_origin = ?, rate_origin_to_bs = ?, amount_destiny_bs = ?,
            receiver_name = ?, receiver_phone = ?,
            rate_buy_usdt = ?, usdt_received = ?,
            rate_sell_usdt_bs = ?, usdt_spent = ?,
            profit_gross_usdt = ?, seller_commission_usdt = ?, profit_net_usdt = ?,
            notes = ?
        WHERE id = ?
    """, (
        date_str, worker_id, country_id, payment_method_id, currency_id,
        sender_name, sender_phone,
        amount_origin, rate_origin_to_bs, amount_destiny_bs,
        receiver_name, receiver_phone,
        rate_buy_usdt, usdt_received,
        rate_sell_usdt_bs, usdt_spent,
        profit_gross_usdt, seller_commission_usdt, profit_net_usdt,
        notes, remesa_id
    ))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_remesa(remesa_id: int) -> bool:
    """
    Elimina físicamente una remesa (DELETE).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM remittances WHERE id = ?", (remesa_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_remesas() -> list[dict[str, Any]]:
    """
    Lista todas las remesas con información completa.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.*,
            w.name as worker_name,
            c.name as country_name,
            pm.name as payment_method_name,
            cu.code as currency_code,
            cu.name as currency_name
        FROM remittances r
        LEFT JOIN workers w ON r.worker_id = w.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
        LEFT JOIN currencies cu ON r.currency_id = cu.id
        ORDER BY r.date DESC, r.id DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# ✅ NUEVO: GESTIÓN DE SALDOS FINANCIEROS
# ========================================

# 🔸 CUENTAS FINANCIERAS
def agregar_cuenta_financiera(
    nombre: str,
    tipo: str = "otro",
    balance: float = 0.0,
    currency: str = "USD",
    tags: Optional[str] = None,
    notas: Optional[str] = None
) -> int:
    """
    Agrega una nueva cuenta financiera (ej: Banco Venezuela, Airtm, Binance).
    """
    conn = get_connection()
    cur = conn.cursor()

    # Verificar si ya existe
    cur.execute("SELECT id FROM financial_accounts WHERE name = ?", (nombre,))
    if cur.fetchone():
        conn.close()
        raise ValueError(f"Ya existe una cuenta con el nombre '{nombre}'")

    cur.execute("""
        INSERT INTO financial_accounts (name, type, balance, currency, tags, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, tipo, balance, currency, tags, notas))

    conn.commit()
    cuenta_id = cur.lastrowid

    # Registrar movimiento inicial
    if balance != 0:
        cur.execute("""
            INSERT INTO account_movements (account_id, type, amount, old_balance, new_balance, description)
            VALUES (?, 'deposit', ?, 0.0, ?, 'Saldo inicial')
        """, (cuenta_id, balance, balance))
        conn.commit()

    conn.close()
    return cuenta_id

def editar_cuenta_financiera(
    cuenta_id: int,
    nuevo_nombre: Optional[str] = None,
    nuevo_tipo: Optional[str] = None,
    nuevo_balance: Optional[float] = None,
    nueva_currency: Optional[str] = None,
    nuevos_tags: Optional[str] = None,
    nuevas_notas: Optional[str] = None
) -> bool:
    """
    Edita una cuenta financiera existente.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Obtener datos actuales
    cur.execute("SELECT name, balance FROM financial_accounts WHERE id = ?", (cuenta_id,))
    cuenta = cur.fetchone()
    if not cuenta:
        conn.close()
        return False

    # Construir query dinámica
    campos = []
    valores = []

    if nuevo_nombre is not None:
        # Verificar que el nuevo nombre no exista en otra cuenta
        cur.execute("SELECT id FROM financial_accounts WHERE name = ? AND id != ?", (nuevo_nombre, cuenta_id))
        if cur.fetchone():
            conn.close()
            raise ValueError(f"Ya existe otra cuenta con el nombre '{nuevo_nombre}'")
        campos.append("name = ?")
        valores.append(nuevo_nombre)

    if nuevo_tipo is not None:
        campos.append("type = ?")
        valores.append(nuevo_tipo)

    if nuevo_balance is not None:
        old_balance = cuenta['balance']
        campos.append("balance = ?")
        valores.append(nuevo_balance)

        # Registrar movimiento si cambió el balance
        if old_balance != nuevo_balance:
            tipo_mov = "deposit" if nuevo_balance > old_balance else "withdrawal"
            monto = abs(nuevo_balance - old_balance)
            desc = "Ajuste manual de saldo"

            cur.execute("""
                INSERT INTO account_movements (account_id, type, amount, old_balance, new_balance, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cuenta_id, tipo_mov, monto, old_balance, nuevo_balance, desc))

    if nueva_currency is not None:
        campos.append("currency = ?")
        valores.append(nueva_currency)

    if nuevos_tags is not None:
        campos.append("tags = ?")
        valores.append(nuevos_tags)

    if nuevas_notas is not None:
        campos.append("notes = ?")
        valores.append(nuevas_notas)

    # Agregar updated_at
    campos.append("updated_at = datetime('now')")

    if campos:
        valores.append(cuenta_id)
        query = f"UPDATE financial_accounts SET {', '.join(campos)} WHERE id = ?"
        cur.execute(query, valores)
        conn.commit()

    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_cuenta_financiera(cuenta_id: int) -> bool:
    """
    Marca una cuenta como inactiva (soft delete).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE financial_accounts
        SET is_active = 0, updated_at = datetime('now')
        WHERE id = ?
    """, (cuenta_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_cuentas_financieras_activas() -> list[dict[str, Any]]:
    """
    Lista todas las cuentas financieras activas.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, type, balance, currency, tags, notes, created_at, updated_at
        FROM financial_accounts
        WHERE is_active = 1
        ORDER BY
            CASE type
                WHEN 'banco' THEN 1
                WHEN 'wallet' THEN 2
                WHEN 'efectivo' THEN 3
                ELSE 4
            END, name
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def obtener_cuenta_financiera(cuenta_id: int) -> Optional[dict[str, Any]]:
    """
    Obtiene una cuenta financiera específica.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, type, balance, currency, tags, notes, created_at, updated_at
        FROM financial_accounts
        WHERE id = ? AND is_active = 1
    """, (cuenta_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def actualizar_balance_cuenta(cuenta_id: int, nuevo_balance: float, descripcion: str = "Ajuste manual") -> bool:
    """
    Actualiza el balance de una cuenta y registra el movimiento.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Obtener balance actual
    cur.execute("SELECT balance FROM financial_accounts WHERE id = ?", (cuenta_id,))
    result = cur.fetchone()
    if not result:
        conn.close()
        return False

    old_balance = result['balance']

    if old_balance == nuevo_balance:
        conn.close()
        return True  # No hay cambio

    # Determinar tipo de movimiento
    tipo_mov = "deposit" if nuevo_balance > old_balance else "withdrawal"
    monto = abs(nuevo_balance - old_balance)

    # Actualizar cuenta
    cur.execute("""
        UPDATE financial_accounts
        SET balance = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (nuevo_balance, cuenta_id))

    # Registrar movimiento
    cur.execute("""
        INSERT INTO account_movements (account_id, type, amount, old_balance, new_balance, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cuenta_id, tipo_mov, monto, old_balance, nuevo_balance, descripcion))

    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def agregar_movimiento_cuenta(
    cuenta_id: int,
    tipo: str,
    monto: float,
    descripcion: str,
    notas: Optional[str] = None
) -> bool:
    """
    Agrega un movimiento a una cuenta y actualiza su balance automáticamente.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Obtener balance actual
    cur.execute("SELECT balance FROM financial_accounts WHERE id = ?", (cuenta_id,))
    result = cur.fetchone()
    if not result:
        conn.close()
        return False

    old_balance = result['balance']

    # Calcular nuevo balance
    if tipo == "deposit":
        new_balance = old_balance + monto
    elif tipo == "withdrawal":
        new_balance = old_balance - monto
    else:  # adjustment
        new_balance = monto  # En adjustments, monto es el nuevo balance total

    # Actualizar cuenta
    cur.execute("""
        UPDATE financial_accounts
        SET balance = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (new_balance, cuenta_id))

    # Registrar movimiento
    cur.execute("""
        INSERT INTO account_movements (account_id, type, amount, old_balance, new_balance, description, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cuenta_id, tipo, monto, old_balance, new_balance, descripcion, notas))

    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def obtener_movimientos_cuenta(cuenta_id: int, limite: int = 50) -> list[dict[str, Any]]:
    """
    Obtiene los últimos movimientos de una cuenta.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type, amount, old_balance, new_balance, description, notes, created_at
        FROM account_movements
        WHERE account_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (cuenta_id, limite))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# 🔸 DEDUCCIONES / GASTOS PENDIENTES
def agregar_deduccion(
    descripcion: str,
    monto: float,
    cuenta_id: Optional[int] = None,
    fecha_limite: Optional[str] = None,
    notas: Optional[str] = None
) -> int:
    """
    Agrega una deducción pendiente (gasto, vuelto, etc.).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO financial_deductions (description, amount, account_id, due_date, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (descripcion, monto, cuenta_id, fecha_limite, notas))

    conn.commit()
    deduccion_id = cur.lastrowid
    conn.close()
    return deduccion_id

def marcar_deduccion_resuelta(deduccion_id: int) -> bool:
    """
    Marca una deducción como resuelta.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE financial_deductions
        SET status = 'resolved', resolved_at = datetime('now')
        WHERE id = ?
    """, (deduccion_id,))

    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def eliminar_deduccion(deduccion_id: int) -> bool:
    """
    Elimina físicamente una deducción.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM financial_deductions WHERE id = ?", (deduccion_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def listar_deducciones_pendientes() -> list[dict[str, Any]]:
    """
    Lista todas las deducciones pendientes.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.*,
            a.name as account_name
        FROM financial_deductions d
        LEFT JOIN financial_accounts a ON d.account_id = a.id
        WHERE d.status = 'pending'
        ORDER BY
            CASE WHEN d.due_date IS NULL THEN 1 ELSE 0 END,
            d.due_date,
            d.created_at
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def listar_todas_deducciones(limite: int = 100) -> list[dict[str, Any]]:
    """
    Lista todas las deducciones (pendientes y resueltas).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.*,
            a.name as account_name
        FROM financial_deductions d
        LEFT JOIN financial_accounts a ON d.account_id = a.id
        ORDER BY d.status, d.created_at DESC
        LIMIT ?
    """, (limite,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# 🔸 RESUMEN FINANCIERO
def obtener_resumen_financiero() -> dict[str, Any]:
    """
    Calcula el resumen financiero completo:
    - Subtotal (suma de todos los saldos)
    - Total deducciones pendientes
    - Total real
    - Desglose por tipo de cuenta
    """
    conn = get_connection()
    cur = conn.cursor()

    # Obtener suma de saldos de cuentas activas
    cur.execute("""
        SELECT
            COALESCE(SUM(balance), 0) as subtotal,
            COUNT(*) as total_cuentas
        FROM financial_accounts
        WHERE is_active = 1
    """)
    resultado = dict(cur.fetchone() or {})

    # Obtener suma de deducciones pendientes
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as total_deducciones
        FROM financial_deductions
        WHERE status = 'pending'
    """)
    deducciones = dict(cur.fetchone() or {})

    # Obtener desglose por tipo de cuenta
    cur.execute("""
        SELECT
            type,
            COUNT(*) as cantidad,
            COALESCE(SUM(balance), 0) as total
        FROM financial_accounts
        WHERE is_active = 1
        GROUP BY type
        ORDER BY total DESC
    """)
    desglose_tipos = [dict(r) for r in cur.fetchall()]

    conn.close()

    subtotal = resultado.get('subtotal', 0) or 0
    total_deducciones = deducciones.get('total_deducciones', 0) or 0
    total_real = subtotal - total_deducciones

    return {
        'subtotal': subtotal,
        'total_deducciones': total_deducciones,
        'total_real': total_real,
        'total_cuentas': resultado.get('total_cuentas', 0) or 0,
        'desglose_por_tipo': desglose_tipos,
        'cuentas_con_saldo': [t for t in desglose_tipos if t['total'] > 0]
    }

def obtener_saldos_por_tipo() -> dict[str, float]:
    """
    Obtiene los saldos agrupados por tipo de cuenta.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            type,
            COALESCE(SUM(balance), 0) as total
        FROM financial_accounts
        WHERE is_active = 1
        GROUP BY type
    """)

    resultados = {}
    for row in cur.fetchall():
        resultados[row['type']] = row['total']

    conn.close()
    return resultados

# 🔸 SNAPSHOTS / HITOS
def crear_snapshot_financiero(
    nombre: str,
    notas: Optional[str] = None
) -> int:
    """
    Crea un snapshot de la situación financiera actual.
    """
    # Obtener resumen actual
    resumen = obtener_resumen_financiero()

    # Obtener detalles de cuentas
    cuentas = listar_cuentas_financieras_activas()

    # Obtener deducciones pendientes
    deducciones = listar_deducciones_pendientes()

    # Crear datos del snapshot
    snapshot_data = {
        'resumen': resumen,
        'cuentas': cuentas,
        'deducciones': deducciones,
        'timestamp': datetime.now().isoformat()
    }

    # Convertir a JSON string
    import json
    data_str = json.dumps(snapshot_data, default=str, ensure_ascii=False)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO financial_snapshots (name, total_balance, subtotal, total_deductions, notes, snapshot_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nombre,
        resumen['total_real'],
        resumen['subtotal'],
        resumen['total_deducciones'],
        notas,
        data_str
    ))

    conn.commit()
    snapshot_id = cur.lastrowid
    conn.close()
    return snapshot_id

def listar_snapshots_financieros(limite: int = 20) -> list[dict[str, Any]]:
    """
    Lista todos los snapshots guardados.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, total_balance, subtotal, total_deductions, notes, created_at
        FROM financial_snapshots
        ORDER BY created_at DESC
        LIMIT ?
    """, (limite,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def obtener_snapshot_financiero(snapshot_id: int) -> Optional[dict[str, Any]]:
    """
    Obtiene un snapshot específico.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, total_balance, subtotal, total_deductions, notes, snapshot_data, created_at
        FROM financial_snapshots
        WHERE id = ?
    """, (snapshot_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    resultado = dict(row)

    # Parsear JSON si existe
    if resultado.get('snapshot_data'):
        import json
        try:
            resultado['data_parsed'] = json.loads(resultado['snapshot_data'])
        except:
            resultado['data_parsed'] = {}

    return resultado

def eliminar_snapshot_financiero(snapshot_id: int) -> bool:
    """
    Elimina un snapshot.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM financial_snapshots WHERE id = ?", (snapshot_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

# 🔸 FUNCIONES DE BÚSQUEDA Y FILTRO
def buscar_cuentas_por_nombre(busqueda: str) -> list[dict[str, Any]]:
    """
    Busca cuentas por nombre.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, type, balance, currency, tags, notes
        FROM financial_accounts
        WHERE is_active = 1 AND name LIKE ?
        ORDER BY name
    """, (f"%{busqueda}%",))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def filtrar_cuentas_por_tipo(tipo: str) -> list[dict[str, Any]]:
    """
    Filtra cuentas por tipo.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, type, balance, currency, tags, notes
        FROM financial_accounts
        WHERE is_active = 1 AND type = ?
        ORDER BY name
    """, (tipo,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def filtrar_cuentas_por_saldo(min_saldo: float = 0, max_saldo: Optional[float] = None) -> list[dict[str, Any]]:
    """
    Filtra cuentas por rango de saldo.
    """
    conn = get_connection()
    cur = conn.cursor()

    if max_saldo is not None:
        cur.execute("""
            SELECT id, name, type, balance, currency, tags, notes
            FROM financial_accounts
            WHERE is_active = 1 AND balance BETWEEN ? AND ?
            ORDER BY balance DESC
        """, (min_saldo, max_saldo))
    else:
        cur.execute("""
            SELECT id, name, type, balance, currency, tags, notes
            FROM financial_accounts
            WHERE is_active = 1 AND balance >= ?
            ORDER BY balance DESC
        """, (min_saldo,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ========================================
# 📊 FUNCIONES PARA HISTORIAL/DASHBOARD
# ========================================

def obtener_resumen_ganancias(fecha_inicio: str = None, fecha_fin: str = None) -> dict:
    """Obtiene resumen de ganancias en un rango de fechas"""
    conn = get_connection()
    cur = conn.cursor()

    where_clause = ""
    params = []

    if fecha_inicio and fecha_fin:
        where_clause = "WHERE date BETWEEN ? AND ?"
        params = [fecha_inicio, fecha_fin]
    elif fecha_inicio:
        where_clause = "WHERE date >= ?"
        params = [fecha_inicio]
    elif fecha_fin:
        where_clause = "WHERE date <= ?"
        params = [fecha_fin]

    # Obtener recargas en el periodo
    recargas_query = f"""
        SELECT
            COUNT(*) as total_recargas,
            COALESCE(SUM(amount_received_usd), 0) as total_recibido_usd,
            COALESCE(SUM(profit_usd), 0) as ganancia_recargas_usd,
            COALESCE(SUM(seller_commission_usd), 0) as comisiones_recargas_usd
        FROM recharges
        {where_clause}
    """
    cur.execute(recargas_query, params)
    recargas = dict(cur.fetchone() or {})

    # Obtener remesas en el periodo
    remesas_query = f"""
        SELECT
            COUNT(*) as total_remesas,
            COALESCE(SUM(amount_origin), 0) as total_origin,
            COALESCE(SUM(profit_net_usdt), 0) as ganancia_remesas_usdt,
            COALESCE(SUM(seller_commission_usdt), 0) as comisiones_remesas_usdt,
            COALESCE(SUM(amount_destiny_bs), 0) as total_destiny_bs
        FROM remittances
        {where_clause}
    """
    cur.execute(remesas_query, params)
    remesas = dict(cur.fetchone() or {})

    conn.close()

    # Calcular totales
    total_recargas = recargas.get('total_recargas', 0) or 0
    total_remesas = remesas.get('total_remesas', 0) or 0

    ganancia_recargas = recargas.get('ganancia_recargas_usd', 0) or 0
    ganancia_remesas = remesas.get('ganancia_remesas_usdt', 0) or 0

    comisiones_recargas = recargas.get('comisiones_recargas_usd', 0) or 0
    comisiones_remesas = remesas.get('comisiones_remesas_usdt', 0) or 0

    return {
        'recargas': recargas,
        'remesas': remesas,
        'total_transacciones': total_recargas + total_remesas,
        'total_recargas': total_recargas,
        'total_remesas': total_remesas,
        'ganancia_total_usd': ganancia_recargas,
        'ganancia_total_usdt': ganancia_remesas,
        'comisiones_total_usd': comisiones_recargas,
        'comisiones_total_usdt': comisiones_remesas,
        'ganancia_neta_dueño_usd': ganancia_recargas - comisiones_recargas,
        'ganancia_neta_dueño_usdt': ganancia_remesas - comisiones_remesas,
        'total_destiny_bs': remesas.get('total_destiny_bs', 0) or 0,
        'total_recibido_usd': recargas.get('total_recibido_usd', 0) or 0,
        'total_origin': remesas.get('total_origin', 0) or 0
    }

def obtener_comisiones_trabajador(worker_id: int, fecha_inicio: str = None, fecha_fin: str = None) -> dict:
    """Calcula comisiones de un trabajador en un periodo"""
    conn = get_connection()
    cur = conn.cursor()

    where_clause = "WHERE worker_id = ?"
    params = [worker_id]

    if fecha_inicio and fecha_fin:
        where_clause += " AND date BETWEEN ? AND ?"
        params.extend([fecha_inicio, fecha_fin])
    elif fecha_inicio:
        where_clause += " AND date >= ?"
        params.append(fecha_inicio)
    elif fecha_fin:
        where_clause += " AND date <= ?"
        params.append(fecha_fin)

    # Comisiones de recargas
    recargas_query = f"""
        SELECT
            COUNT(*) as recargas_count,
            COALESCE(SUM(amount_received_usd), 0) as total_recibido_usd,
            COALESCE(SUM(seller_commission_usd), 0) as comisiones_recargas_usd,
            COALESCE(SUM(profit_usd), 0) as ganancia_total_recargas_usd
        FROM recharges
        {where_clause}
    """
    cur.execute(recargas_query, params)
    recargas = dict(cur.fetchone() or {})

    # Comisiones de remesas
    remesas_query = f"""
        SELECT
            COUNT(*) as remesas_count,
            COALESCE(SUM(amount_origin), 0) as total_origin,
            COALESCE(SUM(seller_commission_usdt), 0) as comisiones_remesas_usdt,
            COALESCE(SUM(profit_net_usdt), 0) as ganancia_total_remesas_usdt
        FROM remittances
        {where_clause}
    """
    cur.execute(remesas_query, params)
    remesas = dict(cur.fetchone() or {})

    conn.close()

    # Obtener nombre del trabajador
    trabajadores = listar_trabajadores_activos()
    nombre_trabajador = next((w['name'] for w in trabajadores if w['id'] == worker_id), f"Trabajador #{worker_id}")

    return {
        'worker_id': worker_id,
        'worker_name': nombre_trabajador,
        'recargas': recargas,
        'remesas': remesas,
        'total_comisiones_usd': (recargas.get('comisiones_recargas_usd', 0) or 0),
        'total_comisiones_usdt': (remesas.get('comisiones_remesas_usdt', 0) or 0),
        'total_transacciones': (recargas.get('recargas_count', 0) or 0) + (remesas.get('remesas_count', 0) or 0),
        'total_recargas': recargas.get('recargas_count', 0) or 0,
        'total_remesas': remesas.get('remesas_count', 0) or 0,
        'total_venta_usd': (recargas.get('total_recibido_usd', 0) or 0),
        'total_venta_origen': (remesas.get('total_origin', 0) or 0),
        'ganancia_generada_usd': (recargas.get('ganancia_total_recargas_usd', 0) or 0),
        'ganancia_generada_usdt': (remesas.get('ganancia_total_remesas_usdt', 0) or 0)
    }

def obtener_transacciones_combinadas(fecha_inicio: str = None, fecha_fin: str = None,
                                    worker_id: Optional[int] = None,
                                    tipo: Optional[str] = None) -> list:
    """Obtiene TODAS las transacciones (recargas + remesas) filtradas"""
    conn = get_connection()
    cur = conn.cursor()

    transacciones = []

    # Construir WHERE clause para recargas
    where_recargas = []
    params_recargas = []

    if fecha_inicio and fecha_fin:
        where_recargas.append("r.date BETWEEN ? AND ?")
        params_recargas.extend([fecha_inicio, fecha_fin])

    if worker_id:
        where_recargas.append("r.worker_id = ?")
        params_recargas.append(worker_id)

    where_recargas_sql = " AND ".join(where_recargas) if where_recargas else "1=1"

    # Si tipo es específico y no es "RECARGA", saltar recargas
    if tipo not in ["REMESA", "remesa"]:
        recargas_query = f"""
            SELECT
                'RECARGA' as tipo,
                r.id,
                r.date,
                w.name as worker_name,
                c.name as country_name,
                g.name as game_name,
                p.name as product_name,
                pm.name as payment_method_name,
                r.amount_received_usd as monto,
                r.cost_usd as costo,
                r.seller_commission_usd as comision,
                r.profit_usd as ganancia,
                r.customer_name as cliente_nombre,  -- ✅ NUEVO: Incluir nombre del cliente
                NULL as currency_code,
                NULL as amount_origin,
                NULL as rate_origin_to_bs,
                NULL as amount_destiny_bs,
                NULL as usdt_received,
                NULL as usdt_spent,
                NULL as profit_gross_usdt,
                NULL as profit_net_usdt,
                NULL as sender_name,
                NULL as receiver_name,
                r.notes
            FROM recharges r
            LEFT JOIN workers w ON r.worker_id = w.id
            LEFT JOIN countries c ON r.country_id = c.id
            LEFT JOIN games g ON r.game_id = g.id
            LEFT JOIN products p ON r.product_id = p.id
            LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
            WHERE {where_recargas_sql}
            ORDER BY r.date DESC, r.id DESC
        """

        cur.execute(recargas_query, params_recargas)
        for row in cur.fetchall():
            transacciones.append(dict(row))

    # Construir WHERE clause para remesas
    where_remesas = []
    params_remesas = []

    if fecha_inicio and fecha_fin:
        where_remesas.append("r.date BETWEEN ? AND ?")
        params_remesas.extend([fecha_inicio, fecha_fin])

    if worker_id:
        where_remesas.append("r.worker_id = ?")
        params_remesas.append(worker_id)

    where_remesas_sql = " AND ".join(where_remesas) if where_remesas else "1=1"

    # Si tipo es específico y no es "REMESA", saltar remesas
    if tipo not in ["RECARGA", "recarga"]:
        remesas_query = f"""
            SELECT
                'REMESA' as tipo,
                r.id,
                r.date,
                w.name as worker_name,
                c.name as country_name,
                NULL as game_name,
                NULL as product_name,
                pm.name as payment_method_name,
                NULL as monto,
                NULL as costo,
                r.seller_commission_usdt as comision,
                NULL as ganancia,
                NULL as cliente_nombre,  -- ✅ Para mantener consistencia en columnas
                cu.code as currency_code,
                r.amount_origin,
                r.rate_origin_to_bs,
                r.amount_destiny_bs,
                r.usdt_received,
                r.usdt_spent,
                r.profit_gross_usdt,
                r.profit_net_usdt,
                r.sender_name,
                r.receiver_name,
                r.notes
            FROM remittances r
            LEFT JOIN workers w ON r.worker_id = w.id
            LEFT JOIN countries c ON r.country_id = c.id
            LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
            LEFT JOIN currencies cu ON r.currency_id = cu.id
            WHERE {where_remesas_sql}
            ORDER BY r.date DESC, r.id DESC
        """

        cur.execute(remesas_query, params_remesas)
        for row in cur.fetchall():
            transacciones.append(dict(row))

    conn.close()

    # Ordenar todas las transacciones por fecha
    transacciones.sort(key=lambda x: (x['date'], x['id']), reverse=True)

    return transacciones

def obtener_ganancias_por_dia(dias: int = 7) -> list:
    """Obtiene ganancias diarias de los últimos N días"""
    conn = get_connection()
    cur = conn.cursor()

    # Calcular fecha de inicio
    fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

    # Recargas por día
    recargas_query = """
        SELECT
            date,
            COALESCE(SUM(profit_usd), 0) as ganancia_usd,
            COALESCE(SUM(seller_commission_usd), 0) as comisiones_usd
        FROM recharges
        WHERE date >= ?
        GROUP BY date
        ORDER BY date
    """

    cur.execute(recargas_query, (fecha_inicio,))
    recargas_por_dia = {row['date']: dict(row) for row in cur.fetchall()}

    # Remesas por día
    remesas_query = """
        SELECT
            date,
            COALESCE(SUM(profit_net_usdt), 0) as ganancia_usdt,
            COALESCE(SUM(seller_commission_usdt), 0) as comisiones_usdt
        FROM remittances
        WHERE date >= ?
        GROUP BY date
        ORDER BY date
    """

    cur.execute(remesas_query, (fecha_inicio,))
    remesas_por_dia = {row['date']: dict(row) for row in cur.fetchall()}

    conn.close()

    # Combinar resultados
    resultados = []
    todas_fechas = set(list(recargas_por_dia.keys()) + list(remesas_por_dia.keys()))

    for fecha in sorted(todas_fechas):
        recarga = recargas_por_dia.get(fecha, {'ganancia_usd': 0, 'comisiones_usd': 0})
        remesa = remesas_por_dia.get(fecha, {'ganancia_usdt': 0, 'comisiones_usdt': 0})

        resultados.append({
            'fecha': fecha,
            'ganancia_recargas': recarga['ganancia_usd'],
            'comisiones_recargas': recarga['comisiones_usd'],
            'ganancia_remesas': remesa['ganancia_usdt'],
            'comisiones_remesas': remesa['comisiones_usdt'],
            'ganancia_total': recarga['ganancia_usd'] + remesa['ganancia_usdt'],
            'comisiones_total': recarga['comisiones_usd'] + remesa['comisiones_usdt'],
            'ganancia_neta': (recarga['ganancia_usd'] + remesa['ganancia_usdt']) -
                            (recarga['comisiones_usd'] + remesa['comisiones_usdt'])
        })

    return resultados

def obtener_top_trabajadores(limite: int = 5, fecha_inicio: str = None, fecha_fin: str = None) -> list:
    """Obtiene los trabajadores más productivos"""
    conn = get_connection()
    cur = conn.cursor()

    where_clause = ""
    params = []

    if fecha_inicio and fecha_fin:
        where_clause = "WHERE date BETWEEN ? AND ?"
        params = [fecha_inicio, fecha_fin]

    # Recargas por trabajador
    recargas_query = f"""
        SELECT
            w.id,
            w.name,
            COUNT(r.id) as total_recargas,
            COALESCE(SUM(r.amount_received_usd), 0) as venta_recargas_usd,
            COALESCE(SUM(r.profit_usd), 0) as ganancia_recargas_usd,
            COALESCE(SUM(r.seller_commission_usd), 0) as comisiones_recargas_usd
        FROM workers w
        LEFT JOIN recharges r ON w.id = r.worker_id {where_clause}
        GROUP BY w.id, w.name
    """

    cur.execute(recargas_query, params)
    recargas_trabajadores = {row['id']: dict(row) for row in cur.fetchall()}

    # Remesas por trabajador
    remesas_query = f"""
        SELECT
            w.id,
            w.name,
            COUNT(rm.id) as total_remesas,
            COALESCE(SUM(rm.amount_origin), 0) as venta_remesas_origen,
            COALESCE(SUM(rm.profit_net_usdt), 0) as ganancia_remesas_usdt,
            COALESCE(SUM(rm.seller_commission_usdt), 0) as comisiones_remesas_usdt
        FROM workers w
        LEFT JOIN remittances rm ON w.id = rm.worker_id {where_clause}
        GROUP BY w.id, w.name
    """

    cur.execute(remesas_query, params)
    remesas_trabajadores = {row['id']: dict(row) for row in cur.fetchall()}

    conn.close()

    # Combinar resultados
    resultados = []
    todos_ids = set(list(recargas_trabajadores.keys()) + list(remesas_trabajadores.keys()))

    for worker_id in todos_ids:
        rec = recargas_trabajadores.get(worker_id, {'name': '', 'total_recargas': 0, 'venta_recargas_usd': 0,
                                                    'ganancia_recargas_usd': 0, 'comisiones_recargas_usd': 0})
        rem = remesas_trabajadores.get(worker_id, {'name': '', 'total_remesas': 0, 'venta_remesas_origen': 0,
                                                  'ganancia_remesas_usdt': 0, 'comisiones_remesas_usdt': 0})

        nombre = rec['name'] or rem['name']
        if not nombre:
            continue

        total_transacciones = (rec['total_recargas'] or 0) + (rem['total_remesas'] or 0)
        ganancia_total = (rec['ganancia_recargas_usd'] or 0) + (rem['ganancia_remesas_usdt'] or 0)
        comisiones_total = (rec['comisiones_recargas_usd'] or 0) + (rem['comisiones_remesas_usdt'] or 0)

        resultados.append({
            'id': worker_id,
            'nombre': nombre,
            'total_transacciones': total_transacciones,
            'total_recargas': rec['total_recargas'] or 0,
            'total_remesas': rem['total_remesas'] or 0,
            'venta_recargas_usd': rec['venta_recargas_usd'] or 0,
            'venta_remesas_origen': rem['venta_remesas_origen'] or 0,
            'ganancia_generada': ganancia_total,
            'comisiones_ganadas': comisiones_total,
            'ganancia_neta_para_dueño': ganancia_total - comisiones_total
        })

    # Ordenar por ganancia generada (descendente)
    resultados.sort(key=lambda x: x['ganancia_generada'], reverse=True)

    return resultados[:limite]

def obtener_resumen_mensual(mes: int, año: int) -> dict:
    """Obtiene resumen de un mes específico"""
    fecha_inicio = f"{año}-{mes:02d}-01"

    # Calcular último día del mes
    if mes == 12:
        fecha_fin = f"{año}-12-31"
    else:
        fecha_fin = f"{año}-{(mes+1):02d}-01"
        # Restar un día para obtener el último día del mes
        from datetime import datetime, timedelta
        fecha_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        fecha_obj = fecha_obj - timedelta(days=1)
        fecha_fin = fecha_obj.strftime("%Y-%m-%d")

    return obtener_resumen_ganancias(fecha_inicio, fecha_fin)