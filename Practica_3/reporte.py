from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from xml.sax.saxutils import escape
from collections import defaultdict
import csv,json,statistics,math
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing,Line,String,PolyLine,Circle
from pypdf import PdfWriter,PdfReader
import pypdfium2 as pdfium
B=Path(__file__).resolve().parent;Q=B/'qa';Q.mkdir(exist_ok=True)
rows=list(csv.DictReader((B/'resultados/mediciones.csv').open(encoding='utf-8')))
assert len(rows)==88 and all(r['estado']=='OK' and r['valido']=='True' for r in rows)
G=defaultdict(list)
for r in rows:G[(r['lenguaje'],r['problema'],int(r['n']),int(r['bits']),r['metodo'],r['representacion'])].append(r)
def val(lang,problema,n,bits=64,metodo='quickselect',rep='array'):
    rr=G[(lang,problema,n,bits,metodo,rep)]
    return statistics.median(float(r['segundos']) for r in rr),max(float(r['pico_mib']) for r in rr)
for n in [1000,5000,10000,50000,100000,500000,1000000,5000000,10000000]:
    vv={r['valor'] for r in rows if r['problema']=='quickselect' and int(r['n'])==n};assert len(vv)==1
summary=[]
for key,rs in sorted(G.items()):
    l,p,n,b,m,rep=key;t,mem=val(l,p,n,b,m,rep)
    summary.append(dict(lenguaje=l,problema=p,n=n,bits=b,metodo=m,representacion=rep,repeticiones=len(rs),segundos=t,pico_mib=mem,valido=True))
with (B/'resultados/resumen.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
env=json.loads((B/'resultados/entorno.json').read_text(encoding='utf-8'))
for name,file in [('Arial','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf'),('Mono','consola.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
logos=[str(B/'assets/ipn.png'),str(B/'assets/escom.png')]
c=canvas.Canvas(str(Q/'portada.pdf'),pagesize=(612,792))
c.drawImage(ImageReader(logos[0]),2,704,width=107,height=76,mask='auto');c.drawImage(ImageReader(logos[1]),521,711,width=91,height=69,mask='auto')
def line(t,y,size,color='#282828',font='Bold'):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawCentredString(306,y,t)
line('INSTITUTO POLITÉCNICO NACIONAL',690,20,'#003366');line('ESCUELA SUPERIOR DE CÓMPUTO',632,20,'#4682B4')
line('UNIDAD DE APRENDIZAJE:',555,16,'#646464');line('ANÁLISIS Y DESARROLLO DE ALGORITMOS',528,16,'#646464')
line('PRÁCTICA 3',460,18,'#003366');line('DIVIDE Y VENCERÁS',432,20,'#003366');line('Quickselect y multiplicación de Strassen',391,12,'#646464','Italic')
line('Profesor: ANDRES GARCIA FLORIANO',290,15);line('Alumno:',240,16);line('Hernandez Barrios Samuel Rodrigo',215,16);line('Tercer semestre',162,16);line('3BV1',121,16);line('Fecha de entrega: 30 de octubre de 2026',78,14)
c.showPage();c.save()
S={'p':ParagraphStyle('p',fontName='Arial',fontSize=10.5,leading=14,spaceAfter=8),'h1':ParagraphStyle('h1',fontName='Bold',fontSize=18,leading=22,spaceAfter=12,keepWithNext=True),'h2':ParagraphStyle('h2',fontName='Bold',fontSize=12,leading=16,spaceBefore=8,spaceAfter=6,keepWithNext=True),'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=11),'head':ParagraphStyle('head',fontName='Bold',fontSize=9,leading=11),'code':ParagraphStyle('code',fontName='Mono',fontSize=9.5,leading=13,spaceAfter=9)}
flow=[]
def p(t):flow.append(Paragraph(escape(t),S['p']))
def h(t):flow.append(Paragraph(escape(t),S['h2']))
def page(t,first=False):
    if not first:flow.append(PageBreak())
    flow.append(Paragraph(escape(t),S['h1']))
def code(t):flow.append(Preformatted(t,S['code']))
def table(data,widths):
    t=Table([[Paragraph(escape(str(v)),S['head' if i==0 else 'cell']) for v in row] for i,row in enumerate(data)],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,HexColor('#D9D9D9')),('BACKGROUND',(0,0),(-1,0),HexColor('#DFEAF3')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),7)]));flow.append(t);flow.append(Spacer(1,8))
