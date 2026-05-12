# Análisis Algorítmico — Sistema de Análisis Algorítmico Financiero

**Universidad del Quindío** — Programa de Ingeniería de Sistemas y Computación
**Curso**: Análisis de Algoritmos — 2026-1

---

## 1. Análisis de Complejidad por Módulo

### 1.1 Módulo ETL

#### `src/etl/cleaner.py` — DataCleaner

| Método | Tiempo | Espacio | Explicación |
|--------|--------|---------|-------------|
| `detect_missing_values` | O(n × f) | O(k) | n = registros, f = campos (5: OHLCV). Escanea cada campo de cada registro. k = índices faltantes |
| `detect_duplicates` | O(n) | O(n) | HashSet de tuplas (date, symbol). Una pasada + almacenamiento de claves únicas |
| `detect_outliers_zscore` | O(n) | O(1) | Dos pasadas: media/stdev + detección. Sin almacenamiento auxiliar |
| `detect_outliers_iqr` | O(n log n) | O(n) | Ordenamiento Timsort (Python) domina. Almacena lista de tuplas (idx, valor) |
| `interpolate_missing` | **O(n)** | O(n) | *Antes: O(n²)* — escaneo lineal por cada índice faltante. *Ahora:* precomputación de `prev_valid` y `next_valid` en dos pasadas O(n), luego O(1) por índice faltante |
| `interpolate_forward_fill` | O(n) | O(n) | Una pasada hacia adelante con `last_valid`. Copia defensiva del dataset |
| `interpolate_backward_fill` | O(n) | O(n) | Una pasada hacia atrás con `next_valid`. Análogo a forward-fill |
| `remove_duplicates` | O(n) | O(n) | Filtro por comprensión con HashSet O(1) por consulta |
| `clean_records` (pipeline) | **O(n log n)** | O(n) | Dominado por IQR. El resto de operaciones son O(n) |

**Cuello de botella eliminado**: `interpolate_missing` pasó de O(k × n) ≈ O(n²) a O(n) mediante precomputación de vecinos. Para n = 1250 registros con k = 100 índices faltantes, el costo se reduce de ~125,000 iteraciones a ~2,500.

#### `src/etl/unifier.py` — DataUnifier

| Método | Tiempo | Espacio | Explicación |
|--------|--------|---------|-------------|
| `_market_trading_days` | O(d) | O(d) | d = días en rango. Itera día a día verificando si es hábil |
| `_precompute_trading_days` | O(d_bvc + d_nyse) | O(d_bvc + d_nyse) | Memoiza los conjuntos de días hábiles, evitando recalcular por símbolo |
| `validate_record` | O(f) | O(1) | f = 7 campos requeridos. O(1) espacio, sin asignaciones |
| `detect_calendar_gaps` | O(s × d + n) | O(s × d + n) | Por cada símbolo, calcula días esperados vs existentes |
| `align_calendars` | **O(s × d + n)** | O(s × d + n) | s = símbolos (20), d = días (~1250). Antes llamaba `_market_trading_days` 20+ veces; ahora usa caché con 2 llamadas |
| `unify_datasets` | **O(n log n)** | O(n) | Ordenamiento Timsort domina. Filtra registros válidos O(n) + sort O(n log n) |
| `load_from_csv` | O(n) | O(n) | Itera filas del CSV, parsea tipos, valida. Maneja excepciones por fila |
| `save_to_csv` | O(n) | O(1) | Escritura secuencial. Sin almacenamiento adicional |
| `generate_statistics` | O(n) | O(s) | Una pasada con acumuladores. s = símbolos únicos |

**Optimización aplicada**: Se eliminaron ~18 llamadas redundantes a `_market_trading_days` mediante `_precompute_trading_days`. Antes se llamaba 2 veces para los sets + 1 vez por símbolo (20). Ahora solo 2 veces.

#### `src/etl/fetcher.py` — Fetcher (versión reescrita)

