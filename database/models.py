"""
database/models.py - [translate:PUENTE A OPERATIONS - COMPATIBILIDAD]
│
│ Propósito:
│ • Mantener compatibilidad con código antiguo que importe get_connection o init_db
│ • Delegar TODA la lógica real a database.operations
│ • Evitar tener dos definiciones distintas de tablas o conexión
"""

from database.operations import (
    get_connection,
    inicializar_base_de_datos,
)

# Alias para compatibilidad con nombre antiguo
def init_db():
    """
    Inicializa la base de datos.

    Alias fino a inicializar_base_de_datos() para que
    cualquier código viejo que llame init_db siga funcionando.
    """
    inicializar_base_de_datos()
