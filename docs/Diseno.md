# Documento de Diseño — Sistema de Análisis Algorítmico Financiero

**Universidad del Quindío** — Programa de Ingeniería de Sistemas y Computación
**Curso**: Análisis de Algoritmos — 2026-1

---

## 1. Introducción

El análisis financiero moderno depende de la capacidad computacional para procesar grandes volúmenes de datos históricos y detectar patrones relevantes en el comportamiento de activos financieros. Este proyecto implementa un sistema que aplica métodos cuantitativos, algoritmos clásicos y técnicas de análisis de series temporales sobre datos reales de la Bolsa de Valores de Colombia (BVC) y ETFs internacionales (S&P 500).

El sistema se compone de cinco módulos principales:
1. **ETL**: Extracción, limpieza y unificación automatizada de datos financieros
2. **Similitud**: 4 algoritmos de comparación entre series temporales
3. **Patrones y Volatilidad**: Detección de patrones por ventana deslizante y clasificación de riesgo
4. **Dashboard**: Visualizaciones interactivas y reporte PDF exportable
5. **API REST**: Despliegue como aplicación web con documentación completa

---

## 2. Arquitectura del Sistema

### 2.1 Estructura del Proyecto

```
investment-algorithm/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── gateway.py              # App factory + registro de Blueprints
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── similarity.py       # Req 2: endpoints de similitud
│   │   │   ├── patterns.py         # Req 3: endpoints de patrones y volatilidad
│   │   │   ├── dashboard.py        # Req 4: candlestick, SMA, resumen
│   │   │   └── reports.py          # Req 4: generación de PDF
│   │   └── templates/
│   │       ├── base.html           # Layout base con navegación
│   │       └── pages/
│   │           ├── index.html      # Landing con estadísticas
│   │           ├── similarity.html # Comparación interactiva de similitud
│   │           ├── patterns.html   # Detección de patrones
│   │           ├── risk.html       # Ranking de riesgo por volatilidad
│   │           └── dashboard.html  # Dashboard completo + exportación PDF
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── fetcher.py              # Orquestador multi-fuente (delega en providers/)
│   │   ├── scraper.py              # Scraper alternativo (fallback legacy)
│   │   ├── cleaner.py              # Limpieza: duplicados, outliers, interpolación
│   │   ├── unifier.py              # Unificación, alineación de calendarios
│   │   └── providers/              # Sistema Multi-Source con fallback automático
│   │       ├── __init__.py
│   │       ├── base.py             # DataProvider (interfaz abstracta)
│   │       ├── multi_source.py     # MultiSourceFetcher (orquestador)
│   │       ├── tiingo.py           # Tiingo API (principal, 500 req/h)
│   │       ├── yahoo_api.py        # Yahoo Finance API (rate limiting)
│   │       ├── alpha_vantage.py    # Alpha Vantage API
│   │       ├── web_scraper.py      # Scraping 5 sitios financieros
│   │       └── binance.py          # Binance API (solo crypto)
│   ├── services/
│   │   ├── similarity/             # Req 2: 4 algoritmos de similitud
│   │   │   ├── __init__.py         # SimilarityAnalyzer (agregador)
│   │   │   ├── euclidean.py        # Distancia Euclidiana O(n)
│   │   │   ├── pearson.py          # Correlación de Pearson O(n)
│   │   │   ├── dtw.py              # Dynamic Time Warping O(n×m)
│   │   │   └── cosine.py           # Similitud por Coseno O(n)
│   │   ├── patterns/               # Req 3: patrones y volatilidad
│   │   │   ├── __init__.py
│   │   │   ├── sliding_window.py   # Ventana deslizante O(n)
│   │   │   └── volatility.py       # Volatilidad y riesgo O(n)
│   │   ├── reporting/              # Req 4: reportes
│   │   │   ├── __init__.py
│   │   │   ├── pdf_report.py       # Generación de PDF con ReportLab
│   │   │   └── technical.py        # SMA e indicadores técnicos O(n)
│   │   ├── volume_analyzer.py      # Análisis de volumen
│   │   └── main_runner.py          # Orquestador del pipeline
│   ├── sorting/                    # 12 algoritmos de ordenamiento
│   │   ├── __init__.py
│   │   ├── algorithms.py
│   │   ├── comparator.py
│   │   └── visualizer.py
│   ├── static/
│   │   ├── css/style.css           # Estilos del frontend
│   │   └── js/charts.js            # Utilidades Chart.js
├── tests/
│   ├── test_similarity.py          # 20 tests de similitud
│   ├── test_patterns.py            # 21 tests de patrones y volatilidad
│   └── test_dashboard.py           # 6 tests de SMA y dashboard
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── Diseno.md                   # Este documento
│   └── Documento de diseño.docx
├── outputs/                        # Reportes PDF generados
├── Proyecto.md                     # Enunciado del proyecto
├── Plan.md                         # Plan de desarrollo
├── requirements.txt
├── Taskfile.yml
├── docker-compose.yml
├── Dockerfile.api
└── Dockerfile.etl
```