| Componente | Tiempo | Explicación |
|------------|--------|-------------|
| Circuit Breaker | O(1) | Contador + timestamp de reset. Sin iteraciones |
| Backoff exponencial con jitter | O(1) | Fórmula: min(base × 2^attempt + random(0, jitter), max_delay) |
| Plan B (BeautifulSoup) | O(p) | p = peticiones de scraping. Rate limiting de 2s entre requests |
| Pool de conexiones | O(1) | requests.Session reutiliza conexiones TCP (keep-alive) |
| User-Agent rotatorio | O(1) | Selección aleatoria de lista predefinida |
| `fetch_with_fallback` | O(r + p) | r = reintentos HTTP (5), p = scraping (solo si HTTP falla) |

### 1.2 Módulo de Similitud

#### `src/services/similarity/euclidean.py`

```
d(x, y) = √( (1/n) × Σ(xᵢ - yᵢ)² )
```

- **Tiempo**: O(n) — una pasada para calcular diferencias al cuadrado y acumular
- **Espacio**: O(1) — solo un acumulador (`sum_squared_diff`)
- **Operaciones por iteración**: 1 resta, 1 multiplicación, 1 suma
- **Caso base**: Empty series → retorno inmediato O(1)
- **Edge case**: NaN → `math.isnan` + `continue`, salta el par inválido

#### `src/services/similarity/pearson.py`

```
r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² · Σ(yᵢ - ȳ)²)
```

- **Tiempo**: O(n) — filtro NaN O(n) + media O(n) + covarianza/varianzas O(n) = 3 pasadas
- **Espacio**: O(n) — dos listas auxiliares `filtered_s1` y `filtered_s2` (nuevo, para NaN filtering)
- **Operaciones por iteración** (segunda pasada): 2 restas, 1 multiplicación, 1 suma (cov), 2 multiplicaciones, 2 sumas (vars)
- **Caso base**: n < 3 → retorno inmediato con error
- **Edge case**: varianza cero → correlación = 0.0 (evita división por cero)

**Nota de optimización**: Las 3 pasadas son O(n) cada una. Se podrían fusionar en 2 pasadas (media + cov/var simultánea) pero a costa de legibilidad. En la práctica, para n = 1250, 3 pasadas vs 2 es diferencia despreciable (~0.01ms).

#### `src/services/similarity/cosine.py`

```
cos(θ) = (x · y) / (||x|| · ||y||)
```

- **Tiempo**: O(n) — una pasada para producto punto y normas
- **Espacio**: O(1) — 3 acumuladores (dot_product, norm1, norm2)
- **Operaciones por iteración**: 2 multiplicaciones, 3 sumas
- **Caso base**: Series vacías → retorno inmediato O(1)
- **Edge case**: Norma cero → similarity = 0.0, angle = 90°
- **Clamping**: `max(-1.0, min(1.0, similarity))` + clamping redundante para acos

#### `src/services/similarity/dtw.py`

```
D[i][j] = |xᵢ - yⱼ| + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
```

**Modo matriz completa** (`full_matrix=True`):
- **Tiempo**: O(n × m) sin ventana, O(n × w) con Sakoe-Chiba
- **Espacio**: O(n × m) — matriz completa (n+1) × (m+1)
- **Memoria**: Para n = m = 1250, ~12.5 MB (1251² × 8 bytes). Para n = m = 10000, ~800 MB (riesgo OOM)
- **Path de warping**: O(n + m) — reconstrucción del camino óptimo

**Modo memoria reducida** (`full_matrix=False`):
- **Tiempo**: O(n × m) u O(n × w) — misma complejidad
- **Espacio**: O(m) — solo 2 filas (prev_row + curr_row), cada una de tamaño m+1
- **Memoria**: Para n = m = 1250, ~20 KB (2 × 1251 × 8 bytes)
- **Limitación**: No reconstruye el camino de warping; solo calcula la distancia

**Optimización Sakoe-Chiba**: Restringe warping a banda de ancho w:
- w típico = 10-20% de n. Para n = 1250, w = 125-250
- Complejidad se reduce de O(n²) a O(n × w), factor de mejora de 5-10x
- Sin ventana: 1,562,500 celdas. Con w=125: 156,250 celdas

#### `src/services/similarity/__init__.py` — SimilarityAnalyzer

