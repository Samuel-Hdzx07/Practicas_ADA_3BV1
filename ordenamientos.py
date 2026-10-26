"""Cinco ordenamientos propios. Datos de la practica: centesimas exactas."""
def bubble_sort(a):
    for fin in range(len(a) - 1, 0, -1):
        cambio = False
        for j in range(fin):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                cambio = True
        if not cambio:
            break
    return a


def merge_sort(a):
    n = len(a)
    aux = [0.0] * n
    ancho = 1
    while ancho < n:
        for inicio in range(0, n, 2 * ancho):
            medio, fin = min(inicio + ancho, n), min(inicio + 2 * ancho, n)
            i, j, k = inicio, medio, inicio
            while i < medio and j < fin:
                if a[i] <= a[j]:
                    aux[k] = a[i]; i += 1
                else:
                    aux[k] = a[j]; j += 1
                k += 1
            while i < medio:
                aux[k] = a[i]; i += 1; k += 1
            while j < fin:
                aux[k] = a[j]; j += 1; k += 1
        a, aux = aux, a
        ancho *= 2
    return a


class Nodo:
    __slots__ = ('valor', 'cantidad', 'izq', 'der')
    def __init__(self, valor):
        self.valor, self.cantidad = valor, 1
        self.izq = self.der = None


def tree_sort(a):
    raiz = None
    for valor in a:
        if raiz is None:
            raiz = Nodo(valor); continue
        actual = raiz
        while True:
            if valor == actual.valor:
                actual.cantidad += 1; break
            lado = 'izq' if valor < actual.valor else 'der'
            siguiente = getattr(actual, lado)
            if siguiente is None:
                setattr(actual, lado, Nodo(valor)); break
            actual = siguiente
    pila, actual, i = [], raiz, 0
    while actual is not None or pila:
        while actual is not None:
            pila.append(actual); actual = actual.izq
        actual = pila.pop()
        for _ in range(actual.cantidad):
            a[i] = actual.valor; i += 1
        actual = actual.der
    return a


def heap_sort(a):
    def bajar(raiz, fin):
        while 2 * raiz + 1 < fin:
            hijo = 2 * raiz + 1
            if hijo + 1 < fin and a[hijo] < a[hijo + 1]:
                hijo += 1
            if a[raiz] >= a[hijo]:
                break
            a[raiz], a[hijo] = a[hijo], a[raiz]
            raiz = hijo
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        bajar(i, n)
    for fin in range(n - 1, 0, -1):
        a[0], a[fin] = a[fin], a[0]
        bajar(0, fin)
    return a


def counting_sort(a):
    # Claves enteras correspondientes a reales con exactamente dos decimales.
    if not a:
        return a
    minimo = round(min(a) * 100)
    maximo = round(max(a) * 100)
    if maximo - minimo > 1_000_000:
        raise ValueError('Rango demasiado grande para Counting Sort')
    cuentas = [0] * (maximo - minimo + 1)
    for valor in a:
        clave = round(valor * 100)
        if abs(valor * 100 - clave) > 1e-7:
            raise ValueError('Se requieren valores en centesimas')
        cuentas[clave - minimo] += 1
    pos = 0
    for i, cantidad in enumerate(cuentas):
        for _ in range(cantidad):
            a[pos] = (i + minimo) / 100.0; pos += 1
    return a


ALGORITMOS = dict(bubble=bubble_sort, merge=merge_sort, tree=tree_sort,
                  heap=heap_sort, counting=counting_sort)


def generar(n, semilla=2026):
    estado = semilla
    for _ in range(n):
        estado = (1664525 * estado + 1013904223) & 0xffffffff
        yield ((estado % 100001) - 50000) / 100.0
