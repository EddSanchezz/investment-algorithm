# Informe de Seguimiento 1 - Análisis de Algoritmos

## Universidad del Quindío
### Programa de Ingeniería de Sistemas y Computación
### Curso: Análisis de Algoritmos - 2026-1

---

## 1. Introducción y Contexto del Proyecto

Este seguimiento 1 hace parte del proyecto final de análisis de algoritmos, enfocados en el primer punto de este mismo. Este seguimiento está enfocado no solo en entender cómo funcionan algunos algoritmos de ordenamiento, observar el tiempo de ejecución de estos y entender la complejidad de cada uno, sino también en obtener, entender y organizar toda la información que estos algoritmos reciben. Uno de los puntos importantes a la hora de usar un algoritmo de ordenamiento es obtener la menor complejidad y tiempo de ejecución posible, con esto optimizar tiempo y operaciones, esto debido a la gran cantidad de datos que se manejan hoy en día en las empresas modernas.

El análisis financiero moderno depende en gran medida de la capacidad computacional para procesar grandes volúmenes de datos históricos y detectar patrones relevantes en el comportamiento de los activos financieros. En los mercados actuales, donde la información se genera de manera continua y a gran escala, resulta indispensable el uso de algoritmos eficientes que permitan comparar, agrupar y analizar series de tiempo financieras de forma rigurosa.

Este proyecto tiene como objetivo aplicar métodos cuantitativos, algoritmos clásicos y técnicas de análisis de series temporales sobre datos reales provenientes de la Bolsa de Valores de Colombia (BVC) y de activos globales relevantes para el inversor local, como índices bursátiles y ETFs internacionales (S&P 500).

---

## 2. Objetivos del Proyecto

El propósito de este proyecto es diseñar e implementar una serie de algoritmos que permitan realizar análisis técnico, estadístico y comparativo de activos financieros, haciendo énfasis en la eficiencia computacional, la correcta fundamentación matemática de las métricas utilizadas y el análisis formal de la complejidad algorítmica.

Los objetivos específicos incluyen:

1. **Automatizar el proceso ETL** de extracción, limpieza y unificación de datos financieros.
2. **Implementar 12 algoritmos de ordenamiento** desde cero, sin usar librerías de alto nivel.
3. **Analizar la complejidad algorítmica** de cada método mediante análisis formal Big-O.
4. **Comparar el rendimiento real** de los algoritmos mediante benchmarking.
5. **Identificar patrones de volumen** en los días de mayor negociación.

---

## 3. Activos Financieros Utilizados

Para este proyecto se seleccionaron 12 activos financieros que incluyen acciones colombianas y ETFs internacionales, permitiendo una diversificación representativa del mercado tanto local como global.

### 3.1 Acciones Colombianas

| Símbolo | Nombre Completo | Sector |
|---------|-----------------|--------|
| **ISA** | Interconexión Eléctrica S.A. | Energía eléctrica - Transmisión |
| **GEB** | Grupo Energía de Bogotá | Energía - Distribución |

### 3.2 ETFs Internacionales

| Símbolo | Nombre Completo | Descripción |
|---------|-----------------|-------------|
| **VOO** | Vanguard S&P 500 ETF | Replica el índice S&P 500, que incluye las 500 empresas más grandes de Estados Unidos |
| **VTI** | Vanguard Total Stock Market ETF | Incluye todas las empresas del mercado estadounidense |
| **QQQ** | Invesco QQQ Trust | Seguí el Nasdaq-100, concentrando en empresas de tecnología |
| **SPY** | SPDR S&P 500 ETF Trust | Uno de los ETFs más antiguos y líquidos del S&P 500 |
| **VEA** | Vanguard FTSE Developed Markets | Incluye mercados desarrollados de Europa, Japón y Australia |
| **VWO** | Vanguard FTSE Emerging Markets | Incluye mercados emergentes como China, India y Brasil |
| **BND** | Vanguard Total Bond Market ETF | Fondo de bonos gubernamentales y corporativos de EE.UU. |
| **EFA** | iShares MSCI EAFE ETF | Países desarrollados de Europa, Asia y Australia |
| **EEM** | iShares MSCI Emerging Markets ETF | Mercados emergentes a nivel mundial |
| **TLT** | iShares 20+ Year Treasury Bond | Bonos del tesoro estadounidenses a largo plazo |

La selección de estos activos responde a la necesidad de tener una muestra representativa del mercado financiero, combinando exposición local (acciones colombianas) con diversificación internacional a través de ETFs que replican índices globales, de desarrollados y emergentes, además de bonos para diversificación.

---

## 4. Arquitectura del Sistema

El proyecto sigue una **arquitectura de microservicios modular** implementada en Python, donde cada componente es un módulo independiente que puede ejecutarse de forma autónoma.