| Método | Tiempo | Espacio |
|--------|--------|---------|
| `_extract_series` | O(n₁ + n₂) | O(min(n₁, n₂)) |
| `_returns` | O(n) | O(n) |
| `compare` 1-par | O(4n) = O(n) | O(n) |
| `compute_correlation_matrix` | **O(s² × n)** | O(s²) |

**Matriz de correlación**: Para s = 20, n = 1250:
- Llamadas a Pearson: s(s-1)/2 = 190
- Operaciones totales: ~190 × 1250 × 3 = ~712,500 operaciones de punto flotante
- Matriz resultante: 20 × 20 = 400 flotantes (~3.2 KB)

### 1.3 Módulo de Patrones

#### `src/services/patterns/sliding_window.py`

**Consecutive Up**:
```
contador = 0
para cada i en 1..n-1:
    si close[i] > close[i-1]: contador++
    sino: contador = 0
    si contador >= min_days: registrar
```
- **Tiempo**: O(n) — una pasada con contador acumulado
- **Espacio**: O(k) — k = ocurrencias detectadas (para almacenar fechas)
- **Operaciones por iteración**: 1 comparación, 1 incremento/reset condicional

**Gap Up**:
```
para cada i en 1..n-1:
    gap_pct = (open[i] - close[i-1]) / close[i-1] × 100
    si gap_pct > threshold: registrar
```
- **Tiempo**: O(n) — una pasada
- **Espacio**: O(k) — k = gaps detectados
- **Operaciones por iteración**: 1 resta, 1 división, 1 multiplicación, 1 comparación

#### `src/services/patterns/volatility.py`

| Función | Tiempo | Espacio | Fórmula |
|---------|--------|---------|---------|
| `daily_returns` | O(n) | O(n) | rᵢ = (pᵢ - pᵢ₋₁) / pᵢ₋₁ |
| `standard_deviation` | O(n) | O(1) | σ = √(Σ(rᵢ - r̄)² / (n-1)) |
| `annualized_volatility` | O(1) | O(1) | σ_anual = σ_diaria × √252 |
| `classify_risk` | O(1) | O(1) | Rangos: <15%, 15-30%, ≥30% |
| `VolatilityAnalyzer.analyze` | O(n) | O(n) | Retornos + desviación + clasificación |
| `VolatilityAnalyzer.ranking` | **O(s × n + s log s)** | O(s) | Analiza cada símbolo + ordena por volatilidad |

### 1.4 Módulo de Reportes Técnicos

#### `src/services/reporting/technical.py`

**Simple Moving Average (SMA)**:
```
SMA[i] = (cumsum[i] - cumsum[i - window]) / window
```
- **Tiempo**: O(n) — suma acumulativa en una pasada + consultas O(1) por posición
- **Espacio**: O(n) — almacena el array de salida
- **Versión ingenua** (sin cumsum): O(n × w) para w = 20 → 20x más lento en el peor caso

#### `src/services/reporting/pdf_report.py`

- **Tiempo**: O(n + s²) — datos (n) + heatmap matplotlib (s²)
- **Cuello de botella**: matplotlib rendering (no optimizable desde Python puro)

### 1.5 Módulo API (Flask)

- **Enrutamiento**: O(1) por request (Werkzeug routing tree)
- **Templates Jinja2**: O(t) donde t = tamaño del template (compilado a bytecode, cacheado)
- **Chart.js**: Renderizado en cliente (navegador), sin carga en servidor

---

## 2. Análisis de Memoria Detallado

### 2.1 Perfil de Memoria por Pipeline

| Etapa | Estructura | Tamaño típico | Pico |
|-------|-----------|---------------|------|
| Fetch | Lista de registros OHLC por símbolo | 20 × 1250 × ~200B ≈ 5 MB | 5 MB |
| Cleaner (copia defensiva) | Lista de dicts copiados | ~5 MB × 2 = 10 MB | 10 MB |
| Cleaner (interpolate_missing) | prev_valid/next_valid arrays | 2 × 1250 × 8B ≈ 20 KB | 10 MB |
| Unifier (align_calendars) | Dict de símbolos + registros None | ~25,000 registros × 200B ≈ 5 MB | 12 MB |
| SimilarityAnalyzer (matriz) | Matriz de correlación 20×20 | 400 × 8B ≈ 3.2 KB | 12 MB |
| DTW matriz completa | (n+1) × (m+1) × 8B | ~12.5 MB (1250×1250) | 24.5 MB |
| DTW memoria reducida | 2 × (m+1) × 8B | ~20 KB | 12 MB |
| PDF (matplotlib heatmap) | Figura PNG en memoria | ~500 KB | 12.5 MB |

