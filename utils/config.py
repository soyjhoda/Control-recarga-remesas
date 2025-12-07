"""
utils/config.py - [translate:CONFIGURACIONES + LOGO TRYHARDS]
"""
import os
import sys

# ========================================
# 📍 RUTAS DE ARCHIVOS - FUNCIONA EN .EXE Y DESARROLLO
# ========================================
def get_base_path():
    """Obtiene la ruta base donde está el ejecutable o el script"""
    if getattr(sys, 'frozen', False):
        # Si estamos en un .exe
        return os.path.dirname(sys.executable)
    else:
        # Si estamos en desarrollo
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_path()
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

# ========================================
# 🔍 DEBUG: Verificar rutas (solo en modo debug)
# ========================================
if SETTINGS["debug"]:
    print(f"🔧 DEBUG CONFIG:")
    print(f"   BASE_DIR: {BASE_DIR}")
    print(f"   DB_PATH: {DB_PATH}")
    print(f"   Existe data/: {os.path.exists(DATA_DIR)}")
    print(f"   Existe app.db: {os.path.exists(DB_PATH)}")