# Prácticas ADA 3BV1

Hernandez Barrios Samuel Rodrigo · Profesor ANDRES GARCIA FLORIANO

## Práctica 2 — Complejidad en ordenamiento

Cinco algoritmos propios en Java y Python: Bubble, Merge, Tree, Heap y Counting.
Incluye pruebas, mediciones crudas, resumen, matriz de cobertura, entorno, reporte
con tablas y gráficas y un ZIP con la estructura completa de carpetas.

### Estado experimental

Hay **31 de 50 combinaciones solicitadas con al menos una ejecución terminada
y validada**. El resto no tiene medición completa por restricciones de memoria
o tiempo. Esto no significa que estén satisfechas todas las longitudes de la
consigna. `cobertura.csv` registra cada combinación y su motivo.

| Lenguaje / algoritmo | 100 mil | 1 millón | 10 millones | 100 millones | Mil millones |
|---|---|---|---|---|---|
| Python bubble | OK (1) | Sin completar | Sin completar | Sin completar | Sin completar |
| Python merge | OK (3) | OK (3) | OK (1) | Sin completar | Sin completar |
| Python tree | OK (3) | OK (3) | OK (1) | Sin completar | Sin completar |
| Python heap | OK (3) | OK (3) | OK (1) | Sin completar | Sin completar |
| Python counting | OK (3) | OK (3) | OK (1) | OK (1) | Sin completar |
| Java bubble | OK (3) | Sin completar | Sin completar | Sin completar | Sin completar |
| Java merge | OK (3) | OK (3) | OK (3) | OK (3) | Sin completar |
| Java tree | OK (3) | OK (3) | OK (3) | OK (3) | Sin completar |
| Java heap | OK (3) | OK (3) | OK (3) | OK (3) | Sin completar |
| Java counting | OK (3) | OK (3) | OK (3) | OK (3) | Sin completar |

Los paréntesis indican el número de repeticiones. Las ampliaciones costosas de
Python tienen una repetición; no permiten evaluar variabilidad. La sesión
inicial y la ampliación de Java tienen tres. Se conservan los intentos fallidos
del historial, sin inventar tiempos para llenar las combinaciones restantes.

### Qué cambió en la ampliación

Se amplió el presupuesto de 256 a 1280 o 2048 MiB según la RAM libre, el heap Java
a 1152 o 1792 MiB y los límites
temporales a 120 segundos para Bubble Java, 600 segundos para Bubble Python y
240 a 360 segundos para los demás. Se mantiene una reserva de RAM libre de 512 MiB.
Se retoman solamente las combinaciones sin resultado completo. Los valores
concretos por sesión están en los archivos `entorno*.json`.

La prueba adicional de Counting Python con cien millones usa un arreglo compacto
`array('d')` en lugar de una lista de objetos float. Su estado y resultado constan
en los CSV; es una variante de almacenamiento, no un algoritmo diferente ni una
medición comparable sin esa salvedad. Los demás ensayos Python utilizan listas.

### Ejecutar los fuentes publicados en la raíz

```powershell
python pruebas.py
javac Ordenamientos.java
java Ordenamientos test
python medir.py --java java --max-n 1000000000
```

Requisitos: Python 3, JDK 17 o superior y Windows para medir memoria.
Los algoritmos no dependen de Windows. El medidor no requiere paquetes externos.
Los CSV publicados están en la raíz; las nuevas ejecuciones escriben en `resultados/`.
El ZIP conserva la estructura original; el README de su interior explica sus comandos.

```powershell
python medir.py --append --solo-pendientes --continuar-tras-fallo --lenguajes Java --presupuesto-mib 1280 --java-heap-mib 1152 --limite 240 --bubble-limite 120
python medir.py --append --solo-pendientes --continuar-tras-fallo --lenguajes Python --presupuesto-mib 1280 --limite 240 --bubble-limite 600 --repeticiones 1
```

### Datos, validación y memoria

Se generan centésimas de -500.00 a 500.00 con el mismo LCG de 32 bits y semilla
2026 en ambos lenguajes. Counting opera sobre las claves enteras en centésimas;
no se presenta como ordenamiento de reales arbitrarios. Tree es un BST sin
balance y cuenta duplicados. El rango acotado favorece estos métodos.

Cada resultado completo verifica orden y conservación exacta de frecuencias.
El tiempo mide solo el algoritmo. La memoria es el pico residente del proceso
completo en MiB, incluidos runtime y datos; no es su espacio auxiliar aislado.
El PDF separa cálculos teóricos de mediciones reales e identifica los casos que
no se terminaron. Los archivos de entorno conservan las configuraciones originales.

Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.