page('1 Objetivo y protocolo experimental',True)
p('Se resuelve la selección del elemento de posición k mediante Quickselect y se implementa la multiplicación de Strassen. Se comparan Java y Python, enteros de 32 y 64 bits, y matrices representadas en dos dimensiones y en un arreglo contiguo unidimensional. Todas las ejecuciones registradas terminaron y pasaron la validación.')
h('Cobertura de las pruebas')
p('Se realizaron 88 ejecuciones: 40 de Quickselect y 48 de matrices. La lista de la consigna repite n = 5000; se conserva como un segundo ensayo. Se añade n = 50000 como complemento claramente identificado: son cuatro ejecuciones adicionales. Así, las 84 ejecuciones de la lista literal se completaron, además de las cuatro complementarias. No hay casos omitidos por recursos.')
p('En términos de combinaciones únicas, se cubrieron las 80 exigidas: ocho tamaños distintos de Quickselect × dos tipos × dos lenguajes = 32, y seis tamaños de matrices × dos métodos × dos representaciones × dos lenguajes = 48. El complemento de 50000 añade otras cuatro combinaciones.')
h('Tiempo y memoria')
p('Cada ensayo se ejecuta en un proceso nuevo y los procesos se lanzan secuencialmente. El tiempo mide solo el algoritmo; excluye generación, lectura de referencias y validación. Python utiliza perf_counter y Java nanoTime. Quickselect tiene un calentamiento de tres valores; no se aplica un calentamiento prolongado de la JVM para matrices. Las cifras incluyen efectos de compilación JIT dentro de la región medida.')
p('La memoria es el pico residente del proceso completo, PeakWorkingSetSize de Windows, consultado cada 20 ms. Incluye runtime, datos, algoritmo y validación; no equivale al espacio auxiliar aislado. MiB = 2^20 bytes. Hay una observación por configuración, salvo n = 5000, repetido por la lista de origen; en ese caso las tablas muestran la mediana de dos tiempos y el mayor pico. No se infiere significancia estadística.')
h('Validación y entorno')
p('Antes de medir se aprobaron 62 pruebas Java y 67 Python. Incluyen extremos de k, duplicados, valores negativos y productos comparados con una referencia independiente con ciclos i,j,k. Las matrices grandes se comparan celda por celda con archivos de referencia calculados fuera de las mediciones. Quickselect se valida por el rango del resultado contra los valores originales.')
p(f'Sistema: {env["sistema"]}. RAM física: {env["ram_total"]/2**30:.2f} GiB; libre al inicio: {env["ram_libre"]/2**30:.2f} GiB. Java: '+env['java'].splitlines()[0]+'. Python: '+env['python'].splitlines()[0]+'. El archivo entorno.json conserva versiones, opciones y hashes SHA-256 de las referencias.')

page('2 Quickselect y generación de datos')
p('Se busca el elemento que ocuparía la posición k al ordenar de forma creciente, usando k desde 1. Quickselect evita ordenar todo el arreglo: particiona alrededor de un pivote y continúa únicamente en el segmento que contiene la posición buscada.')
h('Partición en tres regiones')
code('objetivo = k - 1\nMientras el intervalo no este vacio:\n    elegir un pivote seudoaleatorio del intervalo\n    dividir en valores menores, iguales y mayores\n    si objetivo esta en menores: continuar a la izquierda\n    si objetivo esta en mayores: continuar a la derecha\n    si objetivo esta en iguales: devolver pivote')
p('La partición mantiene los elementos menores a la izquierda, los iguales al centro y los mayores a la derecha. Cada intercambio conserva los valores. Si el objetivo queda en la región de iguales, el pivote es la respuesta; en caso contrario se descarta una región que no puede contener la posición. La implementación iterativa evita acumular llamadas recursivas y maneja duplicados.')
h('Distribución y anchura de los enteros')
p('Se define v(i) = ((7654321i + 1234567) módulo 10000000) + 1 para i de 0 a n − 1. El multiplicador es coprimo con 10000000; por ello no repite valores en los tamaños usados. Se aplica Fisher–Yates con un LCG de 32 bits y semilla 2026 para obtener el orden seudoaleatorio. No es un generador criptográfico ni una muestra uniforme de todos los subconjuntos posibles.')
p('Los valores pertenecen a [1, 10^7]. Para n = 10^7 forman una permutación de todo ese intervalo; para n menores se baraja un subconjunto determinista distribuido en el intervalo. Java usa int[] y long[]; Python usa array(i) y array(q), verificando que sus elementos ocupen 4 y 8 bytes. Los valores caben en 32 bits: la diferencia experimental es su almacenamiento, no un rango numérico distinto.')
p('Se mide la posición k = piso((n + 1)/2), la mediana inferior cuando n es par. La comprobación cuenta valores originales menores e iguales al resultado y verifica menores < k ≤ menores + iguales. Los resultados coinciden entre lenguajes y anchuras para cada tamaño; con diez millones el resultado es 5000000.')
h('Complejidad')
p('Con particiones razonablemente equilibradas, el tiempo esperado es Θ(n); si los pivotes producen divisiones extremas de forma repetida, el peor caso es Θ(n²). El espacio auxiliar de esta versión iterativa es Θ(1), excluyendo la entrada. El arreglo requiere 4n u 8n bytes, además de encabezados y runtime.')

