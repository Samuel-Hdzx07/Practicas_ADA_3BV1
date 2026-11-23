# Práctica 4 — Algoritmos voraces y codificación Huffman

Hernandez Barrios Samuel Rodrigo · 3BV1 · ADA

Profesor: ANDRES GARCIA FLORIANO

La guía adjunta tiene “Práctica 3” en su encabezado, aunque la actividad asignada en Teams es la práctica 4. Este directorio sigue el número de la actividad y conserva el contenido de Huffman.

## Qué se implementó

- Compresor y descompresor Huffman para cualquier archivo de bytes.
- `BitWriter` y `BitReader` que empaquetan bits en bytes, en orden de bit más significativo a menos significativo.
- Árbol serializado en preorden: `1` seguido del byte para una hoja; `0` para un nodo interno.
- Cabecera `HUF1` con el tamaño original de 64 bits y la cantidad de símbolos distintos.
- Descompresión que se detiene tras producir el tamaño original declarado, por lo que ignora correctamente los ceros de relleno del último byte.
- Pruebas de ida y vuelta, detección de truncamiento y benchmark de los tres tipos de archivo de la guía.

## Compilación y ejecución

Desde esta carpeta, en Windows con MinGW:

```powershell
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -static -static-libgcc -static-libstdc++ cpp/huffman.cpp -o cpp/huffman.exe
python pruebas.py
python medir.py
```

