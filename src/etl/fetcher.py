"""
Fetcher Module — Extracción de datos financieros mediante HTTP directo.

Arquitectura:
- Circuit Breaker: ante N fallos consecutivos, espera antes de reintentar
- Backoff exponencial con jitter: evita雷鸣(thundering herd) en APIs
- Plan B (Fallback): si Yahoo Finance falla, usa scraping ético con BeautifulSoup
- Pool de conexiones: reutiliza conexiones TCP via requests.Session

Restricciones del proyecto:
- ✅ NO usa yfinance / pandas_datareader (peticiones HTTP explícitas)
- ✅ Parseo manual del JSON de respuesta
- ✅ Reintentos automáticos documentados
"""

import random
import time
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Optional

import requests
import csv
import os

# ─── Constantes de configuración ──────────────────────────────────────────

MAX_RETRIES: int = 5
"""Número máximo de reintentos por símbolo antes de escalar al Plan B."""

BACKOFF_BASE: float = 2.0
"""Segundos base para backoff exponencial."""

JITTER_MAX: float = 1.0
"""Máximo jitter aleatorio en segundos para evitar sincronización."""

CIRCUIT_BREAKER_THRESHOLD: int = 10
"""Fallos consecutivos globales que activan el Circuit Breaker."""

CIRCUIT_BREAKER_RESET: float = 60.0
"""Segundos de espera tras activar el Circuit Breaker."""

REQUEST_TIMEOUT: int = 30
"""Timeout por petición HTTP en segundos."""

RATE_LIMIT_DELAY: float = 0.5
"""Delay entre peticiones a distintos símbolos en segundos."""

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]
"""
Lista de User-Agent para rotación.
Mitiga bloqueos por fingerprinting en APIs financieras.
"""


def _exponential_backoff(attempt: int) -> float:
    """
    Calcula delay con backoff exponencial y jitter.

    Fórmula: delay = BACKOFF_BASE^attempt + random(0, JITTER_MAX)

    Análisis de complejidad: O(1)

    El jitter distribuido uniformemente evita que múltiples workers
    reintenten al mismo tiempo (problema de雷鸣).

    Args:
        attempt: Número de intento (0-indexed)

    Returns:
        Segundos de espera antes del siguiente reintento
    """
    return BACKOFF_BASE ** attempt + random.uniform(0, JITTER_MAX)


def _parse_yahoo_timestamp(ts: int) -> str:
    """
    Convierte timestamp Unix a string de fecha.

    Args:
        ts: Timestamp Unix en segundos

    Returns:
        Fecha en formato YYYY-MM-DD
    """
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