### 2.2 Flujo de Ejecución

```
Multi-Source (Tiingo → Yahoo → Alpha Vantage → Web Scraper → Binance)
                           │
                           ▼
Extracción (fetcher) → Limpieza (cleaner) → Unificación (unifier)
                                                    │
                           ┌─────────────────────────┘
                           ▼
               Alineación de Calendarios
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
          Similitud    Patrones    Dashboard
         (4 alg.)    (sliding     (correlación,
                      window,      candlestick,
                      volatilidad)  PDF)
               │           │           │
               ▼           ▼           ▼
          API REST — App Web (Flask + Chart.js)
```

### 2.3 Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Backend | Python 3.11+ | Lenguaje principal |
| API | Flask 3.0 | Framework web REST |
| Frontend | Jinja2 + Chart.js | Templates y gráficos interactivos |
| HTTP | requests 2.31 | Peticiones HTTP directas a APIs |
| PDF | ReportLab 4.1 | Generación de reportes |
| Gráficos PDF | Matplotlib 3.8 | Imágenes para reportes |
| Testing | pytest 7.4 | Tests unitarios |
| Linter | Ruff 0.1 | Calidad de código |
| Infra | Docker + Taskfile | Contenedores y automatización |

---

## 3. Requerimiento 1 — ETL Automatizado

### 3.1 Extracción — Sistema Multi-Source con Fallback Automático

Se implementó una arquitectura Multi-Source que intenta obtener datos de 5 proveedores en secuencia, deteniéndose en el primero que retorna datos exitosamente. Esto garantiza robustez ante fallos de APIs individuales, rate limiting o cambios en la estructura de sitios web.

**Arquitectura:**

```
MultiSourceFetcher (orquestador)
    │
    ├── [1] Tiingo API          → 500 req/hora gratis, datos ajustados
    ├── [2] Yahoo Finance API   → Rate limiting mejorado + Circuit Breaker
    ├── [3] Alpha Vantage API   → 5 calls/minuto, cobertura global
    ├── [4] Web Scraper         → 5 sitios (StockAnalysis, Investing.com,
    │                              Google Finance, MarketWatch, CNBC)
    └── [5] Binance API         → Solo crypto (BTC, ETH, etc.)
```

Cada proveedor implementa la interfaz abstracta `DataProvider` (`providers/base.py`):

```python
class DataProvider(ABC):
    @abstractmethod
    def fetch(self, symbol, start_date, end_date) -> List[Dict]: ...
    def is_available(self) -> bool: ...
    def close(self) -> None: ...
```

**Orden de prioridad:** Tiingo → Yahoo Finance → Alpha Vantage → Web Scraper → Binance

El `MultiSourceFetcher` (`providers/multi_source.py`) itera sobre los providers, llama a `fetch()` y retorna los datos del primer proveedor que retorna una lista no vacía. Si todos fallan, retorna lista vacía.

**Proveedores implementados:**

