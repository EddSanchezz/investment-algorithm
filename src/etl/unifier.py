"""
Unifier Module - Unificación de datasets financieros.
Este módulo implementa la capa de carga del proceso ETL.
Combina datos de múltiples fuentes manteniendo integridad temporal.
Incluye alineación de calendarios bursátiles y manejo de desalineaciones.
"""

from typing import List, Dict, Set
from datetime import datetime, timedelta
import csv
import os


COLOMBIAN_HOLIDAYS: Set[str] = set()
NYSE_HOLIDAYS: Set[str] = set()


def _load_colombian_holidays() -> Set[str]:
    """Carga festivos colombianos fijos para 2018-2027 con caché."""
    if COLOMBIAN_HOLIDAYS:
        return COLOMBIAN_HOLIDAYS
    holidays = set()
    for year in range(2018, 2028):
        holidays.update(_colombian_fixed_holidays(year))
    return holidays


def _colombian_fixed_holidays(year: int) -> List[str]:
    """Genera lista de 17 festivos colombianos fijos para un año dado."""
    h = []
    h.append(f"{year}-01-01")
    h.append(f"{year}-01-06")
    h.append(f"{year}-03-19")
    h.append(f"{year}-05-01")
    h.append(f"{year}-05-19")
    h.append(f"{year}-06-02")
    h.append(f"{year}-06-09")
    h.append(f"{year}-06-23")
    h.append(f"{year}-06-30")
    h.append(f"{year}-07-20")
    h.append(f"{year}-08-07")
    h.append(f"{year}-08-18")
    h.append(f"{year}-10-13")
    h.append(f"{year}-11-03")
    h.append(f"{year}-11-17")
    h.append(f"{year}-12-08")
    h.append(f"{year}-12-25")
    return h


def _load_nyse_holidays() -> Set[str]:
    """Carga festivos NYSE fijos para 2018-2027 con caché."""
    if NYSE_HOLIDAYS:
        return NYSE_HOLIDAYS
    holidays = set()
    for year in range(2018, 2028):
        holidays.add(f"{year}-01-01")
        holidays.add(f"{year}-01-15")
        holidays.add(f"{year}-02-19")
        holidays.add(f"{year}-03-29")
        holidays.add(f"{year}-05-27")
        holidays.add(f"{year}-06-19")
        holidays.add(f"{year}-07-04")
        holidays.add(f"{year}-09-02")
        holidays.add(f"{year}-11-28")
        holidays.add(f"{year}-12-25")
    return holidays


def _is_weekend(date_str: str) -> bool:
    """Verifica si una fecha cae en sábado o domingo."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() >= 5


def _is_bvc_trading_day(date_str: str) -> bool:
    """Verifica si una fecha es día hábil en la BVC (Colombia)."""
    if _is_weekend(date_str):
        return False
    holidays = _load_colombian_holidays()
    return date_str not in holidays


def _is_nyse_trading_day(date_str: str) -> bool:
    """Verifica si una fecha es día hábil en la NYSE (EE.UU.)."""
    if _is_weekend(date_str):
        return False
    holidays = _load_nyse_holidays()
    return date_str not in holidays


def _next_trading_day(date_str: str, market: str) -> str:
    """Encuentra el siguiente día hábil después de una fecha dada (max 30 días)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    check_fn = _is_bvc_trading_day if market == "bvc" else _is_nyse_trading_day
    for _ in range(30):
        dt += timedelta(days=1)
        candidate = dt.strftime("%Y-%m-%d")
        if check_fn(candidate):
            return candidate
    return date_str


