# Investment Algorithm - Financial Data Analysis

A quantitative analysis project focused on financial time series from the Colombian Stock Exchange (BVC) and global assets, implementing classical sorting algorithms with formal complexity analysis.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [API Data Sources](#api-data-sources)
- [Sorting Algorithms](#sorting-algorithms)
- [Complexity Analysis](#complexity-analysis)
- [Testing](#testing)
- [License](#license)
- [Authors](#authors)

## Overview

This project implements an automated ETL pipeline for financial data extraction and performs algorithmic analysis on historical stock prices, returns, and volatility. The system downloads and processes data for a portfolio of at least 20 assets with a minimum of 5 years of historical data.

## Features

- **Automated ETL Pipeline**: Extract, transform, and load financial data from public APIs
- **Data Cleaning**: Handle missing values, inconsistencies, and anomalies
- **12 Sorting Algorithms**: Implementations with formal complexity analysis
- **Time Series Analysis**: Performance comparison with visualizations
- **Volume Analysis**: Top 15 trading days identification
- **Multi-Asset Portfolio**: Colombian stocks (ECOPETROL, ISA, GEB) and global ETFs (VOO, CSPX)

## Project Structure

```
investment-algorithm/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── fetcher.py          # Data fetching from APIs
│   │   ├── cleaner.py          # Data cleaning utilities
│   │   ├── unifier.py          # Dataset unification
│   │   └── validator.py        # Data validation
│   ├── sorting/
│   │   ├── __init__.py
│   │   ├── bubble_sort.py      # Bubble Sort O(n²)
│   │   ├── selection_sort.py   # Selection Sort O(n²)
│   │   ├── insertion_sort.py   # Insertion Sort O(n²)
│   │   ├── merge_sort.py       # Merge Sort O(n log n)
│   │   ├── quick_sort.py       # Quick Sort O(n log n)
│   │   ├── heap_sort.py        # Heap Sort O(n log n)
│   │   ├── shell_sort.py       # Shell Sort O(n²) / O(n log² n)
│   │   ├── counting_sort.py    # Counting Sort O(n + k)
│   │   ├── radix_sort.py       # Radix Sort O(nk)
│   │   ├── cocktail_sort.py    # Cocktail Sort O(n²)
│   │   ├── comb_sort.py        # Comb Sort O(n²)
│   │   └── tim_sort.py         # Tim Sort O(n log n)
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── time_analyzer.py    # Timing utilities
│   │   └── performance_table.py # Results table generator
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── bar_chart.py        # Bar chart generator
│   └── utils/
│       ├── __init__.py
│       └── constants.py        # Configuration constants
├── tests/
│   ├── __init__.py
│   ├── test_sorting.py         # Sorting algorithm tests
│   ├── test_etl.py             # ETL pipeline tests
│   └── test_integration.py     # Integration tests
├── data/
│   └── (raw and processed data)
└── output/
    ├── sorting_results.csv     # Timing results
    ├── bar_chart.png           # Visualization output
    └── analysis_report.txt     # Text report
```

## Installation

### Prerequisites

- Python 3.9+
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/investment-algorithm.git
cd investment-algorithm

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Full Analysis Pipeline

```bash
python src/main.py
```

### Individual Modules

```bash
# Run ETL pipeline
python -m src.etl.fetcher

# Run sorting analysis
python -m src.sorting.bubble_sort

# Generate visualizations
python -m src.visualization.bar_chart
```

### Command Line Arguments

```bash
python src/main.py --assets 20 --years 5 --output output/
python src/main.py --skip-etl --sort-only  # Use cached data
```

## Requirements

The project fulfills these academic requirements:

1. **ETL Automation**: Complete automated extraction, transformation, and loading of financial data
2. **Data Unification**: Unified dataset for 20+ assets with 5+ years of data
3. **Sorting Analysis**: Analysis of 12 sorting algorithms with performance comparison
4. **Visualization**: Bar chart representation of sorting times
5. **Volume Analysis**: Top 15 trading days by volume

### Asset Portfolio

| Symbol | Name | Market |
|--------|------|--------|
| ECOPETROL | Ecopetrol S.A. | Colombia |
| ISA | Interconexión Eléctrica | Colombia |
| GEB | Grupo Energía Bogotá | Colombia |
| PFBCOLOM | Preferencial Bancolombia | Colombia |
| CEMEXLATAM | CEMEX Latam Holdings | Colombia |
| NUTRESA | Grupo Nutresa | Colombia |
| VOO | Vanguard S&P 500 ETF | USA |
| CSPX | iShares Core S&P 500 | USA |
| EFA | iShares MSCI EAFE | USA |
| ... | (15+ more assets) | |

## API Data Sources

Data is fetched using direct HTTP requests to public APIs:

- **Yahoo Finance API**: Historical price data via CSV download
- **Alternative**: Investing.com data scraping (respecting robots.txt)

### Data Fields

Each record contains:
- `date`: Trading date (YYYY-MM-DD)
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `symbol`: Asset ticker symbol

## Sorting Algorithms

| Algorithm | Time Complexity | Space Complexity | Type |
|-----------|-----------------|------------------|------|
| Bubble Sort | O(n²) | O(1) | Comparison |
| Selection Sort | O(n²) | O(1) | Comparison |
| Insertion Sort | O(n²) / O(n) best | O(1) | Comparison |
| Merge Sort | O(n log n) | O(n) | Comparison |
| Quick Sort | O(n log n) / O(n²) worst | O(log n) | Comparison |
| Heap Sort | O(n log n) | O(1) | Comparison |
| Shell Sort | O(n²) / O(n log² n) | O(1) | Comparison |
| Counting Sort | O(n + k) | O(k) | Non-comparison |
| Radix Sort | O(nk) | O(n + k) | Non-comparison |
| Cocktail Sort | O(n²) | O(1) | Comparison |
| Comb Sort | O(n²) / O(n log n) best | O(1) | Comparison |
| Tim Sort | O(n log n) | O(n) | Hybrid |

## Complexity Analysis

### Bubble Sort (O(n²))

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```

- **Best Case**: O(n) when already sorted
- **Average Case**: O(n²)
- **Worst Case**: O(n²) when reverse sorted

### Merge Sort (O(n log n))

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)
```

- **Recurrence**: T(n) = 2T(n/2) + Θ(n)
- **By Master Theorem**: T(n) = Θ(n log n)

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_sorting.py -v
```

### Test Categories

- **Unit Tests**: Individual algorithm correctness
- **Integration Tests**: ETL pipeline end-to-end
- **Performance Tests**: Timing validation

## License

This project was developed for academic purposes as part of the Algorithm Analysis course at Universidad del Quindío.

## Authors

- **[Your Name]** - Algorithm Analysis 2026-1
- Universidad del Quindío
- Programa de Ingeniería de Sistemas y Computación

## Acknowledgments

- Universidad del Quindío - Algorithm Analysis Course
- Professor: [Professor Name]
- Course: Análisis de Algoritmos - 2026-1