| Proveedor | Archivo | API Key | Rate Limit | Cobertura |
|-----------|---------|---------|------------|-----------|
| Tiingo | `tiingo.py` | Sí (incluida) | 500 req/hora | US stocks, ETFs, ADRs |
| Yahoo Finance | `yahoo_api.py` | No | ~200 req/hora práctica | Global |
| Alpha Vantage | `alpha_vantage.py` | Sí (incluida) | 5 calls/min, 500/día | Global |
| Web Scraper | `web_scraper.py` | No | N/A (depende del sitio) | 5 sitios financieros |
| Binance | `binance.py` | No | 1200 req/min | Crypto (BTC, ETH, etc.) |

**Mecanismos de tolerancia a fallos:**

1. **Yahoo Finance — Circuit Breaker**: Tras 20 fallos consecutivos, espera 120 segundos antes de reintentar. Esto evita saturar la API cuando está rate limitando.
2. **Alpha Vantage — Rate limiting propio**: Delay de 12.5s entre llamadas para respetar el límite de 5 calls/min.
3. **Web Scraper — Multi-sitio**: Si un sitio cambia su HTML o bloquea, automáticamente prueba el siguiente sitio (StockAnalysis → Investing → Google Finance → MarketWatch → CNBC).
4. **Delay entre providers**: 1s entre cambios de proveedor.
5. **Delay entre símbolos**: 2s entre descargas de distintos activos.

**Parsing manual:** Cada proveedor parsea la respuesta JSON o HTML a un formato OHLCV unificado: `{date, symbol, open, high, low, close, volume}`.

**23 activos:** 4 acciones colombianas (ECOPETROL.CL, ISA.CL, GEB.CL, NUTRESA.CL) + 16 ETFs internacionales (VOO, VTI, QQQ, SPY, VEA, VWO, BND, EFA, EEM, TLT, IVV, SCHD, DIA, IWM, XLF, XLK) + 3 acciones NYSE (KO, PFE, PEP).

### 3.2 Limpieza de Datos

#### Eliminación de Duplicados
- **Técnica**: HashSet con tuplas (date, symbol) como clave
- **Complejidad**: O(n) tiempo, O(n) espacio
- **Justificación**: Cada par (fecha, símbolo) debe ser único. Los duplicados distorsionan estadísticas (media, varianza, volumen total).

#### Detección de Outliers — Z-Score
- **Fórmula**: |z| = |(x - μ) / σ| > 3.0
- **Complejidad**: O(n) — dos pasadas (media y desviación)
- **Limitación**: Asume distribución normal de los datos

#### Detección de Outliers — IQR (Rango Intercuartil)
- **Fórmula**: Outlier si x < Q1 - 1.5×IQR o x > Q3 + 1.5×IQR
- **Complejidad**: O(n log n) — dominada por el ordenamiento para cuartiles
- **Justificación**: Más robusto que Z-Score porque no asume distribución normal. Los retornos financieros típicamente no siguen una distribución normal (tienen colas pesadas).

#### Interpolación Lineal
- **Fórmula**: valor = (anterior + siguiente) / 2
- **Complejidad**: O(n) — búsqueda de vecinos + promedio
- **Justificación**: Preserva la longitud del dataset y mantiene tendencias sin discontinuidades.

#### Forward Fill
- **Técnica**: Propagar el último valor conocido hacia adelante
- **Complejidad**: O(n)
- **Aplicación**: Cuando el valor se mantiene constante hasta nuevo registro

#### Backward Fill
- **Técnica**: Propagar el siguiente valor conocido hacia atrás
- **Complejidad**: O(n)
- **Aplicación**: Valores faltantes al inicio de la serie

**Orden del pipeline de limpieza:**
1. Duplicados primero (afectan estadísticas)
2. Outliers después (basados en estadísticas corregidas)
3. Interpolación último (usa contexto temporal completo)
   - Lineal primero (mejor estimación con vecinos)
   - Forward-fill segundo (respaldo si falta vecino anterior)
   - Backward-fill último (respaldo si falta vecino siguiente)

### 3.3 Alineación de Calendarios Bursátiles

Se implementó un sistema de detección de días hábiles para cada mercado:

