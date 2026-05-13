"""
Capa de acceso a datos — separada de gateway.py para evitar imports circulares.

Proporciona get_records() con caché en memoria usada por todas las rutas API.
"""

import os
from typing import List, Dict, Optional
from src.etl.unifier import DataUnifier
from src.sorting.comparator import SortingComparator
from src.services.volume_analyzer import VolumeAnalyzer

DATA_FILE: str = "data/processed/unified_data.csv"
unifier: DataUnifier = DataUnifier()
comparator: SortingComparator = SortingComparator()
volume_analyzer: VolumeAnalyzer = VolumeAnalyzer()

_records_cache: Optional[List[Dict]] = None


def get_records() -> List[Dict]:
    """Carga y cachea los registros unificados desde CSV. O(n)."""
    global _records_cache
    if _records_cache is None:
        if os.path.exists(DATA_FILE):
            _records_cache = unifier.load_from_csv(DATA_FILE)
        else:
            _records_cache = []
    return _records_cache


def invalidate_cache() -> None:
    """Invalida la caché forzando recarga en la próxima llamada. O(1)."""
    global _records_cache
    _records_cache = None
