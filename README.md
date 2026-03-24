# Investment Algorithm - Seguimiento 1

## Descripción

Este proyecto es parte del curso de Análisis de Algoritmos de la Universidad del Quindío. El objetivo es analizar el rendimiento de 12 algoritmos de ordenamiento utilizando datos financieros reales (acciones y ETFs), comparando la complejidad teórica Big-O con el tiempo real de ejecución.

## ¿Qué hace el proyecto?

1. **Descarga datos financieros** mediante web scraping de Investing.com (Selenium)
2. **Limpia los datos** (elimina duplicados, interpola valores faltantes, detecta outliers)
3. **Ordena los registros** por fecha y precio de cierre usando 12 algoritmos diferentes
4. **Analiza el volumen** de negociación para identificar los 15 días con mayor actividad
5. **Genera gráficos** comparativos de rendimiento

## Activos Financieros Utilizados

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

## Opciones Adicionales

| Comando | Descripción |
|---------|-------------|
| `task clean` | Limpia archivos generados |
| `task lint` | Verifica código con linter |
| `task api` | Inicia servidor REST en localhost:5000 |

---

*Proyecto desarrollado para el curso de Análisis de Algoritmos - Universidad del Quindío - 2026-1*