- **BVC (Colombia)**: 18 festivos fijos por año + fines de semana
- **NYSE (EE.UU.)**: 10 festivos fijos por año + fines de semana

**Algoritmo de alineación:**
1. Para cada símbolo, se identifica su mercado (BVC o NYSE)
2. Se calcula la unión de todos los días hábiles de ambos mercados
3. Para fechas donde un activo no tiene datos, se inserta un registro con valores `None`
4. El `DataCleaner` interpola esos valores en la siguiente etapa

**Complejidad**: O(s × d + n) donde s = símbolos, d = días en el rango, n = registros

---

## 4. Requerimiento 2 — Algoritmos de Similitud

### 4.1 Distancia Euclidiana

**Archivo**: `src/services/similarity/euclidean.py`

**Fórmula:**
```
d(x, y) = √( (1/n) × Σ(xᵢ - yᵢ)² )
```

**Interpretación**: 0 = series idénticas. Valores más altos = mayor disimilitud.

**Complejidad**: O(n) tiempo, O(1) espacio — una pasada para diferencias al cuadrado.

**Aplicación**: Comparación de precios normalizados o retornos diarios.

### 4.2 Correlación de Pearson

**Archivo**: `src/services/similarity/pearson.py`

**Fórmula:**
```
r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² · Σ(yᵢ - ȳ)²)
```

**Interpretación**: r ∈ [-1, 1]. 1 = correlación perfecta positiva, 0 = sin relación lineal, -1 = correlación inversa.

**Complejidad**: O(n) tiempo, O(1) espacio — media (1 pasada) + covarianza/varianzas (1 pasada).

**Aplicación**: Medir relación lineal entre retornos de activos para diversificación de portafolio.

### 4.3 Dynamic Time Warping (DTW)

**Archivo**: `src/services/similarity/dtw.py`

**Fórmula:**
```
DTW(x, y) = min π Σ(i,j)∈π |xᵢ - yⱼ|
```

Donde π es un camino de warping que alinea los índices de ambas series.

**Algoritmo**: Programación dinámica — matriz de distancia acumulada D de tamaño (n+1)×(m+1):
```
D[i][j] = |xᵢ - yⱼ| + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
```

**Optimización (Sakoe-Chiba)**: Restringe el warping a una banda de ancho w alrededor de la diagonal, reduciendo la complejidad de O(n×m) a O(n×w).

**Complejidad**: O(n×m) sin optimización, O(n×w) con Sakoe-Chiba.

**Aplicación**: Comparar activos con desfases temporales o diferentes calendarios.

### 4.4 Similitud por Coseno

**Archivo**: `src/services/similarity/cosine.py`

**Fórmula:**
```
cos(θ) = (x · y) / (||x|| · ||y||) = Σ(xᵢ · yᵢ) / √(Σxᵢ²) · √(Σyᵢ²)
```

**Interpretación**: cos(θ) ∈ [-1, 1]. 1 = misma dirección, 0 = ortogonal, -1 = dirección opuesta. A diferencia de Pearson, NO centra los datos (no resta la media).

**Complejidad**: O(n) tiempo, O(1) espacio — una pasada para producto punto y normas.

**Aplicación**: Comparar perfiles de retornos diarios considerando magnitud y dirección.

### 4.5 SimilarityAnalyzer (Agregador)

**Archivo**: `src/services/similarity/__init__.py`

La clase `SimilarityAnalyzer` coordina los 4 algoritmos:
1. Extrae y alinea series de dos símbolos por fecha común (O(n))
2. Calcula retornos diarios (O(n))
3. Ejecuta los 4 algoritmos y retorna resultados estructurados
4. Método `compute_correlation_matrix()` para matriz completa O(s² × n)

**Endpoint API**: `GET /api/similarity?s1=VOO&s2=SPY`

---

## 5. Requerimiento 3 — Patrones y Volatilidad

### 5.1 Ventana Deslizante

**Archivo**: `src/services/patterns/sliding_window.py`

