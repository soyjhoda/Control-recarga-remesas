"""
utils/config.py - [translate:CONFIGURACIONES + LOGO TRYHARDS]
"""
import os

# ========================================
# 📍 RUTAS DE ARCHIVOS
# ========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
ICONS_DIR = os.path.join(BASE_DIR, "icons")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# ========================================
# 🖼️ LOGO TRYHARDS
# ========================================
LOGO_PATH = os.path.join(ICONS_DIR, "logohome.png")

# ========================================
# 🎨 COLORES ORIGINALES (mantener compatibilidad)
# ========================================
COLORS = {
    "primary": "#2E86C1", "success": "#00B894", "danger": "#E17055",
    "warning": "#FDCB6E", "dark": "#2D3436", "light": "#F8F9FA",
    "white": "#FFFFFF", "background": "#F1F2F6"
}

# ========================================
# ⚙️ CONFIGURACIONES
# ========================================
SETTINGS = {
    "debug": True, "default_currency": "USD", "default_date_format": "%Y-%m-%d",
    "max_recent_days": 30, "auto_backup_days": 7
}

EXCHANGE_RATES = {"USD_to_VES": 40.0, "USDT_to_USD": 0.99}