page('3 Resultados de Quickselect')
p('Tiempos en segundos y memoria en MiB del proceso completo. n = 50000 es complementario; n = 5000 reúne los dos ensayos de la lista original. Todos los valores seleccionados pasaron la validación del rango k.')
ns=[1000,5000,10000,50000,100000,500000,1000000,5000000,10000000]
h('Tiempo de selección')
t=[['n','Java 32','Java 64','Python 32','Python 64']]
for n in ns:t.append([f'{n:,}']+[f'{val(l,"quickselect",n,b)[0]:.6f}' for l,b in [('Java',32),('Java',64),('Python',32),('Python',64)]])
table(t,[100,102,102,102,102])
h('Pico residente del proceso')
t=[['n','Java 32','Java 64','Python 32','Python 64']]
for n in ns:t.append([f'{n:,}']+[f'{val(l,"quickselect",n,b)[1]:.2f}' for l,b in [('Java',32),('Java',64),('Python',32),('Python',64)]])
table(t,[100,102,102,102,102])
p('El ruido de arranque y el pequeño número de observaciones afectan especialmente los casos breves. El consumo total no tiene por qué duplicarse entre 32 y 64 bits: el runtime y otras estructuras contribuyen al pico medido.')

page('4 Multiplicación de Strassen')
p('El método tradicional usa tres ciclos i,k,j y calcula C[i,j] acumulando A[i,k]B[k,j]. Strassen divide A y B en cuatro bloques y reemplaza las ocho multiplicaciones convencionales por siete productos recursivos.')
h('Siete productos')
code('M1 = (A11 + A22)(B11 + B22)\nM2 = (A21 + A22)B11\nM3 = A11(B12 - B22)\nM4 = A22(B21 - B11)\nM5 = (A11 + A12)B22\nM6 = (A21 - A11)(B11 + B12)\nM7 = (A12 - A22)(B21 + B22)\n\nC11 = M1 + M4 - M5 + M7\nC12 = M3 + M5\nC21 = M2 + M4\nC22 = M1 - M2 + M3 + M6')
h('Condiciones de la implementación')
p('Se prueban n = 16, 32, 64, 128, 256 y 512, todos potencias de dos. Cada entrada contiene enteros entre −9 y 9 generados con el mismo LCG: semilla 2026 para A y 2027 para B. Los valores coinciden en Java y Python. Se utiliza un umbral de 16: los subproblemas de tamaño ≤ 16 se resuelven con el método tradicional; por eso el ensayo Strassen de n = 16 corresponde a su caso base.')
p('Java almacena entradas y resultados en long. Python usa buffers array(q) de 64 bits, aunque sus operaciones temporales son enteros de precisión arbitraria. Los valores de entrada acotados y estos tamaños mantienen los resultados e intermedios dentro del rango de 64 bits. La igualdad de los productos se comprueba exactamente, sin tolerancias de punto flotante.')
h('Representaciones y complejidad')
p('En 2D, Java usa long[][] y Python una lista de filas array(q): cada fila tiene datos contiguos, pero las filas se asignan por separado. En 1D, Java usa long[] y Python un solo array(q) de n² elementos, con índice i·n+j. El término contiguo se refiere al buffer de valores de la matriz, no al lugar de los demás objetos del proceso.')
p('Tradicional cuesta Θ(n³). Strassen cumple T(n) = 7T(n/2) + Θ(n²), por lo que el teorema maestro da Θ(n^log_2(7)), aproximadamente Θ(n^2.807). Esta implementación copia bloques y conserva productos intermedios; su espacio auxiliar asintótico es O(n²). Su menor exponente no garantiza que sea más rápido en todas las dimensiones pequeñas.')

