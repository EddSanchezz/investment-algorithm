# Investment Algorithm - Seguimiento 1

## Requisitos

- **Python**: 3.10 o superior
- **Taskfile**: 3.0 o superior
- **SO**: Windows, Linux, macOS

## Descripción

Este proyecto es parte del curso de Análisis de Algoritmos de la Universidad del Quindío. El objetivo es analizar el rendimiento de 12 algoritmos de ordenamiento utilizando datos financieros reales (acciones y ETFs), comparando la complejidad teórica Big-O con el tiempo real de ejecución.

## Documentación del Proyecto

El proyecto cuenta con documentación formal en:
- **Documento de diseño**: `docs/Diseno.md` (este archivo)
- **Informe principal**: `Seguimiento 1 - Análisis de algoritmos`

## ¿Qué hace el proyecto?

1. **Descarga datos financieros** mediante HTTP directo de Yahoo Finance API
   - Peticiones explícitas sin librerías de alto nivel
   - Reintentos con backoff exponencial
   - Parsing manual de respuestas JSON
2. **Limpia los datos** (elimina duplicados, interpola valores faltantes, detecta outliers)
   - Duplicados: HashSet O(n)
   - Outliers: Rango Intercuartil (IQR) O(n)
   - Interpolación: Lineal O(n)
3. **Ordena los registros** por fecha y precio de cierre usando 12 algoritmos diferentes
4. **Analiza el volumen** de negociación para identificar los 15 días con mayor actividad
5. **Genera gráficos** comparativos de rendimiento

## Arquitectura del Sistema

```
src/
├── etl/
│   ├── fetcher.py        # Extracción HTTP directo (peticiones explícitas)
│   ├── scraper.py        # Scraper alternativo
│   ├── cleaner.py        # Limpieza con justificación algorítmica
│   └── unifier.py        # Unificación y conciliación de datos
├── sorting/
│   ├── algorithms.py     # 12 algoritmos de ordenamiento
│   ├── comparator.py     # Comparador de rendimiento
│   └── visualizer.py     # Generación de gráficos
└── services/
    ├── volume_analyzer.py # Análisis de volumen
    └── main_runner.py    # Orquestador principal
```

### Proceso ETL

1. **Extracción**: Peticiones HTTP directas a Yahoo Finance API
2. **Transformación**: Limpieza (duplicados, outliers, valores faltantes)
3. **Carga**: Unificación en dataset único

## Activos Financieros

### Acciones Colombianas (4)
| Símbolo | Nombre |
|---------|--------|
| ECOPETROL | Ecopetrol S.A. |
| ISA | Interconexión Eléctrica S.A. |
| GEB | Grupo Energía de Bogotá |
| NUTRESA | Nutresa S.A. |

### ETFs Internacionales (16)
| Símbolo | Nombre |
|---------|--------|
| VOO | Vanguard S&P 500 ETF |
| VTI | Vanguard Total Stock Market |
| QQQ | Invesco QQQ Trust (Nasdaq-100) |
| SPY | SPDR S&P 500 ETF |
| VEA | Vanguard FTSE Developed Markets |
| VWO | Vanguard FTSE Emerging Markets |
| BND | Vanguard Total Bond Market |
| EFA | iShares MSCI EAFE |
| EEM | iShares MSCI Emerging Markets |
| TLT | iShares 20+ Year Treasury Bond |
| IVV | iShares Core S&P 500 ETF |
| SCHD | Schwab U.S. Dividend Equity ETF |
| DIA | SPDR Dow Jones Industrial Average |
| IWM | iShares Russell 2000 ETF |
| XLF | Financial Select Sector SPDR |
| XLK | Technology Select Sector SPDR |

**Total: 20 activos**

## Documentación del Código

El código está documentado con:

- **Docstrings** en todas las clases y funciones principales
- **Comentarios** explicando decisiones técnicas
- **Complejidad algorítmica** documentada en cada función

### Ejemplo de documentación en cleaner.py:

```python
def detect_duplicates(self, records: List[Dict]) -> List[int]:
    """
    Detecta registros duplicados basándose en fecha y símbolo.
    Complejidad: O(n) usando tabla hash para deduplicación
    """
```

### Ejemplo en fetcher.py:

```python
def fetch_historical_data(self, symbol: str, start_date: datetime, end_date: datetime):
    """
    Descarga datos históricos mediante HTTP directo.
    Konstruye la URL con parámetros period1, period2, interval.
    Parsing manual del JSON de respuesta.
    Reintentos automáticos con backoff.
    """
```

## Ejecución

### Primera vez
```bash
task install   # Crea entorno virtual e instala dependencias
task run       # Ejecuta el pipeline completo
```

### Después de la primera vez
```bash
task run       # Ya tiene el entorno instalado
```

### Ejecutar sin Taskfile
```bash
python -m pip install -r requirements.txt
python -m src.services.main_runner
```

## Opciones Adicionales

| Comando | Descripción |
|---------|-------------|
| `task clean` | Limpia archivos generados |
| `task lint` | Verifica código con linter |
| `task api` | Inicia servidor REST en localhost:5000 |

## Problemas Comunes

| Problema | Solución |
|----------|----------|
| Error 404 al descargar | Verificar símbolo correcto. Las acciones colombianas necesitan sufijo `.CL` (ej: `ECOPETROL.CL`) |
| Timeout de conexión | Verificar conexión a internet. Aumentar timeout en `src/etl/fetcher.py` si es necesario |
| Sin datos disponibles | La API de Yahoo Finance puede tener limitaciones. Verificar símbolo en yahoo.com |
| Error de permisos | Asegurarse de tener permisos de escritura en la carpeta `data/` |
| Warning de outliers | Es normal en datos financieros. Los outliers se detectan pero no se eliminan automáticamente |

## Salida Generada

- `data/raw/raw_data.csv` - Datos crudos
- `data/processed/unified_data.csv` - Datos unificados
- `data/processed/sorting_results.csv` - Tabla 1 (algoritmos, complejidad, tamaño, tiempo)
- `data/processed/top_volume_days.csv` - 15 días con mayor volumen
- `data/processed/complexity_comparison.png` - Gráfico comparativo

## Utilización de la IA

Este proyecto utilizó inteligencia artificial generativa como apoyo para:
- Estructuración inicial del proyecto
- Generación de código base
- Resolución de problemas técnicos (ej: RecursionError en algoritmos)

El diseño algorítmico, análisis de complejidad y documentación fueron desarrollados manualmente.

---

*Proyecto desarrollado para el curso de Análisis de Algoritmos - Universidad del Quindío - 2026-1*