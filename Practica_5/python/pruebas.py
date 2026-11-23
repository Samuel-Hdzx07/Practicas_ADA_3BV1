from __future__ import annotations

import random
import unittest

from programacion_dinamica import (
    cambio_formas_memoizado,
    cambio_formas_recursivo,
    cambio_formas_tabla,
    cambio_minimo_memoizado,
    cambio_minimo_recursivo,
    cambio_minimo_tabla,
    lcs_subcadena_memoizada,
    lcs_subcadena_recursiva,
    lcs_subcadena_tabla,
    lcs_subsecuencia_memoizada,
    lcs_subsecuencia_recursiva,
    lcs_subsecuencia_tabla,
    mochila_memoizada,
    mochila_recursiva,
    mochila_tabla,
)


def versiones_mochila(pesos, valores, capacidad):
    return (
        mochila_recursiva(pesos, valores, capacidad),
        mochila_memoizada(pesos, valores, capacidad),
        mochila_tabla(pesos, valores, capacidad),
    )


def oraculo_mochila(pesos, valores, capacidad):
    mejor = 0
    for mascara in range(1 << len(pesos)):
        peso_total = sum(pesos[i] for i in range(len(pesos)) if mascara & (1 << i))
        valor_total = sum(valores[i] for i in range(len(valores)) if mascara & (1 << i))
        if peso_total <= capacidad:
            mejor = max(mejor, valor_total)
    return mejor


def oraculo_cambio_minimo(monedas, cantidad):
    distancias = [None] * (cantidad + 1)
    distancias[0] = 0
    for actual in range(cantidad + 1):
        if distancias[actual] is None:
            continue
        for moneda in set(monedas):
            siguiente = actual + moneda
            if siguiente <= cantidad:
                candidato = distancias[actual] + 1
                if distancias[siguiente] is None or candidato < distancias[siguiente]:
                    distancias[siguiente] = candidato
    return distancias[cantidad]