#### Patrón 1: Días Consecutivos al Alza
- **Definición**: Secuencia de N días donde close > close anterior
- **Algoritmo**: Contador acumulado — O(n) tiempo, O(1) espacio
  ```
  contador = 0
  para cada día i:
    si close[i] > close[i-1]: contador++
    sino: contador = 0
    si contador >= N: patrón detectado
  ```
- **Endpoint**: `GET /api/patterns?symbol=VOO&pattern=consecutive_up&min_days=3`

#### Patrón 2: Gap Up
- **Definición**: Día donde open > prev_close × (1 + threshold)
- **Algoritmo**: Comparación día contra día anterior — O(n)
- **Parámetro**: threshold configurable (default 2%)
- **Endpoint**: `GET /api/patterns?symbol=VOO&pattern=gap_up&threshold=0.02`

### 5.2 Volatilidad y Clasificación de Riesgo

**Archivo**: `src/services/patterns/volatility.py`

#### Cálculo de Retornos Diarios
```
rᵢ = (closeᵢ - closeᵢ₋₁) / closeᵢ₋₁
```
Complejidad: O(n)

#### Desviación Estándar
```
σ = √(Σ(rᵢ - r̄)² / (n-1))
```
Complejidad: O(n)

#### Volatilidad Anualizada
```
σ_anual = σ_diaria × √252
```
Se usan 252 días de negociación como estándar bursátil.

#### Clasificación de Riesgo

| Categoría | Rango | Color |
|-----------|-------|-------|
| Conservador | σ_anual < 15% | 🟢 Verde |
| Moderado | 15% ≤ σ_anual < 30% | 🟡 Amarillo |
| Agresivo | σ_anual ≥ 30% | 🔴 Rojo |

**Complejidad total**: O(s × n + s log s) donde s = número de símbolos, n = registros por símbolo.

**Endpoints**:
- `GET /api/volatility?symbol=VOO` — Métricas individuales
- `GET /api/volatility/ranking` — Ranking completo

---

## 6. Requerimiento 4 — Dashboard y Reportes

### 6.1 Matriz de Correlación

Calcula el coeficiente de Pearson entre todos los pares de activos.

- **Complejidad**: O(s² × n) donde s = símbolos, n = observaciones
- **Visualización**: Heatmap dinámico en el frontend (colores por valor)
- **Endpoint**: `GET /api/correlation-matrix`

### 6.2 Media Móvil Simple (SMA)

**Archivo**: `src/services/reporting/technical.py`

```
SMA[i] = (cumsum[i] - cumsum[i - window]) / window
```

- SMA-20: media de 20 días (~1 mes de negociación)
- SMA-50: media de 50 días (~2.5 meses)
- **Complejidad**: O(n) con suma acumulativa

**Endpoint**: `GET /api/candlestick?symbol=VOO&smas=20,50&limit=252`

### 6.3 Reporte PDF

**Archivo**: `src/services/reporting/pdf_report.py`

**Tecnología**: ReportLab para estructura + matplotlib para gráficos incrustados.

**Secciones del PDF:**
1. **Portada**: Universidad, curso, título, fecha de generación
2. **Resumen del Portafolio**: activos, registros, rango de fechas
3. **Matriz de Correlación**: heatmap generado con matplotlib, tabla de pares extremos
4. **Ranking de Riesgo**: tabla completa con colores por categoría, distribución
5. **Candlestick**: gráfico de precios con SMA-20 y SMA-50
6. **Similitud**: tabla con las 4 métricas del par más correlacionado

**Endpoint**: `POST /api/report/generate` (con JSON opcional `{"symbol": "VOO"}`)

---

## 7. Requerimiento 5 — Despliegue y Documentación

### 7.1 API REST

La API está organizada en Blueprints de Flask para modularidad:

| Blueprint | Endpoints | Propósito |
|-----------|-----------|-----------|
| `similarity_bp` | `GET /api/similarity` | Similitud entre 2 activos |
| | `GET /api/similarity/symbols` | Listar símbolos disponibles |
| | `GET /api/correlation-matrix` | Matriz de correlación completa |
| `patterns_bp` | `GET /api/patterns` | Detección de patrones |
| | `GET /api/volatility` | Volatilidad por activo |
| | `GET /api/volatility/ranking` | Ranking de riesgo |
| `dashboard_bp` | `GET /api/candlestick` | Datos OHLC + SMA |
| | `GET /api/dashboard/summary` | Resumen del dashboard |
| `reports_bp` | `POST /api/report/generate` | Generar PDF |

