# Plan de Desarrollo — Sistema de Análisis Algorítmico Financiero

## Universidad del Quindío
### Programa de Ingeniería de Sistemas y Computación
### Análisis de Algoritmos — 2026-1

---

## 1. Estado Actual del Proyecto

### Base Existente (Seguimiento 1)

El proyecto ya cuenta con una base funcional desarrollada en el Seguimiento 1:

| Componente | Archivos | Estado |
|------------|----------|--------|
| ETL (Extracción) | `src/etl/fetcher.py`, `scraper.py` | HTTP directo a Yahoo Finance, 20 activos, 5 años |
| ETL (Limpieza) | `src/etl/cleaner.py` | Duplicados (HashSet O(n)), Outliers (Z-Score O(n)), Interpolación lineal O(n) |
| ETL (Unificación) | `src/etl/unifier.py` | Validación, unificación, estadísticas O(n log n) |
| Sorting (12 algoritmos) | `src/sorting/algorithms.py` | TimSort, Comb, Selection, Tree, Pigeonhole, Bucket, Radix, Counting, Cocktail, Gnome, Heap, Shell |
| Comparador | `src/sorting/comparator.py` | Benchmark multi-run con tabla de resultados |
| Visualizador | `src/sorting/visualizer.py` | Gráfico de complejidad comparativa |
| Análisis de Volumen | `src/services/volume_analyzer.py` | Top N días por volumen O(n log n) |
| API REST | `src/api/gateway.py` | Flask, endpoints básicos |
| Infraestructura | `Dockerfile.api`, `Dockerfile.etl`, `docker-compose.yml`, `Taskfile.yml` | Contenedores Docker + automatización Taskfile |

### Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ / Flask 3.0 |
| Frontend | Flask + Jinja2 + Chart.js |
| Visualización offline | Matplotlib 3.8 |
| PDF | ReportLab |
| Tests | pytest 7.4 |
| Linter | Ruff 0.1 |
| Infra | Docker + Taskfile |

---

## 2. Arquitectura Objetivo

```
investment-algorithm/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── gateway.py              # App factory + registro de Blueprints
│   │   ├── routes/
│   │   │   ├── __init__.py          # Blueprint aggregator
│   │   │   ├── similarity.py       # Req 2: endpoints de similitud
│   │   │   ├── patterns.py         # Req 3: endpoints de patrones y volatilidad
│   │   │   ├── dashboard.py        # Req 4: endpoints del dashboard
│   │   │   └── reports.py          # Req 4: exportación de reportes
│   │   └── templates/
│   │       ├── base.html           # Layout base con navegación
│   │       └── pages/
│   │           ├── index.html      # Landing page
│   │           ├── similarity.html # Comparación de similitud
│   │           ├── patterns.html   # Detección de patrones
│   │           ├── risk.html       # Ranking de riesgo
│   │           └── dashboard.html  # Dashboard completo + heatmap
│   ├── etl/                        # (SIN CAMBIOS)
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   ├── scraper.py
│   │   ├── cleaner.py
│   │   └── unifier.py
│   ├── services/
│   │   ├── similarity/             # NUEVO: Req 2
│   │   │   ├── __init__.py
│   │   │   ├── euclidean.py        # Distancia Euclidiana
│   │   │   ├── pearson.py          # Correlación de Pearson
│   │   │   ├── dtw.py              # Dynamic Time Warping
│   │   │   └── cosine.py           # Similitud por Coseno
│   │   ├── patterns/               # NUEVO: Req 3
│   │   │   ├── __init__.py
│   │   │   ├── sliding_window.py   # Ventana deslizante para patrones
│   │   │   └── volatility.py       # Métricas de volatilidad y riesgo
│   │   └── reporting/              # NUEVO: Req 4
│   │       ├── __init__.py
│   │       └── pdf_report.py       # Generación de reportes PDF
│   ├── sorting/                    # (SIN CAMBIOS)
│   │   ├── __init__.py
│   │   ├── algorithms.py
│   │   ├── comparator.py
│   │   └── visualizer.py
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── charts.js           # Lógica de gráficas Chart.js
├── data/
│   ├── raw/
│   │   └── raw_data.csv
│   └── processed/
│       ├── unified_data.csv
│       ├── sorting_results.csv
│       ├── top_volume_days.csv
│       └── complexity_comparison.png
├── docs/
│   ├── Diseno.md                   # Documento de diseño actualizado
│   └── Documento de diseño.docx
├── outputs/                        # Reportes PDF generados
├── tests/
│   ├── __init__.py
│   ├── test_fetcher.py
│   ├── test_cleaner.py
│   ├── test_similarity.py
│   ├── test_patterns.py
│   └── test_volatility.py
├── Proyecto.md                     # Enunciado del proyecto
├── Plan.md                         # Este archivo
├── requirements.txt
├── Taskfile.yml
├── docker-compose.yml
├── Dockerfile.api
└── Dockerfile.etl
```

