# Investment Algorithm - Análisis de Algoritmos

## Descripción del Proyecto

Este proyecto implementa un sistema de análisis algorítmico aplicado a datos financieros, desarrollado como parte del curso de Análisis de Algoritmos en la Universidad del Quindío.

El sistema procesa datos históricos de activos financieros (acciones y ETFs) y demuestra el análisis formal de complejidad algorítmica mediante la implementación de 12 algoritmos de ordenamiento y análisis de volumen de negociación.

## Arquitectura del Sistema

El proyecto sigue una **arquitectura de microservicios modular** donde cada componente es un módulo independiente de Python que puede ejecutarse de forma autónoma:

```
investment-algorithm/
├── src/
│   ├── __init__.py
│   ├── etl/                      # Microservicio ETL
│   │   ├── fetcher.py            # Obtención de datos HTTP
│   │   ├── cleaner.py            # Limpieza y transformación
│   │   └── unifier.py            # Unificación de datasets
│   ├── sorting/                  # Microservicio de Ordenamiento
│   │   ├── algorithms.py         # 12 algoritmos implementados
│   │   ├── comparator.py        # Benchmark y comparaciones
│   │   └── visualizer.py        # Generación de gráficos
│   ├── services/                 # Microservicio de Análisis
│   │   ├── volume_analyzer.py    # Análisis de volumen
│   │   └── main_runner.py        # Orquestador principal
│   └── api/                      # API REST
│       └── gateway.py            # Endpoints REST
├── data/
│   ├── raw/                      # Datos sin procesar
│   └── processed/                # Datos unificados y gráficos
├── tests/                        # Pruebas unitarias
├── Taskfile.yml                  # Tareas automatizadas
├── requirements.txt              # Dependencias Python
├── docker-compose.yml            # Orquestación Docker
└── README.md                     # Este archivo
```

## Requerimientos Funcionales

### Requerimiento 1: Proceso ETL Automatizado

El sistema implementa un proceso ETL completamente automatizado:

#### 1.1 Extracción de Datos (fetcher.py)

```python
class FinancialDataFetcher:
    def fetch_historical_data(self, symbol, start_date, end_date) -> List[Dict]
    def fetch_multiple_assets(self, symbols, years) -> List[Dict]
```

- **Fuente de datos**: Yahoo Finance API (HTTP directo)
- **Historial**: 5 años de datos diarios por activo
- **Campos**: Date, Open, High, Low, Close, Volume
- **Complejidad**: O(n × d) donde n = número de activos, d = días

**Justificación de HTTP directo**: Se usa `requests` en lugar de `yfinance` para cumplir con el requerimiento de peticiones HTTP explícitas y manejo manual de parsing.

#### 1.2 Limpieza de Datos (cleaner.py)

```python
class DataCleaner:
    def clean_records(self, records) -> Tuple[List[Dict], Dict]
```

El proceso de limpieza incluye:

| Técnica | Justificación | Complejidad |
|---------|---------------|-------------|
| Eliminación de duplicados | Afectan cálculos estadísticos | O(n) |
| Interpolación lineal | Preserva longitud de series temporales | O(n) |
| Detección de outliers (Z-Score) | Identifica anomalías en precios | O(n) |

**Decisiones algorítmicas documentadas en el código fuente.**

#### 1.3 Unificación (unifier.py)

```python
class DataUnifier:
    def unify_datasets(self, datasets) -> List[Dict]
    def generate_statistics(self, records) -> Dict
```

- Combina datos de múltiples activos
- Ordena por fecha y precio de cierre
- Genera estadísticas del dataset

### Requerimiento 2: Análisis de Algoritmos de Ordenamiento

Se implementan **12 algoritmos de ordenamiento** con análisis de complejidad formal:

| # | Algoritmo | Complejidad Promedio | Complejidad Peor Caso |
|---|-----------|---------------------|------------------------|
| 1 | TimSort | O(n log n) | O(n log n) |
| 2 | Comb Sort | O(n²) | O(n²) |
| 3 | Selection Sort | O(n²) | O(n²) |
| 4 | Tree Sort | O(n log n) | O(n²) |
| 5 | Pigeonhole Sort | O(n + k) | O(n + k) |
| 6 | Bucket Sort | O(n + k) | O(n²) |
| 7 | QuickSort | O(n log n) | O(n²) |
| 8 | HeapSort | O(n log n) | O(n log n) |
| 9 | Bitonic Sort | O(log² n) | O(log² n) |
| 10 | Gnome Sort | O(n²) | O(n²) |
| 11 | Binary Insertion Sort | O(n²) | O(n²) |
| 12 | Radix Sort | O(nk) | O(nk) |

