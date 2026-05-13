# Investment Algorithm — Análisis Algorítmico Financiero

**Universidad del Quindío** — Programa de Ingeniería de Sistemas y Computación
**Curso**: Análisis de Algoritmos — 2026-1

## Requisitos

- **Python**: 3.10 o superior
- **Taskfile**: 3.0 o superior
- **SO**: Windows, Linux, macOS

## Descripción

Sistema de análisis algorítmico de activos financieros que implementa:
1. **ETL**: Extracción multi-fuente HTTP (Tiingo, Yahoo, Alpha Vantage, Scraper, Binance) para 23 activos y 5+ años
2. **Similitud**: 4 algoritmos (Euclidiana, Pearson, DTW, Coseno) con comparación de pares y grupos
3. **Patrones**: Ventana deslizante (alza, baja, gaps y breakouts)
4. **Volatilidad**: Clasificación de riesgo (Conservador/Moderado/Agresivo)
5. **Dashboard**: Heatmap de correlación, candlestick con SMA, fórmulas matemáticas renderizadas y reporte PDF
6. **API REST**: Flask con frontend Chart.js

## Documentación

- **Documento de diseño**: `docs/Diseno.md`
- **Plan de desarrollo**: `Plan.md`
- **Enunciado del proyecto**: `Proyecto.md`

## Arquitectura

```
src/
├── api/
│   ├── gateway.py              # App Flask + Blueprints
│   ├── routes/
│   │   ├── similarity.py       # Similitud entre activos
│   │   ├── patterns.py         # Patrones y volatilidad
│   │   ├── dashboard.py        # Candlestick y SMA
│   │   └── reports.py          # Generación de PDF
│   └── templates/pages/        # Frontend (Jinja2 + Chart.js)
├── etl/
│   ├── fetcher.py              # HTTP directo a Yahoo Finance
│   ├── cleaner.py              # Limpieza (duplicados, outliers, interpolación)
│   └── unifier.py              # Unificación + alineación calendarios
├── services/
│   ├── similarity/             # 4 algoritmos de similitud
│   ├── patterns/               # Ventana deslizante + volatilidad
│   └── reporting/              # PDF + indicadores técnicos
├── sorting/                    # 12 algoritmos de ordenamiento
├── static/                     # CSS + JS
└── tests/                      # 47 tests unitarios
```

## Activos Financieros (23)

### Acciones Colombianas (4)
| Símbolo | Nombre |
|---------|--------|
| ECOPETROL | Ecopetrol S.A. |
| ISA | Interconexión Eléctrica S.A. |
| GEB | Grupo Energía de Bogotá |
| NUTRESA | Nutresa S.A. |

### ETFs Internacionales (16)
VOO, VTI, QQQ, SPY, VEA, VWO, BND, EFA, EEM, TLT, IVV, SCHD, DIA, IWM, XLF, XLK

### Acciones NYSE (3)
KO, PFE, PEP

## Ejecución

### Primera vez
```bash
task install   # Crea .venv e instala dependencias
task run       # Pipeline ETL completo
```

### Servidor web
```bash
task api       # localhost:5000
```

### Tests
```bash
task test      # 47 tests unitarios
```

### Sin Taskfile
```bash
pip install -r requirements.txt
python -m src.services.main_runner
python -m src.api.gateway
```

En Linux/macOS se recomienda esta ruta directa con Python mientras el `Taskfile` siga orientado a Windows.

## Opciones

| Comando | Descripción |
|---------|-------------|
| `task run` | Pipeline ETL completo |
| `task api` | Servidor web en :5000 |
| `task test` | Ejecuta tests |
| `task lint` | Verifica código |
| `task clean` | Limpia archivos generados |

## Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servidor |
| GET | `/api/similarity?s1=VOO&s2=SPY` | 4 métricas de similitud |
| GET | `/api/similarity/group?symbols=VOO&symbols=SPY&symbols=QQQ` | Comparación multi-activo |
| GET | `/api/correlation-matrix` | Matriz de correlación |
| GET | `/api/patterns?symbol=VOO&pattern=breakout_up&window=20` | Patrones |
| GET | `/api/volatility/ranking` | Ranking de riesgo |
| GET | `/api/candlestick?symbol=VOO` | OHLC + SMA |
| POST | `/api/report/generate` | Descargar PDF |

## Salida Generada

- `data/raw/raw_data.csv` — Datos crudos
- `data/processed/unified_data.csv` — Datos unificados
- `data/processed/sorting_results.csv` — Benchmark de ordenamiento
- `data/processed/top_volume_days.csv` — Días con mayor volumen
- `data/processed/complexity_comparison.png` — Gráfico comparativo
- `outputs/reporte_*.pdf` — Reportes PDF generados

## Restricciones del Proyecto

- ✅ Peticiones HTTP directas (sin yfinance/pandas_datareader)
- ✅ Algoritmos implementados manualmente (sin scipy/sklearn)
- ✅ Datos descargados automáticamente (sin datasets estáticos)
- ✅ Reproducibilidad garantizada (--force-download)
- ✅ Declaración de uso de IA documentada

## Utilización de la IA

Este proyecto utilizó inteligencia artificial generativa como apoyo para:
- Planificación estructurada del proyecto en fases
- Generación de código base (algoritmos, rutas, frontend)
- Tests unitarios y documentación

El diseño algorítmico, análisis de complejidad y decisiones arquitectónicas fueron desarrollados manualmente.

---

*Proyecto desarrollado para el curso de Análisis de Algoritmos - Universidad del Quindío - 2026-1*