---

## 3. Fases de Implementación

### Fase 1: Mejora del Pipeline ETL (Req 1)

**Objetivo**: Robustecer el proceso ETL existente para cumplir con todos los requisitos del proyecto.

#### 1.1 Manejo de Calendarios Bursátiles

- **Qué**: Detectar y manejar diferencias entre calendarios de mercados (BVC vs NYSE)
- **Cómo**: Implementar función que identifique días faltantes por activo, alinee todas las series a un calendario unificado
- **Complejidad**: O(n × a) donde n = registros, a = activos
- **Archivos afectados**: `src/etl/unifier.py`

#### 1.2 Interpolación Mejorada

- **Qué**: Documentar y justificar algorítmicamente cada técnica de interpolación
- **Técnicas**: Lineal (O(n)), Forward-fill (O(n)), Backward-fill (O(n))
- **Justificación**: La interpolación lineal preserva tendencias sin introducir discontinuidades; forward-fill es apropiado para datos faltantes al inicio
- **Archivos afectados**: `src/etl/cleaner.py`

#### 1.3 Detección de Anomalías (IQR)

- **Qué**: Agregar método de Rango Intercuartil (IQR) como complemento a Z-Score
- **Complejidad**: O(n log n) dominada por ordenamiento para encontrar cuartiles
- **Archivos afectados**: `src/etl/cleaner.py`

#### 1.4 Reproducibilidad

- **Qué**: El pipeline `task run-etl` debe regenerar todos los datos desde cero
- **Verificación**: Ejecutar en entorno limpio y confirmar que los resultados sean equivalentes

---

### Fase 2: Algoritmos de Similitud (Req 2)

**Objetivo**: Implementar 4 algoritmos de similitud entre series temporales, con análisis de complejidad y UI interactiva.

#### 2.1 Distancia Euclidiana — `src/services/similarity/euclidean.py`

- **Fórmula**: d(x, y) = √(Σ(xᵢ - yᵢ)²)
- **Aplicación**: Precios normalizados o retornos diarios
- **Complejidad**: O(n) donde n = longitud de las series
- **Espacial**: O(1) — solo acumulador

#### 2.2 Correlación de Pearson — `src/services/similarity/pearson.py`

- **Fórmula**: r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² · Σ(yᵢ - ȳ)²)
- **Interpretación**: r ∈ [-1, 1]; 1 = correlación perfecta, 0 = sin relación, -1 = correlación inversa
- **Complejidad**: O(n) — una pasada para medias, otra para covarianza y varianzas

#### 2.3 Dynamic Time Warping (DTW) — `src/services/similarity/dtw.py`

- **Qué**: Compara secuencias que pueden diferir en velocidad o fase (permite "warping" no lineal del eje temporal)
- **Algoritmo**: Programación dinámica — matriz de distancia acumulada
- **Complejidad**: O(n × m) donde n, m = longitudes de las series
- **Optimización**: Constraint de Sakoe-Chiba (banda de warping) para limitar a O(n × w) donde w = ancho de banda
- **Nota**: Debe implementarse manualmente, sin librerías

#### 2.4 Similitud por Coseno — `src/services/similarity/cosine.py`

- **Fórmula**: cos(θ) = (x · y) / (||x|| · ||y||)
- **Aplicación**: Vectores de retornos diarios
- **Complejidad**: O(n) — producto punto + normas

