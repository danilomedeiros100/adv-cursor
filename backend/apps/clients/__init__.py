"""
Clientes - Módulo de gestão de clientes
"""

from .routes import router
from .schemas import *
from .services import *

__all__ = ["router"]
