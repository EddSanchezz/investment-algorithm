# Documento de Diseño - Proyecto de Análisis de Algoritmos

## 1. Introducción

Este proyecto implementa un sistema de análisis de algoritmos de ordenamiento utilizando datos financieros reales. El objetivo es comparar el rendimiento de 12 algoritmos de ordenamiento mediante la medición de tiempo de ejecución y verificar la complejidad algorítmica teórica.

## 2. Arquitectura del Sistema

### 2.1 Estructura del Proyecto

```
src/
├── etl/
│   ├── fetcher.py        # Extracción de datos HTTP directo
│   ├── scraper.py        # Scraper alternativo
│   ├── cleaner.py        # Limpieza de datos
│   └── unifier.py        # Unificación de datasets
├── sorting/
│   ├── algorithms.py     # 12 algoritmos de ordenamiento
│   ├── comparator.py     # Comparador de rendimiento
│   └── visualizer.py     # Generación de gráficos
└── services/
    ├── volume_analyzer.py # Análisis de volumen
    └── main_runner.py    # Orquestador principal
```

### 2.2 Flujo de Ejecución

```
Extracción (fetcher) → Limpieza (cleaner) → Unificación (unifier)
         ↓
Ordenamiento (12 algoritmos) → Medición de tiempo
         ↓
Análisis de Volumen
         ↓
Generación de CSV y Gráficos
```

## 3. Proceso ETL - Extracción de Datos

### 3.1 Peticiones Explícitas a APIs Públicas

El proyecto utiliza Yahoo Finance API mediante HTTP directo (peticiones explícitas), cumpliendo con el requisito del documento de seguimiento de no usar librerías de alto nivel como yfinance.

#### Construcción de la consulta

La URL de la API se construye de la siguiente manera:

```
https://query1.finance.yahoo.com/v8/finance/chart/{SIMBOLO}?period1={TIMESTAMP_INICIO}&period2={TIMESTAMP_FIN}&interval=1d
```

**Parámetros utilizados:**
- `period1`: Timestamp Unix de la fecha de inicio (epoch seconds)
- `period2`: Timestamp Unix de la fecha de fin (epoch seconds)
- `interval`: Frecuencia de datos (1d = diario)
- `events`: Incluye datos históricos de precios

**Headers utilizados:**
- `User-Agent`: Mozilla/5.0 para identificar como navegador
- Accept: application/json para recibir respuesta en JSON

#### Parsing de respuestas

La respuesta JSON de la API se parsea manualmente para extraer:
1. `timestamp`: Lista de fechas en formato Unix
2. `indicators.quote`: Objeto con arrays de open, high, low, close, volume
3. Se itera sobre cada timestamp y se crea un registro con los datos OHLCV correspondientes

**Código relevante en `src/etl/fetcher.py:52-67`:**
```python
timestamps = result_data["timestamp"]
quote = result_data.get("indicators", {}).get("quote", [{}])[0]

for i, ts in enumerate(timestamps):
    if quote["open"][i] is None:
        continue
    record = {
        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
        "symbol": symbol.split(".")[0].upper(),
        "open": quote["open"][i],
        "high": quote["high"][i],
        "low": quote["low"][i],
        "close": quote["close"][i],
        "volume": quote["volume"][i],
    }
    records.append(record)
```

#### Manejo de errores y reintentos

El código implementa reintentos automáticos (MAX_RETRIES = 3) con backoff exponencial:

```python
for attempt in range(self.MAX_RETRIES):
    try:
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        # ... procesar respuesta
    except requests.exceptions.RequestException as e:
        if attempt < self.MAX_RETRIES - 1:
            time.sleep(2 * (attempt + 1))  # Backoff: 2s, 4s
        else:
            print(f"Error fetching {symbol}: {e}")
            return records
```

### 3.2 Limpieza de Datos

**Justificación algorítmica de las técnicas utilizadas:**

