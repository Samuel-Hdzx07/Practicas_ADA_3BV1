from pathlib import Path
from array import array
import sys,time,json
from dac import *

tipo=sys.argv[1]
if tipo=='select':
    n,bits=int(sys.argv[2]),int(sys.argv[3]);k=(n+1)//2
    quickselect(array('i',[3,1,2]),2)
    a=datos_seleccion(n,bits)
    inicio=time.perf_counter();valor=quickselect(a,k);segundos=time.perf_counter()-inicio
    # Rango calculado contra la secuencia original, no contra un arreglo ordenado.
    menores=iguales=0
    for i in range(n):
        v=(7654321*i+1234567)%M+1
        menores+=v<valor;iguales+=v==valor
    valido=menores<k<=menores+iguales
    print(json.dumps(dict(segundos=segundos,valido=valido,valor=int(valor),k=k)),flush=True)
elif tipo=='matrix':
    n=int(sys.argv[2]);metodo=sys.argv[3];plana=sys.argv[4]=='1d'
    a=datos_matriz(n,2026,plana);b=datos_matriz(n,2027,plana)
    inicio=time.perf_counter()
    c=strassen(a,b,n,plana) if metodo=='strassen' else tradicional_1d(a,b,n) if plana else tradicional_2d(a,b,n)
    segundos=time.perf_counter()-inicio
    ruta=Path(__file__).resolve().parents[1]/'referencias'/f'{n}.bin'
    ref=array('q');ref.frombytes(ruta.read_bytes())
    if sys.byteorder=='little':ref.byteswap()
    valido=aplanar(c,plana)==ref
    print(json.dumps(dict(segundos=segundos,valido=valido)),flush=True)
else:raise ValueError(tipo)