#### 2.5 Agregador — `src/services/similarity/__init__.py`

- Clase `SimilarityAnalyzer` que calcula los 4 métodos y retorna resultados estructurados
- Endpoint `GET /api/similarity?symbol1=VOO&symbol2=SPY`

#### 2.6 Frontend — `src/api/templates/pages/similarity.html`

- Selector de Activo 1 y Activo 2 (dropdown con los 20 activos)
- Botón "Calcular Similitud"
- Gráfica superpuesta de precios históricos (Chart.js)
- Tabla de resultados con los 4 algoritmos
- Para cada método: fórmula matemática, descripción, complejidad O(·)
- **REST**: `GET /api/similarity?s1=VOO&s2=SPY`

---

### Fase 3: Patrones y Volatilidad (Req 3)

**Objetivo**: Detección de patrones mediante ventanas deslizantes y clasificación de riesgo por volatilidad.

#### 3.1 Ventana Deslizante — `src/services/patterns/sliding_window.py`

**Patrón 1: Días Consecutivos al Alza**
- **Definición**: Secuencia de N días donde close > close anterior
- **Algoritmo**: Ventana deslizante de tamaño N, O(n × N) naive, O(n) optimizado con contador acumulado
- **Parámetro configurable**: N (default 3)

**Patrón 2: "Gap Up"**
- **Definición**: Día donde open > prev_close × (1 + umbral), es decir, apertura significativamente superior al cierre anterior
- **Umbral**: Configurable (default 2%)
- **Algoritmo**: O(n) comparando cada día contra el anterior

**Funcionalidad**:
- Detectar frecuencia de patrones en todo el historial
- Agrupar por año para análisis temporal
- Tabla de ocurrencias por año y activo

#### 3.2 Volatilidad y Riesgo — `src/services/patterns/volatility.py`

**Métricas**:
- **Desviación estándar de retornos**: σ = √(Σ(rᵢ - r̄)² / (n-1)), O(n)
- **Volatilidad histórica anualizada**: σ_anual = σ_diaria × √252, O(n)
- **Retorno diario**: rᵢ = (closeᵢ - closeᵢ₋₁) / closeᵢ₋₁, O(n)

**Clasificación de Riesgo**:
| Categoría | Volatilidad Anualizada | Color |
|-----------|----------------------|-------|
| Conservador | < 15% | Verde |
| Moderado | 15% – 30% | Amarillo |
| Agresivo | > 30% | Rojo |

**Salida**: Listado completo de activos ordenados por volatilidad ascendente

#### 3.3 Endpoints API

- `GET /api/patterns?symbol=VOO&pattern=consecutive_up&n=3` — Frecuencia del patrón
- `GET /api/volatility/ranking` — Ranking de volatilidad de todos los activos
- `GET /api/volatility?symbol=VOO` — Métricas individuales

#### 3.4 Frontend — `src/api/templates/pages/patterns.html`

- Dropdown de activo
- Selector de patrón (Consecutive Up / Gap Up)
- Tabla de frecuencias por año
- Gráfica de barras de ocurrencias anuales (Chart.js)

#### 3.5 Frontend — `src/api/templates/pages/risk.html`

- Tabla ranking completa con colores por categoría
- Barra de progreso visual para cada activo
- Promedio del portafolio

---

### Fase 4: Dashboard Visual (Req 4)

**Objetivo**: Visualizaciones clave + exportación PDF.

#### 4.1 Matriz de Correlación (Heatmap)

- **Backend**: Calcular matriz de Pearson entre todos los pares de activos, O(a² × n)
- **Frontend**: Chart.js heatmap (o tabla con gradiente de color)
- Endpoint: `GET /api/correlation-matrix`

#### 4.2 Candlestick + Medias Móviles

- **Candlestick**: Datos OHLC por activo
- **Medias Móviles Simples (SMA)**:
  - SMA-20 (mensual aprox): O(n)
  - SMA-50 (trimestral aprox): O(n)
  - Implementación manual con ventana deslizante acumulativa
- **Frontend**: Chart.js candlestick plugin
- Endpoint: `GET /api/candlestick?symbol=VOO&sma=20,50`