for lang in ['Java','Python']:
    page(('5' if lang=='Java' else '6')+' Resultados de matrices en '+lang)
    p('Cada cifra procede de una ejecución completa y validada. 2D indica filas separadas; 1D, buffer plano. Los tiempos excluyen la generación de matrices y la comprobación del resultado.')
    h('Tiempo en segundos')
    t=[['n','Tradicional 2D','Tradicional 1D','Strassen 2D','Strassen 1D']]
    for n in [16,32,64,128,256,512]:t.append([n]+[f'{val(lang,"matriz",n,64,m,r)[0]:.6f}' for m,r in [('tradicional','2d'),('tradicional','1d'),('strassen','2d'),('strassen','1d')]])
    table(t,[44,116,116,116,116])
    h('Pico residente del proceso en MiB')
    t=[['n','Tradicional 2D','Tradicional 1D','Strassen 2D','Strassen 1D']]
    for n in [16,32,64,128,256,512]:t.append([n]+[f'{val(lang,"matriz",n,64,m,r)[1]:.2f}' for m,r in [('tradicional','2d'),('tradicional','1d'),('strassen','2d'),('strassen','1d')]])
    table(t,[44,116,116,116,116])
    h('Comparación con n igual a 512')
    for rep in ['2d','1d']:
        trad=val(lang,'matriz',512,64,'tradicional',rep)[0];st=val(lang,'matriz',512,64,'strassen',rep)[0]
        p(f'En {rep.upper()}, tradicional tarda {trad:.6f} s y Strassen {st:.6f} s. La razón tiempo tradicional / tiempo Strassen es {trad/st:.2f}. Una razón mayor que 1 favorece Strassen; menor que 1 favorece el método tradicional.')
    p('Las diferencias entre 1D y 2D incluyen acceso por índices, operaciones sobre filas, creación de bloques y administración de memoria. No se atribuyen solo a la localidad de caché. El experimento no utiliza BLAS, NumPy ni multiplicación de bibliotecas.')

