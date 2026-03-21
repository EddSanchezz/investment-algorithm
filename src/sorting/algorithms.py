"""
Sorting Algorithms Module - Implementación de 12 algoritmos de ordenamiento.
Cada algoritmo incluye análisis de complejidad algorítmica documentado.
"""


class SortingAlgorithms:
    """
    Colección de algoritmos de ordenamiento con análisis de complejidad.

    Los algoritmos están implementados de forma explícita para demostrar
    comprensión del funcionamiento interno y permitir análisis de rendimiento.

    Estructura de datos usada: Lista de diccionarios con clave 'sort_key'
    Cada diccionario representa un registro financiero a ordenar.
    """

    def __init__(self):
        self.comparison_count = 0
        self.swap_count = 0

    def reset_counters(self):
        """Reinicia los contadores de comparaciones e intercambios."""
        self.comparison_count = 0
        self.swap_count = 0

    # =========================================================================
    # 1. TIM SORT - O(n log n) promedio y peor caso
    # =========================================================================
    """
    TimSort combina ordenamiento por inserción (para pequeños bloques) con
    mezcla de sub-arreglos ordenados (mergesort).
    
    Análisis de complejidad:
    - Mejor caso: O(n) cuando ya está ordenado
    - Peor caso: O(n log n)
    - Promedio: O(n log n)
    
    Justificación: En datos parcialmente ordenados (común en series temporales
    financieras), TimSort es altamente eficiente porque detecta "runs"
    (secuencias ordenadas naturalmente).
    """

    MIN_MERGE = 32

    def tim_sort(self, arr: list) -> list:
        """
        Implementación de TimSort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n log n) en la mayoría de los casos
        """
        self.reset_counters()
        n = len(arr)

        if n <= 1:
            return arr.copy()

        def calc_min_run(n: int) -> int:
            r = 0
            while n >= self.MIN_MERGE:
                r |= n & 1
                n >>= 1
            return n + r

        def insertion_sort(left: int, right: int) -> None:
            for i in range(left + 1, right + 1):
                key = arr[i]
                j = i - 1
                while j >= left:
                    self.comparison_count += 1
                    if arr[j]["sort_key"] > key["sort_key"]:
                        arr[j + 1] = arr[j]
                        self.swap_count += 1
                        j -= 1
                    else:
                        break
                arr[j + 1] = key

        def merge(left: int, mid: int, right: int) -> None:
            left_arr = arr[left : mid + 1]
            right_arr = arr[mid + 1 : right + 1]

            i = j = 0
            k = left

            while i < len(left_arr) and j < len(right_arr):
                self.comparison_count += 1
                if left_arr[i]["sort_key"] <= right_arr[j]["sort_key"]:
                    arr[k] = left_arr[i]
                    i += 1
                else:
                    arr[k] = right_arr[j]
                    j += 1
                k += 1

            while i < len(left_arr):
                arr[k] = left_arr[i]
                i += 1
                k += 1

            while j < len(right_arr):
                arr[k] = right_arr[j]
                j += 1
                k += 1

        min_run = calc_min_run(n)

        for start in range(0, n, min_run):
            end = min(start + min_run - 1, n - 1)
            insertion_sort(start, end)

        size = min_run
        while size < n:
            for left in range(0, n, 2 * size):
                mid = min(n - 1, left + size - 1)
                right = min(left + 2 * size - 1, n - 1)
                if mid < right:
                    merge(left, mid, right)
            size *= 2

        return arr.copy()

    # =========================================================================
    # 2. COMB SORT - O(n²) pero mejorado sobre Bubble Sort
    # =========================================================================
    """
    Comb Sort es una mejora de Bubble Sort que usa "gaps" (espacios) decrecientes
    para eliminar valores pequeños al final de la lista (turtles).
    
    Análisis de complejidad:
    - Mejor caso: O(n)
    - Peor caso: O(n²)
    - Promedio: O(n²/2^p) donde p es el número de iteraciones
    
    La constante de reducción típica es 1.3 (determinada empíricamente).
    """

    SHRINK_FACTOR = 1.3

    def comb_sort(self, arr: list) -> list:
        """
        Implementación de Comb Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n²) promedio, optimizado vs Bubble Sort
        """
        self.reset_counters()
        n = len(arr)
        arr = arr.copy()
        gap = n
        sorted_ = False

        while not sorted_:
            gap = int(gap / self.SHRINK_FACTOR)
            if gap <= 1:
                gap = 1
                sorted_ = True

            i = 0
            while i + gap < n:
                self.comparison_count += 1
                if arr[i]["sort_key"] > arr[i + gap]["sort_key"]:
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    self.swap_count += 1
                    sorted_ = False
                i += 1

        return arr

    # =========================================================================
    # 3. SELECTION SORT - O(n²)
    # =========================================================================
    """
    Selection Sort divide la lista en sublista ordenada y no ordenada.
    Encuentra el mínimo en la sublista no ordenada y lo intercambia.
    
    Análisis de complejidad:
    - Mejor caso: O(n²)
    - Peor caso: O(n²)
    - Promedio: O(n²)
    
    Ventaja: Mínimo número de escrituras (intercambios) = O(n)
    Desventaja: No es estable naturalmente, hace n² comparaciones siempre.
    """

    def selection_sort(self, arr: list) -> list:
        """
        Implementación de Selection Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n²) - siempre hace n² comparaciones
        """
        self.reset_counters()
        n = len(arr)
        arr = arr.copy()

        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self.comparison_count += 1
                if arr[j]["sort_key"] < arr[min_idx]["sort_key"]:
                    min_idx = j

            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.swap_count += 1

        return arr

    # =========================================================================
    # 4. TREE SORT - O(n log n)
    # =========================================================================
    """
    Tree Sort construye un BST (Binary Search Tree) y luego hace un
    recorrido in-order para obtener los elementos ordenados.
    
    Análisis de complejidad:
    - Mejor caso (árbol balanceado): O(n log n)
    - Peor caso (árbol degenerado): O(n²)
    - Promedio: O(n log n)
    
    Usa BST en lugar de árbol balanceado para simplicidad.
    """

    class TreeNode:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    def tree_sort(self, arr: list) -> list:
        """
        Implementación de Tree Sort usando BST.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n log n) promedio, O(n²) peor caso
        """
        self.reset_counters()

        if not arr:
            return []

        def insert(node, value):
            if node is None:
                return self.TreeNode(value)

            if value["sort_key"] < node.value["sort_key"]:
                node.left = insert(node.left, value)
            else:
                node.right = insert(node.right, value)

            return node

        def inorder(node, result):
            if node:
                inorder(node.left, result)
                result.append(node.value)
                inorder(node.right, result)

        root = None
        for item in arr:
            root = insert(root, item)

        result = []
        inorder(root, result)

        self.comparison_count = len(arr) * (len(arr) - 1) // 2

        return result

    # =========================================================================
    # 5. PIGEONHOLE SORT - O(n + k)
    # =========================================================================
    """
    Pigeonhole Sort es útil cuando el rango de valores (k) es menor que
    el número de elementos (n).
    
    Análisis de complejidad:
    - Tiempo: O(n + k) donde k = rango de valores
    - Espacio: O(k)
    
    Limitación: Solo funciona con enteros positivos y rango conocido.
    """

    def pigeonhole_sort(self, arr: list) -> list:
        """
        Implementación de Pigeonhole Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key' (valores numéricos)

        Retorna:
            Lista ordenada

        Complejidad: O(n + k) donde k = rango de valores
        """
        self.reset_counters()

        if not arr:
            return []

        min_val = min(arr, key=lambda x: x["sort_key"])["sort_key"]
        max_val = max(arr, key=lambda x: x["sort_key"])["sort_key"]

        if isinstance(min_val, float):
            scale = 100
            min_val = int(min_val * scale)
            max_val = int(max_val * scale)
            arr = [
                {
                    "sort_key": int(x["sort_key"] * scale),
                    **{k: v for k, v in x.items() if k != "sort_key"},
                }
                for x in arr
            ]

        range_size = max_val - min_val + 1
        holes = [[] for _ in range(range_size)]

        for item in arr:
            holes[item["sort_key"] - min_val].append(item)
            self.comparison_count += 1

        result = []
        for hole in holes:
            for item in hole:
                result.append(item)

        return result

    # =========================================================================
    # 6. BUCKET SORT - O(n + k)
    # =========================================================================
    """
    Bucket Sort distribuye elementos en "buckets" (contenedores) y luego
    ordena cada bucket individualmente.
    
    Análisis de complejidad:
    - Mejor caso: O(n + k) cuando todos los buckets tienen distribución uniforme
    - Peor caso: O(n²) cuando todos los elementos caen en un bucket
    
    Necesita un algoritmo de ordenamiento secundario para los buckets.
    """

    def bucket_sort(self, arr: list, num_buckets: int = 10) -> list:
        """
        Implementación de Bucket Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'
            num_buckets: Número de buckets a usar

        Retorna:
            Lista ordenada

        Complejidad: O(n + k) promedio, O(n²) peor caso
        """
        self.reset_counters()

        if not arr:
            return []

        values = [x["sort_key"] for x in arr]
        min_val = min(values)
        max_val = max(values)

        buckets = [[] for _ in range(num_buckets)]
        range_size = (max_val - min_val) / num_buckets if num_buckets > 0 else 1

        for item in arr:
            idx = (
                min(int((item["sort_key"] - min_val) / range_size), num_buckets - 1)
                if range_size > 0
                else 0
            )
            buckets[idx].append(item)
            self.comparison_count += 1

        for bucket in buckets:
            bucket.sort(key=lambda x: x["sort_key"])

        result = []
        for bucket in buckets:
            result.extend(bucket)

        return result

    # =========================================================================
    # 7. QUICKSORT - O(n log n) promedio
    # =========================================================================
    """
    QuickSort usa la estrategia "divide y vencerás":
    1. Selecciona un pivote
    2. Particiona: elementos menores a un lado, mayores al otro
    3. Ordena recursivamente las particiones
    
    Análisis de complejidad:
    - Mejor caso: O(n log n) con pivote equilibrado
    - Peor caso: O(n²) cuando el pivote es siempre el mínimo/máximo
    - Promedio: O(n log n)
    
    Implementamos la versión de partición de Lomuto.
    """

    def quicksort(self, arr: list, low: int = None, high: int = None) -> list:
        """
        Implementación de QuickSort con partición de Lomuto.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'
            low: Índice inferior (default: 0)
            high: Índice superior (default: len-1)

        Retorna:
            Lista ordenada

        Complejidad: O(n log n) promedio, O(n²) peor caso
        """
        self.reset_counters()
        arr = arr.copy()

        if low is None:
            low = 0
        if high is None:
            high = len(arr) - 1

        def partition(low: int, high: int) -> int:
            pivot = arr[high]["sort_key"]
            i = low - 1

            for j in range(low, high):
                self.comparison_count += 1
                if arr[j]["sort_key"] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    self.swap_count += 1

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            self.swap_count += 1
            return i + 1

        def quicksort_recursive(low: int, high: int) -> None:
            if low < high:
                pivot_idx = partition(low, high)
                quicksort_recursive(low, pivot_idx - 1)
                quicksort_recursive(pivot_idx + 1, high)

        if len(arr) > 1:
            quicksort_recursive(low, high)

        return arr

    # =========================================================================
    # 8. HEAPSORT - O(n log n)
    # =========================================================================
    """
    HeapSort usa una estructura de datos heap (montículo) para ordenar.
    
    Paso 1: Construir max-heap desde el arreglo (O(n))
    Paso 2: Extraer máximo repetidamente y reacomodar heap (O(n log n))
    
    Análisis de complejidad:
    - Mejor caso: O(n log n)
    - Peor caso: O(n log n) - siempre
    - Promedio: O(n log n)
    
    Ventaja: Garantiza O(n log n) en todos los casos.
    Desventaja: No es estable.
    """

    def heapsort(self, arr: list) -> list:
        """
        Implementación de HeapSort con max-heap.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n log n) en todos los casos
        """
        self.reset_counters()
        n = len(arr)
        arr = arr.copy()

        def heapify(size: int, root: int) -> None:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < size:
                self.comparison_count += 1
                if arr[left]["sort_key"] > arr[largest]["sort_key"]:
                    largest = left

            if right < size:
                self.comparison_count += 1
                if arr[right]["sort_key"] > arr[largest]["sort_key"]:
                    largest = right

            if largest != root:
                arr[root], arr[largest] = arr[largest], arr[root]
                self.swap_count += 1
                heapify(size, largest)

        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)

        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self.swap_count += 1
            heapify(i, 0)

        return arr

    # =========================================================================
    # 9. BITONIC SORT - O(log² n)
    # =========================================================================
    """
    Bitonic Sort es un algoritmo de ordenamiento paralelo basado en
    comparaciones y ordenamiento de bitonic sequences.
    
    Análisis de complejidad:
    - Tiempo: O(log² n) para n = 2^k
    - Muy eficiente en arquitecturas paralelas (PRAM model)
    
    Limitación: Solo funciona para arregles de longitud 2^k.
    """

    def bitonic_sort(self, arr: list, ascending: bool = True) -> list:
        """
        Implementación de Bitonic Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'
            ascending: Orden ascendente o descendente

        Retorna:
            Lista ordenada

        Complejidad: O(log² n)
        """
        self.reset_counters()

        n = len(arr)
        if n == 0 or (n & (n - 1)) != 0:
            next_pow2 = 1
            while next_pow2 < n:
                next_pow2 *= 2
            arr = arr + [{"sort_key": float("inf")} for _ in range(next_pow2 - n)]

        arr = arr.copy()

        def compare_and_swap(i: int, j: int, direction: bool) -> None:
            if direction != (arr[i]["sort_key"] > arr[j]["sort_key"]):
                arr[i], arr[j] = arr[j], arr[i]
                self.swap_count += 1
            self.comparison_count += 1

        def bitonic_merge(start: int, size: int, direction: bool) -> None:
            if size > 1:
                k = size // 2
                for i in range(start, start + k):
                    compare_and_swap(i, i + k, direction)
                bitonic_merge(start, k, direction)
                bitonic_merge(start + k, k, direction)

        def bitonic_sort_recursive(start: int, size: int, direction: bool) -> None:
            if size > 1:
                k = size // 2
                bitonic_sort_recursive(start, k, True)
                bitonic_sort_recursive(start + k, k, False)
                bitonic_merge(start, size, direction)

        size = len(arr)
        k = 1
        while k < size:
            k *= 2

        bitonic_sort_recursive(0, k, ascending)

        return arr[:n]

    # =========================================================================
    # 10. GNOME SORT - O(n²)
    # =========================================================================
    """
    Gnome Sort es similar a Insertion Sort pero con un enfoque diferente.
    El algoritmo "camina" por el arreglo, ajustando elementos como un gnomo
    que organiza macetas.
    
    Análisis de complejidad:
    - Mejor caso: O(n) cuando ya está ordenado
    - Peor caso: O(n²)
    - Promedio: O(n²)
    
    Ventaja: Código muy simple e intuitivo.
    """

    def gnome_sort(self, arr: list) -> list:
        """
        Implementación de Gnome Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n²) promedio
        """
        self.reset_counters()
        arr = arr.copy()
        n = len(arr)
        index = 0

        while index < n:
            if index == 0:
                index += 1

            self.comparison_count += 1
            if arr[index]["sort_key"] >= arr[index - 1]["sort_key"]:
                index += 1
            else:
                arr[index], arr[index - 1] = arr[index - 1], arr[index]
                self.swap_count += 1
                index -= 1

        return arr

    # =========================================================================
    # 11. BINARY INSERTION SORT - O(n²)
    # =========================================================================
    """
    Binary Insertion Sort usa búsqueda binaria para encontrar la posición
    de inserción, reduciendo comparaciones de O(n²) a O(n log n).
    
    Análisis de complejidad:
    - Búsqueda: O(log n) por elemento
    - Inserción: O(n) por elemento (shift)
    - Total: O(n²) pero con menos comparaciones que Insertion Sort normal
    
    Ventaja: Reduce el factor de comparaciones significativamente.
    """

    def binary_insertion_sort(self, arr: list) -> list:
        """
        Implementación de Binary Insertion Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(n²) pero con O(n log n) comparaciones
        """
        self.reset_counters()
        arr = arr.copy()
        n = len(arr)

        def binary_search(arr: list, item, low: int, high: int) -> int:
            while low < high:
                mid = (low + high) // 2
                self.comparison_count += 1
                if arr[mid]["sort_key"] < item["sort_key"]:
                    low = mid + 1
                else:
                    high = mid
            return low

        for i in range(1, n):
            key = arr[i]
            pos = binary_search(arr, key, 0, i)

            j = i - 1
            while j >= pos:
                arr[j + 1] = arr[j]
                self.swap_count += 1
                j -= 1

            arr[pos] = key

        return arr

    # =========================================================================
    # 12. RADIX SORT - O(nk)
    # =========================================================================
    """
    Radix Sort ordena elemento por elemento (dígitos/caracteres).
    Usa counting sort como algoritmo auxiliar para cada posición.
    
    Análisis de complejidad:
    - Tiempo: O(nk) donde k = número de dígitos
    - Espacio: O(n + k)
    
    Ventaja: Performance lineal para enteros con rango limitado.
    Desventaja: Requiere dígitos con orden natural (0-9).
    """

    def radix_sort(self, arr: list) -> list:
        """
        Implementación de Radix Sort (LSD - Least Significant Digit).

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'

        Retorna:
            Lista ordenada

        Complejidad: O(nk) donde k = número de dígitos
        """
        self.reset_counters()

        if not arr:
            return []

        values = [x["sort_key"] for x in arr]

        if isinstance(values[0], float):
            scale = 100
            values = [int(v * scale) for v in values]
            arr = [
                {
                    "sort_key": int(x["sort_key"] * scale),
                    **{k: v for k, v in x.items() if k != "sort_key"},
                }
                for x in arr
            ]
        else:
            values = [int(v) for v in values]

        max_val = max(values)
        exp = 1

        while max_val // exp > 0:
            self.radix_counting_sort(arr, exp)
            exp *= 10

        return arr

    def radix_counting_sort(self, arr: list, exp: int) -> None:
        """
        Counting Sort auxiliar para Radix Sort.

        Parámetros:
            arr: Lista de diccionarios con clave 'sort_key'
            exp: Posición decimal actual

        Complejidad: O(n + k) donde k = 10 (dígitos 0-9)
        """
        n = len(arr)
        output = [None] * n
        count = [0] * 10

        for item in arr:
            digit = int(item["sort_key"] // exp) % 10
            count[digit] += 1
            self.comparison_count += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        for i in range(n - 1, -1, -1):
            digit = int(arr[i]["sort_key"] // exp) % 10
            output[count[digit] - 1] = arr[i]
            count[digit] -= 1

        for i in range(n):
            arr[i] = output[i]
            self.swap_count += 1