#### 4.3 Reporte PDF — `src/services/reporting/pdf_report.py`

**Secciones del PDF**:
1. Portada: Universidad, curso, título, fecha
2. Resumen del portafolio: activos, rango de fechas, estadísticas
3. Matriz de Correlación (imagen generada con matplotlib)
4. Tabla de Similitud (mejores pares)
5. Ranking de Riesgo (tabla completa)
6. Candlestick del activo principal (imagen matplotlib)
7. Análisis de Patrones (tabla resumen)

**Biblioteca**: ReportLab para PDF + matplotlib para imágenes incrustadas
Endpoint: `GET /api/report/download` → descarga PDF

#### 4.4 Frontend — `src/api/templates/pages/dashboard.html`

- Heatmap de correlación (matriz visual)
- Selector de activo → candlestick interactivo con SMA-20 / SMA-50 toggle
- Botón "Exportar Reporte PDF"
- Cards resumen: total activos, rango fechas, activo más volátil, activo menos volátil

---

### Fase 5: Despliegue y Documentación (Req 5)

#### 5.1 Refactorización API

- Separar rutas en Blueprints de Flask
- `src/api/routes/__init__.py` — registro centralizado
- Mantener compatibilidad con Docker

#### 5.2 Tests Unitarios — `tests/`

| Archivo | Cobertura |
|---------|-----------|
| `test_similarity.py` | 4 algoritmos de similitud, SimilarityAnalyzer, matriz de correlación |
| `test_patterns.py` | Ventana deslizante, gap up, volatilidad, clasificación de riesgo, ranking |
| `test_dashboard.py` | SMA con diferentes ventanas, casos borde (None, vacío) |
| `test_sorting.py` | Algoritmos de ordenamiento (TimSort, QuickSort, TreeSort, HeapSort, etc.) |

#### 5.3 Documentación

- **`docs/Diseno.md`**: Actualizar con:
  - Arquitectura completa del sistema
  - Diagrama de componentes
  - Descripción detallada de cada requerimiento
  - Análisis de complejidad de cada algoritmo implementado
  - Decisiones de diseño justificadas
  - Declaración de uso de IA

#### 5.4 Declaración de IA

Documentar explícitamente:
- Herramientas utilizadas (CLI de Claude)
- Alcance del uso (planificación, generación de código base, resolución de problemas)
- Qué NO fue generado por IA (diseño algorítmico, análisis de complejidad, fundamentación matemática)

#### 5.5 Reproducibilidad

Verificación final:
```
git clone <repo>
task install
task run       # Pipeline completo
task api       # Servidor web
```

---

## 4. Diseño del Frontend

### Navegación

Barra lateral izquierda fija (responsive) con enlaces:

```
[ Logo / Título ]
─────────────────
  Inicio
  Similitud
  Patrones
  Riesgo
  Dashboard
  API Docs
─────────────────
```

### Página de Inicio (`index.html`)

```
┌──────────────────────────────────────────────────────┐
│  📊 Investment Algorithm Dashboard                    │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │
│  │ 20       │  │ 5+ años  │  │ 4 sim.   │  │ PDF  │ │
│  │ Activos  │  │Historial │  │Algoritmos│  │Report│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────┘ │
│                                                       │
│  Tabla rápida: Activo | Precio | Volatilidad | Riesgo │
│  ─────────────────────────────────────────────────── │
│  VOO      | $450  | 18%       | Moderado             │
│  ECOPETROL| $2500 | 35%       | Agresivo             │
│  ...                                                    │
└──────────────────────────────────────────────────────┘
```

### Página de Similitud (`similarity.html`)

