"""
utils/styles.py - [translate:ESTILOS TECNOLÓGICOS TRYHARDS]
"""
import tkinter as tk
from tkinter import ttk

# COLORES CYBERPUNK/TECH TRYHARDS
TECH_COLORS = {
    "bg_primary": "#0a0e17",      # Negro espacial
    "bg_secondary": "#1a1f2e",     # Gris carbón tech
    "bg_card": "#242b3a",          # Azul carbón metálico
    "primary": "#00d4ff",          # Cian neón BRILLANTE
    "success": "#00ff88",          # Verde gaming NEÓN
    "warning": "#ffaa00",          # Naranja cyberpunk
    "danger": "#ff4757",           # Rojo neón
    "text_light": "#e0e6ed",       # Blanco plateado
    "text_dark": "#a4b0be",        # Gris legible
    "accent": "#6c5ce7",           # Púrpura tech
    "gradient_start": "#667eea",   # Gradiente inicio
    "gradient_end": "#764ba2",     # Gradiente fin
    "table_bg": "#1e2430",         # Fondo tabla oscuro
    "table_fg": "#ffffff",         # Texto tabla blanco
    "table_odd": "#2a3140",        # Fila impar tabla
    "table_even": "#222836",       # Fila par tabla
    "table_header": "#00d4ff",     # Encabezado tabla
}

class AppStyles:
    def __init__(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()

    def _configure_styles(self):
        # BOTONES NEÓN
        self.style.configure('Primary.TButton',
            background=TECH_COLORS["primary"], foreground='black',
            font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=[20, 12])
        self.style.map('Primary.TButton', background=[('active', '#00b8e6')])

        self.style.configure('Success.TButton',
            background=TECH_COLORS["success"], foreground='black',
            font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=[20, 12])

        self.style.configure('Danger.TButton',
            background=TECH_COLORS["danger"], foreground='white',
            font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=[20, 12])

        # TARJETAS MODERNAS
        self.style.configure('Card.TFrame',
            background=TECH_COLORS["bg_card"], relief='solid',
            borderwidth=1, bordercolor='#374151')

        # ENTRADAS DE TEXTO
        self.style.configure('TEntry',
            fieldbackground=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"],
            insertcolor=TECH_COLORS["primary"]
        )

        self.style.configure('TCombobox',
            fieldbackground=TECH_COLORS["bg_card"],
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"]
        )

        # TABLAS PROFESIONALES (ESTILOS OSCUROS)
        self.style.configure('Custom.Treeview',
            background=TECH_COLORS["table_odd"],
            foreground=TECH_COLORS["table_fg"],
            fieldbackground=TECH_COLORS["table_odd"],
            rowheight=28,
            font=('Segoe UI', 11),
            borderwidth=0
        )

        self.style.configure('Custom.Treeview.Heading',
            background=TECH_COLORS["table_header"],
            foreground='white',
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            borderwidth=0
        )

        self.style.map('Custom.Treeview.Heading',
            background=[('active', TECH_COLORS["primary"])]
        )

        # SEPARADORES
        self.style.configure('TSeparator',
            background='#374151'
        )

        # LABEL FRAMES
        self.style.configure('TLabelframe',
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"]
        )

        self.style.configure('TLabelframe.Label',
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["primary"],
            font=('Segoe UI', 12, 'bold')
        )

        # SCROLLBARS
        self.style.configure('Vertical.TScrollbar',
            background=TECH_COLORS["bg_secondary"],
            troughcolor=TECH_COLORS["bg_card"],
            arrowcolor=TECH_COLORS["primary"]
        )

def apply_styles(root):
    """Aplica estilos + retorna colores"""
    styles = AppStyles()
    root.configure(bg=TECH_COLORS["bg_primary"])

    # Configurar colores para tkinter widgets básicos
    root.option_add('*background', TECH_COLORS["bg_primary"])
    root.option_add('*foreground', TECH_COLORS["text_light"])
    root.option_add('*Entry.background', TECH_COLORS["bg_card"])
    root.option_add('*Entry.foreground', TECH_COLORS["text_light"])
    root.option_add('*Entry.insertBackground', TECH_COLORS["primary"])
    root.option_add('*Text.background', TECH_COLORS["bg_card"])
    root.option_add('*Text.foreground', TECH_COLORS["text_light"])
    root.option_add('*Listbox.background', TECH_COLORS["bg_card"])
    root.option_add('*Listbox.foreground', TECH_COLORS["text_light"])

    return styles.style, TECH_COLORS