# Práctica 3 — Divide y vencerás

Hernandez Barrios Samuel Rodrigo · 3BV1 · ADA

Profesor: ANDRES GARCIA FLORIANO. Fecha de entrega: 30 de octubre de 2026.

**[Abrir el reporte PDF](Practica3_ADA_Hernandez_Barrios_Samuel_Rodrigo_3BV1.pdf)**

## Qué se implementó

- Quickselect iterativo con pivote seudoaleatorio y partición de tres vías.
- Datasets de enteros de 32 y 64 bits, con el mismo orden de valores en ambos lenguajes.
- Multiplicación tradicional i,k,j y Strassen con umbral 16.
- Matrices por filas separadas (2D) y buffer unidimensional contiguo (1D).
- Medición de tiempo y pico residente del proceso, validación y registro por caso.

## Cobertura completa de esta práctica

**88 ejecuciones terminadas y verificadas**: 40 Quickselect y 48 matrices.
La lista de la captura repite 5000; se conservaron los dos ensayos. Se añadieron
cuatro ensayos complementarios con n=50000, identificados en el CSV. Las 84
ejecuciones de la lista literal terminaron, más los cuatro complementos.
En términos de combinaciones únicas, se cubren las 80 obligatorias y cuatro
complementarias. No hubo límites de tiempo, errores ni fallos de memoria.

| Apartado | Java | Python |
|---|---:|---:|
| Quickselect 32 bits | 10 correctas | 10 correctas |
| Quickselect 64 bits | 10 correctas | 10 correctas |
| Tradicional 2D | 6 correctas | 6 correctas |
| Tradicional 1D | 6 correctas | 6 correctas |
| Strassen 2D | 6 correctas | 6 correctas |
| Strassen 1D | 6 correctas | 6 correctas |

Quickselect usa n = 1000, 5000, 10000, 5000, 100000, 500000, 1000000, 5000000,
10000000 y el complemento 50000. En matrices n = 16, 32, 64, 128, 256 y 512.
Se aprobaron además 62 pruebas Java y 67 Python antes de medir.

## Ejecutar desde esta carpeta

Requiere Python 3, JDK 17 o superior y Windows para el medidor de memoria.
Los algoritmos y sus pruebas pequeñas no usan dependencias externas.

```powershell
python python/pruebas.py
javac java/Practica3.java
java -cp java Practica3 test
python medir.py --java java --javac javac
```

Si Java no está en PATH, usar rutas absolutas a los ejecutables del JDK.
El medidor compila, verifica los algoritmos y genera las referencias antes
de ejecutar los 88 casos. `--reanudar` permite retomar una ejecución incompleta.
Los límites configurados son 180 s por proceso, 1024 MiB de pico y una reserva
de 256 MiB de RAM libre; la JVM usa `-Xmx768m`. Ningún caso alcanzó esos límites.

## Datasets y verificación

Para selección se genera `v(i)=((7654321*i+1234567) % 10000000)+1` y luego se
baraja con Fisher–Yates usando un LCG de 32 bits y semilla 2026. El multiplicador
es coprimo con diez millones; no hay repetidos. Con n=10^7 se recorre todo el
intervalo [1,10^7]. Para tamaños menores es un subconjunto determinista y
distribuido en el intervalo, no un muestreo uniforme de todos los subconjuntos.
No es un generador criptográfico. El pivote usa un LCG separado con semilla 99.
Se mide k=(n+1)//2 y se valida su rango contando sobre los datos originales.
Java utiliza int[]/long[]; Python array('i')/array('q'), verificando 4/8 bytes.

Matrices: valores entre -9 y 9 con semillas 2026 y 2027. Java usa long; Python
buffers array('q') y aritmética entera. En 2D las filas son buffers separados;
en 1D los valores pertenecen a un único buffer. El caso base de Strassen es
tradicional para n<=16. Cada producto se compara celda por celda con las
referencias binarias calculadas fuera de las mediciones. Los archivos .bin
almacenan long con signo en big-endian; entorno.json conserva sus SHA-256.
Las pruebas pequeñas usan una referencia independiente con ciclos i,j,k.

## Interpretación de tiempo y memoria

Cada proceso mide solo el algoritmo, excluyendo generación y validación.
El pico residente incluye el runtime y todo el proceso; no es una medición
aislada del espacio auxiliar. MiB=2^20 bytes. Se consulta PeakWorkingSetSize
cada 20 ms. Son observaciones individuales salvo la repetición literal de
5000, resumida con mediana de dos tiempos y máximo de memoria. No se afirma
significancia estadística ni un calentamiento prolongado del JIT.

Quickselect esperado Θ(n), peor Θ(n²), auxiliar Θ(1). Tradicional Θ(n³).
Strassen Θ(n^log₂7), aproximadamente Θ(n^2.807), y O(n²) auxiliar en esta
implementación con copias de bloques. Las representaciones y la sobrecarga
pueden cambiar la velocidad práctica; el menor exponente no garantiza una
ventaja para todos los tamaños pequeños.

## Archivos

- `python/` y `java/`: código fuente y pruebas.
- `medir.py`: controlador de procesos y memoria.
- `resultados/mediciones.csv`: 88 resultados crudos y sus verificaciones.
- `resultados/resumen.csv`: 84 combinaciones únicas resumidas.
- `resultados/pruebas.txt`: resultados de pruebas previas.
- `resultados/entorno.json`: configuración y hashes de referencias.
- `referencias/`: productos exactos usados para validar todas las celdas.
- `evidencias/ejecuciones.log`: salida íntegra de los 88 casos.
- `reporte.py` y `assets/`: generación del PDF.

Para regenerar el PDF se requieren reportlab, pypdf y pypdfium2, además de las
fuentes Arial y Consolas de Windows. Ejecutar `python reporte.py` después de
completar las mediciones. Los algoritmos no requieren estos paquetes.

Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.