```
┌──────────────────────────────────────────────────────┐
│  Análisis de Similitud                                │
│                                                       │
│  Activo 1: [VOO ▾]    Activo 2: [SPY ▾]  [Calcular] │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │  Gráfica de Precios Superpuestos (Chart.js)   │    │
│  │  ─────────────────────────────────────────    │    │
│  │  📈 VOO ──  📈 SPY ──                        │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  Resultados:                                          │
│  ┌──────────────┬──────────┬──────────────────────┐  │
│  │ Algoritmo    │ Valor    │ Complejidad          │  │
│  ├──────────────┼──────────┼──────────────────────┤  │
│  │ Euclidiana   │ 12.45    │ O(n)                 │  │
│  │ Pearson      │ 0.98     │ O(n)                 │  │
│  │ DTW          │ 8.32     │ O(n×m)               │  │
│  │ Coseno       │ 0.99     │ O(n)                 │  │
│  └──────────────┴──────────┴──────────────────────┘  │
│                                                       │
│  📘 Explicación Matemática (expandible)               │
│  ▼ Distancia Euclidiana                               │
│    d(x,y) = √(Σ(xᵢ - yᵢ)²)                          │
│    La distancia euclidiana mide...                    │
└──────────────────────────────────────────────────────┘
```

### Página de Patrones (`patterns.html`)

```
┌──────────────────────────────────────────────────────┐
│  Detección de Patrones                               │
│                                                       │
│  Activo: [VOO ▾]    Patrón: [Consecutive Up ▾]       │
│  Ventana: [3 ▾] días     [Buscar]                    │
│                                                       │
│  Frecuencia por año:                                  │
│  ┌──────┬────────────┐  ┌──────────────────────┐    │
│  │ Año  │ Ocurrencias│  │  📊 Bar Chart         │    │
│  ├──────┼────────────┤  │                        │    │
│  │ 2021 │ 45         │  │  ████████              │    │
│  │ 2022 │ 38         │  │  ██████                │    │
│  │ 2023 │ 52         │  │  ██████████            │    │
│  │ 2024 │ 41         │  │  ███████               │    │
│  │ 2025 │ 36         │  │  █████                 │    │
│  └──────┴────────────┘  └──────────────────────┘    │
│                                                       │
│  Últimas ocurrencias: 2025-03-15, 2025-02-28, ...    │
└──────────────────────────────────────────────────────┘
```

### Página de Riesgo (`risk.html`)