#### Eliminación de Duplicados
- **Técnica**: HashSet para detección O(1)
- **Complejidad**: O(n)
- **Justificación**: Cada registro debe ser único; los duplicados afectan cálculos estadísticos (media, varianza, volumen total)

**Código en `src/etl/cleaner.py:62-85`:**
```python
seen = set()
duplicate_indices = []
for idx, record in enumerate(records):
    key = (record["date"], record["symbol"])
    if key in seen:
        duplicate_indices.append(idx)
    else:
        seen.add(key)
```

#### Detección de Outliers
- **Técnica**: Rango Intercuartil (IQR)
- **Complejidad**: O(n)
- **Justificación**: Valores extremos distorsionan el análisis; IQR es robusto porque no asume distribución normal

**Fórmula**: Se considera outlier si valor < Q1 - 1.5×IQR o valor > Q3 + 1.5×IQR

#### Interpolación de Valores Faltantes
- **Técnica**: Interpolación lineal
- **Complejidad**: O(n)
- **Justificación**: 
  - Preserva longitud del dataset (importante para series temporales)
  - Mantiene tendencias sin introducir discontinuidades
  - Usa valores vecinos válidos para estimar el faltante

**Código en `src/etl/cleaner.py:126-182`:**
```python
# Busca el valor anterior y siguiente válidos
for i in range(idx - 1, -1, -1):
    if i not in indices_set and records_copy[i].get(field) is not None:
        prev_idx = i
        break
# ... interpola como promedio de vecinos
records_copy[idx][field] = (prev_value + next_value) / 2
```

### 3.3 Conciliación de Calendarios Bursátiles

El proyecto maneja las diferencias entre mercados de la siguiente manera:

1. **Mercados diferentes**: Los activos colombianos (sufijo .CL) y los internacionales (sin sufijo) se descargan por separado, cada uno con su propio rango de fechas disponible en Yahoo Finance.

2. **Desalineaciones temporales**: Al unificar los datos, se ordenan por fecha usando el criterio de ordenamiento establecido (fecha + precio de cierre). Los días sin negociación para un activo no generan registros, pero otros activos pueden tener datos ese día.

   **Ejemplo concreto:**
   - El 15 de marzo de 2025 es festivo en Colombia (San José) pero no en EE.UU.
   - Al descargar datos, ECOPETROL no tendrá registro para esa fecha, pero VOO sí lo tendrá
   - Al unificar, el dataset simplemente tendrá un registro menos para ECOPETROL ese día
   - Al ordenar por fecha, el algoritmo maneja correctamente los "huecos" porque no intenta forzar un registro donde no existe

3. **Díasfestivos**: No se agregan días festivos manualmente; el sistema simplemente toma los datos disponibles de cada fuente. La API de Yahoo Finance ya filtra los días sin negociación (fines de semana y festivos locales).

4. **Complejidad del manejo**: La unificación tiene complejidad O(n log n) dominada por el ordenamiento final. El sistema no requiere algoritmos adicionales para detectar o llenar huecos porque los algoritmos de ordenamiento funcionan correctamente con series de diferente longitud.

**Nota de mejora para versión futura**: Se podría implementar un mapeo explícito de días festivos por mercado (Colombia vs EE.UU.) para:
- Detectar y documentar explícitamente los huecos
- Estandarizar la cantidad de datos por activo
- Calcular métricas de disponibilidad por activo

## 4. Requerimiento 2: Análisis de Algoritmos de Ordenamiento

### 4.1 Los 12 Algoritmos

| # | Algoritmo | Complejidad Teórica |
|---|-----------|---------------------|
| 1 | TimSort | O(n log n) |
| 2 | Comb Sort | O(n²) |
| 3 | Selection Sort | O(n²) |
| 4 | Tree Sort | O(n log n) |
| 5 | Pigeonhole Sort | O(n + k) |
| 6 | BucketSort | O(n + k) |
| 7 | QuickSort | O(n log n) |
| 8 | HeapSort | O(n log n) |
| 9 | Bitonic Sort | O(log² n) |
| 10 | Gnome Sort | O(n²) |
| 11 | Binary Insertion Sort | O(n²) |
| 12 | RadixSort | O(nk) |