### 2.2 Overhead de Python

Cada registro es un `dict` con 7 campos:
- `dict` overhead: ~240 bytes (32 bytes × 7 punteros + tabla hash)
- `float` objects: 7 × 24 bytes = 168 bytes
- `str` objects (date, symbol): longitud variable (~20 chars) + objeto str (~50 bytes c/u)
- **Total por registro**: ~500-600 bytes

Para 25,000 registros (pico): ~12-15 MB solo en datos Python.

### 2.3 Optimización de Memoria en DTW

La opción `full_matrix=False` reduce la memoria de O(n×m) a O(m):

| n | m | full_matrix=True | full_matrix=False |
|---|---|---|---|
| 1,250 | 1,250 | ~12.5 MB | ~20 KB |
| 5,000 | 5,000 | ~200 MB | ~80 KB |
| 10,000 | 10,000 | ~800 MB | ~160 KB |

Para el dataset actual (n ≤ 1250), la matriz completa es aceptable (~12.5 MB). Para escalar a 10,000+ días, el modo reducido es esencial.

---

## 3. Cuellos de Botella Específicos de Python

### 3.1 GIL (Global Interpreter Lock)

El GIL impide la ejecución paralela de hilos Python. Impacto en el sistema:

| Operación | ¿Afectada por GIL? | Mitigación |
|-----------|-------------------|------------|
| Cálculos CPU-bound (DTW, Pearson, etc.) | **Sí** | No aplica (todos los algoritmos son single-thread) |
| I/O de red (fetcher) | **No** | `requests` libera el GIL durante espera de red |
| I/O de disco (CSV, PDF) | **No** | Operaciones de archivo liberan el GIL |
| matplotlib rendering | **Sí** | Se ejecuta una sola vez al generar PDF |

**Decisión**: Todos los algoritmos se ejecutan secuencialmente. No se justifica multiprocesamiento porque:
- El pipeline completo toma < 5 segundos para 20 activos
- `multiprocessing` añadiría overhead de serialización de datos
- La API sirve requests individuales (no procesamiento batch)

### 3.2 Listas vs Deques

| Operación | List (array dinámico) | Deque (doble cola) |
|-----------|----------------------|-------------------|
| `append` al final | O(1) amortizado | O(1) |
| `pop` del final | O(1) | O(1) |
| `pop(0)` del inicio | **O(n)** | O(1) |
| `insert(0, x)` | **O(n)** | O(1) |
| Acceso por índice | **O(1)** | O(n) |
| Iteración | O(n) | O(n) |

**Uso en el sistema**:
- Todos los algoritmos iteran secuencialmente (acceso O(1) por índice con listas)
- No se realizan inserciones/eliminaciones al inicio
- **Decisión correcta**: `list` es la estructura óptima para este patrón de acceso

### 3.3 Comprensiones de Listas vs Bucles For

```python
# Comprensión (C-optimizado)
values = [r[field] for r in records if r.get(field) is not None]

# Bucle for (bytecode Python)
values = []
for r in records:
    if r.get(field) is not None:
        values.append(r[field])
```

**Rendimiento**: Las comprensiones son ~1.5-2x más rápidas porque ejecutan en el bucle C de Python, no en bytecode. Se usan en:
- `detect_outliers_zscore` (línea 114)
- `detect_outliers_iqr` (línea 160-161)
- `remove_duplicates` (línea 361)
- `generate_statistics` (líneas 370-374)

### 3.4 Costo de las Llamadas a Función

Python tiene overhead ~50-100 ns por llamada a función. En bucles cerrados como DTW:
```python
# Por cada celda de la matriz
cost = abs(series1[i - 1] - series2[j - 1])  # ~100 ns
dtw_matrix[i][j] = cost + min(...)             # ~150 ns con 3 accesos
```

