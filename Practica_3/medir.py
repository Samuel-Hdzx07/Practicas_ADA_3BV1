"""Mediciones aisladas en Windows. Solo biblioteca estandar."""
from pathlib import Path
import argparse,csv,ctypes as ct,hashlib,json,platform,subprocess,sys,time
B=Path(__file__).resolve().parent
class Mem(ct.Structure):
    _fields_=[('cb',ct.c_ulong),('fallos',ct.c_ulong)]+[(s,ct.c_size_t) for s in ['pico','actual','pp','p','np','n','page','peakpage']]
class Estado(ct.Structure):
    _fields_=[('length',ct.c_ulong),('load',ct.c_ulong)]+[(s,ct.c_ulonglong) for s in ['total','libre','page','apage','virt','avirt','ext']]
K=ct.WinDLL('kernel32',use_last_error=True);K.OpenProcess.restype=ct.c_void_p;K.OpenProcess.argtypes=[ct.c_ulong,ct.c_int,ct.c_ulong];K.CloseHandle.argtypes=[ct.c_void_p]
P=ct.WinDLL('psapi',use_last_error=True);P.GetProcessMemoryInfo.argtypes=[ct.c_void_p,ct.POINTER(Mem),ct.c_ulong]
def memoria():
    s=Estado();s.length=ct.sizeof(s);K.GlobalMemoryStatusEx(ct.byref(s));return s
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--java',default='java');ap.add_argument('--javac',default='javac');ap.add_argument('--limite',type=float,default=180);ap.add_argument('--memoria-mib',type=int,default=1024);ap.add_argument('--reanudar',action='store_true');args=ap.parse_args()
    for f in ['resultados','referencias','evidencias']:(B/f).mkdir(exist_ok=True)
    subprocess.run([args.javac,str(B/'java/Practica3.java')],check=True)
    java=[args.java,'-Xms16m','-Xmx768m','-cp',str(B/'java'),'Practica3']
    checks=[]
    for cmd in [[sys.executable,str(B/'python/pruebas.py')],java+['test']]:
        r=subprocess.run(cmd,capture_output=True,text=True,check=True);checks.append(r.stdout.strip())
    (B/'resultados/pruebas.txt').write_text('\n'.join(checks),encoding='utf-8')
    # Referencias exactas de todas las celdas, fuera de las mediciones.
    for n in [16,32,64,128,256,512]:subprocess.run(java+['reference',str(n),str(B/f'referencias/{n}.bin')],check=True)
    env=dict(sistema=platform.platform(),cpu=platform.processor(),python=sys.version,java=subprocess.run([args.java,'-version'],capture_output=True,text=True).stderr,ram_total=memoria().total,ram_libre=memoria().libre,opciones=vars(args),fecha_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),referencias_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'referencias').glob('*.bin')})
    (B/'resultados/entorno.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
    tamanos=[1000,5000,10000,5000,100000,500000,1000000,5000000,10000000,50000]
    casos=[]
    for lang in ['Java','Python']:
        for bits in [32,64]:
            for posicion,n in enumerate(tamanos):casos.append(dict(lenguaje=lang,problema='quickselect',n=n,bits=bits,metodo='quickselect',representacion='array',ensayo=posicion+1,complementaria=n==50000))
        for n in [16,32,64,128,256,512]:
            for metodo in ['tradicional','strassen']:
                for rep in ['2d','1d']:casos.append(dict(lenguaje=lang,problema='matriz',n=n,bits=64,metodo=metodo,representacion=rep,ensayo=1,complementaria=False))
    columnas=list(casos[0])+['estado','segundos','pico_mib','valido','valor','k','motivo']
    completados=set()
    if args.reanudar and (B/'resultados/mediciones.csv').exists():
        with (B/'resultados/mediciones.csv').open(encoding='utf-8') as f:
            completados={(r['lenguaje'],r['problema'],r['n'],r['bits'],r['metodo'],r['representacion'],r['ensayo']) for r in csv.DictReader(f) if r['estado']=='OK'}
    with (B/'resultados/mediciones.csv').open('a' if args.reanudar else 'w',newline='',encoding='utf-8') as f, (B/'evidencias/ejecuciones.log').open('a' if args.reanudar else 'w',encoding='utf-8') as log:
        writer=csv.DictWriter(f,fieldnames=columnas)
        if not args.reanudar:writer.writeheader()
        for indice,caso in enumerate(casos,1):
            clave=tuple(str(caso[x]) for x in ['lenguaje','problema','n','bits','metodo','representacion','ensayo'])
            if clave in completados:continue
            n=caso['n'];tipo='select' if caso['problema']=='quickselect' else 'matrix'
            params=[tipo,str(n),str(caso['bits'])] if tipo=='select' else [tipo,str(n),caso['metodo'],caso['representacion']]
            if caso['lenguaje']=='Java':
                if tipo=='matrix':params.append(str(B/f'referencias/{n}.bin'))
                cmd=java+params
            else:cmd=[sys.executable,str(B/'python/caso.py')]+params
            inicio=time.perf_counter();proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            handle=K.OpenProcess(0x410,False,proc.pid);pico=0;estado='OK';motivo=''
            while True:
                m=Mem();m.cb=ct.sizeof(m)
                if handle and P.GetProcessMemoryInfo(handle,ct.byref(m),m.cb):pico=max(pico,m.pico)
                if proc.poll() is not None:break
                if time.perf_counter()-inicio>args.limite:estado='TIEMPO_LIMITE';motivo=f'Vida del proceso supera {args.limite}s';proc.kill();break
                if pico>args.memoria_mib*2**20 or memoria().libre<256*2**20:estado='MEMORIA_LIMITE';motivo='Limite de pico o reserva de RAM libre de 256 MiB';proc.kill();break
                time.sleep(.02)
            out,err=proc.communicate()
            if handle:K.CloseHandle(handle)
            fila=dict(caso,estado=estado,pico_mib=round(pico/2**20,3),motivo=motivo)
            if estado=='OK':
                try:
                    datos=json.loads(out.strip().splitlines()[-1]);fila.update(datos)
                    if proc.returncode or not datos['valido']:raise ValueError('Validacion fallida')
                except Exception:fila.update(estado='ERROR',motivo=(err or out)[-1000:])
            writer.writerow(fila);f.flush()
            mensaje=f'[{indice}/{len(casos)}] {caso} -> {fila}'
            log.write(mensaje+'\n');log.flush();print(mensaje,flush=True)
    print('FIN DE LAS EJECUCIONES',flush=True)
if __name__=='__main__':main()
