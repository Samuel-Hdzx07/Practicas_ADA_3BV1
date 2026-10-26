# Prácticas ADA 3BV1

Hernandez Barrios Samuel Rodrigo · Profesor ANDRES GARCIA FLORIANO

## Práctica 2 — Complejidad en ordenamiento

Incluye cinco algoritmos en Java y Python, mediciones reales, validaciones,
CSV de datos crudos y resumen, entorno de ejecución y reporte PDF.
Las longitudes grandes omitidas y los límites de tiempo están documentados.

El ZIP conserva la estructura original completa de la práctica. Los archivos
fuente también están disponibles individualmente en la raíz para su consulta.
Para ejecutar estos archivos de la raíz:

```powershell
python pruebas.py
javac Ordenamientos.java
java Ordenamientos test
python medir.py --java java --max-n 1000000000
```

El medidor funciona en Windows y no necesita paquetes Python externos.
Requiere Python 3 y JDK 17 o superior. Los algoritmos son portables.
El ejecutor admite tanto las carpetas del ZIP como los fuentes en la raíz.
Los CSV publicados están en la raíz; las nuevas ejecuciones escriben en resultados/.

## Metodología y límites

Se generan valores de -500.00 a 500.00 con dos decimales, misma semilla LCG 2026
para ambos lenguajes. Counting Sort opera sobre claves en centésimas: no se
presenta como solución para reales arbitrarios. Tree Sort usa BST sin balance
con un contador por clave duplicada.

Cada caso completado tiene tres repeticiones y valida orden y frecuencias.
El tiempo excluye generación y validación. La memoria es el pico residente del
proceso completo, no su espacio auxiliar aislado. Límites: 8 segundos Bubble,
45 segundos otros métodos y 256 MiB por proceso. La JVM usa -Xmx256m.
Las tablas separan casos completados, omitidos e interrumpidos.

Hay resultados completos para Merge, Tree, Heap y Counting a 100000 y 1000000
elementos en ambos lenguajes, y a 10000000 en Java. Bubble tiene pruebas
complementarias a 1000, 5000 y 10000; con 100000 se interrumpió por tiempo.
Los tamaños de 100 millones y mil millones no se ejecutaron por presupuesto.
No se han inventado tiempos para completar los tamaños faltantes.

El README dentro del ZIP contiene la documentación detallada y las complejidades.

Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.