def oraculo_formas(monedas, cantidad):
    coins = sorted(set(monedas))

    def enumerar(i, restante):
        if restante == 0:
            return 1
        if i == len(coins) or restante < 0:
            return 0
        return sum(enumerar(i + 1, restante - k * coins[i])
                   for k in range(restante // coins[i] + 1))

    return enumerar(0, cantidad)


def es_subsecuencia(candidata, texto):
    indice = 0
    for simbolo in texto:
        if indice < len(candidata) and candidata[indice] == simbolo:
            indice += 1
    return indice == len(candidata)


def oraculo_lcsq(a, b):
    corto, otro = (a, b) if len(a) <= len(b) else (b, a)
    mejor = 0
    for mascara in range(1 << len(corto)):
        candidata = "".join(corto[i] for i in range(len(corto)) if mascara & (1 << i))
        if len(candidata) > mejor and es_subsecuencia(candidata, otro):
            mejor = len(candidata)
    return mejor


def oraculo_subcadena(a, b):
    mejor = 0
    for inicio in range(len(a)):
        for fin in range(inicio + 1, len(a) + 1):
            if len(a[inicio:fin]) > mejor and a[inicio:fin] in b:
                mejor = fin - inicio
    return mejor


class PruebasProgramacionDinamica(unittest.TestCase):
    def test_mochila_casos_limite_y_oraculo_exhaustivo(self):
        casos = [
            ([], [], 0),
            ([1], [5], 0),
            ([3], [7], 2),
            ([2, 3, 4], [3, 4, 5], 5),
            ([10, 20, 30], [60, 100, 120], 50),
            ([1, 1, 2], [1, 1, 2], 2),
        ]
        self.assertEqual(versiones_mochila(*casos[3]), (7, 7, 7))
        self.assertEqual(versiones_mochila(*casos[4]), (220, 220, 220))
        rng = random.Random(2026)
        for _ in range(25):
            n = rng.randrange(0, 9)
            pesos = [rng.randrange(1, 10) for _ in range(n)]
            valores = [rng.randrange(0, 25) for _ in range(n)]
            capacidad = rng.randrange(0, 25)
            esperado = oraculo_mochila(pesos, valores, capacidad)
            self.assertEqual(versiones_mochila(pesos, valores, capacidad),
                             (esperado, esperado, esperado))
        with self.assertRaises(ValueError):
            mochila_tabla([1], [], 1)
        with self.assertRaises(ValueError):
            mochila_tabla([0], [1], 1)

    def test_cambio_minimo_y_cantidades_imposibles(self):
        casos = [
            ([], 0, 0),
            ([1, 3, 4], 6, 2),  # Evita el resultado subóptimo 4+1+1.
            ([4, 6], 5, None),
            ([2, 5], 3, None),
            ([5, 1, 3, 3], 6, 2),
        ]
        for monedas, cantidad, esperado in casos:
            resultados = (cambio_minimo_recursivo(monedas, cantidad),
                          cambio_minimo_memoizado(monedas, cantidad),
                          cambio_minimo_tabla(monedas, cantidad))
            self.assertEqual(resultados, (esperado, esperado, esperado))

        rng = random.Random(6025)
        for _ in range(25):
            monedas = [rng.randrange(1, 10) for _ in range(rng.randrange(0, 5))]
            cantidad = rng.randrange(0, 22)
            esperado = oraculo_cambio_minimo(monedas, cantidad)
            resultados = (cambio_minimo_recursivo(monedas, cantidad),
                          cambio_minimo_memoizado(monedas, cantidad),
                          cambio_minimo_tabla(monedas, cantidad))
            self.assertEqual(resultados, (esperado, esperado, esperado))
        with self.assertRaises(ValueError):
            cambio_minimo_tabla([0, 1], 4)

    def test_cambio_formas_conteo_de_combinaciones(self):
        casos = [([], 0, 1), ([], 5, 0), ([1, 2, 5], 5, 4),
                 ([2, 5], 3, 0), ([1, 2, 2], 4, 3)]
        for monedas, cantidad, esperado in casos:
            resultados = (cambio_formas_recursivo(monedas, cantidad),
                          cambio_formas_memoizado(monedas, cantidad),
                          cambio_formas_tabla(monedas, cantidad))
            self.assertEqual(resultados, (esperado, esperado, esperado))

        rng = random.Random(5120)
        for _ in range(20):
            monedas = [rng.randrange(1, 8) for _ in range(rng.randrange(0, 5))]
            cantidad = rng.randrange(0, 16)
            esperado = oraculo_formas(monedas, cantidad)
            resultados = (cambio_formas_recursivo(monedas, cantidad),
                          cambio_formas_memoizado(monedas, cantidad),
                          cambio_formas_tabla(monedas, cantidad))
            self.assertEqual(resultados, (esperado, esperado, esperado))

    def test_lcs_subsecuencia_con_oraculo(self):
        casos = [("", "", 0), ("ABC", "", 0), ("ABC", "DEF", 0),
                 ("ABCD", "XBDY", 2), ("XABYCDZ", "QABRCDS", 4),
                 ("ABCBDAB", "BDCABA", 4), ("😀x", "a😀x", 2)]
        for a, b, esperado in casos:
            resultados = (lcs_subsecuencia_recursiva(a, b),
                          lcs_subsecuencia_memoizada(a, b),
                          lcs_subsecuencia_tabla(a, b))
            self.assertEqual(resultados, (esperado, esperado, esperado))

        rng = random.Random(5230)
        for _ in range(25):
            a = "".join(rng.choice("ABC") for _ in range(rng.randrange(0, 9)))
            b = "".join(rng.choice("ABC") for _ in range(rng.randrange(0, 9)))
            esperado = oraculo_lcsq(a, b)
            resultados = (lcs_subsecuencia_recursiva(a, b),
                          lcs_subsecuencia_memoizada(a, b),
                          lcs_subsecuencia_tabla(a, b))
            self.assertEqual(resultados, (esperado, esperado, esperado))

    def test_lcs_subcadena_contigua_con_oraculo(self):
        casos = [("", "", 0), ("ABC", "", 0), ("ABC", "DEF", 0),
                 ("ABCD", "XBDY", 1), ("XABYCDZ", "QABRCDS", 2),
                 ("ABC", "ZABCZ", 3), ("😀x", "a😀x", 2)]
        for a, b, esperado in casos:
            resultados = (lcs_subcadena_recursiva(a, b),
                          lcs_subcadena_memoizada(a, b),
                          lcs_subcadena_tabla(a, b))
            self.assertEqual(resultados, (esperado, esperado, esperado))

        rng = random.Random(5231)
        for _ in range(25):
            a = "".join(rng.choice("ABC") for _ in range(rng.randrange(0, 9)))
            b = "".join(rng.choice("ABC") for _ in range(rng.randrange(0, 9)))
            esperado = oraculo_subcadena(a, b)
            resultados = (lcs_subcadena_recursiva(a, b),
                          lcs_subcadena_memoizada(a, b),
                          lcs_subcadena_tabla(a, b))
            self.assertEqual(resultados, (esperado, esperado, esperado))


if __name__ == "__main__":
    unittest.main(verbosity=2)
