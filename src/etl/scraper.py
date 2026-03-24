"""
Scraper Module - Web scraping de datos financieros desde Investing.com.
Este módulo obtiene datos históricos de acciones y ETFs mediante Selenium.
"""

import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)


class InvestingScraper:
    """
    Scraper para obtener datos financieros desde Investing.com.

    Utiliza Selenium para navegar y extraer datos históricos de precios.
    Incluye manejo de ratelimit y detection avoidance.

    Complejidad de extracción por activo: O(d) donde d = días solicitados
    """

    BASE_URL = "https://www.investing.com/equities/{symbol}-historical-data"

    COLOMBIAN_STOCKS = {
        "ecopetrol": "Ecopetrol S.A.",
        "isa": "ISA",
        "geb": "Grupo Energía de Bogotá",
        "nutresa": "Nutresa",
    }

    INTERNATIONAL_ETFS = {
        "voo": "Vanguard S&P 500 ETF",
        "vti": "Vanguard Total Stock Market",
        "qqq": "Invesco QQQ Trust",
        "spy": "SPDR S&P 500 ETF",
        "vea": "Vanguard FTSE Developed Markets",
        "vwo": "Vanguard FTSE Emerging Markets",
        "bnd": "Vanguard Total Bond Market",
        "efa": "iShares MSCI EAFE",
        "eem": "iShares MSCI Emerging Markets",
        "tlt": "iShares 20+ Year Treasury Bond",
        "ivv": "iShares Core S&P 500 ETF",
        "schd": "Schwab U.S. Dividend Equity ETF",
        "dia": "SPDR Dow Jones Industrial Average",
        "iwm": "iShares Russell 2000 ETF",
        "xlf": "Financial Select Sector SPDR",
        "xlk": "Technology Select Sector SPDR",
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait_time = random.uniform(2, 4)

    def _init_driver(self) -> webdriver.Chrome:
        """
        Inicializa el driver de Chrome con opciones anti-detección.
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
            },
        )

        return driver

    def _safe_get(self, url: str, max_retries: int = 3) -> bool:
        """
        Navega a una URL de forma segura con reintentos.
        """
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(self.wait_time)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
                else:
                    print(f"Error navigating to {url}: {e}")
                    return False
        return False

    def _wait_for_table(self, timeout: int = 10) -> bool:
        """
        Espera a que la tabla de datos históricos cargue.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "historical-data-table"))
            )
            return True
        except TimeoutException:
            return False

    def _parse_date(self, date_str: str) -> str:
        """
        Convierte formato de fecha de Investing.com a YYYY-MM-DD.
        """
        try:
            dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return date_str

    def _extract_number(self, value_str: str) -> Optional[float]:
        """
        Convierte string de precio a número.
        """
        if not value_str or value_str == "-":
            return None

        cleaned = value_str.replace(",", "").replace(".", "").strip()

        try:
            return float(cleaned)
        except ValueError:
            return None

    def fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime = None
    ) -> List[Dict]:
        """
        Descarga datos históricos para un símbolo desde Investing.com.

        Parámetros:
            symbol: Símbolo del activo (ej: 'ecopetrol', 'voo')
            start_date: Fecha inicial del período
            end_date: Fecha final (default: datetime.now())

        Retorna:
            Lista de diccionarios con OHLCV

        Complejidad: O(d) donde d = número de días
        """
        if end_date is None:
            end_date = datetime.now()

        if self.driver is None:
            self.driver = self._init_driver()

        url = f"https://www.investing.com/equities/{symbol.lower()}-historical-data"

        if not self._safe_get(url):
            return []

        if not self._wait_for_table():
            print(f"Tabla no encontrada para {symbol}")
            return []

        records = []

        try:
            table = self.driver.find_element(By.CLASS_NAME, "historical-data-table")
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")

                    if len(cols) >= 6:
                        date_str = cols[0].text.strip()
                        date = self._parse_date(date_str)

                        if (
                            start_date
                            <= datetime.strptime(date, "%Y-%m-%d")
                            <= end_date
                        ):
                            record = {
                                "date": date,
                                "symbol": symbol.upper(),
                                "open": self._extract_number(cols[1].text),
                                "high": self._extract_number(cols[2].text),
                                "low": self._extract_number(cols[3].text),
                                "close": self._extract_number(cols[4].text),
                                "volume": self._extract_number(
                                    cols[5]
                                    .text.replace("M", "000000")
                                    .replace("K", "000")
                                ),
                            }

                            if record["close"] is not None:
                                records.append(record)

                except (StaleElementReferenceException, NoSuchElementException):
                    continue

        except NoSuchElementException:
            print(f"Tabla no encontrada para {symbol}")

        time.sleep(random.uniform(1, 2))

        return records

    def fetch_multiple_assets(self, symbols: List[str], years: int = 5) -> List[Dict]:
        """
        Descarga datos para múltiples activos.

        Parámetros:
            symbols: Lista de símbolos a descargar
            years: Número de años de historial

        Retorna:
            Lista combinada de todos los registros

        Complejidad: O(n * d) donde n = número de activos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        all_records = []
        total = len(symbols)

        for idx, symbol in enumerate(symbols, 1):
            print(f"Descargando {symbol.upper()} ({idx}/{total})...")

            records = self.fetch_historical_data(symbol, start_date, end_date)

            if records:
                all_records.extend(records)
                print(f"  -> {len(records)} registros obtenidos")
            else:
                print("  -> Sin datos disponibles")

            if idx < total:
                delay = random.uniform(3, 6)
                time.sleep(delay)

        return all_records

    def close(self):
        """
        Cierra el driver del navegador.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