Además, rutas HTML para las páginas del frontend:
- `/` — Inicio
- `/similarity` — Página de similitud interactiva
- `/patterns` — Página de patrones
- `/risk` — Página de riesgo
- `/dashboard` — Dashboard completo

### 7.2 Frontend

Tecnología: Jinja2 (templates Flask) + Chart.js (visualizaciones).

**Páginas:**
- **Inicio**: Cards resumen con estadísticas del dataset, tabla de activos
- **Similitud**: Selector de 2 activos, gráfica superpuesta, tabla de 4 métricas, explicación matemática
- **Patrones**: Selector de activo + patrón, gráfica de frecuencia por año, últimas ocurrencias
- **Riesgo**: Ranking ordenado con colores, gráfico doughnut de distribución, stats resumen
- **Dashboard**: Heatmap de correlación dinámico, candlestick con toggle SMA-20/SMA-50, botón de exportación PDF

### 7.3 Despliegue

**Docker**:
```bash
docker-compose up    # Inicia API + ETL
```

**Taskfile**:
```bash
task install   # Crear entorno virtual + instalar dependencias
task run       # Pipeline ETL completo
task api       # Servidor web en localhost:5000
task test      # Ejecutar tests
task lint      # Verificar código
```

### 7.4 Reproducibilidad

El pipeline es completamente reproducible:
```bash
task install
python -m src.services.main_runner --force-download
python -m src.api.gateway
```

El flag `--force-download` garantiza que los datos se descarguen desde cero, sin usar caché.

---

## 8. Análisis de Complejidad Consolidado

| Componente | Algoritmo | Complejidad Temporal | Complejidad Espacial |
|------------|-----------|---------------------|---------------------|
| ETL - Multi-Source | 5 providers en secuencia | O(p × r) requests | O(n × a) datos |
| ETL - Descarga | HTTP requests por provider | O(a) requests | O(n × a) datos |
| ETL - Duplicados | HashSet | O(n) | O(n) |
| ETL - Outliers Z-Score | Media + Desviación | O(n) | O(1) |
| ETL - Outliers IQR | Ordenar + Cuartiles | O(n log n) | O(n) |
| ETL - Interpolación Lineal | Vecinos + Promedio | O(n) | O(n) |
| ETL - Forward Fill | Propagación adelante | O(n) | O(1) |
| ETL - Backward Fill | Propagación atrás | O(n) | O(1) |
| ETL - Alineación Calendarios | Unión de fechas | O(s × d) | O(d) |
| ETL - Unificación | Sort + Merge | O(n log n) | O(n) |
| Similitud - Euclidiana | Suma diferencias² | O(n) | O(1) |
| Similitud - Pearson | Covarianza / Varianza | O(n) | O(1) |
| Similitud - DTW | Programación Dinámica | O(n × m) / O(n × w) | O(n × m) |
| Similitud - Coseno | Producto punto | O(n) | O(1) |
| Similitud - Matriz Correlación | Pearson por pares | O(s² × n) | O(s²) |
| Patrones - Consecutive Up | Contador acumulado | O(n) | O(1) |
| Patrones - Gap Up | Comparación día anterior | O(n) | O(1) |
| Volatilidad | Desviación estándar | O(n) | O(1) |
| SMA | Suma acumulativa | O(n) | O(n) |
| Reporte PDF | Generación + matplotlib | O(n) | O(n) |

Donde:
- n = número de registros por activo (≈1250 para 5 años)
- s = número de símbolos (20)
- a = número de activos (20)
- d = días en el rango temporal
- m = longitud de segunda serie (DTW)
- w = ancho de banda Sakoe-Chiba
- p = número de providers (5)
- r = número de reintentos por provider