```
┌──────────────────────────────────────────────────────┐
│  Ranking de Riesgo (Volatilidad)                      │
│                                                       │
│  ┌────────┬──────────┬────────┬──────────────────┐   │
│  │ #      │ Activo   │ Vol.   │ Categoría        │   │
│  │        │          │ Anual  │                  │   │
│  ├────────┼──────────┼────────┼──────────────────┤   │
│  │ 1      │ BND      │  8.2%  │ 🟢 Conservador   │   │
│  │ 2      │ TLT      │ 12.1%  │ 🟢 Conservador   │   │
│  │ 3      │ VOO      │ 18.5%  │ 🟡 Moderado      │   │
│  │ ...    │ ...      │ ...    │ ...              │   │
│  │ 20     │ XLK      │ 32.4%  │ 🔴 Agresivo      │   │
│  └────────┴──────────┴────────┴──────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### Dashboard (`dashboard.html`)

```
┌──────────────────────────────────────────────────────┐
│  Dashboard Completo                      [📥 PDF]    │
│                                                       │
│  ┌── Matriz de Correlación ─────────────────┐        │
│  │  Heatmap (20×20) con gradiente de color   │        │
│  │  -1 (rojo) ... 0 (blanco) ... +1 (azul)  │        │
│  └───────────────────────────────────────────┘        │
│                                                       │
│  ┌── Candlestick ──────────────────────────┐  ┌──┐   │
│  │  [VOO ▾]  [SMA-20 ✓] [SMA-50 ☐]        │  │  │   │
│  │  📊 Candle + medias móviles             │  │  │   │
│  └─────────────────────────────────────────┘  └──┘   │
│  Resumen:                                            │
│  Activo más correlacionado: VOO-SPY (0.99)           │
│  Activo menos correlacionado: BND-XLF (-0.45)        │
└──────────────────────────────────────────────────────┘
```

---

## 5. Restricciones del Proyecto

### ❌ Prohibido
- **yfinance**, **pandas_datareader** o librerías que encapsulen la descarga en una llamada
- Librerías que implementen similitud/DTW/clustering en una sola función (scikit-learn, scipy.spatial.distance)
- Datasets estáticos descargados manualmente
- ML para reemplazar algoritmos clásicos
- Funciones de alto nivel que encapsulen los algoritmos solicitados

### ✅ Permitido
- `requests` para HTTP directo (ya implementado)
- `csv`, `json` para parseo manual
- `matplotlib` para gráficos estáticos
- `numpy` para operaciones matemáticas básicas (sumatorias, promedios, raíces)
- Chart.js en frontend (libería de visualización)
- ReportLab para generación de PDF
- `pytest` para testing
- `ruff` para linting

---

## 6. Requisitos de Instalación

```txt
requests==2.31.0       # Peticiones HTTP (permitida)
matplotlib==3.8.0      # Gráficos estáticos
pandas==2.1.0          # Solo para estructuras básicas (NO para similitud)
numpy==1.26.0          # Solo operaciones matemáticas básicas
flask==3.0.0           # Servidor web
pytest==7.4.0          # Tests
ruff==0.1.0            # Linter
beautifulsoup4==4.12.0 # Scraping (fallback)
reportlab==4.1.0       # Generación de PDF
```

---

## 7. Tareas Detalladas por Fase

### Fase 1: Mejora ETL (Req 1)

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 1.1 | Implementar alineación de calendarios bursátiles | `src/etl/unifier.py` | Alta |
| 1.2 | Agregar detección IQR de anomalías | `src/etl/cleaner.py` | Media |
| 1.3 | Mejorar documentación de interpolación | `src/etl/cleaner.py` | Alta |
| 1.4 | Verificar reproducibilidad del pipeline | `src/services/main_runner.py` | Alta |

### Fase 2: Similitud (Req 2)

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 2.1 | Implementar Distancia Euclidiana | `src/services/similarity/euclidean.py` | Alta |
| 2.2 | Implementar Correlación de Pearson | `src/services/similarity/pearson.py` | Alta |
| 2.3 | Implementar DTW | `src/services/similarity/dtw.py` | Alta |
| 2.4 | Implementar Similitud por Coseno | `src/services/similarity/cosine.py` | Alta |
| 2.5 | Crear SimilarityAnalyzer (agregador) | `src/services/similarity/__init__.py` | Alta |
| 2.6 | Endpoint REST de similitud | `src/api/routes/similarity.py` | Alta |
| 2.7 | Template HTML de similitud | `src/api/templates/pages/similarity.html` | Media |
| 2.8 | Tests de algoritmos de similitud | `tests/test_similarity.py` | Media |

### Fase 3: Patrones y Volatilidad (Req 3)

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 3.1 | Implementar ventana deslizante (patrón consecutive up) | `src/services/patterns/sliding_window.py` | Alta |
| 3.2 | Implementar patrón Gap Up | `src/services/patterns/sliding_window.py` | Alta |
| 3.3 | Calcular desviación estándar y volatilidad | `src/services/patterns/volatility.py` | Alta |
| 3.4 | Clasificación de riesgo | `src/services/patterns/volatility.py` | Alta |
| 3.5 | Endpoints de patrones y volatilidad | `src/api/routes/patterns.py` | Alta |
| 3.6 | Template HTML de patrones y riesgo | `src/api/templates/pages/` | Media |
| 3.7 | Tests de patrones y volatilidad | `tests/test_patterns.py`, `tests/test_volatility.py` | Media |

### Fase 4: Dashboard y PDF (Req 4)

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 4.1 | Calcular matriz de correlación | `src/api/routes/dashboard.py` | Alta |
| 4.2 | Implementar SMA (20 y 50) | `src/api/routes/dashboard.py` | Alta |
| 4.3 | Endpoint de candlestick | `src/api/routes/dashboard.py` | Alta |
| 4.4 | Template HTML del dashboard | `src/api/templates/pages/dashboard.html` | Alta |
| 4.5 | Generación de reporte PDF | `src/services/reporting/pdf_report.py` | Alta |
| 4.6 | Endpoint de descarga PDF | `src/api/routes/reports.py` | Alta |
| 4.7 | Lógica JavaScript de Chart.js | `src/static/js/charts.js` | Media |
| 4.8 | Estilos CSS | `src/static/css/style.css` | Media |

### Fase 5: Despliegue y Documentación (Req 5)

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 5.1 | Refactorizar API con Blueprints | `src/api/gateway.py`, `src/api/routes/` | Alta |
| 5.2 | Escribir tests unitarios | `tests/` | Alta |
| 5.3 | Actualizar documento de diseño | `docs/Diseno.md` | Alta |
| 5.4 | Declaración de uso de IA | `docs/Diseno.md` | Alta |
| 5.5 | Verificar reproducibilidad | — | Alta |
| 5.6 | Actualizar README.md | `README.md` | Media |
| 5.7 | Verificar linting (ruff) | — | Media |

---

## 8. Análisis de Complejidad General

| Componente | Algoritmo | Complejidad Temporal | Complejidad Espacial |
|------------|-----------|---------------------|---------------------|
| ETL - Descarga | HTTP requests paralelizados | O(a) requests | O(n × a) datos |
| ETL - Duplicados | HashSet | O(n) | O(n) |
| ETL - Outliers | Z-Score / IQR | O(n) / O(n log n) | O(1) / O(n) |
| ETL - Interpolación | Lineal | O(n) | O(n) |
| ETL - Unificación | Sort + Merge | O(n log n) | O(n) |
| Similitud - Euclidiana | Suma diferencias² | O(n) | O(1) |
| Similitud - Pearson | Covarianza / Varianza | O(n) | O(1) |
| Similitud - DTW | Programación Dinámica | O(n × m) | O(n × m) |
| Similitud - Coseno | Producto punto | O(n) | O(1) |
| Patrones - Sliding Window | Ventana deslizante | O(n) | O(1) |
| Volatilidad | Desviación estándar | O(n) | O(1) |
| Correlación (matriz) | Pearson por pares | O(a² × n) | O(a²) |
| SMA | Ventana acumulativa | O(n) | O(1) |
| Reporte PDF | Generación | O(n) | O(n) |

---

## 9. Documentación Requerida

### Documento de Diseño (`docs/Diseno.md`)

Debe contener:
1. **Introducción**: contexto, objetivos, alcance
2. **Arquitectura del Sistema**: diagrama de componentes, descripción de capas
3. **Requerimiento 1 — ETL**:
   - Descripción del proceso de extracción (HTTP directo a Yahoo Finance)
   - Algoritmos de limpieza (HashSet, Z-Score, IQR, interpolación lineal)
   - Justificación de cada técnica con análisis de complejidad
   - Manejo de calendarios bursátiles
4. **Requerimiento 2 — Similitud**:
   - Fórmula matemática de cada algoritmo
   - Pseudocódigo o descripción algorítmica detallada
   - Análisis de complejidad Big-O
   - Interpretación de resultados
5. **Requerimiento 3 — Patrones y Volatilidad**:
   - Formalización de patrones
   - Algoritmo de ventana deslizante
   - Cálculo de volatilidad
   - Clasificación de riesgo
6. **Requerimiento 4 — Dashboard**:
   - Visualizaciones implementadas
   - Algoritmos de correlación y SMA
   - Estructura del reporte PDF
7. **Requerimiento 5 — Despliegue**:
   - Instrucciones de instalación
   - Configuración Docker
   - Endpoints API documentados
8. **Análisis de Complejidad Consolidado**: tabla comparativa
9. **Declaración de Uso de IA**:
   - Herramientas utilizadas
   - Alcance del uso
   - Limitaciones y responsabilidades

---

## 10. Criterios de Éxito

- [x] Pipeline ETL automatizado y reproducible (20+ activos, 5+ años)
- [x] 4 algoritmos de similitud implementados manualmente con análisis Big-O
- [x] 2 patrones detectados mediante ventana deslizante
- [x] Ranking de riesgo por volatilidad con 3 categorías
- [x] Dashboard web con heatmap de correlación + candlestick + SMA
- [x] Reporte PDF exportable
- [x] Tests unitarios para cada nuevo módulo
- [x] Documento de diseño completo
- [x] Sin uso de librerías prohibidas
- [x] Aplicación web desplegable con Docker