def chart(title,series,xs,logy=True):
    d=Drawing(508,243);l,b,w,hh=62,45,425,158
    values=[v for label,color,ys in series for v in ys]
    lo=math.floor(math.log10(min(values))) if logy else 0;hi=math.ceil(math.log10(max(values))) if logy else math.ceil(max(values)/10)*10
    if hi==lo:hi+=1
    def xy(x,y):return (l+w*(math.log10(x)-math.log10(min(xs)))/(math.log10(max(xs))-math.log10(min(xs))),b+hh*((math.log10(y)-lo)/(hi-lo) if logy else y/hi))
    d.add(String(l,b+hh+22,title,fontName='Bold',fontSize=11))
    for tick in range(lo,hi+1) if logy else range(0,int(hi)+1,10):
        yy=b+hh*((tick-lo)/(hi-lo) if logy else tick/hi);d.add(Line(l,yy,l+w,yy,strokeColor=HexColor('#dddddd')));d.add(String(l-6,yy-3,f'10^{tick}' if logy else str(tick),fontName='Arial',fontSize=8,textAnchor='end'))
    for x in xs:
        xx,_=xy(x,values[0]);d.add(String(xx,b-15,f'{x:g}',fontName='Arial',fontSize=8,textAnchor='middle'))
    for j,(label,color,ys) in enumerate(series):
        points=[]
        for x,y in zip(xs,ys):
            xx,yy=xy(x,y);points.extend([xx,yy]);d.add(Circle(xx,yy,2,fillColor=HexColor(color),strokeColor=None))
        d.add(PolyLine(points,strokeColor=HexColor(color),strokeWidth=1.2));d.add(String(l+(j%2)*220,14-(j//2)*12,label,fontName='Arial',fontSize=8,fillColor=HexColor(color)))
    return d
page('7 Gráficas comparativas')
xs=[1000,10000,100000,1000000,10000000]
flow.append(chart('Quickselect de 64 bits · segundos',[(l,c,[val(l,'quickselect',n,64)[0] for n in xs]) for l,c in [('Java','#225c88'),('Python','#c46a20')]],xs))
flow.append(Spacer(1,20))
xs=[16,32,64,128,256,512]
flow.append(chart('Matrices Python · segundos',[(label,c,[val('Python','matriz',n,64,m,r)[0] for n in xs]) for label,c,m,r in [('Tradicional 2D','#225c88','tradicional','2d'),('Tradicional 1D','#c46a20','tradicional','1d'),('Strassen 2D','#228844','strassen','2d'),('Strassen 1D','#8646a3','strassen','1d')]],xs))
p('Ambos ejes son logarítmicos. Las líneas unen observaciones medidas, sin interpolar nuevas ejecuciones ni predecir tiempos. Las tablas previas contienen todos los casos de 32 bits, 64 bits, matrices y memoria.')
p('La tendencia de Quickselect es compatible con un costo esperado lineal en esta secuencia, con variación por el número de particiones. En matrices, el umbral, las copias y la sobrecarga explican que el cruce entre métodos dependa del lenguaje y de la dimensión; una sola observación por configuración limita la precisión de esa comparación.')

page('8 Resultados y reproducción')
h('Resultados verificados')
table([['Apartado','Ejecuciones','Estado'],['Quickselect Java 32 y 64 bits','20','Todas correctas'],['Quickselect Python 32 y 64 bits','20','Todas correctas'],['Matrices Java 2D y 1D','24','Todas correctas'],['Matrices Python 2D y 1D','24','Todas correctas'],['Total','88','88 terminadas y verificadas']],[266,100,142])
p('Las 84 ejecuciones de la lista literal, incluida la repetición de 5000, están completas. También terminaron las cuatro pruebas complementarias de 50000. No hubo agotamiento de recursos ni cortes, por lo que no se requieren capturas de fallos. Se conserva el registro de cada ejecución en evidencias/ejecuciones.log, con configuración, tiempo, memoria y resultado de validación.')
h('Estructura y comandos')
code('Practica_3/\n  python/       algoritmos, caso y pruebas\n  java/         Practica3.java\n  referencias/  productos exactos en binario\n  resultados/   CSV, resumen, entorno y pruebas\n  evidencias/   registro de ejecuciones\n  medir.py      ejecucion aislada\n  README.md     instrucciones\n  Practica3_ADA_Hernandez_Barrios_Samuel_Rodrigo_3BV1.pdf')
code('python python/pruebas.py\njavac java/Practica3.java\njava -cp java Practica3 test\npython medir.py --java java --javac javac')
p('Requisitos: Python 3, JDK 17 o superior y Windows para el medidor de memoria. Las implementaciones de algoritmos no necesitan paquetes externos. Las referencias se regeneran al ejecutar el medidor y sus hashes permiten comprobar los archivos usados. Se pueden retomar casos incompletos con --reanudar; los datos crudos se conservan.')
flow.append(Paragraph('Repositorio público: <link href="https://github.com/Samuel-Hdzx07/Practicas_ADA_3BV1/tree/main/Practica_3" color="#003366">Practicas_ADA_3BV1 / Practica_3</link>. La práctica 2 se conserva por separado en Practica_2.',S['p']))
h('Referencias y declaración de apoyo de IA')
flow.append(Paragraph('OpenAI. (2026). ChatGPT [Herramienta de inteligencia artificial generativa]. <link href="https://chatgpt.com" color="#003366">https://chatgpt.com</link>.',S['p']))
p('Se utilizó ChatGPT como apoyo en el formato, la organización y el contenido.')
def footer(c,d):
    c.setFont('Arial',8);c.setFillColor(HexColor('#646464'));c.drawString(52,30,'ADA | Práctica 3 | Hernandez Barrios Samuel Rodrigo | 3BV1');c.drawRightString(560,30,str(d.page))
SimpleDocTemplate(str(Q/'contenido.pdf'),pagesize=(612,792),leftMargin=52,rightMargin=52,topMargin=43,bottomMargin=48).build(flow,onFirstPage=footer,onLaterPages=footer)
w=PdfWriter();w.append(str(Q/'portada.pdf'));w.append(str(Q/'contenido.pdf'));w.add_metadata({'/Title':'Práctica 3 Divide y vencerás','/Author':'Hernandez Barrios Samuel Rodrigo'})
final=B/'Practica3_ADA_Hernandez_Barrios_Samuel_Rodrigo_3BV1.pdf'
with final.open('wb') as f:w.write(f)
doc=pdfium.PdfDocument(str(final))
for i,page in enumerate(doc):page.render(scale=1.2).to_pil().save(Q/f'pagina_{i+1}.png')
print('PDF creado:',final,'Paginas:',len(doc),'Ensayos validados:',len(rows))
