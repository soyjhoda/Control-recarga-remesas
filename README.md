# 📊 Control Recargas & Remesas - App de Escritorio

## 🎯 Propósito

App profesional para **control total** de recargas digitales, juegos y remesas internacionales. Registra operaciones, calcula ganancias automáticas (USD/USDT → Bolívares), divide utilidades por trabajador, historial filtrable y reportes diarios.

## 📁 Estructura de Carpetas y Archivos

ControlRecargasRemesas/
│
├── 📁 data/ # 📄 Datos exportados (CSV, backups automáticos)
├── 📁 icons/ # 🖼️ Iconos de la app (agregaremos PNGs después)
│
├── 📁 utils/ # ⚙️ Funciones reutilizables y configuraciones
│ ├── init.py # 🔗 Hace que sea un módulo Python
│ ├── helpers.py # 📅 Fechas, validaciones, cálculos matemáticos
│ └── config.py # 🎨 Colores, rutas, configuraciones de la app
│
├── 📁 database/ # 🗄️ Base de datos SQLite (local en tu PC)
│ ├── init.py # 🔗 Módulo Python
│ ├── models.py # 📋 Estructura tablas: Recargas, Remesas, Usuarios, Países
│ └── operations.py # 🔄 CRUD completo (Crear, Leer, Actualizar, Eliminar)
│
├── 📁 gui/ # 🖥️ Interfaz gráfica con pestañas
│ ├── init.py # 🔗 Módulo Python
│ ├── main_window.py # 🏠 Ventana principal + pestañas (Dashboard/Recargas/Remesas/Historial)
│ ├── recargas_tab.py # 💳 Formulario + tabla para recargas de juegos/digitales
│ ├── remesas_tab.py # 🌎 Formulario + tabla para remesas (país, tasa, USDT→Bs)
│ ├── historial_tab.py # 📊 Historial filtrable (día/usuario/país/tipo)
│ └── dashboard_tab.py # 📈 Resumen ganancias diarias + gráficos simples
│
├── 📁 reports/ # 📤 Exportaciones y reportes
│ ├── init.py # 🔗 Módulo Python
│ └── generator.py # 📊 CSV, Excel, PDF + gráficos de ganancias
│
├── main.py # 🚀 Archivo PRINCIPAL (une toda la app)
├── run.bat # ⚡ Doble clic para EJECUTAR la app
├── requirements.txt # 📦 Librerías Python necesarias
└── README.md # 📖 ¡ESTE ARCHIVO! Documentación completa

## 🛠️ Cómo Funciona Cada Módulo

| Módulo      | Responsabilidad        | Ejemplo de uso                                         |
| ----------- | ---------------------- | ------------------------------------------------------ |
| `utils/`    | Funciones comunes      | Calcular ganancia, validar montos                      |
| `database/` | Guarda/registra TODO   | `agregar_recarga(trabajador="Juan", pais="Venezuela")` |
| `gui/`      | Lo que VES en pantalla | Botones grandes, tablas claras, pestañas               |
| `reports/`  | Exporta datos          | "Generar reporte diario → Excel"                       |

## 🚀 Para Ejecutar

1. Doble clic en `run.bat`
2. ¡La app se abre! Sin instalar nada extra.

## 🔧 Mantenimiento Fácil

-   **Error en recargas?** Solo mira `gui/recargas_tab.py`
-   **Agregar país nuevo?** Edita `database/models.py`
-   **Cambiar colores?** `utils/config.py`

**Creado con ♥️ por [JhodaStudios] + perplexity - 2025**
