from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path


PRACTICA = Path(__file__).resolve().parent
JAVA_DIR = PRACTICA / "java"
RESULTADOS = PRACTICA / "resultados"
sys.path.insert(0, str(PRACTICA / "python"))

from programacion_dinamica import (  # noqa: E402
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


def detectar_java(nombre: str) -> str:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidato = Path(java_home) / "bin" / (nombre + (".exe" if os.name == "nt" else ""))
        if candidato.is_file():
            return str(candidato)
    if os.name == "nt":
        instalaciones = sorted(Path("C:/Program Files/Java").glob("jdk*/bin/" + nombre + ".exe"))
        if instalaciones:
            return str(instalaciones[-1])
    return shutil.which(nombre) or nombre


def medir_python(problema, estrategia, carga, dimension, funcion):
    esperado = funcion()  # calentamiento
    tiempos = []
    for _ in range(5):
        inicio = time.perf_counter_ns()
        resultado = funcion()
        tiempos.append(time.perf_counter_ns() - inicio)
        if resultado != esperado:
            raise RuntimeError(f"Resultado inestable en Python: {problema}/{estrategia}/{carga}")
    return {
        "lenguaje": "Python",
        "problema": problema,
        "estrategia": estrategia,
        "carga": carga,
        "dimension": dimension,
        "mediana_ms": f"{statistics.median(tiempos) / 1_000_000:.6f}",
        "resultado": esperado,
    }


def filas_python():
    filas = []
    pesos = [1 + (i * 7) % 17 for i in range(18)]
    valores = [1 + (i * 13) % 50 for i in range(18)]
    capacidad = 55
    for estrategia, funcion in [
        ("recursion", lambda: mochila_recursiva(pesos, valores, capacidad)),
        ("memoizacion", lambda: mochila_memoizada(pesos, valores, capacidad)),
        ("tabulacion", lambda: mochila_tabla(pesos, valores, capacidad)),
    ]:
        filas.append(medir_python("mochila", estrategia, "comun", len(pesos), funcion))

    pesos = [1 + (i * 7 + 1) % 19 for i in range(90)]
    valores = [1 + (i * 13 + 2) % 47 for i in range(90)]
    for estrategia, funcion in [
        ("memoizacion", lambda: mochila_memoizada(pesos, valores, 700)),
        ("tabulacion", lambda: mochila_tabla(pesos, valores, 700)),
    ]:
        filas.append(medir_python("mochila", estrategia, "escalable", len(pesos), funcion))

    monedas = [1, 3, 4, 7]
    for problema, funciones in [
        ("cambio_minimo", [cambio_minimo_recursivo, cambio_minimo_memoizado, cambio_minimo_tabla]),
        ("cambio_formas", [cambio_formas_recursivo, cambio_formas_memoizado, cambio_formas_tabla]),
    ]:
        for estrategia, funcion in zip(("recursion", "memoizacion", "tabulacion"), funciones):
            filas.append(medir_python(problema, estrategia, "comun", 24,
                                      lambda funcion=funcion: funcion(monedas, 24)))

    monedas_escalables = [7, 13, 29]
    for problema, funciones, cantidad in [
        ("cambio_minimo", [cambio_minimo_memoizado, cambio_minimo_tabla], 600),
        ("cambio_formas", [cambio_formas_memoizado, cambio_formas_tabla], 250),
    ]:
        for estrategia, funcion in zip(("memoizacion", "tabulacion"), funciones):
            filas.append(medir_python(problema, estrategia, "escalable", cantidad,
                                      lambda funcion=funcion, cantidad=cantidad:
                                      funcion(monedas_escalables, cantidad)))

    a, b = "A" * 10, "B" * 10
    for problema, funciones in [
        ("LCSq", [lcs_subsecuencia_recursiva, lcs_subsecuencia_memoizada,
                  lcs_subsecuencia_tabla]),
        ("LCS_subcadena", [lcs_subcadena_recursiva, lcs_subcadena_memoizada,
                           lcs_subcadena_tabla]),
    ]:
        for estrategia, funcion in zip(("recursion", "memoizacion", "tabulacion"), funciones):
            filas.append(medir_python(problema, estrategia, "comun", len(a),
                                      lambda funcion=funcion: funcion(a, b)))

    def cadena(n, semilla):
        return "".join(chr(ord("A") + ((i * 17 + semilla) % 4)) for i in range(n))

    a, b = cadena(160, 1), cadena(160, 3)
    for problema, funciones in [
        ("LCSq", [lcs_subsecuencia_memoizada, lcs_subsecuencia_tabla]),
        ("LCS_subcadena", [lcs_subcadena_memoizada, lcs_subcadena_tabla]),
    ]:
        for estrategia, funcion in zip(("memoizacion", "tabulacion"), funciones):
            filas.append(medir_python(problema, estrategia, "escalable", len(a),
                                      lambda funcion=funcion: funcion(a, b)))
    return filas


def compilar_y_medir_java(java, javac):
    fuentes = ["ProgramacionDinamica.java", "PruebasProgramacionDinamica.java", "Benchmarks.java"]
    compilacion = subprocess.run(
        [javac, "-Xlint:all", *fuentes], cwd=JAVA_DIR, text=True, capture_output=True
    )
    if compilacion.returncode != 0:
        raise RuntimeError(f"Falló la compilación Java:\n{compilacion.stdout}{compilacion.stderr}")
    resultado = subprocess.run(
        [java, "-cp", str(JAVA_DIR), "Benchmarks"], text=True, capture_output=True
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"Falló el benchmark Java:\n{resultado.stdout}{resultado.stderr}")
    return list(csv.DictReader(resultado.stdout.splitlines()))


def version_java(java):
    resultado = subprocess.run([java, "-version"], text=True, capture_output=True)
    lineas = (resultado.stderr or resultado.stdout).splitlines()
    return lineas[0] if lineas else "No disponible"


def main():
    parser = argparse.ArgumentParser(description="Mide las versiones Python y Java de la práctica 5")
    parser.add_argument("--java", default=detectar_java("java"), help="Ejecutable de Java")
    parser.add_argument("--javac", default=detectar_java("javac"), help="Compilador javac")
    args = parser.parse_args()

    filas = filas_python()
    filas.extend(compilar_y_medir_java(args.java, args.javac))
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTADOS / "benchmarks.csv"
    columnas = ["lenguaje", "problema", "estrategia", "carga", "dimension", "mediana_ms", "resultado"]
    with csv_path.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(filas)

    entorno = {
        "sistema": platform.platform(),
        "procesador": platform.processor(),
        "python": sys.version,
        "java": version_java(args.java),
        "compilador_java": version_java(args.javac),
        "repeticiones_medidas": 5,
        "calentamientos_python": 1,
        "calentamientos_java": 1,
        "estadistico": "mediana; Java usa 3 repeticiones medidas por variante",
        "cargas_comunes": {
            "mochila": "n=18, capacidad=55",
            "cambio": "monedas=[1,3,4,7], cantidad=24",
            "LCSq_y_LCS": "dos cadenas disjuntas de longitud 10",
        },
        "cargas_escalables": {
            "mochila": "n=90, capacidad=700",
            "cambio_minimo": "cantidad=600, monedas=[7,13,29]",
            "cambio_formas": "cantidad=250, monedas=[7,13,29]",
            "LCSq_y_LCS": "dos cadenas de longitud 160",
        },
    }
    (RESULTADOS / "entorno.json").write_text(
        json.dumps(entorno, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(filas)} mediciones guardadas en {csv_path}")
    for fila in filas:
        print("{lenguaje:6} {problema:16} {estrategia:12} {carga:9} n={dimension:>3} "
              "mediana={mediana_ms:>9} ms resultado={resultado}".format(**fila))


if __name__ == "__main__":
    main()