---

## 9. Tests Unitarios

**Total**: 139 tests, todos pasando.

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `tests/test_similarity.py` | 20 | Distancia Euclidiana, Pearson, DTW, Coseno, SimilarityAnalyzer |
| `tests/test_patterns.py` | 21 | Consecutive Up, Gap Up, PatternAnalyzer, retornos, desviación, volatilidad, clasificación, VolatilityAnalyzer, ranking |
| `tests/test_dashboard.py` | 6 | SMA con diferentes ventanas, casos borde |
| `tests/test_etl_fetcher.py` | 4 | MultiSourceFetcher, fetch_historical_data, fetch_multiple_assets, save_to_csv |
| `tests/test_etl_cleaner.py` | 26 | Duplicados, outliers Z-Score/IQR, interpolación, forward/backward fill, pipeline completo |
| `tests/test_etl_unifier.py` | 10 | Unificación, estadísticas, símbolos disponibles, integración |
| `tests/test_etl_scraper.py` | 8 | Scraper básico, símbolo inválido, conexión fallida, parseo |
| `tests/test_comparator.py` | 9 | Comparator con todos los algoritmos |
| `tests/test_sorting.py` | 12 | Algoritmos de ordenamiento (TimSort, Comb, Selection, Tree, etc.) |
| `tests/test_api_gateway.py` | 14 | Endpoints, blueprints, HTML pages |
| `tests/test_pdf_report.py` | 5 | Generación de PDF con diferentes configuraciones |

Ejecución: `task test` o `python -m pytest tests/ -v`

---

## 10. Declaración de Uso de IA

En el desarrollo de este proyecto se utilizó inteligencia artificial generativa como apoyo para:

### Herramientas utilizadas
- **Anthropic Claude (CLI de opencode)**: Asistente principal para planificación, generación de código y resolución de problemas

### Alcance del uso
1. **Planificación**: Estructuración inicial del proyecto en fases (`Plan.md`)
2. **Generación de código base**: Implementación de los 4 algoritmos de similitud, detección de patrones, módulo de volatilidad, dashboard y reporte PDF
3. **Refactorización**: Migración de rutas planas a Blueprints de Flask
4. **Frontend**: Generación de templates HTML con Chart.js
5. **Tests**: Creación de tests unitarios para cada módulo
6. **Documentación**: Este documento de diseño

### Lo que NO fue generado por IA
- El diseño algorítmico y la selección de técnicas
- El análisis formal de complejidad computacional (Big-O)
- La fundamentación matemática de cada algoritmo
- Las decisiones de diseño arquitectónico
- La interpretación de resultados financieros

### Registro de Prompts de Asistencia

Los siguientes pares prompt-respuesta corresponden únicamente a consultas de ayuda,
debugging, refactorización y revisión de código. Los algoritmos fueron obtenidos
de fuentes externas (páginas web en español, documentación técnica) y no se listan aquí.