### Análisis Detallado de Complejidades

#### TimSort - O(n log n)
Combina insertion sort para pequeños bloques con merge sort para combinar resultados. Detecta "runs" naturales en datos parcialmente ordenados.

```python
def tim_sort(self, arr: list) -> list:
    # Fase 1: Crear runs con insertion sort O(min_run)
    # Fase 2: Merge de runs O(log n) × O(n) = O(n log n)
```

#### QuickSort - O(n log n) promedio
Usa partición de Lomuto. El pivote se coloca en su posición final.

```python
def quicksort(self, arr, low, high):
    if low < high:
        pivot_idx = partition(low, high)  # O(n) para particionar
        quicksort(low, pivot_idx - 1)     # O(log n) niveles
        quicksort(pivot_idx + 1, high)
```

#### HeapSort - O(n log n) garantizado
Construye max-heap y extrae el máximo repetidamente.

```python
def heapsort(self, arr):
    # Construcción heap: O(n)
    # Extracción: n × O(log n) = O(n log n)
```

## Instalación y Uso

### Requisitos Previos
- Python 3.10+
- [Taskfile](https://taskfile.dev/) (opcional, pero recomendado)
- Docker y Docker Compose (opcional)

### Instalación Rápida con Taskfile

```bash
# 1. Instalar Taskfile (ver https://taskfile.dev/#/installation)

# 2. Ejecutar con un solo comando
task install    # Crea entorno virtual e instala dependencias
task run        # Ejecuta el pipeline completo
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `task install` | Crea entorno virtual (.venv) e instala dependencias |
| `task run` | Ejecuta pipeline con datos de ejemplo |
| `task run-full` | Ejecuta pipeline descargando datos reales |
| `task api` | Inicia el servidor API REST |
| `task test` | Ejecuta pruebas unitarias |
| `task clean` | Limpia archivos generados y caches |
| `task build` | Construye imágenes Docker |
| `task lint` | Ejecuta linter de código |

### Instalación Manual (sin Taskfile)

```bash
# Clonar el repositorio
git clone <repo-url>
cd investment-algorithm

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pipeline
python -m src.services.main_runner --sample
```

### Ejecución con Opciones

```bash
# Usar datos de ejemplo (más rápido)
task run

# Descargar datos reales (tarda más)
task run-full

# Especificar símbolos
python -m src.services.main_runner --symbols VOO SPY QQQ --years 3

# Iniciar API REST
task api
# API disponible en http://localhost:5000
```

### Uso con Docker

```bash
# Construir imágenes
docker-compose build

# Ejecutar contenedores
docker-compose up

# Ver logs
docker-compose logs -f
```

## API REST

La API proporciona endpoints para acceder a los resultados:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Estado del servicio |
| `/api/records` | GET | Lista de registros |
| `/api/records/sorted` | GET | Registros ordenados |
| `/api/volume/top?n=15` | GET | Top N días por volumen |
| `/api/sorting/benchmark` | GET | Benchmark de algoritmos |
| `/api/statistics` | GET | Estadísticas del dataset |

### Ejecutar API

```bash
python -m src.api.gateway
# API disponible en http://localhost:5000
```

## Análisis de Volumen de Negociación

El sistema identifica los **15 días con mayor volumen** de negociación para todos los activos combinados:

```python
# Agregación por fecha: O(n)
# Ordenamiento: O(m log m) donde m = días únicos
# Total: O(n + m log m)
```

## Visualizaciones

Se generan automáticamente:

1. **Diagrama de barras** (`sorting_times.png`): Tiempos de cada algoritmo
2. **Gráfico de complejidad** (`complexity_comparison.png`): Complejidad teórica vs tiempo real

## Restricciones Implementadas

- ❌ No usa `yfinance` o `pandas_datareader`
- ✅ Usa `requests` para HTTP directo
- ❌ No usa funciones de ordenamiento de librerías
- ✅ Implementación explícita de todos los algoritmos
- ❌ No usa datasets estáticos pre-descargados
- ✅ Reproducibilidad total del proceso ETL

## Tecnologias Utilizadas

- **Python 3.10+**: Lenguaje principal
- **requests**: Peticiones HTTP
- **pandas**: Manipulación de datos
- **matplotlib**: Visualizaciones
- **Flask**: API REST
- **Docker**: Contenedores

## Autores

Desarrollado para el curso de Análisis de Algoritmos - Universidad del Quindío - 2026-1

## Licencia

Este proyecto es para fines educativos.
