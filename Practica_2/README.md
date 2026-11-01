# Práctica 2 — Complejidad en ordenamiento

Hernandez Barrios Samuel Rodrigo · 3BV1 · ADA

Bubble Sort, Merge Sort iterativo, Tree Sort con BST sin balance y contador de duplicados,
Heap Sort y Counting Sort, implementados en Java y Python sin usar ordenamientos
de biblioteca dentro de los algoritmos. Las bibliotecas de ordenamiento se usan
solamente como referencia en las pruebas pequeñas.

## Datos y alcance

Los datos son reales discretizados: centésimas entre -500.00 y 500.00.
Se generan como enteros divididos entre 100 y se almacenan en `float` o `double`.
Counting Sort se aplica a las claves enteras en centésimas; no sirve como
ordenamiento directo de cualquier real arbitrario. No se redondean entradas
externas con más decimales: se rechazan. No se incluyen NaN ni infinitos.

Ambos lenguajes usan el mismo generador LCG de 32 bits, semilla 2026,
recurrencia `(1664525*x + 1013904223) mod 2^32` y clave
`(x mod 100001) - 50000`. Los tamaños son 100000, 1000000,
10000000, 100000000 y 1000000000.

## Ejecutar

Requisitos: Windows para el medidor, Python 3 y JDK 17 o superior.
Las implementaciones de los algoritmos no dependen de Windows ni de paquetes externos.

```powershell
python python/pruebas.py
javac java/Ordenamientos.java
java -cp java Ordenamientos test
python medir.py --java java --max-n 1000000000 --presupuesto-mib 256
```

Si Java no está en PATH, pasar la ruta absoluta a `java.exe`.
La compilación usa `javac` del mismo JDK. El ejecutor llama al Python que lo inicia.
Para ejecutar un caso individual:

```powershell
python python/caso.py merge 100000
java -Xmx256m -cp java Ordenamientos heap 100000
```

## Protocolo de medición

Cada repetición corre en un proceso nuevo, secuencialmente, con entrada idéntica.
Se realizan tres repeticiones por caso completado. El cronómetro de ordenamiento
excluye generación, calentamiento y validación. Python usa `perf_counter` y Java
`nanoTime`. El calentamiento usa 200 elementos (una vez Python, cinco Java);
no elimina por completo los efectos del JIT, GC o cachés.

Se comprueba orden no decreciente y conservación exacta de frecuencias para las
100001 claves. Las pruebas pequeñas también comparan contra el ordenamiento
de biblioteca. El pico de memoria es `PeakWorkingSetSize` de Windows del proceso
completo, consultado cada 20 ms. Incluye datos, verificadores, runtime y JVM:
no es una medida aislada del espacio auxiliar ni es comparable directamente
como consumo intrínseco entre lenguajes. MiB significa 2^20 bytes.

En la sesión inicial, el límite de 8 segundos para Bubble y de 45 segundos para los demás abarca
la vida del proceso, no solo el cronómetro interno. Las interrupciones no se
presentan como tiempos completos. El tamaño mayor de Bubble se omite por política
de tiempo. Los casos que exceden el presupuesto conservador de memoria no se
inician; el CSV indica el estado y motivo. `--max-n` permite acotar una sesión;
`--min-n`, `--lenguajes Java` y `--append` permiten agregar una sesión posterior.
Cada sesión adicional registra su entorno por separado. La JVM usa `-Xmx256m`;
aumentar el presupuesto del medidor por sí solo no cambia ese límite de heap.
La ampliación usa `--java-heap-mib` para configurarlo explícitamente.

## Ampliación de las mediciones

Se retiró el presupuesto inicial de 256 MiB para los nuevos casos. La ampliación
permite hasta 1280 o 2048 MiB por proceso según la RAM libre, mantiene 512 MiB
de RAM libre para el sistema y configura el heap Java en 1152 o 1792 MiB.
Java tiene tres repeticiones por caso;
los casos costosos ampliados de Python tienen una repetición. Se conserva el
historial completo, incluidas interrupciones anteriores, sin sustituirlo ni
inventar resultados.

```powershell
python medir.py --append --solo-pendientes --continuar-tras-fallo --lenguajes Java --presupuesto-mib 1280 --java-heap-mib 1152 --limite 240 --bubble-limite 120
python medir.py --append --solo-pendientes --continuar-tras-fallo --lenguajes Python --presupuesto-mib 1280 --limite 240 --bubble-limite 600 --repeticiones 1
```

`--solo-pendientes` omite combinaciones que ya tienen una ejecución validada.
`--reserva-mib` fija la reserva de RAM libre; si se cruza durante una ejecución,
el proceso de prueba se interrumpe y se registra. `--bubble-max-n` controla
el mayor tamaño que se inicia para Bubble. No hay una ejecución completa de
Bubble con un millón o más de elementos. La tabla `cobertura.csv` describe las
50 combinaciones y distingue resultados completos de estados sin completar.

## Resultados

`resultados/mediciones.csv`: datos crudos y estados, incluidas filas omitidas.
Una sesión posterior puede completar una combinación previamente omitida;
se conservan ambas filas como historial. Para el resumen se priorizan las filas OK.
`resultados/entorno*.json`: versiones, RAM y configuración.
El reporte PDF contiene medianas de tiempo y máximos de pico de memoria para los
casos completados; no contiene tiempos inventados para casos no ejecutados.
El conjunto aleatorio y su rango acotado favorecen Counting Sort y limitan el
número de nodos distintos de Tree Sort. No representa todos los casos posibles.

## Complejidad

| Algoritmo | Tiempo | Espacio auxiliar |
|---|---|---|
| Bubble con salida temprana | Mejor Θ(n), promedio/peor Θ(n²) | Θ(1) |
| Merge iterativo | Θ(n log n) | Θ(n) |
| Tree BST sin balance | Esperado O(n log(u+1)), peor O(nu), u ≤ n | O(u+h), h ≤ u |
| Heap | O(n log n), peor Θ(n log n) | Θ(1) |
| Counting | Θ(n+k) | Θ(k) |

En Tree se cuentan duplicados en un nodo; n es número de valores y u de valores
distintos. En entradas distintas y ordenadas puede degenerar a Θ(n²).
Counting reconstruye valores, no registros con identidad: esta implementación
no promete estabilidad para registros. Merge y Bubble preservan orden de iguales;
Heap no es estable.

Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.