| # | Prompt | Respuesta |
|---|--------|-----------|
| 1 | *"El test de NaN en euclidean.py falla porque la norma da NaN. ¿Qué falta?"* | Filtrar `None` y `NaN` de ambas series antes de calcular la suma de cuadrados. Agregar `_validate_series()` que retorna `(0, 0, 0)` si alguna serie queda vacía tras el filtrado. |
| 2 | *"¿Cómo migro las rutas de Flask de un solo archivo a Blueprints sin romper la app?"* | Crear `src/api/routes/` con `similarity.py`, `patterns.py`, `dashboard.py`. Cada uno con `Blueprint()` y registro en `gateway.py` via `app.register_blueprint()`. El `static_folder` debe apuntar a `../static` relativo al gateway. |
| 3 | *"¿Por qué el DTW explota en memoria con series de 5000 puntos?"* | La matriz completa es O(n²). Agregar `full_matrix=False` para mantener solo 2 filas (O(m)). El flag debe aceptar `Optional[int]` para la ventana Sakoe-Chiba. |
| 4 | *"Hay un KeyError potencial en comparator.py línea 69 cuando el campo sort_key no existe"* | Usar `r.get(sort_key, 0)` en vez de `r[sort_key]`. Además los contadores `comparison_count` y `swap_count` no se resetean entre runs; hay que asignarlos a 0 antes de cada `algorithm()`. |
| 5 | *"El SMA del reporte técnico da valores incorrectos cuando hay None en la serie"* | No tratar None como 0.0. Llevar un `valid_count` acumulativo paralelo al `cumsum` y usarlo en el denominador: `actual = valid_count[i+1] - valid_count[i+1-window]`. Si `actual == 0`, retornar None. |
| 6 | *"¿Dónde pongo los símbolos colombianos (ECOPETROL, ISA, etc.) para no duplicarlos?"* | Moverlos del frontend JS a un endpoint `/api/similarity/symbols` que retorna `{"colombian": [...], "international": [...]}`. El frontend hace fetch una vez y los muestra. |
| 7 | *"El Bitonic Sort no ordena correctamente ¿qué tiene mal el compare_and_swap?"* | La condición `direction != should_swap` debe ser `direction == should_swap`. La lógica correcta: en ascending (True) se intercambia si `arr[i] > arr[j]`; en descending (False) si `arr[i] < arr[j]`. Ambas se cumplen con `==`. |
| 8 | *"El scraper.py falla silenciosamente con ciertos símbolos"* | Validar todos los campos OHLCV (no solo `open`). Cambiar `except Exception` por `except (KeyError, TypeError, IndexError)` para no tragar errores de programación. |
| 9 | *"El cosine retorna similarity > 1.0 por errores de punto flotante"* | Hacer clamp del valor retornado, no solo del input de `acos`. Usar `clamped = max(-1.0, min(1.0, similarity))` y retornar `clamped`. |
| 10 | *"¿Cómo asegurar reproducibilidad con --force-download?"* | El flag debe skipear el caché de archivos CSV y forzar descarga + recleaning + reunificación completa. Agregar `--use-scraper` opcional para cambiar entre API y BeautifulSoup. |
| 11 | *"Yahoo Finance rate limita mucho. ¿Cómo hacer un sistema multi-fuente con fallback?"* | Crear interfaz abstracta `DataProvider`, implementar 5 providers (Tiingo, Yahoo, Alpha Vantage, Web Scraper, Binance). `MultiSourceFetcher` orquesta el fallback automático. |
| 12 | *"El scraper de Investing.com ya no funciona. ¿Cómo añadir StockAnalysis y Google Finance?"* | Refactorizar scraper monolítico a `ScraperProvider` con múltiples sitios encadenados. Cada sitio tiene su propio método `_try_sitio()` y se prueban en secuencia. |
| 13 | *"¿Cómo integrar Binance para los símbolos crypto del portafolio?"* | Crear `BinanceProvider` que usa `/api/v3/klines`. Detectar símbolos crypto y delegar directamente bypassando el Web Scraper. |

---

## 11. Limitaciones y Trabajo Futuro

### Limitaciones conocidas
- Tiingo API tiene cobertura limitada para tickers colombianos (solo ADRs)
- Alpha Vantage tiene rate limit muy restrictivo (5 calls/minuto)
- Los scrapers web dependen de la estructura HTML que puede cambiar sin previo aviso
- Yahoo Finance sigue siendo propenso a rate limiting (>200 req/hora)
- Los festivos colombianos se modelan con fechas fijas (no móviles como Semana Santa)
- El DTW sin restricción de ventana tiene complejidad O(n²) para series largas
- La generación de PDF usa archivos temporales para imágenes matplotlib

### Posibles mejoras
- Implementar caché de datos con SQLite para evitar descargas repetidas
- Agregar autenticación básica a la API
- Soporte para más mercados (Europa, Asia)
- Patrones adicionales: doble techo, cabeza y hombros, banderas
- Notificaciones por email cuando se detecten patrones
- Despliegue en la nube (Heroku, Railway, o servidor VPS)

---

*Documento de diseño generado para el curso de Análisis de Algoritmos — Universidad del Quindío — 2026-1*
