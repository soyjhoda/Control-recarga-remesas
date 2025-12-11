"""
utils/styles.py - [translate:ESTILOS TECNOLÓGICOS TRYHARDS]
"""
import tkinter as tk
from tkinter import ttk

# COLORES CYBERPUNK/TECH TRYHARDS - MEJORADO CONTRASTE
TECH_COLORS = {
    "bg_primary": "#0a0e17",      # Negro espacial
    "bg_secondary": "#1a1f2e",     # Gris carbón tech
    "bg_card": "#242b3a",          # Azul carbón metálico
    "primary": "#00d4ff",          # Cian neón BRILLANTE
    "success": "#00ff88",          # Verde gaming NEÓN
    "warning": "#ffaa00",          # Naranja cyberpunk
    "danger": "#ff4757",           # Rojo neón
    "text_light": "#ffffff",       # BLANCO PURO (mejor contraste)
    "text_dark": "#cbd5e1",        # Gris más claro para mejor legibilidad
    "text_muted": "#94a3b8",       # Gris para texto secundario
    "accent": "#6c5ce7",           # Púrpura tech
    "gradient_start": "#667eea",   # Gradiente inicio
    "gradient_end": "#764ba2",     # Gradiente fin
    "table_bg": "#1e2430",         # Fondo tabla oscuro
    "table_fg": "#ffffff",         # Texto tabla blanco (máximo contraste)
    "table_odd": "#2a3140",        # Fila impar tabla
    "table_even": "#222836",       # Fila par tabla
    "table_header": "#00d4ff",     # Encabezado tabla
    "table_header_text": "#000000", # Texto negro en encabezado (máximo contraste)
}

