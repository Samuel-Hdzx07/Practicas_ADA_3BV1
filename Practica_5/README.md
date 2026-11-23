# Práctica 5 — Programación dinámica

Hernandez Barrios Samuel Rodrigo · 3BV1 · ADA

Profesor: ANDRES GARCIA FLORIANO
Fecha límite indicada en Teams: 25 de noviembre de 2026

## Alcance y supuestos

La captura no detalla las variantes de los problemas ni el formato de entrada. Para hacer resultados reproducibles se fijaron estos supuestos:

- **Mochila:** 0/1; cada artículo se puede elegir una vez, con peso positivo, valor no negativo y capacidad máxima. Se devuelve el valor óptimo.
- **Cambio:** se incluye el problema de mínimo número de monedas con reutilización ilimitada. Como “Cambio” también se usa para contar combinaciones, se agrega esa segunda variante; cuenta combinaciones sin distinguir el orden.
- **LCSq:** longitud de la subsecuencia común más larga; los caracteres pueden no ser contiguos.
- **LCS:** longitud de la subcadena común más larga; los caracteres deben ser contiguos.

Las rutinas devuelven el valor o la longitud óptima, no la selección de artículos ni la cadena reconstruida. Si el profesor se refería a otra variante, se debe adaptar la interfaz antes de entregar.

## Código y ejecución

Se implementaron recursión ingenua, memoización y tabulación en Python y Java. Para ejecutar desde la raíz del repositorio:

```powershell
python Practica_5/python/pruebas.py
javac -Xlint:all Practica_5/java/ProgramacionDinamica.java Practica_5/java/PruebasProgramacionDinamica.java Practica_5/java/Benchmarks.java
java -cp Practica_5/java PruebasProgramacionDinamica
python Practica_5/medir.py
```

`medir.py` compila Java y corre ambos benchmarks. Busca Java en `JAVA_HOME` o en `C:\Program Files\Java\jdk*`; también acepta `--java` y `--javac`. Si el launcher `java` del sistema apunta a un alias que no inicia el JDK, usa la ruta completa a `java.exe` y `javac.exe`.

## Recurrencias y complejidad

`n` es el número de artículos, `C` la capacidad, `m` el número de denominaciones, `A` la cantidad objetivo y `p`,`q` las longitudes de las cadenas.

| Problema | Recursión ingenua | Memoización | Tabulación |
|---|---|---|---|
| Mochila 0/1 | `O(2ⁿ)` tiempo, `O(n)` pila | `O(nC)` tiempo y memoria | `O(nC)` tiempo y memoria |
| Cambio mínimo | Exponencial en `A` | `O(mA)` tiempo, `O(A)` estados/pila | `O(mA)` tiempo, `O(A)` memoria |
| Conteo de combinaciones | Exponencial | `O(mA)` tiempo y memoria | `O(mA)` tiempo, `O(A)` memoria |
| LCSq | Exponencial en `p+q` | `O(pq)` tiempo/memoria | `O(pq)` tiempo/memoria |
| LCS contigua | Exponencial en `p+q` | `O(pq)` tiempo/memoria | `O(pq)` tiempo/memoria |

La tabla de mochila es **pseudo-polinomial**: el costo depende del valor numérico de `C`, no solo del tamaño de su representación. Las versiones memoizadas evitan recalcular estados; las tabuladas evalúan los estados en un orden iterativo. Las versiones recursivas se miden únicamente con entradas pequeñas.

## Casos de prueba y optimalidad

Los verificadores comparan las tres estrategias entre sí y contra oráculos pequeños independientes. Se usan casos límite y 120 entradas pseudoaleatorias reproducibles con semillas fijas.

| Problema | Entrada | Resultado esperado | Qué comprueba |
|---|---|---:|---|
| Mochila | Sin artículos, `C=0` | 0 | Caso vacío |
| Mochila | Artículo `(peso=3, valor=7)`, `C=2` | 0 | Artículo que no cabe |
| Mochila | `(2,3),(3,4),(4,5)`, `C=5` | 7 | Combinación que llena la capacidad |
| Mochila | `(10,60),(20,100),(30,120)`, `C=50` | 220 | Óptimo distinto de elegir por mejor razón valor/peso local |
| Cambio mínimo | Monedas `{1,3,4}`, `A=6` | 2 | El enfoque voraz `4+1+1` usa una moneda de más |
| Cambio mínimo | Monedas `{4,6}`, `A=5` | Imposible | Cantidad no representable |
| Cambio mínimo | Monedas repetidas `{5,1,3,3}`, `A=6` | 2 | Denominaciones duplicadas y desordenadas |
| Formas de cambio | `{1,2,5}`, `A=5` | 4 | Combinaciones, sin contar permutaciones |
| LCSq / LCS | `ABCD` y `XBDY` | 2 / 1 | Distingue subsecuencia de subcadena contigua |
| LCSq / LCS | `XABYCDZ` y `QABRCDS` | 4 / 2 | Combina dos coincidencias separadas |
| LCSq / LCS | Cadenas vacías o sin símbolos comunes | 0 / 0 | Casos frontera |

