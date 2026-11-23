# Prácticas ADA 3BV1

Hernandez Barrios Samuel Rodrigo · Profesor ANDRES GARCIA FLORIANO

## Entregables

| Práctica | Reporte / análisis | Código y resultados |
|---|---|---|
| 2 · Complejidad en ordenamiento | [Abrir PDF](Practica_2/Practica2_ADA_Hernandez_Barrios_Samuel_Rodrigo_3BV1.pdf) | [Carpeta de la práctica 2](Practica_2/) |
| 3 · Divide y vencerás | [Abrir PDF](Practica_3/Practica3_ADA_Hernandez_Barrios_Samuel_Rodrigo_3BV1.pdf) | [Carpeta de la práctica 3](Practica_3/) |
| 4 · Algoritmos voraces y Huffman | [Análisis y resultados](Practica_4/README.md) | [Carpeta de la práctica 4](Practica_4/) |

## Organización

```text
Practica_2/
  python/        Cinco algoritmos de ordenamiento
  java/          Ordenamientos.java
  resultados/    Mediciones, cobertura y entorno
  medir.py       Ejecutor de rendimiento
  README.md      Instrucciones y límites experimentales
  *.pdf          Reporte
  *.zip          Paquete de la práctica 2
Practica_3/
  python/        Quickselect, tradicional y Strassen
  java/          Practica3.java
  resultados/    CSV crudo, resumen, entorno y pruebas
  referencias/   Productos exactos para validación
  evidencias/    Registro completo de las ejecuciones
  assets/        Recursos del reporte
  medir.py       Ejecutor y verificador
  reporte.py     Generador del PDF
  README.md      Instrucciones de reproducción
  *.pdf          Reporte
Practica_4/
  cpp/           Compresor y descompresor Huffman en C++17
  resultados/    Benchmarks, entorno y pruebas
  medir.py       Compresión, descompresión y verificación
  pruebas.py     Casos de ida y vuelta y entradas inválidas
  README.md      Análisis teórico y resultados
  conversacion_ia.md Transcripción de apoyo con IA
```

## Estado de las prácticas

- **Práctica 2:** implementaciones y resultados ampliados; conserva sus 31 de 50
  combinaciones completadas y las limitaciones descritas en su reporte y cobertura.
- **Práctica 3:** todas las pruebas de la consigna completadas y verificadas.
  Hay 88 ejecuciones: 84 de la lista literal, que repite 5000, y cuatro
  complementarias con n=50000. No hubo fallos de recursos.
- **Práctica 4:** compresor Huffman en C++17, siete comprobaciones y tres
  benchmarks validados con SHA-256; el ZIP se expandió 334 bytes y el archivo
  homogéneo de 10 millones de bytes se redujo a 12.500% de su tamaño.

Cada carpeta tiene su propio README con los comandos, datos, tipos y protocolo.
El enlace principal del repositorio sigue siendo el mismo. Los reportes ahora
se encuentran dentro de la carpeta de su práctica, con enlaces directos arriba.

Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.
