from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


PRACTICA = Path(__file__).resolve().parent
DEFAULT_BINARY = PRACTICA / "cpp" / ("huffman.exe" if os.name == "nt" else "huffman")
TEMP_ROOT = PRACTICA / "tmp"


def ejecutar(binary: Path, operacion: str, entrada: Path, salida: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), operacion, str(entrada), str(salida)],
        check=False,
        text=True,
        capture_output=True,
    )


def comprobar_caso(binary: Path, nombre: str, datos: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="huffman-test-", dir=TEMP_ROOT) as tmp:
        carpeta = Path(tmp)
        original = carpeta / "original.bin"
        comprimido = carpeta / "archivo.huf"
        recuperado = carpeta / "recuperado.bin"
        original.write_bytes(datos)

        resultado = ejecutar(binary, "compress", original, comprimido)
        if resultado.returncode != 0:
            raise AssertionError(f"{nombre}: compresión fallida: {resultado.stderr.strip()}")

        resultado = ejecutar(binary, "decompress", comprimido, recuperado)
        if resultado.returncode != 0:
            raise AssertionError(f"{nombre}: descompresión fallida: {resultado.stderr.strip()}")
        if recuperado.read_bytes() != datos:
            raise AssertionError(f"{nombre}: el contenido recuperado difiere del original")

        print(f"OK  {nombre:24} {len(datos):>10} -> {comprimido.stat().st_size:>10} bytes")


def comprobar_truncamiento(binary: Path) -> None:
    datos = b"ABCDE" * 200
    with tempfile.TemporaryDirectory(prefix="huffman-truncate-", dir=TEMP_ROOT) as tmp:
        carpeta = Path(tmp)
        original = carpeta / "original.bin"
        comprimido = carpeta / "archivo.huf"
        incompleto = carpeta / "incompleto.huf"
        salida = carpeta / "salida.bin"
        original.write_bytes(datos)

        resultado = ejecutar(binary, "compress", original, comprimido)
        if resultado.returncode != 0:
            raise AssertionError(f"No se pudo preparar la prueba de truncamiento: {resultado.stderr.strip()}")

        contenido = comprimido.read_bytes()
        incompleto.write_bytes(contenido[:-1])
        resultado = ejecutar(binary, "decompress", incompleto, salida)
        if resultado.returncode == 0:
            raise AssertionError("El descompresor aceptó un flujo truncado")
        print("OK  rechazo de flujo truncado")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pruebas de ida y vuelta del compresor Huffman")
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY, help="Ruta al ejecutable de Huffman")
    args = parser.parse_args()
    binary = args.binary.resolve()
    if not binary.is_file():
        parser.error(f"No existe el ejecutable: {binary}. Compílalo primero con g++.")
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    casos = [
        ("archivo vacio", b""),
        ("un unico byte", b"A"),
        ("alfabeto de 256 bytes", bytes(range(256))),
        ("mensaje de la practica", b"ABRACADABRA_ALGORITMO_AVANZADO_ESCOM"),
        ("binario con repeticiones", bytes([0, 1, 255, 0, 255, 128, 1]) * 4096),
        ("una sola letra, 10^7 veces", b"A" * 10_000_000),
    ]

    for nombre, datos in casos:
        comprobar_caso(binary, nombre, datos)
    comprobar_truncamiento(binary)
    print(f"\n{len(casos) + 1} comprobaciones correctas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