En Linux o macOS, compilar sin las opciones `-static-libgcc -static-libstdc++`:

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic cpp/huffman.cpp -o cpp/huffman
python3 pruebas.py
python3 medir.py
```

Los scripts detectan el nombre del ejecutable según el sistema operativo. Para comprimir o descomprimir manualmente:

```text
cpp/huffman.exe compress entrada.bin salida.huf
cpp/huffman.exe decompress salida.huf recuperado.bin
```

`pruebas.py` valida archivo vacío, un byte, los 256 valores posibles, el mensaje de la práctica, datos binarios con repeticiones, diez millones de letras `A` y un flujo truncado.

## Fase 1 — Teoría de Huffman

Mensaje analizado (36 caracteres): `ABRACADABRA_ALGORITMO_AVANZADO_ESCOM`. La frecuencia relativa es `pᵢ = fᵢ/36`.

| Símbolo | Frecuencia | Probabilidad | Símbolo | Frecuencia | Probabilidad |
|---|---:|---:|---|---:|---:|
| A | 9 | 0.250000 | M | 2 | 0.055556 |
| B | 2 | 0.055556 | N | 1 | 0.027778 |
| C | 2 | 0.055556 | O | 4 | 0.111111 |
| D | 2 | 0.055556 | R | 3 | 0.083333 |
| E | 1 | 0.027778 | S | 1 | 0.027778 |
| G | 1 | 0.027778 | T | 1 | 0.027778 |
| I | 1 | 0.027778 | V | 1 | 0.027778 |
| L | 1 | 0.027778 | Z | 1 | 0.027778 |
| `_` | 3 | 0.083333 |  |  |  |

Con `H(X) = -Σ pᵢ log₂(pᵢ)`, la entropía empírica es **3.668839 bits por carácter**.

Para resolver empates, el montículo prioriza primero la frecuencia y después el menor byte que contiene cada subárbol. La rama izquierda recibe `0` y la derecha `1`. Cada renglón muestra los dos nodos extraídos del bosque, su suma y el nodo que vuelve al montículo:

| Paso | Nodos extraídos | Nodo reintegrado |
|---:|---|---:|
| 1 | E(1) + G(1) | EG(2) |
| 2 | I(1) + L(1) | IL(2) |
| 3 | N(1) + S(1) | NS(2) |
| 4 | T(1) + V(1) | TV(2) |
| 5 | Z(1) + B(2) | ZB(3) |
| 6 | C(2) + D(2) | CD(4) |
| 7 | EG(2) + IL(2) | EGIL(4) |
| 8 | M(2) + NS(2) | MNS(4) |
| 9 | TV(2) + ZB(3) | TVZB(5) |
| 10 | R(3) + `_`(3) | R_(6) |
| 11 | CD(4) + EGIL(4) | CDEGIL(8) |
| 12 | MNS(4) + O(4) | MNSO(8) |
| 13 | TVZB(5) + R_(6) | TVZBR_(11) |
| 14 | CDEGIL(8) + MNSO(8) | CDEGILMNSO(16) |
| 15 | A(9) + TVZBR_(11) | ATVZBR_(20) |
| 16 | CDEGILMNSO(16) + ATVZBR_(20) | raíz(36) |

| Símbolo | Código | Longitud | Símbolo | Código | Longitud |
|---|---|---:|---|---|---:|
| A | `10` | 2 | M | `0100` | 4 |
| B | `11011` | 5 | N | `01010` | 5 |
| C | `0000` | 4 | O | `011` | 3 |
| D | `0001` | 4 | R | `1110` | 4 |
| E | `00100` | 5 | S | `01011` | 5 |
| G | `00101` | 5 | T | `11000` | 5 |
| I | `00110` | 5 | V | `11001` | 5 |
| L | `00111` | 5 | Z | `11010` | 5 |
| `_` | `1111` | 4 |  |  |  |

La longitud total codificada es `Σ fᵢ|cᵢ| = 133` bits. Por tanto, `L̄ = 133/36 = 3.694444` bits por carácter y se cumple `3.668839 ≤ 3.694444 < 4.668839`, es decir, `H(X) ≤ L̄ < H(X)+1`.

### Sobrecarga de las dos serializaciones

- **Tabla de frecuencias:** `256 × 4 = 1024 bytes` para el alfabeto de 256 valores de byte.
- **Árbol en preorden:** para `k=17` hojas, `2k−1=33` marcas de nodo y `8k=136` bits de símbolos: `169 bits`, que ocupan `ceil(169/8)=22 bytes` tras rellenar el último byte.
- Con la cabecera fija común de este formato (4 bytes de firma, 8 de tamaño original y 2 de cantidad de símbolos), la metadata sería **1038 bytes** con la tabla y **36 bytes** con el árbol. El archivo Huffman real del mensaje de 36 bytes ocupa **53 bytes**: 14 de cabecera, 22 de árbol y 17 de datos codificados.

## Fase 2 — Auditoría del uso de IA

### Por qué no sirve guardar cada bit como carácter

El ejemplo `01011` contiene cinco bits de información, pero como `std::string` ocupa cinco bytes de caracteres. Un `BitWriter` guarda esos mismos cinco bits en un byte. Para `B` bits, la cadena binaria necesita aproximadamente `B` bytes, frente a `ceil(B/8)` bytes empaquetados, además de la capacidad reservada y la metadata de `std::string`.

En el mensaje analizado, la longitud media es 3.694 bits por carácter. Si cada bit se escribe como un carácter ASCII, el cuerpo ocupa unos 3.694 bytes por carácter fuente; el original ocupa 1 byte por carácter. La versión de bits en texto no comprime el archivo y el árbol/cabecera aumentan el resultado. La representación empaquetada guarda los 133 bits del mensaje en 17 bytes.

Una realocación individual de una cadena de longitud `B` puede copiar `O(B)` datos. Con crecimiento geométrico, la suma de las copias es `O(B)` amortizada; como el alfabeto de bytes es fijo, `B=O(N)` respecto al número `N` de símbolos de entrada. Reservar capacidad reduce realocaciones, pero no corrige el desperdicio de ocho bits de almacenamiento por cada bit codificado. El compresor escribe directamente en un buffer de bytes con desplazamientos y máscaras.

### Contraprompt para revisar una implementación

> Revisa el compresor Huffman para C++17. No representes los bits como caracteres `'0'` y `'1'`. Propón clases `BitWriter` y `BitReader` que empaqueten y lean bits en un buffer `uint8_t`, usando desplazamientos y máscaras, con orden de bit explícito. Conserva la longitud original en la cabecera y serializa el árbol en preorden. Explica las invariantes, el costo temporal y de memoria, y prueba archivos vacíos, un único símbolo, los 256 valores de byte y un último byte con padding. Señala errores sin sustituir la implementación completa del estudiante.

### Trampa de padding del último byte

El flujo `10110011 010` tiene once bits. El empaquetador produce los bytes `10110011 01000000`; los cinco ceros finales son relleno. Sin metadata, un descompresor no puede distinguirlos de bits útiles. Este formato almacena el número original de bytes como `uint64_t` y decodifica exactamente esa cantidad de símbolos. Así no interpreta el padding como datos ni necesita adivinar cuántos bits del último byte son válidos.

## Benchmark

`medir.py` comprime cada entrada, la descomprime, compara SHA-256 y registra tamaños y tiempos en `resultados/benchmarks.csv`. El ratio es `bytes comprimidos / bytes originales × 100%`; superar 100% indica expansión. Se midió una ejecución por fase y caso, por lo que los tiempos sirven como observaciones de esta máquina y no como estimación estadística.

| Caso | Bytes originales | Bytes Huffman | Ratio | Compresión | Descompresión | Resultado |
|---|---:|---:|---:|---:|---:|---|
| Código C++ estructurado | 14,063 | 8,614 | 61.253% | 0.0276 s | 0.0249 s | Correcto |
| Paquete ZIP del repo | 492,797 | 493,131 | 100.068% | 0.0291 s | 0.0649 s | Correcto |
| `A` repetida 10 millones de veces | 10,000,000 | 1,250,016 | 12.500% | 0.0932 s | 0.0549 s | Correcto |

El ZIP crece 334 bytes debido a la metadata: Huffman no encuentra redundancia útil en un archivo ya comprimido y su árbol ocupa espacio. El caso homogéneo no causa división entre cero, bucles infinitos ni crecimiento de recursión: el árbol tiene una hoja, el código asignado es `0`, y las rutinas procesan el flujo de forma iterativa.

## Archivos

- `cpp/huffman.cpp`: compresor, descompresor, árbol y clases de bits.
- `pruebas.py`: pruebas reproducibles de ida y vuelta y rechazo de truncamiento.
- `medir.py`: benchmarks y verificación SHA-256.
- `resultados/benchmarks.csv`: mediciones crudas.
- `resultados/entorno.json`: entorno y parámetros de medición.
- `resultados/pruebas.txt`: salida de la suite de pruebas.
- `conversacion_ia.md`: transcripción de la conversación de apoyo.

## Alcances

El formato detecta firma incorrecta, cabeceras inconsistentes, árboles inválidos y flujos truncados. No incluye checksum ni autenticación: una alteración que conserve una estructura decodificable podría producir bytes incorrectos. La implementación lee el archivo de entrada y construye la salida comprimida en memoria, así que el uso de memoria es `O(N + C)` para `N` bytes originales y `C` bytes codificados.