### 4.2 Criterio de Ordenamiento

- **Primario**: Fecha de cotización
- **Secundario**: Precio de cierre (cuando las fechas son iguales)

## 5. Activos Financieros

### 10 Acciones Colombianas
ECOPETROL, ISA, GEB, NUTRESA, GRUPOSURA, BANCOLOMBIA, COLTEJERA, ENKA, PREFERENCIAL, CANACOL

### 10 ETFs Internacionales
VOO, VTI, QQQ, SPY, VEA, VWO, BND, EFA, EEM, TLT

## 6. Justificación de Decisiones Técnicas

### 6.1 API de Yahoo Finance
- Cumple con el requisito de "peticiones explícitas a APIs públicas"
- Provee datos financieros históricos de calidad
- No requiere librerías de alto nivel como yfinance

### 6.2 Implementación Manual de Algoritmos
- Cada algoritmo está implementado explícitamente
- Permite análisis transparente del comportamiento
- Evita uso de funciones encapsuladas

### 6.3 Datos Reales
- El sistema siempre usa datos reales de la API
- No se permiten datasets estáticos o manuales
- La reproducibilidad está garantizada

## 7. Utilización de la IA

En el desarrollo de este proyecto se utilizó inteligencia artificial generativa como apoyo para la implementación. A continuación se documentan los usos realizados:

### Prompts relevantes utilizados:

1. *"Ayudame a hacer un proyecto base teniendo en cuenta los archivos llamados seguimiento 1 dentro de la carpeta docs, en este caso quiero que crees la estructura de carpetas de un proyecto con arquitectura de microservicios, en el readme quiero que agregues toda la información relevante, recuerda comentar las carpetas en ingles, pero nuestra conversación en español"*

2. *"necesito que simplifiques la ejecución del proyecto con taskfile, la idea es poder ejecutar el proyecto solo con el comando task run u alguna herramienta similar, recuerda instalar todas las dependencias de python necesarias y usar un .venv"*

3. *"estoy teniendo un problema con algunos algoritmos, al parecer sale: 'RecursionError: maximum recursion depth exceeded while calling a Python object' pero no aparece en todos los algoritmos"*

4. *"organiza un poco la grafica complexity_comparison, ya que como algunos algoritmos tienen un tiempo de ejecución y complejidad teorica similar, lo que hace que se sobrepongan los nombres, asi que mejor pon el nombre a la izquierda o la derecha del punto de color"*

5. *"aún se siguen sobreponiendo algunos nombres con otros, alguna idea? necesito poder observar correctamente los datos de cada algoritmo en la gráfica, si es necesario se puede cambiar el tipo de gráfica"*

**La IA se utilizó como soporte para la estructuración del proyecto, generación de código base y resolución de problemas técnicos. El diseño algorítmico, el análisis de complejidad y la documentación técnica fueron desarrollados de manera manual y personal.**

## 8. Requisitos de Ejecución

- Python 3.10+
- Taskfile 3.0+

Ejecución: `task run` o `python -m src.services.main_runner`

## 9. Conclusiones

El proyecto cumple con todos los requisitos de Seguimiento 1:

1. ✅ Proceso ETL automatizado con peticiones explícitas a APIs públicas
2. ✅ 20 activos financieros (4 colombianos + 16 internacionales)
3. ✅ 5 años de historial
4. ✅ Datos OHLCV completos
5. ✅ 12 algoritmos de ordenamiento implementados manualmente
6. ✅ Tabla 1 con método+complejidad, tamaño y tiempo
7. ✅ Ordenamiento por fecha y precio de cierre
8. ✅ Gráfico de barras comparativo
9. ✅ 15 días con mayor volumen
10. ✅ Datos reales de API pública
11. ✅ Sin uso de librerías de alto nivel para adquisición de datos
12. ✅ Declaración del uso de IA documentada