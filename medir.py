"""Ejecutor Windows aislado. No extrapola tiempos ni memoria medida."""
import argparse
import csv
import ctypes as ct
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
PYTHON_DIR = BASE/'python' if (BASE/'python').is_dir() else BASE
JAVA_DIR = BASE/'java' if (BASE/'java').is_dir() else BASE
class Memoria(ct.Structure):
    _fields_ = [('cb',ct.c_ulong),('PageFaultCount',ct.c_ulong),
                ('PeakWorkingSetSize',ct.c_size_t),('WorkingSetSize',ct.c_size_t),
                ('QuotaPeakPagedPoolUsage',ct.c_size_t),('QuotaPagedPoolUsage',ct.c_size_t),
                ('QuotaPeakNonPagedPoolUsage',ct.c_size_t),('QuotaNonPagedPoolUsage',ct.c_size_t),
                ('PagefileUsage',ct.c_size_t),('PeakPagefileUsage',ct.c_size_t)]
class Estado(ct.Structure):
    _fields_=[('length',ct.c_ulong),('load',ct.c_ulong),('total',ct.c_ulonglong),
              ('avail',ct.c_ulonglong),('page',ct.c_ulonglong),('apage',ct.c_ulonglong),
              ('virt',ct.c_ulonglong),('avirt',ct.c_ulonglong),('ext',ct.c_ulonglong)]
kernel=ct.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.restype=ct.c_void_p
kernel.OpenProcess.argtypes=[ct.c_ulong,ct.c_int,ct.c_ulong]
kernel.CloseHandle.argtypes=[ct.c_void_p]
psapi=ct.WinDLL('psapi',use_last_error=True)
psapi.GetProcessMemoryInfo.argtypes=[ct.c_void_p,ct.POINTER(Memoria),ct.c_ulong]
def disponible():
    m=Estado();m.length=ct.sizeof(m);kernel.GlobalMemoryStatusEx(ct.byref(m));return m

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--java',default='java')
    parser.add_argument('--repeticiones',type=int,default=3)
    parser.add_argument('--limite',type=float,default=45)
    parser.add_argument('--bubble-limite',type=float,default=8)
    parser.add_argument('--max-n',type=int,default=1_000_000_000)
    parser.add_argument('--min-n',type=int,default=100_000)
    parser.add_argument('--lenguajes',nargs='+',default=['Python','Java'])
    parser.add_argument('--append',action='store_true')
    parser.add_argument('--algoritmos',nargs='+',default=['bubble','merge','tree','heap','counting'])
    parser.add_argument('--tamanos',type=int,nargs='+',default=[100_000,1_000_000,10_000_000,100_000_000,1_000_000_000])
    parser.add_argument('--presupuesto-mib',type=int,default=256)
    args=parser.parse_args()
    (BASE/'resultados').mkdir(exist_ok=True)
    m=disponible()
    metadata=dict(sistema=platform.platform(),cpu=platform.processor(),python=sys.version,
        java=subprocess.run([args.java,'-version'],capture_output=True,text=True).stderr.strip(),
        ram_total_bytes=m.total,ram_disponible_inicio_bytes=m.avail,
        argumentos=vars(args),semilla=2026,rango='[-500.00, 500.00], paso 0.01',
        memoria='PeakWorkingSetSize del proceso completo; MiB=2^20 bytes',
        reloj='perf_counter Python; nanoTime Java; solo ordenamiento',
        repeticiones='procesos nuevos, 200 elementos de calentamiento (Java 5 veces)')
    (BASE/'resultados'/(f'entorno_{time.time_ns()}.json' if args.append else 'entorno.json')).write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    columnas=['lenguaje','algoritmo','n','repeticion','estado','segundos','pico_mib','valido','motivo']
    fallos=set()
    with (BASE/'resultados'/'mediciones.csv').open('a' if args.append else 'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columnas)
        if not args.append:writer.writeheader()
        for lenguaje in args.lenguajes:
            for algoritmo in args.algoritmos:
                for n in args.tamanos:
                    if n<args.min_n:continue
                    motivo=''
                    # Estimaciones de preseleccion, no mediciones del algoritmo.
                    requerido=(48 if lenguaje=='Python' else 20)*n + 32*2**20
                    presupuesto=min(args.presupuesto_mib*2**20,max(0,disponible().avail-128*2**20))
                    if algoritmo=='bubble' and n>100_000: motivo='Costo cuadratico: omitido por presupuesto de tiempo'
                    elif n>args.max_n: motivo='Fuera del maximo n configurado para esta sesion'
                    elif requerido>presupuesto: motivo='Preseleccion: excede presupuesto conservador de memoria'
                    elif (lenguaje,algoritmo) in fallos: motivo='Tamano mayor omitido tras interrupcion del menor'
                    if motivo:
                        writer.writerow(dict(lenguaje=lenguaje,algoritmo=algoritmo,n=n,repeticion=0,estado='NO_EJECUTADO',motivo=motivo));f.flush();continue
                    for rep in range(1,args.repeticiones+1):
                        cmd=([sys.executable,str(PYTHON_DIR/'caso.py'),algoritmo,str(n)] if lenguaje=='Python'
                            else [args.java,'-Xms16m','-Xmx256m','-cp',str(JAVA_DIR),'Ordenamientos',algoritmo,str(n)])
                        limite=args.bubble_limite if algoritmo=='bubble' else args.limite
                        fila=dict(lenguaje=lenguaje,algoritmo=algoritmo,n=n,repeticion=rep)
                        inicio=time.perf_counter();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                        handle=kernel.OpenProcess(0x410,False,p.pid);pico=0;estado='OK';motivo=''
                        while True:
                            mem=Memoria();mem.cb=ct.sizeof(mem)
                            if handle and psapi.GetProcessMemoryInfo(handle,ct.byref(mem),mem.cb):pico=max(pico,mem.PeakWorkingSetSize)
                            terminado=p.poll() is not None
                            if terminado:break
                            if time.perf_counter()-inicio>limite:
                                estado='TIEMPO_LIMITE';motivo=f'Proceso supero {limite:g} s; no es tiempo de ordenamiento completo';p.kill();break
                            if pico>args.presupuesto_mib*2**20:
                                estado='MEMORIA_LIMITE';motivo='Proceso supero presupuesto de memoria';p.kill();break
                            time.sleep(.02)
                        stdout,stderr=p.communicate()
                        if handle:kernel.CloseHandle(handle)
                        fila.update(estado=estado,pico_mib=round(pico/2**20,3),motivo=motivo)
                        if estado=='OK':
                            try:
                                resultado=json.loads(stdout.strip().splitlines()[-1]);fila.update(resultado)
                                if p.returncode or not resultado['valido']:raise ValueError('validacion fallida')
                            except Exception:
                                fila.update(estado='ERROR',motivo=(stderr or stdout)[-500:])
                        writer.writerow(fila);f.flush()
                        print(lenguaje,algoritmo,n,rep,fila['estado'],fila.get('segundos',''),flush=True)
                        if fila['estado']!='OK':fallos.add((lenguaje,algoritmo));break

if __name__=='__main__':main()