Para n = m = 1250: 1,562,500 celdas × ~250 ns ≈ **390 ms** solo en overhead de operaciones.

### 3.5 Manejo de Errores (try/except)

```python
# En load_from_csv (nuevo):
try:
    record = { ... float(row["open"]) ... }
except (ValueError, KeyError, TypeError):
    continue
```

`try/except` sin excepción tiene costo ~0. El costo solo se paga cuando ocurre el error (mecanismo de excepciones con tabla de jump). Para datos válidos (99.9% de los casos), el overhead es despreciable.

### 3.6 Hash de Strings

Las fechas como strings `"2024-01-01"` se usan como claves en diccionarios:
- `detect_duplicates`: tupla `(date, symbol)` como clave → hash de 2 strings
- `align_calendars`: `{r["date"]: r for r in sym_records}` → hash de fecha
- `detect_calendar_gaps`: `symbols_dates[sym].add(date)` → hash en set

El hashing de strings de 10 caracteres cuesta ~50-100 ns. Para 25,000 registros: ~2.5 ms. Despreciable.

---

## 4. Análisis de Algoritmo de Ordenamiento

Python usa **Timsort** (O(n log n) peor caso, O(n) mejor caso):

| Uso en el sistema | n | Mejor caso | Peor caso |
|-------------------|---|-----------|-----------|
| `align_calendars: sort` | 25,000 | O(n) si ya está ordenado | O(n log n) |
| `unify_datasets: sort` | 25,000 | O(n) | O(n log n) |
| `detect_outliers_iqr: sorted` | 1,250 | O(n log n) | O(n log n) |
| `detect_calendar_gaps: sorted` | 250 | O(n) | O(n log n) |

Timsort es **adaptativo**: detecta secuencias ya ordenadas (common en datos temporales), reduciendo el costo real.

---

## 5. Análisis de Amortización

### 5.1 Backoff Exponencial (fetcher)

```
tiempo_espera = min(base × 2^attempt + random(0, jitter), max_delay)
```

- Tasa de fallo ~p. Tiempo esperado por request: `Σ p^i × (2^i - 1) × base`
- Para p = 0.1 (10% de fallo), tiempo extra esperado: ~2.1s sobre 30s de timeout
- Para p = 0.5 (50% de fallo), tiempo extra esperado: ~21s (circuit breaker activa antes)

### 5.2 Circuit Breaker

```
umbral = 10 fallos consecutivos
reset_timeout = 60 segundos
```

- Bajo condiciones normales: nunca se activa
- Bajo fallo sostenido: falla rápido después de 10 intentos (evita 50+ intentos inútiles)
- Amortizado: reduce el tiempo de fallo de O(r × timeout) a O(umbral × timeout)

### 5.3 Crecimiento de Listas (append)

```python
records_copy = [r.copy() for r in records]
```

- `list.append()` tiene O(1) amortizado (redimensionamiento por factor 1.125)
- Para n = 1250: ~10-12 redimensionamientos
- Costo total de copia: O(n) + overhead de redimensionamiento O(log n)

---

## 6. Bottlenecks Identificados y Mitigados

### 6.1 BUG CORREGIDO: interpolate_missing O(n²) → O(n)

**Síntoma**: `interpolate_missing` escaneaba linealmente desde cada índice faltante hacia adelante y atrás buscando vecinos válidos. Para k índices faltantes, cada búsqueda recorría hasta n/2 posiciones promedio.

**Complejidad original**: O(k × n) ≈ O(n²) cuando k ≈ n/2

```
para cada idx en sorted(indices):           # O(k)
    para i en range(idx-1, -1, -1):         # O(n) en peor caso
        si i no en indices_set y válido:
            prev_idx = i; break
    para i en range(idx+1, len(records)):   # O(n) en peor caso
        si i no en indices_set y válido:
            next_idx = i; break
```

Para n = 1250, k = 600: ~750,000 iteraciones internas.

