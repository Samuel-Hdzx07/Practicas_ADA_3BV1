"""Quickselect y multiplicacion clasica/Strassen, sin librerias numericas."""
from array import array

M = 10_000_000
class Aleatorio:
    def __init__(self, semilla=2026): self.x=semilla
    def siguiente(self):
        self.x=(1664525*self.x+1013904223)&0xffffffff
        return self.x

def datos_seleccion(n,bits):
    if not 0<n<=M: raise ValueError('n fuera de rango')
    a=array('i' if bits==32 else 'q',((7654321*i+1234567)%M+1 for i in range(n)))
    assert a.itemsize==bits//8
    rng=Aleatorio()
    for i in range(n-1,0,-1):
        j=rng.siguiente()%(i+1)
        a[i],a[j]=a[j],a[i]
    return a

def quickselect(a,k):
    if not 1<=k<=len(a): raise ValueError('k debe pertenecer a [1,n]')
    objetivo=k-1;izq=0;der=len(a)-1;rng=Aleatorio(99)
    while izq<=der:
        pivote=a[izq+rng.siguiente()%(der-izq+1)]
        menor=i=izq;mayor=der
        while i<=mayor:
            if a[i]<pivote:
                a[menor],a[i]=a[i],a[menor];menor+=1;i+=1
            elif a[i]>pivote:
                a[i],a[mayor]=a[mayor],a[i];mayor-=1
            else:i+=1
        if objetivo<menor:der=menor-1
        elif objetivo>mayor:izq=mayor+1
        else:return pivote
    raise AssertionError('Invariante invalida')

def datos_matriz(n,semilla,plana):
    rng=Aleatorio(semilla)
    datos=array('q',(rng.siguiente()%19-9 for _ in range(n*n)))
    return datos if plana else [datos[i*n:(i+1)*n] for i in range(n)]

def tradicional_1d(a,b,n):
    c=array('q',[0])*(n*n)
    for i in range(n):
        fila=i*n
        for k in range(n):
            v=a[fila+k];otra=k*n
            for j in range(n):c[fila+j]+=v*b[otra+j]
    return c

def tradicional_2d(a,b,n):
    c=[array('q',[0])*n for _ in range(n)]
    for i in range(n):
        ai=a[i];ci=c[i]
        for k in range(n):
            v=ai[k];bk=b[k]
            for j in range(n):ci[j]+=v*bk[j]
    return c

def sumar(a,b,signo,plana):
    if plana:return array('q',(x+signo*y for x,y in zip(a,b)))
    return [array('q',(x+signo*y for x,y in zip(ar,br))) for ar,br in zip(a,b)]

def dividir(a,n,plana):
    h=n//2;partes=[]
    for r,c in [(0,0),(0,h),(h,0),(h,h)]:
        if plana:
            bloque=array('q')
            for i in range(h):bloque.extend(a[(r+i)*n+c:(r+i)*n+c+h])
        else:bloque=[a[r+i][c:c+h] for i in range(h)]
        partes.append(bloque)
    return partes

def unir(c11,c12,c21,c22,h,plana):
    if not plana:return [c11[i]+c12[i] for i in range(h)]+[c21[i]+c22[i] for i in range(h)]
    c=array('q');
    for izq,der in [(c11,c12),(c21,c22)]:
        for i in range(h):c.extend(izq[i*h:(i+1)*h]);c.extend(der[i*h:(i+1)*h])
    return c

def strassen(a,b,n,plana,umbral=16):
    if n<=umbral:return tradicional_1d(a,b,n) if plana else tradicional_2d(a,b,n)
    if n%2:raise ValueError('Se requiere dimension potencia de dos')
    h=n//2
    a11,a12,a21,a22=dividir(a,n,plana);b11,b12,b21,b22=dividir(b,n,plana)
    def add(x,y):return sumar(x,y,1,plana)
    def sub(x,y):return sumar(x,y,-1,plana)
    def mul(x,y):return strassen(x,y,h,plana,umbral)
    m1=mul(add(a11,a22),add(b11,b22))
    m2=mul(add(a21,a22),b11)
    m3=mul(a11,sub(b12,b22))
    m4=mul(a22,sub(b21,b11))
    m5=mul(add(a11,a12),b22)
    m6=mul(sub(a21,a11),add(b11,b12))
    m7=mul(sub(a12,a22),add(b21,b22))
    return unir(add(sub(add(m1,m4),m5),m7),add(m3,m5),add(m2,m4),add(add(sub(m1,m2),m3),m6),h,plana)

def aplanar(a,plana):
    if plana:return a
    out=array('q')
    for fila in a:out.extend(fila)
    return out