class YahooFinanceFetcher:
    """
    Descargador de datos financieros vía HTTP directo a Yahoo Finance API.

    Plan B (Fallback):
        Si tras MAX_RETRIES no se obtienen datos, el método
        `fetch_with_fallback()` intenta scraping ético con BeautifulSoup
        sobre portales financieros alternativos.

    Circuit Breaker:
        Si hay CIRCUIT_BREAKER_THRESHOLD fallos consecutivos globales,
        el fetcher espera CIRCUIT_BREAKER_RESET segundos antes de
        reintentar, para no saturar la API ni nuestra IP.
    """

    BASE_URL: str = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    FALLBACK_URL: str = "https://finance.yahoo.com/quote/{symbol}/history"

    def __init__(
        self,
        logger: Optional[Callable[[str], None]] = None,
    ):
        """
        Inicializa el fetcher.

        Args:
            logger: Función callback para logging (default: print)
        """
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

        # Pool de conexiones: reutiliza sockets TCP
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0,
        )
        self._session.mount("https://", adapter)

        self._consecutive_failures: int = 0
        self._circuit_open_until: float = 0.0

    # ──────────────────────────────────────────────────────────────────────
    # Método principal
    # ──────────────────────────────────────────────────────────────────────

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Descarga datos históricos para un símbolo vía HTTP directo.

        Estrategia de reintentos:
        1. Intento 0: petición inmediata
        2. Intento 1-4: backoff exponencial con jitter
        3. Si Circuit Breaker está abierto, falla inmediatamente sin red

        Análisis de complejidad:
            Temporal: O(n) donde n = número de registros devueltos
            Espacial: O(n) para almacenar los registros

        Args:
            symbol: Símbolo del activo (ej: "VOO", "ECOPETROL.CL")
            start_date: Fecha de inicio del historial
            end_date: Fecha de fin del historial

        Returns:
            Lista de registros OHLCV. Vacía si no hay datos.
        """
        if self._circuit_open():
            self._logger(
                f"  ⚠ Circuit Breaker abierto hasta "
                f"{datetime.fromtimestamp(self._circuit_open_until).strftime('%H:%M:%S')}. "
                f"Saltando {symbol}."
            )
            return []

        url = self.BASE_URL.format(symbol=symbol.upper())
        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
            "events": "history",
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                records = self._parse_yahoo_response(response.json(), symbol)
                self._consecutive_failures = 0
                return records

            except ValueError as e:
                self._logger(
                    f"  ✗ Error de parseo JSON en {symbol}: {e}. "
                    f"La API devolvió contenido no válido."
                )
                return []

            except requests.exceptions.RequestException as e:
                self._consecutive_failures += 1
                self._check_circuit_breaker()

                if attempt < MAX_RETRIES - 1:
                    delay = _exponential_backoff(attempt)
                    self._logger(
                        f"  ⚠ Reintento {attempt + 1}/{MAX_RETRIES} para {symbol} "
                        f"en {delay:.1f}s (error: {e.__class__.__name__})"
                    )
                    time.sleep(delay)
                else:
                    self._logger(
                        f"  ✗ Fallo definitivo para {symbol} tras {MAX_RETRIES} intentos: {e}"
                    )

            except (KeyError, TypeError, IndexError) as e:
                self._logger(
                    f"  ✗ Error de parseo en {symbol}: {e}. "
                    f"La respuesta de la API no tiene el formato esperado."
                )
                return []

        return []

    # ──────────────────────────────────────────────────────────────────────
    # Plan B: Fallback con BeautifulSoup
    # ──────────────────────────────────────────────────────────────────────

    def fetch_with_fallback(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Intenta descarga primaria; si falla, escala al Plan B (scraping ético).

        Plan B:
        1. Usa BeautifulSoup para parsear HTML de Yahoo Finance
        2. Extrae la tabla de datos históricos
        3. Filtra por rango de fechas

        Scraping ético:
        - Rate limiting: 2s entre peticiones
        - User-Agent rotatorio
        - Solo accede a datos públicos
        - No sobrecarga el servidor

        Análisis de complejidad:
            Temporal: O(n) para parsear la tabla HTML
            Espacial: O(n) para los registros extraídos

        Args:
            symbol: Símbolo del activo
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de registros OHLCV
        """
        records = self.fetch_historical_data(symbol, start_date, end_date)
        if records:
            return records

        self._logger(f"  → Plan B: scraping ético para {symbol}...")
        return self._fallback_scrape(symbol, start_date, end_date)

    def _fallback_scrape(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Scraping ético de Yahoo Finance HTML.

        Solo se ejecuta cuando el método principal falla.
        Incluye rate limiting y respeto a robots.txt implícito.

        Returns:
            Lista de registros OHLCV scrapeados
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            self._logger(
                "  ✗ BeautifulSoup no está instalado. "
                "Ejecuta: pip install beautifulsoup4"
            )
            return []

        url = self.FALLBACK_URL.format(symbol=symbol.upper())
        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
        }

        try:
            time.sleep(2.0)
            self._session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            })
            response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if not table:
                self._logger(f"  ✗ No se encontró tabla histórica para {symbol}")
                return []

            records: List[Dict] = []
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                try:
                    date_str = cols[0].get_text(strip=True)
                    record = {
                        "date": date_str,
                        "symbol": symbol.split(".")[0].upper(),
                        "open": self._safe_float(cols[1].get_text()),
                        "high": self._safe_float(cols[2].get_text()),
                        "low": self._safe_float(cols[3].get_text()),
                        "close": self._safe_float(cols[4].get_text()),
                        "volume": self._safe_float(cols[6].get_text()),
                    }
                    record_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if start_date <= record_date <= end_date:
                        records.append(record)
                except (ValueError, IndexError):
                    continue

            self._logger(f"  ✓ Scraping exitoso: {len(records)} registros para {symbol}")
            return records

        except Exception as e:
            self._logger(f"  ✗ Falló el scraping para {symbol}: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────
    # Batch download
    # ──────────────────────────────────────────────────────────────────────

    def fetch_multiple_assets(
        self,
        symbols: List[str],
        years: int = 5,
        use_fallback: bool = False,
    ) -> List[Dict]:
        """
        Descarga datos para múltiples activos secuencialmente.

        Para 20 activos × 5 años ≈ 20 × 1250 = 25,000 registros.
        Con rate limiting de 0.5s, el tiempo total estimado es ~10s.

        Análisis de complejidad:
            Temporal: O(a × n) donde a = activos, n = registros por activo
            Espacial: O(a × n) para el dataset completo

        Args:
            symbols: Lista de símbolos a descargar
            years: Años de historial (default: 5)
            use_fallback: Si True, usa fallback scraping ante fallos

        Returns:
            Dataset combinado de todos los activos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        all_records: List[Dict] = []
        total = len(symbols)

        for idx, symbol in enumerate(symbols, 1):
            self._logger(f"Descargando {symbol.upper()} ({idx}/{total})...")

            if use_fallback:
                records = self.fetch_with_fallback(symbol, start_date, end_date)
            else:
                records = self.fetch_historical_data(symbol, start_date, end_date)

            if records:
                all_records.extend(records)
                self._logger(f"  ✓ {len(records)} registros")
            else:
                self._logger("  - Sin datos")

            if idx < total:
                time.sleep(RATE_LIMIT_DELAY)

        return all_records

    # ──────────────────────────────────────────────────────────────────────
    # CSV output
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def save_to_csv(records: List[Dict], filepath: str) -> None:
        """
        Guarda registros en CSV.

        Análisis de complejidad:
            Temporal: O(n) — escritura secuencial de n registros
            Espacial: O(1) — buffer de escritura

        Args:
            records: Lista de registros OHLCV
            filepath: Ruta del archivo CSV de salida
        """
        if not records:
            print("No hay datos para guardar")
            return

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fieldnames = ["date", "symbol", "open", "high", "low", "close", "volume"]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Datos guardados en {filepath} ({len(records)} registros)")

    # ──────────────────────────────────────────────────────────────────────
    # Métodos auxiliares privados
    # ──────────────────────────────────────────────────────────────────────

    def _parse_yahoo_response(self, data: dict, symbol: str) -> List[Dict]:
        """
        Parsea la respuesta JSON de Yahoo Finance API.

        Estructura esperada:
        {
            "chart": {
                "result": [{
                    "timestamp": [int, ...],
                    "indicators": {
                        "quote": [{
                            "open": [float, ...],
                            "high": [float, ...],
                            "low": [float, ...],
                            "close": [float, ...],
                            "volume": [int, ...]
                        }]
                    }
                }]
            }
        }

        Análisis de complejidad:
            Temporal: O(t) donde t = número de timestamps en la respuesta
            Espacial: O(t) para la lista de registros

        Args:
            data: Diccionario parseado del JSON de respuesta
            symbol: Símbolo solicitado (para incluir en cada registro)

        Returns:
            Lista de registros OHLCV

        Raises:
            KeyError: Si la respuesta no tiene la estructura esperada
        """
        result = data.get("chart", {}).get("result", [])
        if not result:
            return []

        result_data = result[0]
        timestamps = result_data.get("timestamp")
        if not timestamps:
            return []

        quote = result_data.get("indicators", {}).get("quote", [{}])[0]
        opens: List[Optional[float]] = quote.get("open", [])
        highs: List[Optional[float]] = quote.get("high", [])
        lows: List[Optional[float]] = quote.get("low", [])
        closes: List[Optional[float]] = quote.get("close", [])
        volumes: List[Optional[int]] = quote.get("volume", [])

        records: List[Dict] = []
        clean_symbol = symbol.split(".")[0].upper()

        for i, ts in enumerate(timestamps):
            if i >= len(closes) or closes[i] is None:
                continue
            records.append({
                "date": _parse_yahoo_timestamp(ts),
                "symbol": clean_symbol,
                "open": opens[i] if i < len(opens) else None,
                "high": highs[i] if i < len(highs) else None,
                "low": lows[i] if i < len(lows) else None,
                "close": closes[i],
                "volume": volumes[i] if i < len(volumes) else None,
            })

        return records

    def _circuit_open(self) -> bool:
        """Verifica si el Circuit Breaker está abierto."""
        if self._circuit_open_until > time.time():
            return True
        return False

    def _check_circuit_breaker(self) -> None:
        """
        Activa el Circuit Breaker si se superó el umbral de fallos.

        Estrategia: si hay CIRCUIT_BREAKER_THRESHOLD fallos consecutivos,
        esperamos CIRCUIT_BREAKER_RESET segundos antes de reintentar.
        Esto evita saturar la API y que nuestra IP sea bloqueada.
        """
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self._circuit_open_until = time.time() + CIRCUIT_BREAKER_RESET
            self._logger(
                f"  🔴 Circuit Breaker activado por {CIRCUIT_BREAKER_RESET}s "
                f"tras {self._consecutive_failures} fallos consecutivos."
            )
            self._consecutive_failures = 0

    @staticmethod
    def _safe_float(text: str) -> Optional[float]:
        """
        Convierte texto a float de forma segura.

        Args:
            text: String con valor numérico (ej: "1,234.56")

        Returns:
            Float o None si no es convertible
        """
        if not text or text == "-":
            return None
        try:
            return float(text.replace(",", ""))
        except ValueError:
            return None

    def close(self) -> None:
        """Cierra la sesión HTTP y libera recursos."""
        self._session.close()


# ─── Alias retrocompatible ────────────────────────────────────────────────
FinancialDataFetcher = YahooFinanceFetcher