class DataUnifier:
    """
    Unificador de datos financieros de múltiples activos.

    Funcionalidades:
    - Combina datos de múltiples símbolos en un solo dataset
    - Alinea calendarios bursátiles (BVC vs NYSE)
    - Rellena días faltantes con None para interpolación posterior
    - Ordena por fecha para mantener integridad temporal
    - Valida consistencia entre registros
    - Genera estadísticas del dataset unificado

    Complejidad temporal: O(n log n) dominada por el ordenamiento
    Complejidad espacial: O(n) para almacenar el dataset unificado
    """

    COLOMBIAN_SYMBOLS = ["ECOPETROL", "ISA", "GEB", "NUTRCSA"]

    REQUIRED_FIELDS = ["date", "symbol", "open", "high", "low", "close", "volume"]

    def _is_colombian(self, symbol: str) -> bool:
        """Determina si un símbolo pertenece al mercado colombiano (BVC)."""
        return symbol.upper() in [s.upper() for s in self.COLOMBIAN_SYMBOLS]

    def _market_trading_days(
        self, start_date: str, end_date: str, market: str
    ) -> List[str]:
        """Genera lista de días hábiles para un mercado en un rango de fechas."""
        check_fn = _is_bvc_trading_day if market == "bvc" else _is_nyse_trading_day
        days = []
        dt = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        while dt <= end:
            candidate = dt.strftime("%Y-%m-%d")
            if check_fn(candidate):
                days.append(candidate)
            dt += timedelta(days=1)
        return days

    def _precompute_trading_days(
        self, start_date: str, end_date: str
    ) -> tuple:
        """Precalcula y cachea días hábiles para BVC y NYSE en un rango."""
        bvc_days = set(self._market_trading_days(start_date, end_date, "bvc"))
        nyse_days = set(self._market_trading_days(start_date, end_date, "nyse"))
        return bvc_days, nyse_days

    def validate_record(self, record: Dict) -> bool:
        """
        Valida que un registro tenga todos los campos requeridos y valores válidos.

        Parámetros:
            record: Diccionario con datos del registro

        Retorna:
            True si el registro es válido, False en caso contrario

        Complejidad: O(f) donde f = número de campos requeridos (7)
        """
        for field in self.REQUIRED_FIELDS:
            if field not in record:
                return False
            if record[field] is None:
                return False

        if record["close"] <= 0 or record["volume"] < 0:
            return False

        return True

    def detect_calendar_gaps(self, records: List[Dict]) -> Dict[str, List[str]]:
        """
        Detecta días faltantes por activo comparando contra los días hábiles
        del mercado correspondiente (BVC o NYSE).

        Para cada símbolo, calcula qué días hábiles del mercado NO tienen registro.
        Esto permite identificar desalineaciones entre calendarios bursátiles.

        Parámetros:
            records: Lista de registros financieros unificados

        Retorna:
            Dict: {symbol: [fechas_faltantes]} para cada símbolo con gaps

        Complejidad: O(s * d) donde s = símbolos, d = días en el rango
        """
        symbols_dates: Dict[str, Set[str]] = {}
        global_min = None
        global_max = None

        for r in records:
            sym = r["symbol"]
            date = r["date"]
            if sym not in symbols_dates:
                symbols_dates[sym] = set()
            symbols_dates[sym].add(date)
            if global_min is None or date < global_min:
                global_min = date
            if global_max is None or date > global_max:
                global_max = date

        if global_min is None or global_max is None:
            return {}

        gaps: Dict[str, List[str]] = {}
        for sym, dates in symbols_dates.items():
            market = "bvc" if self._is_colombian(sym) else "nyse"
            expected = self._market_trading_days(global_min, global_max, market)
            missing = sorted([d for d in expected if d not in dates])
            if missing:
                gaps[sym] = missing

        return gaps

    def align_calendars(self, records: List[Dict]) -> List[Dict]:
        """
        Alinea las series temporales de todos los activos para que compartan
        el mismo conjunto de fechas (unión de todos los días hábiles).

        Para fechas donde un activo no tiene datos (por diferencias de calendario
        bursátil o días festivos), inserta un registro con valores None que
        será interpolado por el DataCleaner.

        Flujo:
        1. Encuentra el rango global de fechas [min, max]
        2. Calcula la unión de días hábiles de todos los mercados
        3. Para cada símbolo, inserta registros None en fechas faltantes

        Parámetros:
            records: Lista de registros financieros unificados

        Retorna:
            Lista de registros con calendarios alineados

        Complejidad: O(s * d + n) donde s = símbolos, d = días, n = registros
        """
        if not records:
            return []

        symbols_data: Dict[str, List[Dict]] = {}
        global_min = None
        global_max = None

        for r in records:
            sym = r["symbol"]
            if sym not in symbols_data:
                symbols_data[sym] = []
            symbols_data[sym].append(r)
            d = r["date"]
            if global_min is None or d < global_min:
                global_min = d
            if global_max is None or d > global_max:
                global_max = d

        if global_min is None or global_max is None:
            return records

        bvc_days_set, nyse_days_set = self._precompute_trading_days(
            global_min, global_max
        )
        all_trading_days = sorted(bvc_days_set | nyse_days_set)

        bvc_sorted = sorted(bvc_days_set)
        nyse_sorted = sorted(nyse_days_set)
        market_days_cache = {"bvc": bvc_sorted, "nyse": nyse_sorted}

        aligned: List[Dict] = []
        for sym, sym_records in symbols_data.items():
            existing = {r["date"]: r for r in sym_records}
            market = "bvc" if self._is_colombian(sym) else "nyse"
            market_days = market_days_cache[market]

            for date in market_days:
                if date in existing:
                    aligned.append(existing[date])
                else:
                    aligned.append(
                        {
                            "date": date,
                            "symbol": sym,
                            "open": None,
                            "high": None,
                            "low": None,
                            "close": None,
                            "volume": None,
                        }
                    )

        aligned.sort(key=lambda x: (x["date"], x["symbol"]))
        return aligned

    def unify_datasets(self, datasets: List[List[Dict]]) -> List[Dict]:
        """
        Combina múltiples datasets en uno solo.

        Parámetros:
            datasets: Lista de listas de registros (cada lista es un activo)

        Retorna:
            Dataset unificado con todos los registros

        Complejidad: O(n) para concatenar + O(n log n) para ordenar
        El ordenamiento es necesario para mantener la integridad temporal
        """
        all_records = []

        for dataset in datasets:
            for record in dataset:
                if self.validate_record(record):
                    all_records.append(record)

        all_records.sort(key=lambda x: (x["date"], x["symbol"]))

        return all_records

    def load_from_csv(self, filepath: str) -> List[Dict]:
        """
        Carga registros desde un archivo CSV.

        Parámetros:
            filepath: Ruta del archivo CSV

        Retorna:
            Lista de diccionarios con los datos

        Complejidad: O(n) donde n = número de registros en el CSV
        """
        records = []

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record = {
                        "date": row["date"],
                        "symbol": row["symbol"],
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                    }
                    if self.validate_record(record):
                        records.append(record)
                except (ValueError, KeyError, TypeError):
                    continue

        return records

    def save_to_csv(self, records: List[Dict], filepath: str) -> None:
        """
        Guarda registros en un archivo CSV unificado.

        Parámetros:
            records: Lista de registros
            filepath: Ruta del archivo de salida

        Complejidad: O(n) para escritura de n registros
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.REQUIRED_FIELDS)
            writer.writeheader()
            writer.writerows(records)

        print(f"Dataset unificado guardado en {filepath} ({len(records)} registros)")

    def generate_statistics(self, records: List[Dict]) -> Dict:
        """
        Genera estadísticas descriptivas del dataset unificado.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Diccionario con estadísticas (símbolos, registros, rango de fechas)

        Complejidad: O(n) para recorrer todos los registros
        """
        if not records:
            return {"total_records": 0}

        symbols = set(r["symbol"] for r in records)
        dates = [r["date"] for r in records]

        total_volume = sum(r["volume"] for r in records)
        avg_volume = total_volume / len(records)

        return {
            "total_records": len(records),
            "unique_symbols": len(symbols),
            "symbols": sorted(list(symbols)),
            "date_range": (min(dates), max(dates)),
            "total_volume": total_volume,
            "average_volume": avg_volume,
        }
