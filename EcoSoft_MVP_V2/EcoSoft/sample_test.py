# sample_test.py
# Archivo de prueba para EcoSoft – contiene varios patrones costosos

def bubble_sort(arr):
    """Ordenamiento burbuja con bucles anidados."""
    n = len(arr)
    for i in range(n):          # bucle externo
        for j in range(n - 1):  # bucle interno (anidado)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def factorial(n):
    """Cálculo factorial recursivo."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # llamada recursiva


def fibonacci(n):
    """Fibonacci recursivo (doble recursividad)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # dos llamadas recursivas


def get_squares(limit):
    """List comprehension para cuadrados."""
    squares = [x ** 2 for x in range(limit)]
    return squares


def get_evens(numbers):
    """Otra list comprehension."""
    return [n for n in numbers if n % 2 == 0]


def process_data(data):
    """Procesamiento con bucle simple."""
    result = []
    for item in data:
        result.append(item * 2)
    return result


# Función con nombre repetido (redundancia)
def process_data(data):
    """Segunda definición de process_data."""
    return [d + 1 for d in data]


if __name__ == "__main__":
    print(bubble_sort([5, 3, 8, 1]))
    print(factorial(6))
    print(get_squares(10))
