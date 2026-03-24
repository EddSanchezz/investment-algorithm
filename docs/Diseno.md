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
│   └── visualizer.py    # Generación de gráficos
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

## 3. Requerimiento 1: Proceso ETL

### 3.1 Extracción de Datos

**Módulo**: `src/etl/fetcher.py`

**Funcionalidad**: Descarga datos financieros desde Yahoo Finance API mediante HTTP directo.

**Complejidad**: O(n × d) donde n = número de activos, d = días de historial

**Implementación**:
- Uso de `requests` para HTTP directo (no librerías de alto nivel)
- Construcción manual de URLs de la API
- Parsing manual de respuestas JSON
- Manejo de errores con reintentos

**Datos extraídos** (OHLCV):
- Fecha (date)
- Precio de apertura (open)
- Precio máximo (high)
- Precio mínimo (low)
- Precio de cierre (close)
- Volumen de negociación (volume)

**Activos configurados** (20):
- Colombianos: ECOPETROL, ISA, GEB, NUTRESA
- Internacionales: VOO, VTI, QQQ, SPY, VEA, VWO, BND, EFA, EEM, TLT, IVV, SCHD, DIA, IWM, XLF, XLK

**Historial**: 5 años por defecto

### 3.2 Limpieza de Datos

**Módulo**: `src/etl/cleaner.py`

**Funcionalidad**: Detecta y maneja problemas en los datos.

**Técnicas implementadas**:
1. **Eliminación de duplicados**: HashSet para detectar registros duplicados
2. **Detección de outliers**: Rango intercuartil (IQR) - valores fuera de Q1-1.5×IQR o Q3+1.5×IQR
3. **Interpolación de valores faltantes**: Interpolación lineal entre valores válidos
4. **Manejo de registros inconsistentes**: Validación de rangos de precios

**Complejidad**: O(n) para cada paso

### 3.3 Unificación de Datos

**Módulo**: `src/etl/unifier.py`

**Funcionalidad**: Combina datos de múltiples activos en un solo dataset.

**Complejidad**: O(n)

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

**Implementación**: Método `compareTo()` en la clase `DatoFinanciero`

### 4.3 Tabla de Resultados

**Archivo**: `data/processed/sorting_results.csv`

**Formato**:
```
Metodo de ordenamiento,Tamano,Tiempo (s)
TimSort O(n log n),2512,0.004688
```

**Columnas combinadas**: Método de ordenamiento + Complejidad en una sola columna

## 5. Análisis de Volumen

### 5.1 Cálculo de Volumen

**Módulo**: `src/services/volume_analyzer.py`

**Funcionalidad**: Calcula el volumen total por fecha sumando todos los activos.

**Complejidad**: O(n) para聚合 + O(n log n) para ordenamiento

### 5.2 Resultados

**Archivo**: `data/processed/top_volume_days.csv`

**Contenido**: 15 días con mayor volumen total (orden ascendente)

## 6. Visualización

### 6.1 Gráfico de Rendimiento

**Módulo**: `src/sorting/visualizer.py`

**Tipo**: Gráfico de barras horizontal

**Contenido**: Tiempos de ejecución de los 12 algoritmos, ordenados por complejidad teórica

**Colores**: Diferentes colores por complejidad algorítmica

## 7. Justificación de Decisiones Técnicas

### 7.1 API de Yahoo Finance

Se utiliza Yahoo Finance API mediante requests HTTP directos porque:
- Cumple con el requisito de "peticiones explícitas a APIs públicas"
- Provee datos financieros históricos de calidad
- No requiere librerías de alto nivel como yfinance

### 7.2 Implementación Manual de Algoritmos

Cada algoritmo está implementado explícitamente:
- Permite análisis transparente del comportamiento
- Evita uso de funciones encapsuladas
- Demuestra comprensión de las técnicas de ordenamiento

### 7.3 Datos Reales

El sistema siempre usa datos reales de la API:
- No se permiten datasets estáticos o manuales
- La reproducibilidad está garantizada
- Cada ejecución puede reproducir los mismos datos

## 8. Ejecución del Proyecto

### 8.1 Requisitos

- Python 3.10+
- Taskfile 3.0+

### 8.2 Comandos

```bash
task install  # Instalar dependencias
task run      # Ejecutar pipeline completo
```

### 8.3 Archivos Generados

- `data/raw/raw_data.csv` - Datos crudos
- `data/processed/unified_data.csv` - Datos unificados
- `data/processed/sorting_results.csv` - Tabla 1
- `data/processed/top_volume_days.csv` - 15 días mayor volumen
- `data/processed/complexity_comparison.png` - Gráfico

## 9. Conclusiones

El proyecto cumple con todos los requisitos de Seguimiento 1:

1. ✅ Proceso ETL automatizado
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
