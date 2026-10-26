from ordenamientos import ALGORITMOS, generar

casos = [[], [1], [3, 2, 1], [-1, 0, -1, 2], [1, 2, 3],
         [2.25, -1.5, 0, 2.25], list(generar(500))]
for nombre, funcion in ALGORITMOS.items():
    for caso in casos:
        assert funcion(caso.copy()) == sorted(caso), nombre
print('35 pruebas Python correctas')