### 4.1 Estructura de Directorios

```
investment-algorithm/
├── src/
│   ├── __init__.py
│   ├── etl/                      # Módulo ETL
│   │   ├── fetcher.py           # Obtención de datos HTTP directo
│   │   ├── cleaner.py            # Limpieza y transformación
│   │   └── unifier.py            # Unificación de datasets
│   ├── sorting/                  # Módulo de Ordenamiento
│   │   ├── algorithms.py         # 12 algoritmos implementados
│   │   ├── comparator.py         # Benchmark y comparaciones
│   │   └── visualizer.py         # Generación de gráficos
│   ├── services/                 # Módulo de Servicios
│   │   ├── volume_analyzer.py    # Análisis de volumen
│   │   └── main_runner.py        # Orquestador principal
│   └── api/                      # API REST
│       └── gateway.py            # Endpoints REST
├── data/
│   ├── raw/                      # Datos sin procesar
│   └── processed/                # Datos unificados y gráficos
├── docs/                         # Documentación
├── Taskfile.yml                  # Tareas automatizadas
├── requirements.txt              # Dependencias Python
├── docker-compose.yml            # Orquestación Docker
└── README.md                     # Documentación técnica
```

### 4.2 Componentes Principales

**Módulo ETL (Extracción, Transformación y Carga):**
Este módulo es responsable de obtener los datos financieros desde fuentes públicas, limpiarlos y unificarlos en un solo dataset. Se implementó utilizando peticiones HTTP directas mediante la librería `requests`, evitando el uso de librerías de alto nivel como yfinance que encapsulan toda la lógica de obtención de datos.

**Módulo de Ordenamiento:**
Contiene la implementación desde cero de 12 algoritmos de ordenamiento diferentes, cada uno con su análisis de complejidad algorítmica documentado. Este módulo es el núcleo del análisis académico del proyecto.

**Módulo de Servicios:**
Incluye el orquestador principal que coordina todas las etapas del pipeline y el analizador de volumen de negociación para identificar los días con mayor actividad.

**Módulo API:**
Proporciona endpoints REST para acceder a los resultados del análisis de forma programática.

---

## 5. Metodología y Implementación

### 5.1 Proceso ETL

El proceso ETL implementado sigue tres etapas claramente definidas:

**Extracción de Datos:**
La obtención de datos financieros se realiza mediante peticiones HTTP directas a la API de Yahoo Finance. Se opted por esta implementación manual para cumplir con el requisito de utilizar peticiones explícitas y manejo manual de parsing, en lugar de rely on librerías que encapsulen toda la lógica. Cada activo se descarga con un período histórico de 5 años, obteniendo los campos: Date, Open, High, Low, Close y Volume.

La complejidad temporal de esta etapa es O(n × d) donde n representa el número de activos y d el número de días por activo.

**Limpieza de Datos:**
Se implementaron tres técnicas de limpieza que se aplican en pipeline:

1. **Eliminación de Duplicados:** Se detectan y eliminan registros que comparten la misma fecha y símbolo. Esta técnica es importante porque los duplicados afectan directamente los cálculos estadísticos, causando sobrestimación del volumen y alteración de promedios. Complejidad: O(n).

2. **Interpolación Lineal:** Cuando se detectan valores faltantes en las series temporales, se utiliza interpolación lineal para completar estos huecos. La justificación de usar interpolación en lugar de eliminar el registro es que las series temporales financieras deben mantener su longitud para permitir análisis posteriores de tendencia y volatilidad. Complejidad: O(n).

3. **Detección de Outliers mediante Z-Score:** Se identifican valores atípicos que podrían representar errores en los datos o eventos extraordinarios. Un valor se considera atípico cuando su desviación respecto a la media supera 3 desviaciones estándar. Complejidad: O(n).

**Unificación de Datos:**
Finalmente, todos los datos de los diferentes activos se combinan en un solo dataset, ordenando los registros primero por fecha y luego por precio de cierre como criterio secundario. Esta unificación permite realizar análisis agregados a través de todos los activos.

### 5.2 Algoritmos de Ordenamiento Implementados

Se implementaron 12 algoritmos de ordenamiento desde cero, cada uno con su análisis de complejidad algorítmica:

| # | Algoritmo | Complejidad Promedio | Peor Caso | Descripción del Funcionamiento |
|---|-----------|---------------------|-----------|--------------------------------|
| 1 | TimSort | O(n log n) | O(n log n) | Combina Insertion Sort para bloques pequeños con Merge Sort para combinar resultados. Detecta "runs" naturales en datos parcialmente ordenados, lo que lo hace muy eficiente para datos financieros. |
| 2 | Comb Sort | O(n²) | O(n²) | Evolución del Bubble Sort que utiliza un gap (espacio) decreciente. El factor de reducción típico es 1.3, determinado empíricamente. |
| 3 | Selection Sort | O(n²) | O(n²) | Divide el array en sublista ordenada y no ordenada, seleccionando el mínimo en cada iteración. |
| 4 | Tree Sort | O(n log n) | O(n²) | Construye un BST (Binary Search Tree) y luego realiza recorrido in-order. Versión iterativa para evitar límites de recursión. |
| 5 | Pigeonhole Sort | O(n + k) | O(n + k) | Útil cuando el rango de valores (k) es menor que el número de elementos (n). Versión genérica para manejar diferentes tipos de datos. |
| 6 | Bucket Sort | O(n + k) | O(n²) | Distribuye elementos en buckets y luego ordena cada bucket individualmente. |
| 7 | QuickSort | O(n log n) | O(n²) | Usa partición de Lomuto donde el pivote se coloca en su posición final. Versión iterativa para evitar límites de recursión. |
| 8 | HeapSort | O(n log n) | O(n log n) | **Garantiza** O(n log n) en todos los casos. Construye un max-heap y extrae el máximo repetidamente. |
| 9 | Bitonic Sort | O(log² n) | O(log² n) | Diseñado para arquitecturas paralelas. Requiere que n sea potencia de 2. |
| 10 | Gnome Sort | O(n²) | O(n²) | Similar a Insertion Sort pero con un enfoque de "caminata" que recuerda a un gnomo ordenando macetas. |
| 11 | Binary Insertion Sort | O(n²) | O(n²) | Usa búsqueda binaria para encontrar la posición de inserción, reduciendo comparaciones a O(n log n) aunque la inserción sigue siendo O(n). |
| 12 | Radix Sort | O(nk) | O(nk) | Ordena elemento por elemento usando el método LSD (Least Significant Digit). Excelente para enteros. |

### 5.3 Justificación de Implementación

Se decidió implementar todos los algoritmos desde cero (sin usar funciones de librerías) porque el objetivo académico del proyecto es demostrar comprensión del funcionamiento interno de cada algoritmo, permitiendo el análisis transparente de su comportamiento algorítmico.

Además, se implementaron versiones iterativas de algoritmos recursivos (como QuickSort y Tree Sort) para evitar los límites de profundidad de recursión que Python impone, permitiendo ordenar datasets de mayor tamaño.

---

## 6. Resultados Obtenidos

### 6.1 Tabla de Tiempos de Ejecución

Las siguientes mediciones fueron realizadas con un dataset de 12,792 registros (datos de 5 años para 11 activos):

| Algoritmo | Complejidad Teórica | Tiempo Promedio (ms) |
|-----------|---------------------|----------------------|
| Radix Sort | O(nk) | 3.14 |
| Pigeonhole Sort | O(n + k) | 3.30 |
| Bucket Sort | O(n + k) | 8.61 |
| TimSort | O(n log n) | 33.47 |
| Comb Sort | O(n²) | 95.10 |
| HeapSort | O(n log n) | 107.71 |
| Bitonic Sort | O(log² n) | 352.45 |
| Tree Sort | O(n log n) | 1,051.90 |
| QuickSort | O(n log n) | 2,107.53 |
| Binary Insertion Sort | O(n²) | 4,093.35 |
| Selection Sort | O(n²) | 14,090.68 |
| Gnome Sort | O(n²) | 21,215.64 |

### 6.2 Análisis de Volumen de Negociación

Los 15 días con mayor volumen de negociación (ordenados ascendentemente):

| Posición | Fecha | Volumen Total |
|----------|-------|---------------|
| 1 | 2022-05-10 | 523,933,100 |
| 2 | 2022-05-06 | 524,817,600 |
| 3 | 2022-03-16 | 532,327,500 |
| 4 | 2022-05-11 | 532,436,800 |
| 5 | 2026-03-20 | 533,631,900 |
| 6 | 2025-04-08 | 535,633,300 |
| 7 | 2022-01-26 | 543,699,765 |
| 8 | 2022-05-05 | 553,376,500 |
| 9 | 2022-03-08 | 554,580,900 |
| 10 | 2022-01-21 | 573,758,520 |
| 11 | 2022-02-24 | 655,342,790 |
| 12 | 2025-04-04 | 672,647,500 |
| 13 | 2025-04-09 | 772,774,300 |
| 14 | 2022-01-24 | 780,424,236 |
| 15 | 2025-04-07 | 846,523,800 |

### 6.3 Visualizaciones Generadas

El sistema genera automáticamente dos visualizaciones:

1. **Diagrama de barras (sorting_times.png):** Muestra los tiempos de ejecución de los 12 algoritmos de manera ascendente, permitiendo una comparación visual directa.

