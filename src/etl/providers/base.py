"""
Base Data Provider - Interfaz abstracta para todos los proveedores de datos.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional


class DataProvider(ABC):
    """
    Interfaz abstracta para proveedores de datos financieros.

    Cada provider debe implementar el método fetch() que retorna
    una lista de registros OHLCV.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del proveedor para logging."""
        pass

    @abstractmethod
    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Descarga datos históricos para un símbolo.

        Args:
            symbol: Símbolo del activo (ej: "ECOPETROL", "VOO")
            start_date: Fecha de inicio del historial
            end_date: Fecha de fin del historial

        Returns:
            Lista de registros OHLCV con campos:
            - date: str (YYYY-MM-DD)
            - symbol: str
            - open: float or None
            - high: float or None
            - low: float or None
            - close: float or None
            - volume: int or None

            Retorna lista vacía si no hay datos disponibles.
        """
        pass

    def is_available(self) -> bool:
        """
        Verifica si el proveedor está disponible.

        Returns:
            True si el provider puede ser usado, False otherwise
        """
        return True

    def close(self) -> None:
        """Cierra recursos si es necesario. Override en subclasses."""
        pass