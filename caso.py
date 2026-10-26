import json
import sys
import time
from ordenamientos import ALGORITMOS, generar

algoritmo, n = sys.argv[1], int(sys.argv[2])
# Calentamiento de la misma funcion fuera del intervalo medido.
ALGORITMOS[algoritmo](list(generar(200)))
a = list(generar(n))
cuentas = [0] * 100001
for v in a:
    cuentas[round(v * 100) + 50000] += 1
inicio = time.perf_counter()
a = ALGORITMOS[algoritmo](a)
segundos = time.perf_counter() - inicio
valido = len(a) == n
anterior = float('-inf')
for v in a:
    if v < anterior:
        valido = False
    anterior = v
    cuentas[round(v * 100) + 50000] -= 1
valido = valido and all(c == 0 for c in cuentas)
print(json.dumps(dict(segundos=segundos, valido=valido)), flush=True)
