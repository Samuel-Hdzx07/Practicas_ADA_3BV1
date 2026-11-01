from array import array
from dac import *
cuenta=0
for bits in [32,64]:
    for datos in [[9],[3,2,1],[2,2,1,2,3],[-5,0,4,-5]]:
        for k in range(1,len(datos)+1):
            assert quickselect(array('i' if bits==32 else 'q',datos),k)==sorted(datos)[k-1]
            cuenta+=1
for datos,k in [([],1),([1],0),([1],2)]:
    try:quickselect(datos,k);raise AssertionError('Falto validar k')
    except ValueError:cuenta+=1
for n in [1,2,4,8,16,32]:
    a=datos_matriz(n,2026,False);b=datos_matriz(n,2027,False)
    # Referencia independiente i,j,k; los metodos medidos usan i,k,j.
    ref=array('q',(sum(a[i][k]*b[k][j] for k in range(n)) for i in range(n) for j in range(n)))
    for plana in [False,True]:
        aa=aplanar(a,False) if plana else a;bb=aplanar(b,False) if plana else b
        tradicional=tradicional_1d(aa,bb,n) if plana else tradicional_2d(aa,bb,n)
        assert aplanar(tradicional,plana)==ref;cuenta+=1
        for umbral in [1,16]:
            assert aplanar(strassen(aa,bb,n,plana,umbral),plana)==ref;cuenta+=1
assert datos_seleccion(1000,32)==array('i',datos_seleccion(1000,64));cuenta+=1
assert len(set(datos_seleccion(1000,32)))==1000;cuenta+=1
print(cuenta,'pruebas Python correctas')
