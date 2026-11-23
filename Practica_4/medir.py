from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path


PRACTICA = Path(__file__).resolve().parent
REPO = PRACTICA.parent
DEFAULT_BINARY = PRACTICA / "cpp" / ("huffman.exe" if os.name == "nt" else "huffman")
TAM_REPETICIONES = 10_000_000
TEMP_ROOT = PRACTICA / "tmp"


def ejecutar(binary: Path, operacion: str, entrada: Path, salida: Path) -> float:
    inicio = time.perf_counter()
    resultado = subprocess.run(
        [str(binary), operacion, str(entrada), str(salida)],
        check=False,
        text=True,
        capture_output=True,
    )
    duracion = time.perf_counter() - inicio
    if resultado.returncode != 0:
        raise RuntimeError(f"{operacion} falló: {resultado.stderr.strip()}")
    return duracion


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for bloque in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def ruta_reproducible(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return path.name


def preparar_entrada_repetida(path: Path) -> None:
    bloque = b"A" * (1024 * 1024)
    restantes = TAM_REPETICIONES
    with path.open("wb") as stream:
        while restantes:
            cantidad = min(restantes, len(bloque))
            stream.write(bloque[:cantidad])
            restantes -= cantidad


def medir_caso(binary: Path, nombre: str, entrada: Path, carpeta: Path) -> dict[str, object]:
    comprimido = carpeta / f"{nombre}.huf"
    recuperado = carpeta / f"{nombre}.recuperado"
    tiempo_compresion = ejecutar(binary, "compress", entrada, comprimido)
    tiempo_descompresion = ejecutar(binary, "decompress", comprimido, recuperado)

    original_hash = sha256(entrada)
    recuperado_hash = sha256(recuperado)
    if original_hash != recuperado_hash:
        raise RuntimeError(f"La validación SHA-256 falló para el caso {nombre}.")

    original = entrada.stat().st_size
    comprimido_size = comprimido.stat().st_size
    ratio = comprimido_size / original * 100 if original else 0.0
    fila: dict[str, object] = {
        "caso": nombre,
        "archivo": entrada.name,
        "bytes_originales": original,
        "bytes_comprimidos": comprimido_size,
        "ratio_compresion_pct": f"{ratio:.4f}",
        "bytes_ahorrados": original - comprimido_size,
        "tiempo_compresion_s": f"{tiempo_compresion:.6f}",
        "tiempo_descompresion_s": f"{tiempo_descompresion:.6f}",
        "sha256_original": original_hash,
        "sha256_recuperado": recuperado_hash,
        "verificacion": "correcta",
    }
    print(
        f"{nombre:24} {original:>10} -> {comprimido_size:>10} bytes  "
        f"ratio={ratio:8.3f}%  comp={tiempo_compresion:.4f}s  decomp={tiempo_descompresion:.4f}s  OK"
    )
    return fila


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark reproducible del compresor Huffman")
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY, help="Ruta al ejecutable de Huffman")
    parser.add_argument("--texto", type=Path, default=PRACTICA / "cpp" / "huffman.cpp",
                        help="Archivo de texto estructurado")
    parser.add_argument("--precomprimido", type=Path,
                        default=REPO / "Practica_2" / "Practica2_ADA_Codigo_y_Resultados.zip",
                        help="Archivo ZIP existente para el caso ya comprimido")
    parser.add_argument("--salida", type=Path, default=PRACTICA / "resultados")
    args = parser.parse_args()

    binary = args.binary.resolve()
    texto = args.texto.resolve()
    precomprimido = args.precomprimido.resolve()
    if not binary.is_file():
        parser.error(f"No existe el ejecutable: {binary}. Compílalo primero con g++.")
    if not texto.is_file():
        parser.error(f"No existe el archivo de texto: {texto}")
    if not precomprimido.is_file():
        parser.error(f"No existe el archivo ZIP de referencia: {precomprimido}")

    args.salida.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    filas: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="huffman-benchmark-", dir=TEMP_ROOT) as tmp:
        carpeta = Path(tmp)
        repetido = carpeta / "A_10_millones.bin"
        preparar_entrada_repetida(repetido)
        filas.append(medir_caso(binary, "texto_estructurado", texto, carpeta))
        filas.append(medir_caso(binary, "archivo_zip", precomprimido, carpeta))
        filas.append(medir_caso(binary, "A_repetida_10_millones", repetido, carpeta))

    csv_path = args.salida / "benchmarks.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    try:
        compilador = subprocess.run(
            ["g++", "--version"], check=True, text=True, capture_output=True
        ).stdout.splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        compilador = "No disponible en PATH"

    entorno = {
        "sistema": platform.platform(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor(),
        "python": sys.version,
        "compilador": compilador,
        "flags_compilacion": "-std=c++17 -O2 -Wall -Wextra -Wpedantic -static -static-libgcc -static-libstdc++ (MinGW/Windows)",
        "ejecutable": ruta_reproducible(binary),
        "archivo_texto": ruta_reproducible(texto),
        "archivo_precomprimido": ruta_reproducible(precomprimido),
        "tamano_caso_homogeneo": TAM_REPETICIONES,
        "ratio_pct": "bytes_comprimidos / bytes_originales * 100",
        "reloj": "time.perf_counter; una ejecución por fase y caso",
    }
    (args.salida / "entorno.json").write_text(
        json.dumps(entorno, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nResultados: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