**Solución**: Precomputar `prev_valid[i]` = último índice válido antes de i, y `next_valid[i]` = siguiente índice válido después de i, en **dos pasadas O(n)**.

```
# Pasada 1: prev_valid
last_valid = None
para i en range(n):
    si i no en indices_set y records[i][field] != None:
        last_valid = i
    prev_valid[i] = last_valid

# Pasada 2: next_valid
next_seen = None
para i en range(n-1, -1, -1):
    si i no en indices_set y records[i][field] != None:
        next_seen = i
    next_valid[i] = next_seen

# Interpolación: O(1) por índice faltante
para idx en indices:
    p = prev_valid[idx]; n = next_valid[idx]
    records[idx] = (records[p] + records[n]) / 2
```

**Mejora**: De 750,000 iteraciones a ~2,500. Factor de mejora: ~300x para n = 1250.

### 6.2 Optimizado: Llamadas redundantes a _market_trading_days

**Antes**: `align_calendars` llamaba `_market_trading_days` 2 veces (BVC + NYSE sets) + 1 vez por cada uno de los 20 símbolos = 22 llamadas.

**Después**: `_precompute_trading_days` cachea los resultados. Solo 2 llamadas.

**Mejora**: 22x menos llamadas al generador de días hábiles.

### 6.3 Code smell corregido: import math inline

**Antes** en `cosine.py`:
```python
similarity = max(-1.0, min(1.0, similarity))
import math  # <-- inline import, code smell
angle_degrees = round(math.degrees(math.acos(similarity)), 4)
```

**Después**: `import math` al inicio del archivo. Además, clamping redundante para evitar `ValueError: math domain error` en `acos`.

### 6.4 Riesgo OOM mitigado: DTW full_matrix opcional

**Riesgo**: DTW sin límite para series de 10000+ días requiere ~800 MB de RAM.

**Mitigación**: Modo `full_matrix=False` usa solo 2 filas (~20 KB). El usuario puede optar por no reconstruir el path de warping cuando solo necesita la distancia.

---

## 7. Resumen de Complejidad Consolidado

| Componente | Tiempo | Espacio | ¿Optimizable? |
|------------|--------|---------|---------------|
| ETL - Fetch HTTP | O(a) | O(n × a) | Paralelizable con asyncio |
| ETL - Duplicados | O(n) | O(n) | No (necesita HashSet) |
| ETL - Outliers Z-Score | O(n) | O(1) | No |
| ETL - Outliers IQR | O(n log n) | O(n) | Sí (Quickselect O(n)) |
| ETL - Interpolación Lineal | **O(n)** ✅ | O(n) | No (antes era O(n²)) |
| ETL - Forward/Backward Fill | O(n) | O(n) | No |
| ETL - Alineación Calendarios | O(s × d) | O(d) | Caché implementado ✅ |
| Similitud - Euclidiana | O(n) | O(1) | No |
| Similitud - Pearson | O(n) | O(1) | No (O(n) con NaN filtering) |
| Similitud - DTW (completa) | O(n × m) | O(n × m) | Sí ✅ (opción memoria reducida) |
| Similitud - DTW (Sakoe-Chiba) | O(n × w) | O(w) | No |
| Similitud - Coseno | O(n) | O(1) | No |
| Matriz de Correlación | O(s² × n) | O(s²) | Sí (muestreo para s grande) |
| Patrones - Sliding Window | O(n) | O(1) | No |
| Volatilidad | O(n) | O(1) | No |
| SMA | O(n) | O(n) | No |
| Ranking de Riesgo | O(s × n + s log s) | O(s) | No |

✅ = optimización ya aplicada

---

## 8. Declaración de Uso de IA

Este análisis fue generado con asistencia de inteligencia artificial (Anthropic Claude vía opencode CLI) como herramienta de apoyo para:

- Verificación formal de complejidad Big-O
- Identificación de cuellos de botella en Python
- Sugerencias de optimización de memoria
- Documentación estructurada del análisis

El contenido técnico (fórmulas, medidas de complejidad, decisiones arquitectónicas) fue revisado y validado manualmente.

---

*Documento de análisis algorítmico — Curso de Análisis de Algoritmos — Universidad del Quindío — 2026-1*
