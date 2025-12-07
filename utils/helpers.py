"""
utils/helpers.py - [translate:CÁLCULOS FINANCIEROS Y UTILIDADES]
│
│ Propósito:
│ • calc_profit_from_exchange() → Convierte USD/USDT → Bs + calcula GANANCIA
│ • split_profit_for_roles() → Divide ganancia: 60% dueño, 40% trabajador
│ • format_currency() → Formatea Bs. 1.234,56
│ • validate_amount() → Valida montos > 0
│ • get_today_string() → Fecha actual YYYY-MM-DD
"""

from typing import Tuple
from datetime import datetime
from utils.config import EXCHANGE_RATES

# ========================================
# 💰 CÁLCULO DE GANANCIAS AUTOMÁTICO
# ========================================
def calc_profit_from_exchange(
    amount_foreign: float,
    rate_to_usd: float,
    rate_usd_to_ves: float,
    cost_ves_real: float
) -> Tuple[float, float, float]:
    """
    BLOQUE 1: Convierte MONEDA extranjera → USD → VES + calcula GANANCIA

    Fórmula:
    amount_usd = amount_foreign * rate_to_usd
    amount_ves = amount_usd * rate_usd_to_ves
    profit_ves = amount_ves - cost_ves_real

    Ejemplo:
    $100 USDT * 0.99 = $99 USD * 40 Bs/USD = Bs.3.960
    Costo real Bs.3.800 → GANANCIA Bs.160
    """
    amount_usd = amount_foreign * rate_to_usd
    amount_ves = amount_usd * rate_usd_to_ves
    profit_ves = amount_ves - cost_ves_real

    return amount_usd, amount_ves, profit_ves

# ========================================
# 👥 DIVISIÓN DE UTILIDADES (60/40)
# ========================================
def split_profit_for_roles(profit_ves: float) -> Tuple[float, float]:
    """
    BLOQUE 2: Divide ganancia automáticamente
    60% Dueño (owner_share_ves)
    40% Trabajador (worker_share_ves)

    Ejemplo: Ganancia Bs.160 → Dueño Bs.96, Trabajador Bs.64
    """
    owner_share = profit_ves * 0.60
    worker_share = profit_ves * 0.40
    return owner_share, worker_share

# ========================================
# 💳 FORMATEO DE MONEDAS
# ========================================
def format_currency(amount: float, currency: str = "VES") -> str:
    """
    BLOQUE 3: Formatea números → Bs. 1.234,56

    Args:
        amount: 1234.5
        currency: "VES" → "Bs.", "USD" → "$"

    Retorna: "Bs. 1.234,56"
    """
    if currency == "VES":
        symbol = "Bs. "
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        symbol = "$ "
        formatted = f"{amount:,.2f}"

    return f"{symbol}{formatted}"

# ========================================
# ✅ VALIDACIONES
# ========================================
def validate_amount(amount: float) -> bool:
    """BLOQUE 4: Monto > 0 y razonable (máx Bs.1.000.000)"""
    return amount > 0 and amount < 1_000_000

def validate_date(date_str: str) -> bool:
    """BLOQUE 5: Formato YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False

# ========================================
# 📅 FUNCIONES DE FECHA
# ========================================
def get_today_string() -> str:
    """
    BLOQUE 6: Retorna la fecha actual en formato YYYY-MM-DD

    Ejemplo: "2025-12-07"
    """
    return datetime.now().strftime("%Y-%m-%d")

def get_current_datetime() -> str:
    """
    BLOQUE 7: Retorna fecha y hora actual en formato YYYY-MM-DD HH:MM:SS

    Ejemplo: "2025-12-07 15:30:45"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")