2. **Gráfico de complejidad (complexity_comparison.png):** Barras horizontales que ordenan los algoritmos por su complejidad teórica, permitiendo observar la relación entre la complejidad Big-O teórica y el tiempo real de ejecución.

---

## 7. Conclusiones

### 7.1 Hallazgos Principales

Del análisis de los resultados se pueden extraer varias conclusiones relevantes:

**Complejidad teórica vs. Rendimiento real:**
Los algoritmos con mejor complejidad teórica no siempre son los más rápidos en la práctica. Radix Sort y Pigeonhole Sort, con complejidades O(nk) y O(n + k) respectivamente, superaron significativamente a algoritmos con O(n log n) como TimSort y QuickSort. Esto se debe a que la complejidad teórica asume un modelo de computación simplificado, mientras que en la práctica intervienen factores como la constantes, el tipo de datos y la eficiencia de la implementación.

**Eficiencia de TimSort:**
TimSort, utilizado por Python en su función sort() nativa, demostró ser muy eficiente con un tiempo de ~33ms para 12,792 registros. Su capacidad de detectar "runs" naturales en datos parcialmente ordenados lo hace especialmente adecuado para datos financieros, que típicamente presentan tendencia y orden parcial.

**Algoritmos a evitar para grandes volúmenes:**
Gnome Sort y Selection Sort, ambos con complejidad O(n²), resultaron impracticables para el volumen de datos usado, superando los 14 y 21 segundos respectivamente. Estos algoritmos deberían evitarse en aplicaciones que procesan grandes cantidades de datos.

### 7.2 Recomendaciones

Para procesamiento de datos financieros en producción, se recomienda:

- **Para datos principalmente numéricos y enteros:** Radix Sort o Pigeonhole Sort ofrecen el mejor rendimiento.
- **Para datos parcialmente ordenados:** TimSort es la elección más segura.
- **Para guarantee de rendimiento:** HeapSort siempre garantiza O(n log n).
- **Evitar:** Gnome Sort, Selection Sort y otros algoritmos O(n²) para volúmenes significativos.

---

## 8. Uso de Herramientas de Inteligencia Artificial

En el desarrollo de este proyecto se utilizó inteligencia artificial generativa como apoyo para la implementación. A continuación se documentan los usos realizados:

**Prompts relevantes utilizados:**

1. *Ayudame a hacer un proyecto basandote en los archivos llamados seguimiento 1 dentro de la carpeta docs, en el readme quiero que agregues toda la información relevante, ademas quiero que solo el codigo esté en ingles, todo lo demas (los comentarios, el readme, etc) en español*

2. *necesito que simplifiques la ejecución del proyecto con taskfile, la idea es poder ejecutar el proyecto solo con el comando task run u alguna herramienta similar, recuerda instalar todas las dependencias de python necesarias y usar un .venv*

3. *organiza un poco la grafica complexity_comparison, ya que como algunos algoritmos tienen un tiempo de ejecución y complejidad teorica similar, lo que hace que se sobrepongan los nombres, asi que mejor pon el nombre a la izquierda o la derecha del punto de color*

4. *aun se siguen sobreponiendo algunos nombres con otros, alguna idea?*

La IA se utilizó como soporte para la estructuración del proyecto, generación de código base y resolución de problemas técnicos. El diseño algorítmico, el análisis de complejidad y la documentación técnica fueron desarrollados de manera independiente para cumplir con los objetivos académicos del curso.

---

## 9. Ejecución del Proyecto

### Requisitos Previos
- Python 3.10+
- Taskfile (opcional pero recomendado)

### Comandos de Ejecución

```bash
# Primera vez - Instalación
task install    # Crea entorno virtual e instala dependencias

# Ejecución normal
task run        # Ejecuta el pipeline completo (usa datos de ejemplo)

# Para datos reales
task run-full   # Descarga datos reales desde Yahoo Finance
```

### Otros Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `task api` | Inicia el servidor API REST |
| `task test` | Ejecuta pruebas unitarias |
| `task clean` | Limpia archivos generados |
| `task lint` | Ejecuta linter de código |

---

## 10. Tecnologías Utilizadas

- **Python 3.10+**: Lenguaje de programación principal
- **requests**: Peticiones HTTP para extracción de datos
- **matplotlib**: Generación de visualizaciones
- **pandas**: Manipulación de datos
- **Flask**: API REST
- **Docker**: Contenedores

---

## 11. Referencias y Recursos

- Documentación del Seguimiento 1 - Universidad del Quindío
- Yahoo Finance API (fuente de datos)
- Documentación de Taskfile (https://taskfile.dev/)

---

*Proyecto desarrollado para el curso de Análisis de Algoritmos - Universidad del Quindío - 2026-1*
