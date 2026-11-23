"""Soluciones de referencia para los problemas de la práctica 5.

Supuestos: mochila 0/1; cambio ilimitado con objetivo de minimizar monedas;
LCSq mide subsecuencia común y LCS mide subcadena contigua común. También se
incluye, como variante adicional de cambio, el conteo de combinaciones.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Sequence


def _validar_mochila(pesos: Sequence[int], valores: Sequence[int], capacidad: int) -> None:
    if len(pesos) != len(valores):
        raise ValueError("pesos y valores deben tener la misma longitud")
    if capacidad < 0:
        raise ValueError("la capacidad no puede ser negativa")
    if any(peso <= 0 for peso in pesos):
        raise ValueError("los pesos deben ser enteros positivos")
    if any(valor < 0 for valor in valores):
        raise ValueError("los valores no pueden ser negativos")


def mochila_recursiva(pesos: Sequence[int], valores: Sequence[int], capacidad: int) -> int:
    """Mochila 0/1 por recurrencia directa; complejidad O(2^n)."""
    _validar_mochila(pesos, valores, capacidad)

    def resolver(i: int, restante: int) -> int:
        if i == 0 or restante == 0:
            return 0
        if pesos[i - 1] > restante:
            return resolver(i - 1, restante)
        return max(
            resolver(i - 1, restante),
            valores[i - 1] + resolver(i - 1, restante - pesos[i - 1]),
        )

    return resolver(len(pesos), capacidad)


def mochila_memoizada(pesos: Sequence[int], valores: Sequence[int], capacidad: int) -> int:
    """Mochila 0/1 top-down; O(nC) tiempo y memoria en el peor caso."""
    _validar_mochila(pesos, valores, capacidad)

    @lru_cache(maxsize=None)
    def resolver(i: int, restante: int) -> int:
        if i == 0 or restante == 0:
            return 0
        if pesos[i - 1] > restante:
            return resolver(i - 1, restante)
        return max(
            resolver(i - 1, restante),
            valores[i - 1] + resolver(i - 1, restante - pesos[i - 1]),
        )

    return resolver(len(pesos), capacidad)


def mochila_tabla(pesos: Sequence[int], valores: Sequence[int], capacidad: int) -> int:
    """Mochila 0/1 bottom-up; O(nC) tiempo y memoria."""
    _validar_mochila(pesos, valores, capacidad)
    n = len(pesos)
    dp = [[0] * (capacidad + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        peso, valor = pesos[i - 1], valores[i - 1]
        for c in range(capacidad + 1):
            dp[i][c] = dp[i - 1][c]
            if peso <= c:
                dp[i][c] = max(dp[i][c], valor + dp[i - 1][c - peso])
    return dp[n][capacidad]


def _normalizar_monedas(monedas: Sequence[int], cantidad: int) -> tuple[int, ...]:
    if cantidad < 0:
        raise ValueError("la cantidad no puede ser negativa")
    if any(moneda <= 0 for moneda in monedas):
        raise ValueError("las denominaciones deben ser enteros positivos")
    return tuple(sorted(set(monedas)))


def cambio_minimo_recursivo(monedas: Sequence[int], cantidad: int) -> int | None:
    """Mínimo de monedas con reutilización ilimitada; None si no hay solución."""
    coins = _normalizar_monedas(monedas, cantidad)
    infinito = cantidad + 1

    def resolver(restante: int) -> int:
        if restante == 0:
            return 0
        mejor = infinito
        for moneda in coins:
            if moneda > restante:
                break
            anterior = resolver(restante - moneda)
            if anterior < infinito:
                mejor = min(mejor, anterior + 1)
        return mejor

    resultado = resolver(cantidad)
    return None if resultado == infinito else resultado


def cambio_minimo_memoizado(monedas: Sequence[int], cantidad: int) -> int | None:
    coins = _normalizar_monedas(monedas, cantidad)
    infinito = cantidad + 1

    @lru_cache(maxsize=None)
    def resolver(restante: int) -> int:
        if restante == 0:
            return 0
        mejor = infinito
        for moneda in coins:
            if moneda > restante:
                break
            anterior = resolver(restante - moneda)
            if anterior < infinito:
                mejor = min(mejor, anterior + 1)
        return mejor

    resultado = resolver(cantidad)
    return None if resultado == infinito else resultado


def cambio_minimo_tabla(monedas: Sequence[int], cantidad: int) -> int | None:
    coins = _normalizar_monedas(monedas, cantidad)
    infinito = cantidad + 1
    dp = [infinito] * (cantidad + 1)
    dp[0] = 0
    for total in range(1, cantidad + 1):
        for moneda in coins:
            if moneda > total:
                break
            if dp[total - moneda] != infinito:
                dp[total] = min(dp[total], dp[total - moneda] + 1)
    return None if dp[cantidad] == infinito else dp[cantidad]


def cambio_formas_recursivo(monedas: Sequence[int], cantidad: int) -> int:
    """Cantidad de combinaciones (orden irrelevante), con uso ilimitado."""
    coins = _normalizar_monedas(monedas, cantidad)

    def resolver(i: int, restante: int) -> int:
        if restante == 0:
            return 1
        if restante < 0 or i == len(coins):
            return 0
        return resolver(i + 1, restante) + resolver(i, restante - coins[i])

    return resolver(0, cantidad)


def cambio_formas_memoizado(monedas: Sequence[int], cantidad: int) -> int:
    coins = _normalizar_monedas(monedas, cantidad)

    @lru_cache(maxsize=None)
    def resolver(i: int, restante: int) -> int:
        if restante == 0:
            return 1
        if restante < 0 or i == len(coins):
            return 0
        return resolver(i + 1, restante) + resolver(i, restante - coins[i])

    return resolver(0, cantidad)


def cambio_formas_tabla(monedas: Sequence[int], cantidad: int) -> int:
    coins = _normalizar_monedas(monedas, cantidad)
    dp = [0] * (cantidad + 1)
    dp[0] = 1
    for moneda in coins:
        for total in range(moneda, cantidad + 1):
            dp[total] += dp[total - moneda]
    return dp[cantidad]


def lcs_subsecuencia_recursiva(a: str, b: str) -> int:
    """Longitud de la subsecuencia común más larga (LCSq), O(2^(m+n))."""
    return _lcs_subsecuencia_sin_cache(a, b, 0, 0)


def _lcs_subsecuencia_sin_cache(a: str, b: str, i: int, j: int) -> int:
    if i == len(a) or j == len(b):
        return 0
    if a[i] == b[j]:
        return 1 + _lcs_subsecuencia_sin_cache(a, b, i + 1, j + 1)
    return max(
        _lcs_subsecuencia_sin_cache(a, b, i + 1, j),
        _lcs_subsecuencia_sin_cache(a, b, i, j + 1),
    )


def lcs_subsecuencia_memoizada(a: str, b: str) -> int:
    @lru_cache(maxsize=None)
    def resolver(i: int, j: int) -> int:
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + resolver(i + 1, j + 1)
        return max(resolver(i + 1, j), resolver(i, j + 1))

    return resolver(0, 0)


def lcs_subsecuencia_tabla(a: str, b: str) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def lcs_subcadena_recursiva(a: str, b: str) -> int:
    """Longitud de la subcadena común más larga; coincidencias contiguas."""
    def racha(i: int, j: int) -> int:
        if i == len(a) or j == len(b) or a[i] != b[j]:
            return 0
        return 1 + racha(i + 1, j + 1)

    def mejor(i: int, j: int) -> int:
        if i == len(a) or j == len(b):
            return 0
        return max(racha(i, j), mejor(i + 1, j), mejor(i, j + 1))

    return mejor(0, 0)


def lcs_subcadena_memoizada(a: str, b: str) -> int:
    @lru_cache(maxsize=None)
    def racha(i: int, j: int) -> int:
        if i == len(a) or j == len(b) or a[i] != b[j]:
            return 0
        return 1 + racha(i + 1, j + 1)

    @lru_cache(maxsize=None)
    def mejor(i: int, j: int) -> int:
        if i == len(a) or j == len(b):
            return 0
        return max(racha(i, j), mejor(i + 1, j), mejor(i, j + 1))

    return mejor(0, 0)


def lcs_subcadena_tabla(a: str, b: str) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    mejor = 0
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                mejor = max(mejor, dp[i][j])
    return mejor