La optimalidad de mochila se contrasta enumerando todos los subconjuntos en instancias pequeñas. El mínimo de monedas se compara con una búsqueda BFS por cantidades; las formas se enumeran por denominación. Para LCSq se enumeran subsecuencias candidatas y para LCS se revisan subcadenas contiguas.

Los casos escalables prueban `n=90,C=700` para mochila, `A=600` para cambio mínimo, `A=250` para formas de cambio, y dos cadenas de longitud 160 para LCSq/LCS. Las variantes ingenuas se mantienen en tamaños pequeños porque su tiempo crece exponencialmente.

## Verificación

- Python: **5 grupos de pruebas correctos**, con casos límite, comparaciones entre las tres versiones, oráculos y entradas inválidas.
- Java: **435 verificaciones correctas**, también con casos aleatorios y oráculos independientes.
- Java se compiló con `-Xlint:all` sin advertencias.
- Benchmark: **50 mediciones** (25 por lenguaje). Cada método tuvo un calentamiento; Python registró cinco tiempos y Java tres. La tabla reporta la mediana y excluye el arranque del proceso/JVM.

## Resultados de eficiencia

Los tiempos están en milisegundos y corresponden a esta máquina. Son observaciones de una corrida, no una afirmación de significancia estadística.

### Cargas comunes

Mochila usa `n=18,C=55`; cambio usa `{1,3,4,7},A=24`; LCSq y LCS usan cadenas disjuntas de longitud 10. Los resultados de cada fila coincidieron entre recursión, memoización y tabulación.

| Problema | Lenguaje | Recursión | Memoización | Tabulación |
|---|---|---:|---:|---:|
| Mochila | Python | 8.8363 | 0.2425 | 0.1017 |
| Mochila | Java | 0.2859 | 0.0685 | 0.0503 |
| Cambio mínimo | Python | 24.1882 | 0.0165 | 0.0093 |
| Cambio mínimo | Java | 0.3350 | 0.0162 | 0.0112 |
| Formas de cambio | Python | 0.1392 | 0.0348 | 0.0048 |
| Formas de cambio | Java | 0.0203 | 0.0236 | 0.0131 |
| LCSq | Python | 29.5585 | 0.0378 | 0.0140 |
| LCSq | Java | 0.4169 | 0.0176 | 0.0091 |
| LCS contigua | Python | 52.3202 | 0.0592 | 0.0064 |
| LCS contigua | Java | 0.4253 | 0.0197 | 0.0055 |

### Cargas escalables

Se comparan memoización y tabulación. Para cambio se usan `{7,13,29}` a fin de probar cantidades grandes sin una cadena recursiva de profundidad igual a `A`.

| Problema | Carga | Lenguaje | Memoización | Tabulación |
|---|---|---|---:|---:|
| Mochila | `n=90,C=700` | Python | 16.1944 | 8.4839 |
| Mochila | `n=90,C=700` | Java | 0.6224 | 0.2799 |
| Cambio mínimo | `A=600` | Python | 0.2635 | 0.1658 |
| Cambio mínimo | `A=600` | Java | 0.0206 | 0.0760 |
| Formas de cambio | `A=250` | Python | 0.1814 | 0.0288 |
| Formas de cambio | `A=250` | Java | 0.0202 | 0.0356 |
| LCSq | `p=q=160` | Python | 0.2742 | 2.6887 |
| LCSq | `p=q=160` | Java | 0.1175 | 0.8019 |
| LCS contigua | `p=q=160` | Python | 17.5485 | 1.4785 |
| LCS contigua | `p=q=160` | Java | 0.5210 | 0.5391 |

El top-down puede ser más rápido si visita pocos estados, como ocurrió con LCSq en esta carga; tabulación siempre recorre la cuadrícula completa. Las diferencias pequeñas entre las dos estrategias también dependen de la asignación de memoria, el intérprete/JIT y el tamaño de entrada.

## Archivos

- `python/programacion_dinamica.py`: algoritmos Python.
- `python/pruebas.py`: oráculos y pruebas Python.
- `java/ProgramacionDinamica.java`: algoritmos Java.
- `java/PruebasProgramacionDinamica.java`: pruebas y oráculos Java.
- `java/Benchmarks.java`: mediciones Java dentro del proceso.
- `medir.py`: mediciones Python/Java y generación de resultados.
- `resultados/benchmarks.csv`: 50 mediciones crudas.
- `resultados/entorno.json`: entorno y protocolo reproducible.
- `resultados/pruebas_python.txt`, `resultados/pruebas_java.txt`: salidas de las pruebas.

## Notas de implementación

- Para cambio mínimo, Python devuelve `None` y Java `-1` si no existe solución.
- Las monedas se normalizan a denominaciones únicas ordenadas; deben ser positivas.
- El conteo de formas en Java usa `long` y `Math.addExact` para señalar desbordamiento; Python conserva enteros de precisión arbitraria.
- Las cadenas Java se recorren por puntos de código Unicode, igual que Python, no por unidades UTF-16 individuales.