class AppStyles:
    def __init__(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()

    def _configure_styles(self):
        # BOTONES NEÓN - MEJOR CONTRASTE
        self.style.configure('Primary.TButton',
            background=TECH_COLORS["primary"],
            foreground='black',  # Texto negro sobre cian (alto contraste)
            font=('Segoe UI', 12, 'bold'),
            borderwidth=0,
            padding=[20, 12]
        )
        self.style.map('Primary.TButton',
            background=[('active', '#00b8e6')],
            foreground=[('active', 'black')]
        )

        self.style.configure('Success.TButton',
            background=TECH_COLORS["success"],
            foreground='black',  # Texto negro sobre verde (alto contraste)
            font=('Segoe UI', 12, 'bold'),
            borderwidth=0,
            padding=[20, 12]
        )
        self.style.map('Success.TButton',
            background=[('active', '#00e677')],
            foreground=[('active', 'black')]
        )

        self.style.configure('Danger.TButton',
            background=TECH_COLORS["danger"],
            foreground='white',  # Texto blanco sobre rojo (alto contraste)
            font=('Segoe UI', 12, 'bold'),
            borderwidth=0,
            padding=[20, 12]
        )
        self.style.map('Danger.TButton',
            background=[('active', '#ff3346')],
            foreground=[('active', 'white')]
        )

        # BOTÓN SECUNDARIO (para acciones como "Limpiar", "Editar")
        self.style.configure('Secondary.TButton',
            background=TECH_COLORS["bg_secondary"],
            foreground=TECH_COLORS["text_light"],  # Blanco sobre gris oscuro
            font=('Segoe UI', 11, 'bold'),
            borderwidth=1,
            bordercolor=TECH_COLORS["primary"],
            padding=[15, 8]
        )
        self.style.map('Secondary.TButton',
            background=[('active', TECH_COLORS["bg_card"])],
            foreground=[('active', TECH_COLORS["primary"])]
        )

        # TARJETAS MODERNAS
        self.style.configure('Card.TFrame',
            background=TECH_COLORS["bg_card"],
            relief='solid',
            borderwidth=1,
            bordercolor='#374151'
        )

        # ENTRADAS DE TEXTO - MEJORADO CONTRASTE
        self.style.configure('TEntry',
            fieldbackground=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"],  # Blanco sobre fondo oscuro
            insertcolor=TECH_COLORS["primary"],
            borderwidth=2,
            relief='solid',
            padding=[8, 6]
        )
        self.style.map('TEntry',
            fieldbackground=[('focus', TECH_COLORS["bg_secondary"])],
            bordercolor=[('focus', TECH_COLORS["primary"])]
        )

        self.style.configure('TCombobox',
            fieldbackground=TECH_COLORS["bg_card"],
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"],  # Blanco sobre fondo oscuro
            selectbackground=TECH_COLORS["primary"],
            selectforeground='black'
        )

        # TABLAS PROFESIONALES (ESTILOS OSCUROS) - MEJOR CONTRASTE
        self.style.configure('Custom.Treeview',
            background=TECH_COLORS["table_odd"],
            foreground=TECH_COLORS["table_fg"],  # Blanco puro para máximo contraste
            fieldbackground=TECH_COLORS["table_odd"],
            rowheight=32,  # Un poco más alto para mejor lectura
            font=('Segoe UI', 11),
            borderwidth=0
        )

        # Filas alternas para mejor legibilidad
        self.style.map('Custom.Treeview',
            background=[('selected', TECH_COLORS["primary"])],
            foreground=[('selected', 'black')]
        )

        # ENCABEZADO DE TABLA - MEJOR CONTRASTE
        self.style.configure('Custom.Treeview.Heading',
            background=TECH_COLORS["table_header"],
            foreground=TECH_COLORS["table_header_text"],  # TEXTO NEGRO sobre cian
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            borderwidth=0,
            padding=[10, 5]
        )

        self.style.map('Custom.Treeview.Heading',
            background=[('active', TECH_COLORS["primary"])],
            foreground=[('active', 'black')]
        )

        # SEPARADORES
        self.style.configure('TSeparator',
            background=TECH_COLORS["primary"],  # Más visible
            relief='raised'
        )

        # LABEL FRAMES - MEJOR CONTRASTE
        self.style.configure('TLabelframe',
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["text_light"],  # Blanco sobre fondo oscuro
            relief='solid',
            borderwidth=1
        )

        self.style.configure('TLabelframe.Label',
            background=TECH_COLORS["bg_card"],
            foreground=TECH_COLORS["primary"],  # Cian neón para títulos
            font=('Segoe UI', 13, 'bold')
        )

        # SCROLLBARS
        self.style.configure('Vertical.TScrollbar',
            background=TECH_COLORS["bg_secondary"],
            troughcolor=TECH_COLORS["bg_card"],
            arrowcolor=TECH_COLORS["primary"],
            bordercolor=TECH_COLORS["primary"]
        )

        # LABELS - MEJOR CONTRASTE GENERAL
        self.style.configure('Title.TLabel',
            background=TECH_COLORS["bg_primary"],
            foreground=TECH_COLORS["primary"],  # Cian neón para títulos
            font=('Segoe UI', 16, 'bold')
        )

        self.style.configure('Subtitle.TLabel',
            background=TECH_COLORS["bg_primary"],
            foreground=TECH_COLORS["text_light"],  # Blanco para subtítulos
            font=('Segoe UI', 14, 'bold')
        )

        self.style.configure('Normal.TLabel',
            background=TECH_COLORS["bg_primary"],
            foreground=TECH_COLORS["text_dark"],  # Gris claro legible
            font=('Segoe UI', 11)
        )

        # CHECKBUTTONS Y RADIOBUTTONS
        self.style.configure('TCheckbutton',
            background=TECH_COLORS["bg_primary"],
            foreground=TECH_COLORS["text_light"],
            indicatorcolor=TECH_COLORS["bg_card"],
            indicatordiameter=15
        )

        self.style.map('TCheckbutton',
            background=[('active', TECH_COLORS["bg_primary"])],
            indicatorcolor=[('selected', TECH_COLORS["primary"])]
        )

def apply_styles(root):
    """Aplica estilos + retorna colores"""
    styles = AppStyles()
    root.configure(bg=TECH_COLORS["bg_primary"])

    # Configurar colores para tkinter widgets básicos
    root.option_add('*background', TECH_COLORS["bg_primary"])
    root.option_add('*foreground', TECH_COLORS["text_light"])  # Blanco por defecto
    root.option_add('*Entry.background', TECH_COLORS["bg_card"])
    root.option_add('*Entry.foreground', TECH_COLORS["text_light"])  # Blanco en entries
    root.option_add('*Entry.insertBackground', TECH_COLORS["primary"])
    root.option_add('*Entry.borderWidth', 2)
    root.option_add('*Text.background', TECH_COLORS["bg_card"])
    root.option_add('*Text.foreground', TECH_COLORS["text_light"])  # Blanco en text
    root.option_add('*Text.selectBackground', TECH_COLORS["primary"])
    root.option_add('*Text.selectForeground', 'black')
    root.option_add('*Listbox.background', TECH_COLORS["bg_card"])
    root.option_add('*Listbox.foreground', TECH_COLORS["text_light"])  # Blanco en listbox
    root.option_add('*Listbox.selectBackground', TECH_COLORS["primary"])
    root.option_add('*Listbox.selectForeground', 'black')
    root.option_add('*Button.background', TECH_COLORS["bg_secondary"])
    root.option_add('*Button.foreground', TECH_COLORS["text_light"])  # Blanco en botones genéricos
    root.option_add('*Button.activeBackground', TECH_COLORS["bg_card"])
    root.option_add('*Button.activeForeground', TECH_COLORS["primary"])
    root.option_add('*Label.background', TECH_COLORS["bg_primary"])
    root.option_add('*Label.foreground', TECH_COLORS["text_dark"])  # Gris claro para labels
    root.option_add('*Checkbutton.background', TECH_COLORS["bg_primary"])
    root.option_add('*Checkbutton.foreground', TECH_COLORS["text_light"])
    root.option_add('*Radiobutton.background', TECH_COLORS["bg_primary"])
    root.option_add('*Radiobutton.foreground', TECH_COLORS["text_light"])
    root.option_add('*font', ('Segoe UI', 11))

    return styles.style, TECH_COLORS